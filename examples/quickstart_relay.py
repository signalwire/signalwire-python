#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

# Quickstart: real-time call control over WebSocket with the RELAY client.
#
# This is the canonical README RELAY quickstart, kept as a real, gate-compiled example
# so the README code block can be included from it byte-for-byte (README-INCLUDE gate).

# region: relay
from signalwire.relay import RelayClient

client = RelayClient(
    project="...", token="...", host="example.signalwire.com", contexts=["default"]
)


@client.on_call
async def handle(call):
    await call.answer()
    action = await call.play([{"type": "tts", "params": {"text": "Welcome!"}}])
    await action.wait()
    await call.hangup()


client.run()
# endregion: relay
