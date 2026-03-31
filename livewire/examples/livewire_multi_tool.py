#!/usr/bin/env python3
"""
LiveWire multi-tool agent example.

Demonstrates an agent with several tools, custom LLM model selection, and
endpointing configuration -- all using LiveKit-compatible API symbols.

Usage:
    python livewire_multi_tool.py
"""

from signalwire.livewire import (
    Agent,
    AgentSession,
    AgentServer,
    JobContext,
    RunContext,
    function_tool,
    run_app,
)


@function_tool
def get_weather(location: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {location} is 72 F and sunny."


@function_tool
def get_time(timezone: str) -> str:
    """Get the current time in a timezone."""
    return f"The current time in {timezone} is 3:45 PM."


@function_tool(name="search_web", description="Search the web for information")
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web."""
    return f"Found {max_results} results for '{query}'. Top result: Example article about {query}."


server = AgentServer()


@server.rtc_session(agent_name="multi-tool-agent")
async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions=(
            "You are a knowledgeable assistant with access to weather, "
            "time, and web search tools.  Use whichever tool is most "
            "appropriate for the user's question."
        ),
        tools=[get_weather, get_time, web_search],
    )

    session = AgentSession(
        llm="openai/gpt-4o",
        allow_interruptions=True,
        min_endpointing_delay=0.5,
        max_endpointing_delay=3.0,
    )
    await session.start(agent, room=ctx.room)
    session.generate_reply(
        instructions="Introduce yourself and explain the tools you have available."
    )


if __name__ == "__main__":
    run_app(server)
