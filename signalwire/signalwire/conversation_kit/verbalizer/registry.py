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
# The neutral, language-agnostic base. Returned by get() for any UNregistered
# language (e.g. "de" with no plugin), so unknown languages keep the base's generic
# guidance() and safe passthrough output instead of inheriting English's opt-outs.
_DEFAULT = Verbalizer()


def register(verbalizer: Verbalizer) -> Verbalizer:
    """Register a language plugin under its `lang` code. Returns it (chainable)."""
    _REGISTRY[verbalizer.lang.lower()] = verbalizer
    return verbalizer


def get(lang: str | None) -> Verbalizer:
    """Resolve a verbalizer for a BCP-47 tag ('pl', 'pl-PL', 'de-DE', …).

    Falls back to the neutral base ``Verbalizer`` for an unregistered language — NOT
    to English. The base keeps the generic ``guidance()`` a real language still needs;
    English is a specific plugin that deliberately opts out of guidance. Never returns
    None, never raises on an unknown language.
    """
    code = (lang or "").replace("_", "-").split("-")[0].lower()
    return _REGISTRY.get(code) or _DEFAULT


def available() -> list[str]:
    """The language codes currently registered. (Registration is import-time, so no
    concurrent-mutation guard is needed; sorted() already returns a fresh list.)"""
    return sorted(_REGISTRY)
