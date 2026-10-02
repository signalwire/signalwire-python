"""
Semantic gates, change_voice and the semantic gate params.

The platform refuses a whole function when any of its gates breaks a rule
(mod_openai semantic_gates.c), so the SDK checks gates by the same rules when
a tool is defined. These tests follow those rules one by one.
"""

import json
from typing import Any

import pytest

from signalwire import AgentBase, DataMap, FunctionResult, SemanticGate
from signalwire.core.semantic_gate import gate_definitions

AUTH = ("user", "pass")


def _gate(**overrides: Any) -> dict[str, Any]:
    gate: dict[str, Any] = {
        "question": "Has the caller asked for a refund in `conversation`?",
        "threshold": 0.9,
        "on_fail": {"response": "refund was not run."},
    }
    gate.update(overrides)
    return gate


def _functions(agent: AgentBase) -> dict[str, dict[str, Any]]:
    main = json.loads(agent._render_swml())["sections"]["main"]
    ai = next(verb["ai"] for verb in main if "ai" in verb)
    return {f["function"]: f for f in ai["SWAIG"]["functions"]}


def _agent() -> AgentBase:
    return AgentBase(name="gated", route="/", basic_auth=AUTH, suppress_logs=True)


def _handler(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    return FunctionResult("done")


class TestSemanticGate:
    def test_a_string_on_fail_is_the_response(self) -> None:
        gate = SemanticGate("Q in `conversation`?", 0.9, "refund was not run.")
        assert gate.to_dict() == {
            "question": "Q in `conversation`?",
            "threshold": 0.9,
            "on_fail": {"response": "refund was not run."},
        }

    def test_every_field(self) -> None:
        gate = SemanticGate(
            "Has the caller explicitly asked to cancel in `conversation`?",
            threshold=0.95,
            on_fail=FunctionResult(
                tool_result="cancel_account was not run.",
                tool_prompt="Ask the caller to confirm that they want to cancel.",
            ).update_global_data({"cancel_attempted": True}),
            true_means="The caller says they want to cancel.",
            false_means="The caller asked about cancelling, or said something else.",
            id="explicit_request",
        )
        assert gate.to_dict() == {
            "id": "explicit_request",
            "question": "Has the caller explicitly asked to cancel in `conversation`?",
            "criteria": {
                "true": "The caller says they want to cancel.",
                "false": "The caller asked about cancelling, or said something else.",
            },
            "threshold": 0.95,
            "on_fail": {
                "response": {
                    "tool_result": "cancel_account was not run.",
                    "tool_prompt": "Ask the caller to confirm that they want to cancel.",
                },
                "action": [{"set_global_data": {"cancel_attempted": True}}],
            },
        }

    def test_post_process_is_kept_with_actions(self) -> None:
        result = FunctionResult("not run.", post_process=True).update_global_data({"a": 1})
        on_fail = SemanticGate("Q?", 0.5, result).to_dict()["on_fail"]
        assert on_fail["post_process"] is True

    def test_a_result_without_a_response_is_refused(self) -> None:
        # FunctionResult would fill in "Action completed.", which reads as a success
        with pytest.raises(ValueError, match="on_fail needs a response"):
            SemanticGate("Q?", 0.5, FunctionResult().update_global_data({"a": 1}))

    def test_a_tool_prompt_without_a_tool_result_is_refused_when_defined(self) -> None:
        gate = SemanticGate("Q?", 0.5, FunctionResult(tool_prompt="Ask again."))
        with pytest.raises(ValueError, match="on_fail.response.tool_result is missing"):
            gate_definitions([gate], "refund")


class TestPlatformRules:
    """Each rule semantic_gates.c applies, with its reason."""

    @pytest.mark.parametrize(
        ("gates", "reason"),
        [
            ([], "gates must hold 1 to 8 gates, not 0"),
            ([_gate(id=f"g{i}") for i in range(9)], "gates must hold 1 to 8 gates, not 9"),
            ([_gate(gate="x")], "gate 1: unknown key 'gate'"),
            ([_gate(Threshold=0.5)], "gate 1: unknown key 'Threshold'"),
            ([_gate(question="")], "gate 1: question is missing or empty"),
            ([_gate(question="é" * 4097)], "gate 1: question is longer than 8192 bytes"),
            ([_gate(threshold=0)], "threshold must be a number above 0 and at most 1"),
            ([_gate(threshold=1.01)], "threshold must be a number above 0 and at most 1"),
            ([_gate(threshold=True)], "threshold must be a number above 0 and at most 1"),
            ([_gate(threshold="0.9")], "threshold must be a number above 0 and at most 1"),
            ([{"question": "Q?", "threshold": 0.5}], "gate 1: on_fail is missing"),
            ([_gate(on_fail="no")], "gate 1: on_fail must be an object"),
            ([_gate(on_fail={})], "gate 1: on_fail.response is missing"),
            ([_gate(on_fail={"response": ""})], "gate 1: on_fail.response is empty"),
            ([_gate(on_fail={"response": {"tool_prompt": "x"}})],
             "on_fail.response.tool_result is missing or empty"),
            ([_gate(on_fail={"response": {"tool_result": "no", "tool_prompt": 1}})],
             "on_fail.response.tool_prompt must be a string"),
            ([_gate(on_fail={"response": "no", "action": {"say": "x"}})],
             "on_fail.action must be an array"),
            ([_gate(on_fail={"response": "é" * 4100})], "on_fail is larger than 8192 bytes"),
            ([_gate(criteria={})], "criteria must be an object with true and/or false"),
            ([_gate(criteria={"yes": "x"})], "criteria has an unknown key 'yes'"),
            ([_gate(criteria={"true": ""})], "criteria.true must be a non-empty string"),
            ([_gate(criteria={"false": "x" * 2049})], "criteria.false is longer than 2048 bytes"),
            ([_gate(id="has space")], "id must be 1 to 64 letters, digits or underscores"),
            ([_gate(id="x" * 65)], "id must be 1 to 64 letters, digits or underscores"),
            ([_gate(id="same"), _gate(id="same")], "gate 2: id 'same' is already used by gate 1"),
            # An explicit id equal to a generated one is a collision too
            ([_gate(), _gate(id="gate_1")], "gate 2: id 'gate_1' is already used by gate 1"),
        ],
    )
    def test_a_gate_the_platform_refuses_is_refused(
        self, gates: list[dict[str, Any]], reason: str
    ) -> None:
        with pytest.raises(ValueError) as caught:
            gate_definitions(gates, "refund")
        assert reason in str(caught.value)

    def test_the_limits_themselves_are_accepted(self) -> None:
        gates = [_gate(id=f"g{i}") for i in range(8)]
        gates[0] = _gate(id="x" * 64, question="q" * 8192, threshold=1,
                         criteria={"true": "t" * 2048, "false": "f"})
        assert len(gate_definitions(gates, "refund")) == 8

    @pytest.mark.parametrize("name", [
        "startup_hook", "hangup_hook", "check_for_input", "end_call", "hangup",
        "wait_for_user", "next_step", "change_context", "pause_conversation",
    ])
    def test_hook_and_built_in_names_cant_carry_gates(self, name: str) -> None:
        with pytest.raises(ValueError, match="hook or built-in function name"):
            gate_definitions([_gate()], name)


class TestDefiningGatedTools:
    def test_define_tool_renders_gates_and_gate_fillers(self) -> None:
        agent = _agent()
        agent.define_tool(
            name="refund", description="Refund an order", parameters={}, handler=_handler,
            gates=[SemanticGate("Q in `conversation`?", 0.9, "refund was not run.")],
            gate_fillers={"auto": ["Let me verify that."]},
        )
        refund = _functions(agent)["refund"]
        assert refund["gates"] == [
            {"question": "Q in `conversation`?", "threshold": 0.9,
             "on_fail": {"response": "refund was not run."}}
        ]
        assert refund["gate_fillers"] == {"auto": ["Let me verify that."]}

    def test_define_tool_refuses_a_bad_gate_at_once(self) -> None:
        agent = _agent()
        with pytest.raises(ValueError, match="refund: gate 1: threshold"):
            agent.define_tool(name="refund", description="Refund", parameters={},
                              handler=_handler, gates=[_gate(threshold=2)])
        assert "refund" not in agent._tool_registry._swaig_functions

    def test_gate_fillers_need_gates(self) -> None:
        with pytest.raises(ValueError, match="gate_fillers needs gates"):
            _agent().define_tool(name="refund", description="Refund", parameters={},
                                 handler=_handler, gate_fillers={"default": ["One moment."]})

    def test_a_class_decorated_tool_takes_gates(self) -> None:
        class Shop(AgentBase):
            def __init__(self) -> None:
                super().__init__(name="shop", route="/", basic_auth=AUTH, suppress_logs=True)

            @AgentBase.tool(name="place_order", description="Place the order", parameters={},
                            gates=[_gate(question="Has the caller confirmed the order in "
                                                  "`conversation`?")])
            def place_order(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
                return FunctionResult("placed")

        gates = _functions(Shop())["place_order"]["gates"]
        assert gates[0]["question"].startswith("Has the caller confirmed")

    def test_a_data_map_takes_gates(self) -> None:
        agent = _agent()
        agent.register_swaig_function(
            DataMap("cancel_order")
            .description("Cancel the order")
            .webhook("POST", "https://api.example.com/cancel")
            .output(FunctionResult("Cancelled."))
            .gate(SemanticGate("Has the caller asked to cancel in `conversation`?", 0.95,
                               "cancel_order was not run.", id="asked"))
            .gate_fillers({"default": ["One moment."]})
            .to_swaig_function()
        )
        cancel = _functions(agent)["cancel_order"]
        assert cancel["gates"][0]["id"] == "asked"
        assert cancel["gate_fillers"] == {"default": ["One moment."]}

    def test_a_raw_function_dict_is_checked(self) -> None:
        with pytest.raises(ValueError, match="lookup: gate 1: on_fail is missing"):
            _agent().register_swaig_function({
                "function": "lookup", "description": "Look up",
                "data_map": {"output": {"response": "x"}},
                "gates": [{"question": "Q?", "threshold": 0.5}],
            })

    def test_fillers_take_the_auto_key_and_wait_scripts(self) -> None:
        agent = _agent()
        fillers = {"auto": ["One moment", ["Let me look that up", "Still searching"]]}
        agent.define_tool(name="search", description="Search", parameters={},
                          handler=_handler, fillers=fillers)
        assert _functions(agent)["search"]["fillers"] == fillers


class TestFunctionResultActions:
    def test_change_voice(self) -> None:
        result = FunctionResult("Switching voices.").change_voice("elevenlabs.rachel")
        assert result.to_dict()["action"] == [{"change_voice": "elevenlabs.rachel"}]

    @pytest.mark.parametrize("voice", ["", "   "])
    def test_change_voice_needs_a_voice(self, voice: str) -> None:
        with pytest.raises(ValueError, match="voice must be a non-empty string"):
            FunctionResult().change_voice(voice)

    def test_set_semantic_state_replaces_it_whole(self) -> None:
        state = {"order": {"item": "large pepperoni", "confirmed": True}}
        result = FunctionResult("Noted.").set_semantic_state(state)
        assert result.to_dict()["action"] == [{"set_global_data": {"semantic_state": state}}]


class TestSemanticGateParams:
    def test_each_param(self) -> None:
        agent = _agent().set_semantic_gates(enabled=False, timeout_ms=4000, history=0)
        main = json.loads(agent._render_swml())["sections"]["main"]
        params = next(verb["ai"] for verb in main if "ai" in verb)["params"]
        assert (params["semantic_gates_enabled"], params["semantic_gate_timeout_ms"],
                params["semantic_gate_history"]) == (False, 4000, 0)

    def test_left_out_params_keep_the_platform_default(self) -> None:
        agent = _agent().set_semantic_gates(history=50)
        assert agent._params == {"semantic_gate_history": 50}

    @pytest.mark.parametrize(("kwargs", "message"), [
        ({"enabled": "yes"}, "enabled must be a boolean"),
        ({"timeout_ms": 499}, "timeout_ms must be an integer from 500 to 10000"),
        ({"timeout_ms": 10001}, "timeout_ms must be an integer from 500 to 10000"),
        ({"timeout_ms": 2500.0}, "timeout_ms must be an integer from 500 to 10000"),
        ({"history": 101}, "history must be an integer from 0 to 100"),
        ({"history": True}, "history must be an integer from 0 to 100"),
    ])
    def test_out_of_range_values_are_refused(self, kwargs: dict[str, Any], message: str) -> None:
        with pytest.raises(ValueError, match=message):
            _agent().set_semantic_gates(**kwargs)
