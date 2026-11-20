"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Payments: a task pack that takes a card payment the caller agreed to, without
the model ever hearing the card. Add it to an ``Operations`` or a
``ServiceAgent`` with ``add_to``.

The amount comes from your ``charge`` function, never from the model: the
caller names what they're paying (an invoice, an order), ``charge`` says how
much, and that's read back for their yes. Then the platform's pay verb takes
the card on the keypad and charges it through your payment connector. When
it's finished, the model is told to call the result tool, which reads the
outcome the platform recorded (not anything the model says) and records a
payment that went through, with its money, in the call's history.
"""

from __future__ import annotations

import inspect
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from types import MappingProxyType
from typing import Any

from signalwire.core.function_result import FunctionResult
from signalwire.core.agent_base import AgentBase
from signalwire.operations.agent import Operations, _Said
from signalwire.operations.model import Change, Field, Operation, Refuse, Write
from signalwire.operations.money import amount_of, check_currency
from signalwire.operations.wording import _Wording

PAY_VARS = ("pay_result", "pay_payment_results")
"""The SWML variables the pay verb sets that the result tool reads; the pack
asks the platform to post them with every tool request
(``swaig_post_swml_vars``)."""


@dataclass(frozen=True)
class Charge:
    """What a payment is for and how much, as ``charge`` gives it."""

    amount: Decimal | int | float | str
    """How much to charge: more than 0."""
    description: str
    """What it's for, as it's said: "invoice 1042, for March"."""
    currency: str | None = None
    """Its ISO 4217 code; defaults to the pack's, else the service's."""


@dataclass(frozen=True)
class PaymentResult:
    """How a payment went, as ``on_result`` gets it."""

    result: str
    """The platform's ``pay_result``: ``success``, ``too-many-failed-attempts``, ``payment-connector-error``,
    ``caller-interrupted-with-star``, ``caller-hung-up``, ``validation-error``, ``internal-error``,
    ``relay-pay-stop``, ``empty`` or ``failed``."""
    amount: Decimal
    currency: str
    description: str
    paying_for: str
    """What the caller said they were paying, as ``charge`` got it."""
    details: Mapping[str, Any] = field(default_factory=dict)
    """The platform's ``pay_payment_results``: the token, confirmation code and masked card, when there are."""

    @property
    def succeeded(self) -> bool:
        return self.result == "success"


PAYMENTS_WORDING: Mapping[str, str] = MappingProxyType(
    {
        "tool": "Take a card payment for something they owe, read back first.",
        "tool.paying_for": "What they're paying, such as an invoice or order number, as they said it.",
        "ask.paying_for": "What would they like to pay?",
        "read_back": "Take {amount} on a card for {description}. Shall I go ahead?",
        "started": "The card details are taken next, on the keypad.",
        "started.then": "Tell them they'll enter their card on the keypad now, and say nothing more.",
        "finished": "The payment has finished. Call {tool} now, and say nothing before it.",
        "result.tool": "How the payment that just finished went. Call it once the payment has finished.",
        "paid": "The payment went through: {amount} for {description}.",
        "paid.then": "Tell them it went through.",
        "failed": "The payment didn't go through ({result}). Nothing was charged.",
        "failed.then": "Tell them, and ask if they'd like to try again.",
        "unknown": "There's no payment result yet.",
        "unknown.then": "If a payment just finished, tell them you can't confirm it went through, and offer to "
        "check another way.",
        "none": "No payment was started.",
        "amount.bad": "{paying_for} has nothing to pay.",
    }
)
"""Every key the ``Payments`` pack's words come from, with its default."""


class Payments:
    """
    Take a card payment, read back first, through your payment connector.

    Example:
        Payments(
            connector_url="https://pay.example.com/connector",
            charge=lambda call, invoice: Charge(billing.balance(invoice), f"invoice {invoice}"),
            currency="USD",
            language="en-US",
        ).add_to(agent)
    """

    def __init__(
        self,
        *,
        connector_url: str,
        charge: Callable[[Any, str], Any],
        currency: str | None = None,
        language: str | None = None,
        voice: str | None = None,
        security_code: bool = True,
        postal_code: bool = True,
        max_attempts: int = 1,
        reusable: bool = False,
        card_types: Sequence[str] | None = None,
        status_url: str | None = None,
        connector_parameters: Mapping[str, str] | None = None,
        on_result: Callable[[Any, PaymentResult], Any] | None = None,
        before_identity: bool = False,
        tool: str = "take_payment",
        result_tool: str = "payment_result",
        wording: Mapping[str, str] | None = None,
        state_key: str = "payments",
    ) -> None:
        """
        Args:
            connector_url: Your payment connector, which the platform sends
                the card to.
            charge: ``charge(call, paying_for)`` returns the ``Charge`` for
                what the caller said they're paying; it may be ``async``,
                and may raise ``Refuse`` (nothing owed, not theirs) or
                ``Need``.
            currency: The ISO 4217 code of the amounts; defaults to the
                service's ``currency``. A payment needs one.
            language: The language code the platform's card prompts are
                spoken in, such as ``"en-US"``; defaults to the agent's
                first language. A payment needs one.
            voice: The voice of the card prompts; defaults to the agent's
                first language's voice.
            security_code: Whether the card's security code is asked for.
            postal_code: Whether the billing postal code is asked for.
            max_attempts: How many times the caller may try the card.
            reusable: True for a token the connector can charge again (a
                card kept on file), False for one charge.
            card_types: The card types taken, such as ``["visa",
                "mastercard"]``; Visa, Mastercard and American Express when
                None, as ``FunctionResult.pay`` takes them.
            status_url: Where the platform posts each step of the payment.
            connector_parameters: More name/value pairs for the connector.
            on_result: ``on_result(call, result)`` gets every
                ``PaymentResult``, for your records; it may be ``async``.
            before_identity: True to take payments from callers who aren't
                identified.
            tool: The payment tool's name.
            result_tool: The result tool's name.
            wording: Words in place of the defaults, by key; the keys are
                those of ``PAYMENTS_WORDING``.
            state_key: Where in ``call.state`` the payment under way is
                kept.
        """
        if not connector_url:
            raise ValueError("Payments needs connector_url, your payment connector")
        self._connector, self._charge = connector_url, charge
        self._currency = check_currency(currency)
        self._language, self._voice = language, voice
        self._prompts: tuple[str, str | None] | None = (
            None  # the language and voice, once installed
        )
        self._security_code, self._postal_code = security_code, postal_code
        self._attempts = max_attempts
        self._token = "reusable" if reusable else "one-time"
        self._cards = " ".join(card_types) if card_types else None
        self._status_url = status_url
        self._parameters = [
            {"name": k, "value": v} for k, v in (connector_parameters or {}).items()
        ]
        self._on_result = on_result
        self._before_identity = before_identity
        self.tool, self.result_tool = tool, result_tool
        """The tools' names."""
        self._w = _Wording(PAYMENTS_WORDING, wording, "Payments", "PAYMENTS_WORDING")
        self._key = state_key

    def add_to(self, target: Any) -> Any:
        """Register the pack's operations on an ``Operations`` or a ``ServiceAgent``; returns it."""
        ops = getattr(target, "ops", target)
        if not isinstance(ops, Operations):
            raise TypeError(
                f"add_to takes an Operations or a ServiceAgent, not {type(target).__name__}"
            )
        ops._install_hooks.append(self._installing)
        w, pack = self._w, self

        async def take_prepare(self: Operation, call: Any, f: Any) -> Change:
            found = pack._charge(call, f.paying_for)
            if inspect.isawaitable(found):
                found = await found
            charge = found if isinstance(found, Charge) else Charge(**dict(found))
            amount = amount_of(charge.amount)
            currency = (
                check_currency(charge.currency)
                or pack._currency
                or call.service._currency
            )
            if not currency:
                raise ValueError(
                    "a payment needs a currency: give Charge, Payments or the service one"
                )
            if amount <= 0:
                raise Refuse(w("amount.bad", paying_for=f.paying_for))
            money = call.service._money_format(amount, currency)
            return Change(
                read_back=w("read_back", amount=money, description=charge.description),
                touches=[f"payment:{f.paying_for}"],
                writes=[
                    Write(
                        "take_payment",
                        amount=str(amount),
                        currency=currency,
                        description=charge.description,
                        paying_for=f.paying_for,
                    )
                ],
                done=w("started"),
                then=w("started.then"),
            )

        def take_apply(self: Operation, call: Any, write: Write) -> None:
            a = write.args
            call.state[pack._key] = {
                **(call.state.get(pack._key) or {}),
                "pending": dict(a),
            }
            call.act(pack._pay(call, a))

        ops.operation(
            type(
                "TakePayment",
                (Operation,),
                {
                    "__doc__": w("tool"),
                    "prepare": take_prepare,
                    "apply": take_apply,
                    "before_identity": self._before_identity,
                    "paying_for": Field(
                        str, w("tool.paying_for"), ask=w("ask.paying_for")
                    ),
                },
            ),
            tool=self.tool,
            kind=self.tool,
        )

        async def result_prepare(self: Operation, call: Any, f: Any) -> Change:
            mine = dict(call.state.get(pack._key) or {})
            pending = mine.pop("pending", None)
            if not pending:
                raise _Said(w("none"))
            swml_vars = call.raw_data.get("SWMLVars")
            result = (
                str((swml_vars or {}).get("pay_result") or "")
                if isinstance(swml_vars, Mapping)
                else ""
            )
            if not result:
                raise _Said(w("unknown"), w("unknown.then"))
            call.state[pack._key] = (
                mine  # settled: a later call to this tool finds none under way
            )
            outcome = PaymentResult(
                result=result,
                amount=amount_of(pending["amount"]),
                currency=str(pending["currency"]),
                description=str(pending["description"]),
                paying_for=str(pending["paying_for"]),
                details=_details(swml_vars.get("pay_payment_results")),
            )
            if pack._on_result is not None:
                done = pack._on_result(call, outcome)
                if inspect.isawaitable(done):
                    await done
            if not outcome.succeeded:
                raise _Said(w("failed", result=result), w("failed.then"))
            money = call.service._money_format(outcome.amount, outcome.currency)
            return Change(
                read_back="",
                touches=[f"payment:{outcome.paying_for}"],
                money=[outcome.amount],
                currency=outcome.currency,
                done=w("paid", amount=money, description=outcome.description),
                then=w("paid.then"),
            )

        ops.operation(
            type(
                "PaymentResult",
                (Operation,),
                {
                    "__doc__": w("result.tool"),
                    "prepare": result_prepare,
                    "confirm": False,
                    "before_identity": self._before_identity,
                },
            ),
            tool=self.result_tool,
            kind=self.result_tool,
        )
        return target

    def _installing(self, agent: AgentBase) -> None:
        """
        What the pack needs of the agent: the pay verb's variables posted with
        each tool request, and a language for the card prompts, the agent's
        first unless one was given. Checked here, so an agent missing one
        fails when it's set up rather than on a call.
        """
        have = agent._params.get("swaig_post_swml_vars")
        if have is not True:
            listed = list(have) if isinstance(have, (list, tuple)) else []
            agent.set_param(
                "swaig_post_swml_vars", list(dict.fromkeys([*listed, *PAY_VARS]))
            )
        languages = getattr(agent, "_languages", None) or []
        first = languages[0] if languages and isinstance(languages[0], Mapping) else {}
        language = self._language or first.get("code")
        if not language:
            raise ValueError(
                "Payments needs a language for the card prompts: give it language=, or the agent a language"
            )
        self._prompts = (str(language), self._voice or first.get("voice"))

    def _pay(self, call: Any, a: Mapping[str, Any]) -> FunctionResult:
        """The pay verb for a payment the caller said yes to, with what the model is told once it's finished."""
        assert self._prompts is not None  # noqa: S101  # set when the service was installed
        language, voice = self._prompts
        options: dict[str, Any] = {
            "charge_amount": str(a["amount"]),
            "currency": str(a["currency"]).lower(),
            "language": language,
            "description": str(a["description"]),
            "security_code": self._security_code,
            "postal_code": self._postal_code,
            "max_attempts": self._attempts,
            "token_type": self._token,
            "ai_response": self._w("finished", tool=self.result_tool),
        }
        if voice:
            options["voice"] = voice
        if self._cards:
            options["valid_card_types"] = self._cards
        if self._status_url:
            options["status_url"] = self._status_url
        if self._parameters:
            options["parameters"] = list(self._parameters)
        return FunctionResult().pay(self._connector, **options)


def _details(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except ValueError:
            return {}
        return dict(parsed) if isinstance(parsed, Mapping) else {}
    return {}


__all__ = ["PAYMENTS_WORDING", "PAY_VARS", "Charge", "PaymentResult", "Payments"]
