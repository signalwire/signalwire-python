"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for the LiveWire compatibility module.
"""

import io
import json
import sys
from collections.abc import Iterator
from typing import Any
import pytest
from unittest.mock import patch, Mock

from signalwire.livewire import (
    Agent,
    AgentSession,
    AgentServer,
    RunContext,
    JobContext,
    JobProcess,
    Room,
    ChatContext,
    StopResponse,
    ToolError,
    AgentHandoff,
    function_tool,
    NOT_GIVEN,
    BANNER,
    TIPS,
    run_app,
    voice,
    llm_ns,
    cli_ns,
    inference,
    _global_noop,
    _print_banner,
    _print_tip,
)
from signalwire.livewire.plugins import (
    DeepgramSTT,
    OpenAILLM,
    CartesiaTTS,
    ElevenLabsTTS,
    SileroVAD,
    _reset_logged,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_noop_trackers() -> Iterator[None]:
    """Reset all noop trackers between tests so 'log once' does not leak."""
    _global_noop.reset()
    _reset_logged()
    yield
    _global_noop.reset()
    _reset_logged()


# ---------------------------------------------------------------------------
# Agent creation
# ---------------------------------------------------------------------------

class TestAgentCreation:
    """Test Agent class construction and properties."""

    def test_basic_creation(self) -> None:
        agent = Agent(instructions="You are a helpful assistant.")
        assert agent.instructions == "You are a helpful assistant."
        assert agent._tools == []
        assert agent.session is None

    def test_creation_with_tools(self) -> None:
        @function_tool
        def greet(name: str) -> str:
            """Say hello."""
            return f"Hello, {name}!"

        agent = Agent(instructions="Greet people.", tools=[greet])
        assert len(agent._tools) == 1
        assert agent._tools[0]._tool_name == "greet"

    def test_creation_with_noop_params(self) -> None:
        """STT, TTS, VAD, turn_detection trigger noop logs."""
        agent = Agent(
            instructions="test",
            stt="deepgram",
            tts="cartesia",
            vad="silero",
            turn_detection="server",
        )
        assert _global_noop.was_logged("agent_stt")
        assert _global_noop.was_logged("agent_tts")
        assert _global_noop.was_logged("agent_vad")
        assert _global_noop.was_logged("agent_turn_detection")

    def test_creation_without_noop_params(self) -> None:
        """NOT_GIVEN params should NOT trigger noop logs."""
        Agent(instructions="test")
        assert not _global_noop.was_logged("agent_stt")
        assert not _global_noop.was_logged("agent_tts")

    def test_session_property(self) -> None:
        agent = Agent(instructions="test")
        session = AgentSession()
        agent.session = session
        assert agent.session is session


class TestAgentLifecycleHooks:
    """Test Agent lifecycle hooks (async)."""

    @pytest.mark.asyncio
    async def test_on_enter(self) -> None:
        """Default on_enter is a no-op — must return None and must not
        mutate the agent's instructions."""
        agent = Agent(instructions="test")
        result = await agent.on_enter()  # type: ignore[func-returns-value]  # asserting no-op returns None
        assert result is None
        # No-op contract: state unchanged.
        assert agent.instructions == "test"

    @pytest.mark.asyncio
    async def test_on_exit(self) -> None:
        """Default on_exit returns None and leaves instructions intact."""
        agent = Agent(instructions="test")
        result = await agent.on_exit()  # type: ignore[func-returns-value]  # asserting no-op returns None
        assert result is None
        assert agent.instructions == "test"

    @pytest.mark.asyncio
    async def test_on_user_turn_completed(self) -> None:
        """Default on_user_turn_completed returns None and accepts the
        optional turn_ctx/new_message kwargs without modifying state."""
        agent = Agent(instructions="test")
        result = await agent.on_user_turn_completed(  # type: ignore[func-returns-value]  # asserting no-op returns None
            turn_ctx={"role": "user"},
            new_message={"text": "hi"},
        )
        assert result is None
        assert agent.instructions == "test"

    @pytest.mark.asyncio
    async def test_update_instructions(self) -> None:
        agent = Agent(instructions="old")
        await agent.update_instructions("new")
        assert agent.instructions == "new"

    @pytest.mark.asyncio
    async def test_update_tools(self) -> None:
        agent = Agent(instructions="test")
        assert agent._tools == []
        await agent.update_tools(["tool1", "tool2"])
        assert agent._tools == ["tool1", "tool2"]


class TestAgentPipelineNodes:
    """Test pipeline node no-ops."""

    @pytest.mark.asyncio
    async def test_stt_node_noop(self) -> None:
        agent = Agent(instructions="test")
        await agent.stt_node()
        assert _global_noop.was_logged("stt_node")

    @pytest.mark.asyncio
    async def test_llm_node_noop(self) -> None:
        agent = Agent(instructions="test")
        await agent.llm_node()
        assert _global_noop.was_logged("llm_node")

    @pytest.mark.asyncio
    async def test_tts_node_noop(self) -> None:
        agent = Agent(instructions="test")
        await agent.tts_node()
        assert _global_noop.was_logged("tts_node")


# ---------------------------------------------------------------------------
# function_tool decorator
# ---------------------------------------------------------------------------

class TestFunctionTool:
    """Test the @function_tool decorator."""

    def test_basic_decorator_no_args(self) -> None:
        @function_tool
        def get_weather(location: str) -> str:
            """Get the weather for a location."""
            return f"Sunny in {location}"

        assert get_weather._livewire_tool is True  # type: ignore[attr-defined]  # dynamic tool attr
        assert get_weather._tool_name == "get_weather"  # type: ignore[attr-defined]  # dynamic tool attr
        assert get_weather._tool_description == "Get the weather for a location."  # type: ignore[attr-defined]  # dynamic tool attr
        props = get_weather._tool_parameters["properties"]  # type: ignore[attr-defined]  # dynamic tool attr
        assert "location" in props
        assert props["location"]["type"] == "string"
        assert get_weather._tool_parameters.get("required") == ["location"]  # type: ignore[attr-defined]  # dynamic tool attr

    def test_decorator_with_custom_name(self) -> None:
        @function_tool(name="my_tool", description="custom desc")
        def something(x: int) -> str:
            return str(x)

        assert something._tool_name == "my_tool"
        assert something._tool_description == "custom desc"

    def test_decorator_with_multiple_params(self) -> None:
        @function_tool
        def search(query: str, limit: int = 10) -> str:
            """Search for something."""
            return query

        params = search._tool_parameters  # type: ignore[attr-defined]  # dynamic tool attr
        assert "query" in params["properties"]
        assert "limit" in params["properties"]
        assert params["properties"]["limit"]["type"] == "integer"
        # 'limit' has a default, so only 'query' is required
        assert params.get("required") == ["query"]

    def test_decorator_preserves_callable(self) -> None:
        @function_tool
        def echo(text: str) -> str:
            return text

        assert echo("hello") == "hello"

    def test_decorator_skips_run_context_param(self) -> None:
        @function_tool
        def my_tool(ctx: RunContext, city: str) -> str:
            """Look up city info."""
            return city

        params = my_tool._tool_parameters  # type: ignore[attr-defined]  # dynamic tool attr
        assert "ctx" not in params["properties"]
        assert "city" in params["properties"]

    def test_type_mapping(self) -> None:
        @function_tool
        def typed(a: str, b: int, c: float, d: bool) -> str:
            return "ok"

        props = typed._tool_parameters["properties"]  # type: ignore[attr-defined]  # dynamic tool attr
        assert props["a"]["type"] == "string"
        assert props["b"]["type"] == "integer"
        assert props["c"]["type"] == "number"
        assert props["d"]["type"] == "boolean"


# ---------------------------------------------------------------------------
# AgentSession
# ---------------------------------------------------------------------------

class TestAgentSession:
    """Test AgentSession construction and methods."""

    def test_basic_creation(self) -> None:
        session = AgentSession()
        assert session.userdata == {}
        assert session.history == []
        assert session._allow_interruptions is True

    def test_creation_with_userdata(self) -> None:
        session = AgentSession(userdata={"key": "value"})
        assert session.userdata == {"key": "value"}

    def test_userdata_setter(self) -> None:
        session = AgentSession()
        session.userdata = {"new": "data"}
        assert session.userdata == {"new": "data"}

    @pytest.mark.asyncio
    async def test_start(self) -> None:
        session = AgentSession()
        agent = Agent(instructions="test")
        await session.start(agent)
        assert session._agent is agent
        assert agent.session is session
        assert session._started is True

    def test_say(self) -> None:
        session = AgentSession()
        session.say("Hello!")
        session.say("How can I help?")
        assert session._say_queue == ["Hello!", "How can I help?"]

    def test_generate_reply(self) -> None:
        session = AgentSession()
        session.generate_reply(instructions="Greet the user")
        assert "Greet the user" in session._say_queue

    def test_interrupt_noop(self) -> None:
        session = AgentSession()
        session.interrupt()  # Should not raise
        assert session._noop.was_logged("interrupt")

    def test_update_agent(self) -> None:
        session = AgentSession()
        agent1 = Agent(instructions="first")
        agent2 = Agent(instructions="second")
        session.update_agent(agent1)
        assert session._agent is agent1
        session.update_agent(agent2)
        assert session._agent is agent2
        assert agent2.session is session

    def test_noop_stt(self) -> None:
        AgentSession(stt=DeepgramSTT())
        assert _global_noop.was_logged("stt")

    def test_noop_tts(self) -> None:
        AgentSession(tts=CartesiaTTS())
        assert _global_noop.was_logged("tts")

    def test_noop_vad(self) -> None:
        AgentSession(vad=SileroVAD.load())
        assert _global_noop.was_logged("vad")

    def test_noop_turn_detection(self) -> None:
        AgentSession(turn_detection="server")
        assert _global_noop.was_logged("turn_detection")

    def test_noop_max_tool_steps(self) -> None:
        AgentSession(max_tool_steps=10)
        assert _global_noop.was_logged("max_tool_steps")


# ---------------------------------------------------------------------------
# RunContext
# ---------------------------------------------------------------------------

class TestRunContext:
    """Test RunContext mirrors livekit RunContext."""

    def test_basic_creation(self) -> None:
        session = AgentSession(userdata={"foo": "bar"})
        ctx = RunContext(session)
        assert ctx.session is session
        assert ctx.userdata == {"foo": "bar"}

    def test_userdata_without_session(self) -> None:
        ctx = RunContext()
        assert ctx.userdata == {}

    def test_creation_with_extras(self) -> None:
        ctx = RunContext(None, speech_handle="sh", function_call="fc")
        assert ctx.speech_handle == "sh"
        assert ctx.function_call == "fc"


# ---------------------------------------------------------------------------
# JobContext
# ---------------------------------------------------------------------------

class TestJobContext:
    """Test JobContext noop methods."""

    @pytest.mark.asyncio
    async def test_connect_noop(self) -> None:
        ctx = JobContext()
        await ctx.connect()
        assert _global_noop.was_logged("connect")

    @pytest.mark.asyncio
    async def test_wait_for_participant_noop(self) -> None:
        ctx = JobContext()
        await ctx.wait_for_participant(identity="test-user")
        assert _global_noop.was_logged("wait_for_participant")

    def test_room_name(self) -> None:
        ctx = JobContext()
        assert ctx.room.name == "livewire-room"

    def test_proc(self) -> None:
        ctx = JobContext()
        assert isinstance(ctx.proc, JobProcess)
        assert ctx.proc.userdata == {}


# ---------------------------------------------------------------------------
# Room / JobProcess
# ---------------------------------------------------------------------------

class TestRoom:
    def test_name(self) -> None:
        assert Room.name == "livewire-room"


class TestJobProcess:
    def test_userdata(self) -> None:
        proc = JobProcess()
        proc.userdata["key"] = "val"
        assert proc.userdata == {"key": "val"}


# ---------------------------------------------------------------------------
# Plugin stubs
# ---------------------------------------------------------------------------

class TestPluginStubs:
    """Test that plugin stubs construct without error."""

    def test_deepgram_stt(self) -> None:
        stt = DeepgramSTT(model="nova-2")
        assert stt._kwargs == {"model": "nova-2"}

    def test_openai_llm(self) -> None:
        llm = OpenAILLM(model="gpt-4o")
        assert llm.model == "gpt-4o"

    def test_cartesia_tts(self) -> None:
        tts = CartesiaTTS(voice="default")
        assert tts._kwargs == {"voice": "default"}

    def test_elevenlabs_tts(self) -> None:
        tts = ElevenLabsTTS(voice_id="abc")
        assert tts._kwargs == {"voice_id": "abc"}

    def test_silero_vad(self) -> None:
        vad = SileroVAD()
        assert isinstance(vad, SileroVAD)

    def test_silero_vad_load(self) -> None:
        vad = SileroVAD.load()
        assert isinstance(vad, SileroVAD)


# ---------------------------------------------------------------------------
# Inference stubs
# ---------------------------------------------------------------------------

class TestInferenceStubs:
    def test_inference_stt(self) -> None:
        from signalwire.livewire import InferenceSTT
        stt = InferenceSTT("whisper-large-v3")
        assert stt.model == "whisper-large-v3"

    def test_inference_llm(self) -> None:
        from signalwire.livewire import InferenceLLM
        llm = InferenceLLM("gpt-4o")
        assert llm.model == "gpt-4o"

    def test_inference_tts(self) -> None:
        from signalwire.livewire import InferenceTTS
        tts = InferenceTTS("tts-1")
        assert tts.model == "tts-1"


# ---------------------------------------------------------------------------
# Noop logging (log once per feature)
# ---------------------------------------------------------------------------

class TestNoopLogging:
    """Verify that noop messages are logged at most once."""

    def test_log_once(self) -> None:
        first = _global_noop.once("test_key", "message")
        assert first is True
        second = _global_noop.once("test_key", "message again")
        assert second is False

    def test_was_logged(self) -> None:
        assert not _global_noop.was_logged("unique_key")
        _global_noop.once("unique_key", "msg")
        assert _global_noop.was_logged("unique_key")

    def test_reset(self) -> None:
        _global_noop.once("reset_key", "msg")
        assert _global_noop.was_logged("reset_key")
        _global_noop.reset()
        assert not _global_noop.was_logged("reset_key")

    def test_agent_stt_logs_once(self) -> None:
        Agent(instructions="a", stt="deepgram")
        assert _global_noop.was_logged("agent_stt")
        # Second construction should NOT log again (already logged)
        result = _global_noop.once("agent_stt", "again")
        assert result is False


# ---------------------------------------------------------------------------
# Banner and tips
# ---------------------------------------------------------------------------

class TestBannerAndTips:
    """Test banner printing and tip selection."""

    def test_banner_contains_livewire(self) -> None:
        assert "LiveKit-compatible agents powered by SignalWire" in BANNER

    def test_banner_contains_ascii_art(self) -> None:
        assert "LiveWire" in BANNER or "/ /___/ /" in BANNER

    def test_tips_count(self) -> None:
        assert len(TIPS) == 10

    def test_tips_are_strings(self) -> None:
        for tip in TIPS:
            assert isinstance(tip, str)
            assert len(tip) > 20

    def test_print_banner_tty(self) -> None:
        buf = io.StringIO()
        with patch.object(sys, "stderr", buf):
            with patch.object(buf, "isatty", return_value=True):
                _print_banner()
        output = buf.getvalue()
        assert "\033[36m" in output  # cyan
        assert "LiveKit-compatible" in output

    def test_print_banner_no_tty(self) -> None:
        buf = io.StringIO()
        with patch.object(sys, "stderr", buf):
            with patch.object(buf, "isatty", return_value=False):
                _print_banner()
        output = buf.getvalue()
        assert "\033[36m" not in output
        assert "LiveKit-compatible" in output

    def test_print_tip(self) -> None:
        buf = io.StringIO()
        with patch.object(sys, "stderr", buf):
            _print_tip()
        output = buf.getvalue()
        assert "Did you know?" in output


# ---------------------------------------------------------------------------
# Exceptions / signals
# ---------------------------------------------------------------------------

class TestExceptionsAndSignals:
    def test_stop_response_is_exception(self) -> None:
        assert issubclass(StopResponse, Exception)

    def test_tool_error_is_exception(self) -> None:
        assert issubclass(ToolError, Exception)

    def test_agent_handoff(self) -> None:
        agent = Agent(instructions="test")
        handoff = AgentHandoff(agent, returns="result")
        assert handoff.agent is agent
        assert handoff.returns == "result"


# ---------------------------------------------------------------------------
# ChatContext
# ---------------------------------------------------------------------------

class TestChatContext:
    def test_basic(self) -> None:
        ctx = ChatContext()
        assert ctx.messages == []

    def test_append(self) -> None:
        ctx = ChatContext()
        result = ctx.append(role="user", text="Hello")
        assert len(ctx.messages) == 1
        assert ctx.messages[0] == {"role": "user", "content": "Hello"}
        assert result is ctx  # chaining


# ---------------------------------------------------------------------------
# Namespace aliases
# ---------------------------------------------------------------------------

class TestNamespaces:
    def test_voice_namespace(self) -> None:
        assert voice.Agent is Agent
        assert voice.AgentSession is AgentSession

    def test_llm_namespace(self) -> None:
        assert llm_ns.tool is function_tool
        assert llm_ns.ToolError is ToolError
        assert llm_ns.ChatContext is ChatContext

    def test_cli_namespace(self) -> None:
        assert cli_ns.run_app is run_app

    def test_inference_namespace(self) -> None:
        from signalwire.livewire import InferenceSTT, InferenceLLM, InferenceTTS
        assert inference.STT is InferenceSTT
        assert inference.LLM is InferenceLLM
        assert inference.TTS is InferenceTTS


# ---------------------------------------------------------------------------
# AgentServer
# ---------------------------------------------------------------------------

class TestAgentServer:
    def test_basic_creation(self) -> None:
        server = AgentServer()
        assert server._entrypoint is None
        assert server.setup_fnc is None

    def test_rtc_session_decorator(self) -> None:
        server = AgentServer()

        @server.rtc_session(agent_name="test-agent")
        async def entrypoint(ctx: JobContext) -> None:
            pass

        assert server._entrypoint is entrypoint
        assert server._agent_name == "test-agent"

    def test_rtc_session_no_parens(self) -> None:
        """rtc_session can also be used as a decorator with func as first arg."""
        server = AgentServer()

        @server.rtc_session
        async def entrypoint(ctx: JobContext) -> None:
            pass

        assert server._entrypoint is entrypoint


# ---------------------------------------------------------------------------
# NOT_GIVEN sentinel
# ---------------------------------------------------------------------------

class TestNotGiven:
    def test_sentinel_identity(self) -> None:
        assert NOT_GIVEN is NOT_GIVEN
        assert NOT_GIVEN is not None
        assert NOT_GIVEN is not False
        assert NOT_GIVEN is not 0


# ---------------------------------------------------------------------------
# Integration: AgentSession._build_sw_agent
# ---------------------------------------------------------------------------

class TestBuildSwAgent:
    """Test that _build_sw_agent creates a valid SignalWire AgentBase."""

    @pytest.mark.asyncio
    async def test_build_basic(self) -> None:
        session = AgentSession()
        agent = Agent(instructions="You are a test agent.")
        await session.start(agent)

        with patch("signalwire.core.agent_base.uvicorn", Mock()):
            sw = session._build_sw_agent()

        assert sw is not None
        assert session._sw_agent is sw

    @pytest.mark.asyncio
    async def test_build_with_tools(self) -> None:
        @function_tool
        def ping(msg: str) -> str:
            """Ping back."""
            return f"pong: {msg}"

        session = AgentSession()
        agent = Agent(instructions="test", tools=[ping])
        await session.start(agent)

        with patch("signalwire.core.agent_base.uvicorn", Mock()):
            sw = session._build_sw_agent()

        # The tool should be registered
        tool_names = [f.name for f in sw._tool_registry._swaig_functions.values()
                      if hasattr(f, "name")]
        assert "ping" in tool_names

    @pytest.mark.asyncio
    async def test_build_raises_without_start(self) -> None:
        session = AgentSession()
        with pytest.raises(RuntimeError, match="No Agent bound"):
            session._build_sw_agent()


# ---------------------------------------------------------------------------
# run_app serves the agent of the session the entrypoint starts
# ---------------------------------------------------------------------------


def _ai_verb(sw: Any) -> dict[str, Any]:
    """The ai verb of the SWML document ``sw`` renders."""
    doc = json.loads(sw._render_swml())
    return next(verb["ai"] for verb in doc["sections"]["main"] if "ai" in verb)


class _Served:
    """Records the AgentBase instances run_app() runs, instead of serving."""

    def __init__(self) -> None:
        self.agents: list[Any] = []

    def __enter__(self) -> "_Served":
        from signalwire.core.agent_base import AgentBase

        def run(agent: Any, *args: Any, **kwargs: Any) -> None:
            self.agents.append(agent)

        self._patch = patch.object(AgentBase, "run", run)
        self._patch.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self._patch.stop()


class TestRunAppServes:
    def test_the_started_session_is_built_and_run(self) -> None:
        @function_tool
        def get_weather(location: str) -> str:
            """Get the weather."""
            return f"Sunny in {location}"

        server = AgentServer()

        @server.rtc_session(agent_name="weather")
        async def entrypoint(ctx: JobContext) -> None:
            await ctx.connect()
            session = AgentSession(llm="openai/gpt-4o")
            await session.start(
                Agent(instructions="You are a weather assistant.", tools=[get_weather]),
                room=ctx.room,
            )

        with _Served() as served, patch("sys.stderr", new_callable=io.StringIO):
            run_app(server)

        (sw,) = served.agents
        ai = _ai_verb(sw)
        assert ai["prompt"]["text"] == "You are a weather assistant."
        assert ai["params"]["model"] == "gpt-4o"
        assert [f["function"] for f in ai["SWAIG"]["functions"]] == ["get_weather"]

    def test_the_agent_is_built_after_the_entrypoint_returns(self) -> None:
        """So an update_agent() after start() still applies."""
        server = AgentServer()

        @server.rtc_session()
        async def entrypoint(ctx: JobContext) -> None:
            session = AgentSession()
            await session.start(Agent(instructions="first"))
            session.update_agent(Agent(instructions="second"))

        with _Served() as served, patch("sys.stderr", new_callable=io.StringIO):
            run_app(server)

        (sw,) = served.agents
        assert _ai_verb(sw)["prompt"]["text"] == "second"

    def test_the_last_session_started_is_served(self) -> None:
        server = AgentServer()

        @server.rtc_session()
        async def entrypoint(ctx: JobContext) -> None:
            await AgentSession().start(Agent(instructions="one"))
            await AgentSession().start(Agent(instructions="two"))

        with _Served() as served, patch("sys.stderr", new_callable=io.StringIO):
            run_app(server)

        (sw,) = served.agents
        assert _ai_verb(sw)["prompt"]["text"] == "two"

    def test_an_agent_the_entrypoint_sets_is_run_as_is(self) -> None:
        server = AgentServer()
        own = Mock()

        @server.rtc_session()
        def entrypoint(ctx: JobContext) -> None:
            ctx._agent = own

        with patch("sys.stderr", new_callable=io.StringIO):
            run_app(server)
        own.run.assert_called_once_with()

    def test_no_session_means_nothing_is_served(self) -> None:
        server = AgentServer()

        @server.rtc_session()
        async def entrypoint(ctx: JobContext) -> None:
            await ctx.connect()

        with _Served() as served, patch("sys.stderr", new_callable=io.StringIO), \
             patch("signalwire.livewire._logger") as logger:
            run_app(server)

        assert served.agents == []
        (message,) = logger.error.call_args.args
        assert "session.start(agent)" in message

    @pytest.mark.asyncio
    async def test_a_session_started_outside_run_app_belongs_to_no_job(self) -> None:
        from signalwire.livewire import _current_job

        session = AgentSession()
        await session.start(Agent(instructions="standalone"))
        assert _current_job.get() is None
        assert session._agent is not None


class TestLlmModel:
    """The model param comes from a model name or a plugin's ``model``,
    never from the plugin object's repr."""

    @pytest.mark.parametrize(
        ("llm", "model"),
        [
            ("openai/gpt-4o", "gpt-4o"),
            ("gpt-4o-mini", "gpt-4o-mini"),
            (OpenAILLM(model="gpt-4o"), "gpt-4o"),
            (inference.LLM(model="openai/gpt-4.1-mini"), "gpt-4.1-mini"),
        ],
    )
    @pytest.mark.asyncio
    async def test_session_llm(self, llm: Any, model: str) -> None:
        session = AgentSession(llm=llm)
        await session.start(Agent(instructions="x"))
        assert _ai_verb(session._build_sw_agent())["params"]["model"] == model

    @pytest.mark.asyncio
    async def test_agent_llm_hint(self) -> None:
        session = AgentSession()
        await session.start(Agent(instructions="x", llm=OpenAILLM(model="gpt-4o")))
        assert _ai_verb(session._build_sw_agent())["params"]["model"] == "gpt-4o"

    @pytest.mark.asyncio
    async def test_a_plugin_without_a_model_sets_none(self) -> None:
        session = AgentSession(llm=OpenAILLM())
        await session.start(Agent(instructions="x"))
        params = _ai_verb(session._build_sw_agent()).get("params", {})
        assert "model" not in params

    @pytest.mark.asyncio
    async def test_disallowing_interruptions_turns_barge_off(self) -> None:
        # barge_confidence isn't in the schema and the platform ignores it
        session = AgentSession(allow_interruptions=False)
        await session.start(Agent(instructions="x"))
        params = _ai_verb(session._build_sw_agent())["params"]
        assert params["enable_barge"] is False
        assert "barge_confidence" not in params
