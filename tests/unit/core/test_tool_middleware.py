"""
Tool middleware and the dedupe of transport retries.

SignalWire sends a tool request again, with the same body, after a timeout,
a failed connection or a 5xx (webhook.c). The retry carries the first
request's tool_call_id; a call the model makes again gets a new one, and some
calls carry none (actions.c). So a retry is the same call_id, tool_call_id and
function, and only that is answered from the first attempt.
"""

import asyncio
import threading
from typing import Any

import pytest

from signalwire import AgentBase, FunctionResult, ToolRefusal
from signalwire.core.tool_middleware import CallNext, ResendDedupe, resolve

AUTH = ("user", "pass")


def _agent() -> AgentBase:
    return AgentBase(name="middleware", route="/", basic_auth=AUTH, suppress_logs=True)


def _dict(result: Any) -> dict[str, Any]:
    return result.to_dict() if isinstance(result, FunctionResult) else result


def _raw(tool_call_id: str | None = "tc-1", call_id: str = "call-1") -> dict[str, Any]:
    raw: dict[str, Any] = {"call_id": call_id}
    if tool_call_id is not None:
        raw["tool_call_id"] = tool_call_id
    return raw


class TestMiddleware:
    def test_middleware_runs_in_order_around_the_handler(self) -> None:
        seen: list[str] = []

        def outer(name: str, args: dict[str, Any], raw: dict[str, Any], call_next: CallNext) -> Any:
            seen.append(f"outer {name}")
            return call_next({**args, "city": args["city"].title()}, raw)

        def inner(name: str, args: dict[str, Any], raw: dict[str, Any], call_next: CallNext) -> Any:
            seen.append(f"inner {args['city']}")
            result = call_next(args, raw)
            seen.append("inner after")
            return result

        def weather(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
            seen.append(f"handler {args['city']}")
            return FunctionResult(f"Sunny in {args['city']}")

        agent = _agent().add_tool_middleware(outer)
        agent.define_tool("weather", "Weather", {}, weather, middleware=[inner])
        result = _dict(agent.on_function_call("weather", {"city": "rome"}, _raw()))
        assert result["response"] == "Sunny in Rome"
        assert seen == ["outer weather", "inner Rome", "handler Rome", "inner after"]

    def test_a_middleware_can_answer_without_the_handler(self) -> None:
        def closed(name: str, args: dict[str, Any], raw: dict[str, Any], call_next: CallNext) -> Any:
            return FunctionResult(tool_result=f"{name} was not run: the store is closed.")

        calls: list[Any] = []
        agent = _agent().add_tool_middleware(closed)
        agent.define_tool("order", "Order", {}, lambda a, r: calls.append(a))
        assert _dict(agent.on_function_call("order", {}, _raw()))["response"] == {
            "tool_result": "order was not run: the store is closed."}
        assert calls == []

    def test_a_refusal_or_crash_in_middleware_is_an_outcome(self) -> None:
        def refuse(name: str, args: dict[str, Any], raw: dict[str, Any], call_next: CallNext) -> Any:
            raise ToolRefusal("order was not run.", "Ask for the account first.")

        def crash(name: str, args: dict[str, Any], raw: dict[str, Any], call_next: CallNext) -> Any:
            raise RuntimeError("secret")

        refused, crashed = _agent(), _agent()
        refused.add_tool_middleware(refuse).define_tool("order", "Order", {}, lambda a, r: "x")
        crashed.add_tool_middleware(crash).define_tool("order", "Order", {}, lambda a, r: "x")
        assert _dict(refused.on_function_call("order", {}, _raw()))["response"]["tool_prompt"] == (
            "Ask for the account first.")
        result = _dict(crashed.on_function_call("order", {}, _raw()))
        assert result["response"]["tool_result"].startswith("order failed before it finished")
        assert "secret" not in str(result)

    async def test_an_async_middleware_around_an_async_handler(self) -> None:
        async def stamp(name: str, args: dict[str, Any], raw: dict[str, Any],
                        call_next: CallNext) -> Any:
            result = await resolve(call_next(args, raw))
            return FunctionResult(f"{result.response} (checked)")

        async def weather(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
            return FunctionResult("Sunny")

        agent = _agent().add_tool_middleware(stamp)
        agent.define_tool("weather", "Weather", {}, weather)
        assert _dict(await agent.on_function_call("weather", {}, _raw()))["response"] == (
            "Sunny (checked)")


class TestResendDedupe:
    def _counting_agent(self, delay: threading.Event | None = None) -> tuple[AgentBase, list[str]]:
        runs: list[str] = []

        def charge(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
            runs.append(raw.get("tool_call_id", ""))
            if delay is not None:
                delay.wait(5)
            return FunctionResult(f"Charged, run {len(runs)}")

        agent = _agent()
        agent.define_tool("charge", "Charge", {}, charge)
        return agent, runs

    def test_a_retry_after_the_first_finished_gets_its_result(self) -> None:
        agent, runs = self._counting_agent()
        first = _dict(agent.on_function_call("charge", {}, _raw("tc-1")))
        retry = _dict(agent.on_function_call("charge", {}, _raw("tc-1")))
        assert runs == ["tc-1"]
        assert retry == first == {"response": "Charged, run 1"}

    def test_a_retry_while_the_first_is_running_waits_for_it(self) -> None:
        release = threading.Event()
        agent, runs = self._counting_agent(release)
        results: list[dict[str, Any]] = []
        threads = [threading.Thread(target=lambda: results.append(
            _dict(agent.on_function_call("charge", {}, _raw("tc-1"))))) for _ in range(2)]
        for thread in threads:
            thread.start()
        while not runs:
            threading.Event().wait(0.01)
        release.set()
        for thread in threads:
            thread.join(5)
        assert runs == ["tc-1"]
        assert results == [{"response": "Charged, run 1"}] * 2

    @pytest.mark.parametrize(("first", "second"), [
        (_raw("tc-1"), _raw("tc-2")),                    # the model called it again
        (_raw("tc-1", "call-1"), _raw("tc-1", "call-2")),  # another call
        (_raw(None), _raw(None)),                        # no tool_call_id
    ])
    def test_other_calls_run(self, first: dict[str, Any], second: dict[str, Any]) -> None:
        agent, runs = self._counting_agent()
        agent.on_function_call("charge", {}, first)
        agent.on_function_call("charge", {}, second)
        assert len(runs) == 2

    def test_it_can_be_turned_off(self) -> None:
        agent, runs = self._counting_agent()
        agent.set_tool_resend_dedupe(False)
        agent.on_function_call("charge", {}, _raw("tc-1"))
        agent.on_function_call("charge", {}, _raw("tc-1"))
        assert len(runs) == 2
        agent.set_tool_resend_dedupe(True)
        agent.on_function_call("charge", {}, _raw("tc-9"))
        agent.on_function_call("charge", {}, _raw("tc-9"))
        assert len(runs) == 3

    def test_per_request_copies_share_it(self) -> None:
        agent, runs = self._counting_agent()
        first, second = agent._create_ephemeral_copy(), agent._create_ephemeral_copy()
        first.on_function_call("charge", {}, _raw("tc-1"))
        second.on_function_call("charge", {}, _raw("tc-1"))
        assert runs == ["tc-1"]

    async def test_an_async_retry_awaits_the_first(self) -> None:
        release = asyncio.Event()
        runs: list[int] = []

        async def charge(args: dict[str, Any], raw: dict[str, Any]) -> FunctionResult:
            runs.append(1)
            await release.wait()
            return FunctionResult("Charged")

        agent = _agent()
        agent.define_tool("charge", "Charge", {}, charge)
        first = asyncio.ensure_future(agent.on_function_call("charge", {}, _raw("tc-1")))
        await asyncio.sleep(0)
        retry = asyncio.ensure_future(agent.on_function_call("charge", {}, _raw("tc-1")))
        await asyncio.sleep(0)
        release.set()
        results = [_dict(await first), _dict(await retry)]
        assert runs == [1]
        assert results == [{"response": "Charged"}] * 2

    def test_old_results_are_dropped(self) -> None:
        dedupe = ResendDedupe(ttl=0)
        runs: list[int] = []

        def call_next(args: dict[str, Any], raw: dict[str, Any]) -> str:
            runs.append(1)
            return "ok"

        dedupe("charge", {}, _raw("tc-1"), call_next)
        dedupe("charge", {}, _raw("tc-1"), call_next)
        assert len(runs) == 2
