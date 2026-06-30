"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Language-agnostic verbalizer interface.

A *verbalizer* turns structured values (numbers, units, dates, emails) into
spoken-form text that a TTS engine will read correctly in a given language.
This is the contract every language plugin implements; subclass ``Verbalizer``
and override only the methods that differ for your language.

The base class is intentionally a usable, language-neutral fallback (English-ish
/ passthrough) so an unregistered language still produces sane output instead of
crashing. It depends on nothing beyond the standard library — keep it that way so
conversation_kit stays a self-contained leaf subpackage and trivially unit-testable.
"""

from __future__ import annotations

import re
from typing import ClassVar

#: Values the numeric methods accept (a spoken-form string, or a raw number).
Numeric = str | int | float


class Verbalizer:
    """Base interface + safe default behaviour. One subclass per language."""

    #: BCP-47 primary subtag this plugin handles (e.g. "pl", "de", "en").
    lang: ClassVar[str] = "und"

    #: Spoken word for each email/identifier separator. Override per language.
    SEPARATORS: ClassVar[dict[str, str]] = {
        "@": "at",
        ".": "dot",
        "-": "dash",
        "_": "underscore",
        "+": "plus",
    }

    #: Spelling-alphabet letter names (lowercase letter -> spoken name).
    #: Empty = spell with the bare character.
    LETTERS: ClassVar[dict[str, str]] = {}

    #: Unit tokens ``measure_text`` verbalizes in free text (e.g. ("mm/s", "Hz")).
    #: Empty = ``measure_text`` is a no-op (base / English passthrough).
    MEASURE_UNITS: ClassVar[tuple[str, ...]] = ()

    #: Base LLM directive for this language (e.g. "Mów po polsku."). Optional.
    INSTRUCTION: ClassVar[str] = ""

    def guidance(self, glossary: dict[str, str] | None = None) -> str:
        """LLM speaking instructions for everything done via instruction (not
        deterministic transforms). These rules are GENERIC and LANGUAGE-AGNOSTIC —
        every plugin inherits them; they're phrased about "the conversation
        language", not a specific one. The number rule is added only when this
        plugin actually verbalizes numbers (MEASURE_UNITS set). The caller's domain
        ``glossary`` is woven into a "use these terms, never coin a word" rule.

        Subclasses normally DON'T override this — they inherit it and just set
        INSTRUCTION / MEASURE_UNITS / SEPARATORS. Override only to add a genuinely
        language-specific note, or to opt out (English returns "").
        """
        parts = [
            "Speak the conversation language naturally and idiomatically. NEVER transliterate, "
            "calque, or invent a word from another language; if there is no native word, keep "
            "the original term or describe it briefly — never coin one.",
            "EMAILS: never voice raw @ or . symbols, and NEVER narrate the assembly aloud (don't "
            "say things like 'add the at-sign before gmail' or 'with dot com') — the caller must "
            "not hear the mechanics. Say an email only via its spoken-words form; if a part is "
            "unclear, ask the caller to say the whole address again.",
            "DATES: say a date as weekday + day + month in the conversation language, never the "
            "ISO or numeric form.",
            "Do not spell words out letter by letter unless asked; read abbreviations and IDs as "
            "whole tokens.",
        ]
        if self.MEASURE_UNITS:
            parts.insert(
                1,
                "NUMBERS: every reading in the tool data is already written as "
                "correct words in the conversation language — say it EXACTLY as "
                "written; never turn it back into digits, re-translate, or re-phrase "
                "the number.",
            )
        if glossary:
            terms = "; ".join(f"{k} = {v}" for k, v in glossary.items())
            parts.append(f"Use these established terms (never coin a word): {terms}.")
        return " ".join(parts)

    # --- numeric -------------------------------------------------------- #

    def number(self, value: Numeric) -> str:
        """A bare number as words. Base: passthrough (English TTS reads digits)."""
        return str(value).strip()

    def unit(self, value: Numeric, unit: str) -> str:
        """A measured value + its unit, agreement-correct. Base: '<number> <unit>'."""
        return f"{self.number(value)} {unit}".strip()

    # --- temporal ------------------------------------------------------- #

    def date(self, iso: str) -> str:
        """An ISO date (YYYY-MM-DD) spoken naturally. Base: passthrough."""
        return iso

    # --- identifiers (structure is universal; only the words differ) ---- #

    def email(self, address: str) -> str:
        """Speak an email/identifier: keep the alphanumeric runs as words, replace
        each separator with its spoken word. 'a.b@gmail.com' -> 'a <dot> b <at>
        gmail <dot> com'. Shared across languages via ``SEPARATORS``.
        """
        a = (address or "").strip()
        if not a:
            return ""
        keys = "".join(re.escape(k) for k in self.SEPARATORS)
        parts = re.split(f"([{keys}])", a)
        return " ".join(self.SEPARATORS.get(p, p) for p in parts if p != "").strip()

    def measure_text(self, text: str) -> str:
        """Verbalize every '<number> <unit>' (and '<a>-<b> <unit>' ranges) in free
        text, for the units in ``MEASURE_UNITS``. Everything else is left untouched —
        ISO/DIN codes, dates, versions, bare numbers — so there are no false
        positives. No-op unless ``MEASURE_UNITS`` is set. The unit token may be
        attached ('2.6mm/s') or spaced ('2.6 mm/s').
        """
        if not text or not self.MEASURE_UNITS:
            return text
        units = "|".join(
            re.escape(u) for u in sorted(self.MEASURE_UNITS, key=len, reverse=True)
        )
        num = r"-?\d+(?:[.,]\d+)?"
        # Ranges first (a U+2013 en dash or a hyphen between two numbers, e.g.
        # "10-100 Hz") so the single-value pass doesn't grab only the second
        # number. Both separators are accepted because an LLM may emit either. The
        # en dash in the character class below is a deliberate alternative
        # separator, so RUF001 (ambiguous-character) is suppressed on that line.
        text = re.sub(
            rf"({num})\s*[–-]\s*({num})\s*({units})(?![\w])",  # noqa: RUF001
            lambda m: (
                f"{self.number(m.group(1))} do {self.unit(m.group(2), m.group(3))}"
            ),
            text,
        )
        return re.sub(
            rf"({num})\s*({units})(?![\w])",
            lambda m: self.unit(m.group(1), m.group(2)),
            text,
        )

    def spell(self, token: str) -> str:
        """Spell a token out character by character (fallback for stubborn STT)."""
        out = []
        for ch in (token or "").strip():
            lc = ch.lower()
            if lc in self.LETTERS:
                out.append(self.LETTERS[lc])
            else:
                out.append(ch)
        return " ".join(out)
