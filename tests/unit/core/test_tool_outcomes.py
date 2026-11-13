"""
What the model gets back from a tool: vouched arguments, refusals, crashes,
and handler results that aren't a SWAIG result yet.

A tool result the model reads as an outcome must match what happened. A
crash can come after the work was done, so it reports the outcome as unknown;
a handler that declines says what is true; and data without a response is
the data, not "Function completed successfully".
"""

import json
from typing import Any

import pytest

from signalwire import AgentBase, FunctionResult, ToolRefusal
from signalwire.core.function_result import TOOL_ERROR_PROMPT, settle_result
from signalwire.core.swaig_function import (
    VOUCHED_PARAMETER,
    VOUCHED_PROMPT,
    SWAIGFunction,
)

AUTH = ("user", "pass")


def _agent() -> AgentBase:
    return AgentBase(name="outcomes", route="/", basic_auth=AUTH, suppress_logs=True)


def _rendered(agent: AgentBase, name: str) -> dict[str, Any]:
    main = json.loads(agent._render_swml())["sections"]["main"]
    ai = next(verb["ai"] for verb in main if "ai" in verb)
    return next(f for f in ai["SWAIG"]["functions"] if f["function"] == name)


def _dict(result: Any) -> dict[str, Any]:
    return result.to_dict() if isinstance(result, FunctionResult) else result


ZIP: dict[str, Any] = {"type": "object", "properties": {"zip": {"type": "string", "description": "ZIP"}},
       "required": ["zip"]}


class TestVouched:
    def test_the_model_sees_a_required_boolean(self) -> None:
        agent = _agent()
        agent.define_tool("find_store", "Find a store", ZIP, lambda a, r: "ok", vouched=True)
        parameters = _rendered(agent, "find_store")["parameters"]
        assert parameters["properties"][VOUCHED_PARAMETER]["type"] == "boolean"
        assert parameters["required"] == ["zip", VOUCHED_PARAMETER]
        # The definition the agent holds is unchanged
        assert VOUCHED_PARAMETER not in ZIP["properties"]

    def test_a_tool_that_isnt_vouched_has_no_such_argument(self) -> None:
        agent = _agent()
        agent.define_tool("find_store", "Find a store", ZIP, lambda a, r: "ok")
        assert VOUCHED_PARAMETER not in _rendered(agent, "find_store")["parameters"]["properties"]

    @pytest.mark.parametrize("args", [{"zip": "10001"}, {"zip": "10001", VOUCHED_PARAMETER: False},
                                      {"zip": "10001", VOUCHED_PARAMETER: "true"}])
    def test_unless_vouched_the_handler_does_not_run(self, args: dict[str, Any]) -> None:
        calls: list[dict[str, Any]] = []

        def find_store(a: dict[str, Any], r: dict[str, Any]) -> str:
            calls.append(a)
            return "ok"

        agent = _agent()
        agent.define_tool("find_store", "Find a store", ZIP, find_store, vouched=True)
        result = _dict(agent.on_function_call("find_store", args, {}))
        assert calls == []
        assert result["response"] == {"tool_result": "find_store was not run.",
                                      "tool_prompt": VOUCHED_PROMPT}

    def test_vouched_the_handler_runs_without_the_argument(self) -> None:
        calls: list[dict[str, Any]] = []

        def find_store(a: dict[str, Any], r: dict[str, Any]) -> FunctionResult:
            calls.append(a)
            return FunctionResult("Store 12")

        agent = _agent()
        agent.define_tool("find_store", "Find a store", ZIP, find_store, vouched=True)
        result = _dict(agent.on_function_call(
            "find_store", {"zip": "10001", VOUCHED_PARAMETER: True}, {}))
        assert calls == [{"zip": "10001"}]
        assert result["response"] == "Store 12"

    def test_execute_follows_the_same_rule(self) -> None:
        func = SWAIGFunction("find_store", lambda a, r: FunctionResult("Store 12"),
                             "Find a store", ZIP, vouched=True)
        assert func.execute({"zip": "1"})["response"]["tool_result"] == "find_store was not run."
        assert func.execute({"zip": "1", VOUCHED_PARAMETER: True})["response"] == "Store 12"

    def test_the_decorator_takes_it(self) -> None:
        class Shop(AgentBase):
            @AgentBase.tool(name="find_store", description="Find a store", parameters=ZIP,
                            vouched=True)
            def find_store(self, args: dict[str, Any], raw_data: dict[str, Any]) -> str:
                return "ok"

        agent = Shop(name="shop", route="/", basic_auth=AUTH, suppress_logs=True)
        assert VOUCHED_PARAMETER in _rendered(agent, "find_store")["parameters"]["required"]


class TestRefusalsAndCrashes:
    def test_a_refusal_is_the_handlers_own_outcome(self) -> None:
        def place_order(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
            raise ToolRefusal("place_order was not run: the item is out of stock.",
                              "Offer the caller the similar items in stock.")

        agent = _agent()
        agent.define_tool("place_order", "Place the order", {}, place_order)
        assert _dict(agent.on_function_call("place_order", {}, {}))["response"] == {
            "tool_result": "place_order was not run: the item is out of stock.",
            "tool_prompt": "Offer the caller the similar items in stock."}

    def test_a_crash_reports_an_unknown_outcome_without_the_exception(self) -> None:
        def charge(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
            raise RuntimeError("db password rejected for user admin")

        agent = _agent()
        agent.define_tool("charge", "Charge the card", {}, charge)
        result = _dict(agent.on_function_call("charge", {}, {}))
        assert result["response"] == {
            "tool_result": "charge failed before it finished, so whether it took effect is unknown.",
            "tool_prompt": TOOL_ERROR_PROMPT}
        assert "password" not in json.dumps(result)

    async def test_an_async_handler_is_treated_the_same(self) -> None:
        async def refuses(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
            raise ToolRefusal("lookup was not run: no account matches.")

        async def crashes(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
            raise ValueError("boom")

        agent = _agent()
        agent.define_tool("lookup", "Look up", {}, refuses)
        agent.define_tool("charge", "Charge", {}, crashes)
        refused = _dict(await agent.on_function_call("lookup", {}, {}))
        crashed = _dict(await agent.on_function_call("charge", {}, {}))
        assert refused["response"] == {"tool_result": "lookup was not run: no account matches."}
        assert crashed["response"]["tool_result"].startswith("charge failed before it finished")

    def test_execute_reports_a_crash_the_same_way(self) -> None:
        def boom(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
            raise RuntimeError("boom")

        result = SWAIGFunction("charge", boom, "Charge").execute({})
        assert result["response"]["tool_result"].startswith("charge failed before it finished")


class TestHandlerResults:
    @pytest.mark.parametrize(("returned", "expected"), [
        ({"response": "Done."}, {"response": "Done."}),
        # A result with actions only is a SWAIG result; execute() used to
        # replace it, actions and all, with "Function completed successfully"
        ({"action": [{"say": "Hi"}]}, {"action": [{"say": "Hi"}]}),
        ({"balance": 12.5, "currency": "USD"}, {"response": '{"balance": 12.5, "currency": "USD"}'}),
        ({}, {"response": "lookup returned no result, so whether it took effect is unknown."}),
    ])
    def test_a_dict_is_a_result_or_its_data(self, returned: dict[str, Any],
                                            expected: dict[str, Any]) -> None:
        assert settle_result("lookup", returned) == expected
        func = SWAIGFunction("lookup", lambda a, r: dict(returned), "Look up")
        assert func.execute({}) == expected
        agent = _agent()
        agent.define_tool("lookup", "Look up", {}, lambda a, r: dict(returned))
        assert _dict(agent.on_function_call("lookup", {}, {})) == expected

    def test_none_keeps_its_result(self) -> None:
        assert settle_result("lookup", None).to_dict() == {
            "response": "Function executed successfully"}
