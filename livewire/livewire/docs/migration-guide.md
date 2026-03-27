# Migrating from LiveKit Agents to LiveWire

This guide walks through porting a LiveKit Python agent to LiveWire so it
runs on SignalWire infrastructure.

## Step 1: Change your imports

```python
# Before
from livekit.agents import Agent, AgentSession, cli
from livekit.agents import function_tool
from livekit.plugins import deepgram, openai, cartesia, silero

# After
from signalwire.livewire import (
    Agent,
    AgentSession,
    AgentServer,
    JobContext,
    function_tool,
    run_app,
    DeepgramSTT,
    OpenAILLM,
    CartesiaTTS,
    SileroVAD,
)
```

## Step 2: Keep your tools exactly the same

The `@function_tool` decorator works identically.  Parameter type-hints are
extracted automatically and mapped to SignalWire's SWAIG function schema.

```python
@function_tool
def get_weather(location: str) -> str:
    """Get the current weather for a city."""
    return f"Sunny in {location}."
```

## Step 3: Keep your Agent + AgentSession pattern

```python
agent = Agent(
    instructions="You are a helpful weather assistant.",
    tools=[get_weather],
)

session = AgentSession(
    llm="openai/gpt-4o",          # mapped to SignalWire AI param
    stt=DeepgramSTT(),             # no-op (SignalWire handles STT)
    tts=CartesiaTTS(),             # no-op (SignalWire handles TTS)
    vad=SileroVAD.load(),          # no-op (SignalWire handles VAD)
    allow_interruptions=True,       # mapped to barge config
    min_endpointing_delay=0.5,      # mapped to end_of_speech_timeout
)
```

## Step 4: Replace cli.run_app with LiveWire's run_app

```python
# Before
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

# After
server = AgentServer()

@server.rtc_session(agent_name="my-agent")
async def entrypoint(ctx: JobContext):
    await ctx.connect()
    agent = Agent(instructions="...", tools=[get_weather])
    session = AgentSession()
    await session.start(agent, room=ctx.room)

if __name__ == "__main__":
    run_app(server)
```

## What's different under the hood

- **STT, TTS, VAD**: SignalWire's control plane handles all media processing.
  Plugin classes like `DeepgramSTT`, `CartesiaTTS`, and `SileroVAD` still
  construct so your code runs unchanged, but they are no-ops.

- **LLM model**: The model string (e.g. `"openai/gpt-4o"`) is mapped to
  SignalWire's AI engine parameter.  The provider prefix is stripped
  automatically.

- **Rooms**: SignalWire does not use the LiveKit room abstraction.
  `ctx.connect()` and `ctx.wait_for_participant()` are safe no-ops.

- **Barge-in / interruptions**: `session.interrupt()` is a no-op because
  SignalWire handles barge-in automatically.  `allow_interruptions=False`
  maps to `barge_confidence=1.0`.

- **Endpointing delays**: `min_endpointing_delay` maps to
  `end_of_speech_timeout`; `max_endpointing_delay` maps to
  `attention_timeout`.

## "Did You Know?" tips

When you run a LiveWire agent, you will see a random tip about SignalWire
features that go beyond what LiveKit offers -- DataMap tools, Contexts & Steps,
built-in skills, and more.
