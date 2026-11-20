"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

An Operations installed beside the agent's own setup and beside another
Operations: namespaced names, the record's key and version, the agent's own
prompt sections and initial step.
"""

from __future__ import annotations

from typing import Any

import pytest

from signalwire import AgentBase
from signalwire.operations import Change, Field, Operation, Operations, ServiceAgent, Write
from signalwire.operations.record import RECORD_VERSION
from signalwire.testing import CallSimulator

WRITES: list[tuple[str, dict[str, Any]]] = []


def said(args: dict[str, Any]) -> dict[str, Any]:
    return {**args, "data_supplied_by_user": True}


def service(namespace: str | None, kind: str, **kwargs: Any) -> Operations:
    ops = Operations(role=f"You handle {kind}.", namespace=namespace, **kwargs)
    ops.writes_with(lambda call, w: WRITES.append((w.name, dict(w.args))))

    @ops.operation(tool=f"change_{kind}", kind=kind)
    class Change_(Operation):
        """Change something."""

        what = Field(str, "What to change.")

        def prepare(self, call: Any, f: Any) -> Change:
            return Change(
                read_back=f"Change the {kind} {f.what}. Shall I?",
                touches=[f"{kind}:{f.what}"],
                writes=[Write(f"{kind}_write", what=f.what)],
            )

    return ops


def test_a_namespace_names_everything_it_generates() -> None:
    ops = service("billing", "plan")
    ops.identify(any_of=[["email"]], find=lambda call, keys: "a1")
    ops.transfer_with(lambda call, summary: None)
    ops.operation(type("Note", (Operation,), {
        "__doc__": "Add a note.", "guidance": "Ask what the note says.",
        "prepare": lambda self, call, f: Change(read_back="Add it?", writes=[]),
    }))
    agent = ops.install(AgentBase(name="t", suppress_logs=True))
    tools = set(agent._tool_registry._swaig_functions)
    assert {"confirm_billing_change", "decline_billing_change", "billing_transfer_to_human",
            "billing_find_account", "change_plan"} <= tools
    assert not {"confirm_change", "decline_change", "transfer_to_human", "find_account"} & tools
    contexts = agent.define_contexts().to_dict()
    steps = {s["name"] for s in contexts["default"]["steps"]}
    assert steps == {"billing_identify", "billing_main", "billing_confirm", "billing_note"}
    assert "billing_transferred" in contexts
    record = agent._global_data["billing"]
    assert record["v"] == RECORD_VERSION == 1 and "ops" not in agent._global_data
    assert "${global_data.billing.now}" in agent._params["conscience"]
    main = next(s for s in contexts["default"]["steps"] if s["name"] == "billing_main")
    assert "${global_data.billing.account}" in main["text"]


def test_without_a_namespace_the_names_are_plain() -> None:
    agent = service(None, "plan").install(AgentBase(name="t", suppress_logs=True))
    assert {"confirm_change", "decline_change"} <= set(agent._tool_registry._swaig_functions)
    assert agent._global_data["ops"]["v"] == RECORD_VERSION


def test_a_namespace_must_be_lower_case_words() -> None:
    for bad in ("Billing", "1st", "bill-ing", ""):
        with pytest.raises(ValueError, match="namespace"):
            Operations(role="r", namespace=bad)


def test_a_second_service_without_a_namespace_says_how_to_fix_it() -> None:
    agent = service(None, "plan").install(AgentBase(name="t", suppress_logs=True))
    with pytest.raises(ValueError, match="namespace="):
        service(None, "order").install(agent)


def test_two_services_on_one_agent_keep_their_changes_apart() -> None:
    WRITES.clear()
    agent = AgentBase(name="t", suppress_logs=True)
    billing = service("billing", "plan")
    orders = service("orders", "order")
    # Each offers the other's tools in its own steps (named as generated: "main", "confirm")
    billing.offer("change_order", "confirm_orders_change", "decline_orders_change", steps=["main", "confirm"])
    orders.offer("change_plan", "confirm_billing_change", "decline_billing_change", steps=["main", "confirm"])
    billing.install(agent)
    orders.install(agent)
    sim = CallSimulator(agent)
    assert sim.step == "billing_main", "the first service's main step starts the call"
    sim.call("change_plan", said({"what": "gold"}))
    assert sim.step == "billing_confirm"
    sim.call("change_order", said({"what": "#1"}))
    assert sim.global_data["billing"]["waiting"]["kind"] == "plan"
    assert sim.global_data["orders"]["waiting"]["kind"] == "order" and sim.step == "orders_confirm"
    # The yes the platform's gate heard is to the orders read-back: billing's is read again, nothing written
    sim.caller("yes")
    again = sim.call("confirm_billing_change", {"change": "plan"})
    assert "read to them again" in again.response and WRITES == []
    sim.caller("yes")
    done = sim.call("confirm_billing_change", {"change": "plan"})
    assert done.ran and WRITES == [("plan_write", {"what": "gold"})]


def test_install_adds_to_the_agents_own_sections_and_keeps_its_initial_step() -> None:
    agent = AgentBase(name="t", suppress_logs=True)
    agent.prompt_add_section("Role", body="You work for Acme.")
    agent.prompt_add_section("Rules", bullets=["Be kind.", "Never guess."])
    ctx = agent.define_contexts().add_context("default")
    ctx.add_step("welcome").set_text("Greet them.")
    ctx.set_initial_step("welcome")
    service(None, "plan", rules=["Never guess.", "Read changes back."]).install(agent)
    assert agent.pom is not None
    sections = agent.pom.to_dict()
    assert [s["title"] for s in sections] == ["Role", "Rules"]
    assert sections[0]["body"] == "You work for Acme.\n\nYou handle plan."
    assert sections[1]["bullets"] == ["Be kind.", "Never guess.", "Read changes back."]
    assert CallSimulator(agent).step == "welcome"


def test_call_go_main_moves_to_the_namespaced_main_step() -> None:
    ops = service("billing", "plan")
    ops.phase("intro", "Say hello.", initial=True)

    @ops.lookup("Their plan.", tool="plan_info")
    def plan_info(call: Any) -> str:
        call.go("main")
        return "Gold."

    sim = CallSimulator(ops.install(AgentBase(name="t", suppress_logs=True)))
    assert sim.step == "intro"
    sim.call("plan_info", {})
    assert sim.step == "billing_main"


def test_record_text_reads_the_record_from_global_data() -> None:
    ops = service("billing", "plan")
    assert ops.record_text({"billing": {"asked": "a new plan"}}) == "What they asked for: a new plan"
    assert ops.record_text({}) == ""


def test_service_agent_passes_operations_arguments_on() -> None:
    agent = ServiceAgent("shop", role="You run a shop.", namespace="shop", rules=["One rule."],
                         suppress_logs=True)
    assert agent.ops._names.record == "shop"
    assert agent.ops._rules == ["One rule."]


def test_service_agents_registration_methods_are_its_own() -> None:
    # Methods of the class, so the reference lists them, and the ones that set something up chain on the agent
    for name in ("operation", "lookup", "phase", "offer", "confirm_gates", "identify", "writes_with", "transfer_with"):
        assert name in vars(ServiceAgent), name
    agent = ServiceAgent("s", role="r", suppress_logs=True)
    assert agent.phase("intro", "Say hello.") is agent and agent.offer("weather") is agent
    assert agent.ops._phases[0][0] == "intro" and agent.ops._offers[0][0] == ["weather"]
    assert agent.confirm_gates()[0].id == "agreed"
