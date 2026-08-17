#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

# Quickstart: manage SignalWire resources over HTTP with the REST client.
#
# This is the canonical README REST quickstart, kept as a real, gate-compiled example
# so the README code block can be included from it byte-for-byte (README-INCLUDE gate).

call_id = "..."

# region: rest
from signalwire.rest import RestClient

client = RestClient(project="...", token="...", host="example.signalwire.com")

client.fabric.ai_agents.create(name="Support Bot", prompt={"text": "You are helpful."})
client.calling.play(call_id, play=[{"type": "tts", "params": {"text": "Hello!"}}])
client.phone_numbers.search(areacode="512")
client.datasphere.documents.search(query_string="billing policy")
# endregion: rest
