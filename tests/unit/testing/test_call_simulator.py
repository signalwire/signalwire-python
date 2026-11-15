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
            "The steps that offer it: confirm. The tools available now are: review_order.\n")

    def test_an_unknown_tool(self) -> None:
        assert CallSimulator(_shop()).call("refund").response == (
            "Nothing ran: there is no tool named refund. "
            "The tools available now are: review_order.\n")

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
        said = [e["content"] for e in sim.call_log if e["role"] == "assistant" and e["content"]]
        assert said[-1] == "That's a large tea. Is that right?"
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
        assert sim.offered() == ["unlock", "secret"]
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


class TestMarks:
    def test_a_mark_is_kept_with_its_place_in_the_log(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("read_back", "Read back", {}, lambda a, r: FunctionResult(
            "Read it back.").set_semantic_gate_mark("read_back"))
        sim = CallSimulator(agent)
        sim.caller("A tea.")
        sim.call("read_back")
        sim.caller("Yes.")
        since = sim.call_log[sim.marks["read_back"]:]
        assert [e.get("content") for e in since if e["role"] == "user"] == ["Yes."]


class TestPlatformReplyDetails:
    def test_the_current_step_isnt_among_the_steps_that_offer_it(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("lookup", "Look up", {}, lambda a, r: "ok")
        agent.define_tool("other", "Other", {}, lambda a, r: "ok")
        ctx = agent.define_contexts().add_context("default")
        # A step that lists a tool and is in it has used it up; no other step offers it
        ctx.add_step("one").set_text("One").set_functions(["lookup", "other"])
        sim = CallSimulator(agent, global_data={})
        sim._toggled["lookup"] = False
        assert sim.call("lookup").response == (
            "Nothing ran: lookup isn't available at this point in the call. "
            "The tools available now are: other.\n")

    def test_no_tools_at_all(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("lookup", "Look up", {}, lambda a, r: "ok")
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("one").set_text("One").set_functions("none")
        assert CallSimulator(agent).call("lookup").response == (
            "Nothing ran: lookup isn't available at this point in the call. "
            "No tools are available now.\n")

    def test_a_call_keeps_sixteen_marks(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("mark", "Mark", {"type": "object", "properties": {
            "name": {"type": "string"}}}, lambda a, r: FunctionResult("ok").set_semantic_gate_mark(
                a["name"]))
        sim = CallSimulator(agent)
        for n in range(17):
            sim.call("mark", {"name": f"m{n}"})
        assert len(sim.marks) == 16 and "m0" not in sim.marks


class TestToolMentionCheck:
    def test_a_result_naming_a_tool_the_next_step_lacks_fails(self) -> None:
        from signalwire.testing import ToolMentionError

        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("find_store", "Find", {}, lambda a, r: FunctionResult(
            tool_result="Store 12.", tool_prompt="Now call place_order.").swml_change_step("pick"))
        agent.define_tool("place_order", "Order", {}, lambda a, r: "ok")
        agent.define_tool("pick_time", "Pick", {}, lambda a, r: FunctionResult(
            "Picked. Next, place_order.").swml_change_step("order"))
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("find").set_text("Find.").set_functions(["find_store"])
        ctx.add_step("pick").set_text("Pick.").set_functions(["pick_time"])
        ctx.add_step("order").set_text("Order.").set_functions(["place_order"])
        sim = CallSimulator(agent, check_tool_mentions=True)
        with pytest.raises(ToolMentionError, match="names place_order, which step 'pick'"):
            sim.call("find_store")
        # Naming the tool of the step the result moves the call to is fine
        assert sim.call("pick_time").ran
        # Off by default
        CallSimulator(agent).call("find_store")


class TestModelView:
    """What the model gets, after each step's history mode: applied when the
    step's instructions are injected, before the follow-up request right after
    the result that moved the call there, to everything before it
    (STEP_HISTORY.md; mod_openai check_steps runs before every request)."""

    def _agent(self, mode: str | None) -> AgentBase:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.set_global_data({"store": "Main Street"})
        agent.define_tool("lookup", "Look up", {}, lambda a, r: FunctionResult(
            tool_result="Order 7 is a tea.", tool_prompt="Tell the caller.").swml_change_step(
                "next"))
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("first").set_text("Look it up.").set_functions(["lookup"])
        second = ctx.add_step("next").set_text("Help at ${global_data.store}.")
        if mode:
            second.set_history(mode)
        return agent

    def _run(self, mode: str | None) -> list[tuple[str, str]]:
        sim = CallSimulator(self._agent(mode))
        sim.caller("Where's my order?")
        sim.call("lookup")
        sim.caller("Thanks.")
        return [(e["role"], e["content"] or "<tool call>") for e in sim.model_view()]

    def test_default_clears_old_instructions(self) -> None:
        assert self._run(None) == [
            ("user", "Where's my order?"),
            ("assistant", "<tool call>"),
            ("tool", "Order 7 is a tea."),
            ("system", "Tell the caller."),
            ("system", "Help at Main Street."),
            ("user", "Thanks."),
        ]

    def test_keep_keeps_everything(self) -> None:
        assert self._run("keep")[0] == ("system", "Look it up.")

    def test_hide_takes_everything_before_the_entering_exchange(self) -> None:
        # The call that moved the call here, its result and note, are the
        # step's start, and stay
        assert self._run("hide") == [
            ("assistant", "<tool call>"),
            ("tool", "Order 7 is a tea."),
            ("system", "Tell the caller."),
            ("system", "Help at Main Street."),
            ("user", "Thanks."),
        ]

    def test_a_post_process_change_keeps_its_call_and_the_reply(self) -> None:
        # The actions run after the model's reply to the result; the change
        # keeps the call and everything stored from it on (mod_openai
        # delayed_call_id, ai_conversation_tag_call_cause)
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("lookup", "Look up", {}, lambda a, r: FunctionResult(
            "Order 7.", post_process=True).swml_change_step("next"))
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("first").set_text("Look it up.").set_functions(["lookup"])
        ctx.add_step("next").set_text("Next.").set_history("hide")
        sim = CallSimulator(agent)
        sim.caller("Where's my order?")
        sim.call("lookup")
        assert sim.step == "first"
        sim.agent_says("Order 7 is on its way.")
        assert sim.step == "next"
        sim.caller("Thanks.")
        assert [e["content"] for e in sim.model_view()] == [
            "", "Order 7.", "Order 7 is on its way.", "Thanks.", "Next."]

    def test_post_process_actions_wait_for_the_reply(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("finish", "Finish", {}, lambda a, r: FunctionResult(
            "Done.", post_process=True).hangup())
        agent.define_tool("bye", "Bye", {}, lambda a, r: FunctionResult(
            "Bye.", post_process=True).say("Goodbye."))
        sim = CallSimulator(agent)
        sim.call("finish")
        assert not sim.ended
        # A newer post_process result replaces actions still waiting
        sim.call("bye")
        sim.agent_says("Thanks for calling.")
        assert not sim.ended
        assert sim.call_log[-1]["content"] == "Goodbye."

    def test_a_say_before_the_change_in_the_same_result_stays(self) -> None:
        # A result's action list is one scope: a change anywhere in it keeps
        # what the list added, before the change too
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("confirm", "Confirm", {}, lambda a, r: FunctionResult(
            "Read back.").say("That's a large tea.").swml_change_step("next"))
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("first").set_text("Take the order.").set_functions(["confirm"])
        ctx.add_step("next").set_text("Confirm.").set_history("hide")
        sim = CallSimulator(agent)
        sim.caller("A large tea.")
        sim.call("confirm")
        # The say goes after the call's result, held past system entries until
        # the next caller or agent turn (mod_openai conversation.c held_says)
        assert [e["content"] for e in sim.model_view()] == [
            "", "Read back.", "Confirm.", "That's a large tea."]
        sim.caller("Yes.")
        assert [e["content"] for e in sim.model_view()][-2:] == ["That's a large tea.", "Yes."]

    def test_a_post_process_change_keeps_calls_chained_after_its_own(self) -> None:
        # The range runs from the waiting list's call to the change; a newer
        # post_process list brings its own call
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("lookup", "Look up", {}, lambda a, r: FunctionResult(
            "Order 7.", post_process=True).swml_change_step("next"))
        agent.define_tool("price", "Price", {}, lambda a, r: FunctionResult("Four dollars."))
        agent.define_tool("check", "Check", {}, lambda a, r: FunctionResult(
            "Checked.", post_process=True).swml_change_step("next"))
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("first").set_text("Look it up.").set_functions(["lookup", "price", "check"])
        ctx.add_step("next").set_text("Next.").set_history("hide")
        sim = CallSimulator(agent)
        sim.call("lookup")
        sim.call("price")
        sim.agent_says("Order 7 is four dollars.")
        assert [e["content"] for e in sim.model_view()] == [
            "", "Order 7.", "", "Four dollars.", "Order 7 is four dollars.", "Next."]
        sim = CallSimulator(agent)
        sim.call("lookup")
        sim.call("check")
        sim.agent_says("All set.")
        assert [e["content"] for e in sim.model_view()] == ["", "Checked.", "All set.", "Next."]

    def test_the_step_text_is_expanded_again_when_a_value_changes(self) -> None:
        agent = self._agent(None)
        agent.define_tool("move", "Move", {}, lambda a, r: FunctionResult(
            "Moved.").update_global_data({"store": "Elm Street"}))
        ctx = agent._contexts_builder._contexts["default"]  # type: ignore[union-attr]
        ctx._steps["next"].set_functions(["move"])
        sim = CallSimulator(agent)
        sim.call("lookup")
        sim.call("move")
        view = [e["content"] for e in sim.model_view()]
        # In place, nothing appended; the call log keeps the text as it went in
        assert view.count("Help at Elm Street.") == 1
        assert "Help at Main Street." not in view
        assert [e["content"] for e in sim.call_log].count("Help at Main Street.") == 1

    def test_an_end_step_keeps_the_text_it_went_in_with(self) -> None:
        agent = self._agent(None)
        agent.define_tool("move", "Move", {}, lambda a, r: FunctionResult(
            "Moved.").update_global_data({"store": "Elm Street"}))
        ctx = agent._contexts_builder._contexts["default"]  # type: ignore[union-attr]
        ctx._steps["next"].set_functions(["move"]).set_end(True)
        sim = CallSimulator(agent)
        sim.call("lookup")
        sim.call("move")
        assert "Help at Main Street." in [e["content"] for e in sim.model_view()]

    def test_isolate_restores_when_the_step_is_left(self) -> None:
        agent = self._agent("isolate")
        ctx = agent._contexts_builder._contexts["default"]  # type: ignore[union-attr]
        ctx.add_step("after").set_text("After.")
        agent.define_tool("move_on", "Move", {}, lambda a, r: FunctionResult("ok").swml_change_step(
            "after"))
        ctx._steps["next"].set_functions(["move_on"])
        sim = CallSimulator(agent)
        sim.caller("Where's my order?")
        sim.call("lookup")
        assert [e["content"] for e in sim.model_view()] == [
            "", "Order 7 is a tea.", "Tell the caller.", "Help at Main Street."]
        sim.call("move_on")
        sim.caller("Bye.")
        contents = [e["content"] for e in sim.model_view()]
        assert contents[0] == "Where's my order?"
        assert contents[-2:] == ["After.", "Bye."]


class TestSpokenMode:
    """history "spoken": at the step's entry, earlier tool calls, tool
    results, turn-scoped system notes and old instructions leave for the rest
    of the call; every spoken turn stays (mod_openai STEP_HISTORY.md)."""

    def test_the_work_goes_and_the_talk_stays(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("lookup", "Look up", {}, lambda a, r: FunctionResult(
            tool_result="Order 7 is a tea.", tool_prompt="Tell the caller."))
        agent.define_tool("finish", "Finish", {}, lambda a, r: FunctionResult(
            "Lookup finished.").swml_change_step("next"))
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("first").set_text("Look it up.").set_functions(["lookup", "finish"])
        ctx.add_step("next").set_text("Next request.").set_history("spoken")
        sim = CallSimulator(agent)
        sim.caller("Where's my order? And my balance.")
        sim.call("lookup")
        sim.agent_says("It's a tea.")
        sim.call("finish")
        assert [(e["role"], e["content"] or "<tool call>") for e in sim.model_view()] == [
            ("user", "Where's my order? And my balance."),
            ("assistant", "It's a tea."),
            # The exchange that entered the step stays: it's the step's start
            ("assistant", "<tool call>"),
            ("tool", "Lookup finished."),
            ("system", "Next request."),
        ]

    def test_a_say_stays_when_its_call_goes(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("lookup", "Look up", {}, lambda a, r: FunctionResult(
            "Order 7.").say("Your order is on its way."))
        agent.define_tool("finish", "Finish", {}, lambda a, r: FunctionResult(
            "Done.").swml_change_step("next"))
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("first").set_text("Look it up.").set_functions(["lookup", "finish"])
        ctx.add_step("next").set_text("Next.").set_history("spoken")
        sim = CallSimulator(agent)
        sim.caller("Where is it?")
        sim.call("lookup")
        sim.call("finish")
        # With no turn after it, the say is held to the end
        assert [e["content"] for e in sim.model_view()] == [
            "Where is it?", "", "Done.", "Next.", "Your order is on its way."]

    def test_a_later_isolate_doesnt_bring_back_what_spoken_took(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("lookup", "Look up", {}, lambda a, r: FunctionResult(
            "Order 7.").swml_change_step("talk"))
        agent.define_tool("confirm", "Confirm", {}, lambda a, r: FunctionResult(
            "Read back.").swml_change_step("confirm"))
        agent.define_tool("done", "Done", {}, lambda a, r: FunctionResult(
            "Done.").swml_change_step("after"))
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("first").set_text("Look up.").set_functions(["lookup"])
        ctx.add_step("talk").set_text("Talk.").set_history("spoken").set_functions(["confirm"])
        ctx.add_step("confirm").set_text("Confirm.").set_history("isolate").set_functions(["done"])
        ctx.add_step("after").set_text("After.")
        sim = CallSimulator(agent)
        sim.caller("Where's my order?")
        sim.call("lookup")
        sim.caller("Cancel it.")
        sim.call("confirm")
        # isolate keeps the exchange that entered it: the confirm call
        assert [e["content"] for e in sim.model_view()] == ["", "Read back.", "Confirm."]
        sim.call("done")
        contents = [e["content"] for e in sim.model_view()]
        # isolate brings back what it hid, which includes the lookup that
        # entered the spoken step: spoken kept that as the step's start
        assert contents[:3] == ["Where's my order?", "", "Order 7."]
        assert "Cancel it." in contents


class TestGateConversation:
    def _sim(self, mode: str | None = None) -> CallSimulator:
        agent = _shop()
        if mode:
            agent._contexts_builder._contexts["default"]._steps["confirm"].set_history(mode)  # type: ignore[union-attr]
        return CallSimulator(agent)

    def test_the_window_is_the_spoken_turns_the_model_sees(self) -> None:
        sim = self._sim()
        sim.caller("A tea, and my balance later.")
        sim.call("review_order", {"item": "a tea"})
        sim.caller("Yes.")
        assert sim.gate_conversation() == [
            "user: A tea, and my balance later.",
            "assistant: That's a tea. Is that right?",
            "user: Yes.",
        ]
        assert sim.gate_conversation({"history": 1}) == ["user: Yes."]

    def test_hide_takes_the_callers_earlier_words_from_gates_too(self) -> None:
        sim = self._sim("hide")
        sim.caller("A tea, and my balance later.")
        sim.call("review_order", {"item": "a tea"})
        sim.caller("Yes.")
        # The read-back said by the call that entered the step stays
        assert sim.gate_conversation() == [
            "assistant: That's a tea. Is that right?", "user: Yes."]

    def test_spoken_keeps_them(self) -> None:
        sim = self._sim("spoken")
        sim.caller("A tea, and my balance later.")
        sim.call("review_order", {"item": "a tea"})
        sim.caller("Yes.")
        assert sim.gate_conversation()[0] == "user: A tea, and my balance later."

    def test_the_proposal_starts_at_its_read_back(self) -> None:
        sim = self._sim()
        sim.caller("A tea, and my balance later.")
        sim.call("review_order", {"item": "a tea"})
        sim.caller("Yes.")
        assert sim.gate_conversation({"dialogue": "proposal"}) == [
            "assistant: That's a tea. Is that right?",
            "user: Yes.",
        ]

    def test_since_a_mark(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        sim = CallSimulator(agent)
        sim.caller("Earlier words.")
        sim._apply({"action": [{"semantic_gate_mark": "rb", "say": "Is that right?"}]})
        sim.caller("Yes.")
        assert sim.gate_conversation({"since": "rb"}) == [
            "assistant: Is that right?", "user: Yes."]
        assert sim.gate_conversation({"since": "unset"})[0] == "user: Earlier words."

    def test_a_say_before_the_state_in_the_same_result_is_in_the_proposal(self) -> None:
        # The proposal dates from the start of the result's action list, so
        # the order of its action objects doesn't matter
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("review", "Review", {}, lambda a, r: FunctionResult(
            "Read back.").say("That's a tea. Is that right?").set_semantic_state(
                {"proposal": "a tea"}))
        sim = CallSimulator(agent)
        sim.caller("A tea, and my balance later.")
        sim.call("review")
        sim.caller("Yes.")
        assert sim.gate_conversation({"dialogue": "proposal"}) == [
            "assistant: That's a tea. Is that right?", "user: Yes."]

    def test_a_say_before_the_mark_in_the_same_result_is_after_it(self) -> None:
        agent = AgentBase(name="t", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.define_tool("review", "Review", {}, lambda a, r: FunctionResult(
            "Read back.").say("Is that right?").set_semantic_gate_mark("rb"))
        sim = CallSimulator(agent)
        sim.caller("Earlier words.")
        sim.call("review")
        sim.caller("Yes.")
        assert sim.gate_conversation({"since": "rb"}) == [
            "assistant: Is that right?", "user: Yes."]
