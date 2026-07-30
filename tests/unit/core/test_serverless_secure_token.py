"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Serverless `secure=True` token enforcement.

A tool registered with ``secure=True`` must be enforced on EVERY transport, not
just HTTP. These tests pin the contract across all four serverless modes
(lambda, cgi, google_cloud_function, azure_function) for the four token states:

  * valid       -> the handler RUNS (a fix that refuses everything is not a fix)
  * forged      -> refused
  * absent      -> refused (omitting a credential is never weaker than a wrong one)
  * no call_id  -> refused (a token can only be validated against a call_id)

An ``secure=False`` tool proceeds ungated in every state.

The refusal shape is a 200 + FunctionResult body, NOT an HTTP error status --
the engine (mod_openai) has no handling for a SWAIG refusal status, so the tool
reports that it cannot execute and the model relays it.
"""

import base64
import io
import json
import sys
from typing import Any
from unittest.mock import Mock, patch

import pytest

from signalwire.core.agent_base import AgentBase
from signalwire.core.function_result import FunctionResult

HANDLER_RAN = "HANDLER RAN"
REFUSAL_FRAGMENT = "security token for this function is invalid"

_USER = "u"
_PASS = "p"
_BASIC = "Basic " + base64.b64encode(f"{_USER}:{_PASS}".encode()).decode()

CALL_ID = "test-call-id"


class _SecureAgent(AgentBase):
    """Agent exposing one secure tool and one insecure tool."""

    def __init__(self) -> None:
        super().__init__(
            name="secure-agent",
            route="/",
            basic_auth=(_USER, _PASS),
        )
        self.define_tool("secret_tool", "secure", {}, self._handler, secure=True)
        self.define_tool("open_tool", "insecure", {}, self._handler, secure=False)

    def _handler(self, args: dict[str, Any], raw_data: Any) -> FunctionResult:
        return FunctionResult(HANDLER_RAN)


@pytest.fixture
def agent() -> _SecureAgent:
    return _SecureAgent()


def _valid_token(
    agent: _SecureAgent, function_name: str, call_id: str = CALL_ID
) -> str:
    return str(agent._session_manager.generate_token(function_name, call_id))


def _swaig_body(function_name: str, call_id: str | None = CALL_ID) -> dict[str, Any]:
    body: dict[str, Any] = {
        "function": function_name,
        "argument": {"parsed": [{}], "raw": "{}"},
    }
    if call_id is not None:
        body["call_id"] = call_id
    return body


def _assert_ran(payload: dict[str, Any]) -> None:
    assert payload.get("response") == HANDLER_RAN, (
        f"expected the handler to RUN, got {payload!r}"
    )


def _assert_refused(payload: dict[str, Any]) -> None:
    response = payload.get("response", "")
    assert REFUSAL_FRAGMENT in response, (
        f"expected a secure-token REFUSAL, got {payload!r}"
    )
    assert HANDLER_RAN not in json.dumps(payload), (
        f"handler RAN despite an invalid/absent token: {payload!r}"
    )


# ---------------------------------------------------------------------------
# Per-mode invocation helpers -- each returns the decoded SWAIG result dict.
#
# The four modes carry the query string in four DIFFERENT places; that is the
# whole point of the per-mode extraction under test.
# ---------------------------------------------------------------------------


def _invoke_lambda_v2(
    agent: _SecureAgent,
    function_name: str,
    token: str | None,
    call_id: str | None = CALL_ID,
) -> dict[str, Any]:
    """HTTP API v2 payload: `rawPath` + `queryStringParameters` dict."""
    event: dict[str, Any] = {
        "rawPath": f"/{function_name}",
        "headers": {"Authorization": _BASIC},
        "body": json.dumps(_swaig_body(function_name, call_id)),
    }
    if token is not None:
        event["queryStringParameters"] = {"__token": token}
    result = agent.handle_serverless_request(event=event, mode="lambda")
    assert result["statusCode"] == 200, (
        f"refusal must be a 200 + FunctionResult body, got {result['statusCode']}"
    )
    return dict(json.loads(result["body"]))


def _invoke_lambda_v2_raw(
    agent: _SecureAgent,
    function_name: str,
    token: str | None,
    call_id: str | None = CALL_ID,
) -> dict[str, Any]:
    """HTTP API v2 payload variant carrying `rawQueryString` instead of the dict."""
    event: dict[str, Any] = {
        "rawPath": f"/{function_name}",
        "headers": {"Authorization": _BASIC},
        "body": json.dumps(_swaig_body(function_name, call_id)),
    }
    if token is not None:
        event["rawQueryString"] = f"__token={token}"
    result = agent.handle_serverless_request(event=event, mode="lambda")
    assert result["statusCode"] == 200
    return dict(json.loads(result["body"]))


def _invoke_lambda_v1(
    agent: _SecureAgent,
    function_name: str,
    token: str | None,
    call_id: str | None = CALL_ID,
) -> dict[str, Any]:
    """REST API v1 payload: `pathParameters.proxy` + `queryStringParameters`."""
    event: dict[str, Any] = {
        "pathParameters": {"proxy": function_name},
        "headers": {"Authorization": _BASIC},
        "body": json.dumps(_swaig_body(function_name, call_id)),
    }
    if token is not None:
        event["queryStringParameters"] = {"__token": token}
    result = agent.handle_serverless_request(event=event, mode="lambda")
    assert result["statusCode"] == 200
    return dict(json.loads(result["body"]))


def _invoke_cgi(
    agent: _SecureAgent,
    function_name: str,
    token: str | None,
    call_id: str | None = CALL_ID,
) -> dict[str, Any]:
    """CGI: `QUERY_STRING` environment variable."""
    body = json.dumps(_swaig_body(function_name, call_id))
    env = {
        "PATH_INFO": f"/{function_name}",
        "CONTENT_LENGTH": str(len(body)),
        "HTTP_AUTHORIZATION": _BASIC,
        "QUERY_STRING": f"__token={token}" if token is not None else "",
    }
    with (
        patch.dict("os.environ", env, clear=False),
        patch.object(sys, "stdin", io.StringIO(body)),
    ):
        result = agent.handle_serverless_request(mode="cgi")
    return dict(result)


def _invoke_gcf(
    agent: _SecureAgent,
    function_name: str,
    token: str | None,
    call_id: str | None = CALL_ID,
) -> dict[str, Any]:
    """Google Cloud Functions: Flask `request.args` mapping."""
    request = Mock()
    request.path = f"/{function_name}"
    request.method = "POST"
    request.url = f"https://region-proj.cloudfunctions.net/{function_name}"
    request.headers = {"Authorization": _BASIC}
    request.args = {"__token": token} if token is not None else {}
    request.query_string = f"__token={token}".encode() if token is not None else b""
    payload = _swaig_body(function_name, call_id)
    request.is_json = True
    request.get_json = Mock(return_value=payload)
    request.get_data = Mock(return_value=json.dumps(payload).encode())

    captured: dict[str, Any] = {}

    class _Response:
        def __init__(self, response: str, status: int, headers: Any = None) -> None:
            captured["body"] = response
            captured["status"] = status

    flask_stub = Mock()
    flask_stub.Response = _Response
    with patch.dict(sys.modules, {"flask": flask_stub}):
        agent.handle_serverless_request(event=request, mode="google_cloud_function")

    assert captured["status"] == 200, (
        f"refusal must be a 200 + FunctionResult body, got {captured['status']}"
    )
    return dict(json.loads(captured["body"]))


def _invoke_azure(
    agent: _SecureAgent,
    function_name: str,
    token: str | None,
    call_id: str | None = CALL_ID,
) -> dict[str, Any]:
    """Azure Functions: `req.params` mapping (and the query in `req.url`)."""
    query = f"?__token={token}" if token is not None else ""
    req = Mock()
    req.url = f"https://app.azurewebsites.net/api/myagent/{function_name}{query}"
    req.method = "POST"
    req.headers = {"Authorization": _BASIC}
    req.params = {"__token": token} if token is not None else {}
    req.get_body = Mock(
        return_value=json.dumps(_swaig_body(function_name, call_id)).encode()
    )

    captured: dict[str, Any] = {}

    class _HttpResponse:
        def __init__(
            self, body: str, status_code: int = 200, headers: Any = None
        ) -> None:
            captured["body"] = body
            captured["status"] = status_code

    func_stub = Mock()
    func_stub.HttpResponse = _HttpResponse
    with patch.dict(
        sys.modules,
        {"azure": Mock(functions=func_stub), "azure.functions": func_stub},
    ):
        agent.handle_serverless_request(event=req, mode="azure_function")

    assert captured["status"] == 200, (
        f"refusal must be a 200 + FunctionResult body, got {captured['status']}"
    )
    return dict(json.loads(captured["body"]))


_INVOKERS = {
    "lambda_v2": _invoke_lambda_v2,
    "lambda_v2_rawquery": _invoke_lambda_v2_raw,
    "lambda_v1": _invoke_lambda_v1,
    "cgi": _invoke_cgi,
    "google_cloud_function": _invoke_gcf,
    "azure_function": _invoke_azure,
}

MODES = list(_INVOKERS)


# ---------------------------------------------------------------------------
# The 4-state matrix, per mode.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
def test_secure_tool_valid_token_runs(agent: _SecureAgent, mode: str) -> None:
    """A VALID token must still run the handler in every serverless mode."""
    token = _valid_token(agent, "secret_tool")
    _assert_ran(_INVOKERS[mode](agent, "secret_tool", token))


@pytest.mark.parametrize("mode", MODES)
def test_secure_tool_forged_token_refused(agent: _SecureAgent, mode: str) -> None:
    """A FORGED token must be refused in every serverless mode."""
    _assert_refused(
        _INVOKERS[mode](agent, "secret_tool", "obviously-not-a-valid-token")
    )


@pytest.mark.parametrize("mode", MODES)
def test_secure_tool_absent_token_refused(agent: _SecureAgent, mode: str) -> None:
    """An ABSENT token must be refused -- never weaker than a wrong one."""
    _assert_refused(_INVOKERS[mode](agent, "secret_tool", None))


@pytest.mark.parametrize("mode", MODES)
def test_secure_tool_missing_call_id_refused(agent: _SecureAgent, mode: str) -> None:
    """A token with NO call_id to check it against counts as UNVALIDATED."""
    token = _valid_token(agent, "secret_tool")
    _assert_refused(_INVOKERS[mode](agent, "secret_tool", token, call_id=None))


@pytest.mark.parametrize("mode", MODES)
def test_secure_tool_token_for_other_function_refused(
    agent: _SecureAgent, mode: str
) -> None:
    """A token minted for a DIFFERENT function must not authorize this one."""
    token = _valid_token(agent, "open_tool")
    _assert_refused(_INVOKERS[mode](agent, "secret_tool", token))


@pytest.mark.parametrize("mode", MODES)
def test_secure_tool_token_for_other_call_refused(
    agent: _SecureAgent, mode: str
) -> None:
    """A token minted for a DIFFERENT call_id must not authorize this call."""
    token = _valid_token(agent, "secret_tool", call_id="some-other-call")
    _assert_refused(_INVOKERS[mode](agent, "secret_tool", token))


# ---------------------------------------------------------------------------
# An insecure tool proceeds ungated in every state -- the fix must not make
# `secure=False` behave like `secure=True`.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
def test_insecure_tool_absent_token_runs(agent: _SecureAgent, mode: str) -> None:
    _assert_ran(_INVOKERS[mode](agent, "open_tool", None))


@pytest.mark.parametrize("mode", MODES)
def test_insecure_tool_forged_token_runs(agent: _SecureAgent, mode: str) -> None:
    _assert_ran(_INVOKERS[mode](agent, "open_tool", "garbage-token"))


@pytest.mark.parametrize("mode", MODES)
def test_insecure_tool_missing_call_id_runs(agent: _SecureAgent, mode: str) -> None:
    _assert_ran(_INVOKERS[mode](agent, "open_tool", None, call_id=None))


# ---------------------------------------------------------------------------
# The `token` fallback spelling is honoured exactly as HTTP does.
# ---------------------------------------------------------------------------


def test_lambda_bare_token_param_accepted(agent: _SecureAgent) -> None:
    """HTTP reads `__token` then falls back to `token`; serverless matches."""
    token = _valid_token(agent, "secret_tool")
    event = {
        "rawPath": "/secret_tool",
        "headers": {"Authorization": _BASIC},
        "queryStringParameters": {"token": token},
        "body": json.dumps(_swaig_body("secret_tool")),
    }
    result = agent.handle_serverless_request(event=event, mode="lambda")
    _assert_ran(json.loads(result["body"]))


def test_lambda_dunder_token_wins_over_bare(agent: _SecureAgent) -> None:
    """`__token` takes precedence over `token`, matching the HTTP path."""
    token = _valid_token(agent, "secret_tool")
    event = {
        "rawPath": "/secret_tool",
        "headers": {"Authorization": _BASIC},
        "queryStringParameters": {"__token": token, "token": "garbage"},
        "body": json.dumps(_swaig_body("secret_tool")),
    }
    result = agent.handle_serverless_request(event=event, mode="lambda")
    _assert_ran(json.loads(result["body"]))
