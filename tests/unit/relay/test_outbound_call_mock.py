"""Real-mock-backed tests for outbound calls (``RelayClient.dial``).

The dial flow is the most fragile RELAY surface: ``calling.dial`` returns a
plain 200 with NO call_id; the actual call info arrives via subsequent
``calling.call.state`` (per leg) and ``calling.call.dial`` (with the winner)
events keyed by ``tag``.  These tests run the real SDK against the mock so
the wire shape AND the SDK's tag-based reassembly are both validated.

The mock's ``/__mock__/scenarios/dial`` endpoint scripts the entire dance
(winner state events + per-loser state events + final dial event with
``dial_winner: true``).
"""

from __future__ import annotations

import asyncio
import re
import uuid

import pytest

from signalwire.relay.client import RelayError
from signalwire.relay.call import Call

from .conftest import _RELAY_MOCK_AVAILABLE


pytestmark = pytest.mark.skipif(
    not _RELAY_MOCK_AVAILABLE,
    reason="mock_relay not adjacent — clone porting-sdk next to signalwire-python",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _phone_device(to: str = "+15551112222", frm: str = "+15553334444") -> dict:
    return {"type": "phone", "params": {"to_number": to, "from_number": frm}}


# ---------------------------------------------------------------------------
# Happy-path dial
# ---------------------------------------------------------------------------


async def test_dial_resolves_to_call_with_winner_id(
    signalwire_relay_client, mock_relay
):
    """``dial()`` returns a Call carrying the winner's call_id."""
    mock_relay.arm_dial(
        tag="t-happy",
        winner_call_id="winner-1",
        states=["created", "ringing", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
        delay_ms=1,
    )
    call = await signalwire_relay_client.dial(
        [[_phone_device()]],
        tag="t-happy",
        dial_timeout=5.0,
    )
    assert isinstance(call, Call)
    assert call.call_id == "winner-1"
    assert call.tag == "t-happy"
    assert call.state == "answered"
    assert call.direction == "outbound"


async def test_dial_journal_records_calling_dial_frame(
    signalwire_relay_client, mock_relay
):
    """The mock journal contains a ``calling.dial`` frame with the right tag."""
    mock_relay.arm_dial(
        tag="t-frame",
        winner_call_id="winner-frame",
        states=["created", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
    )
    await signalwire_relay_client.dial(
        [[_phone_device()]],
        tag="t-frame",
        dial_timeout=5.0,
    )
    [entry] = mock_relay.journal_recv(method="calling.dial")
    p = entry.frame["params"]
    assert p["tag"] == "t-frame"
    assert isinstance(p["devices"], list)
    assert p["devices"][0][0]["type"] == "phone"


async def test_dial_with_max_duration_in_frame(
    signalwire_relay_client, mock_relay
):
    """``max_duration`` flows into the on-wire calling.dial params."""
    mock_relay.arm_dial(
        tag="t-md",
        winner_call_id="winner-md",
        states=["created", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
    )
    await signalwire_relay_client.dial(
        [[_phone_device()]],
        tag="t-md",
        max_duration=300,
        dial_timeout=5.0,
    )
    [entry] = mock_relay.journal_recv(method="calling.dial")
    assert entry.frame["params"]["max_duration"] == 300


async def test_dial_auto_generates_uuid_tag_when_omitted(
    signalwire_relay_client, mock_relay
):
    """When ``tag`` is omitted the SDK generates a UUID and includes it on the wire."""
    # Auto-generated tag is unknowable upfront; arm dial without a tag-based
    # match — the mock's dial scenario uses the SDK's tag automatically.
    # We can't pre-seed a scenario without knowing the tag; instead, push
    # the dial answer event manually after the dial frame lands.
    dial_done = asyncio.Event()
    seen_tag: dict[str, str] = {}

    async def _push_dial_answer():
        # Wait for the dial frame to arrive in the journal.
        for _ in range(200):
            entries = mock_relay.journal_recv(method="calling.dial")
            if entries:
                seen_tag["v"] = entries[-1].frame["params"]["tag"]
                break
            await asyncio.sleep(0.01)
        else:
            return
        # Fire the answered event.
        mock_relay.push(
            {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "signalwire.event",
                "params": {
                    "event_type": "calling.call.dial",
                    "params": {
                        "tag": seen_tag["v"],
                        "node_id": "node-mock-1",
                        "dial_state": "answered",
                        "call": {
                            "call_id": "auto-tag-winner",
                            "node_id": "node-mock-1",
                            "tag": seen_tag["v"],
                            "device": _phone_device(),
                            "dial_winner": True,
                        },
                    },
                },
            }
        )
        dial_done.set()

    pusher = asyncio.create_task(_push_dial_answer())
    try:
        call = await signalwire_relay_client.dial(
            [[_phone_device()]],
            dial_timeout=5.0,
        )
    finally:
        pusher.cancel()
        try:
            await pusher
        except asyncio.CancelledError:
            pass

    assert call.call_id == "auto-tag-winner"
    # The tag the SDK generated should be a UUID.
    uuid_re = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    assert uuid_re.match(seen_tag["v"]), (
        f"expected UUID-shaped tag, got {seen_tag['v']!r}"
    )
    assert call.tag == seen_tag["v"]


# ---------------------------------------------------------------------------
# Failure paths
# ---------------------------------------------------------------------------


async def test_dial_failed_raises_relay_error(
    signalwire_relay_client, mock_relay
):
    """A pushed ``calling.call.dial(failed)`` event makes ``dial()`` raise."""
    # Push a failure event after a small delay so the SDK's pending future
    # is set up first.
    dial_failed = asyncio.Event()

    async def _push_failure():
        # Wait for the SDK's calling.dial frame to land.
        for _ in range(200):
            if mock_relay.journal_recv(method="calling.dial"):
                break
            await asyncio.sleep(0.01)
        mock_relay.push(
            {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "signalwire.event",
                "params": {
                    "event_type": "calling.call.dial",
                    "params": {
                        "tag": "t-fail",
                        "node_id": "node-mock-1",
                        "dial_state": "failed",
                        "call": {},
                    },
                },
            }
        )
        dial_failed.set()

    pusher = asyncio.create_task(_push_failure())
    try:
        with pytest.raises(RelayError, match="Dial failed"):
            await signalwire_relay_client.dial(
                [[_phone_device()]],
                tag="t-fail",
                dial_timeout=5.0,
            )
    finally:
        pusher.cancel()
        try:
            await pusher
        except asyncio.CancelledError:
            pass


async def test_dial_timeout_when_no_dial_event(
    signalwire_relay_client, mock_relay
):
    """No scripted dial event → SDK times out cleanly."""
    # Don't arm any dial scenario.
    with pytest.raises(RelayError, match="timed out"):
        await signalwire_relay_client.dial(
            [[_phone_device()]],
            tag="t-timeout",
            dial_timeout=0.5,
        )


# ---------------------------------------------------------------------------
# Parallel dial — winner + losers
# ---------------------------------------------------------------------------


async def test_dial_winner_carries_dial_winner_true(
    signalwire_relay_client, mock_relay
):
    """The mock's emitted ``calling.call.dial`` event carries ``dial_winner: true``."""
    mock_relay.arm_dial(
        tag="t-winner",
        winner_call_id="WIN-ID",
        states=["created", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
        losers=[
            {"call_id": "LOSE-A", "states": ["created", "ended"]},
            {"call_id": "LOSE-B", "states": ["created", "ended"]},
        ],
    )
    call = await signalwire_relay_client.dial(
        [[_phone_device()]],
        tag="t-winner",
        dial_timeout=5.0,
    )
    assert call.call_id == "WIN-ID"

    # Verify the server-pushed dial event in the journal carries dial_winner.
    sends = mock_relay.journal_send(event_type="calling.call.dial")
    assert sends, "no calling.call.dial event was pushed"
    [final] = [
        e for e in sends
        if (e.frame.get("params", {}).get("params", {}).get("dial_state") == "answered")
    ]
    inner = final.frame["params"]["params"]
    assert inner["call"]["dial_winner"] is True
    assert inner["call"]["call_id"] == "WIN-ID"


async def test_dial_losers_get_state_events(signalwire_relay_client, mock_relay):
    """Loser legs receive their own state events ending in ``ended``."""
    mock_relay.arm_dial(
        tag="t-losers",
        winner_call_id="WIN-2",
        states=["created", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
        losers=[
            {"call_id": "L1", "states": ["created", "ended"]},
        ],
    )
    await signalwire_relay_client.dial(
        [[_phone_device()]],
        tag="t-losers",
        dial_timeout=5.0,
    )
    state_events = mock_relay.journal_send(event_type="calling.call.state")
    loser_states = [
        e.frame["params"]["params"]
        for e in state_events
        if e.frame["params"]["params"].get("call_id") == "L1"
    ]
    assert any(s.get("call_state") == "ended" for s in loser_states), (
        f"loser L1 never reached 'ended'; saw: {loser_states}"
    )


async def test_dial_losers_cleaned_up_from_calls_dict(
    signalwire_relay_client, mock_relay
):
    """The SDK removes ended loser calls from its internal _calls registry."""
    mock_relay.arm_dial(
        tag="t-cleanup",
        winner_call_id="WIN-CL",
        states=["created", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
        losers=[
            {"call_id": "LOSE-CL", "states": ["created", "ended"]},
        ],
    )
    call = await signalwire_relay_client.dial(
        [[_phone_device()]],
        tag="t-cleanup",
        dial_timeout=5.0,
    )
    # Give time for state events to flow through.
    await asyncio.sleep(0.1)
    assert "LOSE-CL" not in signalwire_relay_client._calls
    # Winner is still present.
    assert call.call_id in signalwire_relay_client._calls


# ---------------------------------------------------------------------------
# Devices shape on the wire
# ---------------------------------------------------------------------------


async def test_dial_devices_serial_two_legs_on_wire(
    signalwire_relay_client, mock_relay
):
    """Serial dial (one leg with multiple devices) flows through correctly."""
    mock_relay.arm_dial(
        tag="t-serial",
        winner_call_id="WIN-SER",
        states=["created", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
    )
    devs = [
        [
            _phone_device(to="+15551110001"),
            _phone_device(to="+15551110002"),
        ]
    ]
    await signalwire_relay_client.dial(
        devs, tag="t-serial", dial_timeout=5.0
    )
    [entry] = mock_relay.journal_recv(method="calling.dial")
    assert len(entry.frame["params"]["devices"]) == 1
    assert len(entry.frame["params"]["devices"][0]) == 2
    assert (
        entry.frame["params"]["devices"][0][0]["params"]["to_number"]
        == "+15551110001"
    )


async def test_dial_devices_parallel_two_legs_on_wire(
    signalwire_relay_client, mock_relay
):
    """Parallel dial (two legs) flows through correctly."""
    mock_relay.arm_dial(
        tag="t-par",
        winner_call_id="WIN-PAR",
        states=["created", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
    )
    devs = [
        [_phone_device(to="+15551110001")],
        [_phone_device(to="+15551110002")],
    ]
    await signalwire_relay_client.dial(devs, tag="t-par", dial_timeout=5.0)
    [entry] = mock_relay.journal_recv(method="calling.dial")
    assert len(entry.frame["params"]["devices"]) == 2


# ---------------------------------------------------------------------------
# State transitions during dial
# ---------------------------------------------------------------------------


async def test_dial_records_call_state_progression_on_winner(
    signalwire_relay_client, mock_relay
):
    """The winner's state events flow created → ringing → answered."""
    mock_relay.arm_dial(
        tag="t-prog",
        winner_call_id="WIN-PROG",
        states=["created", "ringing", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
    )
    call = await signalwire_relay_client.dial(
        [[_phone_device()]], tag="t-prog", dial_timeout=5.0
    )
    # By the time dial() returns, all state events have been pushed.
    state_events = mock_relay.journal_send(event_type="calling.call.state")
    winner_states = [
        e.frame["params"]["params"]["call_state"]
        for e in state_events
        if e.frame["params"]["params"].get("call_id") == "WIN-PROG"
    ]
    assert "created" in winner_states
    assert "ringing" in winner_states
    assert "answered" in winner_states
    assert call.state == "answered"


# ---------------------------------------------------------------------------
# After dial — call object is usable
# ---------------------------------------------------------------------------


async def test_dialed_call_can_send_subsequent_command(
    signalwire_relay_client, mock_relay
):
    """A dial-winner Call can be used to issue further RELAY commands."""
    mock_relay.arm_dial(
        tag="t-after",
        winner_call_id="WIN-AFTER",
        states=["created", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
    )
    call = await signalwire_relay_client.dial(
        [[_phone_device()]], tag="t-after", dial_timeout=5.0
    )
    # Issue a hangup — ensures the SDK has the call_id + node_id and the
    # mock accepts the calling.end frame.
    await call.hangup()
    end_frames = mock_relay.journal_recv(method="calling.end")
    assert end_frames, "no calling.end frame in journal"
    assert end_frames[-1].frame["params"]["call_id"] == "WIN-AFTER"


async def test_dialed_call_can_play(signalwire_relay_client, mock_relay):
    """A dialed (outbound) call can issue calling.play via the same Call object."""
    mock_relay.arm_dial(
        tag="t-play",
        winner_call_id="WIN-PLAY",
        states=["created", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
    )
    call = await signalwire_relay_client.dial(
        [[_phone_device()]], tag="t-play", dial_timeout=5.0
    )
    await call.play([{"type": "tts", "params": {"text": "hi"}}])
    play_frames = mock_relay.journal_recv(method="calling.play")
    assert play_frames, "no calling.play frame after dial"
    p = play_frames[-1].frame["params"]
    assert p["call_id"] == "WIN-PLAY"
    assert p["play"][0]["type"] == "tts"


# ---------------------------------------------------------------------------
# Tag preservation
# ---------------------------------------------------------------------------


async def test_dial_preserves_explicit_tag(signalwire_relay_client, mock_relay):
    """An explicit tag flows verbatim into the SDK's Call.tag."""
    mock_relay.arm_dial(
        tag="my-very-explicit-tag-99",
        winner_call_id="WIN-T",
        states=["created", "answered"],
        node_id="node-mock-1",
        device=_phone_device(),
    )
    call = await signalwire_relay_client.dial(
        [[_phone_device()]],
        tag="my-very-explicit-tag-99",
        dial_timeout=5.0,
    )
    assert call.tag == "my-very-explicit-tag-99"


# ---------------------------------------------------------------------------
# JSON-RPC envelope
# ---------------------------------------------------------------------------


async def test_dial_uses_jsonrpc_2_0(signalwire_relay_client, mock_relay):
    """The dial frame on the wire is JSON-RPC 2.0 with id+method+params."""
    mock_relay.arm_dial(
        tag="t-rpc",
        winner_call_id="W",
        states=["created", "answered"],
        node_id="n",
        device=_phone_device(),
    )
    await signalwire_relay_client.dial(
        [[_phone_device()]], tag="t-rpc", dial_timeout=5.0
    )
    [entry] = mock_relay.journal_recv(method="calling.dial")
    assert entry.frame["jsonrpc"] == "2.0"
    assert entry.frame["method"] == "calling.dial"
    assert "id" in entry.frame
    assert "params" in entry.frame
