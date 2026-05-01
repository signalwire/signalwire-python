"""Real-mock-backed tests for messaging (``send_message`` + inbound).

The messaging schemas are permissive (the C# server forwards JObject to
the messaging gateway), so the mock validates the wire frame loosely. We
still assert that the SDK builds the right ``messaging.send`` shape and
correctly processes the inbound ``messaging.receive`` and
``messaging.state`` events the mock can push.
"""

from __future__ import annotations

import asyncio
import uuid

import pytest

from signalwire.relay.message import Message

from .conftest import _RELAY_MOCK_AVAILABLE


pytestmark = pytest.mark.skipif(
    not _RELAY_MOCK_AVAILABLE,
    reason="mock_relay not adjacent — clone porting-sdk next to signalwire-python",
)


# ---------------------------------------------------------------------------
# send_message — outbound
# ---------------------------------------------------------------------------


async def test_send_message_journals_messaging_send(
    signalwire_relay_client, mock_relay
):
    msg = await signalwire_relay_client.send_message(
        to_number="+15551112222",
        from_number="+15553334444",
        body="hello",
        tags=["t1", "t2"],
    )
    assert isinstance(msg, Message)
    assert msg.message_id  # mock generates one
    assert msg.body == "hello"
    [entry] = mock_relay.journal_recv(method="messaging.send")
    p = entry.frame["params"]
    assert p["to_number"] == "+15551112222"
    assert p["from_number"] == "+15553334444"
    assert p["body"] == "hello"
    assert p["tags"] == ["t1", "t2"]


async def test_send_message_with_media_only(signalwire_relay_client, mock_relay):
    """A media-only MMS message produces a messaging.send with media but no body."""
    msg = await signalwire_relay_client.send_message(
        to_number="+15551112222",
        from_number="+15553334444",
        media=["https://media.example/cat.jpg"],
    )
    assert isinstance(msg, Message)
    [entry] = mock_relay.journal_recv(method="messaging.send")
    p = entry.frame["params"]
    assert p["media"] == ["https://media.example/cat.jpg"]
    assert "body" not in p or not p.get("body")


async def test_send_message_includes_context(signalwire_relay_client, mock_relay):
    """The context defaults to the protocol string and flows on the wire."""
    msg = await signalwire_relay_client.send_message(
        to_number="+15551112222",
        from_number="+15553334444",
        body="hi",
        context="custom-ctx",
    )
    [entry] = mock_relay.journal_recv(method="messaging.send")
    assert entry.frame["params"]["context"] == "custom-ctx"


async def test_send_message_returns_initial_state_queued(
    signalwire_relay_client, mock_relay
):
    """Right after send, the SDK Message is in 'queued' state."""
    msg = await signalwire_relay_client.send_message(
        to_number="+15551112222",
        from_number="+15553334444",
        body="hi",
    )
    assert msg.state == "queued"
    assert msg.is_done is False


async def test_send_message_resolves_on_delivered(
    signalwire_relay_client, mock_relay
):
    """A pushed messaging.state(delivered) resolves ``await message.wait()``."""
    msg = await signalwire_relay_client.send_message(
        to_number="+15551112222",
        from_number="+15553334444",
        body="hi",
    )
    # Push the terminal delivered state.
    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "signalwire.event",
            "params": {
                "event_type": "messaging.state",
                "params": {
                    "message_id": msg.message_id,
                    "message_state": "delivered",
                    "from_number": "+15553334444",
                    "to_number": "+15551112222",
                    "body": "hi",
                },
            },
        }
    )
    event = await msg.wait(timeout=5)
    assert msg.state == "delivered"
    assert msg.is_done is True
    assert event.params.get("message_state") == "delivered"


async def test_send_message_resolves_on_undelivered(
    signalwire_relay_client, mock_relay
):
    """An undelivered terminal state resolves the Message with that state."""
    msg = await signalwire_relay_client.send_message(
        to_number="+15551112222",
        from_number="+15553334444",
        body="hi",
    )
    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "signalwire.event",
            "params": {
                "event_type": "messaging.state",
                "params": {
                    "message_id": msg.message_id,
                    "message_state": "undelivered",
                    "reason": "carrier_blocked",
                },
            },
        }
    )
    await msg.wait(timeout=5)
    assert msg.state == "undelivered"
    assert msg.reason == "carrier_blocked"


async def test_send_message_resolves_on_failed(
    signalwire_relay_client, mock_relay
):
    """A failed terminal state resolves the Message."""
    msg = await signalwire_relay_client.send_message(
        to_number="+15551112222",
        from_number="+15553334444",
        body="hi",
    )
    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "signalwire.event",
            "params": {
                "event_type": "messaging.state",
                "params": {
                    "message_id": msg.message_id,
                    "message_state": "failed",
                    "reason": "spam",
                },
            },
        }
    )
    await msg.wait(timeout=5)
    assert msg.state == "failed"


async def test_send_message_intermediate_state_does_not_resolve(
    signalwire_relay_client, mock_relay
):
    """Intermediate states (sent) update Message.state but don't resolve."""
    msg = await signalwire_relay_client.send_message(
        to_number="+15551112222",
        from_number="+15553334444",
        body="hi",
    )
    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "signalwire.event",
            "params": {
                "event_type": "messaging.state",
                "params": {
                    "message_id": msg.message_id,
                    "message_state": "sent",
                },
            },
        }
    )
    # Wait for state propagation.
    for _ in range(100):
        if msg.state == "sent":
            break
        await asyncio.sleep(0.02)
    assert msg.state == "sent"
    assert msg.is_done is False


# ---------------------------------------------------------------------------
# Inbound messages
# ---------------------------------------------------------------------------


async def test_inbound_message_fires_on_message_handler(
    signalwire_relay_client, mock_relay
):
    """Pushed messaging.receive event invokes the on_message handler."""
    received = asyncio.Event()
    seen: dict[str, Message] = {}

    @signalwire_relay_client.on_message
    async def handle(msg):
        seen["msg"] = msg
        received.set()

    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "signalwire.event",
            "params": {
                "event_type": "messaging.receive",
                "params": {
                    "message_id": "in-msg-1",
                    "context": "default",
                    "direction": "inbound",
                    "from_number": "+15551110000",
                    "to_number": "+15552220000",
                    "body": "hello back",
                    "media": [],
                    "segments": 1,
                    "message_state": "received",
                    "tags": ["incoming"],
                },
            },
        }
    )
    await asyncio.wait_for(received.wait(), timeout=5)
    m = seen["msg"]
    assert m.message_id == "in-msg-1"
    assert m.direction == "inbound"
    assert m.from_number == "+15551110000"
    assert m.to_number == "+15552220000"
    assert m.body == "hello back"
    assert m.tags == ["incoming"]


# ---------------------------------------------------------------------------
# State progression — full pipeline
# ---------------------------------------------------------------------------


async def test_full_message_state_progression(
    signalwire_relay_client, mock_relay
):
    """sent → delivered progression updates state and resolves."""
    msg = await signalwire_relay_client.send_message(
        to_number="+15551112222",
        from_number="+15553334444",
        body="full pipeline",
    )
    # Push intermediate "sent".
    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "signalwire.event",
            "params": {
                "event_type": "messaging.state",
                "params": {
                    "message_id": msg.message_id,
                    "message_state": "sent",
                },
            },
        }
    )
    for _ in range(100):
        if msg.state == "sent":
            break
        await asyncio.sleep(0.02)
    assert msg.state == "sent"

    # Then "delivered".
    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "signalwire.event",
            "params": {
                "event_type": "messaging.state",
                "params": {
                    "message_id": msg.message_id,
                    "message_state": "delivered",
                },
            },
        }
    )
    await msg.wait(timeout=5)
    assert msg.state == "delivered"
