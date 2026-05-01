"""Real-mock-backed tests for ``signalwire.relay.RelayClient.connect()``.

These tests boot the shared ``mock_relay`` WebSocket server (the same backend
used by every SDK port) and drive the actual ``RelayClient``.  No MagicMock
of ``websockets``; the only patched symbol is ``websockets.connect`` to
redirect the SDK's hardcoded ``wss://`` URI at our local ``ws://``.

Each test checks two things:

1. **Behavioral** — what the SDK exposed back to the developer (e.g. the
   protocol string is set, the connect call returned, exceptions raise on
   error paths).
2. **Wire** — what the mock journaled. Because the mock is schema-driven
   from the production server's C# Params/Result classes, asserting on the
   journal verifies the SDK is sending the exact wire shape the real RELAY
   expects.
"""

from __future__ import annotations

import asyncio
import os

import pytest

from signalwire.relay.client import RelayClient, RelayError, _active_clients
from signalwire.relay.constants import (
    AGENT_STRING,
    METHOD_SIGNALWIRE_CONNECT,
    PROTOCOL_VERSION,
)

from .conftest import _RELAY_MOCK_AVAILABLE


pytestmark = pytest.mark.skipif(
    not _RELAY_MOCK_AVAILABLE,
    reason="mock_relay not adjacent — clone porting-sdk next to signalwire-python",
)


# ---------------------------------------------------------------------------
# Connect — happy path
# ---------------------------------------------------------------------------


async def test_connect_returns_protocol_string(signalwire_relay_client):
    """``client.connect()`` succeeds and ``client.relay_protocol`` is non-empty."""
    client = signalwire_relay_client
    # The fixture already called connect(); assert state is consistent.
    assert client._connected is True
    assert client.relay_protocol.startswith("signalwire_"), (
        f"unexpected protocol: {client.relay_protocol!r}"
    )


async def test_connect_journal_records_signalwire_connect(
    signalwire_relay_client, mock_relay
):
    """The journal contains exactly one signalwire.connect frame from the SDK."""
    j = mock_relay.journal_recv(method=METHOD_SIGNALWIRE_CONNECT)
    assert len(j) == 1, f"expected 1 connect; got {len(j)}: {[e.frame for e in j]}"


async def test_connect_journal_carries_project_and_token(
    signalwire_relay_client, mock_relay
):
    """The auth block on the wire contains the project/token we configured."""
    [entry] = mock_relay.journal_recv(method=METHOD_SIGNALWIRE_CONNECT)
    auth = entry.frame["params"]["authentication"]
    assert auth["project"] == "test_proj"
    assert auth["token"] == "test_tok"


async def test_connect_journal_carries_contexts(signalwire_relay_client, mock_relay):
    """The contexts list flows into the connect frame's ``contexts`` field."""
    [entry] = mock_relay.journal_recv(method=METHOD_SIGNALWIRE_CONNECT)
    assert entry.frame["params"]["contexts"] == ["default"]


async def test_connect_journal_carries_agent_and_version(
    signalwire_relay_client, mock_relay
):
    """The wire frame includes the SDK agent string and protocol version."""
    [entry] = mock_relay.journal_recv(method=METHOD_SIGNALWIRE_CONNECT)
    p = entry.frame["params"]
    assert p["agent"] == AGENT_STRING
    assert p["version"] == PROTOCOL_VERSION


async def test_connect_journal_event_acks_true(signalwire_relay_client, mock_relay):
    """``event_acks`` is sent as True so the server starts ack-mode."""
    [entry] = mock_relay.journal_recv(method=METHOD_SIGNALWIRE_CONNECT)
    assert entry.frame["params"]["event_acks"] is True


# ---------------------------------------------------------------------------
# Reconnect with protocol → session_restored
# ---------------------------------------------------------------------------


async def test_reconnect_with_protocol_string_includes_protocol_in_frame(
    mock_relay, relay_ws_redirect
):
    """A second connect with a stored protocol string carries it on the wire."""
    _active_clients.clear()
    issued: dict[str, str] = {}
    with relay_ws_redirect:
        client1 = RelayClient(
            project="p", token="t", host=mock_relay.relay_host, contexts=["c1"]
        )
        try:
            await client1.connect()
            issued["protocol"] = client1.relay_protocol
        finally:
            await client1.disconnect()

        client2 = RelayClient(
            project="p", token="t", host=mock_relay.relay_host, contexts=["c1"]
        )
        client2._relay_protocol = issued["protocol"]
        try:
            await client2.connect()
        finally:
            await client2.disconnect()
    _active_clients.clear()

    # The second connect frame must carry the same protocol field.
    connect_frames = [
        e for e in mock_relay.journal_recv(method=METHOD_SIGNALWIRE_CONNECT)
        if e.frame["params"].get("protocol") == issued["protocol"]
    ]
    assert connect_frames, (
        f"no resume connect carried protocol={issued['protocol']!r}; saw protocols="
        f"{[e.frame['params'].get('protocol') for e in mock_relay.journal_recv(method=METHOD_SIGNALWIRE_CONNECT)]}"
    )


async def test_reconnect_with_protocol_preserves_protocol_value(
    mock_relay, relay_ws_redirect
):
    """The protocol the SDK reports after reconnect equals what it sent."""
    _active_clients.clear()
    issued: dict[str, str] = {}
    with relay_ws_redirect:
        c1 = RelayClient(project="p", token="t", host=mock_relay.relay_host)
        try:
            await c1.connect()
            issued["v"] = c1.relay_protocol
        finally:
            await c1.disconnect()

        c2 = RelayClient(project="p", token="t", host=mock_relay.relay_host)
        c2._relay_protocol = issued["v"]
        try:
            await c2.connect()
            # Server confirms the same protocol on resume.
            assert c2.relay_protocol == issued["v"]
        finally:
            await c2.disconnect()
    _active_clients.clear()


# ---------------------------------------------------------------------------
# Auth failure paths
# ---------------------------------------------------------------------------


async def test_connect_rejects_empty_creds_at_constructor(monkeypatch):
    """The SDK refuses to construct a client with empty creds."""
    monkeypatch.delenv("SIGNALWIRE_PROJECT_ID", raising=False)
    monkeypatch.delenv("SIGNALWIRE_API_TOKEN", raising=False)
    monkeypatch.delenv("SIGNALWIRE_JWT_TOKEN", raising=False)
    with pytest.raises(ValueError, match="project and token are required"):
        RelayClient(project="", token="", host="anywhere")


async def test_unauthenticated_raw_connect_rejected_by_mock(mock_relay):
    """Bypassing the SDK to send a connect with empty creds — mock returns AUTH_REQUIRED.

    The SDK won't construct an empty-creds client, so we drive the wire
    directly here.  This proves the mock's auth-failure path is reachable —
    a port whose SDK does allow empty creds will receive the same error.
    """
    import json as _json
    import uuid as _uuid

    import websockets as _ws

    sock = await _ws.connect(mock_relay.ws_url)
    try:
        req_id = str(_uuid.uuid4())
        await sock.send(
            _json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "method": "signalwire.connect",
                    "params": {
                        "version": PROTOCOL_VERSION,
                        "agent": AGENT_STRING,
                        "authentication": {"project": "", "token": ""},
                    },
                }
            )
        )
        resp = _json.loads(await sock.recv())
    finally:
        await sock.close()

    assert "error" in resp, f"expected error from mock, got: {resp}"
    err = resp["error"]
    # The mock returns AUTH_REQUIRED in the error.data envelope.
    assert err.get("data", {}).get("signalwire_error_code") == "AUTH_REQUIRED"


# ---------------------------------------------------------------------------
# Connect — JWT path
# ---------------------------------------------------------------------------


async def test_connect_with_jwt_carries_jwt_on_wire(mock_relay, relay_ws_redirect):
    """A JWT-only client sends ``authentication.jwt_token``, no project/token."""
    _active_clients.clear()
    with relay_ws_redirect:
        client = RelayClient(
            jwt_token="fake-jwt-eyJ.AaaA.BbB",
            host=mock_relay.relay_host,
        )
        try:
            await client.connect()
        finally:
            await client.disconnect()
    _active_clients.clear()

    [entry] = mock_relay.journal_recv(method=METHOD_SIGNALWIRE_CONNECT)
    auth = entry.frame["params"]["authentication"]
    assert auth.get("jwt_token") == "fake-jwt-eyJ.AaaA.BbB"
    # JWT path doesn't include project/token.
    assert "token" not in auth or not auth["token"]
