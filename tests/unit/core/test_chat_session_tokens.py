"""
A chat session's requests carry the token minted for its conversation.

The chat service fetches an agent's SWML under the conversation's id, so the
SDK mints that SWML's tokens (each secure function's, and the post-prompt
URL's) for the conversation id. It then sends every request under its own
runtime call id, with the conversation's id as ``conversation_id``. The SDK
compared the token with ``call_id`` alone, so in chat every post-prompt
summary was refused (seen in production: a chat to voice handoff whose
transcript never saved). In that trace the tool calls came under the
conversation id and passed; a secure function accepts either id too, in case
a request comes under the runtime one.
"""

import json
from typing import Any
from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient

from signalwire import AgentBase, FunctionResult

AUTH = ("user", "pass")
CONVERSATION = "chat--2A8gj_DXZDQc2tPtpKigQ6V"
RUNTIME_CALL = "78a8fdfa-8d7c-4a09-ad6d-9cd749516d32"


def _agent(summaries: list[Any]) -> AgentBase:
    agent = AgentBase(name="chat", route="/", basic_auth=AUTH, suppress_logs=True)
    agent.set_prompt_text("Help the caller.")
    agent.set_post_prompt("Summarize the conversation.")
    agent.on_summary = lambda summary, raw_data=None: summaries.append(raw_data)  # type: ignore[method-assign]  # capture the summary
    agent.define_tool(name="lookup", description="Look up", parameters={},
                      handler=lambda args, raw: FunctionResult("found"), secure=True)
    return agent


def _tokens(agent: AgentBase, call_id: str) -> tuple[str, str]:
    """The post-prompt and lookup tokens the SWML for ``call_id`` carries."""
    main = json.loads(agent._render_swml(call_id))["sections"]["main"]
    ai = next(verb["ai"] for verb in main if "ai" in verb)

    def token(url: str) -> str:
        return parse_qs(urlsplit(url).query)["__token"][0]

    lookup = next(f for f in ai["SWAIG"]["functions"] if f["function"] == "lookup")
    return token(ai["post_prompt_url"]), token(lookup["web_hook_url"])


def _post_prompt(client: TestClient, token: str, conversation_id: str | None) -> int:
    body: dict[str, Any] = {"call_id": RUNTIME_CALL, "action": "post_conversation",
                            "post_prompt_data": {"raw": "The caller asked about pricing."}}
    if conversation_id is not None:
        body["conversation_id"] = conversation_id
    return client.post(f"/post_prompt?__token={token}", json=body, auth=AUTH).status_code


def _call_lookup(client: TestClient, token: str, conversation_id: str | None) -> str:
    body: dict[str, Any] = {"function": "lookup", "argument": {"parsed": [{}]},
                            "call_id": RUNTIME_CALL}
    if conversation_id is not None:
        body["conversation_id"] = conversation_id
    response = client.post(f"/swaig?__token={token}", json=body, auth=AUTH)
    return str(response.json().get("response"))


def test_a_chat_summary_is_accepted_under_the_runtime_call_id() -> None:
    summaries: list[Any] = []
    agent = _agent(summaries)
    post_prompt_token, _ = _tokens(agent, CONVERSATION)
    with TestClient(agent.get_app()) as client:
        assert _post_prompt(client, post_prompt_token, CONVERSATION) == 200
    assert summaries and summaries[0]["call_id"] == RUNTIME_CALL


def test_a_secure_tool_runs_in_chat() -> None:
    agent = _agent([])
    _, lookup_token = _tokens(agent, CONVERSATION)
    with TestClient(agent.get_app()) as client:
        assert _call_lookup(client, lookup_token, CONVERSATION) == "found"


def test_the_token_still_has_to_name_this_conversation() -> None:
    agent = _agent([])
    post_prompt_token, lookup_token = _tokens(agent, CONVERSATION)
    with TestClient(agent.get_app()) as client:
        assert _post_prompt(client, post_prompt_token, "chat--another") == 403
        assert _post_prompt(client, post_prompt_token, None) == 403
        assert _call_lookup(client, lookup_token, "chat--another") != "found"
        assert _call_lookup(client, lookup_token, None) != "found"


def test_a_voice_call_is_unchanged() -> None:
    # On a call, the SWML and every request carry the same call id
    agent = _agent([])
    post_prompt_token, lookup_token = _tokens(agent, RUNTIME_CALL)
    with TestClient(agent.get_app()) as client:
        assert _post_prompt(client, post_prompt_token, None) == 200
        assert _call_lookup(client, lookup_token, None) == "found"
