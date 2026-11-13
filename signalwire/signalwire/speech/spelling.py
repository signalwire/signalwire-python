"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

What a caller spelled out, from the recognizer's text.

A caller spells a name, a code or an email address in many ways: letter by
letter ("s m i t h"), with letter names ("ess em eye tee aitch"), with words
("S as in Sam"), with the NATO alphabet ("sierra mike"), or with "double l"
for two. ``read_spelled`` turns all of them into units, one letter, digit or
symbol each, and ``spoken_email`` reads an address said aloud.

The recognizer confuses some letters, and which ones depends on the
recognizer and the voice. ``spelling_variants`` expands units with
confusion groups you supply, measured on your own calls; none are built in.
English only.
"""

from __future__ import annotations

import itertools
import re
from collections.abc import Iterable, Mapping, Sequence

_LETTER_NAMES: dict[str, str] = {
    "a": "A", "ay": "A",
    "b": "B", "be": "B", "bee": "B",
    "c": "C", "see": "C", "sea": "C", "cee": "C",
    "d": "D", "dee": "D",
    "e": "E", "ee": "E",
    "f": "F", "ef": "F", "eff": "F",
    "g": "G", "gee": "G", "jee": "G",
    "h": "H", "aitch": "H", "haitch": "H",
    "i": "I", "eye": "I",
    "j": "J", "jay": "J",
    "k": "K", "kay": "K",
    "l": "L", "el": "L", "ell": "L",
    "m": "M", "em": "M",
    "n": "N", "en": "N",
    "o": "O",
    "p": "P", "pee": "P",
    "q": "Q", "cue": "Q", "queue": "Q",
    "r": "R", "ar": "R", "are": "R",
    "s": "S", "es": "S", "ess": "S",
    "t": "T", "tee": "T", "tea": "T",
    "u": "U", "you": "U",
    "v": "V", "vee": "V",
    "w": "W",
    "x": "X", "ex": "X",
    "y": "Y", "why": "Y", "wye": "Y",
    "z": "Z", "zee": "Z", "zed": "Z",
}  # fmt: skip

_NATO: dict[str, str] = {
    "alpha": "A", "alfa": "A", "bravo": "B", "charlie": "C", "delta": "D",
    "echo": "E", "foxtrot": "F", "golf": "G", "hotel": "H", "india": "I",
    "juliet": "J", "juliett": "J", "kilo": "K", "lima": "L", "mike": "M",
    "november": "N", "oscar": "O", "papa": "P", "quebec": "Q", "romeo": "R",
    "sierra": "S", "tango": "T", "uniform": "U", "victor": "V",
    "whiskey": "W", "whisky": "W", "xray": "X", "x-ray": "X", "yankee": "Y",
    "zulu": "Z",
}  # fmt: skip

_DIGIT_WORDS: dict[str, str] = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
}  # fmt: skip

_SYMBOLS: dict[str, str] = {
    "dot": ".", "period": ".", "point": ".",
    "at": "@",
    "dash": "-", "hyphen": "-",
    "underscore": "_",
    "plus": "+",
    "slash": "/",
}  # fmt: skip

# Words that say how the next letter is written, not which it is
_CASE_WORDS = frozenset(
    {"capital", "uppercase", "upper", "lowercase", "lower", "small"}
)

_TOKEN = re.compile(r"[a-z0-9@._+/'-]+")


def _unit(word: str, *, oh_is_zero: bool) -> str | None:
    """The letter, digit or symbol one spoken word names, or None."""
    if word == "oh":
        return "0" if oh_is_zero else "O"
    for table in (_LETTER_NAMES, _NATO, _DIGIT_WORDS, _SYMBOLS):
        if word in table:
            return table[word]
    if len(word) == 1 and (word.isdigit() or word in "@._+/-"):
        return word
    return None


def read_spelled(text: str, *, oh_is_zero: bool = False) -> list[str]:
    """
    The units a caller spelled: one uppercase letter, digit or symbol each.

    ``read_spelled("S as in Sam, m i t h")`` and ``read_spelled("sierra mike
    india tango hotel")`` are both ``["S", "M", "I", "T", "H"]``.
    "double l" is two L's, and "capital" before a letter is dropped. A word
    that names no letter, such as "smith", is taken as spelled: its letters.

    Args:
        text: The recognizer's text.
        oh_is_zero: True to read "oh" as the digit 0, for a code of digits;
            by default it's the letter O.

    Returns:
        The units, in order.
    """
    tokens = _spelling_tokens(text)
    units: list[str] = []
    i = 0
    while i < len(tokens):
        word = tokens[i]
        # "S as in Sam": the letter, and the word after "as in" is skipped
        if tokens[i + 1 : i + 3] == ["as", "in"]:
            letter = _unit(word, oh_is_zero=False)
            units.append(letter if letter and letter.isalpha() else word[0].upper())
            i += 4
            continue
        if word in _CASE_WORDS:
            i += 1
            continue
        if word == "double" and i + 1 < len(tokens):
            following = tokens[i + 1]
            if following in ("you", "u"):
                units.append("W")
            else:
                unit = _unit(following, oh_is_zero=oh_is_zero)
                units += [unit, unit] if unit else _letters(following) * 2
            i += 2
            continue
        unit = _unit(word, oh_is_zero=oh_is_zero)
        units += [unit] if unit else _letters(word)
        i += 1
    return units


def _spelling_tokens(text: str) -> list[str]:
    """The words of spelled text. A hyphen inside a word, as a recognizer
    writes "S-M-I-T-H", separates units; a spoken "dash" is the symbol."""
    tokens: list[str] = []
    for token in _TOKEN.findall(text.lower()):
        if "-" in token and len(token) > 1 and token not in _NATO:
            tokens += [part for part in token.split("-") if part]
        else:
            tokens.append(token)
    return tokens


def _letters(word: str) -> list[str]:
    return [
        c.upper() if c.isalpha() else c for c in word if c.isalnum() or c in "@._+/-"
    ]


def spoken_email(text: str) -> str:
    """
    An email address said aloud, as text: "john dot smith at example dot com"
    is "john.smith@example.com".

    Words are kept as words, and letters, digits and symbols spelled out are
    joined to them, so "j o h n underscore smith at example dot co dot uk" is
    "john_smith@example.co.uk". An address the recognizer already wrote as
    one is returned lowercased.

    Args:
        text: The recognizer's text.

    Returns:
        The address, lowercased. Check it before you use it: this reads the
        words, it doesn't validate them.
    """
    compact = re.sub(r"\s+", "", text.strip().lower())
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", compact):
        return compact
    tokens = _TOKEN.findall(text.lower())
    parts: list[str] = []
    i = 0
    while i < len(tokens):
        word = tokens[i]
        if word == "at" and tokens[i + 1 : i + 2] == ["sign"]:
            parts.append("@")
            i += 2
            continue
        if tokens[i + 1 : i + 3] == ["as", "in"]:
            letter = _unit(word, oh_is_zero=False)
            parts.append((letter if letter and letter.isalpha() else word[0]).lower())
            i += 4
            continue
        if word == "double" and i + 1 < len(tokens):
            unit = _unit(tokens[i + 1], oh_is_zero=False)
            doubled = (unit or tokens[i + 1]).lower()
            parts.append(doubled * 2)
            i += 2
            continue
        if word in _SYMBOLS:
            parts.append(_SYMBOLS[word])
        elif word in _NATO:
            parts.append(_NATO[word].lower())
        elif word in _DIGIT_WORDS:
            parts.append(_DIGIT_WORDS[word])
        elif len(word) == 1 or (word in _LETTER_NAMES and len(word) <= 2):
            parts.append(_LETTER_NAMES.get(word, word).lower())
        else:
            parts.append(word)
        i += 1
    return "".join(parts)


def spelling_variants(
    units: Sequence[str],
    groups: Mapping[str, Iterable[str]],
    *,
    positions: Iterable[int] | None = None,
    limit: int = 50,
) -> list[str]:
    """
    The spellings ``units`` could be, given letters the recognizer confuses.

    ``groups`` maps a unit to the units it may be heard as, such as
    ``{"S": "F", "F": "S", "M": "N", "N": "M"}``: measure them on your own
    recognizer and voices. The units as heard come first, then the variants
    with one change, then two, and so on, up to ``limit``. Look each up in
    your own records; the first that matches is the likeliest.

    Args:
        units: The units, from ``read_spelled``.
        groups: For each unit, the units it may have been.
        positions: Only these positions vary, such as the words the
            recognizer was least sure of (``AgentBase.speech_finals()``
            gives each word's confidence). Default: all.
        limit: The most spellings to return.

    Returns:
        The spellings, joined.
    """
    allowed = set(range(len(units))) if positions is None else set(positions)
    choices = [
        [unit, *[u for u in groups.get(unit, ()) if u != unit]]
        if n in allowed
        else [unit]
        for n, unit in enumerate(units)
    ]
    varying = [n for n, c in enumerate(choices) if len(c) > 1]
    spellings: list[str] = ["".join(units)]
    for changes in range(1, len(varying) + 1):
        for where in itertools.combinations(varying, changes):
            for picks in itertools.product(*(choices[n][1:] for n in where)):
                spelled = list(units)
                for n, pick in zip(where, picks, strict=True):
                    spelled[n] = pick
                spellings.append("".join(spelled))
                if len(spellings) >= limit:
                    return spellings
    return spellings
