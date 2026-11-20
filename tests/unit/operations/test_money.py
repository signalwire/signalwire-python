"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Money in an operations agent: exact amounts, a currency per change or per
service, totals for each currency apart, and a formatter that can be replaced.
"""

from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any

import pytest

from signalwire import AgentBase
from signalwire.operations import CallContext, Change, Field, Operation, Operations, Write, format_money
from signalwire.testing import CallSimulator


def said(args: dict[str, Any]) -> dict[str, Any]:
    return {**args, "data_supplied_by_user": True}


@pytest.mark.parametrize(
    ("amount", "currency", "text"),
    [
        (54.04, "USD", "$54.04"),
        ("1234.5", "EUR", "€1,234.50"),
        (5404.4, "JPY", "¥5,404"),
        (Decimal("1.2345"), "KWD", "KWD 1.235"),
        (54.04, "CHF", "CHF 54.04"),
        (12, "CAD", "CA$12.00"),
        (54.04, "XOF", "54.04 XOF"),
        (54, "XOF", "54 XOF"),
        (54.04, None, "54.04"),
        (54.5, None, "54.50"),
        (54, None, "54"),
        (-5, "USD", "-$5.00"),
        (0.125, "USD", "$0.13"),
        (0.1 + 0.2, "USD", "$0.30"),
    ],
)
def test_format_money(amount: Any, currency: str | None, text: str) -> None:
    assert format_money(amount, currency) == text


def test_a_currency_is_an_iso_code_and_an_amount_a_number() -> None:
    for bad in ("usd", "US", "DOLLARS", ""):
        with pytest.raises(ValueError, match="ISO 4217"):
            format_money(1, bad)
        with pytest.raises(ValueError, match="ISO 4217"):
            Operations(role="r", currency=bad)
    with pytest.raises(ValueError):
        format_money("ten", "USD")
    with pytest.raises(TypeError):
        format_money(True, "USD")


def till_ops(**kwargs: Any) -> Operations:
    ops = Operations(role="You run a till.", **kwargs)
    ops.writes_with(lambda call, w: None)

    @ops.operation(tool="move_money")
    class Move(Operation):
        """Refund or charge an amount."""

        amount = Field(str, "The amount, less than 0 to refund.")
        currency = Field(str, "Its currency code, if not the till's.", required=False)
        what = Field(str, "What it's for.")

        def prepare(self, call: Any, f: Any) -> Change:
            return Change(read_back=f"Move {f.amount} for {f.what}. Shall I?", touches=[f.what],
                          writes=[Write("move", amount=f.amount)], money=[f.amount], currency=f.currency)

    return ops


def till(**kwargs: Any) -> AgentBase:
    return till_ops(**kwargs).install(AgentBase(name="t", suppress_logs=True))


def settle(sim: CallSimulator, amount: str, what: str, currency: str | None = None) -> Any:
    sim.call("move_money", said({"amount": amount, "what": what, "currency": currency}))
    sim.caller("yes")
    return sim.call("confirm_change", {"change": "move"})


def test_totals_are_kept_for_each_currency_apart() -> None:
    sim = CallSimulator(till(currency="USD"))
    settle(sim, "-10", "a")
    settle(sim, "5", "b", "EUR")
    out = settle(sim, "-2.50", "c")
    assert out.response.endswith(
        "In all, the changes made in this call come to $12.50 back to them and €5.00 charged."
    )
    history = sim.global_data["ops"]["history"]
    assert [(h["money"], h["currency"]) for h in history] == [("-10", "USD"), ("5", "EUR"), ("-2.50", "USD")]
    assert sim.global_data["ops"]["v"] == 1


def test_without_a_currency_amounts_stand_alone() -> None:
    sim = CallSimulator(till())
    settle(sim, "-10", "a")
    out = settle(sim, "-2.5", "b")
    assert out.response.endswith("come to 12.50 back to them.")
    assert sim.global_data["ops"]["history"][0]["currency"] == ""


def test_money_format_writes_the_totals() -> None:
    sim = CallSimulator(till(currency="EUR", money_format=lambda amount, code: f"{amount} {code} netos"))
    settle(sim, "-10", "a")
    out = settle(sim, "-2.5", "b")
    assert "12.5 EUR netos back to them" in out.response


def test_money_a_change_cant_state_fails_when_its_built() -> None:
    ops = till_ops()
    move = ops._operations["move"]
    call = CallContext(ops, {})
    with pytest.raises(ValueError, match="Move.prepare returned a Change whose money"):
        asyncio.run(ops._prepare(call, move, {"amount": "ten", "what": "a"}))
    with pytest.raises(ValueError, match="ISO 4217"):
        asyncio.run(ops._prepare(call, move, {"amount": "1", "what": "b", "currency": "euros"}))
