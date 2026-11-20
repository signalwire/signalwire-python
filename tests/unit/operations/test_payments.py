"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The Payments pack: the amount from charge(), read back, the pay verb, and the
result read from what the platform recorded.
"""

from __future__ import annotations

from typing import Any

import pytest

from signalwire import AgentBase
from signalwire.operations import Charge, Operations, PaymentResult, Payments, Refuse, ServiceAgent
from signalwire.testing import CallSimulator


def said(args: dict[str, Any]) -> dict[str, Any]:
    return {**args, "data_supplied_by_user": True}


INVOICES = {"1042": "54.04"}


def charge(call: Any, invoice: str) -> Charge:
    if invoice not in INVOICES:
        raise Refuse(f"{invoice} isn't one of their invoices.")
    return Charge(INVOICES[invoice], f"invoice {invoice}")


def billing(results: list[PaymentResult], **kwargs: Any) -> ServiceAgent:
    agent = ServiceAgent("billing", role="You take payments for a utility.", currency="USD", suppress_logs=True)
    agent.add_language("English", "en-US", "rime.spore")
    Payments(connector_url="https://pay.example.com/connector", charge=charge,
             on_result=lambda call, result: results.append(result), **kwargs).add_to(agent)
    return agent


def pay_of(actions: list[Any]) -> dict[str, Any]:
    swml = next(a["SWML"] for a in actions if isinstance(a, dict) and "SWML" in a)
    return dict(swml["sections"]["main"][0]["pay"])


def test_a_payment_is_read_back_taken_and_recorded() -> None:
    results: list[PaymentResult] = []
    agent = billing(results)
    sim = CallSimulator(agent, request_fields={"SWMLVars": {"pay_result": "success",
                                                            "pay_payment_results": '{"payment_confirmation_code": "C9"}'}})
    assert sim.params["swaig_post_swml_vars"] == ["pay_result", "pay_payment_results"]
    sim.call("take_payment", said({"paying_for": "1042"}))
    assert sim.global_data["ops"]["waiting"]["read_back"] == (
        "Take $54.04 on a card for invoice 1042. Shall I go ahead?")
    sim.caller("yes")
    started = sim.call("confirm_change", {"change": "take_payment"})
    assert started.response.startswith("Done. The card details are taken next, on the keypad.")
    assert started.tool_prompt == "Tell them they'll enter their card on the keypad now, and say nothing more."
    pay = pay_of(started.actions)
    assert (pay["charge_amount"], pay["currency"], pay["language"], pay["voice"]) == (
        "54.04", "usd", "en-US", "rime.spore")
    assert pay["token_type"] == "one-time" and pay["description"] == "invoice 1042"
    assert pay["valid_card_types"] == "visa mastercard amex", "the pay helper's own, as documented"
    finished = next(a["SWML"] for a in started.actions if isinstance(a, dict) and "SWML" in a)
    assert finished["sections"]["main"][1]["set"]["ai_response"] == (
        "The payment has finished. Call payment_result now, and say nothing before it.")
    # Nothing is counted until the platform says how it went
    assert sim.global_data["ops"]["history"][-1]["money"] == "0"
    out = sim.call("payment_result", said({}))
    assert out.response == "Done. The payment went through: $54.04 for invoice 1042."
    assert sim.global_data["ops"]["history"][-1]["money"] == "54.04"
    assert results[0].succeeded and results[0].details == {"payment_confirmation_code": "C9"}
    again = sim.call("payment_result", said({}))
    assert again.response == "No payment was started."


def test_a_failed_payment_charges_nothing() -> None:
    results: list[PaymentResult] = []
    sim = CallSimulator(billing(results), request_fields={"SWMLVars": {"pay_result": "too-many-failed-attempts"}})
    sim.call("take_payment", said({"paying_for": "1042"}))
    sim.caller("yes")
    sim.call("confirm_change", {"change": "take_payment"})
    out = sim.call("payment_result", said({}))
    assert out.response == "The payment didn't go through (too-many-failed-attempts). Nothing was charged."
    assert sim.global_data["ops"]["history"][-1]["money"] == "0"
    assert results[0].result == "too-many-failed-attempts" and not results[0].succeeded


def test_without_the_platforms_result_nothing_is_assumed() -> None:
    sim = CallSimulator(billing([]))
    sim.call("take_payment", said({"paying_for": "1042"}))
    sim.caller("yes")
    sim.call("confirm_change", {"change": "take_payment"})
    out = sim.call("payment_result", said({}))
    assert out.response == "There's no payment result yet."


def test_the_amount_comes_from_charge_and_needs_a_currency_and_a_language() -> None:
    sim = CallSimulator(billing([]))
    refused = sim.call("take_payment", said({"paying_for": "9"}))
    assert refused.response == "Nothing is changed: 9 isn't one of their invoices."
    no_language = ServiceAgent("b", role="r", currency="USD", suppress_logs=True)
    Payments(connector_url="https://pay.example.com/c", charge=charge).add_to(no_language)
    with pytest.raises(ValueError, match="language"):
        no_language.compile()
    ops = Operations(role="r")
    Payments(connector_url="https://pay.example.com/c", charge=charge, language="es-MX").add_to(ops)
    agent = ops.install(AgentBase(name="t", suppress_logs=True))
    with pytest.raises(ValueError, match="needs a currency"):
        import asyncio

        from signalwire.operations import CallContext

        asyncio.run(ops._prepare(CallContext(ops, {}), ops._operations["take_payment"], {"paying_for": "1042"}))
    assert agent._params["swaig_post_swml_vars"] == ["pay_result", "pay_payment_results"]
