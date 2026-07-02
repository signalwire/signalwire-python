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

    #: Generic technical acronyms ``spell_acronyms`` reads letter-by-letter so a TTS
    #: engine says "er em es", not "rms". Language-agnostic membership (only the
    #: spelling differs per language); kept to widely-recognized, domain-neutral
    #: acronyms on purpose. An application adds its OWN domain acronyms by subclassing
    #: and overriding (e.g. ``ACRONYMS = Verbalizer.ACRONYMS | {"PPV"}``). Capitalization
    #: alone never triggers spelling, so an all-caps name (a customer code, a device id)
    #: is left spoken as-is.
    ACRONYMS: ClassVar[frozenset[str]] = frozenset({"DIN", "ISO", "RMS", "UTC"})

    #: Whether this language verbalizes dates/times in ``datetime_text``. The base and
    #: English read ISO dates/times acceptably as-is, so it stays a no-op there.
    VERBALIZES_DATETIME: ClassVar[bool] = False

    #: Spoken connector between the two ends of a numeric range in ``measure_text``
    #: ("10 to 100 Hz"). Override per language (Polish "do", German "bis").
    RANGE_WORD: ClassVar[str] = "to"

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

    def date(self, iso: str, with_weekday: bool = True, with_year: bool = True) -> str:
        """An ISO date (YYYY-MM-DD) spoken naturally. Base: passthrough."""
        return iso

    def time(self, hour: int, minute: int) -> str:
        """A 24-hour clock time spoken naturally. Base: passthrough 'HH:MM'.
        Raises ValueError outside 0-23 / 0-59 (``datetime_text`` catches it)."""
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(f"time out of range: {hour}:{minute}")
        return f"{hour:02d}:{minute:02d}"

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
        # ``RANGE_WORD`` is the language's connector ("to"/"do"/"bis"). The two ends
        # are read in isolation; a language that inflects range endpoints for case
        # (Polish idiomatically "od <gen> do <gen>") is a documented simplification.
        text = re.sub(
            rf"({num})\s*[–-]\s*({num})\s*({units})(?![\w])",  # noqa: RUF001
            lambda m: (
                f"{self.number(m.group(1))} {self.RANGE_WORD} "
                f"{self.unit(m.group(2), m.group(3))}"
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

    def spell_acronyms(self, text: str) -> str:
        """Read every known acronym (``ACRONYMS``) in free text letter-by-letter, so a
        TTS engine says "er em es" instead of mangling "RMS" into a word. Matched as a
        whole token and CASE-SENSITIVELY, so it never touches a lowercase word (English
        "din"), a longer word ("isolation" contains "iso"), or an unknown all-caps name
        (a customer code) — only the exact, known acronyms. Longest matched first so a
        shorter acronym can't partially consume a longer one.
        """
        if not text or not self.ACRONYMS:
            return text
        alternation = "|".join(
            re.escape(a) for a in sorted(self.ACRONYMS, key=len, reverse=True)
        )
        return re.sub(rf"\b({alternation})\b", lambda m: self.spell(m.group(1)), text)

    def datetime_text(self, text: str) -> str:
        """Verbalize ISO dates and date-times in free text, so a TTS engine reads them
        naturally instead of the model guessing at the digits (on a combined timestamp it
        mixes the day into the minutes). No-op unless the language sets VERBALIZES_DATETIME.
        Date-times are matched before bare dates; a trailing "Z"/"UTC" is normalized to a
        spoken " UTC" for the acronym pass to spell. A date-shaped but INVALID token
        (e.g. "2026-13-45", "25:99") is left untouched — these passes are safe over any text.
        """
        if not text or not self.VERBALIZES_DATETIME:
            return text

        def _datetime(m: re.Match[str]) -> str:
            try:
                spoken_date = self.date(m.group(1), with_weekday=False)
                spoken_time = self.time(int(m.group(2)), int(m.group(3)))
            except (ValueError, KeyError):
                return m.group(0)  # not a real date/time — leave the token alone
            suffix = " UTC" if m.group(4) else ""  # normalize Z/UTC -> spellable " UTC"
            return f"{spoken_date}, {spoken_time}{suffix}"

        def _bare_date(m: re.Match[str]) -> str:
            try:
                return self.date(m.group(1))
            except (ValueError, KeyError):
                return m.group(0)

        text = re.sub(
            r"\b(\d{4}-\d{2}-\d{2})[ T](\d{2}):(\d{2})(?::\d{2})?( ?UTC| ?Z)?\b",
            _datetime,
            text,
        )
        # A date FOLLOWED BY a clock time is the date-time pass's job — the lookahead
        # keeps this bare-date pass from re-grabbing the date half of a date-time whose
        # time was invalid (so "2026-07-01 25:99" stays wholly untouched, not split).
        return re.sub(r"\b(\d{4}-\d{2}-\d{2})\b(?![ T]\d{2}:\d{2})", _bare_date, text)
