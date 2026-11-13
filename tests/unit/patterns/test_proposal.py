"""
The confirm pattern: a function reads a change back and records it, and the
confirm tool's gates judge the caller's answer on the proposal's dialogue.

The platform starts a proposal when semantic_state changes, as of the start
of the action object that sets it, and a say in that object runs first, so
the read-back is the proposal's first turn (SEMANTIC_GATES.md §2). Setting
the same state again marks nothing, so asking again needs a new revision.
"""

import json
from typing import Any

import pytest

from signalwire import AgentBase
from signalwire.core.semantic_gate import gate_definitions
from signalwire.patterns import Proposal, current

READ_BACK = "That's a large tea for pickup at five. Is that right?"


def _raw(state: dict[str, Any] | None) -> dict[str, Any]:
    return {"global_data": {"semantic_state": state} if state is not None else {}}


class TestPropose:
    def test_the_read_back_and_the_state_are_one_action(self) -> None:
        result = Proposal("place_order").propose(READ_BACK, details={"item": "tea"}).to_dict()
        assert result["action"][0] == {
            "say": READ_BACK,
            "set_global_data": {"semantic_state": {
                "item": "tea", "proposal": READ_BACK, "revision": 1}},
        }
        assert result["action"][1] == {"wait_for_user": True}
        assert len(result["action"]) == 2

    def test_the_model_is_told_what_to_wait_for(self) -> None:
        response = Proposal("place_order", decline_tool="change_order").propose(
            READ_BACK).to_dict()["response"]
        assert response["tool_result"] == f"Read back to the caller: {READ_BACK}"
        assert "Call place_order only when they say yes" in response["tool_prompt"]
        assert "call change_order" in response["tool_prompt"]

    def test_a_new_proposal_gets_the_next_revision(self) -> None:
        raw = _raw({"proposal": "older", "revision": 3})
        state = Proposal("place_order").propose(READ_BACK, raw_data=raw).to_dict()[
            "action"][0]["set_global_data"]["semantic_state"]
        assert state["revision"] == 4

    def test_asking_again_reads_the_same_change_as_a_new_revision(self) -> None:
        raw = _raw({"proposal": READ_BACK, "revision": 1, "item": "tea"})
        first = Proposal("place_order").ask_again(raw).to_dict()["action"][0]
        assert first["say"] == READ_BACK
        assert first["set_global_data"]["semantic_state"] == {
            "item": "tea", "proposal": READ_BACK, "revision": 2}

    def test_asking_again_needs_a_proposal(self) -> None:
        with pytest.raises(ValueError, match="no proposal"):
            Proposal("place_order").ask_again(_raw({"done": "x"}))

    def test_complete_records_what_was_done(self) -> None:
        result = Proposal("place_order").complete("Order 4471 is placed.").to_dict()
        assert result["action"] == [{"set_global_data": {"semantic_state": {
            "done": "Order 4471 is placed."}}}]


class TestConfirmGates:
    def test_three_gates_on_the_proposal_dialogue(self) -> None:
        gates = [g.to_dict() for g in Proposal("place_order").confirm_gates()]
        assert [g["id"] for g in gates] == ["answered", "agreed", "read_back"]
        assert {(g["dialogue"], g["threshold"]) for g in gates} == {("proposal", 0.8)}
        # The platform's rules hold: one dialogue for all of them
        assert len(gate_definitions(gates, "place_order")) == 3

    def test_a_fail_quotes_the_proposal_and_turns_chaining_off(self) -> None:
        agreed = Proposal("place_order", decline_tool="change_order").confirm_gates()[1]
        on_fail = agreed.to_dict()["on_fail"]
        assert on_fail["response"]["tool_result"] == (
            "place_order was not run. The caller has not said yes to this change.")
        assert "${global_data.semantic_state.proposal}" in on_fail["response"]["tool_prompt"]
        assert "call change_order" in on_fail["response"]["tool_prompt"]
        assert on_fail["action"] == [{"back_to_back_functions": False}]

    def test_unclear_gates(self) -> None:
        gates = [g.to_dict() for g in Proposal("place_order", unclear=True,
                                                threshold=0.6).confirm_gates()]
        assert all(g["unclear"] is True and g["threshold"] == 0.6 for g in gates)
        assert all("on_unclear" in g for g in gates)

    def test_the_confirm_tool_renders_them(self) -> None:
        agent = AgentBase(name="shop", route="/", basic_auth=("u", "p"), suppress_logs=True)
        order = Proposal("place_order")
        agent.define_tool("place_order", "Place the order", {}, lambda a, r: "placed",
                          gates=order.confirm_gates())
        main = json.loads(agent._render_swml())["sections"]["main"]
        ai = next(verb["ai"] for verb in main if "ai" in verb)
        assert len(ai["SWAIG"]["functions"][0]["gates"]) == 3


class TestCurrent:
    def test_the_proposal_in_the_request(self) -> None:
        state = {"proposal": READ_BACK, "revision": 2}
        assert current(_raw(state)) == state

    @pytest.mark.parametrize("raw", [None, {}, _raw(None), _raw({"done": "x"}),
                                     {"global_data": "x"}])
    def test_none_without_one(self, raw: Any) -> None:
        assert current(raw) is None
