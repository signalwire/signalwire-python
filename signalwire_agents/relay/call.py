"""Call object — represents a live RELAY call with command methods."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Callable, Coroutine, Optional, TYPE_CHECKING

from signalwire_agents.core.logging_config import get_logger

from .constants import (
    CALL_STATE_ENDED,
    EVENT_CALL_PLAY,
    EVENT_CALL_RECORD,
    EVENT_CALL_DETECT,
    EVENT_CALL_STATE,
    PLAY_STATE_FINISHED,
    PLAY_STATE_ERROR,
    RECORD_STATE_FINISHED,
    RECORD_STATE_NO_INPUT,
)
from .event import RelayEvent, parse_event

if TYPE_CHECKING:
    from .client import RelayClient

logger = get_logger("relay_call")

EventHandler = Callable[[RelayEvent], Coroutine[Any, Any, None] | None]


class Action:
    """Base class for async action handles (play, record, detect, etc.).

    Holds a control_id and back-reference to the Call. Resolves when the
    server sends a terminal event for this control_id.
    """

    def __init__(self, call: "Call", control_id: str, terminal_event: str,
                 terminal_states: tuple[str, ...]):
        self.call = call
        self.control_id = control_id
        self._terminal_event = terminal_event
        self._terminal_states = terminal_states
        self._done: asyncio.Future[RelayEvent] = asyncio.get_running_loop().create_future()
        self.result: Optional[RelayEvent] = None
        self.completed = False

    def _check_event(self, event: RelayEvent) -> None:
        """Called by Call when an event matches our control_id."""
        state = event.params.get("state", "")
        if state in self._terminal_states and not self._done.done():
            self.result = event
            self.completed = True
            self._done.set_result(event)

    async def wait(self, timeout: Optional[float] = None) -> RelayEvent:
        """Wait for the action to complete. Returns the terminal event."""
        if timeout is not None:
            return await asyncio.wait_for(self._done, timeout=timeout)
        return await self._done

    @property
    def is_done(self) -> bool:
        return self._done.done()


class PlayAction(Action):
    """Handle for an active play operation."""

    def __init__(self, call: "Call", control_id: str):
        super().__init__(call, control_id, EVENT_CALL_PLAY,
                         (PLAY_STATE_FINISHED, PLAY_STATE_ERROR))

    async def stop(self) -> dict:
        return await self.call._execute("play.stop", {"control_id": self.control_id})

    async def pause(self) -> dict:
        return await self.call._execute("play.pause", {"control_id": self.control_id})

    async def resume(self) -> dict:
        return await self.call._execute("play.resume", {"control_id": self.control_id})

    async def volume(self, volume: float) -> dict:
        return await self.call._execute("play.volume", {
            "control_id": self.control_id, "volume": volume,
        })


class RecordAction(Action):
    """Handle for an active record operation."""

    def __init__(self, call: "Call", control_id: str):
        super().__init__(call, control_id, EVENT_CALL_RECORD,
                         (RECORD_STATE_FINISHED, RECORD_STATE_NO_INPUT))

    async def stop(self) -> dict:
        return await self.call._execute("record.stop", {"control_id": self.control_id})

    async def pause(self, behavior: Optional[str] = None) -> dict:
        params: dict[str, Any] = {"control_id": self.control_id}
        if behavior:
            params["behavior"] = behavior
        return await self.call._execute("record.pause", params)

    async def resume(self) -> dict:
        return await self.call._execute("record.resume", {"control_id": self.control_id})


class DetectAction(Action):
    """Handle for an active detect operation."""

    def __init__(self, call: "Call", control_id: str):
        # Detect events don't have a simple "finished" state — they keep
        # delivering results until stopped or timed out.  We treat any event
        # with "event" field as terminal for wait() (first result).
        super().__init__(call, control_id, EVENT_CALL_DETECT, ("finished", "error"))

    def _check_event(self, event: RelayEvent) -> None:
        # Detect delivers results continuously. Resolve on first result or
        # when finished/error.
        detect = event.params.get("detect", {})
        state = event.params.get("state", "")
        if (detect or state in self._terminal_states) and not self._done.done():
            self.result = event
            self.completed = True
            self._done.set_result(event)

    async def stop(self) -> dict:
        return await self.call._execute("detect.stop", {"control_id": self.control_id})


class CollectAction(Action):
    """Handle for play_and_collect."""

    def __init__(self, call: "Call", control_id: str):
        super().__init__(call, control_id, "calling.call.collect",
                         ("finished", "error", "no_input", "no_match"))

    def _check_event(self, event: RelayEvent) -> None:
        # play_and_collect shares a control_id across play and collect
        # phases.  Only resolve on collect events, not play events.
        if event.event_type != "calling.call.collect":
            return
        result = event.params.get("result", {})
        if result and not self._done.done():
            self.result = event
            self.completed = True
            self._done.set_result(event)
        else:
            super()._check_event(event)

    async def stop(self) -> dict:
        return await self.call._execute("play_and_collect.stop",
                                        {"control_id": self.control_id})

    async def volume(self, volume: float) -> dict:
        return await self.call._execute("play_and_collect.volume", {
            "control_id": self.control_id, "volume": volume,
        })


class Call:
    """Represents a live RELAY call.

    Created by RelayClient on inbound ``calling.call.receive`` events or
    outbound ``dial``/``begin`` responses.
    """

    def __init__(
        self,
        client: "RelayClient",
        call_id: str,
        node_id: str,
        project_id: str,
        context: str,
        *,
        tag: str = "",
        direction: str = "",
        device: Optional[dict[str, Any]] = None,
        state: str = "",
        segment_id: str = "",
    ):
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
        self._ended: asyncio.Future[RelayEvent] = asyncio.get_running_loop().create_future()

    # ------------------------------------------------------------------
    # Internal RPC primitive
    # ------------------------------------------------------------------

    async def _execute(self, method: str, extra_params: Optional[dict[str, Any]] = None) -> dict:
        """Send a ``calling.<method>`` JSON-RPC request for this call.

        The outer JSON-RPC method is ``"calling.<method>"`` (e.g.
        ``"calling.answer"``) with ``node_id`` and ``call_id`` in params.
        """
        rpc_method = f"calling.{method}"
        params: dict[str, Any] = {
            "node_id": self.node_id,
            "call_id": self.call_id,
        }
        if extra_params:
            params.update(extra_params)
        return await self._client.execute(rpc_method, params)

    # ------------------------------------------------------------------
    # Event plumbing
    # ------------------------------------------------------------------

    def on(self, event_type: str, handler: EventHandler) -> None:
        """Register an event listener for this call."""
        self._listeners.setdefault(event_type, []).append(handler)

    async def _dispatch_event(self, payload: dict[str, Any]) -> None:
        """Called by RelayClient when an event arrives for this call."""
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
                    asyncio.ensure_future(result)
            except Exception:
                logger.exception("Error in event handler for %s", event_type)

    async def wait_for(
        self,
        event_type: str,
        predicate: Optional[Callable[[RelayEvent], bool]] = None,
        timeout: Optional[float] = None,
    ) -> RelayEvent:
        """Wait for a specific event, optionally filtered by predicate."""
        future: asyncio.Future[RelayEvent] = asyncio.get_running_loop().create_future()

        def _handler(event: RelayEvent) -> None:
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
                try:
                    self._listeners[event_type].remove(_handler)
                except ValueError:
                    pass

    async def wait_for_ended(self, timeout: Optional[float] = None) -> RelayEvent:
        """Wait for the call to reach the ended state."""
        if timeout is not None:
            return await asyncio.wait_for(self._ended, timeout=timeout)
        return await self._ended

    # ------------------------------------------------------------------
    # Action helper
    # ------------------------------------------------------------------

    async def _start_action(self, action: Action, method: str, params: dict[str, Any]) -> Action:
        """Register an action, execute the RPC, and clean up on failure.

        If _execute raises, the action is removed from _actions and its
        Future is rejected so callers of action.wait() get the error
        instead of hanging forever.
        """
        if self.state == CALL_STATE_ENDED:
            raise RuntimeError("Cannot start action on an ended call")
        self._actions[action.control_id] = action
        try:
            await self._execute(method, params)
        except Exception as exc:
            self._actions.pop(action.control_id, None)
            if not action._done.done():
                action._done.set_exception(exc)
            raise
        return action

    # ------------------------------------------------------------------
    # Call lifecycle methods
    # ------------------------------------------------------------------

    async def answer(self, **kwargs: Any) -> dict:
        """Answer an inbound call."""
        return await self._execute("answer", kwargs or None)

    async def hangup(self, reason: str = "hangup") -> dict:
        """End/hang up the call."""
        return await self._execute("end", {"reason": reason})

    async def pass_(self) -> dict:
        """Decline control of an inbound call, returning it to routing."""
        return await self._execute("pass")

    # ------------------------------------------------------------------
    # Audio playback
    # ------------------------------------------------------------------

    async def play(
        self,
        media: list[dict[str, Any]],
        *,
        volume: Optional[float] = None,
        direction: Optional[str] = None,
        loop: Optional[int] = None,
        control_id: Optional[str] = None,
        **kwargs: Any,
    ) -> PlayAction:
        """Play audio content. Returns a PlayAction for stop/pause/resume/wait."""
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
        return await self._start_action(action, "play", params)

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    async def record(
        self,
        audio: Optional[dict[str, Any]] = None,
        *,
        control_id: Optional[str] = None,
        **kwargs: Any,
    ) -> RecordAction:
        """Record audio from the call. Returns a RecordAction."""
        cid = control_id or str(uuid.uuid4())
        record_obj = {"audio": audio or {}}
        params: dict[str, Any] = {"control_id": cid, "record": record_obj}
        params.update(kwargs)
        action = RecordAction(self, cid)
        return await self._start_action(action, "record", params)

    # ------------------------------------------------------------------
    # Input collection
    # ------------------------------------------------------------------

    async def play_and_collect(
        self,
        media: list[dict[str, Any]],
        collect: dict[str, Any],
        *,
        volume: Optional[float] = None,
        control_id: Optional[str] = None,
        **kwargs: Any,
    ) -> CollectAction:
        """Play audio and collect digit/speech input."""
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
        return await self._start_action(action, "play_and_collect", params)

    # ------------------------------------------------------------------
    # Bridging & connectivity
    # ------------------------------------------------------------------

    async def connect(
        self,
        devices: list[list[dict[str, Any]]],
        *,
        ringback: Optional[list[dict[str, Any]]] = None,
        control_id: Optional[str] = None,
        **kwargs: Any,
    ) -> dict:
        """Bridge the call to one or more destinations."""
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {"control_id": cid, "devices": devices}
        if ringback is not None:
            params["ringback"] = ringback
        params.update(kwargs)
        return await self._execute("connect", params)

    async def disconnect(self) -> dict:
        """Disconnect (unbridge) a connected call."""
        return await self._execute("disconnect")

    # ------------------------------------------------------------------
    # DTMF
    # ------------------------------------------------------------------

    async def send_digits(
        self,
        digits: str,
        *,
        control_id: Optional[str] = None,
    ) -> dict:
        """Send DTMF digits on the call."""
        cid = control_id or str(uuid.uuid4())
        return await self._execute("send_digits", {
            "control_id": cid, "digits": digits,
        })

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    async def detect(
        self,
        detect: dict[str, Any],
        *,
        timeout: Optional[float] = None,
        control_id: Optional[str] = None,
        **kwargs: Any,
    ) -> DetectAction:
        """Start audio detection (machine, fax, digit). Returns a DetectAction."""
        cid = control_id or str(uuid.uuid4())
        params: dict[str, Any] = {"control_id": cid, "detect": detect}
        if timeout is not None:
            params["timeout"] = timeout
        params.update(kwargs)
        action = DetectAction(self, cid)
        return await self._start_action(action, "detect", params)

    def __repr__(self) -> str:
        return (
            f"<Call id={self.call_id!r} state={self.state!r} "
            f"direction={self.direction!r}>"
        )
