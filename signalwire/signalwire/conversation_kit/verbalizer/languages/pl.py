"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Polish verbalizer plugin.

Deterministic spoken Polish for numbers, units, dates and emails — the cases a
TTS/LLM mangles. Self-contained (no num2words dependency): Polish cardinals are
a closed algorithm and we need exact control over decimal place-value reading
and unit case agreement anyway.

Grammar per the project's polish-tts-verbalization spec:
- Decimals read "<int> przecinek <fraction-as-cardinal>" (place-value, never
  digit-by-digit), and the unit goes GENITIVE SINGULAR after any decimal.
- Integer unit agreement by Polish buckets (see `_bucket`).
- Dates: weekday nominative + day ordinal-genitive + month genitive + year.
"""

from __future__ import annotations

from datetime import date as _date
from decimal import Decimal
from typing import ClassVar

from ..base import Numeric, Verbalizer

# --- cardinals ---------------------------------------------------------- #

_ONES = [
    "zero",
    "jeden",
    "dwa",
    "trzy",
    "cztery",
    "pięć",
    "sześć",
    "siedem",
    "osiem",
    "dziewięć",
    "dziesięć",
    "jedenaście",
    "dwanaście",
    "trzynaście",
    "czternaście",
    "piętnaście",
    "szesnaście",
    "siedemnaście",
    "osiemnaście",
    "dziewiętnaście",
]
_TENS = {
    2: "dwadzieścia",
    3: "trzydzieści",
    4: "czterdzieści",
    5: "pięćdziesiąt",
    6: "sześćdziesiąt",
    7: "siedemdziesiąt",
    8: "osiemdziesiąt",
    9: "dziewięćdziesiąt",
}
_HUNDREDS = {
    1: "sto",
    2: "dwieście",
    3: "trzysta",
    4: "czterysta",
    5: "pięćset",
    6: "sześćset",
    7: "siedemset",
    8: "osiemset",
    9: "dziewięćset",
}


def _bucket(n: int) -> str:
    """Polish quantity-agreement bucket for a non-negative integer count."""
    if n == 1:
        return "nom_sg"
    if n % 100 in (12, 13, 14):
        return "gen_pl"
    if n % 10 in (2, 3, 4):
        return "nom_pl"
    return "gen_pl"


def _under_1000(n: int) -> str:
    parts = []
    if n // 100:
        parts.append(_HUNDREDS[n // 100])
    rem = n % 100
    if rem < 20:
        if rem:
            parts.append(_ONES[rem])
    else:
        parts.append(_TENS[rem // 10])
        if rem % 10:
            parts.append(_ONES[rem % 10])
    return " ".join(parts)


def cardinal(n: int) -> str:
    """Non-negative integer -> Polish words (0..999_999, covers our value range)."""
    if n < 0:
        return "minus " + cardinal(-n)
    if n == 0:
        return "zero"
    if n < 1000:
        return _under_1000(n)
    th, rem = divmod(n, 1000)
    parts = []
    if th == 1:
        parts.append("tysiąc")
    else:
        word = {"nom_sg": "tysiąc", "nom_pl": "tysiące", "gen_pl": "tysięcy"}[
            _bucket(th)
        ]
        parts.append(_under_1000(th))
        parts.append(word)
    if rem:
        parts.append(_under_1000(rem))
    return " ".join(parts)


# --- ordinals (genitive) for dates -------------------------------------- #

_ORD_ONES = {
    1: "pierwszego",
    2: "drugiego",
    3: "trzeciego",
    4: "czwartego",
    5: "piątego",
    6: "szóstego",
    7: "siódmego",
    8: "ósmego",
    9: "dziewiątego",
    10: "dziesiątego",
    11: "jedenastego",
    12: "dwunastego",
    13: "trzynastego",
    14: "czternastego",
    15: "piętnastego",
    16: "szesnastego",
    17: "siedemnastego",
    18: "osiemnastego",
    19: "dziewiętnastego",
}
_ORD_TENS = {
    2: "dwudziestego",
    3: "trzydziestego",
    4: "czterdziestego",
    5: "pięćdziesiątego",
    6: "sześćdziesiątego",
    7: "siedemdziesiątego",
    8: "osiemdziesiątego",
    9: "dziewięćdziesiątego",
}


def _ordinal_gen(n: int) -> str:
    """Genitive ordinal 1..99 (day-of-month and year tail share these forms)."""
    if n < 20:
        return _ORD_ONES[n]
    t, o = divmod(n, 10)
    return _ORD_TENS[t] if o == 0 else f"{_ORD_TENS[t]} {_ORD_ONES[o]}"


def _year(y: int) -> str:
    if 2001 <= y <= 2099:
        return f"dwa tysiące {_ordinal_gen(y - 2000)} roku"
    return f"{cardinal(y)} roku"


_MONTHS = {
    1: "stycznia",
    2: "lutego",
    3: "marca",
    4: "kwietnia",
    5: "maja",
    6: "czerwca",
    7: "lipca",
    8: "sierpnia",
    9: "września",
    10: "października",
    11: "listopada",
    12: "grudnia",
}
_WEEKDAYS = [
    "poniedziałek",
    "wtorek",
    "środa",
    "czwartek",
    "piątek",
    "sobota",
    "niedziela",
]


# --- units (nom_sg / nom_pl / gen_pl for integers, gen_sg for decimals) -- #

_UNITS = {
    "mm/s": {
        "nom_sg": "milimetr",
        "nom_pl": "milimetry",
        "gen_pl": "milimetrów",
        "gen_sg": "milimetra",
        "suffix": " na sekundę",
    },
    "Hz": {
        "nom_sg": "herc",
        "nom_pl": "herce",
        "gen_pl": "herców",
        "gen_sg": "herca",
        "suffix": "",
    },
    "°C": {
        "nom_sg": "stopień",
        "nom_pl": "stopnie",
        "gen_pl": "stopni",
        "gen_sg": "stopnia",
        "suffix": " Celsjusza",
    },
    "hPa": {
        "nom_sg": "hektopaskal",
        "nom_pl": "hektopaskale",
        "gen_pl": "hektopaskali",
        "gen_sg": "hektopaskala",
        "suffix": "",
    },
    # "procent" is invariant after a number in modern usage (5 procent, 22 procent).
    "%": {
        "nom_sg": "procent",
        "nom_pl": "procent",
        "gen_pl": "procent",
        "gen_sg": "procent",
        "suffix": "",
    },
    "m/s²": {
        "nom_sg": "metr",
        "nom_pl": "metry",
        "gen_pl": "metrów",
        "gen_sg": "metra",
        "suffix": " na sekundę do kwadratu",
    },
    "m/s2": {
        "nom_sg": "metr",
        "nom_pl": "metry",
        "gen_pl": "metrów",
        "gen_sg": "metra",
        "suffix": " na sekundę do kwadratu",
    },
    "km/h": {
        "nom_sg": "kilometr",
        "nom_pl": "kilometry",
        "gen_pl": "kilometrów",
        "gen_sg": "kilometra",
        "suffix": " na godzinę",
    },
}

_PL_LETTERS = {
    "a": "a",
    "ą": "ą",
    "b": "be",
    "c": "ce",
    "ć": "cie",
    "d": "de",
    "e": "e",
    "ę": "ę",
    "f": "ef",
    "g": "gie",
    "h": "ha",
    "i": "i",
    "j": "jot",
    "k": "ka",
    "l": "el",
    "ł": "eł",
    "m": "em",
    "n": "en",
    "ń": "eń",
    "o": "o",
    "ó": "o kreskowane",
    "p": "pe",
    "q": "ku",
    "r": "er",
    "s": "es",
    "ś": "eś",
    "t": "te",
    "u": "u",
    "v": "fau",
    "w": "wu",
    "x": "iks",
    "y": "igrek",
    "z": "zet",
    "ź": "ziet",
    "ż": "żet",
}


def _decimal(value: Numeric) -> Decimal:
    return Decimal(str(value).strip().replace(",", "."))


class PolishVerbalizer(Verbalizer):
    lang: ClassVar[str] = "pl"
    # email/identifier separators spoken in Polish
    SEPARATORS: ClassVar[dict[str, str]] = {
        "@": "małpka",
        ".": "kropka",
        "-": "myślnik",
        "_": "podkreślnik",
        "+": "plus",
    }
    LETTERS: ClassVar[dict[str, str]] = _PL_LETTERS
    MEASURE_UNITS: ClassVar[tuple[str, ...]] = tuple(_UNITS)
    INSTRUCTION: ClassVar[str] = "Mów po polsku. Odpowiadaj w języku polskim."
    # guidance() is inherited from the base — the speaking rules are language-agnostic.
    # Polish-ness comes from INSTRUCTION + the glossary terms + the transforms above.

    def number(self, value: Numeric) -> str:
        d = _decimal(value)
        neg = d < 0
        d = abs(d)
        int_part = int(d)
        txt = format(d, "f")
        frac = txt.split(".")[1].rstrip("0") if "." in txt else ""
        words = cardinal(int_part)
        if frac:
            lead = len(frac) - len(frac.lstrip("0"))
            rest = frac.lstrip("0")
            fwords = ["zero"] * lead + ([cardinal(int(rest))] if rest else [])
            words = f"{words} przecinek {' '.join(fwords)}"
        return f"minus {words}" if neg else words

    def unit(self, value: Numeric, unit: str) -> str:
        forms = _UNITS.get(unit)
        num = self.number(value)
        if not forms:
            return f"{num} {unit}".strip()
        d = _decimal(value)
        key = "gen_sg" if d != d.to_integral_value() else _bucket(abs(int(d)))
        return f"{num} {forms[key]}{forms['suffix']}"

    def spell(self, token: str) -> str:
        out = []
        for ch in (token or "").strip():
            lc = ch.lower()
            if lc in self.LETTERS:
                out.append(self.LETTERS[lc])
            elif ch.isdigit():
                out.append(cardinal(int(ch)))
            else:
                out.append(ch)
        return " ".join(out)

    def date(self, iso: str, with_weekday: bool = True, with_year: bool = True) -> str:
        y, m, d = (int(p) for p in iso.split("-"))
        parts = []
        if with_weekday:
            parts.append(_WEEKDAYS[_date(y, m, d).weekday()] + ",")
        parts.append(_ordinal_gen(d))
        parts.append(_MONTHS[m])
        if with_year:
            parts.append(_year(y))
        return " ".join(parts)
