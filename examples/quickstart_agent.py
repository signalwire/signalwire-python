#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

# Quickstart: a minimal AI agent.
#
# This is the canonical README quickstart, kept as a real, gate-compiled example so
# the README code block can be included from it byte-for-byte (README-INCLUDE gate).

# region: agent
from signalwire import AgentBase
from signalwire.core.function_result import FunctionResult

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent", route="/agent")

        self.add_language(name="English", code="en-US", voice="inworld.Mark")
        self.prompt_add_section("Role", body="You are a helpful assistant.")

    @AgentBase.tool(name="get_time")
    def get_time(self):
        """Get the current time"""
        from datetime import datetime
        return FunctionResult(f"The time is {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    agent = MyAgent()
    agent.run()
# endregion: agent
