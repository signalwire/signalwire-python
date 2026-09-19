"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

English reference plugin.

English TTS reads digits, emails ("at"/"dot") and dates natively, so the neutral
base behaviour is already correct. This exists mainly as the fallback target and
a worked example of a minimal plugin — override here only if a real gap appears.
"""

from __future__ import annotations

from typing import ClassVar

from ..base import Verbalizer


class EnglishVerbalizer(Verbalizer):
    lang: ClassVar[str] = "en"
    # Base SEPARATORS are already English ("at"/"dot"); nothing to override yet.

    def guidance(self, glossary: dict[str, str] | None = None) -> str:
        # English is read natively by the LLM/TTS — no special guidance needed.
        # This is also the fallback for unregistered languages, so they get "" too.
        return ""
