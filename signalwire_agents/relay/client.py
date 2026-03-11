"""RelayClient — WebSocket + JSON-RPC 2.0 protocol + event dispatch.

One instance = one persistent WebSocket connection to SignalWire RELAY.
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from typing import Any, Callable, Coroutine, Optional

import websockets
import websockets.exceptions

from signalwire_agents.core.logging_config import get_logger

from .call import Call
from .constants import (
    AGENT_STRING,
    PROTOCOL_VERSION,
    DEFAULT_RELAY_HOST,
    EVENT_CALL_RECEIVE,
    METHOD_SIGNALWIRE_CONNECT,
    METHOD_SIGNALWIRE_EVENT,
    METHOD_SIGNALWIRE_PING,
    RECONNECT_BACKOFF_FACTOR,
    RECONNECT_MAX_DELAY,
    RECONNECT_MIN_DELAY,
)
from .event import parse_event

logger = get_logger("relay_client")

CallHandler = Callable[["Call"], Coroutine[Any, Any, None]]


class RelayClient:
    """Manages a WebSocket connection to SignalWire RELAY.

    Usage::

        client = RelayClient(project="...", token="...", contexts=["default"])

        @client.on_call
        async def handle(call):
            await call.answer()
            await call.hangup()

        client.run()
    """

    def __init__(
        self,
        project: Optional[str] = None,
        token: Optional[str] = None,
        host: Optional[str] = None,
        contexts: Optional[list[str]] = None,
    ):
        self.project = project or os.environ.get("SIGNALWIRE_PROJECT_ID", "")
        self.token = token or os.environ.get("SIGNALWIRE_API_TOKEN", "")
        self.host = host or os.environ.get("SIGNALWIRE_SPACE", DEFAULT_RELAY_HOST)
        self.contexts = contexts or []

        if not self.project or not self.token:
            raise ValueError(
                "project and token are required. Pass them directly or set "
                "SIGNALWIRE_PROJECT_ID / SIGNALWIRE_API_TOKEN env vars."
            )

        # Internal state
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._pending: dict[str, asyncio.Future[dict]] = {}
        self._calls: dict[str, Call] = {}
        self._on_call_handler: Optional[CallHandler] = None
        self._connected = False
        self._closing = False
        self._reconnect_delay = RECONNECT_MIN_DELAY
        self._recv_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
        # Server-assigned protocol string from signalwire.connect response.
        # Used as the ``protocol`` field in all subsequent calling commands
        # and sent back on reconnect to resume the same session.
        self._relay_protocol: str = ""
        self._identity: str = ""

    @property
    def relay_protocol(self) -> str:
        """Server-assigned protocol string from the connect response."""
        return self._relay_protocol

    # ------------------------------------------------------------------
    # Decorator for inbound call handler
    # ------------------------------------------------------------------

    def on_call(self, handler: CallHandler) -> CallHandler:
        """Register the inbound call handler (decorator)."""
        self._on_call_handler = handler
        return handler

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Connect to RELAY and authenticate."""
        uri = f"wss://{self.host}"
        logger.info("Connecting to %s", uri)

        self._ws = await websockets.connect(uri, ping_interval=None, max_size=None)
        self._connected = True
        self._reconnect_delay = RECONNECT_MIN_DELAY

        # Start receive loop BEFORE authenticate so responses can be read
        self._recv_task = asyncio.ensure_future(self._recv_loop())

        # Authenticate
        await self._authenticate()

        # Start ping loop after successful auth
        self._ping_task = asyncio.ensure_future(self._ping_loop())

        logger.info("Connected and authenticated to RELAY")

    async def _authenticate(self) -> None:
        """Send signalwire.connect and wait for the response.

        The server returns a ``protocol`` string that must be used as
        the ``protocol`` field in all subsequent ``calling.call`` commands.
        On reconnect the previously-received protocol is sent back to
        resume the same session.
        """
        params: dict[str, Any] = {
            "version": PROTOCOL_VERSION,
            "agent": AGENT_STRING,
            "authentication": {
                "project": self.project,
                "token": self.token,
            },
        }
        if self.contexts:
            params["contexts"] = self.contexts
        # Re-send the protocol on reconnect to resume the session
        if self._relay_protocol:
            params["protocol"] = self._relay_protocol

        result = await self._send_request(METHOD_SIGNALWIRE_CONNECT, params)

        # Capture server-assigned protocol and identity
        self._relay_protocol = result.get("protocol", self._relay_protocol)
        self._identity = result.get("identity", self._identity)
        logger.debug("Auth response: protocol=%s identity=%s",
                     self._relay_protocol, self._identity)

    async def disconnect(self) -> None:
        """Cleanly close the connection."""
        self._closing = True
        self._connected = False

        if self._ping_task:
            self._ping_task.cancel()
            self._ping_task = None

        if self._recv_task:
            self._recv_task.cancel()
            self._recv_task = None

        if self._ws:
            await self._ws.close()
            self._ws = None

        # Cancel any pending request futures
        for fut in self._pending.values():
            if not fut.done():
                fut.cancel()
        self._pending.clear()

        logger.info("Disconnected from RELAY")

    # ------------------------------------------------------------------
    # Public RPC interface
    # ------------------------------------------------------------------

    async def execute(self, method: str, params: dict[str, Any]) -> dict:
        """Send a JSON-RPC request and await the response.

        For calling methods, ``method`` is the full name (e.g.
        ``"calling.answer"``, ``"calling.play"``) with ``node_id``
        and ``call_id`` in ``params``.
        """
        return await self._send_request(method, params)

    async def dial(
        self,
        devices: list[list[dict[str, Any]]],
        *,
        tag: Optional[str] = None,
        max_duration: Optional[int] = None,
    ) -> Call:
        """Initiate an outbound call using dial. Returns a Call object."""
        params: dict[str, Any] = {
            "tag": tag or str(uuid.uuid4()),
            "devices": devices,
        }
        if max_duration:
            params["max_duration"] = max_duration

        result = await self.execute("calling.dial", params)

        # Create a Call object from the response
        call_id = result.get("call_id", "")
        node_id = result.get("node_id", "")
        call = Call(
            client=self,
            call_id=call_id,
            node_id=node_id,
            project_id=self.project,
            context=self._relay_protocol,
            tag=tag or "",
            direction="outbound",
            state=result.get("call_state", "created"),
        )
        self._calls[call_id] = call
        return call

    # ------------------------------------------------------------------
    # Run / event loop entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Blocking entry point — runs the event loop until interrupted."""
        asyncio.run(self._run_forever())

    async def _run_forever(self) -> None:
        """Connect and maintain the connection with auto-reconnect."""
        while not self._closing:
            try:
                await self.connect()
                # Block until the recv loop exits (connection lost)
                if self._recv_task:
                    await self._recv_task
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Connection error")

            if self._closing:
                break

            # Auto-reconnect with exponential backoff
            logger.info("Reconnecting in %.1fs ...", self._reconnect_delay)
            await asyncio.sleep(self._reconnect_delay)
            self._reconnect_delay = min(
                self._reconnect_delay * RECONNECT_BACKOFF_FACTOR,
                RECONNECT_MAX_DELAY,
            )

    # ------------------------------------------------------------------
    # Internal: send / receive
    # ------------------------------------------------------------------

    async def _send_request(self, method: str, params: dict[str, Any]) -> dict:
        """Send a JSON-RPC 2.0 request and return the result."""
        if not self._ws:
            raise RuntimeError("Not connected to RELAY")

        req_id = str(uuid.uuid4())
        message = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params,
        }

        future: asyncio.Future[dict] = asyncio.get_event_loop().create_future()
        self._pending[req_id] = future

        raw = json.dumps(message)
        logger.debug(">> %s", raw)
        await self._ws.send(raw)

        try:
            return await future
        finally:
            self._pending.pop(req_id, None)

    async def _recv_loop(self) -> None:
        """Read messages from the WebSocket until closed."""
        try:
            async for raw in self._ws:
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON received: %s", raw[:200])
                    continue

                logger.debug("<< %s", str(raw)[:500])
                await self._handle_message(msg)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Error in recv loop")
        finally:
            self._connected = False

    async def _handle_message(self, msg: dict[str, Any]) -> None:
        """Route an incoming JSON-RPC message."""
        # JSON-RPC level error (e.g. method not found)
        if "id" in msg and "error" in msg:
            req_id = msg["id"]
            future = self._pending.get(req_id)
            if future and not future.done():
                error = msg["error"]
                future.set_exception(
                    RelayError(error.get("code", -1), error.get("message", "Unknown error"))
                )
            return

        # Response to a pending request
        if "id" in msg and "result" in msg:
            req_id = msg["id"]
            future = self._pending.get(req_id)
            if future and not future.done():
                result = msg["result"]
                # Calling API returns code/message inside result;
                # any code other than "200" is an error.
                code = result.get("code")
                if code is not None and str(code) != "200":
                    future.set_exception(
                        RelayError(int(code), result.get("message", "Unknown error"))
                    )
                else:
                    future.set_result(result)
            return

        # Server-initiated method call (event or ping)
        method = msg.get("method", "")
        params = msg.get("params", {})

        if method == METHOD_SIGNALWIRE_EVENT:
            await self._handle_event(params)
        elif method == METHOD_SIGNALWIRE_PING:
            # Respond to server pings
            if "id" in msg:
                await self._send_pong(msg["id"])

    async def _handle_event(self, payload: dict[str, Any]) -> None:
        """Dispatch a signalwire.event to the appropriate Call."""
        event_type = payload.get("event_type", "")
        event_params = payload.get("params", {})
        call_id = event_params.get("call_id", "")

        logger.debug("Event: %s call_id=%s", event_type, call_id)

        # Inbound call
        if event_type == EVENT_CALL_RECEIVE:
            await self._handle_inbound_call(payload)
            return

        # Route to existing Call
        if call_id and call_id in self._calls:
            await self._calls[call_id]._dispatch_event(payload)

            # Clean up ended calls
            call = self._calls.get(call_id)
            if call and call.state == "ended":
                self._calls.pop(call_id, None)

    async def _handle_inbound_call(self, payload: dict[str, Any]) -> None:
        """Create a Call object for an inbound call and invoke the handler."""
        params = payload.get("params", {})
        call_id = params.get("call_id", "")

        call = Call(
            client=self,
            call_id=call_id,
            node_id=params.get("node_id", ""),
            project_id=params.get("project_id", self.project),
            context=self._relay_protocol or params.get("context", params.get("protocol", "")),
            tag=params.get("tag", ""),
            direction=params.get("direction", "inbound"),
            device=params.get("device"),
            state=params.get("call_state", "created"),
            segment_id=params.get("segment_id", ""),
        )
        self._calls[call_id] = call

        if self._on_call_handler:
            asyncio.ensure_future(self._safe_call_handler(call))
        else:
            logger.warning("Inbound call %s but no on_call handler registered", call_id)

    async def _safe_call_handler(self, call: Call) -> None:
        """Run the on_call handler as a free task so the recv loop is never blocked."""
        try:
            await self._on_call_handler(call)
        except Exception:
            logger.exception("Error in on_call handler for %s", call.call_id)

    async def _send_pong(self, req_id: str) -> None:
        """Respond to a server ping."""
        if not self._ws:
            return
        msg = json.dumps({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {},
        })
        await self._ws.send(msg)

    async def _ping_loop(self) -> None:
        """Periodically send pings to keep the connection alive."""
        try:
            while self._connected and self._ws:
                await asyncio.sleep(30)
                if not self._connected or not self._ws:
                    break
                try:
                    await self._send_request(METHOD_SIGNALWIRE_PING, {})
                except Exception:
                    logger.debug("Ping failed, connection may be lost")
                    break
        except asyncio.CancelledError:
            pass


class RelayError(Exception):
    """Error returned by the RELAY server."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"RELAY error {code}: {message}")
