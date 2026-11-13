"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

AI events: what the platform reports during a call, as it happens.

With an agent's ``event_webhook_url`` set, the platform posts each AI event
it fires, such as ``ai.speech_detect`` for each final of what the caller
said, to that URL, as ``{"event_type", "timestamp", "project_id",
"space_id", "params": {..., "call_id"}}``. ``AgentBase.on_ai_event()`` and
``AgentBase.record_speech_finals()`` set the URL to the agent's own
``/ai_events`` endpoint.

``ai.speech_detect`` carries the final's ``text`` and, from the recognizer,
its ``words``: ``[{"word", "confidence"}]``, as heard, before hearing hints
and number formatting change the text. A call with ``redact_prompt`` set
doesn't send it unless debug is on.
"""

from __future__ import annotations

import threading
from collections import OrderedDict, deque
from typing import Any

#: The event a final of the caller's speech fires
SPEECH_DETECT = "ai.speech_detect"


class SpeechLog:
    """
    The recognizer's finals for each call, newest calls kept.

    Keeps up to ``max_finals`` finals for each of up to ``max_calls`` calls,
    dropping the oldest call's when a new call comes in. Each final is
    ``{"text", "words", "timestamp"}``, ``timestamp`` in seconds since the
    epoch, as the event was sent.
    """

    def __init__(self, max_calls: int = 500, max_finals: int = 200) -> None:
        self.max_calls = max_calls
        self.max_finals = max_finals
        self._lock = threading.Lock()
        self._calls: OrderedDict[str, deque[dict[str, Any]]] = OrderedDict()

    def add(self, event: dict[str, Any]) -> None:
        """Keep the final an ``ai.speech_detect`` event carries."""
        params = event.get("params")
        if not isinstance(params, dict):
            return
        call_id = params.get("call_id")
        text = params.get("text")
        if not isinstance(call_id, str) or not isinstance(text, str):
            return
        words = params.get("words")
        final = {
            "text": text,
            "words": [dict(w) for w in words if isinstance(w, dict)]
            if isinstance(words, list)
            else [],
            "timestamp": event.get("timestamp"),
        }
        with self._lock:
            finals = self._calls.get(call_id)
            if finals is None:
                finals = deque(maxlen=self.max_finals)
                self._calls[call_id] = finals
                while len(self._calls) > self.max_calls:
                    self._calls.popitem(last=False)
            else:
                self._calls.move_to_end(call_id)
            finals.append(final)

    def finals(self, call_id: str, since: float | None = None) -> list[dict[str, Any]]:
        """A call's finals, oldest first, from ``since`` (seconds since the
        epoch) on when it's given."""
        with self._lock:
            kept = list(self._calls.get(call_id, ()))
        if since is not None:
            kept = [
                f
                for f in kept
                if isinstance(f["timestamp"], (int, float)) and f["timestamp"] >= since
            ]
        return [{**f, "words": [dict(w) for w in f["words"]]} for f in kept]

    def forget(self, call_id: str) -> None:
        """Drop a call's finals."""
        with self._lock:
            self._calls.pop(call_id, None)
