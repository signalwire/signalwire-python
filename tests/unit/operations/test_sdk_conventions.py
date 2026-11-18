"""
Operations against the SDK's conventions: field types as Python writes them,
the per-request context's name, installing once under concurrent first
requests, and where an offered tool goes.
"""

from __future__ import annotations

import threading
from typing import Any

import pytest

from signalwire import FunctionResult
from signalwire.operations import CallContext, Change, Field, Operation, ServiceAgent
from signalwire.operations.model import _schema_of


def test_a_field_takes_a_pep_604_optional() -> None:
    assert _schema_of(str | None) == {"type": "string"}
    assert _schema_of(list[int] | None) == {"type": "array", "items": {"type": "integer"}}
    assert Field(int | None, "A count.").schema() == {"type": "integer", "description": "A count."}


def test_the_request_context_is_callcontext() -> None:
    # Not Call: signalwire.relay.Call is a live call
    import signalwire.operations as ops

    assert ops.CallContext is CallContext
    assert not hasattr(ops, "Call")


def _store() -> ServiceAgent:
    agent = ServiceAgent("store", role="You run a store.")

    @agent.operation(tool="cancel_order")
    class Cancel(Operation):
        """Cancel an order."""

        order_id = Field(str, "The order.")

        def prepare(self, call: Any, f: Any) -> Change:
            return Change(read_back=f"Cancel {f.order_id}. Shall I?", touches=[f"order:{f.order_id}"])

    return agent


def test_concurrent_first_requests_install_once() -> None:
    agent = _store()
    installs = []
    real = agent.ops.install

    def counted(target: Any) -> Any:
        installs.append(1)
        return real(target)

    agent.ops.install = counted  # type: ignore[method-assign,assignment]
    threads = [threading.Thread(target=agent.compile) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert installs == [1]


def test_a_failed_install_is_tried_again() -> None:
    agent = _store()
    real = agent.ops.install
    calls = []

    def flaky(target: Any) -> Any:
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("first install fails")
        return real(target)

    agent.ops.install = flaky  # type: ignore[method-assign,assignment]
    with pytest.raises(RuntimeError):
        agent.compile()
    agent.compile()
    assert len(calls) == 2


def _steps(agent: ServiceAgent) -> dict[str, list[str]]:
    agent.compile()
    steps = agent.define_contexts().to_dict()["default"]["steps"]
    return {s["name"]: list(s.get("functions") or []) for s in steps}


def test_an_offer_goes_to_every_step_but_confirm_by_default() -> None:
    agent = _store()
    agent.define_tool("weather", "Weather.", {}, lambda args, raw: FunctionResult("Sunny."))
    agent.offer("weather")
    steps = _steps(agent)
    assert "weather" in steps["main"]
    assert "weather" not in steps["confirm"]


def test_an_offer_can_name_its_steps() -> None:
    agent = _store()
    agent.define_tool("menu", "Menu.", {}, lambda args, raw: FunctionResult("Soup."))
    agent.offer("menu", steps=["confirm"])
    steps = _steps(agent)
    assert "menu" in steps["confirm"] and "menu" not in steps["main"]
