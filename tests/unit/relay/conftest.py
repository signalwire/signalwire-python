"""Mock infrastructure and fixtures for RELAY client tests.

Two test backends coexist:

1. The legacy ``MockWebSocket`` / ``connected_client`` fixtures — a WebSocket
   transport double used by the RelayClient internal-mechanics unit tests
   (``test_client.py``, ``test_message.py``).  These mirror the frozen
   TypeScript reference's ``tests/relay/helpers.ts`` + ``RelayClient.test.ts`` /
   ``Message.test.ts``, which keep an in-memory ``MockWebSocket`` for the same
   resilience coverage (reconnect backoff, ping-failure backoff, recv-loop
   exception handling, queue overflow, force-close, half-open detection) that a
   conformant mock server can't reproduce — it would never emit a malformed
   frame or drop the socket on cue.  They mock the transport on purpose.

2. The ``signalwire_relay_client`` / ``mock_relay`` fixtures — back the SDK with
   a real WebSocket server provided by the ``mock_relay`` package
   (``porting-sdk/test_harness/mock_relay``).  The mock loads RELAY's JSON
   schemas (extracted from switchblade) and synthesizes schema-conformant
   responses.  Tests written against this fixture exercise the SDK's actual
   ``websockets`` transport and then assert on parsed SDK state and the mock's
   HTTP-exposed journal / scenario plumbing.

   This is the parity-grade backend and mirrors the frozen TypeScript reference
   harness ``tests/relay/mocktest.ts``: ONE shared mock server (probe-or-spawn,
   adjacency discovery), and a per-test ``_MockRelayHarness`` *view* scoped to
   the connected client's session so the whole RELAY suite is safe under
   ``pytest -n auto``.

   Isolation key: the connect handshake returns a server-assigned ``sessionid``
   (NO underscore — reading ``session_id`` instead would make scoping a silent
   no-op).  The SDK captures it into ``client._session_id``; when a test uses
   ``signalwire_relay_client`` the ``mock_relay`` view for the same test is
   scoped to that id, so its ``journal()``/``reset()`` and its
   ``push``/``inbound_call``/``arm_*``/``scenario_play`` only ever touch this
   test's session.  A test that builds its own client (e.g. the reconnect tests)
   uses a bare unscoped ``mock_relay`` and filters by a unique protocol value.

   Usage::

       async def test_dial_round_trip(signalwire_relay_client, mock_relay):
           call = await signalwire_relay_client.dial(...)
           j = mock_relay.journal_recv(method="calling.dial")
           assert j

The two backends are independent — a test may use either, but not both at once.
"""

from __future__ import annotations

import asyncio
import atexit
import json
import os
import socket
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Iterable, Iterator, Optional, cast
from unittest.mock import AsyncMock, patch
from urllib.parse import quote

import pytest
import pytest_asyncio
import websockets.exceptions

from signalwire.relay.client import RelayClient, _active_clients
from signalwire.relay.call import Call
from signalwire.relay.constants import METHOD_SIGNALWIRE_CONNECT


# ---------------------------------------------------------------------------
# Adjacency-based discovery for porting-sdk mock packages.
#
# Walk up to find ``../porting-sdk/test_harness/mock_relay/`` and prepend it to
# ``sys.path`` so ``import mock_relay`` / ``python -m mock_relay`` resolve
# without any pip install. Mirrors ``discoverPortingSdkPackage`` in the frozen
# TypeScript reference harness ``tests/relay/mocktest.ts``; the walk ignores
# ``$PORTING_SDK`` deliberately — the filesystem layout is the source of truth.
# ---------------------------------------------------------------------------


def _discover_mock_package(name: str) -> Optional[str]:
    """Return the ``../porting-sdk/test_harness/<name>/`` package root (prepended
    to ``sys.path``), or ``None`` when no adjacent ``porting-sdk`` is reachable."""
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        candidate = parent.parent / "porting-sdk" / "test_harness" / name
        if (candidate / name / "__init__.py").is_file():
            entry = str(candidate)
            if entry not in sys.path:
                sys.path.insert(0, entry)
            return entry
    return None


_RELAY_MOCK_PKG_DIR = _discover_mock_package("mock_relay")
_RELAY_MOCK_AVAILABLE = _RELAY_MOCK_PKG_DIR is not None


# ---------------------------------------------------------------------------
# Mock WebSocket  (legacy transport double — see module docstring backend #1)
# ---------------------------------------------------------------------------

class MockWebSocket:
    """Simulates websockets.WebSocketClientProtocol for unit tests.

    - recv is backed by an asyncio.Queue so tests can inject messages.
    - send captures outgoing messages (parsed as dicts) for assertions.
    """

    def __init__(self) -> None:
        self._recv_queue: asyncio.Queue[str | Exception] = asyncio.Queue()
        self.sent_messages: list[dict[str, Any]] = []
        self.closed = False
        self._close_event = asyncio.Event()

    # --- sending (client → server) ---

    async def send(self, raw: str) -> None:
        if self.closed:
            raise websockets.exceptions.ConnectionClosed(None, None)
        self.sent_messages.append(json.loads(raw))

    # --- receiving (server → client) ---

    async def recv(self) -> str:
        item = await self._recv_queue.get()
        if isinstance(item, Exception):
            raise item
        return item

    def __aiter__(self) -> MockWebSocket:
        return self

    async def __anext__(self) -> str:
        try:
            return await self.recv()
        except (websockets.exceptions.ConnectionClosed, StopAsyncIteration):
            raise StopAsyncIteration

    # --- test helpers ---

    def feed_message(self, msg: dict[str, Any]) -> None:
        """Inject a server message into the recv queue."""
        self._recv_queue.put_nowait(json.dumps(msg))

    def feed_close(self) -> None:
        """Inject a ConnectionClosed exception to end the recv loop."""
        self._recv_queue.put_nowait(
            websockets.exceptions.ConnectionClosed(None, None)
        )

    async def close(self) -> None:
        self.closed = True
        self._close_event.set()
        # Unblock any waiting recv
        self.feed_close()


class AutoAuthMockWebSocket(MockWebSocket):
    """MockWebSocket that auto-replies to signalwire.connect requests.

    Watches send() for a signalwire.connect request and immediately injects
    a matching success response into the recv queue.
    """

    def __init__(self, protocol: str = "test-protocol-abc123", auto_reply_all: bool = False) -> None:
        super().__init__()
        self.protocol = protocol
        self.auto_reply_all = auto_reply_all

    async def send(self, raw: str) -> None:
        await super().send(raw)
        msg = json.loads(raw)
        if msg.get("method") == METHOD_SIGNALWIRE_CONNECT:
            self.feed_message(make_jsonrpc_response(msg["id"], {
                "protocol": self.protocol,
                "identity": "test-identity",
            }))
        elif self.auto_reply_all and "id" in msg and "method" in msg:
            self.feed_message(make_jsonrpc_response(msg["id"], {
                "code": "200", "message": "OK",
            }))


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def make_jsonrpc_response(req_id: str, result: Any) -> dict[str, Any]:
    """Build a JSON-RPC 2.0 success response."""
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def make_jsonrpc_error(req_id: str, code: int, message: str) -> dict[str, Any]:
    """Build a JSON-RPC 2.0 error response."""
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def make_event(
    event_type: str,
    params: dict[str, Any] | None = None,
    msg_id: str | None = None,
) -> dict[str, Any]:
    """Build a signalwire.event server message."""
    return {
        "jsonrpc": "2.0",
        "id": msg_id or str(uuid.uuid4()),
        "method": "signalwire.event",
        "params": {
            "event_type": event_type,
            "params": params or {},
        },
    }


def make_server_ping(msg_id: str | None = None) -> dict[str, Any]:
    """Build a signalwire.ping server message."""
    return {
        "jsonrpc": "2.0",
        "id": msg_id or str(uuid.uuid4()),
        "method": "signalwire.ping",
        "params": {},
    }


def make_calling_response(
    req_id: str, code: str = "200", message: str = "OK", **extra: Any
) -> dict[str, Any]:
    """Build a calling API response (result with code field)."""
    result = {"code": code, "message": message}
    result.update(extra)
    return make_jsonrpc_response(req_id, result)


# ---------------------------------------------------------------------------
# Legacy fixtures (transport double)
# ---------------------------------------------------------------------------

@pytest.fixture
def relay_client() -> Iterator[RelayClient]:
    """Fresh RelayClient with test credentials.  Clears _active_clients."""
    _active_clients.clear()
    client = RelayClient(project="test-project", token="test-token")
    yield client
    _active_clients.clear()


@pytest_asyncio.fixture
async def connected_client() -> AsyncIterator[tuple[RelayClient, AutoAuthMockWebSocket]]:
    """A RelayClient that is connected via a mocked WebSocket.

    Yields ``(client, mock_ws)``.  Disconnects on teardown.
    """
    _active_clients.clear()
    mock_ws = AutoAuthMockWebSocket()

    with patch("signalwire.relay.client.websockets.connect",
               new_callable=AsyncMock, return_value=mock_ws):
        client = RelayClient(project="test-project", token="test-token")
        await client.connect()
        yield client, mock_ws
        if client._connected:
            await client.disconnect()

    _active_clients.clear()


@pytest.fixture
def make_call() -> Callable[..., Call]:
    """Factory that creates a Call object on a connected client."""

    def _factory(
        client: RelayClient,
        call_id: str = "call-1",
        node_id: str = "node-1",
        state: str = "created",
        direction: str = "inbound",
    ) -> Call:
        call = Call(
            client=client,
            call_id=call_id,
            node_id=node_id,
            project_id=client.project,
            context="test-ctx",
            direction=direction,
            state=state,
        )
        client._calls[call_id] = call
        return call

    return _factory


# ---------------------------------------------------------------------------
# Real mock-relay server — probe-or-spawn singleton (mirrors mocktest.ts)
# ---------------------------------------------------------------------------


# Per-process default for parallel RelayClient connections during tests. The
# SDK's _MAX_CONNECTIONS guard otherwise refuses a 2nd client in the same
# process; bumping it lets a single test create multiple clients (used by the
# reconnect-with-protocol-string tests).
os.environ.setdefault("RELAY_MAX_CONNECTIONS", "16")

_DEFAULT_WS_PORT = 8773
_STARTUP_TIMEOUT_S = 30.0
_PROBE_TIMEOUT_S = 2.0


def _resolve_ws_port() -> int:
    raw = os.environ.get("MOCK_RELAY_WS_PORT")
    if raw:
        try:
            p = int(raw)
            if p > 0:
                return p
        except ValueError:
            pass
    return _DEFAULT_WS_PORT


def _resolve_http_port(ws_port: int) -> int:
    raw = os.environ.get("MOCK_RELAY_HTTP_PORT")
    if raw:
        try:
            p = int(raw)
            if p > 0:
                return p
        except ValueError:
            pass
    # Default behavior of mock_relay: HTTP = WS + 1000.
    return ws_port + 1000


def _probe_health(http_url: str) -> bool:
    import requests
    try:
        resp = requests.get(f"{http_url}/__mock__/health", timeout=_PROBE_TIMEOUT_S)
        if resp.status_code != 200:
            return False
        return "schemas_loaded" in resp.json()
    except Exception:
        return False


class _SharedRelayServer:
    """Process-wide handle to the one shared mock_relay server (WS + HTTP)."""

    def __init__(self) -> None:
        self.http_url: Optional[str] = None
        self.ws_url: Optional[str] = None
        self.relay_host: Optional[str] = None
        self._child: Optional[subprocess.Popen[bytes]] = None
        self._lock = threading.Lock()
        self._error: Optional[str] = None

    def ensure(self) -> "_SharedRelayServer":
        with self._lock:
            if self.http_url is not None:
                return self
            if self._error is not None:
                pytest.skip(self._error)

            ws_port = _resolve_ws_port()
            http_port = _resolve_http_port(ws_port)
            http_url = f"http://127.0.0.1:{http_port}"
            ws_url = f"ws://127.0.0.1:{ws_port}"
            relay_host = f"127.0.0.1:{ws_port}"

            if _probe_health(http_url):
                self.http_url, self.ws_url, self.relay_host = http_url, ws_url, relay_host
                return self

            if not _RELAY_MOCK_AVAILABLE:
                self._error = (
                    "mock_relay not adjacent — clone porting-sdk next to signalwire-python"
                )
                pytest.skip(self._error)

            child_env = dict(os.environ)
            if _RELAY_MOCK_PKG_DIR:
                existing = child_env.get("PYTHONPATH", "")
                child_env["PYTHONPATH"] = (
                    f"{_RELAY_MOCK_PKG_DIR}{os.pathsep}{existing}"
                    if existing else _RELAY_MOCK_PKG_DIR
                )
            self._child = subprocess.Popen(
                [
                    sys.executable, "-m", "mock_relay",
                    "--host", "127.0.0.1",
                    "--ws-port", str(ws_port),
                    "--http-port", str(http_port),
                    "--log-level", "error",
                ],
                env=child_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            atexit.register(self._terminate)

            deadline = time.time() + _STARTUP_TIMEOUT_S
            while time.time() < deadline:
                if _probe_health(http_url):
                    self.http_url, self.ws_url, self.relay_host = http_url, ws_url, relay_host
                    return self
                time.sleep(0.1)

            self._terminate()
            self._error = (
                f"mock_relay did not become ready within {_STARTUP_TIMEOUT_S}s on "
                f"ws={ws_port} http={http_port} (clone porting-sdk next to "
                f"signalwire-python, or set MOCK_RELAY_WS_PORT to a pre-running instance)"
            )
            pytest.skip(self._error)

    def _terminate(self) -> None:
        child = self._child
        self._child = None
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except Exception:
                child.kill()


_SHARED_RELAY = _SharedRelayServer()


@dataclass
class _RelayJournalEntry:
    """Lightweight view of a single journal entry the mock server recorded.

    Mirrors the dict shape exposed at ``/__mock__/journal``.
    """

    timestamp: float
    direction: str  # "recv" | "send"
    method: str
    request_id: str
    frame: dict[str, Any]
    connection_id: str
    session_id: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "_RelayJournalEntry":
        return cls(
            timestamp=float(d.get("timestamp", 0.0)),
            direction=str(d.get("direction", "")),
            method=str(d.get("method", "")),
            request_id=str(d.get("request_id", "")),
            frame=d.get("frame") or {},
            connection_id=str(d.get("connection_id", "")),
            session_id=str(d.get("session_id", "")),
        )


class _MockRelayHarness:
    """Per-test view of the shared ``mock_relay`` server's HTTP control plane.

    When ``session_id`` is set (done automatically by ``signalwire_relay_client``
    from the connected client's ``_session_id``), journal reads and
    ``push``/``inbound_call``/``arm_*``/``scenario_play`` are scoped to that one
    session, so a test only ever sees / targets its own frames — making the
    shared mock safe under ``pytest -n auto``.  Left empty => global (unscoped),
    used by tests that build their own clients and filter by a unique value.
    """

    def __init__(self, http_url: str, ws_url: str, relay_host: str) -> None:
        import requests as _requests

        self.http_url = http_url
        self.ws_url = ws_url
        self.relay_host = relay_host
        self.session_id = ""
        self._requests = _requests

    # -- scoping helper ------------------------------------------------------

    def _session_query(self) -> str:
        return f"?session_id={quote(self.session_id, safe='')}" if self.session_id else ""

    # -- journal -------------------------------------------------------------

    def journal(self) -> list[_RelayJournalEntry]:
        """Every journaled frame for this session (or all when unscoped)."""
        resp = self._requests.get(
            f"{self.http_url}/__mock__/journal{self._session_query()}", timeout=5
        )
        resp.raise_for_status()
        return [_RelayJournalEntry.from_dict(d) for d in resp.json()]

    def journal_recv(
        self, *, method: Optional[str] = None
    ) -> list[_RelayJournalEntry]:
        """Return inbound (SDK→server) journal entries, optionally by method."""
        entries = [e for e in self.journal() if e.direction == "recv"]
        if method is not None:
            entries = [e for e in entries if e.method == method]
        return entries

    def journal_send(
        self, *, event_type: Optional[str] = None
    ) -> list[_RelayJournalEntry]:
        """Return server→SDK frames, optionally filtered by inner event_type."""
        entries = [e for e in self.journal() if e.direction == "send"]
        if event_type is None:
            return entries
        out = []
        for e in entries:
            params = e.frame.get("params") or {}
            if (
                e.frame.get("method") == "signalwire.event"
                and isinstance(params, dict)
                and params.get("event_type") == event_type
            ):
                out.append(e)
        return out

    def reset(self) -> None:
        """Clear journal + scenarios.

        A scoped harness leaves the shared state alone (it only reads its own
        session's entries, and a brand-new session starts empty — a global wipe
        would race a concurrent test).  Unscoped harnesses do the legacy global
        reset.
        """
        if self.session_id:
            return
        self._requests.post(f"{self.http_url}/__mock__/journal/reset", timeout=5)
        self._requests.post(f"{self.http_url}/__mock__/scenarios/reset", timeout=5)

    # -- scenario plumbing ---------------------------------------------------

    def arm_method(
        self, method: str, events: Iterable[dict[str, Any]]
    ) -> None:
        """Queue scripted post-RPC events for ``method`` (FIFO consume-once).

        Scoped to this session so a concurrent test can't consume the queue.
        """
        resp = self._requests.post(
            f"{self.http_url}/__mock__/scenarios/{method}{self._session_query()}",
            json=list(events),
            timeout=5,
        )
        resp.raise_for_status()

    def arm_dial(self, **kwargs: Any) -> None:
        """Queue a dial-dance scenario (winner state events + final dial event).

        Scoped to this session so a concurrent dial test can't consume it.
        """
        resp = self._requests.post(
            f"{self.http_url}/__mock__/scenarios/dial{self._session_query()}",
            json=kwargs,
            timeout=5,
        )
        resp.raise_for_status()

    # -- server-initiated pushes --------------------------------------------

    def push(
        self,
        frame: dict[str, Any],
        *,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Push a single ``signalwire.event`` (or other) frame to the SDK.

        Targets this harness's session by default (so a parallel test's client
        never receives it); an explicit ``session_id`` overrides, and an
        unscoped harness with no arg broadcasts (legacy single-threaded).
        """
        target = session_id or self.session_id
        url = f"{self.http_url}/__mock__/push"
        if target:
            url = f"{url}?session_id={quote(target, safe='')}"
        resp = self._requests.post(url, json={"frame": frame}, timeout=5)
        resp.raise_for_status()
        return cast("dict[str, Any]", resp.json())

    def inbound_call(
        self,
        *,
        call_id: Optional[str] = None,
        from_number: str = "+15551234567",
        to_number: str = "+15559876543",
        context: str = "default",
        auto_states: Optional[list[str]] = None,
        delay_ms: int = 50,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Inject an inbound call announcement.

        Targets this harness's session by default so the inbound-call sequence
        reaches only this test's client (an unscoped harness broadcasts, as
        before); an explicit ``session_id`` overrides.
        """
        body: dict[str, Any] = {
            "from_number": from_number,
            "to_number": to_number,
            "context": context,
            "auto_states": auto_states or ["created"],
            "delay_ms": delay_ms,
        }
        if call_id is not None:
            body["call_id"] = call_id
        target = session_id or self.session_id
        if target:
            body["session_id"] = target
        resp = self._requests.post(
            f"{self.http_url}/__mock__/inbound_call", json=body, timeout=5
        )
        resp.raise_for_status()
        return cast("dict[str, Any]", resp.json())

    def scenario_play(self, ops: list[dict[str, Any]]) -> dict[str, Any]:
        """Run a scripted timeline of pushes/sleeps/expect_recv on the server.

        When scoped, each push/expect_recv op is stamped with this session id
        (unless it already carries one), so the timeline targets only this
        test's client and expect_recv matches only this session's frames.
        """
        if self.session_id:
            ops = [self._scope_op(op) for op in ops]
        resp = self._requests.post(
            f"{self.http_url}/__mock__/scenario_play", json=ops, timeout=15
        )
        resp.raise_for_status()
        return cast("dict[str, Any]", resp.json())

    def _scope_op(self, op: dict[str, Any]) -> dict[str, Any]:
        """Inject this.session_id into a timeline op's push/expect_recv spec when
        the op doesn't already specify a session_id.  Leaves sleep ops alone."""
        out = dict(op)
        for key in ("push", "expect_recv"):
            spec = out.get(key)
            if isinstance(spec, dict) and "session_id" not in spec:
                out[key] = {**spec, "session_id": self.session_id}
        return out

    def sessions(self) -> list[dict[str, Any]]:
        """List active WebSocket session metadata."""
        resp = self._requests.get(f"{self.http_url}/__mock__/sessions", timeout=5)
        resp.raise_for_status()
        return cast("list[dict[str, Any]]", resp.json().get("sessions", []))


@pytest.fixture
def mock_relay() -> _MockRelayHarness:
    """Test-facing harness around the shared mock-relay server (unscoped view).

    Used directly by tests that build their own client(s).  When a test also
    uses ``signalwire_relay_client``, that fixture scopes THIS same harness
    object to the connected client's session id.
    """
    shared = _SHARED_RELAY.ensure()
    # ``ensure()`` guarantees these are populated (or skips), so they are non-None.
    return _MockRelayHarness(
        cast(str, shared.http_url),
        cast(str, shared.ws_url),
        cast(str, shared.relay_host),
    )


def _ws_redirect_to_mock(shared: "_SharedRelayServer") -> Any:
    """Build the websockets.connect override that points the SDK at the mock.

    The SDK builds its URI as ``f"wss://{self.host}"`` — wss://, no port.  We
    replace ``websockets.connect`` so any URI the SDK passes is ignored and the
    connection lands on ``ws://host:port`` instead.  This is the one allowed
    transport touch (URL-only redirect; behavior is identical to the real
    ``websockets.connect`` — the SDK still drives the real WS transport against
    a real server).  It mirrors the frozen TS reference passing ``scheme: 'ws'``
    to ``RelayClient`` (Python's client has no scheme option).
    """
    target_url = shared.ws_url
    real_connect = __import__("websockets").connect

    def proxy(uri: str, *args: Any, **kwargs: Any) -> Any:
        return real_connect(target_url, *args, **kwargs)

    return patch("signalwire.relay.client.websockets.connect", side_effect=proxy)


@pytest_asyncio.fixture
async def signalwire_relay_client(
    mock_relay: _MockRelayHarness,
) -> AsyncIterator[RelayClient]:
    """A real ``RelayClient`` connected to the shared mock relay server.

    Connects inside the ``websockets.connect`` URL redirect, then scopes the
    ``mock_relay`` view (the same object handed to this test) to the connected
    client's server-assigned session id, so the test's journal reads/pushes are
    isolated to its own session — safe under ``pytest -n auto``.  The fixture
    handles connect+disconnect; tests just use the client.

    The yield expression is a bare ``RelayClient(...)`` call so static coverage
    tools resolve ``signalwire_relay_client`` to ``RelayClient``.
    """
    _active_clients.clear()
    shared = _SHARED_RELAY.ensure()

    with _ws_redirect_to_mock(shared):
        client = RelayClient(
            project="test_proj",
            token="test_tok",
            host=shared.relay_host,
            contexts=["default"],
        )
        try:
            await client.connect()
            # Scope this test's harness view to the client's session. The mock
            # returns the session id as ``sessionid`` (no underscore) in the
            # connect result; the SDK captures it into ``_session_id``.
            mock_relay.session_id = client._session_id
            yield client
        finally:
            try:
                await client.disconnect()
            except Exception:
                pass

    _active_clients.clear()


@pytest.fixture
def relay_ws_redirect(mock_relay: _MockRelayHarness) -> Any:
    """Return a context-manager that redirects websockets.connect to the mock.

    Use this when a test needs to construct its own RelayClient (e.g. with
    different creds, or to cover the failure path on connect()) instead of
    relying on the auto-connected ``signalwire_relay_client`` fixture.
    """
    return _ws_redirect_to_mock(_SHARED_RELAY.ensure())
