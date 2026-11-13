"""
CallSimulator: an agent's tools through a simulated call, checked as the
platform checks them: the current step's function list, the semantic gates,
and each result's actions on the call's state.
"""

from pathlib import Path
from typing import Any

import pytest

from signalwire import AgentBase, DataMap, FunctionResult
from signalwire.core.post_prompt import caller_turns
from signalwire.patterns import Proposal
from signalwire.testing import CallSimulator, RequestRecorder

ITEM: dict[str, Any] = {
    "type": "object",
    "properties": {"item": {"type": "string", "description": "The item"}},
    "required": ["item"],
}


def _shop() -> AgentBase:
    agent = AgentBase(name="shop", route="/", basic_auth=("u", "p"), suppress_logs=True)
    order = Proposal("place_order", decline_tool="change_order")
    agent.set_global_data({"store": "Main Street"})

    def review_order(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
        return order.propose(f"That's {args['item']}. Is that right?", raw_data=raw,
                             details={"item": args["item"]}).swml_change_step("confirm")

    def place_order(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
        item = raw["global_data"]["semantic_state"]["item"]
        return order.complete(f"The {item} is ordered.").swml_change_step("done")

    def change_order(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
        return FunctionResult("What would you like instead?").swml_change_step("take_order")

    def hang_up(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
        return FunctionResult("Goodbye.").hangup()

    agent.define_tool("review_order", "Read the order back", ITEM, review_order)
    agent.define_tool("place_order", "Place the order", {}, place_order,
                      gates=order.confirm_gates())
    agent.define_tool("change_order", "Change the order", {}, change_order)
    agent.define_tool("hang_up", "End the call", {}, hang_up)
    ctx = agent.define_contexts().add_context("default")
    ctx.add_step("take_order").set_text("Take the order.").set_functions(["review_order"])
    ctx.add_step("confirm").set_text("Confirm it.").set_functions(
        ["place_order", "change_order"])
    ctx.add_step("done").set_text("Say goodbye.").set_functions(["hang_up"])
    return agent


class TestSteps:
    def test_it_starts_in_the_first_step(self) -> None:
        sim = CallSimulator(_shop())
        assert (sim.context, sim.step) == ("default", "take_order")
        assert sim.offered() == ["review_order"]
        assert sim.global_data == {"store": "Main Street"}

    def test_a_tool_the_step_doesnt_offer_doesnt_run(self) -> None:
        sim = CallSimulator(_shop())
        refused = sim.call("place_order")
        assert (refused.ran, refused.blocked_by) == (False, "step")
        assert refused.response == (
            "Nothing ran: place_order isn't available at this point in the call. "
            "The steps that offer it: confirm. The tools available now are: review_order.")

    def test_an_unknown_tool(self) -> None:
        assert CallSimulator(_shop()).call("refund").response == (
            "Nothing ran: there is no tool named refund. "
            "The tools available now are: review_order.")

    def test_the_agents_own_unavailable_response(self) -> None:
        agent = _shop()
        agent.set_param("unavailable_function_response",
                        "${function} can't run here (${steps}); use ${tools}.")
        assert CallSimulator(agent).call("place_order").response == (
            "place_order can't run here (confirm); use review_order.")


class TestTheConfirmFlow:
    def test_a_yes_places_the_order(self) -> None:
        sim = CallSimulator(_shop(), gates=lambda gate, sim, args: True)
        sim.caller("A large tea, please.")
        review = sim.call("review_order", {"item": "a large tea"})
        assert review.ran and sim.step == "confirm"
        assert sim.call_log[-2]["content"] == "That's a large tea. Is that right?"
        assert sim.semantic_state["proposal"] == "That's a large tea. Is that right?"
        assert sim.waiting_for_user
        sim.caller("Yes.")
        placed = sim.call("place_order")
        assert placed.ran
        assert sim.step == "done"
        assert sim.semantic_state == {"done": "The a large tea is ordered."}

    def test_a_gate_that_fails_blocks_it(self) -> None:
        def answers(gate: dict[str, Any], sim: CallSimulator, args: dict[str, Any]) -> Any:
            return 0.2 if gate["id"] == "agreed" else 0.99

        sim = CallSimulator(_shop(), gates=answers)
        sim.call("review_order", {"item": "a tea"})
        sim.caller("Hmm, what sizes are there?")
        blocked = sim.call("place_order")
        assert (blocked.ran, blocked.blocked_by) == (False, "agreed")
        assert blocked.response == "place_order was not run. The caller has not said yes to this change."
        # The platform expands the gate's output from the call's data
        assert '"That\'s a tea. Is that right?"' in (blocked.tool_prompt or "")
        assert sim.chaining is False
        assert sim.step == "confirm"

    def test_an_unclear_gate(self) -> None:
        sim = CallSimulator(_shop(), gates=lambda gate, sim, args: "unclear")
        sim.call("review_order", {"item": "a tea"})
        assert sim.call("place_order").blocked_by == "answered"


class TestActions:
    def test_hangup_ends_the_call(self) -> None:
        sim = CallSimulator(_shop())
        sim.call("review_order", {"item": "a tea"})
        sim.call("place_order")
        sim.call("hang_up")
        assert sim.ended
        with pytest.raises(RuntimeError, match="ended"):
            sim.call("hang_up")

    def test_toggle_functions(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("unlock", "Unlock", {}, lambda a, r: FunctionResult("ok").toggle_functions(
            [{"function": "secret", "active": True}, {"function": "unlock", "active": False}]))
        agent.define_tool("secret", "Secret", {}, lambda a, r: "shh")
        sim = CallSimulator(agent)
        assert sim.offered() == ["secret", "unlock"]
        sim.call("unlock")
        assert sim.offered() == ["secret"]

    def test_unset_global_data(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.set_global_data({"a": 1, "b": 2})
        agent.define_tool("forget", "Forget", {}, lambda a, r: FunctionResult("ok").remove_global_data("a"))
        sim = CallSimulator(agent)
        sim.call("forget")
        assert sim.global_data == {"b": 2}


class TestRequests:
    def test_the_handler_gets_a_request_like_the_platforms(self) -> None:
        seen: list[dict[str, Any]] = []

        def find_store(args: dict[str, Any], raw: dict[str, Any]) -> str:
            seen.append(raw)
            return "Store 12"

        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("find_store", "Find", {}, find_store, needs_conversation=True)
        sim = CallSimulator(agent, call_id="call-9")
        sim.caller("My ZIP is 10001.")
        sim.call("find_store", {"zip": "10001"})
        raw = seen[0]
        assert (raw["function"], raw["call_id"]) == ("find_store", "call-9")
        assert raw["argument"]["parsed"] == [{"zip": "10001"}]
        assert raw["tool_call_id"].startswith("call-9-tool-")
        assert caller_turns(raw) == ["My ZIP is 10001."]

    def test_a_data_map_tool_needs_a_stub(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.register_swaig_function(
            DataMap("weather").description("Weather").webhook("GET", "https://api.example.com/w")
            .output(FunctionResult("Sunny")).to_swaig_function())
        with pytest.raises(ValueError, match="stub"):
            CallSimulator(agent).call("weather")
        stubbed = CallSimulator(agent, stubs={"weather": lambda args: "Sunny in Rome"})
        assert stubbed.call("weather").response == "Sunny in Rome"

    def test_recorded_requests_replay(self, tmp_path: Path) -> None:
        path = tmp_path / "requests.jsonl"
        agent = _shop()
        recorder = RequestRecorder(path)
        agent.add_tool_middleware(recorder)
        sim = CallSimulator(agent)
        sim.call("review_order", {"item": "a tea"})
        assert len(recorder.requests) == 1
        replayed = CallSimulator(agent).replay(RequestRecorder.load(path))
        assert [(r.name, r.args) for r in replayed] == [("review_order", {"item": "a tea"})]
        assert replayed[0].response == "Read back to the caller: That's a tea. Is that right?"


class TestNavigation:
    def test_next_step_follows_valid_steps(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("one").set_text("One").set_valid_steps(["next"])
        ctx.add_step("two").set_text("Two").set_valid_steps(["one"])
        sim = CallSimulator(agent)
        assert "next_step" in sim.offered()
        assert sim.call("next_step", {"step": "next"}).ran and sim.step == "two"
        assert sim.call("next_step", {"step": "two"}).ran is False
        assert sim.call("next_step", {"step": "one"}).ran and sim.step == "one"
