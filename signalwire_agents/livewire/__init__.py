"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
LiveWire -- LiveKit-compatible agents powered by SignalWire.

Developers familiar with livekit-agents can use the same class and function
names; just change the import path to run on SignalWire infrastructure.

    from signalwire_agents.livewire import Agent, AgentSession, function_tool
"""

import sys
import random
import inspect
import logging
import threading
import asyncio
import typing
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Sentinel for "not given" keyword arguments (distinct from None)
# ---------------------------------------------------------------------------

_NOT_GIVEN = object()
NOT_GIVEN = _NOT_GIVEN

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------

BANNER = r"""
    __    _            _       ___
   / /   (_)   _____  | |     / (_)_______
  / /   / / | / / _ \ | | /| / / / ___/ _ \
 / /___/ /| |/ /  __/ | |/ |/ / / /  /  __/
/_____/_/ |___/\___/  |__/|__/_/_/   \___/

 LiveKit-compatible agents powered by SignalWire
"""


def _print_banner():
    """Print the ASCII banner to stderr, using ANSI cyan if a terminal."""
    if sys.stderr.isatty():
        sys.stderr.write(f"\033[36m{BANNER}\033[0m\n")
    else:
        sys.stderr.write(f"{BANNER}\n")


# ---------------------------------------------------------------------------
# "Did You Know?" Tips  (same 10 tips as the Go module)
# ---------------------------------------------------------------------------

TIPS = [
    "SignalWire agents support DataMap tools that execute server-side "
    "-- no webhook infrastructure needed. See: docs/datamap_guide.md",

    "SignalWire Contexts & Steps give you mechanical state control over "
    "conversations -- no prompt engineering needed. See: docs/contexts_guide.md",

    "SignalWire agents can transfer calls between agents with a single "
    "SwmlTransfer() action",

    "SignalWire handles 18 built-in skills (datetime, math, web search, etc.) "
    "with one-liner integration via agent.AddSkill()",

    "SignalWire agents support SMS, conferencing, call recording, and SIP "
    "-- all from the same agent",

    "Your agent's entire AI pipeline (STT, LLM, TTS, VAD) runs in "
    "SignalWire's cloud -- zero infrastructure to manage",

    "SignalWire prefab agents (Survey, Receptionist, FAQ, Concierge) give "
    "you production patterns in 10 lines of code",

    "SignalWire's RELAY client gives you real-time WebSocket call control "
    "with 57+ methods -- play, record, detect, conference, and more",

    "SignalWire agents auto-generate SWML documents -- the platform handles "
    "media, turn detection, and barge-in for you",

    "You can host multiple agents on one server with AgentServer -- each "
    "with its own route, prompt, and tools",
]


def _print_tip():
    """Print a random 'Did you know?' tip to stderr."""
    tip = random.choice(TIPS)
    sys.stderr.write(f"\n\U0001f4a1 Did you know?  {tip}\n\n")


# ---------------------------------------------------------------------------
# Noop logging helpers
# ---------------------------------------------------------------------------

_logger = logging.getLogger("LiveWire")


class _NoopTracker:
    """Ensures each noop message is printed at most once."""

    def __init__(self):
        self._lock = threading.Lock()
        self._logged: Dict[str, bool] = {}

    def once(self, key: str, message: str) -> bool:
        """Log *message* once for *key*.  Returns True if it was logged."""
        with self._lock:
            if self._logged.get(key):
                return False
            self._logged[key] = True
            _logger.info("[LiveWire] %s", message)
            return True

    def was_logged(self, key: str) -> bool:
        with self._lock:
            return self._logged.get(key, False)

    def reset(self):
        with self._lock:
            self._logged.clear()


_global_noop = _NoopTracker()


# ---------------------------------------------------------------------------
# StopResponse / ToolError / AgentHandoff
# ---------------------------------------------------------------------------

class StopResponse(Exception):
    """Signals that a tool should not trigger another LLM reply."""
    pass


class ToolError(Exception):
    """Signals a tool execution error."""
    pass


class AgentHandoff:
    """Signals a handoff to another agent in multi-agent scenarios."""

    def __init__(self, agent, *, returns=None):
        self.agent = agent
        self.returns = returns


# ---------------------------------------------------------------------------
# ChatContext (minimal stub)
# ---------------------------------------------------------------------------

class ChatContext:
    """Minimal stub mirroring livekit ChatContext."""

    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def append(self, *, role: str = "user", text: str = ""):
        self.messages.append({"role": role, "content": text})
        return self


# ---------------------------------------------------------------------------
# function_tool decorator
# ---------------------------------------------------------------------------

def function_tool(func=None, *, name: Optional[str] = None, description: Optional[str] = None):
    """Mirrors the livekit ``@function_tool`` decorator.

    Wraps a plain function so it can be passed into ``Agent(tools=[...])``.
    Parameters are extracted from type-hints; the docstring is used as the
    description when *description* is not provided explicitly.
    """

    def _wrap(fn: Callable) -> Callable:
        tool_name = name or fn.__name__
        tool_desc = description or (inspect.getdoc(fn) or "")

        # Build a JSON-schema-style parameter dict from type hints
        sig = inspect.signature(fn)
        properties: Dict[str, Any] = {}
        required: List[str] = []

        for pname, param in sig.parameters.items():
            # Skip 'self' and RunContext parameters
            if pname == "self":
                continue
            anno = param.annotation
            if anno is not inspect.Parameter.empty and _is_run_context(anno):
                continue

            ptype = "string"
            if anno is not inspect.Parameter.empty:
                ptype = _python_type_to_json(anno)

            properties[pname] = {"type": ptype, "description": pname}
            if param.default is inspect.Parameter.empty:
                required.append(pname)

        schema = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required

        # Attach metadata to the function
        fn._livewire_tool = True
        fn._tool_name = tool_name
        fn._tool_description = tool_desc
        fn._tool_parameters = schema
        fn._tool_handler = fn
        return fn

    if func is not None:
        # Used as @function_tool (without arguments)
        return _wrap(func)
    # Used as @function_tool(name=..., description=...)
    return _wrap


def _is_run_context(annotation) -> bool:
    """Return True if *annotation* looks like a RunContext type."""
    if annotation is RunContext:
        return True
    name = getattr(annotation, "__name__", "") or str(annotation)
    return "RunContext" in name


def _python_type_to_json(annotation) -> str:
    """Map a Python type annotation to a JSON-Schema type string."""
    mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
    }
    return mapping.get(annotation, "string")


# ---------------------------------------------------------------------------
# RunContext
# ---------------------------------------------------------------------------

class RunContext:
    """Mirrors livekit RunContext -- available inside tool handlers."""

    def __init__(self, session=None, *, speech_handle=None, function_call=None):
        self.session = session
        self.speech_handle = speech_handle
        self.function_call = function_call

    @property
    def userdata(self):
        if self.session is not None:
            return self.session.userdata
        return {}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class Agent:
    """Mirrors a livekit Agent -- holds instructions and tool definitions."""

    def __init__(
        self,
        *,
        instructions: str = "",
        tools: Optional[List[Any]] = None,
        chat_ctx: Any = NOT_GIVEN,
        stt: Any = NOT_GIVEN,
        tts: Any = NOT_GIVEN,
        llm: Any = NOT_GIVEN,
        vad: Any = NOT_GIVEN,
        turn_detection: Any = NOT_GIVEN,
        mcp_servers: Any = NOT_GIVEN,
        allow_interruptions: Any = NOT_GIVEN,
        min_endpointing_delay: Any = NOT_GIVEN,
        max_endpointing_delay: Any = NOT_GIVEN,
    ):
        self.instructions = instructions
        self._tools: List[Any] = list(tools or [])
        self._chat_ctx = chat_ctx
        self._session: Optional["AgentSession"] = None
        self._userdata: Any = {}

        # Pipeline config (noop when not NOT_GIVEN)
        if stt is not NOT_GIVEN:
            _global_noop.once(
                "agent_stt",
                "Agent(stt=...): SignalWire's control plane handles speech "
                "recognition at scale -- no configuration needed",
            )
        if tts is not NOT_GIVEN:
            _global_noop.once(
                "agent_tts",
                "Agent(tts=...): SignalWire's control plane handles "
                "text-to-speech at scale -- no configuration needed",
            )
        if vad is not NOT_GIVEN:
            _global_noop.once(
                "agent_vad",
                "Agent(vad=...): SignalWire's control plane handles voice "
                "activity detection at scale automatically",
            )
        if turn_detection is not NOT_GIVEN:
            _global_noop.once(
                "agent_turn_detection",
                "Agent(turn_detection=...): SignalWire's control plane "
                "handles turn detection at scale automatically",
            )
        if mcp_servers is not NOT_GIVEN:
            _global_noop.once(
                "agent_mcp_servers",
                "Agent(mcp_servers=...): MCP servers are not yet supported "
                "in LiveWire -- tools should be registered via function_tool",
            )

        # Store pipeline hints for later mapping
        self._llm_hint = llm
        self._allow_interruptions = allow_interruptions
        self._min_endpointing_delay = min_endpointing_delay
        self._max_endpointing_delay = max_endpointing_delay

    @property
    def session(self) -> Optional["AgentSession"]:
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    # ------------------------------------------------------------------
    # Lifecycle hooks (override in subclass)
    # ------------------------------------------------------------------

    async def on_enter(self):
        """Called when the agent enters.  Override in subclass."""
        pass

    async def on_exit(self):
        """Called when the agent exits.  Override in subclass."""
        pass

    async def on_user_turn_completed(self, turn_ctx=None, new_message=None):
        """Called when the user finishes speaking.  Override in subclass."""
        pass

    # ------------------------------------------------------------------
    # Pipeline nodes -- all noop + log
    # ------------------------------------------------------------------

    async def stt_node(self, audio=None, model_settings=None):
        """Noop -- SignalWire handles STT in its control plane."""
        _global_noop.once(
            "stt_node",
            "Agent.stt_node(): SignalWire's control plane handles speech "
            "recognition -- this node is a no-op",
        )

    async def llm_node(self, chat_ctx=None, tools=None, model_settings=None):
        """Noop -- SignalWire handles LLM in its control plane."""
        _global_noop.once(
            "llm_node",
            "Agent.llm_node(): SignalWire's control plane handles LLM "
            "inference -- this node is a no-op",
        )

    async def tts_node(self, text=None, model_settings=None):
        """Noop -- SignalWire handles TTS in its control plane."""
        _global_noop.once(
            "tts_node",
            "Agent.tts_node(): SignalWire's control plane handles "
            "text-to-speech -- this node is a no-op",
        )

    # ------------------------------------------------------------------
    # Dynamic updates
    # ------------------------------------------------------------------

    async def update_instructions(self, instructions: str):
        """Update the agent's instructions mid-session."""
        self.instructions = instructions

    async def update_tools(self, tools: List[Any]):
        """Update the agent's tool list mid-session."""
        self._tools = list(tools)


# ---------------------------------------------------------------------------
# AgentSession
# ---------------------------------------------------------------------------

class AgentSession:
    """Mirrors a livekit AgentSession -- orchestrator that binds an Agent
    to the SignalWire platform."""

    def __init__(
        self,
        *,
        stt: Any = None,
        tts: Any = None,
        llm: Any = None,
        vad: Any = None,
        turn_detection: Any = None,
        tools: Optional[List[Any]] = None,
        mcp_servers: Any = None,
        userdata: Any = None,
        allow_interruptions: bool = True,
        min_interruption_duration: float = 0.5,
        min_endpointing_delay: float = 0.5,
        max_endpointing_delay: float = 3.0,
        max_tool_steps: int = 3,
        preemptive_generation: bool = False,
    ):
        # Noop pipeline stubs
        if stt is not None:
            _global_noop.once(
                "stt",
                f"AgentSession(stt=...): SignalWire's control plane handles "
                f"speech recognition at scale -- no configuration needed",
            )
        if tts is not None:
            _global_noop.once(
                "tts",
                f"AgentSession(tts=...): SignalWire's control plane handles "
                f"text-to-speech at scale -- no configuration needed",
            )
        if vad is not None:
            _global_noop.once(
                "vad",
                "AgentSession(vad=...): SignalWire's control plane handles "
                "voice activity detection at scale automatically",
            )
        if turn_detection is not None:
            _global_noop.once(
                "turn_detection",
                f"AgentSession(turn_detection=...): SignalWire's control "
                f"plane handles turn detection at scale automatically",
            )
        if mcp_servers is not None:
            _global_noop.once(
                "mcp_servers",
                "AgentSession(mcp_servers=...): MCP servers are not yet "
                "supported in LiveWire -- tools should be registered via "
                "function_tool",
            )

        self._llm = llm
        self._tools = list(tools or [])
        self._userdata = userdata if userdata is not None else {}
        self._allow_interruptions = allow_interruptions
        self._min_interruption_duration = min_interruption_duration
        self._min_endpointing_delay = min_endpointing_delay
        self._max_endpointing_delay = max_endpointing_delay
        self._max_tool_steps = max_tool_steps
        self._preemptive_generation = preemptive_generation

        if max_tool_steps != 3:
            _global_noop.once(
                "max_tool_steps",
                f"AgentSession(max_tool_steps={max_tool_steps}): SignalWire's "
                f"control plane handles tool execution depth at scale "
                f"automatically",
            )

        # Internal state
        self._agent: Optional[Agent] = None
        self._sw_agent = None  # Will hold the real AgentBase
        self._say_queue: List[str] = []
        self._history: List[Dict[str, str]] = []
        self._noop = _NoopTracker()
        self._started = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def userdata(self):
        return self._userdata

    @userdata.setter
    def userdata(self, val):
        self._userdata = val

    @property
    def history(self) -> List[Dict[str, str]]:
        return self._history

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self, agent: Agent, *, room=None, record: bool = False):
        """Bind to an Agent and prepare the underlying SignalWire AgentBase."""
        self._agent = agent
        agent.session = self
        self._started = True

    def say(self, text: str):
        """Queue text to be spoken by the agent."""
        self._say_queue.append(text)

    def generate_reply(self, *, instructions: Optional[str] = None):
        """Trigger the agent to generate a reply.  On SignalWire the prompt
        handles this; if *instructions* is provided they are noted."""
        if instructions:
            self._say_queue.append(instructions)

    def interrupt(self):
        """Noop -- SignalWire handles barge-in automatically."""
        self._noop.once(
            "interrupt",
            "AgentSession.interrupt(): SignalWire handles barge-in "
            "automatically via its control plane",
        )

    def update_agent(self, agent: Agent):
        """Swap in a new Agent."""
        self._agent = agent
        agent.session = self

    # ------------------------------------------------------------------
    # Build the real SignalWire agent (called by run_app)
    # ------------------------------------------------------------------

    def _build_sw_agent(self):
        """Translate the LiveWire session into a SignalWire AgentBase."""
        from signalwire_agents import AgentBase as _AgentBase

        agent = self._agent
        if agent is None:
            raise RuntimeError("No Agent bound to session -- call start() first")

        sw = _AgentBase(
            name="LiveWireAgent",
            route="/",
            schema_validation=False,
        )

        # Prompt
        sw.set_prompt_text(agent.instructions)

        # LLM model
        llm_model = self._llm or getattr(agent, "_llm_hint", NOT_GIVEN)
        if llm_model is not NOT_GIVEN and llm_model is not None:
            model_str = str(llm_model)
            # Strip provider prefix if present  e.g. "openai/gpt-4" -> "gpt-4"
            if "/" in model_str:
                model_str = model_str.split("/", 1)[1]
            sw.set_param("model", model_str)

        # Interruption / barge
        allow = self._allow_interruptions
        agent_allow = getattr(agent, "_allow_interruptions", NOT_GIVEN)
        if agent_allow is not NOT_GIVEN:
            allow = agent_allow
        if not allow:
            sw.set_param("barge_confidence", 1.0)

        # Endpointing delays
        min_ep = self._min_endpointing_delay
        agent_min = getattr(agent, "_min_endpointing_delay", NOT_GIVEN)
        if agent_min is not NOT_GIVEN:
            min_ep = agent_min
        if min_ep and min_ep > 0:
            sw.set_param("end_of_speech_timeout", int(min_ep * 1000))

        max_ep = self._max_endpointing_delay
        agent_max = getattr(agent, "_max_endpointing_delay", NOT_GIVEN)
        if agent_max is not NOT_GIVEN:
            max_ep = agent_max
        if max_ep and max_ep > 0:
            sw.set_param("attention_timeout", int(max_ep * 1000))

        # Initial greeting (say queue)
        for text in self._say_queue:
            sw.prompt_add_section("Initial Greeting", text)

        # Register tools
        all_tools = list(self._tools) + list(agent._tools)
        for t in all_tools:
            if callable(t) and getattr(t, "_livewire_tool", False):
                _register_function_tool(sw, t)

        self._sw_agent = sw
        return sw


def _register_function_tool(sw_agent, fn):
    """Register a @function_tool-decorated function on a SignalWire AgentBase."""
    tool_name = fn._tool_name
    tool_desc = fn._tool_description
    tool_params = fn._tool_parameters

    # Build a handler compatible with define_tool expectations
    def handler(args, raw_data=None):
        from signalwire_agents.core.function_result import SwaigFunctionResult

        sig = inspect.signature(fn)
        call_kwargs = {}
        for pname, param in sig.parameters.items():
            if pname == "self":
                continue
            anno = param.annotation
            if anno is not inspect.Parameter.empty and _is_run_context(anno):
                call_kwargs[pname] = RunContext(session=None)
                continue
            if pname in args:
                call_kwargs[pname] = args[pname]
            elif param.default is not inspect.Parameter.empty:
                call_kwargs[pname] = param.default

        result = fn(**call_kwargs)
        if isinstance(result, str):
            return SwaigFunctionResult(result)
        return SwaigFunctionResult(str(result))

    sw_agent.define_tool(
        name=tool_name,
        description=tool_desc,
        parameters=tool_params,
        handler=handler,
    )


# ---------------------------------------------------------------------------
# Room / JobProcess / JobContext
# ---------------------------------------------------------------------------

class Room:
    """Stub -- SignalWire doesn't use the LiveKit room abstraction."""
    name = "livewire-room"


class JobProcess:
    """Mirrors a livekit JobProcess -- used for prewarm/setup."""

    def __init__(self):
        self.userdata: Dict[str, Any] = {}


class JobContext:
    """Mirrors a livekit JobContext -- provides room and connection info."""

    def __init__(self):
        self.room = Room()
        self.proc = JobProcess()
        self._agent = None

    async def connect(self):
        """Noop -- SignalWire agents connect automatically when the platform
        invokes the SWML endpoint."""
        _global_noop.once(
            "connect",
            "JobContext.connect(): SignalWire's control plane handles "
            "connection lifecycle at scale automatically",
        )

    async def wait_for_participant(self, *, identity=None):
        """Noop -- SignalWire handles participant management automatically."""
        _global_noop.once(
            "wait_for_participant",
            "JobContext.wait_for_participant(): SignalWire's control plane "
            "handles participant management automatically",
        )


# ---------------------------------------------------------------------------
# AgentServer  (mirrors livekit cli.AgentServer / WorkerOptions)
# ---------------------------------------------------------------------------

class AgentServer:
    """Mirrors a livekit AgentServer -- registers entrypoints and starts."""

    def __init__(self, **kwargs):
        self.setup_fnc: Optional[Callable] = None
        self._entrypoint: Optional[Callable] = None
        self._agent_name: str = ""

    def rtc_session(
        self,
        func=None,
        *,
        agent_name: str = "",
        type: str = "room",
        on_request=None,
        on_session_end=None,
    ):
        """Decorator that registers the session entrypoint."""
        if type != "room":
            _global_noop.once(
                "server_type",
                f"AgentServer.rtc_session(type={type!r}): SignalWire's control "
                f"plane handles server topology at scale automatically",
            )

        def _decorator(fn):
            self._entrypoint = fn
            if agent_name:
                self._agent_name = agent_name
            return fn

        if func is not None:
            return _decorator(func)
        return _decorator


# ---------------------------------------------------------------------------
# Plugin stubs  (imported from plugins.py for cleanliness, re-exported here)
# ---------------------------------------------------------------------------

from signalwire_agents.livewire.plugins import (  # noqa: E402
    DeepgramSTT,
    OpenAILLM,
    CartesiaTTS,
    ElevenLabsTTS,
    SileroVAD,
)


# ---------------------------------------------------------------------------
# Inference stubs
# ---------------------------------------------------------------------------

class InferenceSTT:
    """Stub for livekit inference.STT."""

    def __init__(self, model: str = "", **kwargs):
        self.model = model
        _global_noop.once(
            "inference_stt",
            f"InferenceSTT({model!r}): SignalWire's control plane handles "
            f"speech recognition -- inference stubs are no-ops",
        )


class InferenceLLM:
    """Stub for livekit inference.LLM."""

    def __init__(self, model: str = "", **kwargs):
        self.model = model


class InferenceTTS:
    """Stub for livekit inference.TTS."""

    def __init__(self, model: str = "", **kwargs):
        self.model = model
        _global_noop.once(
            "inference_tts",
            f"InferenceTTS({model!r}): SignalWire's control plane handles "
            f"text-to-speech -- inference stubs are no-ops",
        )


# ---------------------------------------------------------------------------
# Namespace aliases matching livekit imports
#
#   from signalwire_agents.livewire import voice, llm_ns, cli_ns, inference
# ---------------------------------------------------------------------------

class _VoiceNamespace:
    Agent = Agent
    AgentSession = AgentSession


class _LLMNamespace:
    tool = staticmethod(function_tool)
    ToolError = ToolError
    ChatContext = ChatContext


class _InferenceNamespace:
    STT = InferenceSTT
    LLM = InferenceLLM
    TTS = InferenceTTS


voice = _VoiceNamespace()
llm_ns = _LLMNamespace()
inference = _InferenceNamespace()


# ---------------------------------------------------------------------------
# run_app
# ---------------------------------------------------------------------------

def run_app(server: AgentServer):
    """Print banner, print a random tip, run the agent.

    This is the main entry point -- mirrors ``livekit.agents.cli.run_app``.
    """
    _print_banner()

    # Run setup if registered
    if server.setup_fnc is not None:
        proc = JobProcess()
        server.setup_fnc(proc)

    # Create a JobContext
    ctx = JobContext()

    # Call the entrypoint -- should create session, agent, tools, etc.
    if server._entrypoint is not None:
        entry = server._entrypoint
        if asyncio.iscoroutinefunction(entry):
            asyncio.get_event_loop().run_until_complete(entry(ctx))
        else:
            entry(ctx)

    # Print a random tip right before starting
    _print_tip()

    # Start the underlying SignalWire agent
    if ctx._agent is not None:
        # The entrypoint set ctx._agent to an AgentBase -- run it
        ctx._agent.run()
    else:
        _logger.error(
            "no agent was started -- did you call session.start() and "
            "session._build_sw_agent()?"
        )


# Also provide a cli_ns namespace for ``from livewire import cli_ns``
class _CLINamespace:
    run_app = staticmethod(run_app)

cli_ns = _CLINamespace()


# ---------------------------------------------------------------------------
# __all__
# ---------------------------------------------------------------------------

__all__ = [
    # Core types
    "Agent",
    "AgentSession",
    "RunContext",
    "function_tool",
    "ChatContext",
    # Exceptions / signals
    "StopResponse",
    "ToolError",
    "AgentHandoff",
    # Infrastructure
    "AgentServer",
    "JobContext",
    "JobProcess",
    "Room",
    # Plugin stubs
    "DeepgramSTT",
    "OpenAILLM",
    "CartesiaTTS",
    "ElevenLabsTTS",
    "SileroVAD",
    # Inference stubs
    "InferenceSTT",
    "InferenceLLM",
    "InferenceTTS",
    # Namespaces
    "voice",
    "llm_ns",
    "cli_ns",
    "inference",
    # Entry point
    "run_app",
    # Sentinel
    "NOT_GIVEN",
    # Banner / tips (for testing)
    "BANNER",
    "TIPS",
]
