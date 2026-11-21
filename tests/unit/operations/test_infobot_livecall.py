"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

say_into_call: inject a message into a live call through an overridable client.
"""

from __future__ import annotations


from signalwire.operations.infobot import say_into_call


def test_say_into_call_uses_injected_client() -> None:
    calls: list[tuple[str, str, str]] = []

    class FakeCalling:
        def ai_message(self, call_id: str, *, role: str, message_text: str) -> str:
            calls.append((call_id, role, message_text))
            return "ok"

    class FakeClient:
        calling = FakeCalling()

    assert say_into_call("c1", "hello", client=FakeClient()) == "ok"
    assert calls == [("c1", "assistant", "hello")]
