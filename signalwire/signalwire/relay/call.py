"""Call object — represents a live RELAY call with command methods."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, TypeVar, TYPE_CHECKING
from collections.abc import Callable, Coroutine

from signalwire.core.logging_config import get_logger

from .constants import (
    CALL_STATE_CREATED,
    CALL_STATE_RINGING,
    CALL_STATE_ANSWERED,
    CALL_STATE_ENDING,
    CALL_STATE_ENDED,
    EVENT_CALL_PLAY,
    EVENT_CALL_RECORD,
    EVENT_CALL_DETECT,
    EVENT_CALL_STATE,
    EVENT_CALL_COLLECT,
    EVENT_CALL_FAX,
    EVENT_CALL_TAP,
    EVENT_CALL_STREAM,
    EVENT_CALL_PAY,
    EVENT_CALL_TRANSCRIBE,
    PLAY_STATE_FINISHED,
    PLAY_STATE_ERROR,
    RECORD_STATE_FINISHED,
    RECORD_STATE_NO_INPUT,
)
from .event import RelayEvent, parse_event
import contextlib

if TYPE_CHECKING:
    from .client import RelayClient

logger = get_logger("relay_call")

# Strong references to fire-and-forget callback tasks. asyncio only keeps a
# weak reference to a running task, so a bare ensure_future on a coroutine
# returned by a user callback could be garbage-collected mid-flight. These
# callbacks run on short-lived Action/Call instances, so the set is module-
# level (outliving any single instance); tasks are discarded on completion.
_bg_tasks: set[asyncio.Task[Any]] = set()


def _spawn_bg(coro: Coroutine[Any, Any, Any]) -> None:
    """Schedule a fire-and-forget coroutine while holding a strong reference.

    Args:
        coro: The coroutine to run in the background.
    """
    task = asyncio.ensure_future(coro)
    _bg_tasks.add(task)
    task.add_done_callback(_bg_tasks.discard)


EventHandler = Callable[[RelayEvent], Coroutine[Any, Any, None] | None]

# Bound to Action so _start_action returns the SAME concrete subtype it was
# given (PlayAction in -> PlayAction out), instead of the base Action.
_ActionT = TypeVar("_ActionT", bound="Action")


# ======================================================================
# Action classes — async handles for controllable operations
# ======================================================================


class Action:
    """Base class for async action handles (play, record, detect, etc.).

    Holds a control_id and back-reference to the Call. Resolves when the server
    sends a terminal event for this control_id.
    """

    def __init__(
        self,
        call: Call,
        control_id: str,
        terminal_event: str,
        terminal_states: tuple[str, ...],
    ):
        """Create an action handle for one control_id on a call.

        Args:
            call: The Call that owns this action.
            control_id: Control ID that ties server events to this action.
            terminal_event: Event type that carries this action's state.
            terminal_states: Event states that mark the action as finished.
        """
        self.call = call
        self.control_id = control_id
        self._terminal_event = terminal_event
        self._terminal_states = terminal_states
        self._done: asyncio.Future[RelayEvent] = (
            asyncio.get_running_loop().create_future()
        )
        self.result: RelayEvent | None = None
        self.completed = False
        self._on_completed: Callable[[RelayEvent], Any] | None = None

    def _check_event(self, event: RelayEvent) -> None:
        """Resolve the action if the event carries a terminal state.

        Called by Call when an event matches our control_id.

        Args:
            event: The event received for this control_id.
        """
        state = event.params.get("state", "")
        if state in self._terminal_states and not self._done.done():
            self._resolve(event)

    def _resolve(self, event: RelayEvent) -> None:
        """Mark the action as completed and fire the on_completed callback.

        Args:
            event: The terminal event to store as the result.
        """
        self.result = event
        self.completed = True
        self._done.set_result(event)
        if self._on_completed is not None:
            try:
                result = self._on_completed(event)
                if asyncio.iscoroutine(result):
                    _spawn_bg(result)
            except Exception:
                logger.exception(
                    f"Error in on_completed callback for {self.control_id}"
                )

    async def wait(self, timeout: float | None = None) -> RelayEvent:
        """Wait for the action to complete.

        A timed-out wait stops only the wait, not the action. The action still
        completes when its terminal event arrives, and a later ``wait()``
        returns that event.

        Args:
            timeout: Maximum seconds to wait. Waits without a limit if None.

        Returns:
            The terminal event.

        Raises:
            asyncio.TimeoutError: If ``timeout`` is exceeded.
        """
        if timeout is not None:
            return await asyncio.wait_for(asyncio.shield(self._done), timeout=timeout)
        return await self._done

    @property
    def is_done(self) -> bool:
        """Whether the action has already reached a terminal state.

        Returns:
            True once the terminal event has arrived, otherwise False.
        """
        return self._done.done()


class StoppableAction(Action):
    """An action that can be stopped.

    The concrete action sets ``_command_prefix`` (e.g. ``"play"``) and ``stop``
    posts ``calling.<prefix>.stop``. Reused by every action whose control
    surface is a ``<prefix>.stop`` command.
    """

    _command_prefix: str = ""

    async def stop(self) -> dict[str, Any]:
        """Stop the action by sending ``calling.<prefix>.stop``.

        Returns:
            The server's response to the stop request.
        """
        return await self.call._execute(
            f"{self._command_prefix}.stop", {"control_id": self.control_id}
        )


class PausableAction(StoppableAction):
    """A stoppable action that can also pause/resume (record, play, collect)."""

    async def pause(self, behavior: str | None = None) -> dict[str, Any]:
        """Pause the action by sending ``calling.<prefix>.pause``.

        Args:
            behavior: Optional pause behavior sent as ``behavior`` in the
                request. Omitted when empty.

        Returns:
            The server's response to the pause request.
        """
        params: dict[str, Any] = {"control_id": self.control_id}
        if behavior:
            params["behavior"] = behavior
        return await self.call._execute(f"{self._command_prefix}.pause", params)

    async def resume(self) -> dict[str, Any]:
        """Resume the action by sending ``calling.<prefix>.resume``.

        Returns:
            The server's response to the resume request.
        """
        return await self.call._execute(
            f"{self._command_prefix}.resume", {"control_id": self.control_id}
        )


class VolumeAction(PausableAction):
    """A pausable action that also supports a volume adjustment (play)."""

    async def volume(self, volume: float) -> dict[str, Any]:
        """Change the volume by sending ``calling.<prefix>.volume``.

        Args:
            volume: Volume adjustment value sent as ``volume`` in the request.

        Returns:
            The server's response to the volume request.
        """
        return await self.call._execute(
            f"{self._command_prefix}.volume",
            {"control_id": self.control_id, "volume": volume},
        )


class PlayAction(VolumeAction):
    """Handle for an active play operation (stop/pause/resume/volume)."""

    _command_prefix = "play"

    def __init__(self, call: Call, control_id: str):
        """Create a handle for a play operation.

        Args:
            call: The Call that owns this action.
            control_id: Control ID of the play operation.
        """
        super().__init__(
            call, control_id, EVENT_CALL_PLAY, (PLAY_STATE_FINISHED, PLAY_STATE_ERROR)
        )


class RecordAction(PausableAction):
    """Handle for an active record operation (stop/pause/resume)."""

    _command_prefix = "record"

    def __init__(self, call: Call, control_id: str):
        """Create a handle for a record operation.

        Args:
            call: The Call that owns this action.
            control_id: Control ID of the record operation.
        """
        super().__init__(
            call,
            control_id,
            EVENT_CALL_RECORD,
            (RECORD_STATE_FINISHED, RECORD_STATE_NO_INPUT),
        )


class DetectAction(StoppableAction):
    """Handle for an active detect operation (stop)."""

    _command_prefix = "detect"

    def __init__(self, call: Call, control_id: str):
        """Create a handle for a detect operation.

        Args:
            call: The Call that owns this action.
            control_id: Control ID of the detect operation.
        """
        super().__init__(call, control_id, EVENT_CALL_DETECT, ("finished", "error"))

    def _check_event(self, event: RelayEvent) -> None:
        """Resolve on the first detect result or on a terminal state.

        Detect delivers results continuously, so the action resolves on the first
        event that has a ``detect`` result or a finished/error state.

        Args:
            event: The event received for this control_id.
        """
        # Detect delivers results continuously. Resolve on first result or
        # when finished/error.
        detect = event.params.get("detect", {})
        state = event.params.get("state", "")
        if (detect or state in self._terminal_states) and not self._done.done():
            self._resolve(event)


class CollectAction(VolumeAction):
    """Handle for play_and_collect (stop/volume use the play_and_collect prefix).

    It also offers ``pause``, ``resume`` and ``start_input_timers``. The
    initial-timeout timer is a collect-specific command.
    """

    _command_prefix = "play_and_collect"

    def __init__(self, call: Call, control_id: str):
        """Create a handle for a play_and_collect operation.

        Args:
            call: The Call that owns this action.
            control_id: Control ID of the play_and_collect operation.
        """
        super().__init__(
            call,
            control_id,
            EVENT_CALL_COLLECT,
            ("finished", "error", "no_input", "no_match"),
        )

    def _check_event(self, event: RelayEvent) -> None:
        """Resolve on a collect result or terminal collect state.

        play_and_collect shares a control_id across play and collect phases. Only
        collect events are considered, so play events never resolve it.

        Args:
            event: The event received for this control_id.
        """
        # play_and_collect shares a control_id across play and collect
        # phases.  Only resolve on collect events, not play events.
        if event.event_type != EVENT_CALL_COLLECT:
            return
        result = event.params.get("result", {})
        if result and not self._done.done():
            self._resolve(event)
        else:
            super()._check_event(event)

    async def start_input_timers(self) -> dict[str, Any]:
        """Start the initial_timeout timer on an active collect.

        Returns:
            The server's response to the ``calling.collect.start_input_timers``
            request.
        """
        return await self.call._execute(
            "collect.start_input_timers", {"control_id": self.control_id}
        )


class StandaloneCollectAction(StoppableAction):
    """Handle for standalone calling.collect (without play)."""

    _command_prefix = "collect"

    def __init__(self, call: Call, control_id: str):
        """Create a handle for a standalone collect operation.

        Args:
            call: The Call that owns this action.
            control_id: Control ID of the collect operation.
        """
        super().__init__(
            call,
            control_id,
            EVENT_CALL_COLLECT,
            ("finished", "error", "no_input", "no_match"),
        )

    def _check_event(self, event: RelayEvent) -> None:
        """Resolve on a collect result or terminal collect state.

        Args:
            event: The event received for this control_id.
        """
        if event.event_type != EVENT_CALL_COLLECT:
            return
        result = event.params.get("result", {})
        state = event.params.get("state", "")
        if (result or state in self._terminal_states) and not self._done.done():
            self._resolve(event)

    async def start_input_timers(self) -> dict[str, Any]:
        """Start the initial_timeout timer on an active collect.

        Returns:
            The server's response to the ``calling.collect.start_input_timers``
            request.
        """
        return await self.call._execute(
            "collect.start_input_timers", {"control_id": self.control_id}
        )


class FaxAction(StoppableAction):
    """Handle for an active send_fax or receive_fax operation.

    The stop prefix (``send_fax``/``receive_fax``) is set per-instance from the
    constructor.
    """

    def __init__(self, call: Call, control_id: str, method_prefix: str):
        """Create a handle for a fax operation.

        Args:
            call: The Call that owns this action.
            control_id: Control ID of the fax operation.
            method_prefix: RPC prefix used by ``stop``: ``send_fax`` or
                ``receive_fax``.
        """
        super().__init__(call, control_id, EVENT_CALL_FAX, ("finished", "error"))
        self._command_prefix = method_prefix


class TapAction(StoppableAction):
    """Handle for an active tap operation (stop)."""

    _command_prefix = "tap"

    def __init__(self, call: Call, control_id: str):
        """Create a handle for a tap operation.

        Args:
            call: The Call that owns this action.
            control_id: Control ID of the tap operation.
        """
        super().__init__(call, control_id, EVENT_CALL_TAP, ("finished",))


class StreamAction(StoppableAction):
    """Handle for an active stream operation (stop)."""

    _command_prefix = "stream"

    def __init__(self, call: Call, control_id: str):
        """Create a handle for a stream operation.

        Args:
            call: The Call that owns this action.
            control_id: Control ID of the stream operation.
        """
        super().__init__(call, control_id, EVENT_CALL_STREAM, ("finished",))


class PayAction(StoppableAction):
    """Handle for an active pay operation (stop)."""

    _command_prefix = "pay"

    def __init__(self, call: Call, control_id: str):
        """Create a handle for a pay operation.

        Args:
            call: The Call that owns this action.
            control_id: Control ID of the pay operation.
        """
        super().__init__(call, control_id, EVENT_CALL_PAY, ("finished", "error"))


class TranscribeAction(StoppableAction):
    """Handle for an active transcribe operation (stop)."""

    _command_prefix = "transcribe"

    def __init__(self, call: Call, control_id: str):
        """Create a handle for a transcribe operation.

        Args:
            call: The Call that owns this action.
            control_id: Control ID of the transcribe operation.
        """
        super().__init__(call, control_id, EVENT_CALL_TRANSCRIBE, ("finished",))


class AIAction(StoppableAction):
    """Handle for an active AI agent session (stop)."""

    _command_prefix = "ai"

    def __init__(self, call: Call, control_id: str):
        """Create a handle for an AI agent session.

        Args:
            call: The Call that owns this action.
            control_id: Control ID of the AI session.
        """
        # AI sessions don't have a standard event type with state field —
        # they end when the call ends or when stopped. We treat "finished"
        # and "error" as terminal states from calling.call.ai events if any.
        super().__init__(call, control_id, "calling.call.ai", ("finished", "error"))


# ======================================================================
# Call class
# ======================================================================


class Call:
    """Represents a live RELAY call.

    Created by RelayClient on inbound ``calling.call.receive`` events or
    outbound ``dial``/``begin`` responses. All call control methods are async.
    Methods that start a long-running operation (play, record, detect, and so
    on) return an Action handle that you can stop, pause or wait on.

    Example:
        ```python
        from signalwire.relay import RelayClient

        client = RelayClient(
            project="your-project-id",
            token="your-api-token",
            contexts=["default"],
        )

        @client.on_call
        async def handle_call(call):
            await call.answer()
            action = await call.play_tts("Welcome to SignalWire!")
            await action.wait()
            await call.hangup()

        client.run()
        ```
    """

    def __init__(
        self,
        client: RelayClient,
        call_id: str,
        node_id: str,
        project_id: str,
        context: str,
        *,
        tag: str = "",
        direction: str = "",
        device: dict[str, Any] | None = None,
        state: str = "",
        segment_id: str = "",
    ):
        """Create a call object.

        Applications normally receive Call objects from RelayClient rather than
        constructing them.

        Args:
            client: The RelayClient that sends this call's requests.
            call_id: Unique ID of the call.
            node_id: ID of the node handling the call.
            project_id: ID of the project that owns the call.
            context: Routing context the call belongs to.
            tag: Correlation tag for the call.
            direction: Call direction, for example inbound or outbound.
            device: Device information for the call endpoint. Defaults to an
                empty dict.
            state: Current call state.
            segment_id: Call segment ID for tracking call legs.
        """
        self._client = client
        self.call_id = call_id
        self.node_id = node_id
        self.project_id = project_id
        self.context = context
        self.tag = tag
        self.direction = direction
        self.device = device or {}
        self.state = state
        self.segment_id = segment_id

        # Event listeners: event_type -> list of handlers
        self._listeners: dict[str, list[EventHandler]] = {}
        # Active actions indexed by control_id
        self._actions: dict[str, Action] = {}
        # Future that resolves when the call ends
        self._ended: asyncio.Future[RelayEvent] = (
            asyncio.get_running_loop().create_future()
        )

    # ------------------------------------------------------------------
    # Internal RPC primitive
    # ------------------------------------------------------------------

    async def _execute(
        self, method: str, extra_params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Send a ``calling.<method>`` JSON-RPC request for this call.

        The outer JSON-RPC method is ``"calling.<method>"`` (e.g.
        ``"calling.answer"``) with ``node_id`` and ``call_id`` in params.

        Only "call gone" is swallowed: a 404 or 410 server error means the call no
        longer exists, so the verb is a no-op and returns ``{}``. Every other server
        error is raised, so real failures (auth, bad params, server faults) reach
        the caller.

        Args:
            method: RPC method name without the ``calling.`` prefix.
            extra_params: Fields merged into the request params after
                ``node_id`` and ``call_id``.

        Returns:
            The server's response, or ``{}`` if the call no longer exists.
        """
        rpc_method = f"calling.{method}"
        params: dict[str, Any] = {
            "node_id": self.node_id,
            "call_id": self.call_id,
        }
        if extra_params:
            params.update(extra_params)
        try:
            return await self._client.execute(rpc_method, params)
        except Exception as exc:
            code = getattr(exc, "code", None)
            if code in (404, 410):
                # Call gone — swallow per the documented contract, return no-op.
                logger.warning(
                    f"Call {self.call_id} gone during {method} (code={code}): {exc}"
                )
                return {}
            # Any other server error (or a non-coded exception) propagates.
            raise

    # ------------------------------------------------------------------
    # Event plumbing
    # ------------------------------------------------------------------

    def on(self, event_type: str, handler: EventHandler) -> None:
        """Register an event listener for this call.

        Args:
            event_type: Event type to listen for, for example
                ``calling.call.state``.
            handler: Function or coroutine function called with each matching
                RelayEvent.
        """
        self._listeners.setdefault(event_type, []).append(handler)

    async def _dispatch_event(self, payload: dict[str, Any]) -> None:
        """Update call state, route to actions and notify listeners.

        Called by RelayClient when an event arrives for this call.

        Args:
            payload: Raw event payload from the server.
        """
        event = parse_event(payload)
        event_type = event.event_type

        # Update call state
        if event_type == EVENT_CALL_STATE:
            self.state = event.params.get("call_state", self.state)
            if self.state == CALL_STATE_ENDED and not self._ended.done():
                self._ended.set_result(event)

        # Route to active actions by control_id
        control_id = event.params.get("control_id", "")
        if control_id and control_id in self._actions:
            action = self._actions[control_id]
            action._check_event(event)
            # Clean up completed actions
            if action.completed:
                self._actions.pop(control_id, None)

        # Notify registered listeners (snapshot list to allow modification during iteration)
        handlers = list(self._listeners.get(event_type, []))
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    _spawn_bg(result)
            except Exception:  # noqa: PERF203  # per-iteration error isolation: one listener's failure must not prevent notifying the others
                logger.exception(f"Error in event handler for {event_type}")

    async def wait_for(
        self,
        event_type: str,
        predicate: Callable[[RelayEvent], bool] | None = None,
        timeout: float | None = None,
    ) -> RelayEvent:
        """Wait for a specific event, optionally filtered by predicate.

        Args:
            event_type: Event type to wait for.
            predicate: Optional function that returns True for the event you
                want. The first event of this type is used if omitted.
            timeout: Maximum seconds to wait. Waits without a limit if None.

        Returns:
            The first matching event.

        Raises:
            asyncio.TimeoutError: If ``timeout`` is exceeded.
        """
        future: asyncio.Future[RelayEvent] = asyncio.get_running_loop().create_future()

        def _handler(event: RelayEvent) -> None:
            """Resolve the future with the first matching event.

            Args:
                event: The event received.
            """
            if future.done():
                return
            if predicate is None or predicate(event):
                future.set_result(event)

        self.on(event_type, _handler)
        try:
            if timeout is not None:
                return await asyncio.wait_for(future, timeout=timeout)
            return await future
        finally:
            # Clean up the one-shot handler
            if event_type in self._listeners:
                with contextlib.suppress(ValueError):
                    self._listeners[event_type].remove(_handler)

    async def wait_for_ended(self, timeout: float | None = None) -> RelayEvent:
        """Wait for the call to reach the ended state.

        Args:
            timeout: Maximum seconds to wait. Waits without a limit if None.

        Returns:
            The event that carried the ended state.

        Raises:
            asyncio.TimeoutError: If ``timeout`` is exceeded.
        """
        if timeout is not None:
            return await asyncio.wait_for(self._ended, timeout=timeout)
        return await self._ended

    # ------------------------------------------------------------------
    # Action helper
    # ------------------------------------------------------------------

    async def _start_action(
        self,
        action: _ActionT,
        method: str,
        params: dict[str, Any],
        on_completed: Callable[[RelayEvent], Any] | None = None,
    ) -> _ActionT:
        """Register an action, execute the RPC, and clean up on failure.

        If _execute raises, the action is removed from _actions and its Future is
        rejected so callers of action.wait() get the error instead of hanging
        forever.

        If the call is already gone (404/410 handled by _execute) or already ended,
        the action is immediately marked completed so action.wait() returns right
        away instead of hanging.

        Args:
            action: The action handle to register.
            method: RPC method name without the ``calling.`` prefix.
            params: Request params, including the control_id.
            on_completed: Optional callback invoked when the action reaches a
                terminal state. Can be a regular function or a coroutine
                function; coroutines are scheduled as tasks.

        Returns:
            The same action that was passed in.
        """
        if self.state == CALL_STATE_ENDED:
            logger.warning(f"Call {self.call_id} already ended, skipping {method}")
            gone_event = RelayEvent(event_type="", params={})
            action._resolve(gone_event)
            return action
        action._on_completed = on_completed
        self._actions[action.control_id] = action
        try:
            result = await self._execute(method, params)
        except Exception as exc:
            self._actions.pop(action.control_id, None)
            if not action._done.done():
                action._done.set_exception(exc)
            raise
        # _execute returns {} when the call is gone (404/410) — resolve
        # the action immediately so action.wait() doesn't hang forever.
        if not result:
            self._actions.pop(action.control_id, None)
            if not action._done.done():
                gone_event = RelayEvent(event_type="", params={})
                action._resolve(gone_event)
        return action

    # ------------------------------------------------------------------
    # Call lifecycle methods
    # ------------------------------------------------------------------

    async def answer(self, **kwargs: Any) -> dict[str, Any]:
        """Answer an inbound call.

        Sends ``calling.answer``.

        Args:
            **kwargs: Extra fields merged into the ``calling.answer`` request
                params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.answer`` request, or ``{}``
            if the call no longer exists.
        """
        return await self._execute("answer", kwargs or None)

    async def ring(self, **kwargs: Any) -> dict[str, Any]:
        """Send 180 Ringing on an inbound call without answering it.

        Sends ``calling.ring``.

        Args:
            **kwargs: Extra fields merged into the ``calling.ring`` request
                params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.ring`` request, or ``{}`` if
            the call no longer exists.
        """
        return await self._execute("ring", kwargs or None)

    async def hangup(self, reason: str = "hangup") -> dict[str, Any]:
        """End/hang up the call.

        Sends ``calling.end``.

        Args:
            reason: Reason sent as ``reason`` in the request.

        Returns:
            The server's response to the ``calling.end`` request, or ``{}`` if
            the call no longer exists.
        """
        return await self._execute("end", {"reason": reason})

    async def pass_(self) -> dict[str, Any]:
        """Decline control of an inbound call, returning it to routing.

        Sends ``calling.pass``. The method name has a trailing underscore because
        ``pass`` is a Python keyword.

        Returns:
            The server's response to the ``calling.pass`` request, or ``{}`` if
            the call no longer exists.
        """
        return await self._execute("pass")

    # ------------------------------------------------------------------
    # Audio playback
    # ------------------------------------------------------------------

    async def play(
        self,
        media: list[dict[str, Any]],
        *,
        volume: float | None = None,
        direction: str | None = None,
        loop: int | None = None,
        control_id: str | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> PlayAction:
        """Play audio content. Returns a PlayAction for stop/pause/resume/wait.

        Sends ``calling.play``. Media items can be TTS, audio file URLs, silence or
        ringtones.

        Args:
            media: List of media items to play. Each item is a dict with a
                ``type`` key and a ``params`` dict, for example ``{"type":
                "tts", "params": {"text": "Hello"}}``.
            volume: Volume adjustment in dB, sent as ``volume``. Omitted if
                None.
            direction: Where the audio goes: ``"listen"`` (the call hears it,
                the platform default), ``"speak"`` (the connected party hears
                it) or ``"both"``. Omitted if None.
            loop: How many times to play the media. ``0`` repeats it until
                stopped. Omitted if None, and the platform plays it once.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.play`` request
                params. They override fields of the same name.

        Returns:
            A PlayAction handle with ``stop()``, ``pause()``, ``resume()``,
            ``volume()`` and ``wait()``. ``wait()`` returns the terminal play
            event.

        Example:
            ```python
            action = await call.play([
                {"type": "tts", "params": {"text": "Please hold while we connect."}},
                {"type": "silence", "params": {"duration": 1}},
                {"type": "audio", "params": {"url": "https://example.com/music.mp3"}},
            ])
            await action.wait()
            ```
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {"control_id": cid, "play": media}
        if volume is not None:
            params["volume"] = volume
        if direction is not None:
            params["direction"] = direction
        if loop is not None:
            params["loop"] = loop
        params.update(kwargs)
        action = PlayAction(self, cid)
        return await self._start_action(
            action, "play", params, on_completed=on_completed
        )

    async def play_tts(
        self,
        text: str,
        *,
        language: str | None = None,
        gender: str | None = None,
        voice: str | None = None,
        volume: float | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
    ) -> PlayAction:
        """Play text-to-speech. Typed convenience over :meth:`play`.

        Restores the legacy ``call.play_tts(text=...)`` ergonomics so callers don't
        hand-build the ``{"type": "tts", "params": {...}}`` media shape. Sends
        ``calling.play``.

        Args:
            text: Text to speak.
            language: Language code placed in the TTS params. Omitted if None.
            gender: Voice gender placed in the TTS params. Omitted if None.
            voice: Voice name placed in the TTS params. Omitted if None.
            volume: Volume adjustment sent as ``volume``. Omitted if None.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.

        Returns:
            A PlayAction handle with ``stop()``, ``pause()``, ``resume()``,
            ``volume()`` and ``wait()``.
        """
        tts: dict[str, Any] = {"text": text}
        if language is not None:
            tts["language"] = language
        if gender is not None:
            tts["gender"] = gender
        if voice is not None:
            tts["voice"] = voice
        return await self.play(
            [{"type": "tts", "params": tts}], volume=volume, on_completed=on_completed
        )

    async def play_audio(
        self,
        url: str,
        *,
        volume: float | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
    ) -> PlayAction:
        """Play an audio file from a URL. Typed convenience over :meth:`play`.

        Sends ``calling.play``.

        Args:
            url: URL of the audio file.
            volume: Volume adjustment sent as ``volume``. Omitted if None.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.

        Returns:
            A PlayAction handle with ``stop()``, ``pause()``, ``resume()``,
            ``volume()`` and ``wait()``.
        """
        return await self.play(
            [{"type": "audio", "params": {"url": url}}],
            volume=volume,
            on_completed=on_completed,
        )

    async def play_silence(
        self,
        duration: float,
        *,
        on_completed: Callable[[RelayEvent], Any] | None = None,
    ) -> PlayAction:
        """Play silence for ``duration`` seconds. Typed convenience over :meth:`play`.

        Sends ``calling.play``.

        Args:
            duration: Seconds of silence to play.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.

        Returns:
            A PlayAction handle with ``stop()``, ``pause()``, ``resume()``,
            ``volume()`` and ``wait()``.
        """
        return await self.play(
            [{"type": "silence", "params": {"duration": duration}}],
            on_completed=on_completed,
        )

    async def play_ringtone(
        self,
        name: str,
        *,
        duration: float | None = None,
        volume: float | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
    ) -> PlayAction:
        """Play a named ringtone by country code. Typed convenience over :meth:`play`.

        Sends ``calling.play``.

        Args:
            name: Ringtone name, for example a country code.
            duration: Seconds to play the ringtone. Omitted if None.
            volume: Volume adjustment sent as ``volume``. Omitted if None.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.

        Returns:
            A PlayAction handle with ``stop()``, ``pause()``, ``resume()``,
            ``volume()`` and ``wait()``.
        """
        rt: dict[str, Any] = {"name": name}
        if duration is not None:
            rt["duration"] = duration
        return await self.play(
            [{"type": "ringtone", "params": rt}],
            volume=volume,
            on_completed=on_completed,
        )

    # ------------------------------------------------------------------
    # Detect convenience (typed wrappers over detect())
    # ------------------------------------------------------------------

    async def detect_digit(
        self,
        *,
        digits: str | None = None,
        timeout: float | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
    ) -> DetectAction:
        """Detect DTMF digits. Typed convenience over :meth:`detect`.

        Sends ``calling.detect`` with a ``digit`` detector.

        Args:
            digits: Digits to listen for, placed in the detector params. Omitted
                if None.
            timeout: Seconds to wait for the detection to finish before stopping
                it.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.

        Returns:
            A DetectAction handle with ``stop()`` and ``wait()``. ``wait()``
            returns the first event that carries a detect result, or the
            finished or error event.
        """
        params: dict[str, Any] = {}
        if digits is not None:
            params["digits"] = digits
        return await self.detect(
            {"type": "digit", "params": params},
            timeout=timeout,
            on_completed=on_completed,
        )

    async def detect_answering_machine(
        self,
        *,
        initial_timeout: float | None = None,
        end_silence_timeout: float | None = None,
        machine_voice_threshold: float | None = None,
        machine_words_threshold: int | None = None,
        detect_interruptions: bool | None = None,
        detect_message_end: bool | None = None,
        timeout: float | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
    ) -> DetectAction:
        """Detect human vs answering machine (AMD).

        Typed convenience over :meth:`detect`.

        Sends ``calling.detect`` with a ``machine`` detector. Each tuning argument
        is placed in the detector params and omitted if None.

        Args:
            initial_timeout: Detector ``initial_timeout`` value.
            end_silence_timeout: Detector ``end_silence_timeout`` value.
            machine_voice_threshold: Detector ``machine_voice_threshold`` value.
            machine_words_threshold: Detector ``machine_words_threshold`` value.
            detect_interruptions: Detector ``detect_interruptions`` value.
            detect_message_end: Detector ``detect_message_end`` value.
            timeout: Seconds to wait for the detection to finish before stopping
                it.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.

        Returns:
            A DetectAction handle with ``stop()`` and ``wait()``. ``wait()``
            returns the first event that carries a detect result, or the
            finished or error event.
        """
        params: dict[str, Any] = {
            key: val
            for key, val in (
                ("initial_timeout", initial_timeout),
                ("end_silence_timeout", end_silence_timeout),
                ("machine_voice_threshold", machine_voice_threshold),
                ("machine_words_threshold", machine_words_threshold),
                ("detect_interruptions", detect_interruptions),
                ("detect_message_end", detect_message_end),
            )
            if val is not None
        }
        return await self.detect(
            {"type": "machine", "params": params},
            timeout=timeout,
            on_completed=on_completed,
        )

    async def detect_fax(
        self,
        *,
        tone: str | None = None,
        timeout: float | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
    ) -> DetectAction:
        """Detect a fax tone (CED/CNG). Typed convenience over :meth:`detect`.

        Sends ``calling.detect`` with a ``fax`` detector.

        Args:
            tone: Fax tone to listen for, placed in the detector params. Omitted
                if None.
            timeout: Seconds to wait for the detection to finish before stopping
                it.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.

        Returns:
            A DetectAction handle with ``stop()`` and ``wait()``. ``wait()``
            returns the first event that carries a detect result, or the
            finished or error event.
        """
        params: dict[str, Any] = {}
        if tone is not None:
            params["tone"] = tone
        return await self.detect(
            {"type": "fax", "params": params},
            timeout=timeout,
            on_completed=on_completed,
        )

    # ------------------------------------------------------------------
    # Prompt convenience (typed media over play_and_collect())
    # ------------------------------------------------------------------

    async def prompt_tts(
        self,
        text: str,
        collect: dict[str, Any],
        *,
        language: str | None = None,
        gender: str | None = None,
        voice: str | None = None,
        volume: float | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
    ) -> CollectAction:
        """Play TTS then collect input. Typed media over :meth:`play_and_collect`.

        Sends ``calling.play_and_collect``.

        Args:
            text: Text to speak as the prompt.
            collect: Input collection config, sent as ``collect``.
            language: Language code placed in the TTS params. Omitted if None.
            gender: Voice gender placed in the TTS params. Omitted if None.
            voice: Voice name placed in the TTS params. Omitted if None.
            volume: Volume adjustment sent as ``volume``. Omitted if None.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.

        Returns:
            A CollectAction handle with ``stop()``, ``pause()``, ``resume()``,
            ``volume()``, ``start_input_timers()`` and ``wait()``. ``wait()``
            returns the collect event that carries the result.
        """
        tts: dict[str, Any] = {"text": text}
        if language is not None:
            tts["language"] = language
        if gender is not None:
            tts["gender"] = gender
        if voice is not None:
            tts["voice"] = voice
        return await self.play_and_collect(
            [{"type": "tts", "params": tts}],
            collect,
            volume=volume,
            on_completed=on_completed,
        )

    async def prompt_audio(
        self,
        url: str,
        collect: dict[str, Any],
        *,
        volume: float | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
    ) -> CollectAction:
        """Play an audio file then collect input.

        Typed media over :meth:`play_and_collect`.

        Sends ``calling.play_and_collect``.

        Args:
            url: URL of the audio file to play as the prompt.
            collect: Input collection config, sent as ``collect``.
            volume: Volume adjustment sent as ``volume``. Omitted if None.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.

        Returns:
            A CollectAction handle with ``stop()``, ``pause()``, ``resume()``,
            ``volume()``, ``start_input_timers()`` and ``wait()``. ``wait()``
            returns the collect event that carries the result.
        """
        return await self.play_and_collect(
            [{"type": "audio", "params": {"url": url}}],
            collect,
            volume=volume,
            on_completed=on_completed,
        )

    # ------------------------------------------------------------------
    # State-wait convenience (typed waits over wait_for())
    # ------------------------------------------------------------------

    async def _wait_for_state(self, target: str, timeout: float | None) -> RelayEvent:
        """Wait until the call reaches ``target`` or a later state.

        Returns immediately if the call is already at or past the target.

        Args:
            target: Call state to wait for.
            timeout: Maximum seconds to wait. Waits without a limit if None.

        Returns:
            The state event, or a synthetic state event if already at or past
            the target.
        """
        order = (
            CALL_STATE_CREATED,
            CALL_STATE_RINGING,
            CALL_STATE_ANSWERED,
            CALL_STATE_ENDING,
            CALL_STATE_ENDED,
        )

        def rank(s: str) -> int:
            """Return the position of a state in the call lifecycle.

            Args:
                s: Call state name.

            Returns:
                Index in the lifecycle order, or -1 for an unknown state.
            """
            return order.index(s) if s in order else -1

        # Already at or past the target -> return immediately (matches legacy SDK).
        if rank(self.state) >= rank(target):
            return RelayEvent(
                event_type=EVENT_CALL_STATE, params={"call_state": self.state}
            )
        return await self.wait_for(
            EVENT_CALL_STATE,
            lambda e: e.params.get("call_state") == target,
            timeout=timeout,
        )

    async def wait_for_answered(self, timeout: float | None = None) -> RelayEvent:
        """Wait until the call is answered (immediate if already answered or past it).

        Args:
            timeout: Maximum seconds to wait. Waits without a limit if None.

        Returns:
            The state event for the answered state.
        """
        return await self._wait_for_state(CALL_STATE_ANSWERED, timeout)

    async def wait_for_ringing(self, timeout: float | None = None) -> RelayEvent:
        """Wait until the call is ringing (immediate if already ringing or past it).

        Args:
            timeout: Maximum seconds to wait. Waits without a limit if None.

        Returns:
            The state event for the ringing state.
        """
        return await self._wait_for_state(CALL_STATE_RINGING, timeout)

    async def wait_for_ending(self, timeout: float | None = None) -> RelayEvent:
        """Wait until the call is ending (immediate if already ending or past it).

        Args:
            timeout: Maximum seconds to wait. Waits without a limit if None.

        Returns:
            The state event for the ending state.
        """
        return await self._wait_for_state(CALL_STATE_ENDING, timeout)

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    async def record(
        self,
        audio: dict[str, Any] | None = None,
        *,
        control_id: str | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> RecordAction:
        """Record audio from the call. Returns a RecordAction.

        Sends ``calling.record`` with the ``audio`` dict wrapped as
        ``record.audio``.

        Args:
            audio: Audio recording configuration, for example ``beep``,
                ``end_silence_timeout`` and ``terminators``. An empty dict is
                sent if None.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.record`` request
                params. They override fields of the same name.

        Returns:
            A RecordAction handle with ``stop()``, ``pause()``, ``resume()`` and
            ``wait()``. ``wait()`` returns the terminal record event.

        Example:
            ```python
            action = await call.record(
                audio={"beep": True, "end_silence_timeout": 3, "terminators": "#"},
            )
            event = await action.wait()
            url = event.params.get("url", "")
            print(f"Recording saved: {url}")
            ```
        """
        cid = control_id or str(uuid.uuid4())
        record_obj = {"audio": audio or {}}
        params: dict[str, Any] = {"control_id": cid, "record": record_obj}
        params.update(kwargs)
        action = RecordAction(self, cid)
        return await self._start_action(
            action, "record", params, on_completed=on_completed
        )

    # ------------------------------------------------------------------
    # Input collection
    # ------------------------------------------------------------------

    async def play_and_collect(
        self,
        media: list[dict[str, Any]],
        collect: dict[str, Any],
        *,
        volume: float | None = None,
        control_id: str | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> CollectAction:
        """Play audio and collect digit/speech input.

        Sends ``calling.play_and_collect``. The returned action resolves on collect
        events only, so ``wait()`` returns when input is collected or the collect
        ends, not when the audio finishes.

        Args:
            media: List of media items to play as the prompt, in the same format
                as :meth:`play`.
            collect: Input collection config, sent as ``collect``. It can hold
                ``digits`` and ``speech`` settings.
            volume: Volume adjustment for the prompt, sent as ``volume``.
                Omitted if None.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.play_and_collect``
                request params. They override fields of the same name.

        Returns:
            A CollectAction handle with ``stop()``, ``pause()``, ``resume()``,
            ``volume()``, ``start_input_timers()`` and ``wait()``. ``wait()``
            returns the collect event that carries the result.

        Example:
            ```python
            action = await call.play_and_collect(
                media=[{"type": "tts", "params": {"text": "Press 1 for sales."}}],
                collect={"digits": {"max": 1, "digit_timeout": 5, "terminators": "#"}},
            )
            event = await action.wait()
            result = event.params.get("result", {})
            digits = result.get("params", {}).get("digits", "")
            ```
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {
            "control_id": cid,
            "play": media,
            "collect": collect,
        }
        if volume is not None:
            params["volume"] = volume
        params.update(kwargs)
        action = CollectAction(self, cid)
        return await self._start_action(
            action, "play_and_collect", params, on_completed=on_completed
        )

    async def collect(
        self,
        *,
        digits: dict[str, Any] | None = None,
        speech: dict[str, Any] | None = None,
        initial_timeout: float | None = None,
        partial_results: bool | None = None,
        continuous: bool | None = None,
        send_start_of_input: bool | None = None,
        start_input_timers: bool | None = None,
        control_id: str | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> StandaloneCollectAction:
        """Collect digit/speech input without playing media.

        Sends ``calling.collect``.

        Args:
            digits: Digit collection settings. Omitted if None.
            speech: Speech collection settings. Omitted if None.
            initial_timeout: Seconds to wait for input to start. Omitted if
                None.
            partial_results: Sent as ``partial_results`` when not None.
            continuous: Sent as ``continuous`` when not None.
            send_start_of_input: Sent as ``send_start_of_input`` when not None.
            start_input_timers: Sent as ``start_input_timers`` when not None.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.collect`` request
                params. They override fields of the same name.

        Returns:
            A StandaloneCollectAction handle with ``stop()``,
            ``start_input_timers()`` and ``wait()``. ``wait()`` returns the
            collect event that carries the result or a terminal state.
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {"control_id": cid}
        if digits is not None:
            params["digits"] = digits
        if speech is not None:
            params["speech"] = speech
        if initial_timeout is not None:
            params["initial_timeout"] = initial_timeout
        if partial_results is not None:
            params["partial_results"] = partial_results
        if continuous is not None:
            params["continuous"] = continuous
        if send_start_of_input is not None:
            params["send_start_of_input"] = send_start_of_input
        if start_input_timers is not None:
            params["start_input_timers"] = start_input_timers
        params.update(kwargs)
        action = StandaloneCollectAction(self, cid)
        return await self._start_action(
            action, "collect", params, on_completed=on_completed
        )

    # ------------------------------------------------------------------
    # Bridging & connectivity
    # ------------------------------------------------------------------

    async def connect(
        self,
        devices: list[list[dict[str, Any]]],
        *,
        ringback: list[dict[str, Any]] | None = None,
        tag: str | None = None,
        max_duration: int | None = None,
        max_price_per_minute: float | None = None,
        status_url: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Bridge the call to one or more destinations.

        Sends ``calling.connect``. The outer list of ``devices`` is tried one group
        at a time; devices inside a group are dialed in parallel.

        Args:
            devices: Device groups to dial. Each device is a dict with a
                ``type`` and a ``params`` dict.
            ringback: Media items to play to the caller while the destination
                rings, in the same format as :meth:`play`. Omitted if None.
            tag: Correlation tag for the connected call. Omitted if None.
            max_duration: Maximum length of the bridged call in seconds. Omitted
                if None.
            max_price_per_minute: Maximum price per minute for the bridged call.
                Omitted if None.
            status_url: URL that receives connection status webhooks. Omitted if
                None.
            **kwargs: Extra fields merged into the ``calling.connect`` request
                params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.connect`` request, or ``{}``
            if the call no longer exists.

        Example:
            ```python
            result = await call.connect([
                [{"type": "phone", "params": {"to_number": "+15551234567",
                                              "from_number": "+15559876543"}}],
                [{"type": "phone", "params": {"to_number": "+15559999999",
                                              "from_number": "+15559876543"}}],
            ])
            ```
        """
        params: dict[str, Any] = {"devices": devices}
        if ringback is not None:
            params["ringback"] = ringback
        if tag is not None:
            params["tag"] = tag
        if max_duration is not None:
            params["max_duration"] = max_duration
        if max_price_per_minute is not None:
            params["max_price_per_minute"] = max_price_per_minute
        if status_url is not None:
            params["status_url"] = status_url
        params.update(kwargs)
        return await self._execute("connect", params)

    async def disconnect(self) -> dict[str, Any]:
        """Disconnect (unbridge) a connected call.

        Sends ``calling.disconnect``.

        Returns:
            The server's response to the ``calling.disconnect`` request, or
            ``{}`` if the call no longer exists.
        """
        return await self._execute("disconnect")

    # ------------------------------------------------------------------
    # DTMF
    # ------------------------------------------------------------------

    async def send_digits(
        self,
        digits: str,
        *,
        control_id: str | None = None,
    ) -> dict[str, Any]:
        """Send DTMF digits on the call.

        Sends ``calling.send_digits``.

        Args:
            digits: DTMF digits to send.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.

        Returns:
            The server's response to the ``calling.send_digits`` request, or
            ``{}`` if the call no longer exists.
        """
        cid = control_id or str(uuid.uuid4())
        return await self._execute(
            "send_digits",
            {
                "control_id": cid,
                "digits": digits,
            },
        )

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    async def detect(
        self,
        detect: dict[str, Any],
        *,
        timeout: float | None = None,
        control_id: str | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> DetectAction:
        """Start audio detection (machine, fax, digit). Returns a DetectAction.

        Sends ``calling.detect``.

        Args:
            detect: Detector config, sent as ``detect``. It holds a ``type`` and
                a ``params`` dict.
            timeout: Seconds to wait before the detection stops, sent as
                ``timeout``. Omitted if None.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.detect`` request
                params. They override fields of the same name.

        Returns:
            A DetectAction handle with ``stop()`` and ``wait()``. ``wait()``
            returns the first event that carries a detect result, or the
            finished or error event.
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {"control_id": cid, "detect": detect}
        if timeout is not None:
            params["timeout"] = timeout
        params.update(kwargs)
        action = DetectAction(self, cid)
        return await self._start_action(
            action, "detect", params, on_completed=on_completed
        )

    # ------------------------------------------------------------------
    # SIP Refer (transfer)
    # ------------------------------------------------------------------

    async def refer(
        self,
        device: dict[str, Any],
        *,
        status_url: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Transfer a SIP call to an external SIP endpoint via REFER.

        Sends ``calling.refer``.

        Args:
            device: Target device config, sent as ``device``.
            status_url: URL that receives refer status webhooks. Omitted if
                None.
            **kwargs: Extra fields merged into the ``calling.refer`` request
                params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.refer`` request, or ``{}`` if
            the call no longer exists.
        """
        params: dict[str, Any] = {"device": device}
        if status_url is not None:
            params["status_url"] = status_url
        params.update(kwargs)
        return await self._execute("refer", params)

    # ------------------------------------------------------------------
    # Payment
    # ------------------------------------------------------------------

    async def pay(
        self,
        payment_connector_url: str,
        *,
        control_id: str | None = None,
        input_method: str | None = None,
        status_url: str | None = None,
        payment_method: str | None = None,
        timeout: str | None = None,
        max_attempts: str | None = None,
        security_code: str | None = None,
        postal_code: str | None = None,
        min_postal_code_length: str | None = None,
        token_type: str | None = None,
        charge_amount: str | None = None,
        currency: str | None = None,
        language: str | None = None,
        voice: str | None = None,
        description: str | None = None,
        valid_card_types: str | None = None,
        parameters: list[dict[str, Any]] | None = None,
        prompts: list[dict[str, Any]] | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> PayAction:
        """Start a payment collection. Returns a PayAction.

        Sends ``calling.pay``. ``input_method`` is sent as ``input``. Every optional
        argument is omitted from the request if None.

        Args:
            payment_connector_url: URL of the payment connector.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            input_method: Input method, sent as ``input``.
            status_url: URL that receives payment status webhooks.
            payment_method: Payment method, sent as ``payment_method``.
            timeout: Sent as ``timeout``.
            max_attempts: Sent as ``max_attempts``.
            security_code: Sent as ``security_code``.
            postal_code: Sent as ``postal_code``.
            min_postal_code_length: Sent as ``min_postal_code_length``.
            token_type: Sent as ``token_type``.
            charge_amount: Sent as ``charge_amount``.
            currency: Sent as ``currency``.
            language: Sent as ``language``.
            voice: Sent as ``voice``.
            description: Sent as ``description``.
            valid_card_types: Sent as ``valid_card_types``.
            parameters: Extra connector parameters, sent as ``parameters``.
            prompts: Prompt definitions, sent as ``prompts``.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.pay`` request
                params. They override fields of the same name.

        Returns:
            A PayAction handle with ``stop()`` and ``wait()``. ``wait()``
            returns the finished or error pay event.
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {
            "control_id": cid,
            "payment_connector_url": payment_connector_url,
        }
        if input_method is not None:
            params["input"] = input_method
        if status_url is not None:
            params["status_url"] = status_url
        if payment_method is not None:
            params["payment_method"] = payment_method
        if timeout is not None:
            params["timeout"] = timeout
        if max_attempts is not None:
            params["max_attempts"] = max_attempts
        if security_code is not None:
            params["security_code"] = security_code
        if postal_code is not None:
            params["postal_code"] = postal_code
        if min_postal_code_length is not None:
            params["min_postal_code_length"] = min_postal_code_length
        if token_type is not None:
            params["token_type"] = token_type
        if charge_amount is not None:
            params["charge_amount"] = charge_amount
        if currency is not None:
            params["currency"] = currency
        if language is not None:
            params["language"] = language
        if voice is not None:
            params["voice"] = voice
        if description is not None:
            params["description"] = description
        if valid_card_types is not None:
            params["valid_card_types"] = valid_card_types
        if parameters is not None:
            params["parameters"] = parameters
        if prompts is not None:
            params["prompts"] = prompts
        params.update(kwargs)
        action = PayAction(self, cid)
        return await self._start_action(
            action, "pay", params, on_completed=on_completed
        )

    # ------------------------------------------------------------------
    # Faxing
    # ------------------------------------------------------------------

    async def send_fax(
        self,
        document: str,
        *,
        identity: str | None = None,
        header_info: str | None = None,
        control_id: str | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> FaxAction:
        """Send a fax document. Returns a FaxAction.

        Sends ``calling.send_fax``.

        Args:
            document: URL of the document to send.
            identity: Sender identity, sent as ``identity``. Omitted if None.
            header_info: Fax header text, sent as ``header_info``. Omitted if
                None.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.send_fax`` request
                params. They override fields of the same name.

        Returns:
            A FaxAction handle with ``stop()`` and ``wait()``. ``wait()``
            returns the finished or error fax event.
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {"control_id": cid, "document": document}
        if identity is not None:
            params["identity"] = identity
        if header_info is not None:
            params["header_info"] = header_info
        params.update(kwargs)
        action = FaxAction(self, cid, "send_fax")
        return await self._start_action(
            action, "send_fax", params, on_completed=on_completed
        )

    async def receive_fax(
        self,
        *,
        control_id: str | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> FaxAction:
        """Receive a fax. Returns a FaxAction.

        Sends ``calling.receive_fax``.

        Args:
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.receive_fax``
                request params. They override fields of the same name.

        Returns:
            A FaxAction handle with ``stop()`` and ``wait()``. ``wait()``
            returns the finished or error fax event.
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {"control_id": cid}
        params.update(kwargs)
        action = FaxAction(self, cid, "receive_fax")
        return await self._start_action(
            action, "receive_fax", params, on_completed=on_completed
        )

    # ------------------------------------------------------------------
    # Tap (media interception)
    # ------------------------------------------------------------------

    async def tap(
        self,
        tap: dict[str, Any],
        device: dict[str, Any],
        *,
        control_id: str | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> TapAction:
        """Intercept call media and stream it. Returns a TapAction.

        Sends ``calling.tap``.

        Args:
            tap: Tap config, sent as ``tap``.
            device: Destination device config, sent as ``device``.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.tap`` request
                params. They override fields of the same name.

        Returns:
            A TapAction handle with ``stop()`` and ``wait()``. ``wait()``
            returns the finished tap event.
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {
            "control_id": cid,
            "tap": tap,
            "device": device,
        }
        params.update(kwargs)
        action = TapAction(self, cid)
        return await self._start_action(
            action, "tap", params, on_completed=on_completed
        )

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

    async def stream(
        self,
        url: str,
        *,
        name: str | None = None,
        codec: str | None = None,
        track: str | None = None,
        status_url: str | None = None,
        status_url_method: str | None = None,
        authorization_bearer_token: str | None = None,
        custom_parameters: dict[str, Any] | None = None,
        control_id: str | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> StreamAction:
        """Start streaming call audio to a WebSocket endpoint. Returns a StreamAction.

        Sends ``calling.stream``. Every optional argument is omitted from the
        request if None.

        Args:
            url: WebSocket URL to stream to.
            name: Sent as ``name``.
            codec: Sent as ``codec``.
            track: Sent as ``track``.
            status_url: URL that receives stream status webhooks.
            status_url_method: HTTP method for ``status_url``.
            authorization_bearer_token: Bearer token sent as
                ``authorization_bearer_token``.
            custom_parameters: Custom parameters, sent as ``custom_parameters``.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.stream`` request
                params. They override fields of the same name.

        Returns:
            A StreamAction handle with ``stop()`` and ``wait()``. ``wait()``
            returns the finished stream event.
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {"control_id": cid, "url": url}
        if name is not None:
            params["name"] = name
        if codec is not None:
            params["codec"] = codec
        if track is not None:
            params["track"] = track
        if status_url is not None:
            params["status_url"] = status_url
        if status_url_method is not None:
            params["status_url_method"] = status_url_method
        if authorization_bearer_token is not None:
            params["authorization_bearer_token"] = authorization_bearer_token
        if custom_parameters is not None:
            params["custom_parameters"] = custom_parameters
        params.update(kwargs)
        action = StreamAction(self, cid)
        return await self._start_action(
            action, "stream", params, on_completed=on_completed
        )

    # ------------------------------------------------------------------
    # Transfer
    # ------------------------------------------------------------------

    async def transfer(
        self,
        dest: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Transfer call control to another RELAY app or SWML script.

        Sends ``calling.transfer``.

        Args:
            dest: Transfer destination, sent as ``dest``.
            **kwargs: Extra fields merged into the ``calling.transfer`` request
                params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.transfer`` request, or ``{}``
            if the call no longer exists.
        """
        params: dict[str, Any] = {"dest": dest}
        params.update(kwargs)
        return await self._execute("transfer", params)

    # ------------------------------------------------------------------
    # Conference
    # ------------------------------------------------------------------

    async def join_conference(
        self,
        name: str,
        *,
        muted: bool | None = None,
        beep: str | None = None,
        start_on_enter: bool | None = None,
        end_on_exit: bool | None = None,
        wait_url: str | None = None,
        max_participants: int | None = None,
        record: str | None = None,
        region: str | None = None,
        trim: str | None = None,
        coach: str | None = None,
        status_callback: str | None = None,
        status_callback_event: str | None = None,
        status_callback_event_type: str | None = None,
        status_callback_method: str | None = None,
        recording_status_callback: str | None = None,
        recording_status_callback_event: str | None = None,
        recording_status_callback_event_type: str | None = None,
        recording_status_callback_method: str | None = None,
        stream_obj: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Join an ad-hoc audio conference.

        Sends ``calling.join_conference``. Every optional argument is omitted from
        the request if None.

        Args:
            name: Conference name.
            muted: Sent as ``muted``.
            beep: Sent as ``beep``.
            start_on_enter: Sent as ``start_on_enter``.
            end_on_exit: Sent as ``end_on_exit``.
            wait_url: Sent as ``wait_url``.
            max_participants: Sent as ``max_participants``.
            record: Sent as ``record``.
            region: Sent as ``region``.
            trim: Sent as ``trim``.
            coach: Sent as ``coach``.
            status_callback: Sent as ``status_callback``.
            status_callback_event: Sent as ``status_callback_event``.
            status_callback_event_type: Sent as ``status_callback_event_type``.
            status_callback_method: Sent as ``status_callback_method``.
            recording_status_callback: Sent as ``recording_status_callback``.
            recording_status_callback_event: Sent as
                ``recording_status_callback_event``.
            recording_status_callback_event_type: Sent as
                ``recording_status_callback_event_type``.
            recording_status_callback_method: Sent as
                ``recording_status_callback_method``.
            stream_obj: Stream config, sent as ``stream``.
            **kwargs: Extra fields merged into the ``calling.join_conference``
                request params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.join_conference`` request, or
            ``{}`` if the call no longer exists.
        """
        params: dict[str, Any] = {"name": name}
        if muted is not None:
            params["muted"] = muted
        if beep is not None:
            params["beep"] = beep
        if start_on_enter is not None:
            params["start_on_enter"] = start_on_enter
        if end_on_exit is not None:
            params["end_on_exit"] = end_on_exit
        if wait_url is not None:
            params["wait_url"] = wait_url
        if max_participants is not None:
            params["max_participants"] = max_participants
        if record is not None:
            params["record"] = record
        if region is not None:
            params["region"] = region
        if trim is not None:
            params["trim"] = trim
        if coach is not None:
            params["coach"] = coach
        if status_callback is not None:
            params["status_callback"] = status_callback
        if status_callback_event is not None:
            params["status_callback_event"] = status_callback_event
        if status_callback_event_type is not None:
            params["status_callback_event_type"] = status_callback_event_type
        if status_callback_method is not None:
            params["status_callback_method"] = status_callback_method
        if recording_status_callback is not None:
            params["recording_status_callback"] = recording_status_callback
        if recording_status_callback_event is not None:
            params["recording_status_callback_event"] = recording_status_callback_event
        if recording_status_callback_event_type is not None:
            params["recording_status_callback_event_type"] = (
                recording_status_callback_event_type
            )
        if recording_status_callback_method is not None:
            params["recording_status_callback_method"] = (
                recording_status_callback_method
            )
        if stream_obj is not None:
            params["stream"] = stream_obj
        params.update(kwargs)
        return await self._execute("join_conference", params)

    async def leave_conference(
        self, conference_id: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Leave an audio conference.

        Sends ``calling.leave_conference``.

        Args:
            conference_id: ID of the conference to leave.
            **kwargs: Extra fields merged into the ``calling.leave_conference``
                request params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.leave_conference`` request,
            or ``{}`` if the call no longer exists.
        """
        params: dict[str, Any] = {"conference_id": conference_id}
        params.update(kwargs)
        return await self._execute("leave_conference", params)

    # ------------------------------------------------------------------
    # Hold / Unhold
    # ------------------------------------------------------------------

    async def hold(self) -> dict[str, Any]:
        """Put the call on hold.

        Sends ``calling.hold``.

        Returns:
            The server's response to the ``calling.hold`` request, or ``{}`` if
            the call no longer exists.
        """
        return await self._execute("hold")

    async def unhold(self) -> dict[str, Any]:
        """Release the call from hold.

        Sends ``calling.unhold``.

        Returns:
            The server's response to the ``calling.unhold`` request, or ``{}``
            if the call no longer exists.
        """
        return await self._execute("unhold")

    # ------------------------------------------------------------------
    # Denoise
    # ------------------------------------------------------------------

    async def denoise(self) -> dict[str, Any]:
        """Start noise reduction on the call.

        Sends ``calling.denoise``.

        Returns:
            The server's response to the ``calling.denoise`` request, or ``{}``
            if the call no longer exists.
        """
        return await self._execute("denoise")

    async def denoise_stop(self) -> dict[str, Any]:
        """Stop noise reduction on the call.

        Sends ``calling.denoise.stop``.

        Returns:
            The server's response to the ``calling.denoise.stop`` request, or
            ``{}`` if the call no longer exists.
        """
        return await self._execute("denoise.stop")

    # ------------------------------------------------------------------
    # Transcribe
    # ------------------------------------------------------------------

    async def transcribe(
        self,
        *,
        control_id: str | None = None,
        status_url: str | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> TranscribeAction:
        """Start transcribing the call. Returns a TranscribeAction.

        Sends ``calling.transcribe``.

        Args:
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            status_url: URL that receives transcription status webhooks. Omitted
                if None.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.transcribe``
                request params. They override fields of the same name.

        Returns:
            A TranscribeAction handle with ``stop()`` and ``wait()``. ``wait()``
            returns the finished transcribe event.
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {"control_id": cid}
        if status_url is not None:
            params["status_url"] = status_url
        params.update(kwargs)
        action = TranscribeAction(self, cid)
        return await self._start_action(
            action, "transcribe", params, on_completed=on_completed
        )

    # ------------------------------------------------------------------
    # Echo
    # ------------------------------------------------------------------

    async def echo(
        self,
        *,
        timeout: float | None = None,
        status_url: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Echo audio back to the caller (useful for testing).

        Sends ``calling.echo``.

        Args:
            timeout: Sent as ``timeout``. Omitted if None.
            status_url: URL that receives echo status webhooks. Omitted if None.
            **kwargs: Extra fields merged into the ``calling.echo`` request
                params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.echo`` request, or ``{}`` if
            the call no longer exists.
        """
        params: dict[str, Any] = {}
        if timeout is not None:
            params["timeout"] = timeout
        if status_url is not None:
            params["status_url"] = status_url
        params.update(kwargs)
        return await self._execute("echo", params or None)

    # ------------------------------------------------------------------
    # Digit bindings
    # ------------------------------------------------------------------

    async def bind_digit(
        self,
        digits: str,
        bind_method: str,
        *,
        bind_params: dict[str, Any] | None = None,
        realm: str | None = None,
        max_triggers: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Bind a DTMF digit sequence to trigger a RELAY method.

        Sends ``calling.bind_digit``.

        Args:
            digits: DTMF digit sequence to bind.
            bind_method: RELAY method to run when the sequence is dialed.
            bind_params: Params for the bound method, sent as ``params``.
                Omitted if None.
            realm: Realm that groups bindings. Omitted if None.
            max_triggers: Maximum number of times the binding fires. Omitted if
                None.
            **kwargs: Extra fields merged into the ``calling.bind_digit``
                request params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.bind_digit`` request, or
            ``{}`` if the call no longer exists.
        """
        params: dict[str, Any] = {
            "digits": digits,
            "bind_method": bind_method,
        }
        if bind_params is not None:
            params["params"] = bind_params
        if realm is not None:
            params["realm"] = realm
        if max_triggers is not None:
            params["max_triggers"] = max_triggers
        params.update(kwargs)
        return await self._execute("bind_digit", params)

    async def clear_digit_bindings(
        self,
        *,
        realm: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Clear all digit bindings, optionally filtered by realm.

        Sends ``calling.clear_digit_bindings``.

        Args:
            realm: Realm to clear. Omitted if None.
            **kwargs: Extra fields merged into the
                ``calling.clear_digit_bindings`` request params. They override
                fields of the same name.

        Returns:
            The server's response to the ``calling.clear_digit_bindings``
            request, or ``{}`` if the call no longer exists.
        """
        params: dict[str, Any] = {}
        if realm is not None:
            params["realm"] = realm
        params.update(kwargs)
        return await self._execute("clear_digit_bindings", params or None)

    # ------------------------------------------------------------------
    # Live transcribe / translate
    # ------------------------------------------------------------------

    async def live_transcribe(
        self,
        action: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Start or stop live transcription on the call.

        Sends ``calling.live_transcribe``.

        Args:
            action: Action config, sent as ``action``.
            **kwargs: Extra fields merged into the ``calling.live_transcribe``
                request params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.live_transcribe`` request, or
            ``{}`` if the call no longer exists.
        """
        params: dict[str, Any] = {"action": action}
        params.update(kwargs)
        return await self._execute("live_transcribe", params)

    async def live_translate(
        self,
        action: dict[str, Any],
        *,
        status_url: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Start or stop live translation on the call.

        Sends ``calling.live_translate``.

        Args:
            action: Action config, sent as ``action``.
            status_url: URL that receives translation status webhooks. Omitted
                if None.
            **kwargs: Extra fields merged into the ``calling.live_translate``
                request params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.live_translate`` request, or
            ``{}`` if the call no longer exists.
        """
        params: dict[str, Any] = {"action": action}
        if status_url is not None:
            params["status_url"] = status_url
        params.update(kwargs)
        return await self._execute("live_translate", params)

    # ------------------------------------------------------------------
    # Room
    # ------------------------------------------------------------------

    async def join_room(
        self,
        name: str,
        *,
        status_url: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Join a video/audio room.

        Sends ``calling.join_room``.

        Args:
            name: Room name.
            status_url: URL that receives room status webhooks. Omitted if None.
            **kwargs: Extra fields merged into the ``calling.join_room`` request
                params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.join_room`` request, or
            ``{}`` if the call no longer exists.
        """
        params: dict[str, Any] = {"name": name}
        if status_url is not None:
            params["status_url"] = status_url
        params.update(kwargs)
        return await self._execute("join_room", params)

    async def leave_room(self, **kwargs: Any) -> dict[str, Any]:
        """Leave the current room.

        Sends ``calling.leave_room``.

        Args:
            **kwargs: Extra fields merged into the ``calling.leave_room``
                request params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.leave_room`` request, or
            ``{}`` if the call no longer exists.
        """
        return await self._execute("leave_room", kwargs or None)

    # ------------------------------------------------------------------
    # AI Agent
    # ------------------------------------------------------------------

    async def ai(
        self,
        *,
        control_id: str | None = None,
        agent: str | None = None,
        prompt: dict[str, Any] | None = None,
        post_prompt: dict[str, Any] | None = None,
        post_prompt_url: str | None = None,
        post_prompt_auth_user: str | None = None,
        post_prompt_auth_password: str | None = None,
        global_data: dict[str, Any] | None = None,
        pronounce: list[dict[str, Any]] | None = None,
        hints: list[str] | None = None,
        languages: list[dict[str, Any]] | None = None,
        SWAIG: dict[str, Any] | None = None,
        ai_params: dict[str, Any] | None = None,
        on_completed: Callable[[RelayEvent], Any] | None = None,
        **kwargs: Any,
    ) -> AIAction:
        """Start an AI agent session on the call. Returns an AIAction.

        Sends ``calling.ai``. Every optional argument is omitted from the request if
        None.

        Args:
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            agent: Sent as ``agent``.
            prompt: Prompt config, sent as ``prompt``.
            post_prompt: Post-prompt config, sent as ``post_prompt``.
            post_prompt_url: Sent as ``post_prompt_url``.
            post_prompt_auth_user: Sent as ``post_prompt_auth_user``.
            post_prompt_auth_password: Sent as ``post_prompt_auth_password``.
            global_data: Sent as ``global_data``.
            pronounce: Pronunciation rules, sent as ``pronounce``.
            hints: Speech hints, sent as ``hints``.
            languages: Language configs, sent as ``languages``.
            SWAIG: SWAIG config, sent as ``SWAIG``.
            ai_params: AI parameters, sent as ``params``.
            on_completed: Callback invoked with the terminal event when the
                action finishes. It can be a plain function or a coroutine
                function.
            **kwargs: Extra fields merged into the ``calling.ai`` request
                params. They override fields of the same name.

        Returns:
            An AIAction handle with ``stop()`` and ``wait()``. ``wait()``
            returns the finished or error AI event, if one arrives.
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {"control_id": cid}
        if agent is not None:
            params["agent"] = agent
        if prompt is not None:
            params["prompt"] = prompt
        if post_prompt is not None:
            params["post_prompt"] = post_prompt
        if post_prompt_url is not None:
            params["post_prompt_url"] = post_prompt_url
        if post_prompt_auth_user is not None:
            params["post_prompt_auth_user"] = post_prompt_auth_user
        if post_prompt_auth_password is not None:
            params["post_prompt_auth_password"] = post_prompt_auth_password
        if global_data is not None:
            params["global_data"] = global_data
        if pronounce is not None:
            params["pronounce"] = pronounce
        if hints is not None:
            params["hints"] = hints
        if languages is not None:
            params["languages"] = languages
        if SWAIG is not None:
            params["SWAIG"] = SWAIG
        if ai_params is not None:
            params["params"] = ai_params
        params.update(kwargs)
        action = AIAction(self, cid)
        return await self._start_action(action, "ai", params, on_completed=on_completed)

    async def amazon_bedrock(
        self,
        *,
        prompt: Any | None = None,
        SWAIG: dict[str, Any] | None = None,
        ai_params: dict[str, Any] | None = None,
        global_data: dict[str, Any] | None = None,
        post_prompt: dict[str, Any] | None = None,
        post_prompt_url: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Connect to an Amazon Bedrock AI agent.

        Sends ``calling.amazon_bedrock``. Every optional argument is omitted from
        the request if None.

        Args:
            prompt: Prompt config, sent as ``prompt``.
            SWAIG: SWAIG config, sent as ``SWAIG``.
            ai_params: AI parameters, sent as ``params``.
            global_data: Sent as ``global_data``.
            post_prompt: Post-prompt config, sent as ``post_prompt``.
            post_prompt_url: Sent as ``post_prompt_url``.
            **kwargs: Extra fields merged into the ``calling.amazon_bedrock``
                request params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.amazon_bedrock`` request, or
            ``{}`` if the call no longer exists.
        """
        params: dict[str, Any] = {}
        if prompt is not None:
            params["prompt"] = prompt
        if SWAIG is not None:
            params["SWAIG"] = SWAIG
        if ai_params is not None:
            params["params"] = ai_params
        if global_data is not None:
            params["global_data"] = global_data
        if post_prompt is not None:
            params["post_prompt"] = post_prompt
        if post_prompt_url is not None:
            params["post_prompt_url"] = post_prompt_url
        params.update(kwargs)
        return await self._execute("amazon_bedrock", params)

    async def ai_message(
        self,
        *,
        message_text: str | None = None,
        role: str | None = None,
        reset: dict[str, Any] | None = None,
        global_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send a message to an active AI agent session.

        Sends ``calling.ai_message``. Every optional argument is omitted from the
        request if None.

        Args:
            message_text: Message text, sent as ``message_text``.
            role: Role of the message, sent as ``role``.
            reset: Reset config, sent as ``reset``.
            global_data: Sent as ``global_data``.
            **kwargs: Extra fields merged into the ``calling.ai_message``
                request params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.ai_message`` request, or
            ``{}`` if the call no longer exists.
        """
        params: dict[str, Any] = {}
        if message_text is not None:
            params["message_text"] = message_text
        if role is not None:
            params["role"] = role
        if reset is not None:
            params["reset"] = reset
        if global_data is not None:
            params["global_data"] = global_data
        params.update(kwargs)
        return await self._execute("ai_message", params)

    async def ai_hold(
        self,
        *,
        timeout: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Put an AI agent session on hold.

        Sends ``calling.ai_hold``.

        Args:
            timeout: Sent as ``timeout``. Omitted if None.
            prompt: Sent as ``prompt``. Omitted if None.
            **kwargs: Extra fields merged into the ``calling.ai_hold`` request
                params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.ai_hold`` request, or ``{}``
            if the call no longer exists.
        """
        params: dict[str, Any] = {}
        if timeout is not None:
            params["timeout"] = timeout
        if prompt is not None:
            params["prompt"] = prompt
        params.update(kwargs)
        return await self._execute("ai_hold", params or None)

    async def ai_unhold(
        self,
        *,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Resume an AI agent session from hold.

        Sends ``calling.ai_unhold``.

        Args:
            prompt: Sent as ``prompt``. Omitted if None.
            **kwargs: Extra fields merged into the ``calling.ai_unhold`` request
                params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.ai_unhold`` request, or
            ``{}`` if the call no longer exists.
        """
        params: dict[str, Any] = {}
        if prompt is not None:
            params["prompt"] = prompt
        params.update(kwargs)
        return await self._execute("ai_unhold", params or None)

    # ------------------------------------------------------------------
    # User events
    # ------------------------------------------------------------------

    async def user_event(
        self,
        *,
        event: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send a custom user-defined event.

        Sends ``calling.user_event``.

        Args:
            event: Event payload, sent as ``event``. Omitted if None.
            **kwargs: Extra fields merged into the ``calling.user_event``
                request params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.user_event`` request, or
            ``{}`` if the call no longer exists.
        """
        params: dict[str, Any] = {}
        if event is not None:
            params["event"] = event
        params.update(kwargs)
        return await self._execute("user_event", params)

    # ------------------------------------------------------------------
    # Queue
    # ------------------------------------------------------------------

    async def queue_enter(
        self,
        queue_name: str,
        *,
        control_id: str | None = None,
        status_url: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Place the call in a queue.

        Sends ``calling.queue.enter``.

        Args:
            queue_name: Name of the queue to enter.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            status_url: URL that receives queue status webhooks. Omitted if
                None.
            **kwargs: Extra fields merged into the ``calling.queue.enter``
                request params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.queue.enter`` request, or
            ``{}`` if the call no longer exists.
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {
            "control_id": cid,
            "queue_name": queue_name,
        }
        if status_url is not None:
            params["status_url"] = status_url
        params.update(kwargs)
        return await self._execute("queue.enter", params)

    async def queue_leave(
        self,
        queue_name: str,
        *,
        control_id: str | None = None,
        queue_id: str | None = None,
        status_url: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Remove the call from a queue.

        Sends ``calling.queue.leave``.

        Args:
            queue_name: Name of the queue to leave.
            control_id: Custom control ID for this operation. A UUID is
                generated if omitted.
            queue_id: Queue ID, sent as ``queue_id``. Omitted if None.
            status_url: URL that receives queue status webhooks. Omitted if
                None.
            **kwargs: Extra fields merged into the ``calling.queue.leave``
                request params. They override fields of the same name.

        Returns:
            The server's response to the ``calling.queue.leave`` request, or
            ``{}`` if the call no longer exists.
        """
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {
            "control_id": cid,
            "queue_name": queue_name,
        }
        if queue_id is not None:
            params["queue_id"] = queue_id
        if status_url is not None:
            params["status_url"] = status_url
        params.update(kwargs)
        return await self._execute("queue.leave", params)

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a short string with the call ID, state and direction.

        Returns:
            A string such as ``<Call id='...' state='answered'
            direction='inbound'>``.
        """
        return (
            f"<Call id={self.call_id!r} state={self.state!r} "
            f"direction={self.direction!r}>"
        )
