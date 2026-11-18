"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Operations beside the rest of an agent: tools it didn't make, other layers'
steps and conscience, routers, platform actions, optional and prefilled
identity, one field at a time.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from signalwire import AgentBase, FunctionResult
from signalwire.operations import Change, Field, Operation, Operations, Refuse, ServiceAgent, Write
from signalwire.testing import CallSimulator


def said(args: dict[str, Any]) -> dict[str, Any]:
    return {**args, "data_supplied_by_user": True}


def booking_agent(**identify: Any) -> ServiceAgent:
    agent = ServiceAgent("bistro", role="You take bookings for a bistro.")
    agent.identify(any_of=[["phone"]], find=lambda call, keys: "g1" if keys.get("phone") == "555" else None,
                   describe=lambda call: "Guest g1", **identify)
    agent.writes_with(lambda call, w: None)

    @agent.operation(tool="book_table")
    class Book(Operation):
        """Book a table."""

        party = Field(int, "How many people.", ask="How many people is it for?")
        when = Field(str, "The day and time.", ask="What day and time?")
        before_identity = True
        ask_in_order = True

        def prepare(self, call: Any, f: Any) -> Change:
            return Change(read_back=f"A table for {f.party} at {f.when}. Shall I book it?",
                          touches=[f"slot:{f.when}"], writes=[Write("book", party=f.party, when=f.when)])

    @agent.operation(tool="cancel_booking")
    class CancelBooking(Operation):
        """Cancel their booking."""

        def prepare(self, call: Any, f: Any) -> Change:
            return Change(read_back="Cancel your booking. Shall I?", touches=["booking"], writes=[Write("cancel")])

    return agent


def test_optional_identity_starts_in_main_and_gates_only_what_needs_it() -> None:
    sim = CallSimulator(booking_agent(required=False))
    assert sim.step == "main"
    assert "find_account" in sim.offered() and "identify" not in json.dumps(sim._contexts)
    refused = sim.call("cancel_booking", said({}))
    assert "Their account isn't found yet." in refused.response
    first = sim.call("book_table", said({"party": None, "when": None}))
    assert first.tool_prompt.startswith("Ask them: How many people is it for?") and "What day" not in first.tool_prompt
    booked = sim.call("book_table", said({"party": 2, "when": "Friday at 7"}))
    assert booked.ran and sim.step == "confirm"
    found = sim.call("find_account", said({"phone": "555", "asked_for": ""}))
    assert "Found their account" in found.response and sim.step == "confirm", "identify doesn't move the call"


def test_prefill_starts_the_call_identified() -> None:
    agent = booking_agent(prefill=lambda request_data, request: {"phone": (request_data or {}).get("caller_id_num")})
    known = agent.ops.prefilled({"caller_id_num": "555"})
    assert known and known["ops"]["account_id"] == "g1" and known["ops"]["account"] == "Guest g1"
    assert agent.ops.prefilled({"caller_id_num": "000"}) is None
    mods = agent.on_swml_request({"caller_id_num": "555"})
    assert mods["global_data"]["ops"]["account_id"] == "g1"
    sim = CallSimulator(agent, global_data=mods["global_data"])
    assert sim.step == "main"
    out = sim.call("cancel_booking", said({}))
    assert out.ran and sim.step == "confirm"


def test_offer_puts_other_tools_in_the_generated_steps() -> None:
    agent = booking_agent()
    agent.define_tool("weather", "Today's weather.", {}, lambda args, raw: FunctionResult("Sunny."))
    agent.define_tool("menu", "The menu.", {}, lambda args, raw: FunctionResult("Soup."))
    agent.offer("weather", before_identity=True)
    agent.offer("menu", where=["main"])
    sim = CallSimulator(agent)
    assert sim.step == "identify" and "weather" in sim.offered() and "menu" not in sim.offered()
    sim.call("find_account", said({"phone": "555", "asked_for": ""}))
    assert {"weather", "menu"} <= set(sim.offered())


def test_router_destinations_ungated_with_connect() -> None:
    agent = ServiceAgent("front", role="You route calls.")
    agent.transfer_with(
        lambda call, summary, to: FunctionResult().connect({"sales": "+15550001", "support": "+15550002"}[to]),
        destinations={"sales": "buying something new", "support": "help with something they have"},
        gated=False, tool="route_call", notice="Connecting you now.",
    )
    sim = CallSimulator(agent)
    assert "route_call" in sim.offered()
    fn = sim.functions["route_call"]
    assert not fn.get("gates") and fn["parameters"]["properties"]["to"]["enum"] == ["sales", "support"]
    out = sim.call("route_call", {"summary": "wants to buy", "to": "sales"})
    assert out.response == "The call is being transferred to sales."
    text = json.dumps(out.actions)
    assert "Connecting you now." in text and "+15550001" in text
    wrong = asyncio.run(agent.ops._transfer_handler({"summary": "", "to": "billing"}, {"global_data": {}}))
    assert "isn't one of the places it goes" in wrong.to_dict()["response"]["tool_result"]


def test_refused_transfer_can_move_the_call() -> None:
    agent = ServiceAgent("bistro2", role="r")

    def closed(call: Any, summary: str) -> None:
        call.go("message")
        raise Refuse("The host stand is closed.", "Offer to take a message.")

    agent.transfer_with(closed, gated=False)
    agent.phase("message", "Take a message.", [])
    sim = CallSimulator(agent)
    out = sim.call("transfer_to_human", {"summary": "wants the host"})
    assert out.response == "The host stand is closed." and sim.step == "message"


def test_act_adds_platform_actions_last() -> None:
    agent = ServiceAgent("bye", role="r")
    agent.writes_with(lambda call, w: None)

    @agent.operation(tool="finish")
    class Finish(Operation):
        """Say goodbye and end the call."""

        confirm = False

        def prepare(self, call: Any, f: Any) -> Change:
            call.act(FunctionResult().say("Goodbye!").hangup())
            return Change(read_back="", done="Ending the call.")

    out = CallSimulator(agent).call("finish", said({}))
    assert [next(iter(a)) for a in out.actions][-2:] == ["say", "hangup"]


def test_another_layer_installs_beside_it() -> None:
    agent = AgentBase(name="both", route="/both", suppress_logs=True)
    agent.set_param("conscience", "${global_data.infobot.now}")
    ctx = agent.define_contexts().add_context("default")
    ctx.add_step("main").add_section("Knowledge", "Answer from search_knowledge.").set_functions(["search_knowledge"])
    agent.define_tool("search_knowledge", "Search the knowledge base.", {}, lambda a, r: FunctionResult("..."))
    ops = Operations(role="You help customers.")
    ops.writes_with(lambda call, w: None)

    @ops.operation(tool="cancel_order")
    class Cancel(Operation):
        """Cancel an order."""

        def prepare(self, call: Any, f: Any) -> Change:
            return Change(read_back="Cancel it. Shall I?")

    ops.install(agent)
    contexts = agent.define_contexts().to_dict()
    main = next(s for s in contexts["default"]["steps"] if s["name"] == "main")
    assert main["functions"][:2] == ["search_knowledge", "cancel_order"]
    assert "Answer from search_knowledge." in main["text"] and "cancel_order" in main["text"]
    assert agent._params["conscience"] == "${global_data.infobot.now}\n\n${global_data.ops.now}"


def test_no_operations_means_no_change_rule_and_no_record() -> None:
    agent = ServiceAgent("faq", role="You answer questions.")

    @agent.lookup("Opening hours.", fields={})
    def hours(call: Any) -> str:
        return "9 to 5."

    sim = CallSimulator(agent)
    prompt = json.dumps(json.loads(agent._render_swml()))
    assert "Nothing changes until" not in prompt
    assert "ops" not in sim.global_data and "conscience" not in sim.params


def test_fillers_by_language_pass_through() -> None:
    agent = ServiceAgent("es", role="r")

    @agent.lookup("Hours.", fields={}, fillers={"es-ES": ["Un momento."], "en-US": ["One moment."]})
    def hours(call: Any) -> str:
        return "9 a 5."

    fn = CallSimulator(agent).functions["hours"]
    assert fn["fillers"] == {"es-ES": ["Un momento."], "en-US": ["One moment."]}
