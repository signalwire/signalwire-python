"""
Integration tests: a secure SWAIG function runs only with its per-call token.

The SDK mints a token into each secure function's ``web_hook_url`` when it
renders SWML for a call. These tests fetch real SWML, take the token from it,
and check that the SWAIG endpoint runs the function with that token, and
refuses it without one, for another call, or for another function.
"""

import base64
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

from signalwire.core.agent_base import AgentBase
from signalwire.core.function_result import FunctionResult

REFUSED = "security token for this function is invalid"


def _handler(text: str) -> Any:
    return lambda args, raw_data: FunctionResult(text)


@pytest.fixture
def agent() -> AgentBase:
    agent = AgentBase(name="tokens", route="/agent")
    agent.define_tool("secret", "A secure tool.", {}, _handler("ran secret"))
    agent.define_tool("other", "Another secure tool.", {}, _handler("ran other"))
    agent.define_tool("open", "A tool without a token.", {}, _handler("ran open"), secure=False)
    return agent


@pytest.fixture
def client(agent: AgentBase) -> TestClient:
    return TestClient(agent.get_app())


def _auth(agent: AgentBase) -> dict[str, str]:
    user, password = agent.get_basic_auth_credentials()[:2]
    return {"Authorization": "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()}


def _token(client: TestClient, agent: AgentBase, function: str, call_id: str) -> str:
    """The token the SWML for ``call_id`` hands out for ``function``."""
    swml = client.get(f"/agent/?call_id={call_id}", headers=_auth(agent)).json()
    ai = next(verb["ai"] for verb in swml["sections"]["main"] if "ai" in verb)
    url: str = next(f["web_hook_url"] for f in ai["SWAIG"]["functions"] if f["function"] == function)
    return parse_qs(urlparse(url).query)["__token"][0]


def _call(client: TestClient, agent: AgentBase, function: str, call_id: str,
          token: str | None = None) -> str:
    query = f"?__token={token}" if token else ""
    resp = client.post(
        f"/agent/swaig{query}",
        json={"function": function, "call_id": call_id, "argument": {"parsed": [{}]}},
        headers=_auth(agent),
    )
    assert resp.status_code == 200
    return str(resp.json()["response"])


def test_the_token_from_the_swml_runs_the_function(client: TestClient, agent: AgentBase) -> None:
    token = _token(client, agent, "secret", "call-1")
    assert _call(client, agent, "secret", "call-1", token) == "ran secret"


def test_no_token_is_refused(client: TestClient, agent: AgentBase) -> None:
    assert REFUSED in _call(client, agent, "secret", "call-1")


def test_a_token_for_another_call_is_refused(client: TestClient, agent: AgentBase) -> None:
    token = _token(client, agent, "secret", "call-1")
    assert REFUSED in _call(client, agent, "secret", "call-2", token)


def test_a_token_for_another_function_is_refused(client: TestClient, agent: AgentBase) -> None:
    token = _token(client, agent, "other", "call-1")
    assert REFUSED in _call(client, agent, "secret", "call-1", token)


def test_a_function_marked_not_secure_needs_no_token(client: TestClient, agent: AgentBase) -> None:
    assert _call(client, agent, "open", "call-1") == "ran open"
