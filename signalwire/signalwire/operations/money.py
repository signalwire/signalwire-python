"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Money as an operations agent states it: amounts kept exactly (``Decimal``), in
the currency each change gives, or the service's. ``format_money`` writes an
amount the way the model reads it, for the currencies in ``CURRENCIES`` and any
other ISO 4217 code; ``Operations(money_format=...)`` replaces it.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from types import MappingProxyType

_CODE = re.compile(r"[A-Z]{3}")

CURRENCIES: Mapping[str, tuple[str, int]] = MappingProxyType(
    {
        # code: (what goes before the amount, digits after the point)
        "USD": ("$", 2),
        "EUR": ("€", 2),
        "GBP": ("£", 2),
        "JPY": ("¥", 0),
        "CNY": ("CN¥", 2),
        "CAD": ("CA$", 2),
        "AUD": ("A$", 2),
        "NZD": ("NZ$", 2),
        "MXN": ("MX$", 2),
        "BRL": ("R$", 2),
        "HKD": ("HK$", 2),
        "INR": ("₹", 2),
        "KRW": ("₩", 0),
        "ILS": ("₪", 2),
        "PHP": ("₱", 2),
        "VND": ("₫", 0),
        "CHF": ("CHF ", 2),
        "SEK": ("SEK ", 2),
        "NOK": ("NOK ", 2),
        "DKK": ("DKK ", 2),
        "PLN": ("PLN ", 2),
        "CZK": ("CZK ", 2),
        "HUF": ("HUF ", 2),
        "SGD": ("SGD ", 2),
        "ZAR": ("ZAR ", 2),
        "AED": ("AED ", 2),
        "SAR": ("SAR ", 2),
        "TRY": ("TRY ", 2),
        "THB": ("THB ", 2),
        "CLP": ("CLP ", 0),
        "COP": ("COP ", 2),
        "ISK": ("ISK ", 0),
        "KWD": ("KWD ", 3),
        "BHD": ("BHD ", 3),
        "JOD": ("JOD ", 3),
        "OMR": ("OMR ", 3),
    }
)
"""The currencies ``format_money`` writes with a symbol or code before the
amount and their own number of decimal places. A symbol several currencies
share is written so it isn't ambiguous (``CA$``, ``A$``)."""


def amount_of(value: object) -> Decimal:
    """
    An amount as a ``Decimal``: from an int, a float (by its shortest
    decimal form, so ``54.04`` stays ``54.04``), a string or a ``Decimal``.
    """
    if isinstance(value, bool):
        raise TypeError("an amount of money can't be a bool")
    if isinstance(value, Decimal):
        amount = value
    elif isinstance(value, (int, float, str)):
        try:
            amount = Decimal(str(value).strip())
        except InvalidOperation:
            raise ValueError(f"{value!r} isn't an amount of money") from None
    else:
        raise TypeError(
            f"an amount of money is a number or a string, not {type(value).__name__}"
        )
    if not amount.is_finite():
        raise ValueError(f"{value!r} isn't an amount of money")
    return amount


def check_currency(code: str | None) -> str | None:
    """A currency code as given, once it's checked to be three capital letters (ISO 4217)."""
    if code is not None and not (isinstance(code, str) and _CODE.fullmatch(code)):
        raise ValueError(
            f"currency {code!r} must be an ISO 4217 code, three capital letters such as 'EUR'"
        )
    return code


def format_money(amount: object, currency: str | None = None) -> str:
    """
    An amount as the model reads it: ``$54.04``, ``€54.04``, ``¥5,404``,
    ``CHF 54.04``. A currency not in ``CURRENCIES`` goes after the amount
    (``54.04 XOF``). With no currency the amount stands alone, with its
    cents when it has any (``54.04``, ``54``).

    Args:
        amount: The amount: a number, a numeric string or a ``Decimal``.
        currency: Its ISO 4217 code, or None.
    """
    value = amount_of(amount)
    sign, value = ("-" if value < 0 else ""), abs(value)
    code = check_currency(currency)
    if code is not None and code in CURRENCIES:
        symbol, digits = CURRENCIES[code]
        return f"{sign}{symbol}{_digits(value, digits)}"
    plain = _digits(
        value, 0 if value == value.to_integral_value() else max(2, _places(value))
    )
    return f"{sign}{plain} {code}" if code else f"{sign}{plain}"


def _places(value: Decimal) -> int:
    exponent = value.normalize().as_tuple().exponent
    return -exponent if isinstance(exponent, int) and exponent < 0 else 0


def _digits(value: Decimal, digits: int) -> str:
    return f"{value.quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP):,.{digits}f}"


__all__ = ["CURRENCIES", "amount_of", "format_money"]
