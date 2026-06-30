"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Typed-input validation + request-payload helpers (product-agnostic).

A voice agent collects values the speech channel can't capture (email, phone,
number, ...) via a keypad: it emits an `input_request` event, the app types the
value back, and a validator decides accept-vs-re-prompt. These are the PURE
pieces — format validation and the request-payload shape — reusable by any
agent. The SDK-coupled bits (emitting the user_event, wait_for_user, the
re-prompt result) live in the agent. No third-party dependencies.
"""

from __future__ import annotations

import re

# Pragmatic, TTS/keypad-oriented email shape: a@b.c with no spaces. Deliberately
# permissive on the local part — we reject only what is clearly NOT an address
# (so a real-but-unusual address is never bounced); the human read-back catches
# a valid-format-but-wrong-person typo, which no regex can.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(value: str) -> bool:
    return bool(_EMAIL_RE.match((value or "").strip()))


def is_valid_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value or "")
    return 7 <= len(digits) <= 15


def is_valid_number(value: str) -> bool:
    try:
        float((value or "").strip().replace(",", "."))
        return True
    except ValueError:
        return False


_VALIDATORS = {
    "email": is_valid_email,
    "tel": is_valid_phone,
    "phone": is_valid_phone,
    "number": is_valid_number,
}


def validate_input(value: str, input_type: str) -> bool:
    """True if `value` is acceptable for `input_type`. Empty is never valid;
    an unknown input_type accepts any non-empty value (the agent still does the
    human read-back)."""
    v = (value or "").strip()
    if not v:
        return False
    fn = _VALIDATORS.get((input_type or "").lower())
    return fn(v) if fn else True


# The event-type string of the universal typed-input channel (agent emits it as
# an SWML user_event; app reveals + focuses the matching field).
INPUT_REQUEST_TYPE = "input_request"


def input_request_payload(
    field: str, label: str = "", input_type: str = "text"
) -> dict:
    """The payload an agent emits (as a user_event) to ask the app to reveal a
    typed-input field. `field` is the key the typed value comes back under."""
    return {
        "type": INPUT_REQUEST_TYPE,
        "field": field,
        "label": label,
        "input_type": input_type,
    }
