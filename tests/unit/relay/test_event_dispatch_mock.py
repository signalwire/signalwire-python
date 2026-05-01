"""Real-mock-backed tests for SDK event dispatch / routing.

Focus: edge cases in the SDK's recv loop and event router that don't fit
neatly into per-action / per-call test files.

Covered:
- Sub-command methods (play.pause/resume/volume, record.pause/resume,
  collect.start_input_timers) journal under the right method name with the
  same control_id as the parent action.
- Unknown event_type doesn't crash the recv loop.
- Bad/unknown call_id is dropped silently.
- Multi-action concurrency: 3 simultaneous actions on one call routed by
  control_id.
- Event ACK round-trip: SDK ACKs server-pushed events back as JSON-RPC
  responses.
- Tag-based dial routing without a top-level call_id (the production
  ``calling.call.dial`` shape).
"""

from __future__ import annotations

import asyncio
import uuid

import pytest

from signalwire.relay.client import RelayClient, _active_clients
from signalwire.relay.constants import METHOD_SIGNALWIRE_EVENT

from .conftest import _RELAY_MOCK_AVAILABLE


pytestmark = pytest.mark.skipif(
    not _RELAY_MOCK_AVAILABLE,
    reason="mock_relay not adjacent — clone porting-sdk next to signalwire-python",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _answered_call(client, mock_relay, call_id: str = "evt-call-1"):
    captured: dict[str, object] = {}
    handler_done = asyncio.Event()

    @client.on_call
    async def _handle(call):
        captured["call"] = call
        await call.answer()
        handler_done.set()

    mock_relay.inbound_call(call_id=call_id, auto_states=["created"])
    await asyncio.wait_for(handler_done.wait(), timeout=5)
    call = captured["call"]
    call.state = "answered"
    return call


def _bare_event_frame(event_type: str, params: dict) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "signalwire.event",
        "params": {"event_type": event_type, "params": params},
    }


# ---------------------------------------------------------------------------
# Sub-command journaling
# ---------------------------------------------------------------------------


async def test_record_pause_journals_record_pause(
    signalwire_relay_client, mock_relay
):
    call = await _answered_call(signalwire_relay_client, mock_relay, "ec-rec-pa")
    action = await call.record(audio={"format": "wav"}, control_id="ec-rec-pa-1")
    await action.pause(behavior="continuous")
    pauses = mock_relay.journal_recv(method="calling.record.pause")
    assert pauses
    p = pauses[-1].frame["params"]
    assert p["control_id"] == "ec-rec-pa-1"
    assert p["behavior"] == "continuous"


async def test_record_resume_journals_record_resume(
    signalwire_relay_client, mock_relay
):
    call = await _answered_call(signalwire_relay_client, mock_relay, "ec-rec-re")
    action = await call.record(audio={"format": "wav"}, control_id="ec-rec-re-1")
    await action.resume()
    resumes = mock_relay.journal_recv(method="calling.record.resume")
    assert resumes and resumes[-1].frame["params"]["control_id"] == "ec-rec-re-1"


async def test_collect_start_input_timers_journals_correctly(
    signalwire_relay_client, mock_relay
):
    """A standalone collect's start_input_timers journals the right method."""
    call = await _answered_call(signalwire_relay_client, mock_relay, "ec-col-sit")
    action = await call.collect(
        digits={"max": 4},
        start_input_timers=False,
        control_id="ec-col-sit-1",
    )
    await action.start_input_timers()
    starts = mock_relay.journal_recv(method="calling.collect.start_input_timers")
    assert starts and starts[-1].frame["params"]["control_id"] == "ec-col-sit-1"


async def test_play_volume_carries_negative_value(
    signalwire_relay_client, mock_relay
):
    call = await _answered_call(signalwire_relay_client, mock_relay, "ec-pvol")
    action = await call.play(
        [{"type": "silence", "params": {"duration": 60}}],
        control_id="ec-pvol-1",
    )
    await action.volume(-5.5)
    vol = mock_relay.journal_recv(method="calling.play.volume")
    assert vol and vol[-1].frame["params"]["volume"] == -5.5


# ---------------------------------------------------------------------------
# Unknown event types — recv loop survives
# ---------------------------------------------------------------------------


async def test_unknown_event_type_does_not_crash(
    signalwire_relay_client, mock_relay
):
    """Pushing a frame with an unknown event_type doesn't break the SDK."""
    mock_relay.push(_bare_event_frame("nonsense.unknown", {"foo": "bar"}))
    # Drive a follow-up call to prove the SDK is still alive.
    await asyncio.sleep(0.1)
    assert signalwire_relay_client._connected is True


async def test_event_with_bad_call_id_is_dropped(
    signalwire_relay_client, mock_relay
):
    """An event with a call_id that doesn't match any registered call is dropped."""
    mock_relay.push(
        _bare_event_frame(
            "calling.call.play",
            {
                "call_id": "no-such-call-bogus",
                "control_id": "stranger",
                "state": "playing",
            },
        )
    )
    await asyncio.sleep(0.1)
    assert signalwire_relay_client._connected is True


async def test_event_with_empty_event_type_is_dropped(
    signalwire_relay_client, mock_relay
):
    """An event whose event_type is empty string is logged and skipped."""
    mock_relay.push(_bare_event_frame("", {"call_id": "x"}))
    await asyncio.sleep(0.1)
    assert signalwire_relay_client._connected is True


# ---------------------------------------------------------------------------
# Multi-action concurrency: 3 actions on one call
# ---------------------------------------------------------------------------


async def test_three_concurrent_actions_resolve_independently(
    signalwire_relay_client, mock_relay
):
    """Three actions with different control_ids each receive their own events."""
    call = await _answered_call(signalwire_relay_client, mock_relay, "ec-3acts")
    play1 = await call.play(
        [{"type": "silence", "params": {"duration": 60}}], control_id="3a-p1"
    )
    play2 = await call.play(
        [{"type": "silence", "params": {"duration": 60}}], control_id="3a-p2"
    )
    rec = await call.record(audio={"format": "wav"}, control_id="3a-r1")

    # Fire only play1's finished.
    mock_relay.push(
        _bare_event_frame(
            "calling.call.play",
            {"call_id": "ec-3acts", "control_id": "3a-p1", "state": "finished"},
        )
    )
    await play1.wait(timeout=2)
    assert play1.is_done is True
    assert play2.is_done is False
    assert rec.is_done is False

    # Fire play2's.
    mock_relay.push(
        _bare_event_frame(
            "calling.call.play",
            {"call_id": "ec-3acts", "control_id": "3a-p2", "state": "finished"},
        )
    )
    await play2.wait(timeout=2)
    assert play2.is_done is True
    assert rec.is_done is False


# ---------------------------------------------------------------------------
# Event ACK round-trip — server-pushed events get ack frames back
# ---------------------------------------------------------------------------


async def test_event_ack_sent_back_to_server(
    signalwire_relay_client, mock_relay
):
    """After receiving signalwire.event, SDK sends back a JSON-RPC response.

    The mock journals every recv frame — we look for a frame with the
    same id as the pushed event whose body is just ``{"id": ..., "result": {}}``.
    """
    evt_id = "evt-ack-test-1"
    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": evt_id,
            "method": "signalwire.event",
            "params": {
                "event_type": "calling.call.play",
                "params": {
                    "call_id": "anything",
                    "control_id": "x",
                    "state": "playing",
                },
            },
        }
    )
    # Wait a moment for the recv loop to ACK.
    await asyncio.sleep(0.2)

    # Search the journal for the SDK's ACK back. The ACK is a recv frame
    # (server side received it) with id == evt_id and a result key.
    j = mock_relay.journal()
    acks = [
        e for e in j
        if e.direction == "recv"
        and e.frame.get("id") == evt_id
        and "result" in e.frame
    ]
    assert acks, (
        f"no event ACK with id={evt_id!r} found in journal; saw recv frames="
        f"{[(e.method, e.frame.get('id')) for e in j if e.direction == 'recv']}"
    )


# ---------------------------------------------------------------------------
# Tag-based dial routing — call.call_id nested
# ---------------------------------------------------------------------------


async def test_dial_event_routes_via_tag_when_no_top_level_call_id(
    mock_relay, relay_ws_redirect
):
    """A calling.call.dial event with no top-level call_id routes via tag.

    Production wire shape: the dial event's ``params`` doesn't carry
    ``call_id`` at the top level — only inside ``params.call.call_id``.
    The SDK's _handle_dial_event must still route correctly.
    """
    _active_clients.clear()
    with relay_ws_redirect:
        client = RelayClient(
            project="p", token="t", host=mock_relay.relay_host, contexts=["default"]
        )
        try:
            await client.connect()
            mock_relay.arm_dial(
                tag="ec-tag-route",
                winner_call_id="WINTAG",
                states=["created", "answered"],
                node_id="n",
                device={"type": "phone", "params": {}},
            )
            call = await client.dial(
                [[{"type": "phone", "params": {"to_number": "+1", "from_number": "+2"}}]],
                tag="ec-tag-route",
                dial_timeout=5.0,
            )
            assert call.call_id == "WINTAG"
            # Verify the dial event the mock pushed had no top-level call_id —
            # only call.call_id nested.
            sends = mock_relay.journal_send(event_type="calling.call.dial")
            assert sends, "no calling.call.dial event in journal"
            inner = sends[-1].frame["params"]["params"]
            # Top-level params: tag, dial_state, call. NO call_id.
            assert "call_id" not in inner
            assert inner["call"]["call_id"] == "WINTAG"
        finally:
            await client.disconnect()
    _active_clients.clear()


# ---------------------------------------------------------------------------
# Server ping handling
# ---------------------------------------------------------------------------


async def test_server_ping_acked_by_sdk(signalwire_relay_client, mock_relay):
    """The mock pushes a signalwire.ping; SDK responds with a JSON-RPC result."""
    ping_id = "ping-test-1"
    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": ping_id,
            "method": "signalwire.ping",
            "params": {},
        }
    )
    await asyncio.sleep(0.2)

    j = mock_relay.journal()
    pongs = [
        e for e in j
        if e.direction == "recv"
        and e.frame.get("id") == ping_id
        and "result" in e.frame
    ]
    assert pongs, f"SDK did not respond to ping; recv frames seen with id={ping_id!r}: {[e.frame for e in j if e.direction == 'recv' and e.frame.get('id') == ping_id]}"


# ---------------------------------------------------------------------------
# Authorization state — captured for reconnect
# ---------------------------------------------------------------------------


async def test_authorization_state_event_captured(
    signalwire_relay_client, mock_relay
):
    """A pushed signalwire.authorization.state event updates SDK internal state."""
    mock_relay.push(
        _bare_event_frame(
            "signalwire.authorization.state",
            {"authorization_state": "test-auth-state-blob"},
        )
    )
    # Wait for recv loop to process.
    for _ in range(100):
        if signalwire_relay_client._authorization_state:
            break
        await asyncio.sleep(0.02)
    assert signalwire_relay_client._authorization_state == "test-auth-state-blob"


# ---------------------------------------------------------------------------
# Calling.error event — does not raise into the SDK
# ---------------------------------------------------------------------------


async def test_calling_error_event_does_not_crash(
    signalwire_relay_client, mock_relay
):
    """An emitted calling.error event is logged but doesn't break recv loop."""
    mock_relay.push(
        _bare_event_frame(
            "calling.error",
            {"code": "5001", "message": "synthetic error"},
        )
    )
    await asyncio.sleep(0.1)
    assert signalwire_relay_client._connected is True


# ---------------------------------------------------------------------------
# State event for an answered call updates Call.state
# ---------------------------------------------------------------------------


async def test_call_state_event_updates_state(
    signalwire_relay_client, mock_relay
):
    """A state event for an existing call updates its .state field."""
    call = await _answered_call(signalwire_relay_client, mock_relay, "ec-stt")
    mock_relay.push(
        _bare_event_frame(
            "calling.call.state",
            {"call_id": "ec-stt", "call_state": "ending", "direction": "inbound"},
        )
    )
    for _ in range(100):
        if call.state == "ending":
            break
        await asyncio.sleep(0.02)
    assert call.state == "ending"


async def test_call_listener_fires_on_event(signalwire_relay_client, mock_relay):
    """Custom event listeners registered via ``call.on(...)`` fire on matching events."""
    call = await _answered_call(signalwire_relay_client, mock_relay, "ec-list")
    fired = asyncio.Event()
    seen = []

    def _on_play(event):
        seen.append(event)
        fired.set()

    call.on("calling.call.play", _on_play)
    mock_relay.push(
        _bare_event_frame(
            "calling.call.play",
            {"call_id": "ec-list", "control_id": "x", "state": "playing"},
        )
    )
    await asyncio.wait_for(fired.wait(), timeout=2)
    assert seen[0].event_type == "calling.call.play"
