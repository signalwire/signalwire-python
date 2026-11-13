"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Numbers as an English text-to-speech voice should say them.

The platform normalizes text before its pronunciation rules run, so a bare
number is already words by then: ``add_pronunciation`` can't make "10001"
read digit by digit. Give the model, or a ``say`` action, the words instead.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

_DIGITS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
)
_TEENS = (
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
)
_TENS = (
    "",
    "",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
)
_SCALES = ("", "thousand", "million", "billion", "trillion")

# Currency: (major singular, major plural, minor singular, minor plural, minor
# units per major); None minor for a currency without one
_CURRENCIES: dict[str, tuple[str, str, str | None, str | None, int]] = {
    "USD": ("dollar", "dollars", "cent", "cents", 100),
    "CAD": ("dollar", "dollars", "cent", "cents", 100),
    "AUD": ("dollar", "dollars", "cent", "cents", 100),
    "NZD": ("dollar", "dollars", "cent", "cents", 100),
    "EUR": ("euro", "euros", "cent", "cents", 100),
    "GBP": ("pound", "pounds", "penny", "pence", 100),
    "MXN": ("peso", "pesos", "centavo", "centavos", 100),
    "INR": ("rupee", "rupees", "paisa", "paise", 100),
    "JPY": ("yen", "yen", None, None, 1),
}


def number_words(n: int) -> str:
    """
    ``n`` in English words: ``number_words(1405)`` is "one thousand four
    hundred five".

    Raises:
        ValueError: For a number of a quadrillion or more.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise ValueError(f"number_words takes an int, got {n!r}")
    if n < 0:
        return f"minus {number_words(-n)}"
    if n == 0:
        return "zero"
    if n >= 1000 ** len(_SCALES):
        raise ValueError(f"{n} is too large to say")
    parts: list[str] = []
    for scale in reversed(range(len(_SCALES))):
        chunk = (n // 1000**scale) % 1000
        if chunk:
            parts.append(_below_thousand(chunk))
            if _SCALES[scale]:
                parts.append(_SCALES[scale])
    return " ".join(parts)


def _below_thousand(n: int) -> str:
    words: list[str] = []
    if n >= 100:
        words += [_DIGITS[n // 100], "hundred"]
        n %= 100
    if n >= 20:
        words.append(_TENS[n // 10] + (f"-{_DIGITS[n % 10]}" if n % 10 else ""))
    elif n >= 10:
        words.append(_TEENS[n - 10])
    elif n:
        words.append(_DIGITS[n])
    return " ".join(words)


def say_digits(
    text: str | int,
    group: int | Sequence[int] | None = None,
    *,
    zero: str = "zero",
) -> str:
    """
    The digits in ``text``, one word each, as a voice should read a ZIP
    code, an account number or a phone number.

    ``say_digits("415-555-0192")`` is "four one five, five five five, zero
    one nine two": with ``group`` left out, the groups are the ones the
    text has, separated by anything that isn't a digit. ``group=3`` splits
    the digits into threes; ``group=(3, 3, 4)`` into those sizes, the rest
    in a last group. A comma between groups makes the voice pause.

    Args:
        text: The digits, with any separators.
        group: The group size, or the sizes in order.
        zero: The word for 0, such as "oh".

    Returns:
        The words, or "" when ``text`` has no digits.
    """
    text = str(text)
    if group is None:
        groups = re.findall(r"\d+", text)
    else:
        digits = re.sub(r"\D", "", text)
        sizes = [group] if isinstance(group, int) else list(group)
        if not sizes or any(isinstance(s, bool) or s < 1 for s in sizes):
            raise ValueError(f"group sizes must be positive, got {group!r}")
        groups = []
        position = 0
        while position < len(digits):
            index = len(groups)
            if isinstance(group, int):
                size = group
            elif index < len(sizes):
                size = sizes[index]
            else:
                size = len(digits) - position  # the rest, in a last group
            groups.append(digits[position : position + size])
            position += size
    names = [zero, *_DIGITS[1:]]
    return ", ".join(" ".join(names[int(d)] for d in g) for g in groups if g)


def say_last_digits(text: str | int, n: int = 4, *, zero: str = "zero") -> str:
    """
    The last ``n`` digits of ``text``, one word each: for "a card ending
    in ..." or "the account ending in ...".

    ``say_last_digits("4111 1111 1111 1234")`` is "one two three four".

    Args:
        text: The number, with any separators.
        n: How many of its last digits.
        zero: The word for 0, such as "oh".

    Returns:
        The words, or "" when ``text`` has no digits.
    """
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError(f"n must be a positive int, got {n!r}")
    digits = re.sub(r"\D", "", str(text))
    return say_digits(digits[-n:], group=n, zero=zero)


def say_money(amount: float | int | str | Decimal, currency: str = "USD") -> str:
    """
    An amount of money in words: ``say_money(14.5)`` is "fourteen dollars
    and fifty cents".

    The amount is rounded to the currency's smallest unit, half up. The
    currencies are USD, CAD, AUD, NZD, EUR, GBP, MXN, INR and JPY.

    Args:
        amount: The amount, in the currency's major unit (dollars, not
            cents).
        currency: The ISO 4217 code.

    Returns:
        The words, such as "one dollar", "five cents" or "minus two
        pounds and one penny".

    Raises:
        ValueError: For an amount that isn't a number, or another currency.
    """
    names = _CURRENCIES.get(currency.upper())
    if names is None:
        raise ValueError(
            f"say_money doesn't know {currency!r}; it takes {sorted(_CURRENCIES)}"
        )
    major_one, major_many, minor_one, minor_many, per_major = names
    if isinstance(amount, bool):
        raise ValueError(f"amount must be a number, got {amount!r}")
    try:
        value = Decimal(str(amount))
    except InvalidOperation:
        raise ValueError(f"amount must be a number, got {amount!r}") from None
    if not value.is_finite():
        raise ValueError(f"amount must be a number, got {amount!r}")
    minor_total = int(
        (abs(value) * per_major).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    )
    major, minor = divmod(minor_total, per_major)
    parts: list[str] = []
    if major or not minor or minor_one is None:
        parts.append(f"{number_words(major)} {major_one if major == 1 else major_many}")
    if minor and minor_one is not None and minor_many is not None:
        parts.append(f"{number_words(minor)} {minor_one if minor == 1 else minor_many}")
    words = " and ".join(parts)
    return f"minus {words}" if value < 0 and minor_total else words
