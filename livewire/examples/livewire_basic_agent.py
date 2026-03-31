#!/usr/bin/env python3
"""
LiveWire basic agent example.

This mirrors a typical LiveKit voice agent -- same class names, same
decorator -- but runs on SignalWire infrastructure.

Usage:
    python livewire_basic_agent.py
"""

from signalwire.livewire import (
    Agent,
    AgentSession,
    AgentServer,
    JobContext,
    function_tool,
    run_app,
    DeepgramSTT,
    CartesiaTTS,
    SileroVAD,
)


@function_tool
def get_weather(location: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {location} is 72 F and sunny."


server = AgentServer()


@server.rtc_session(agent_name="weather-agent")
async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions=(
            "You are a friendly weather assistant. "
            "Use the get_weather tool when the user asks about weather."
        ),
        tools=[get_weather],
    )

    session = AgentSession(
        stt=DeepgramSTT(),
        tts=CartesiaTTS(),
        vad=SileroVAD.load(),
    )
    await session.start(agent, room=ctx.room)
    session.generate_reply(
        instructions="Greet the user warmly and ask what city they want weather for."
    )


if __name__ == "__main__":
    run_app(server)
