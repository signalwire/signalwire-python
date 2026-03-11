"""RelayClient — WebSocket + JSON-RPC 2.0 protocol + event dispatch.

One instance = one persistent WebSocket connection to SignalWire RELAY.

Architecture notes (mirrors the JS SDK):
- JSON-RPC requests are tracked by ``id`` in ``_pending``; responses resolve
  the corresponding Future.
- ``signalwire.event`` messages are acknowledged back to the server (event ACK)
  and then dispatched by ``event_type`` → Call object → Action object.
- Each Action registers with a ``control_id`` and listens for its own
  event_type (e.g. ``calling.call.play``).  Actions filter events by
  ``control_id`` so multiple concurrent actions on the same call work.
- Result code checking accepts any 2xx (matching the JS SDK regex /^2[0-9][0-9]$/).
  ``signalwire.connect`` responses skip code checking entirely.
- Execute has a configurable timeout (default 10s) to detect half-open connections.
- Requests made while disconnected are queued and flushed after re-auth.
- Server pings are tracked; if no ping arrives within the check interval the
  connection is assumed half-open and force-closed for reconnect.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
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
    METHOD_SIGNALWIRE_DISCONNECT,
    METHOD_SIGNALWIRE_EVENT,
    METHOD_SIGNALWIRE_PING,
    RECONNECT_BACKOFF_FACTOR,
    RECONNECT_MAX_DELAY,
    RECONNECT_MIN_DELAY,
)
logger = get_logger("relay_client")

CallHandler = Callable[["Call"], Coroutine[Any, Any, None]]

# Any 2xx code is considered success (matches JS SDK: /^2[0-9][0-9]$/)
_SUCCESS_CODE_RE = re.compile(r"^2\d{2}$")

# Default timeout for execute() requests (seconds)
_EXECUTE_TIMEOUT = 10.0

# If no server ping arrives within this interval, send a client ping as probe
_CHECK_PING_DELAY = 15.0

# Client-side ping interval (sends our own pings between server pings)
_CLIENT_PING_INTERVAL = 30.0

# Max consecutive ping failures before force-closing
_MAX_PING_FAILURES = 3

# Safety limits to prevent unbounded memory growth from malicious/buggy servers
_MAX_ACTIVE_CALLS = 1000
_MAX_QUEUE_SIZE = 500

# Max concurrent RelayClient connections per process (env: RELAY_MAX_CONNECTIONS)
try:
    _MAX_CONNECTIONS = max(1, int(os.environ.get("RELAY_MAX_CONNECTIONS", "1")))
except ValueError:
    _MAX_CONNECTIONS = 1

# Process-wide tracking of active RelayClient connections
_active_clients: set[int] = set()


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

        # Validate host to prevent SSRF / header injection
        if any(c in self.host for c in ('@', '/', '?', '\r', '\n', ' ')):
            raise ValueError(
                f"Invalid host: {self.host!r}. Must be a hostname, not a URL."
            )

        # Internal state
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._pending: dict[str, asyncio.Future[dict]] = {}
        # Track the method for each pending request (for code-checking decisions)
        self._pending_methods: dict[str, str] = {}
        self._calls: dict[str, Call] = {}
        self._on_call_handler: Optional[CallHandler] = None
        self._connected = False
        self._closing = False
        self._reconnect_delay = RECONNECT_MIN_DELAY
        self._recv_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
        # Server-assigned protocol string from signalwire.connect response.
        # Sent back on reconnect to resume the same session.
        self._relay_protocol: str = ""
        self._identity: str = ""
        # Half-open detection: reset on every server ping; fires if no ping
        # arrives within _CHECK_PING_DELAY seconds.
        self._check_ping_handle: Optional[asyncio.TimerHandle] = None
        # Track consecutive client ping failures for exponential backoff
        self._ping_failures: int = 0
        # Queue for requests made while disconnected/reconnecting
        self._execute_queue: list[tuple[dict, asyncio.Future[dict]]] = []

    def __del__(self) -> None:
        _active_clients.discard(id(self))

    async def __aenter__(self) -> "RelayClient":
        await self.connect()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.disconnect()

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
        # Guard against connection leaks — enforce per-process limit
        # (don't count ourselves if we're already tracked, i.e. reconnecting)
        other_count = len(_active_clients - {id(self)})
        if other_count >= _MAX_CONNECTIONS:
            raise RuntimeError(
                f"RelayClient connection limit reached ({_MAX_CONNECTIONS}). "
                f"There are already {other_count} active connection(s) in this process. "
                f"Call disconnect() on existing clients first, or set "
                f"RELAY_MAX_CONNECTIONS env var to allow more."
            )
        _active_clients.add(id(self))

        uri = f"wss://{self.host}"
        logger.info("Connecting to %s", uri)

        self._ws = await websockets.connect(uri, ping_interval=None, max_size=10 * 1024 * 1024)
        self._connected = True
        self._reconnect_delay = RECONNECT_MIN_DELAY

        # Start receive loop BEFORE authenticate so responses can be read
        self._recv_task = asyncio.ensure_future(self._recv_loop())

        # Authenticate
        await self._authenticate()

        # Start client-side ping loop for resilience
        self._ping_failures = 0
        self._ping_task = asyncio.ensure_future(self._ping_loop())

        # Flush any requests that were queued during reconnect
        self._flush_execute_queue()

        logger.info("Connected and authenticated to RELAY")

    async def _authenticate(self) -> None:
        """Send signalwire.connect and wait for the response.

        The server returns a ``protocol`` string that must be used as
        the ``protocol`` field in all subsequent calling commands.
        On reconnect the previously-received protocol is sent back to
        resume the same session.
        """
        params: dict[str, Any] = {
            "version": PROTOCOL_VERSION,
            "agent": AGENT_STRING,
            "event_acks": True,
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
        _active_clients.discard(id(self))

        self._cancel_check_ping()

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

        # Cancel any queued requests
        for _, fut in self._execute_queue:
            if not fut.done():
                fut.cancel()
        self._execute_queue.clear()

        logger.info("Disconnected from RELAY")

    # ------------------------------------------------------------------
    # Public RPC interface
    # ------------------------------------------------------------------

    async def execute(self, method: str, params: dict[str, Any]) -> dict:
        """Send a JSON-RPC request and await the response.

        For calling methods, ``method`` is the full name (e.g.
        ``"calling.answer"``, ``"calling.play"``) with ``node_id``
        and ``call_id`` in ``params``.

        If the connection is not ready, the request is queued and sent
        after re-authentication completes.
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

            self._cancel_check_ping()

            # Reject all pending requests — connection is lost
            self._clear_pending_requests()

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
        """Send a JSON-RPC 2.0 request and return the result.

        If not connected, queues the request for later delivery.
        Applies a timeout to detect half-open connections.
        """
        req_id = str(uuid.uuid4())
        message: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params,
        }

        loop = asyncio.get_running_loop()
        future: asyncio.Future[dict] = loop.create_future()
        self._pending[req_id] = future
        self._pending_methods[req_id] = method

        try:
            if not self._ws or not self._connected:
                # Queue for delivery after reconnect (like JS executeQueue)
                if len(self._execute_queue) >= _MAX_QUEUE_SIZE:
                    raise RelayError(-1, "Execute queue full — too many requests while disconnected")
                self._execute_queue.append((message, future))
                logger.debug("Request queued (not connected): %s", method)
            else:
                raw = json.dumps(message)
                logger.debug(">> %s id=%s", method, req_id)
                await self._ws.send(raw)

            return await asyncio.wait_for(future, timeout=_EXECUTE_TIMEOUT)
        except asyncio.TimeoutError:
            logger.error("Request timeout: %s %s", method, req_id)
            # Timeout may indicate a half-open connection — force reconnect
            if method != METHOD_SIGNALWIRE_CONNECT:
                self._force_close()
            raise RelayError(-1, f"Request timeout for {method}")
        finally:
            self._pending.pop(req_id, None)
            self._pending_methods.pop(req_id, None)

    def _flush_execute_queue(self) -> None:
        """Send any requests that were queued while disconnected."""
        if not self._execute_queue or not self._ws:
            return
        queued = list(self._execute_queue)
        self._execute_queue.clear()
        logger.debug("Flushing %d queued requests", len(queued))
        for message, future in queued:
            if future.done():
                continue
            raw = json.dumps(message)
            logger.debug(">> (queued) %s id=%s", message.get("method", "?"), message.get("id", "?"))
            asyncio.ensure_future(self._safe_send(raw, future))

    async def _safe_send(self, raw: str, future: asyncio.Future) -> None:
        """Send a queued message, rejecting its future on failure."""
        try:
            if self._ws:
                await self._ws.send(raw)
        except Exception as exc:
            if not future.done():
                future.set_exception(
                    RelayError(-1, f"Failed to send queued request: {exc}")
                )

    def _clear_pending_requests(self) -> None:
        """Reject all pending request futures (connection lost)."""
        for fut in self._pending.values():
            if not fut.done():
                fut.set_exception(
                    RelayError(-1, "Connection closed")
                )
        self._pending.clear()
        self._pending_methods.clear()

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
            self._cancel_check_ping()
            if self._ping_task:
                self._ping_task.cancel()
                self._ping_task = None

    async def _handle_message(self, msg: dict[str, Any]) -> None:
        """Route an incoming JSON-RPC message."""
        if not isinstance(msg, dict):
            logger.warning("Ignoring non-dict message")
            return

        # JSON-RPC level error (e.g. method not found)
        if "id" in msg and "error" in msg:
            req_id = msg["id"]
            future = self._pending.get(req_id)
            if future and not future.done():
                error = msg["error"]
                if not isinstance(error, dict):
                    error = {"code": -1, "message": str(error)[:512]}
                future.set_exception(
                    RelayError(error.get("code", -1), str(error.get("message", "Unknown error"))[:512])
                )
            else:
                logger.debug("Error response for unknown/expired request %s", req_id)
            return

        # Response to a pending request
        if "id" in msg and "result" in msg:
            req_id = msg["id"]
            future = self._pending.get(req_id)
            if future and not future.done():
                result = msg["result"]
                if not isinstance(result, dict):
                    future.set_result({"raw": result})
                    return
                # Look up the original request method to decide code-checking
                request_method = self._get_request_method(req_id)
                if request_method == METHOD_SIGNALWIRE_CONNECT:
                    # signalwire.connect: return raw result, no code checking
                    future.set_result(result)
                else:
                    # Calling API: result contains code/message; any 2xx is success
                    code = result.get("code")
                    code_str = str(code) if code is not None else None
                    if code_str is not None and not _SUCCESS_CODE_RE.match(code_str):
                        try:
                            int_code = int(code)
                        except (ValueError, TypeError):
                            int_code = -1
                        future.set_exception(
                            RelayError(int_code, str(result.get("message", "Unknown error"))[:512])
                        )
                    else:
                        future.set_result(result)
            else:
                logger.debug("Response for unknown/expired request %s", req_id)
            return

        # Server-initiated method call (event or ping)
        method = msg.get("method", "")
        params = msg.get("params", {})
        if not isinstance(params, dict):
            logger.warning("Ignoring message with non-dict params")
            return

        if method == METHOD_SIGNALWIRE_EVENT:
            # ACK the event back to the server (like JS _eventAcknowledgingHandler)
            if "id" in msg:
                await self._send_event_ack(msg["id"])
            await self._handle_event(params)
        elif method == METHOD_SIGNALWIRE_PING:
            # Reset the half-open detection timer
            self._reset_check_ping()
            if "id" in msg:
                await self._send_pong(msg["id"])
        elif method == METHOD_SIGNALWIRE_DISCONNECT:
            # Server is telling us to disconnect; respond with empty result
            # then let the server close the socket (reconnect will happen naturally)
            logger.info("Received signalwire.disconnect from server")
            if "id" in msg:
                await self._send_event_ack(msg["id"])
            # Don't set _closing — we want to reconnect after the server closes

    def _get_request_method(self, req_id: str) -> str:
        """Look up the original method for a pending request by ID.

        Used to skip code-checking for signalwire.connect responses.
        """
        return self._pending_methods.get(req_id, "")

    async def _handle_event(self, payload: dict[str, Any]) -> None:
        """Dispatch a signalwire.event to the appropriate Call."""
        event_type = payload.get("event_type", "")
        event_params = payload.get("params", {})
        call_id = event_params.get("call_id", "")

        if not event_type:
            logger.warning("Received event with empty event_type: %s", payload)
            return

        logger.debug("Event: %s call_id=%s", event_type, call_id)

        # Inbound call
        if event_type == EVENT_CALL_RECEIVE:
            await self._handle_inbound_call(payload)
            return

        # Route to existing Call
        call = self._calls.get(call_id) if call_id else None
        if call:
            await call._dispatch_event(payload)

            # Clean up ended calls
            if call.state == "ended":
                self._calls.pop(call_id, None)

    async def _handle_inbound_call(self, payload: dict[str, Any]) -> None:
        """Create a Call object for an inbound call and invoke the handler."""
        if len(self._calls) >= _MAX_ACTIVE_CALLS:
            logger.error("Max active calls (%d) reached, dropping inbound call", _MAX_ACTIVE_CALLS)
            return
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

    async def _send_event_ack(self, req_id: str) -> None:
        """Acknowledge a signalwire.event back to the server."""
        if not self._ws:
            return
        msg = json.dumps({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {},
        })
        await self._ws.send(msg)

    # ------------------------------------------------------------------
    # Client-side ping loop + half-open detection
    # ------------------------------------------------------------------

    async def _ping_loop(self) -> None:
        """Periodically send client pings for resilience.

        - Sends signalwire.ping every _CLIENT_PING_INTERVAL seconds.
        - On failure, retries with exponential backoff up to _MAX_PING_FAILURES.
        - After max failures, force-closes the connection for reconnect.
        - Server pings also reset the failure counter (see _handle_message).
        """
        try:
            while self._connected and self._ws:
                await asyncio.sleep(_CLIENT_PING_INTERVAL)
                if not self._connected or not self._ws:
                    break
                try:
                    await self._send_request(METHOD_SIGNALWIRE_PING, {})
                    # Success — reset failure counter
                    self._ping_failures = 0
                except Exception:
                    self._ping_failures += 1
                    backoff = min(
                        RECONNECT_MIN_DELAY * (RECONNECT_BACKOFF_FACTOR ** self._ping_failures),
                        RECONNECT_MAX_DELAY,
                    )
                    logger.warning(
                        "Client ping failed (%d/%d), backoff %.1fs",
                        self._ping_failures, _MAX_PING_FAILURES, backoff,
                    )
                    if self._ping_failures >= _MAX_PING_FAILURES:
                        logger.error("Max ping failures reached, forcing reconnect")
                        self._force_close()
                        break
                    # Wait the backoff period before retrying
                    await asyncio.sleep(backoff)
        except asyncio.CancelledError:
            pass

    def _reset_check_ping(self) -> None:
        """Reset the server-ping watchdog timer.

        Called when we receive a server ping — resets failure counter and
        restarts the watchdog that will probe if the server goes silent.
        """
        self._ping_failures = 0
        self._cancel_check_ping()
        loop = asyncio.get_running_loop()
        self._check_ping_handle = loop.call_later(
            _CHECK_PING_DELAY, self._on_check_ping_timeout
        )

    def _cancel_check_ping(self) -> None:
        if self._check_ping_handle:
            self._check_ping_handle.cancel()
            self._check_ping_handle = None

    def _on_check_ping_timeout(self) -> None:
        """No server ping received in time — send a client ping as probe.

        The client ping loop will handle failures with exponential backoff.
        This just logs; the ping loop does the actual probing.
        """
        logger.debug("No server ping received in %.1fs, client pings will probe",
                     _CHECK_PING_DELAY)

    def _force_close(self) -> None:
        """Force-close the WebSocket to trigger reconnect."""
        self._cancel_check_ping()
        self._connected = False
        if self._ping_task:
            self._ping_task.cancel()
            self._ping_task = None
        if self._ws:
            asyncio.ensure_future(self._ws.close())


class RelayError(Exception):
    """Error returned by the RELAY server."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"RELAY error {code}: {message}")
