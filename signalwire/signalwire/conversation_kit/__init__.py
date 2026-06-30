"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

conversation-kit — product-agnostic language utilities for voice agents.

Three layers a spoken-conversation agent needs, none tied to any particular product:

    from conversation_kit import compute_date, validate_input, verbalizer

    compute_date({"weekday": "saturday", "which": "next"}, date.today())  # spoken -> ISO date
    validate_input("a@b.com", "email")                                    # input checks
    verbalizer.get("pl").number("2.6")        # -> 'dwa przecinek sześć'  # value -> spoken

- ``dates``      : spoken-date math (resolve a day the caller named to a calendar date).
- ``inputs``     : input validation + the typed-input (on-screen keypad) channel payload.
- ``verbalizer`` : TTS-ready, per-language OUTPUT (numbers / units / dates / emails) plus
                   model-prompt ``guidance()``. Plugin registry — add a language by
                   subclassing ``verbalizer.Verbalizer`` and ``register()``-ing it.

Understand input -> compute -> speak output: the two halves of a voice turn's language
layer in one place. Zero dependencies; the agent layer wraps these into its
SignalWire SWAIG results and prompts.
"""

from __future__ import annotations

from . import verbalizer
from .dates import RESOLVE_DATE_PARAMS, WEEKDAYS, compute_date
from .inputs import (
    INPUT_REQUEST_TYPE,
    input_request_payload,
    is_valid_email,
    is_valid_number,
    is_valid_phone,
    validate_input,
)

__all__ = [
    "INPUT_REQUEST_TYPE",
    "RESOLVE_DATE_PARAMS",
    "WEEKDAYS",
    "compute_date",
    "input_request_payload",
    "is_valid_email",
    "is_valid_number",
    "is_valid_phone",
    "validate_input",
    "verbalizer",
]
