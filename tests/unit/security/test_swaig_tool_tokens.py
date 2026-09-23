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


def test_a_tool_added_per_call_needs_its_token_too() -> None:
    """The token is checked by the agent that runs the function, so a secure
    tool registered by per-call configuration gets no pass."""
    agent = AgentBase(name="tokens", route="/agent")
    agent.add_per_call_config(
        lambda query, body, headers, copy: copy.define_tool(
            "dynamic", "Added per call.", {}, _handler("ran dynamic")))
    client = TestClient(agent.get_app())
    assert REFUSED in _call(client, agent, "dynamic", "call-1")
    token = _token(client, agent, "dynamic", "call-1")
    assert _call(client, agent, "dynamic", "call-1", token) == "ran dynamic"


def test_a_dotted_call_id_keeps_its_token(client: TestClient, agent: AgentBase) -> None:
    """Composed conversation ids such as "root.2" contain dots."""
    token = _token(client, agent, "secret", "chat-abc.1")
    assert _call(client, agent, "secret", "chat-abc.1", token) == "ran secret"


def _summary_agent() -> tuple[AgentBase, TestClient, list[Any]]:
    agent = AgentBase(name="summaries", route="/agent")
    agent.set_post_prompt("Summarize the call.")
    received: list[Any] = []
    agent.on_summary = lambda summary, raw_data=None: received.append(summary)  # type: ignore[method-assign]  # capture
    return agent, TestClient(agent.get_app()), received


def _post_prompt_query(client: TestClient, agent: AgentBase, call_id: str) -> str:
    swml = client.get(f"/agent/?call_id={call_id}", headers=_auth(agent)).json()
    ai = next(verb["ai"] for verb in swml["sections"]["main"] if "ai" in verb)
    url: str = ai["post_prompt_url"]
    return urlparse(url).query


def test_a_summary_for_a_dotted_call_id_is_delivered() -> None:
    agent, client, received = _summary_agent()
    query = _post_prompt_query(client, agent, "chat-abc.1")
    resp = client.post(f"/agent/post_prompt?{query}", headers=_auth(agent),
                       json={"call_id": "chat-abc.1", "summary": "Booked."})
    assert resp.status_code == 200
    assert received == ["Booked."]


def test_a_token_for_one_call_cant_deliver_another_calls_summary() -> None:
    agent, client, received = _summary_agent()
    query = _post_prompt_query(client, agent, "call-a")
    resp = client.post(f"/agent/post_prompt?call_id=call-a&{query}", headers=_auth(agent),
                       json={"call_id": "call-b", "summary": "Forged."})
    assert resp.status_code == 400
    assert received == []
