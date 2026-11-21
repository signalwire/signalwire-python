"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Inject a message into a live call (e.g. speak on the voice leg from elsewhere).
"""

from __future__ import annotations

from typing import Any


def say_into_call(
    call_id: str,
    text: str,
    *,
    role: str = "assistant",
    client: Any = None,
) -> Any:
    """Speak (or inject) a message on a live call by its id.

    Defaults to the public SignalWire REST path
    (``RestClient().calling.ai_message``) with credentials from the usual
    environment variables; pass ``client`` to override — e.g. a client wired to
    different credentials. Nothing deployment-specific is baked in here.
    """
    if client is None:
        from signalwire import RestClient

        client = RestClient()
    return client.calling.ai_message(call_id, role=role, message_text=text)
