"""
Integration tests: serverless requests follow the web server's security rules.

A real AgentBase answers Lambda, CGI, Cloud Functions and Azure Functions
requests. On every platform it must render SWML for the call the request
names, so that call's tokens validate later; run a secure function only with
its token; and, with a signing_key set, refuse unsigned POSTs.
"""

import base64
import hashlib
import hmac
import io
import json
import os
import sys
import types
from collections.abc import Iterator
from typing import Any
from unittest.mock import patch
from urllib.parse import urlparse

import flask
import pytest

from signalwire.agent_server import AgentServer
from signalwire.core.agent_base import AgentBase
from signalwire.core.function_result import FunctionResult

SIGNING_KEY = "PSKtest1234567890abcdef"
REFUSED = "security token for this function is invalid"
LAMBDA_HOST = "abc123.lambda-url.us-east-1.on.aws"


@pytest.fixture(autouse=True)
def _no_ambient_config(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("SIGNALWIRE_SIGNING_KEY", "SWML_PROXY_URL_BASE", "GATEWAY_INTERFACE",
                 "HTTP_AUTHORIZATION", "REQUEST_URI", "QUERY_STRING", "CONTENT_LENGTH"):
        monkeypatch.delenv(name, raising=False)


def _agent(route: str = "/agent", signing_key: str | None = None) -> AgentBase:
    agent = AgentBase(name="serverless", route=route, signing_key=signing_key)
    agent.define_tool("secret", "A secure tool.", {},
                      lambda args, raw_data: FunctionResult(f"ran secret with {args}"))
    return agent


def _auth(agent: AgentBase) -> str:
    user, password = agent.get_basic_auth_credentials()[:2]
    return "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()


def _sign(url: str, body: str) -> str:
    return hmac.new(SIGNING_KEY.encode(), (url + body).encode(), hashlib.sha1).hexdigest()


def _tool_query(swml: str, function: str) -> str:
    """The raw query string of a function's URL in rendered SWML: its token."""
    ai = next(verb["ai"] for verb in json.loads(swml)["sections"]["main"] if "ai" in verb)
    url: str = next(f["web_hook_url"] for f in ai["SWAIG"]["functions"] if f["function"] == function)
    return urlparse(url).query


def _tool_call(call_id: str) -> str:
    return json.dumps({"function": "secret", "call_id": call_id,
                       "argument": {"parsed": [{"topic": "hours"}]}})


# ---------------------------------------------------------------------------
# Lambda
# ---------------------------------------------------------------------------

def _lambda(agent: AgentBase, path: str, body: str = "", query: str = "",
            signature: str | None = None) -> dict[str, Any]:
    headers = {"authorization": _auth(agent)}
    if signature:
        headers["x-signalwire-signature"] = signature
    event = {"rawPath": path, "rawQueryString": query, "headers": headers, "body": body,
             "requestContext": {"domainName": LAMBDA_HOST,
                                "http": {"method": "POST" if body else "GET"}}}
    response: dict[str, Any] = agent.handle_serverless_request(event, None, mode="lambda")
    return response


class TestLambda:
    def test_the_token_from_the_swml_runs_the_function(self) -> None:
        agent = _agent()
        swml = _lambda(agent, "/agent", json.dumps({"call": {"call_id": "call-1"}}))["body"]
        result = _lambda(agent, "/agent/swaig/", _tool_call("call-1"), _tool_query(swml, "secret"))
        assert json.loads(result["body"]) == {"response": "ran secret with {'topic': 'hours'}"}

    def test_no_token_is_refused(self) -> None:
        result = _lambda(_agent(), "/agent/swaig/", _tool_call("call-1"))
        assert REFUSED in json.loads(result["body"])["response"]

    def test_a_token_for_another_call_is_refused(self) -> None:
        agent = _agent()
        swml = _lambda(agent, "/agent", json.dumps({"call": {"call_id": "call-1"}}))["body"]
        result = _lambda(agent, "/agent/swaig/", _tool_call("call-2"), _tool_query(swml, "secret"))
        assert REFUSED in json.loads(result["body"])["response"]

    def test_an_unsigned_post_is_refused(self) -> None:
        result = _lambda(_agent(signing_key=SIGNING_KEY), "/agent", "{}")
        assert result["statusCode"] == 403

    def test_a_signed_post_is_answered(self) -> None:
        body = json.dumps({"call": {"call_id": "call-1"}})
        signature = _sign(f"https://{LAMBDA_HOST}/agent", body)
        result = _lambda(_agent(signing_key=SIGNING_KEY), "/agent", body, signature=signature)
        assert result["statusCode"] == 200
        assert "sections" in json.loads(result["body"])

    def test_per_call_config_applies(self) -> None:
        agent = _agent()
        agent.add_per_call_config(
            lambda query, body, headers, copy: copy.update_global_data({"caller": body.get("caller")}))
        swml = _lambda(agent, "/agent", json.dumps({"call": {"call_id": "c"}, "caller": "Ana"}))["body"]
        ai = next(verb["ai"] for verb in json.loads(swml)["sections"]["main"] if "ai" in verb)
        assert ai["global_data"] == {"caller": "Ana"}


# ---------------------------------------------------------------------------
# CGI
# ---------------------------------------------------------------------------

def _cgi(agent: AgentBase, path: str, body: str = "", query: str = "",
         signature: str | None = None) -> str:
    env = {"PATH_INFO": path, "QUERY_STRING": query, "CONTENT_LENGTH": str(len(body)),
           "REQUEST_METHOD": "POST" if body else "GET", "HTTPS": "on",
           "HTTP_HOST": "example.com", "SCRIPT_NAME": "/cgi-bin/agent.cgi",
           "HTTP_AUTHORIZATION": _auth(agent)}
    if signature:
        env["HTTP_X_SIGNALWIRE_SIGNATURE"] = signature
    with patch.dict(os.environ, env), patch("sys.stdin", io.StringIO(body)):
        response: str = agent.handle_serverless_request(mode="cgi")
    return response


def _cgi_body(response: str) -> str:
    return response.partition("\r\n\r\n")[2]


class TestCGI:
    def test_the_token_from_the_swml_runs_the_function(self) -> None:
        agent = _agent()
        swml = _cgi_body(_cgi(agent, "/agent", json.dumps({"call": {"call_id": "call-1"}})))
        result = _cgi(agent, "/agent/swaig/", _tool_call("call-1"), _tool_query(swml, "secret"))
        assert result.startswith("Status: 200 OK\r\n")
        assert json.loads(_cgi_body(result)) == {"response": "ran secret with {'topic': 'hours'}"}

    def test_no_token_is_refused(self) -> None:
        result = _cgi(_agent(), "/agent/swaig/", _tool_call("call-1"))
        assert REFUSED in json.loads(_cgi_body(result))["response"]

    def test_an_unsigned_post_is_refused(self) -> None:
        result = _cgi(_agent(signing_key=SIGNING_KEY), "/agent/swaig/", _tool_call("call-1"))
        assert result.startswith("Status: 403 Forbidden\r\n")

    def test_a_signed_post_is_answered(self) -> None:
        body = json.dumps({"call": {"call_id": "call-1"}})
        signature = _sign("https://example.com/cgi-bin/agent.cgi/agent", body)
        result = _cgi(_agent(signing_key=SIGNING_KEY), "/agent", body, signature=signature)
        assert result.startswith("Status: 200 OK\r\n")


# ---------------------------------------------------------------------------
# Google Cloud Functions
# ---------------------------------------------------------------------------

GCF_BASE = "https://us-central1-project.cloudfunctions.net"


def _gcf(agent: AgentBase, path: str, body: str = "", query: str = "",
         signature: str | None = None) -> flask.Response:
    headers = {"Authorization": _auth(agent), "Content-Type": "application/json"}
    if signature:
        headers["X-SignalWire-Signature"] = signature
    app = flask.Flask("gcf")
    with app.test_request_context(path, method="POST" if body else "GET", data=body,
                                  query_string=query, headers=headers, base_url=GCF_BASE):
        response: flask.Response = agent.handle_serverless_request(
            flask.request, None, mode="google_cloud_function")
    return response


class TestCloudFunctions:
    def test_the_token_from_the_swml_runs_the_function(self) -> None:
        agent = _agent()
        swml = _gcf(agent, "/agent", json.dumps({"call": {"call_id": "call-1"}})).get_data(as_text=True)
        result = _gcf(agent, "/agent/swaig/", _tool_call("call-1"), _tool_query(swml, "secret"))
        assert json.loads(result.get_data(as_text=True)) == {
            "response": "ran secret with {'topic': 'hours'}"}

    def test_no_token_is_refused(self) -> None:
        result = _gcf(_agent(), "/agent/swaig/", _tool_call("call-1"))
        assert REFUSED in json.loads(result.get_data(as_text=True))["response"]

    def test_an_unsigned_post_is_refused(self) -> None:
        assert _gcf(_agent(signing_key=SIGNING_KEY), "/agent", "{}").status_code == 403

    def test_a_signed_post_is_answered(self) -> None:
        body = json.dumps({"call": {"call_id": "call-1"}})
        signature = _sign(f"{GCF_BASE}/agent", body)
        result = _gcf(_agent(signing_key=SIGNING_KEY), "/agent", body, signature=signature)
        assert result.status_code == 200


# ---------------------------------------------------------------------------
# Azure Functions
# ---------------------------------------------------------------------------

class _HttpResponse:
    def __init__(self, body: str, status_code: int, headers: dict[str, str]) -> None:
        self.body, self.status_code = body, status_code


@pytest.fixture
def azure_functions() -> Iterator[None]:
    package = types.ModuleType("azure")
    module = types.ModuleType("azure.functions")
    module.HttpResponse = _HttpResponse  # type: ignore[attr-defined]  # stand-in for the SDK
    package.functions = module  # type: ignore[attr-defined]  # stand-in for the SDK
    with patch.dict(sys.modules, {"azure": package, "azure.functions": module}):
        yield


AZURE_BASE = "https://myapp.azurewebsites.net/api/myfn"


def _azure(agent: AgentBase, path: str, body: str = "", query: str = "",
           signature: str | None = None) -> _HttpResponse:
    headers = {"Authorization": _auth(agent)}
    if signature:
        headers["x-signalwire-signature"] = signature
    request = types.SimpleNamespace(
        url=f"{AZURE_BASE}{path}" + (f"?{query}" if query else ""),
        method="POST" if body else "GET", headers=headers,
        get_body=lambda: body.encode())
    response: _HttpResponse = agent.handle_serverless_request(request, None, mode="azure_function")
    return response


@pytest.mark.usefixtures("azure_functions")
class TestAzureFunctions:
    def test_the_token_from_the_swml_runs_the_function(self) -> None:
        agent = _agent()
        swml = _azure(agent, "/agent", json.dumps({"call": {"call_id": "call-1"}})).body
        # The token rides in the query string, which must not leak into the path
        result = _azure(agent, "/agent/swaig/", _tool_call("call-1"), _tool_query(swml, "secret"))
        assert json.loads(result.body) == {"response": "ran secret with {'topic': 'hours'}"}

    def test_no_token_is_refused(self) -> None:
        result = _azure(_agent(), "/agent/swaig/", _tool_call("call-1"))
        assert REFUSED in json.loads(result.body)["response"]

    def test_an_unsigned_post_is_refused(self) -> None:
        assert _azure(_agent(signing_key=SIGNING_KEY), "/agent", "{}").status_code == 403

    def test_a_signed_post_is_answered(self) -> None:
        body = json.dumps({"call": {"call_id": "call-1"}})
        signature = _sign(f"{AZURE_BASE}/agent", body)
        result = _azure(_agent(signing_key=SIGNING_KEY), "/agent", body, signature=signature)
        assert result.status_code == 200


# ---------------------------------------------------------------------------
# AgentServer's serverless modes
# ---------------------------------------------------------------------------

class TestAgentServerLambda:
    def test_the_token_from_the_swml_runs_the_function(self) -> None:
        agent = _agent(route="/")
        server = AgentServer()
        server.register(agent, "/myagent")
        swml = server._handle_lambda_request(
            {"path": "/myagent", "headers": {"Authorization": _auth(agent)},
             "body": json.dumps({"call": {"call_id": "call-1"}})}, None)["body"]
        result = server._handle_lambda_request(
            {"rawPath": "/myagent/swaig/", "rawQueryString": _tool_query(swml, "secret"),
             "headers": {"Authorization": _auth(agent)}, "body": _tool_call("call-1")}, None)
        assert json.loads(result["body"]) == {"response": "ran secret with {'topic': 'hours'}"}

    def test_no_token_is_refused(self) -> None:
        agent = _agent(route="/")
        server = AgentServer()
        server.register(agent, "/myagent")
        result = server._handle_lambda_request(
            {"path": "/myagent/swaig", "headers": {"Authorization": _auth(agent)},
             "body": _tool_call("call-1")}, None)
        assert REFUSED in json.loads(result["body"])["response"]
