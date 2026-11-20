"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

FrontDeskAgent: departments with hours, appointments, messages and answers
from documents, through the CallSimulator.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from signalwire.operations import Appointments, Messages, Slot
from signalwire.operations.infobot import InfoBotKnowledge
from signalwire.prefabs import Department, FrontDeskAgent
from signalwire.testing import CallSimulator


def said(args: dict[str, Any]) -> dict[str, Any]:
    return {**args, "data_supplied_by_user": True}


def desk(billing_open: bool = True, **kwargs: Any) -> FrontDeskAgent:
    async def billing_hours(call: Any) -> bool:
        return billing_open

    return FrontDeskAgent(
        role="You answer the phone for Bayside Dental.",
        departments={
            "billing": Department("questions about a bill", "+15550100001", open=billing_hours),
            "the hygienist": Department("questions about a cleaning", "+15550100002"),
        },
        appointments=Appointments(
            openings=lambda call, when, kind: [Slot("s1", "Tuesday at 2 pm")],
            book=lambda call, slot, kind, note: None,
        ),
        messages=Messages(save=lambda call, message: None),
        knowledge=InfoBotKnowledge(search=lambda q: [{"content": "We open at 8.", "score": 1}]),
        caller_id="+15550100000",
        suppress_logs=True,
        **kwargs,
    )


def test_every_part_it_was_given_is_offered() -> None:
    sim = CallSimulator(desk())
    assert {"transfer_to_human", "find_openings", "book_appointment", "take_message",
            "search_knowledge"} <= set(sim.offered())
    to = sim.functions["transfer_to_human"]["parameters"]["properties"]["to"]
    assert to["enum"] == ["billing", "the hygienist"]
    assert not sim.functions["transfer_to_human"].get("gates"), "callers say where to go"


def test_a_department_taking_calls_is_put_through() -> None:
    sim = CallSimulator(desk())
    out = sim.call("transfer_to_human", {"summary": "a bill", "to": "billing"})
    text = json.dumps(out.actions)
    assert "+15550100001" in text and "+15550100000" in text
    assert out.response == "The call is being transferred to billing."


def test_a_closed_department_offers_a_message() -> None:
    sim = CallSimulator(desk(billing_open=False))
    out = sim.call("transfer_to_human", {"summary": "a bill", "to": "billing"})
    assert out.response == "billing isn't taking calls now."
    assert out.tool_prompt == "Tell them, and offer to take a message with take_message."
    assert "+15550100001" not in json.dumps(out.actions)


def test_without_messages_a_closed_department_asks_how_else_to_help() -> None:
    agent = FrontDeskAgent(
        role="r",
        departments={"billing": Department("bills", "+15550100001", open=lambda call: False)},
        desk_wording={"closed": "{department} está cerrado ahora."},
        suppress_logs=True,
    )
    out = CallSimulator(agent).call("transfer_to_human", {"summary": "x", "to": "billing"})
    assert out.response == "billing está cerrado ahora."
    assert out.tool_prompt == "Tell them, and ask how else you can help."
    with pytest.raises(ValueError, match="FrontDeskAgent.WORDING"):
        FrontDeskAgent(role="r", desk_wording={"open": "x"}, suppress_logs=True)


def test_knowledge_is_offered_before_the_caller_is_identified() -> None:
    agent = desk()
    agent.identify(any_of=[["phone"]], find=lambda call, keys: "p1")
    sim = CallSimulator(agent)
    assert sim.step == "identify" and "search_knowledge" in sim.offered()
    assert "We open at 8." in sim.call("search_knowledge", {"query": "hours"}).response
