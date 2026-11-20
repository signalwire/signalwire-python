"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

What only a call can do (take a card, put someone through) says so in a chat,
and emits nothing.
"""

from __future__ import annotations

from typing import Any

from signalwire.operations import Charge, Messages, Payments, ServiceAgent
from signalwire.prefabs import Department, FrontDeskAgent, PersonalAssistantAgent
from signalwire.testing import CallSimulator


def said(args: dict[str, Any]) -> dict[str, Any]:
    return {**args, "data_supplied_by_user": True}


def in_chat(agent: Any) -> CallSimulator:
    return CallSimulator(agent, global_data=agent.ops.prefilled({"conversation_type": "chat"}))


def no_swml(actions: list[Any]) -> bool:
    return not any(isinstance(a, dict) and "SWML" in a for a in actions)


def test_a_payment_isnt_taken_in_a_chat() -> None:
    agent = ServiceAgent("b", role="r", currency="USD", suppress_logs=True)
    agent.add_language("English", "en-US", "rime.spore")
    Payments(connector_url="https://pay.example.com/c", charge=lambda call, x: Charge("5", "x")).add_to(agent)
    out = in_chat(agent).call("take_payment", said({"paying_for": "1"}))
    assert out.response == "A card payment is taken on a call, not in a chat."
    assert out.tool_prompt == "Tell them, and offer to take it when they call."


def test_nobody_is_put_through_from_a_chat() -> None:
    assistant = PersonalAssistantAgent(role="r", owner="Ann", reach="+15550100001",
                                       messages=Messages(save=lambda call, m: None), suppress_logs=True)
    out = in_chat(assistant).call("put_through", said({"name": "Bo", "reason": "lunch"}))
    assert out.response == "Ann can't be put through from a chat."
    assert out.tool_prompt == "Tell them, and offer to take a message with take_message." and no_swml(out.actions)
    desk = FrontDeskAgent(role="r", departments={"billing": Department("bills", "+15550100001")},
                          suppress_logs=True)
    out = in_chat(desk).call("transfer_to_human", {"summary": "x", "to": "billing"})
    assert out.response == "billing can't be reached from a chat." and no_swml(out.actions)
