"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

LiveWire -- LiveKit-compatible agents powered by SignalWire.

Developers familiar with livekit-agents can use the same class and function
names; just change the import path to run on SignalWire infrastructure.

    from signalwire.livewire import Agent, AgentSession, function_tool
"""

import sys
import random
import inspect
import logging
import threading
import asyncio
import contextvars
from typing import Any, Optional, TYPE_CHECKING
from collections.abc import Callable

if TYPE_CHECKING:
    from signalwire.core.function_result import FunctionResult

# ---------------------------------------------------------------------------
# Sentinel for "not given" keyword arguments (distinct from None)
# ---------------------------------------------------------------------------

_NOT_GIVEN = object()
NOT_GIVEN = _NOT_GIVEN

# The JobContext whose entrypoint run_app() is running, so that
# AgentSession.start() can hand its session to the job without the
# entrypoint passing the context along.
_current_job: contextvars.ContextVar[Optional["JobContext"]] = contextvars.ContextVar(
    "livewire_current_job", default=None
)


def _model_name(llm: Any) -> str | None:
    """The model name an ``llm`` option names, or None.

    A string is the model name itself. A plugin object, such as
    ``OpenAILLM(model="gpt-4o")`` or ``inference.LLM(model=...)``, carries it
    in its ``model`` attribute; one without a model names none.
    """
    if llm is NOT_GIVEN or llm is None:
        return None
    model = llm if isinstance(llm, str) else getattr(llm, "model", None)
    if not isinstance(model, str) or not model:
        return None
    return model


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


def _print_banner() -> None:
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
    "SignalWire handles built-in skills (datetime, math, web search, etc.) "
    "with one-liner integration via agent.add_skill()",
    "SignalWire agents support SMS, conferencing, call recording, and SIP "
    "-- all from the same agent",
    "Your agent's entire AI pipeline (STT, LLM, TTS, VAD) runs in "
    "SignalWire's cloud -- zero infrastructure to manage",
    "SignalWire prefab agents (Survey, Receptionist, FAQ, Concierge) give "
    "you production patterns in 10 lines of code",
    "SignalWire's RELAY client gives you real-time WebSocket call control "
    "with methods to play, record, detect, conference, and more",
    "SignalWire agents auto-generate SWML documents -- the platform handles "
    "media, turn detection, and barge-in for you",
    "You can host multiple agents on one server with AgentServer -- each "
    "with its own route, prompt, and tools",
]


def _print_tip() -> None:
    """Print a random 'Did you know?' tip to stderr."""
    tip = random.choice(TIPS)  # noqa: S311  # not cryptographic: picks a cosmetic "Did you know?" CLI tip to print
    sys.stderr.write(f"\n\U0001f4a1 Did you know?  {tip}\n\n")


# ---------------------------------------------------------------------------
# Noop logging helpers
# ---------------------------------------------------------------------------

_logger = logging.getLogger("LiveWire")


class _NoopTracker:
    """Ensures each noop message is printed at most once."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._logged: dict[str, bool] = {}

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

    def reset(self) -> None:
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

    def __init__(self, agent: Any, *, returns: Any = None) -> None:
        self.agent = agent
        self.returns = returns


# ---------------------------------------------------------------------------
# ChatContext (minimal stub)
# ---------------------------------------------------------------------------


class ChatContext:
    """Minimal stub mirroring livekit ChatContext."""

    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    def append(self, *, role: str = "user", text: str = "") -> "ChatContext":
        self.messages.append({"role": role, "content": text})
        return self


# ---------------------------------------------------------------------------
# function_tool decorator
# ---------------------------------------------------------------------------


def function_tool(
    func: "Callable[..., Any] | None" = None,
    *,
    name: str | None = None,
    description: str | None = None,
) -> "Callable[..., Any]":
    """Mirrors the livekit ``@function_tool`` decorator.

    Wraps a plain function so it can be passed into ``Agent(tools=[...])``.
    Parameters are extracted from type-hints; the docstring is used as the
    description when *description* is not provided explicitly.
    """

    def _wrap(fn: "Callable[..., Any]") -> "Callable[..., Any]":
        tool_name = name or fn.__name__
        tool_desc = description or (inspect.getdoc(fn) or "")

        # Build a JSON-schema-style parameter dict from type hints
        sig = inspect.signature(fn)
        properties: dict[str, Any] = {}
        required: list[str] = []

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

        # Attach metadata to the function object. These are dynamic attrs on a
        # Callable, so each assignment carries an attr-defined ignore.
        fn._livewire_tool = True  # type: ignore[attr-defined]
        fn._tool_name = tool_name  # type: ignore[attr-defined]
        fn._tool_description = tool_desc  # type: ignore[attr-defined]
        fn._tool_parameters = schema  # type: ignore[attr-defined]
        fn._tool_handler = fn  # type: ignore[attr-defined]
        return fn

    if func is not None:
        # Used as @function_tool (without arguments)
        return _wrap(func)
    # Used as @function_tool(name=..., description=...)
    return _wrap


def _is_run_context(annotation: Any) -> bool:
    """Return True if *annotation* looks like a RunContext type."""
    if annotation is RunContext:
        return True
    name = getattr(annotation, "__name__", "") or str(annotation)
    return "RunContext" in name


def _python_type_to_json(annotation: Any) -> str:
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

    def __init__(
        self,
        session: Any = None,
        *,
        speech_handle: Any = None,
        function_call: Any = None,
    ) -> None:
        self.session = session
        self.speech_handle = speech_handle
        self.function_call = function_call

    @property
    def userdata(self) -> Any:
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
        tools: list[Any] | None = None,
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
        self._tools: list[Any] = list(tools or [])
        self._chat_ctx = chat_ctx
        self._session: AgentSession | None = None
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
    def session(self, value: "AgentSession | None") -> None:
        self._session = value

    # ------------------------------------------------------------------
    # Lifecycle hooks (override in subclass)
    # ------------------------------------------------------------------

    async def on_enter(self) -> None:
        """Called when the agent enters.  Override in subclass."""
        pass

    async def on_exit(self) -> None:
        """Called when the agent exits.  Override in subclass."""
        pass

    async def on_user_turn_completed(
        self, turn_ctx: Any = None, new_message: Any = None
    ) -> None:
        """Called when the user finishes speaking.  Override in subclass."""
        pass

    # ------------------------------------------------------------------
    # Pipeline nodes -- all noop + log
    # ------------------------------------------------------------------

    async def stt_node(self, audio: Any = None, model_settings: Any = None) -> None:
        """Noop -- SignalWire handles STT in its control plane."""
        _global_noop.once(
            "stt_node",
            "Agent.stt_node(): SignalWire's control plane handles speech "
            "recognition -- this node is a no-op",
        )

    async def llm_node(
        self, chat_ctx: Any = None, tools: Any = None, model_settings: Any = None
    ) -> None:
        """Noop -- SignalWire handles LLM in its control plane."""
        _global_noop.once(
            "llm_node",
            "Agent.llm_node(): SignalWire's control plane handles LLM "
            "inference -- this node is a no-op",
        )

    async def tts_node(self, text: Any = None, model_settings: Any = None) -> None:
        """Noop -- SignalWire handles TTS in its control plane."""
        _global_noop.once(
            "tts_node",
            "Agent.tts_node(): SignalWire's control plane handles "
            "text-to-speech -- this node is a no-op",
        )

    # ------------------------------------------------------------------
    # Dynamic updates
    # ------------------------------------------------------------------

    async def update_instructions(self, instructions: str) -> None:
        """Update the agent's instructions mid-session."""
        self.instructions = instructions

    async def update_tools(self, tools: list[Any]) -> None:
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
        tools: list[Any] | None = None,
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
                "AgentSession(stt=...): SignalWire's control plane handles "
                "speech recognition at scale -- no configuration needed",
            )
        if tts is not None:
            _global_noop.once(
                "tts",
                "AgentSession(tts=...): SignalWire's control plane handles "
                "text-to-speech at scale -- no configuration needed",
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
                "AgentSession(turn_detection=...): SignalWire's control "
                "plane handles turn detection at scale automatically",
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
        self._agent: Agent | None = None
        self._sw_agent: Any = None  # Will hold the real AgentBase
        self._say_queue: list[str] = []
        self._reply_instructions: list[str] = []
        self._history: list[dict[str, str]] = []
        self._noop = _NoopTracker()
        self._started = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def userdata(self) -> Any:
        return self._userdata

    @userdata.setter
    def userdata(self, val: Any) -> None:
        self._userdata = val

    @property
    def history(self) -> list[dict[str, str]]:
        return self._history

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(
        self, agent: Agent, *, room: Any = None, record: bool = False
    ) -> None:
        """Bind to an Agent.

        Inside :func:`run_app`, this also makes the session the one the job
        serves: once the entrypoint returns, ``run_app()`` builds the
        SignalWire agent from the last session started and runs it. The
        agent is built then, not here, so ``say()``, ``generate_reply()`` and
        ``update_agent()`` calls that follow still apply.
        """
        self._agent = agent
        agent.session = self
        self._started = True
        job = _current_job.get()
        if job is not None:
            job._session = self

    def say(self, text: str) -> None:
        """Have the agent open the call with ``text``, word for word.

        The text becomes the AI's ``static_greeting``, which the platform
        speaks as the agent's first words; several calls are joined. Once the
        agent is built, SignalWire can't add speech from here, so a later
        call is ignored with a log message.
        """
        if self._sw_agent is not None:
            self._noop.once(
                "say_after_build",
                "AgentSession.say() after the agent was built: SignalWire "
                "can't add speech mid-call from the session, so it's ignored",
            )
            return
        self._say_queue.append(text)

    def generate_reply(self, *, instructions: str | None = None) -> None:
        """Guide the agent's first reply.

        ``instructions`` is added to the prompt, under "Initial Greeting".
        Without instructions there's nothing to add: the agent replies on its
        own. Once the agent is built, a call is ignored with a log message.
        """
        if not instructions:
            return
        if self._sw_agent is not None:
            self._noop.once(
                "generate_reply_after_build",
                "AgentSession.generate_reply() after the agent was built: "
                "the prompt is already set, so it's ignored",
            )
            return
        self._reply_instructions.append(instructions)

    def interrupt(self) -> None:
        """Noop -- SignalWire handles barge-in automatically."""
        self._noop.once(
            "interrupt",
            "AgentSession.interrupt(): SignalWire handles barge-in "
            "automatically via its control plane",
        )

    def update_agent(self, agent: Agent) -> None:
        """Swap in a new Agent."""
        self._agent = agent
        agent.session = self

    # ------------------------------------------------------------------
    # Build the real SignalWire agent (run_app calls this for the job's session)
    # ------------------------------------------------------------------

    def _build_sw_agent(self) -> Any:
        """Translate the LiveWire session into a SignalWire AgentBase."""
        from signalwire import AgentBase as _AgentBase

        agent = self._agent
        if agent is None:
            raise RuntimeError("No Agent bound to session -- call start() first")

        sw = _AgentBase(
            name="LiveWireAgent",
            route="/",
            schema_validation=False,
        )

        # Prompt: the agent's instructions, then what generate_reply() asked
        # for. The prompt is text, which leaves out any POM section, so the
        # reply instructions are part of the text.
        prompt = agent.instructions
        if self._reply_instructions:
            greeting = "\n\n".join(self._reply_instructions)
            prompt = f"{prompt}\n\n## Initial Greeting\n\n{greeting}".lstrip()
        sw.set_prompt_text(prompt)

        # say(): the platform speaks static_greeting as the agent's first words
        if self._say_queue:
            sw.set_param("static_greeting", " ".join(self._say_queue))

        # LLM model: a model name, or a plugin object's model
        model_str = _model_name(self._llm or getattr(agent, "_llm_hint", NOT_GIVEN))
        if model_str:
            # Strip provider prefix if present  e.g. "openai/gpt-4" -> "gpt-4"
            if "/" in model_str:
                model_str = model_str.split("/", 1)[1]
            sw.set_param("model", model_str)

        # Interruption / barge. Locals are Any: the per-Agent override comes
        # from getattr(..., NOT_GIVEN) whose sentinel default is `object`.
        allow: Any = self._allow_interruptions
        agent_allow = getattr(agent, "_allow_interruptions", NOT_GIVEN)
        if agent_allow is not NOT_GIVEN:
            allow = agent_allow
        if not allow:
            # The platform's switch for barge-in; barge_confidence does nothing
            sw.set_param("enable_barge", False)

        # Endpointing delays
        min_ep: Any = self._min_endpointing_delay
        agent_min = getattr(agent, "_min_endpointing_delay", NOT_GIVEN)
        if agent_min is not NOT_GIVEN:
            min_ep = agent_min
        if min_ep and min_ep > 0:
            sw.set_param("end_of_speech_timeout", int(min_ep * 1000))

        max_ep: Any = self._max_endpointing_delay
        agent_max = getattr(agent, "_max_endpointing_delay", NOT_GIVEN)
        if agent_max is not NOT_GIVEN:
            max_ep = agent_max
        if max_ep and max_ep > 0:
            sw.set_param("attention_timeout", int(max_ep * 1000))

        # Register tools
        all_tools = list(self._tools) + list(agent._tools)
        for t in all_tools:
            if callable(t) and getattr(t, "_livewire_tool", False):
                _register_function_tool(sw, t)

        self._sw_agent = sw
        return sw


def _register_function_tool(sw_agent: Any, fn: "Callable[..., Any]") -> None:
    """Register a @function_tool-decorated function on a SignalWire AgentBase."""
    tool_name = fn._tool_name  # type: ignore[attr-defined]  # dynamic attr set by function_tool()
    tool_desc = fn._tool_description  # type: ignore[attr-defined]  # dynamic attr set by function_tool()
    tool_params = fn._tool_parameters  # type: ignore[attr-defined]  # dynamic attr set by function_tool()

    # Build a handler compatible with define_tool expectations
    def handler(
        args: dict[str, Any], raw_data: dict[str, Any] | None = None
    ) -> "FunctionResult":
        from signalwire.core.function_result import FunctionResult

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
            return FunctionResult(result)
        return FunctionResult(str(result))

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

    def __init__(self) -> None:
        self.userdata: dict[str, Any] = {}


class JobContext:
    """Mirrors a livekit JobContext -- provides room and connection info."""

    def __init__(self) -> None:
        self.room = Room()
        self.proc = JobProcess()
        # An AgentBase to run, if the entrypoint sets one itself
        self._agent: Any = None
        # The last AgentSession started while this job's entrypoint ran
        self._session: AgentSession | None = None

    async def connect(self) -> None:
        """Noop -- SignalWire agents connect automatically when the platform
        invokes the SWML endpoint."""
        _global_noop.once(
            "connect",
            "JobContext.connect(): SignalWire's control plane handles "
            "connection lifecycle at scale automatically",
        )

    async def wait_for_participant(self, *, identity: Any = None) -> None:
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

    def __init__(self, **kwargs: Any) -> None:
        self.setup_fnc: Callable[..., Any] | None = None
        self._entrypoint: Callable[..., Any] | None = None
        self._agent_name: str = ""

    def rtc_session(
        self,
        func: "Callable[..., Any] | None" = None,
        *,
        agent_name: str = "",
        type: str = "room",
        on_request: Any = None,
        on_session_end: Any = None,
    ) -> "Callable[..., Any]":
        """Decorator that registers the session entrypoint."""
        if type != "room":
            _global_noop.once(
                "server_type",
                f"AgentServer.rtc_session(type={type!r}): SignalWire's control "
                f"plane handles server topology at scale automatically",
            )

        def _decorator(fn: "Callable[..., Any]") -> "Callable[..., Any]":
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

from signalwire.livewire.plugins import (  # noqa: E402
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

    def __init__(self, model: str = "", **kwargs: Any) -> None:
        self.model = model
        _global_noop.once(
            "inference_stt",
            f"InferenceSTT({model!r}): SignalWire's control plane handles "
            f"speech recognition -- inference stubs are no-ops",
        )


class InferenceLLM:
    """Stub for livekit inference.LLM."""

    def __init__(self, model: str = "", **kwargs: Any) -> None:
        self.model = model


class InferenceTTS:
    """Stub for livekit inference.TTS."""

    def __init__(self, model: str = "", **kwargs: Any) -> None:
        self.model = model
        _global_noop.once(
            "inference_tts",
            f"InferenceTTS({model!r}): SignalWire's control plane handles "
            f"text-to-speech -- inference stubs are no-ops",
        )


# ---------------------------------------------------------------------------
# Namespace aliases matching livekit imports
#
#   from signalwire.livewire import voice, llm_ns, cli_ns, inference
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


def run_app(server: AgentServer) -> None:
    """Print banner, run the entrypoint, print a random tip, serve the agent.

    This is the main entry point -- mirrors ``livekit.agents.cli.run_app``.
    The entrypoint runs with a :class:`JobContext`; when it returns, the
    SignalWire agent built from the last ``AgentSession`` it started is run,
    which serves HTTP until the process stops.
    """
    _print_banner()

    # Run setup if registered
    if server.setup_fnc is not None:
        proc = JobProcess()
        server.setup_fnc(proc)

    # Create a JobContext
    ctx = JobContext()

    # Call the entrypoint -- should create session, agent, tools, etc.
    # AgentSession.start() finds the job through _current_job.
    if server._entrypoint is not None:
        entry = server._entrypoint
        token = _current_job.set(ctx)
        try:
            if asyncio.iscoroutinefunction(entry):
                asyncio.run(entry(ctx))
            else:
                entry(ctx)
        finally:
            _current_job.reset(token)

    # Build the SignalWire agent from the last session the entrypoint
    # started, unless the entrypoint set ctx._agent itself
    if ctx._agent is None and ctx._session is not None:
        ctx._agent = ctx._session._build_sw_agent()

    # Print a random tip right before starting
    _print_tip()

    # Start the underlying SignalWire agent
    if ctx._agent is not None:
        ctx._agent.run()
    else:
        _logger.error(
            "no agent was started -- the entrypoint must call "
            "await session.start(agent)"
        )


# Also provide a cli_ns namespace for ``from livewire import cli_ns``
class _CLINamespace:
    run_app = staticmethod(run_app)


cli_ns = _CLINamespace()


# ---------------------------------------------------------------------------
# __all__
# ---------------------------------------------------------------------------

__all__ = [  # noqa: RUF022  # deliberately grouped by category (Core types / Exceptions / etc.) with section comments for readability, not alphabetized
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
