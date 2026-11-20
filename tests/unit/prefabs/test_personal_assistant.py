"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

PersonalAssistantAgent: screening, the whisper on the person's leg, and what
the caller is offered when they don't take it.
"""

from __future__ import annotations

from typing import Any

from signalwire.operations import Messages
from signalwire.prefabs import PersonalAssistantAgent
from signalwire.testing import CallSimulator


def said(args: dict[str, Any]) -> dict[str, Any]:
    return {**args, "data_supplied_by_user": True}


def assistant(available: bool = True, **kwargs: Any) -> PersonalAssistantAgent:
    return PersonalAssistantAgent(
        role="You answer Ann Lee's phone.",
        owner="Ann",
        reach="+15550100001",
        available=lambda call: available,
        messages=Messages(save=lambda call, message: None),
        suppress_logs=True,
        **kwargs,
    )


def swml_of(actions: list[Any]) -> dict[str, Any]:
    return next(a["SWML"] for a in actions if isinstance(a, dict) and "SWML" in a)


def test_it_asks_who_and_why_before_putting_through() -> None:
    sim = CallSimulator(assistant())
    out = sim.call("put_through", said({}))
    assert (out.tool_prompt or "").startswith("Ask them: Who's calling? What's it about?")


def test_putting_through_rings_them_with_the_whisper() -> None:
    sim = CallSimulator(assistant(whisper_voice="rime.spore", whisper_language="en-US"))
    out = sim.call("put_through", said({"name": "Bo", "reason": "the ${secret} contract"}))
    assert out.response == "Done. Seeing whether Ann can take it."
    assert out.tool_prompt == "Tell them you'll see if Ann can take it, and say nothing more."
    main = swml_of(out.actions)["sections"]["main"]
    connect = main[0]["connect"]
    assert connect["to"] == "+15550100001" and connect["timeout"] == 20 and "from" not in connect
    prompt = connect["confirm"][0]["prompt"]
    assert prompt["play"] == "say:Bo is calling about the secret} contract. Press 1 to take the call."
    assert (prompt["say_voice"], prompt["say_language"], prompt["initial_timeout"]) == ("rime.spore", "en-US", 15)
    refuse = connect["confirm"][1]["switch"]
    assert refuse["variable"] == "prompt_value" and refuse["default"] == [{"hangup": {}}]
    after = main[1]["switch"]
    assert after["case"] == {"connected": [{"hangup": {}}]}
    assert after["default"][0]["set"]["ai_response"] == (
        "Ann didn't take the call (${connect_failed_reason}). Tell them, and offer to take a message with "
        "take_message."
    )


def test_when_they_arent_taking_calls_a_message_is_offered() -> None:
    sim = CallSimulator(assistant(available=False))
    out = sim.call("put_through", said({"name": "Bo", "reason": "lunch"}))
    assert out.response == "Ann isn't taking calls now."
    assert out.tool_prompt == "Tell them, and offer to take a message with take_message."
    assert not any(isinstance(a, dict) and "SWML" in a for a in out.actions)


def test_the_accept_key_can_be_another() -> None:
    import pytest

    sim = CallSimulator(assistant(accept_key="5", assistant_wording={
        "whisper": "Llama {name} por {reason}. Pulse {key} para atender."}))
    out = sim.call("put_through", said({"name": "Bo", "reason": "el contrato"}))
    connect = swml_of(out.actions)["sections"]["main"][0]["connect"]
    assert connect["confirm"][0]["prompt"]["play"] == "say:Llama Bo por el contrato. Pulse 5 para atender."
    assert list(connect["confirm"][1]["switch"]["case"]) == ["5"]
    with pytest.raises(ValueError, match="one key"):
        assistant(accept_key="12")
