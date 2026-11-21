"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

A voice as the platform takes it in every voice field: one ``engine.voice:model``
string, or a list of them, the first speaking and the rest its fallbacks, tried
in order when it fails.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

MAX_VOICES = 8
"""The most voices a voice field takes: the one that speaks and its fallbacks."""


def _voice_chain(value: Any, what: str = "voice") -> str | list[str]:
    """
    A voice field's value, checked: a non-empty string, or a list of 1 to 8
    non-empty strings (a one-item list is kept as a list).

    Raises:
        ValueError: For an empty voice, an empty list, more than 8, or a
            non-string entry.
    """
    if isinstance(value, str):
        if not value.strip():
            raise ValueError(f"{what} must be a non-empty string, or a list of them")
        return value
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        voices = list(value)
        if not voices:
            raise ValueError(f"{what} must name at least one voice")
        if len(voices) > MAX_VOICES:
            raise ValueError(
                f"{what} takes at most {MAX_VOICES} voices, the first speaking and the rest its fallbacks; "
                f"got {len(voices)}"
            )
        for v in voices:
            if not isinstance(v, str) or not v.strip():
                raise ValueError(
                    f"each of {what}'s voices must be a non-empty string, got {v!r}"
                )
        return voices
    raise ValueError(
        f"{what} must be a string, or a list of up to {MAX_VOICES} strings"
    )


def _voices_by_language(
    value: Any, what: str = "default_voice"
) -> str | list[str] | dict[str, Any]:
    """
    A voice, a list of them, or a mapping of language codes (with a
    ``"default"`` entry for the rest) to either.
    """
    if isinstance(value, Mapping):
        if not value:
            raise ValueError(f"{what} by language needs at least one language")
        out: dict[str, Any] = {}
        for code, voices in value.items():
            if not isinstance(code, str) or not code.strip():
                raise ValueError(
                    f"{what}'s languages must be codes such as 'es-MX' or 'default', got {code!r}"
                )
            out[code] = _voice_chain(voices, f"{what}[{code!r}]")
        return out
    return _voice_chain(value, what)


__all__: list[str] = []
