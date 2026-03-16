# LiveWire -- LiveKit-compatible agents powered by SignalWire

LiveWire lets [LiveKit Python](https://docs.livekit.io/agents/) developers use their
familiar API symbols -- same class names, same function names -- but run on
SignalWire infrastructure.  Just change your import path.

## Quick start

```python
# Before (livekit-agents)
# from livekit.agents import Agent, AgentSession, function_tool, cli

# After (LiveWire -- runs on SignalWire)
from signalwire_agents.livewire import (
    Agent,
    AgentSession,
    AgentServer,
    JobContext,
    function_tool,
    run_app,
)

@function_tool
def get_weather(location: str) -> str:
    """Get the current weather for a city."""
    return f"It is sunny in {location}."

server = AgentServer()

@server.rtc_session(agent_name="weather-agent")
async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(instructions="You are a weather assistant.", tools=[get_weather])
    session = AgentSession()
    await session.start(agent, room=ctx.room)
    session.generate_reply(instructions="Greet the user and ask what city they need weather for.")

if __name__ == "__main__":
    run_app(server)
```

## What maps, what no-ops

| LiveKit concept | LiveWire behaviour |
|---|---|
| `Agent(instructions=...)` | Mapped to SignalWire prompt |
| `@function_tool` | Mapped to `define_tool()` on `AgentBase` |
| `AgentSession(llm=...)` | LLM model mapped to SignalWire AI params |
| `AgentSession(stt=...)` | No-op -- SignalWire handles STT |
| `AgentSession(tts=...)` | No-op -- SignalWire handles TTS |
| `AgentSession(vad=...)` | No-op -- SignalWire handles VAD |
| `session.say(text)` | Queued as initial greeting section |
| `session.interrupt()` | No-op -- SignalWire handles barge-in |
| `ctx.connect()` | No-op -- SignalWire auto-connects |
| Plugin classes (`DeepgramSTT`, etc.) | Constructable stubs, no-op |

## Examples

See the `examples/` directory:

- `livewire_basic_agent.py` -- minimal weather agent
- `livewire_multi_tool.py` -- agent with multiple tools
- `livewire_handoff.py` -- multi-agent handoff

## Migration guide

See `docs/migration-guide.md` for a step-by-step walkthrough of porting a
LiveKit agent to LiveWire.
