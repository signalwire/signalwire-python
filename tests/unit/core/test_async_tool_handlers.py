"""
Tests for tools whose handlers are defined with ``async def``.

The SDK used to call a tool's handler and use the return value directly, so
an async handler's coroutine was never awaited: the handler's body never ran,
and the caller got the coroutine's repr as the tool response. Each dispatch
boundary now finishes the call. The ``/swaig`` endpoint awaits the handler on
the request's event loop, and synchronous callers (the serverless entry
points, ``swaig-test`` and ``SWAIGFunction.execute()``) run it to completion.
"""

import asyncio
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from signalwire import AgentBase
from signalwire.core.function_result import FunctionResult
from signalwire.core.mixins.serverless_mixin import ServerlessMixin
from signalwire.core.mixins.tool_mixin import ToolMixin
from signalwire.core.swaig_function import SWAIGFunction, _resolve_awaitable

CITY = {"city": {"type": "string", "description": "City name"}}


async def lookup(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    await asyncio.sleep(0)
    return FunctionResult(f"Weather in {args['city']}: sunny")


async def returns_none(args: dict[str, Any], raw_data: dict[str, Any]) -> None:
    await asyncio.sleep(0)


async def fails(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    await asyncio.sleep(0)
    raise RuntimeError("upstream timeout")


def sync_lookup(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    return FunctionResult(f"Sync weather in {args['city']}")


def _agent() -> AgentBase:
    # secure=False: these tests are about dispatch, not per-call tokens.
    agent = AgentBase(name="async-tools", route="/agent", basic_auth=("user", "pass"))
    for name, parameters, handler in [
        ("lookup", CITY, lookup),
        ("returns_none", {}, returns_none),
        ("fails", {}, fails),
        ("sync_lookup", CITY, sync_lookup),
    ]:
        agent.define_tool(
            name=name,
            description=name,
            parameters=parameters,
            handler=handler,
            secure=False,
        )

    @agent.tool(name="typed_lookup", description="Typed weather lookup", secure=False)
    async def typed_lookup(city: str) -> FunctionResult:
        """Look up the weather.

        Args:
            city: City name
        """
        await asyncio.sleep(0)
        return FunctionResult(f"Typed weather in {city}")

    return agent


def _swaig_body(function: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "function": function,
        "argument": {"parsed": [args or {}]},
        "call_id": "call-1",
    }


class TestSwaigEndpoint:
    """POST /swaig awaits an async handler on the request's event loop."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(_agent().get_app())

    def _post(
        self, client: TestClient, function: str, args: dict[str, Any] | None = None
    ) -> Any:
        response = client.post(
            "/agent/swaig", json=_swaig_body(function, args), auth=("user", "pass")
        )
        assert response.status_code == 200
        return response.json()

    def test_async_handler_result(self, client: TestClient) -> None:
        assert (
            self._post(client, "lookup", {"city": "Paris"})["response"]
            == "Weather in Paris: sunny"
        )

    def test_async_typed_handler_result(self, client: TestClient) -> None:
        assert (
            self._post(client, "typed_lookup", {"city": "Oslo"})["response"]
            == "Typed weather in Oslo"
        )

    def test_async_handler_returning_none(self, client: TestClient) -> None:
        assert (
            self._post(client, "returns_none")["response"]
            == "Function executed successfully"
        )

    def test_async_handler_error(self, client: TestClient) -> None:
        body = self._post(client, "fails")
        assert body["response"] == "Error executing function 'fails': upstream timeout"

    def test_sync_handler_unchanged(self, client: TestClient) -> None:
        assert (
            self._post(client, "sync_lookup", {"city": "Rome"})["response"]
            == "Sync weather in Rome"
        )


class TestServerless:
    """Both serverless implementations run an async handler to completion."""

    @pytest.mark.parametrize("mixin", [ToolMixin, ServerlessMixin])
    def test_async_handler_result(self, mixin: Any) -> None:
        result = mixin._execute_swaig_function(
            _agent(), "lookup", {"city": "Lima"}, "call-1"
        )
        assert result["response"] == "Weather in Lima: sunny"

    @pytest.mark.parametrize("mixin", [ToolMixin, ServerlessMixin])
    def test_async_handler_error(self, mixin: Any) -> None:
        result = mixin._execute_swaig_function(_agent(), "fails", {}, "call-1")
        assert (
            result["response"] == "Error executing function 'fails': upstream timeout"
        )


class TestResolveAwaitable:
    def test_outside_an_event_loop(self) -> None:
        result = _resolve_awaitable(
            _agent().on_function_call("lookup", {"city": "Kyiv"}, {})
        )
        assert result.to_dict()["response"] == "Weather in Kyiv: sunny"

    def test_inside_a_running_event_loop(self) -> None:
        """asyncio.run() can't nest, so the awaitable runs on another thread's loop."""

        async def call_from_async_code() -> Any:
            return _resolve_awaitable(
                _agent().on_function_call("lookup", {"city": "Cairo"}, {})
            )

        result = asyncio.run(call_from_async_code())
        assert result.to_dict()["response"] == "Weather in Cairo: sunny"

    def test_plain_values_pass_through(self) -> None:
        value = FunctionResult("ready")
        assert _resolve_awaitable(value) is value

    def test_swaig_function_execute(self) -> None:
        func = SWAIGFunction(
            name="lookup", handler=lookup, description="Weather", parameters=CITY
        )
        assert (
            func.execute({"city": "Quito"}, {})["response"] == "Weather in Quito: sunny"
        )


def test_swaig_test_cli_runs_async_handler(tmp_path: Path) -> None:
    agent_file = tmp_path / "async_agent.py"
    agent_file.write_text(
        textwrap.dedent("""
        import asyncio
        from signalwire import AgentBase
        from signalwire.core.function_result import FunctionResult

        agent = AgentBase(name="async-cli", route="/")

        async def lookup(args, raw_data):
            await asyncio.sleep(0)
            return FunctionResult(f"CLI weather in {args['city']}")

        agent.define_tool(
            name="lookup",
            description="Weather",
            parameters={"city": {"type": "string", "description": "City"}},
            handler=lookup,
        )
    """)
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "signalwire.cli.swaig_test_wrapper",
            str(agent_file),
            "--exec",
            "lookup",
            "--city",
            "Lagos",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert "CLI weather in Lagos" in completed.stdout, (
        completed.stdout + completed.stderr
    )
    assert "coroutine" not in completed.stdout
