"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The medium an operations agent works in: given (voice, chat) or found on each
call's first request, and the rules by key.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from signalwire import AgentBase
from signalwire.operations import Change, Operation, Operations, ServiceAgent
from signalwire.testing import CallSimulator


def with_cancel(ops: Any) -> Any:
    ops.writes_with(lambda call, w: None)

    @ops.operation(tool="cancel_order")
    class Cancel(Operation):
        """Cancel an order."""

        def prepare(self, call: Any, f: Any) -> Change:
            return Change(read_back=f"Cancel it ({call.medium or 'no medium'}). Shall I?")

    return ops


def rules_of(agent: AgentBase) -> list[str]:
    assert agent.pom is not None
    return list(next(s for s in agent.pom.to_dict() if s["title"] == "Rules")["bullets"])


def ai_of(swml: str) -> dict[str, Any]:
    doc = json.loads(swml)
    return next(v["ai"] for v in doc["sections"]["main"] if "ai" in v)


def test_a_service_given_a_medium_says_it_in_its_rules() -> None:
    voice = with_cancel(Operations(role="r", medium="voice")).install(AgentBase(name="v", suppress_logs=True))
    assert rules_of(voice)[0] == "This is a phone call. Keep each reply short, but give every fact the caller asks for."
    chat = with_cancel(Operations(role="r", medium="chat")).install(AgentBase(name="c", suppress_logs=True))
    assert rules_of(chat)[0].startswith("This is a chat. Keep each reply short")
    with pytest.raises(ValueError, match="voice, chat"):
        Operations(role="r", medium="fax")


def test_without_a_medium_the_rules_assume_none() -> None:
    agent = with_cancel(Operations(role="r")).install(AgentBase(name="n", suppress_logs=True))
    assert rules_of(agent)[0] == "Keep each reply short, but give every fact the caller asks for."
    assert agent._global_data["ops"]["medium"] == ""


def test_rules_change_by_key_or_are_replaced_by_a_list() -> None:
    keyed = with_cancel(Operations(role="r", rules={"facts": None, "tone": "Be warm."}))
    assert rules_of(keyed.install(AgentBase(name="k", suppress_logs=True))) == [
        "Keep each reply short, but give every fact the caller asks for.",
        "Nothing changes until the caller says yes to a change read back to them and it is confirmed.",
        "Be warm.",
    ]
    listed = with_cancel(Operations(role="r", rules=["Only this."], medium="voice"))
    assert rules_of(listed.install(AgentBase(name="l", suppress_logs=True))) == ["Only this."]
    lookups_only = Operations(role="r")
    lookups_only.lookup("Hours.")(lambda call: "9 to 5")
    assert len(rules_of(lookups_only.install(AgentBase(name="h", suppress_logs=True)))) == 2


def test_the_first_request_shows_the_medium() -> None:
    ops = with_cancel(Operations(role="r"))
    chat = ops.prefilled({"conversation_type": "chat"})
    assert chat is not None and chat["ops"]["medium"] == "chat"
    assert chat["ops"]["now"] == "This is a chat."
    voice = ops.prefilled({"call": {"call_id": "c1"}})
    assert voice is not None and voice["ops"]["medium"] == "voice"
    assert ops.prefilled({}) is None and ops.prefilled({"conversation_type": "fax"}) is None
    fixed = with_cancel(Operations(role="r", medium="voice"))
    assert fixed.prefilled({"conversation_type": "chat"}) is None, "a service's own medium stands"


def test_call_medium_is_the_services_or_the_calls() -> None:
    ops = with_cancel(Operations(role="r"))
    agent = ops.install(AgentBase(name="m", suppress_logs=True))
    sim = CallSimulator(agent, global_data=ops.prefilled({"conversation_type": "chat"}))
    out = sim.call("cancel_order", {"data_supplied_by_user": True})
    assert "Cancel it (chat)" in out.response
    assert sim.global_data["ops"]["now"].startswith("This is a chat.\nWaiting for their answer")


def test_service_agent_starts_each_call_with_its_record_on_both_render_paths() -> None:
    agent = with_cancel(ServiceAgent("s", role="r", suppress_logs=True))
    mods = agent.on_swml_request({"conversation_type": "chat"})
    assert mods is not None and mods["global_data"]["ops"]["medium"] == "chat"
    # With a per-request callback the SWML renders on a copy, which gets the record itself
    seen: list[str] = []
    agent.set_dynamic_config_callback(lambda q, body, h, copy: seen.append(str(body.get("conversation_type"))))
    marker = agent.on_swml_request({"conversation_type": "chat"})
    assert marker is not None and marker.get("__use_ephemeral_agent")
    ai = ai_of(agent._render_swml(None, marker))
    assert seen == ["chat"] and ai["global_data"]["ops"]["medium"] == "chat"
    plain = ai_of(agent._render_swml())
    assert plain["global_data"]["ops"]["medium"] == "", "the agent itself is left as it was"
