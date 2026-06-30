"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Language plugin registry + dispatch.

`get(lang)` returns the verbalizer for a language tag, falling back to English
and finally a language-neutral base instance, so callers never have to special-
case a missing plugin.
"""

from __future__ import annotations

from .base import Verbalizer

_REGISTRY: dict[str, Verbalizer] = {}
_DEFAULT = Verbalizer()


def register(verbalizer: Verbalizer) -> Verbalizer:
    """Register a language plugin under its `lang` code. Returns it (chainable)."""
    _REGISTRY[verbalizer.lang.lower()] = verbalizer
    return verbalizer


def get(lang: str | None) -> Verbalizer:
    """Resolve a verbalizer for a BCP-47 tag ('pl', 'pl-PL', 'de-DE', …).

    Falls back to the 'en' plugin, then a neutral passthrough base, so this
    never returns None and never raises on an unknown language.
    """
    code = (lang or "").replace("_", "-").split("-")[0].lower()
    return _REGISTRY.get(code) or _REGISTRY.get("en") or _DEFAULT


def available() -> list[str]:
    """The language codes currently registered."""
    return sorted(_REGISTRY)
