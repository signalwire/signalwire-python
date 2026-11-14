"""
Step and tool options the platform reads: expected_answer, refresh_step,
back_to_back_functions, nullable optional arguments, native tools, and the
steps that offer a tool.

The shapes follow mod_openai: expected_answer as speech_detect.c reads it
(expected_answer_json), back_to_back_functions as ai_back2back_value_json
does, and a native tool as actions.c dispatches one: a web_hook_url of
"native" runs the platform's own implementation by name.
"""

import json
from typing import Any
from unittest.mock import Mock

import pytest

from signalwire import AgentBase, FunctionResult, Step
from signalwire.core.contexts import GatherQuestion, expected_answer

AUTH = ("user", "pass")


def _agent() -> AgentBase:
    return AgentBase(name="options", route="/", basic_auth=AUTH, suppress_logs=True)


def _ai(agent: AgentBase) -> dict[str, Any]:
    main = json.loads(agent._render_swml())["sections"]["main"]
    return next(verb["ai"] for verb in main if "ai" in verb)


def _function(agent: AgentBase, name: str) -> dict[str, Any]:
    return next(f for f in _ai(agent)["SWAIG"]["functions"] if f["function"] == name)


class TestExpectedAnswer:
    def test_a_step_sends_an_exact_count(self) -> None:
        step = Step("zip").set_text("Ask for the ZIP code.").set_expected_answer(5)
        assert step.to_dict()["expected_answer"] == {"digits": 5}

    def test_a_step_sends_a_range(self) -> None:
        step = Step("pin").set_text("Ask for the PIN.").set_expected_answer(
            min_digits=4, max_digits=6)
        assert step.to_dict()["expected_answer"] == {"min_digits": 4, "max_digits": 6}

    def test_a_step_without_one_sends_none(self) -> None:
        assert "expected_answer" not in Step("s").set_text("t").to_dict()

    def test_a_gather_question_sends_its_own(self) -> None:
        step = Step("collect").set_text("t")
        step.set_gather_info(output_key="caller")
        step.add_gather_question("zip", "Your ZIP code?", expected_answer={"digits": 5})
        step.add_gather_question("name", "Your name?")
        questions = step.to_dict()["gather_info"]["questions"]
        assert questions[0]["expected_answer"] == {"digits": 5}
        assert "expected_answer" not in questions[1]

    @pytest.mark.parametrize(("kwargs", "message"), [
        ({"digits": 0}, "digits must be a whole number from 1 to 64"),
        ({"digits": 65}, "digits must be a whole number from 1 to 64"),
        ({"digits": True}, "digits must be a whole number from 1 to 64"),
        ({"digits": 5.0}, "digits must be a whole number from 1 to 64"),
        ({"digits": 5, "max_digits": 6}, "not both"),
        ({"min_digits": 4}, "needs digits, or both min_digits and max_digits"),
        ({}, "needs digits, or both min_digits and max_digits"),
        ({"min_digits": 6, "max_digits": 4}, "min_digits \\(6\\) must be at most max_digits \\(4\\)"),
    ])
    def test_shapes_the_platform_ignores_are_refused(self, kwargs: dict[str, Any],
                                                     message: str) -> None:
        with pytest.raises(ValueError, match=message):
            expected_answer(**kwargs)

    @pytest.mark.parametrize("given", [{}, {"digit": 5}, {"digits": 5, "extra": 1}, "5"])
    def test_a_question_dict_is_checked(self, given: Any) -> None:
        with pytest.raises(ValueError, match="expected_answer must be"):
            GatherQuestion("zip", "ZIP?", expected_answer=given)


class TestRefreshStep:
    def test_it_enters_the_named_step_after_the_update(self) -> None:
        result = (FunctionResult("Added the drink.")
                  .update_global_data({"order_total": "$14.50"})
                  .refresh_step("take_order"))
        assert result.to_dict()["action"] == [
            {"set_global_data": {"order_total": "$14.50"}},
            {"change_step": "take_order"},
        ]


class TestBackToBackFunctions:
    @pytest.mark.parametrize("value", [True, False, "forever"])
    def test_each_value_the_platform_reads(self, value: Any) -> None:
        result = FunctionResult("Read back the order.").back_to_back_functions(value)
        assert result.to_dict()["action"] == [{"back_to_back_functions": value}]

    @pytest.mark.parametrize("value", ["true", "Forever", 1, None])
    def test_other_values_are_refused(self, value: Any) -> None:
        with pytest.raises(ValueError, match='True, False or "forever"'):
            FunctionResult("x").back_to_back_functions(value)


SIZES: dict[str, Any] = {
    "type": "object",
    "properties": {
        "item": {"type": "string", "description": "The item"},
        "size": {"type": "string", "enum": ["small", "large"], "description": "Size"},
        "note": {"type": ["string"], "description": "A note"},
        "extras": {"anyOf": [{"type": "string"}, {"type": "array"}]},
    },
    "required": ["item"],
}


class TestNullableOptional:
    def _define(self, agent: AgentBase, calls: list[dict[str, Any]],
                **kwargs: Any) -> None:
        def add_item(args: dict[str, Any], raw: dict[str, Any]) -> str:
            calls.append(args)
            return "added"

        agent.define_tool("add_item", "Add an item", SIZES, add_item, **kwargs)

    def test_optional_arguments_take_null(self) -> None:
        agent = _agent()
        self._define(agent, [], nullable_optional=True)
        properties = _function(agent, "add_item")["parameters"]["properties"]
        assert properties["item"] == SIZES["properties"]["item"]
        assert properties["size"]["type"] == ["string", "null"]
        assert properties["size"]["enum"] == ["small", "large", None]
        assert properties["note"]["type"] == ["string", "null"]
        # A schema without a type is left as it is
        assert properties["extras"] == SIZES["properties"]["extras"]

    def test_a_null_reaches_the_handler_as_not_given(self) -> None:
        calls: list[dict[str, Any]] = []
        agent = _agent()
        self._define(agent, calls, nullable_optional=True)
        agent.on_function_call("add_item", {"item": "tea", "size": None, "note": "hot"}, {})
        assert calls == [{"item": "tea", "note": "hot"}]

    def test_the_agent_default_covers_tools_defined_before_it(self) -> None:
        calls: list[dict[str, Any]] = []
        agent = _agent()
        self._define(agent, calls)
        agent.set_nullable_optional_parameters()
        assert _function(agent, "add_item")["parameters"]["properties"]["size"]["type"] == [
            "string", "null"]
        agent.on_function_call("add_item", {"item": "tea", "size": None}, {})
        assert calls == [{"item": "tea"}]

    def test_a_tool_can_opt_out_of_the_agent_default(self) -> None:
        calls: list[dict[str, Any]] = []
        agent = _agent().set_nullable_optional_parameters()
        self._define(agent, calls, nullable_optional=False)
        assert _function(agent, "add_item")["parameters"]["properties"]["size"]["type"] == "string"
        agent.on_function_call("add_item", {"item": "tea", "size": None}, {})
        assert calls == [{"item": "tea", "size": None}]

    def test_off_by_default(self) -> None:
        agent = _agent()
        self._define(agent, [])
        assert _function(agent, "add_item")["parameters"] == SIZES


class TestNativeTool:
    def test_it_is_sent_with_the_native_url(self) -> None:
        agent = _agent()
        agent.define_tool("lookup", "Look up", {}, lambda a, r: "ok")
        agent.define_native_tool("end_call", "End the call once the order is placed.",
                                 {"type": "object", "properties": {"reason": {"type": "string"}}})
        native = _function(agent, "end_call")
        assert native["web_hook_url"] == "native"
        assert native["description"] == "End the call once the order is placed."
        assert native["parameters"]["properties"] == {"reason": {"type": "string"}}
        # The other tools still use the agent's webhook
        swaig = _ai(agent)["SWAIG"]
        assert swaig["defaults"]["web_hook_url"] != "native"
        assert "web_hook_url" not in _function(agent, "lookup") or (
            _function(agent, "lookup")["web_hook_url"] != "native")

    def test_its_url_cannot_be_overridden(self) -> None:
        agent = _agent()
        agent.define_native_tool("end_call", "End the call", web_hook_url="https://x.example")
        assert _function(agent, "end_call")["web_hook_url"] == "native"


class TestStepsOffering:
    def _agent_with_steps(self, *, every_step_lists: bool) -> AgentBase:
        agent = _agent()
        for name in ("find_store", "place_order", "audit_log"):
            agent.define_tool(name, name, {}, lambda a, r: "ok")
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("greet").set_text("Greet").set_functions(["find_store"])
        collect = ctx.add_step("collect").set_text("Collect")
        collect.set_functions("none" if every_step_lists else None)  # type: ignore[arg-type]
        collect.set_gather_info(output_key="order")
        collect.add_gather_question("item", "What item?", functions=["place_order"])
        if not every_step_lists:
            collect._functions = None
        ctx.add_step("confirm").set_text("Confirm").set_functions(["place_order"])
        return agent

    def test_it_names_the_steps_that_list_the_tool(self) -> None:
        agent = self._agent_with_steps(every_step_lists=True)
        builder = agent._contexts_builder
        assert builder is not None
        assert builder.steps_offering("place_order") == [
            ("default", "collect"), ("default", "confirm")]
        assert builder.steps_offering("find_store") == [("default", "greet")]
        assert builder.steps_offering("audit_log") == []

    def test_a_tool_no_step_offers_is_logged_once(self, monkeypatch: pytest.MonkeyPatch) -> None:
        logger = Mock()
        monkeypatch.setattr("signalwire.core.contexts._logger", logger)
        agent = self._agent_with_steps(every_step_lists=True)
        agent._render_swml()
        agent._render_swml()
        assert [c.args[0] for c in logger.warning.call_args_list] == ["tool_offered_by_no_step"]
        assert logger.warning.call_args.kwargs["function"] == "audit_log"

    def test_no_warning_when_a_step_inherits_its_functions(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        logger = Mock()
        monkeypatch.setattr("signalwire.core.contexts._logger", logger)
        self._agent_with_steps(every_step_lists=False)._render_swml()
        logger.warning.assert_not_called()


class TestToolMentions:
    """A tool named where the step doesn't offer it: the model reads the name
    and may call a tool it doesn't have."""

    def _agent(self) -> AgentBase:
        agent = _agent()
        for name in ("find_store", "place_order", "help"):
            agent.define_tool(name, name, {}, lambda a, r: "ok")
        return agent

    def _warnings(self, agent: AgentBase, monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
        logger = Mock()
        monkeypatch.setattr("signalwire.core.contexts._logger", logger)
        agent._render_swml()
        agent._render_swml()
        return [c.kwargs for c in logger.warning.call_args_list
                if c.args[0] == "tool_named_but_not_offered"]

    def test_step_text_criteria_and_context_prompt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        agent = self._agent()
        ctx = agent.define_contexts().add_context("default")
        ctx.set_prompt("You take orders. Call place_order only after a read-back.")
        ctx.add_step("greet").set_text("Greet them, then use find_store.").set_functions(
            ["find_store"]).set_step_criteria("place_order has been called")
        ctx.add_step("confirm").set_text("Confirm, then call place_order.").set_functions(
            ["place_order"])
        warned = {(w["step"], w["where"], w["function"]) for w in self._warnings(agent, monkeypatch)}
        assert warned == {("greet", "criteria", "place_order"),
                          ("greet", "context prompt", "place_order")}

    def test_gate_output_and_gather_questions(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from signalwire import SemanticGate

        agent = _agent()
        agent.define_tool("find_store", "Find", {}, lambda a, r: "ok")
        agent.define_tool("place_order", "Order", {}, lambda a, r: "ok", gates=[
            SemanticGate("Q?", 0.8, "place_order was not run. Call find_store first.", id="g")])
        ctx = agent.define_contexts().add_context("default")
        step = ctx.add_step("confirm").set_text("Confirm.").set_functions(["place_order"])
        step.set_gather_info(output_key="o")
        step.add_gather_question("zip", "Your ZIP? Use find_store.", functions=["find_store"])
        step.add_gather_question("size", "Size? Then find_store.")
        warned = {(w["where"], w["function"]) for w in self._warnings(agent, monkeypatch)}
        assert warned == {("place_order gate g on_fail", "find_store"),
                          ("gather question size", "find_store")}

    def test_one_word_names_count_only_as_code(self, monkeypatch: pytest.MonkeyPatch) -> None:
        agent = self._agent()
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("greet").set_text("Offer help. If stuck, call `help`.").set_functions(
            ["find_store"])
        warned = [(w["where"], w["function"]) for w in self._warnings(agent, monkeypatch)]
        assert warned == [("text", "help")]

    def test_a_step_that_inherits_its_functions_is_skipped(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        agent = self._agent()
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("greet").set_text("Use place_order.")
        assert self._warnings(agent, monkeypatch) == []


class TestInertResets:
    def _warned(self, agent: AgentBase, monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, Any]]:
        logger = Mock()
        monkeypatch.setattr("signalwire.core.contexts._logger", logger)
        agent._render_swml()
        agent._render_swml()
        return [(c.args[0], c.kwargs) for c in logger.warning.call_args_list]

    def test_a_step_with_a_reset_is_terminal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        agent = _agent()
        ctx = agent.define_contexts().add_context("default")
        ctx.add_step("hand_off").set_text("Never shown.").set_reset_system_prompt("You're support.")
        ctx.add_step("after").set_text("After.")
        warned = self._warned(agent, monkeypatch)
        assert [(name, w["step"]) for name, w in warned] == [("step_reset_is_terminal", "hand_off")]

    def test_context_resets_need_a_system_prompt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        agent = _agent()
        builder = agent.define_contexts()
        builder.add_context("default").add_step("s").set_text("S")
        billing = builder.add_context("billing").set_consolidate(True).set_user_prompt("Billing.")
        billing.add_step("b").set_text("B")
        prompted = builder.add_context("support").set_consolidate(True).set_system_prompt("Support.")
        prompted.add_step("p").set_text("P")
        warned = self._warned(agent, monkeypatch)
        assert [(name, w["context"], w["settings"]) for name, w in warned] == [
            ("context_reset_without_system_prompt", "billing", ["consolidate", "user_prompt"])]


class TestNoBargeNextResponse:
    def test_the_action(self) -> None:
        assert FunctionResult("Read it back.").no_barge_next_response().to_dict()["action"] == [
            {"no_barge_next_response": True}]
