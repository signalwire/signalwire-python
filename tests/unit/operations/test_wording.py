"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The words an operations agent generates come from DEFAULT_WORDING, and any of
them can be replaced: checked when the service is made, filled in when used.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from signalwire import AgentBase
from signalwire.operations import (
    DEFAULT_WORDING,
    Change,
    Field,
    Operation,
    Operations,
    Refuse,
    Write,
)
from signalwire.operations.wording import placeholders
from signalwire.testing import CallSimulator


def said(args: dict[str, Any]) -> dict[str, Any]:
    return {**args, "data_supplied_by_user": True}


def shop(**kwargs: Any) -> Operations:
    ops = Operations(role="You run a shop.", **kwargs)
    ops.writes_with(lambda call, w: None)
    ops.transfer_with(lambda call, summary: None)

    @ops.operation(tool="cancel_order")
    class Cancel(Operation):
        """Cancel an order."""

        order_id = Field(str, "The order.")

        def prepare(self, call: Any, f: Any) -> Change:
            if f.order_id == "#shipped":
                raise Refuse("Nothing can change once it ships.")
            return Change(read_back=f"Cancel {f.order_id}. Shall I?", touches=[f.order_id],
                          writes=[Write("cancel", order_id=f.order_id)])

    return ops


def test_every_default_fills_in_with_only_its_own_placeholders() -> None:
    for key, text in DEFAULT_WORDING.items():
        assert key == key.lower() and isinstance(text, str)
        assert all(p.isidentifier() for p in placeholders(text))


def test_overrides_reach_the_steps_tools_results_and_notice() -> None:
    ops = shop(wording={
        "step.main": "Atiende lo que pidan. {help}",
        "tool.confirm": "Haz el cambio leído, cuando digan que sí.",
        "decline.then": "Diles que queda como estaba.",
        "transfer.notice": "Un momento, le paso con una persona.",
        "list.and": " y ",
    })
    agent = ops.install(AgentBase(name="t", suppress_logs=True))
    steps = {s["name"]: s for s in agent.define_contexts().to_dict()["default"]["steps"]}
    assert steps["main"]["text"].startswith("Atiende lo que pidan. To make a change")
    sim = CallSimulator(agent)
    assert sim.functions["confirm_change"]["description"] == "Haz el cambio leído, cuando digan que sí."
    sim.call("cancel_order", said({"order_id": "#1"}))
    declined = sim.call("decline_change", {"change": "cancel"})
    assert (declined.tool_prompt or "").startswith("Diles que queda como estaba.")
    sim.caller("I want a person")
    moved = sim.call("transfer_to_human", {"summary": "wants a person"})
    assert "Un momento, le paso con una persona." in json.dumps(moved.actions, ensure_ascii=False)


def test_an_override_can_drop_placeholders_and_keeps_platform_variables() -> None:
    ops = shop(wording={"step.main": "Help them. Today: ${global_data.today}"})
    agent = ops.install(AgentBase(name="t", suppress_logs=True))
    main = agent.define_contexts().to_dict()["default"]["steps"][0]
    assert main["text"] == "Help them. Today: ${global_data.today}"


def test_an_unknown_key_or_placeholder_fails_when_the_service_is_made() -> None:
    with pytest.raises(ValueError, match="no wording 'step.mian'"):
        shop(wording={"step.mian": "x"})
    with pytest.raises(ValueError, match=r"\{order\}.*can use \{account\}, \{help\}"):
        Operations(role="r", wording={"step.main": "{order} {help}"})
    with pytest.raises(TypeError):
        Operations(role="r", wording={"step.main": 3})  # type: ignore[dict-item]


def test_the_service_prefixes_a_refusal_of_the_developers_own() -> None:
    sim = CallSimulator(shop(wording={"refused.prefix": "Sin cambios: "}).install(
        AgentBase(name="t", suppress_logs=True)))
    out = sim.call("cancel_order", said({"order_id": "#shipped"}))
    assert out.response == "Sin cambios: Nothing can change once it ships."


def test_a_plain_filler_list_is_for_every_language() -> None:
    ops = shop()

    @ops.lookup("Hours.", fields={}, fillers=["One moment."])
    def hours(call: Any) -> str:
        return "9 to 5."

    sim = CallSimulator(ops.install(AgentBase(name="t", suppress_logs=True)))
    assert sim.functions["hours"]["fillers"] == {"default": ["One moment."]}
