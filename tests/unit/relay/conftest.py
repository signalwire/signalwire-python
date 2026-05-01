"""Mock infrastructure and fixtures for RELAY client tests.

Two test backends coexist:

1. The legacy ``MockWebSocket`` / ``connected_client`` fixtures — patches
   ``websockets.connect`` and is used by the older RELAY unit tests
   (``test_client.py``, ``test_call.py``, etc.).  Each test there pre-stages
   responses on the mock WebSocket directly.

2. The newer ``signalwire_relay_client`` / ``mock_relay`` fixtures — back the
   SDK with a real WebSocket server provided by the ``mock_relay`` package
   (``porting-sdk/test_harness/mock_relay``).  The mock loads RELAY's JSON
   schemas (extracted from switchblade) and synthesizes schema-conformant
   responses.  Tests written against this fixture exercise the SDK's actual
   ``websockets`` transport and then assert on parsed SDK state and the
   mock's HTTP-exposed journal / scenario plumbing.

   Usage::

       def test_dial_round_trip(signalwire_relay_client, mock_relay):
           # async usage; see test_outbound_call_mock.py for full pattern
           call = await signalwire_relay_client.dial(...)
           j = mock_relay.journal()
           assert any(e["method"] == "calling.dial" for e in j if e["direction"] == "recv")

The two fixture families are independent — a test may use either, but not
both at once (no one ever needs both).
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
import websockets.exceptions

from signalwire.relay.client import RelayClient, _active_clients
from signalwire.relay.call import Call
from signalwire.relay.constants import METHOD_SIGNALWIRE_CONNECT


# ---------------------------------------------------------------------------
# Adjacency-based discovery for porting-sdk mock packages.
#
# Mirrors tests/unit/rest/conftest.py — must walk up to find
# ``../porting-sdk/test_harness/mock_relay/`` and prepend it to ``sys.path``
# so ``import mock_relay`` resolves without any pip install. The skipif
# marker at module level guards every mock-backed test file.
# ---------------------------------------------------------------------------


def _discover_mock_package(name: str) -> bool:
    """Walk up from this file looking for ``../porting-sdk/test_harness/<name>/``.

    Returns True when a sibling ``porting-sdk`` clone is found and the package
    root has been prepended to ``sys.path``. Idempotent — multiple calls don't
    duplicate ``sys.path`` entries.
    """
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        candidate = parent.parent / "porting-sdk" / "test_harness" / name
        if (candidate / name / "__init__.py").is_file():
            entry = str(candidate)
            if entry not in sys.path:
                sys.path.insert(0, entry)
            return True
    return False


# Try the relative-path discovery first; this works in fresh adjacent clones
# without any prior pip install.
_RELAY_MOCK_AVAILABLE = _discover_mock_package("mock_relay")

try:
    from mock_relay import MockRelayServer  # type: ignore
    _RELAY_MOCK_AVAILABLE = True
except ImportError:  # pragma: no cover - env without porting-sdk available
    MockRelayServer = None  # type: ignore
    _RELAY_MOCK_AVAILABLE = False


# ---------------------------------------------------------------------------
# Mock WebSocket
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

    def __aiter__(self):
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
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def relay_client():
    """Fresh RelayClient with test credentials.  Clears _active_clients."""
    _active_clients.clear()
    client = RelayClient(project="test-project", token="test-token")
    yield client
    _active_clients.clear()


@pytest_asyncio.fixture
async def connected_client():
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
def make_call():
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
# Real mock-relay server fixtures (mock_relay package, ws + http control plane)
# ---------------------------------------------------------------------------


# Per-process default for parallel RelayClient connections during tests. The
# SDK's _MAX_CONNECTIONS guard otherwise refuses a 2nd client in the same
# process; bumping it lets a single test create multiple clients (used by the
# reconnect-with-protocol-string tests).
os.environ.setdefault("RELAY_MAX_CONNECTIONS", "16")


def _free_port() -> int:
    """Pick an unused localhost TCP port for the mock server."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@dataclass
class _RelayJournalEntry:
    """Lightweight view of a single journal entry the mock server recorded.

    Mirrors the dict shape exposed at ``/__mock__/journal`` but is decoupled
    from the upstream type so this conftest doesn't import internal modules.
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
    """Test-facing harness around the running ``MockRelayServer``.

    Wraps the server's HTTP control plane in a typed surface so tests don't
    have to hand-roll ``requests`` calls. All methods talk to the mock over
    plain HTTP — synchronous from the test thread, even though the server's
    WebSocket handler runs on its own asyncio loop.
    """

    def __init__(self, server: "MockRelayServer") -> None:  # type: ignore[name-defined]
        # Local import so the type only resolves when discovery succeeded.
        import requests as _requests

        self._server = server
        self._requests = _requests

    # -- exposed addresses ---------------------------------------------------

    @property
    def ws_url(self) -> str:
        return self._server.ws_url

    @property
    def http_url(self) -> str:
        return self._server.http_url

    @property
    def relay_host(self) -> str:
        """Host:port for the SDK ``host=`` parameter (no scheme)."""
        return self._server.relay_host

    # -- journal -------------------------------------------------------------

    def journal(self) -> list[_RelayJournalEntry]:
        """Return every journaled frame in arrival order."""
        resp = self._requests.get(f"{self.http_url}/__mock__/journal", timeout=5)
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
        """Clear journal + scenario queues. Called between tests automatically."""
        self._requests.post(f"{self.http_url}/__mock__/journal/reset", timeout=5)
        self._requests.post(f"{self.http_url}/__mock__/scenarios/reset", timeout=5)

    # -- scenario plumbing ---------------------------------------------------

    def arm_method(
        self, method: str, events: Iterable[dict[str, Any]]
    ) -> None:
        """Queue scripted post-RPC events for ``method`` (FIFO consume-once)."""
        resp = self._requests.post(
            f"{self.http_url}/__mock__/scenarios/{method}",
            json=list(events),
            timeout=5,
        )
        resp.raise_for_status()

    def arm_dial(self, **kwargs: Any) -> None:
        """Queue a dial-dance scenario (winner state events + final dial event)."""
        resp = self._requests.post(
            f"{self.http_url}/__mock__/scenarios/dial",
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
        """Push a single ``signalwire.event`` (or other) frame to the SDK."""
        url = f"{self.http_url}/__mock__/push"
        if session_id:
            url = f"{url}?session_id={session_id}"
        resp = self._requests.post(url, json={"frame": frame}, timeout=5)
        resp.raise_for_status()
        return resp.json()

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
        """Inject an inbound call announcement into one or every session."""
        body: dict[str, Any] = {
            "from_number": from_number,
            "to_number": to_number,
            "context": context,
            "auto_states": auto_states or ["created"],
            "delay_ms": delay_ms,
        }
        if call_id is not None:
            body["call_id"] = call_id
        if session_id is not None:
            body["session_id"] = session_id
        resp = self._requests.post(
            f"{self.http_url}/__mock__/inbound_call", json=body, timeout=5
        )
        resp.raise_for_status()
        return resp.json()

    def scenario_play(self, ops: list[dict[str, Any]]) -> dict[str, Any]:
        """Run a scripted timeline of pushes/sleeps/expect_recv on the server."""
        resp = self._requests.post(
            f"{self.http_url}/__mock__/scenario_play", json=ops, timeout=15
        )
        resp.raise_for_status()
        return resp.json()

    def sessions(self) -> list[dict[str, Any]]:
        """List active WebSocket session metadata."""
        resp = self._requests.get(f"{self.http_url}/__mock__/sessions", timeout=5)
        resp.raise_for_status()
        return resp.json().get("sessions", [])


@pytest.fixture(scope="session")
def _mock_relay_server_instance():
    """Boot one real mock-relay server for the whole test session."""
    if not _RELAY_MOCK_AVAILABLE:
        pytest.skip(
            "mock_relay not adjacent — clone porting-sdk next to signalwire-python"
        )
    server = MockRelayServer(  # type: ignore[misc]
        host="127.0.0.1",
        ws_port=_free_port(),
        http_port=_free_port(),
        log_level="error",
    ).start()
    try:
        yield server
    finally:
        server.stop()


@pytest.fixture
def mock_relay(_mock_relay_server_instance):
    """Test-facing harness around the mock-relay server.

    The journal and scenario queues are reset before every test so each test
    starts from a clean slate.
    """
    harness = _MockRelayHarness(_mock_relay_server_instance)
    harness.reset()
    yield harness


def _ws_redirect_to_mock(mock_relay_server) -> Any:
    """Build the websockets.connect override that points the SDK at the mock.

    The SDK builds its URI as ``f"wss://{self.host}"`` — wss://, no port. We
    replace ``websockets.connect`` so any URI the SDK passes is ignored and
    the connection lands on ``ws://host:port`` instead.

    The patch only changes the URL; behavior is identical to the real
    websockets.connect. This keeps the dual-contract (touch the real symbol /
    behavioral assertions / journal assertions) intact — see
    ``INTENTIONAL_THIN_TESTS.md`` adjacent to the audit script.
    """
    target_url = mock_relay_server.ws_url
    real_connect = __import__("websockets").connect

    def proxy(uri, *args, **kwargs):
        # Ignore any URI the SDK passed, dial the mock instead.
        return real_connect(target_url, *args, **kwargs)

    return patch("signalwire.relay.client.websockets.connect", side_effect=proxy)


@pytest_asyncio.fixture
async def signalwire_relay_client(mock_relay):
    """A real ``RelayClient`` connected to the mock relay server.

    Yields a connected RelayClient inside the ``websockets.connect`` URL
    redirect.  The fixture handles connect+disconnect; tests just use the
    client.

    The yield expression is a bare ``RelayClient(...)`` call so static
    coverage tools resolve ``signalwire_relay_client`` to ``RelayClient``.
    """
    _active_clients.clear()

    server = mock_relay._server  # the underlying MockRelayServer
    target_url = server.ws_url
    real_connect = __import__("websockets").connect

    def proxy(uri, *args, **kwargs):
        return real_connect(target_url, *args, **kwargs)

    with patch("signalwire.relay.client.websockets.connect", side_effect=proxy):
        client = RelayClient(
            project="test_proj",
            token="test_tok",
            host=server.relay_host,
            contexts=["default"],
        )
        try:
            await client.connect()
            yield client
        finally:
            try:
                await client.disconnect()
            except Exception:
                pass

    _active_clients.clear()


@pytest.fixture
def relay_ws_redirect(mock_relay):
    """Return a context-manager that redirects websockets.connect to the mock.

    Use this when a test needs to construct its own RelayClient (e.g. with
    different creds, or to cover the failure path on connect()) instead of
    relying on the auto-connected ``signalwire_relay_client`` fixture.
    """
    return _ws_redirect_to_mock(mock_relay._server)
