"""
Tests for AgentBase.handle_swaig_request: the /swaig endpoint without FastAPI.

An application that runs its own web server (aiohttp, Flask, a test harness)
hands each request to the agent as primitives and gets back a status, headers
and a body. It follows the web server's rules: basic auth, a signature check
when a signing_key is set, per-call configuration, the per-call token for a
secure function, and the same response for the same request.
"""

import asyncio
import base64
import hashlib
import hmac
import json
import threading
from typing import Any
from urllib.parse import urlparse

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient as AiohttpClient
from aiohttp.test_utils import TestServer
from fastapi.testclient import TestClient

from signalwire.core.agent_base import AgentBase
from signalwire.core.function_result import FunctionResult

BASE = "http://127.0.0.1:8768"
SWAIG_URL = f"{BASE}/agent/swaig"
SIGNING_KEY = "PSKtest1234567890abcdef"
REFUSED = "security token for this function is invalid"


@pytest.fixture(autouse=True)
def _no_ambient_config(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("SIGNALWIRE_SIGNING_KEY", "SWML_PROXY_URL_BASE"):
        monkeypatch.delenv(name, raising=False)


def _agent(signing_key: str | None = None) -> AgentBase:
    agent = AgentBase(
        name="hosted",
        route="/agent",
        basic_auth=("user", "pass"),
        signing_key=signing_key,
    )
    agent.define_tool(
        "secret",
        "A secure tool.",
        {},
        lambda args, raw_data: FunctionResult(f"ran secret with {args}"),
    )
    return agent


def _headers(**extra: str) -> dict[str, str]:
    auth = base64.b64encode(b"user:pass").decode()
    return {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        **extra,
    }


def _call(function: str, call_id: str = "call-1", **args: Any) -> str:
    return json.dumps(
        {"function": function, "call_id": call_id, "argument": {"parsed": [args]}}
    )


def _token_query(agent: AgentBase, function: str, call_id: str = "call-1") -> str:
    """The query string the SWML rendered for ``call_id`` puts on ``function``'s URL."""
    status, _, swml = agent.handle_request(
        "POST", f"{BASE}/agent", _headers(), {"call": {"call_id": call_id}}
    )
    assert status == 200
    ai = next(v["ai"] for v in json.loads(swml)["sections"]["main"] if "ai" in v)
    url: str = next(
        f["web_hook_url"] for f in ai["SWAIG"]["functions"] if f["function"] == function
    )
    return urlparse(url).query


class TestDispatch:
    async def test_a_secure_function_runs_with_its_token(self) -> None:
        agent = _agent()
        query = _token_query(agent, "secret")
        status, headers, body = await agent.handle_swaig_request(
            "POST", f"{SWAIG_URL}?{query}", _headers(), _call("secret", topic="hours")
        )
        assert status == 200
        assert headers["Content-Type"] == "application/json"
        assert json.loads(body) == {"response": "ran secret with {'topic': 'hours'}"}

    async def test_a_secure_function_without_a_token_is_refused(self) -> None:
        status, _, body = await _agent().handle_swaig_request(
            "POST", SWAIG_URL, _headers(), _call("secret")
        )
        assert status == 200
        assert REFUSED in json.loads(body)["response"]

    async def test_a_token_for_another_call_is_refused(self) -> None:
        agent = _agent()
        query = _token_query(agent, "secret", call_id="call-1")
        _, _, body = await agent.handle_swaig_request(
            "POST",
            f"{SWAIG_URL}?{query}",
            _headers(),
            _call("secret", call_id="call-2"),
        )
        assert REFUSED in json.loads(body)["response"]

    async def test_bytes_bodies_are_accepted(self) -> None:
        agent = _agent()
        query = _token_query(agent, "secret")
        _, _, body = await agent.handle_swaig_request(
            "POST", f"{SWAIG_URL}?{query}", _headers(), _call("secret").encode()
        )
        assert json.loads(body) == {"response": "ran secret with {}"}

    async def test_a_missing_function_name_is_a_bad_request(self) -> None:
        status, _, body = await _agent().handle_swaig_request(
            "POST", SWAIG_URL, _headers(), json.dumps({"call_id": "call-1"})
        )
        assert status == 400
        assert json.loads(body) == {"error": "Missing function name"}

    async def test_an_unknown_function_is_reported(self) -> None:
        agent = _agent()
        agent.define_tool(
            "open_tool", "No token needed.", {}, lambda a, r: "x", secure=False
        )
        _, _, body = await agent.handle_swaig_request(
            "POST", SWAIG_URL, _headers(), _call("nope")
        )
        assert json.loads(body) == {"response": "Function 'nope' not found"}

    async def test_get_returns_the_swml(self) -> None:
        status, _, body = await _agent().handle_swaig_request(
            "GET", SWAIG_URL, _headers()
        )
        assert status == 200
        assert "sections" in json.loads(body)

    async def test_other_methods_are_refused(self) -> None:
        status, _, _ = await _agent().handle_swaig_request(
            "PUT", SWAIG_URL, _headers(), _call("secret")
        )
        assert status == 405


class TestAuth:
    async def test_wrong_credentials_are_unauthorized(self) -> None:
        bad = base64.b64encode(b"user:wrong").decode()
        status, headers, body = await _agent().handle_swaig_request(
            "POST", SWAIG_URL, {"Authorization": f"Basic {bad}"}, _call("secret")
        )
        assert status == 401
        assert headers["WWW-Authenticate"] == "Basic"
        assert json.loads(body) == {"error": "Unauthorized"}

    async def test_lower_case_header_names_authenticate(self) -> None:
        headers = {k.lower(): v for k, v in _headers().items()}
        status, _, _ = await _agent().handle_swaig_request(
            "POST", SWAIG_URL, headers, _call("secret")
        )
        assert status == 200

    async def test_an_unsigned_post_is_forbidden_with_a_signing_key(self) -> None:
        status, _, body = await _agent(SIGNING_KEY).handle_swaig_request(
            "POST", SWAIG_URL, _headers(), _call("secret")
        )
        assert status == 403
        assert json.loads(body) == {"error": "Forbidden"}

    async def test_a_signed_post_runs_with_a_signing_key(self) -> None:
        agent = _agent(SIGNING_KEY)
        url = f"{SWAIG_URL}?{_token_query(agent, 'secret')}"
        raw = _call("secret")
        signature = hmac.new(SIGNING_KEY.encode(), (url + raw).encode(), hashlib.sha1)
        status, _, body = await agent.handle_swaig_request(
            "POST",
            url,
            _headers(**{"X-SignalWire-Signature": signature.hexdigest()}),
            raw,
        )
        assert status == 200
        assert json.loads(body) == {"response": "ran secret with {}"}


class TestHandlers:
    async def test_an_async_handler_runs_on_the_callers_event_loop(self) -> None:
        agent = _agent()
        seen: list[asyncio.AbstractEventLoop] = []

        async def where(
            args: dict[str, Any], raw_data: dict[str, Any]
        ) -> FunctionResult:
            seen.append(asyncio.get_running_loop())
            return FunctionResult("async ok")

        agent.define_tool("where", "Async tool.", {}, where, secure=False)
        _, _, body = await agent.handle_swaig_request(
            "POST", SWAIG_URL, _headers(), _call("where")
        )
        assert json.loads(body) == {"response": "async ok"}
        assert seen == [asyncio.get_running_loop()]

    async def test_a_sync_handler_runs_off_the_event_loop_thread(self) -> None:
        agent = _agent()
        threads: list[int] = []

        def blocking(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
            threads.append(threading.get_ident())
            return FunctionResult("sync ok")

        agent.define_tool("blocking", "Sync tool.", {}, blocking, secure=False)
        _, _, body = await agent.handle_swaig_request(
            "POST", SWAIG_URL, _headers(), _call("blocking")
        )
        assert json.loads(body) == {"response": "sync ok"}
        assert threads and threads[0] != threading.get_ident()

    async def test_per_call_configuration_sees_the_request(self) -> None:
        agent = _agent()
        seen: list[tuple[dict[str, Any], dict[str, Any]]] = []

        def configure(
            query: dict[str, Any],
            body: dict[str, Any],
            headers: dict[str, Any],
            copy: AgentBase,
        ) -> None:
            seen.append((query, headers))
            copy.define_tool(
                "added",
                "Added per call.",
                {},
                lambda a, r: FunctionResult("added ran"),
                secure=False,
            )

        agent.set_dynamic_config_callback(configure)
        _, _, body = await agent.handle_swaig_request(
            "POST", f"{SWAIG_URL}?tenant=acme", _headers(), _call("added")
        )
        assert json.loads(body) == {"response": "added ran"}
        assert seen[0][0] == {"tenant": "acme"}
        assert seen[0][1]["content-type"] == "application/json"
        assert "added" not in agent._tool_registry._swaig_functions


class TestSameAsTheWebServer:
    """The same request gets the same answer here and from POST /swaig."""

    @pytest.mark.parametrize(
        "raw",
        [
            _call("secret", topic="hours"),
            json.dumps({"call_id": "call-1"}),
            _call("nope"),
            _call("bad-name"),
        ],
    )
    async def test_matches_post_swaig(self, raw: str) -> None:
        agent = _agent()
        agent.define_tool(
            "open_tool", "No token needed.", {}, lambda a, r: "x", secure=False
        )
        query = _token_query(agent, "secret")
        web = TestClient(agent.get_app()).post(
            f"/agent/swaig?{query}", content=raw, headers=_headers()
        )
        status, _, body = await agent.handle_swaig_request(
            "POST", f"{SWAIG_URL}?{query}", _headers(), raw
        )
        assert (status, json.loads(body)) == (web.status_code, web.json())


class TestInAnAiohttpServer:
    """Mounted in a real aiohttp application, served over a real socket."""

    async def test_a_tool_call_round_trips(self) -> None:
        agent = _agent()

        async def swaig(request: web.Request) -> web.Response:
            status, headers, body = await agent.handle_swaig_request(
                request.method, str(request.url), request.headers, await request.read()
            )
            return web.Response(status=status, headers=headers, text=body)

        app = web.Application()
        app.router.add_route("*", "/agent/swaig", swaig)
        async with AiohttpClient(TestServer(app)) as client:
            query = _token_query(agent, "secret")
            ok = await client.post(
                f"/agent/swaig?{query}",
                data=_call("secret", topic="hours"),
                headers=_headers(),
            )
            assert ok.status == 200
            assert ok.headers["Content-Type"].startswith("application/json")
            assert await ok.json() == {"response": "ran secret with {'topic': 'hours'}"}

            denied = await client.post("/agent/swaig", data=_call("secret"))
            assert denied.status == 401
            assert denied.headers["WWW-Authenticate"] == "Basic"
