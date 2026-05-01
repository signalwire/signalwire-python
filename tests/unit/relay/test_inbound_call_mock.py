"""Real-mock-backed tests for inbound calls (server-initiated).

The mock's ``POST /__mock__/inbound_call`` endpoint pushes a
``calling.call.receive`` frame to the SDK — exactly what the production
RELAY server emits when a phone call arrives in a context the SDK
subscribed to.

These tests verify:

1. The SDK's ``@client.on_call`` handler fires with a Call object whose
   fields reflect the wire frame.
2. Whatever the handler does next (answer, reject, play, ...) appears in
   the mock journal as the right ``calling.<verb>`` frame.
3. State events injected after the SDK answers progress the Call's state.
"""

from __future__ import annotations

import asyncio
import uuid

import pytest

from signalwire.relay.client import RelayClient, _active_clients
from signalwire.relay.call import Call

from .conftest import _RELAY_MOCK_AVAILABLE


pytestmark = pytest.mark.skipif(
    not _RELAY_MOCK_AVAILABLE,
    reason="mock_relay not adjacent — clone porting-sdk next to signalwire-python",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _state_push_frame(
    call_id: str, call_state: str, *, tag: str = "", direction: str = "inbound"
) -> dict:
    """Build a signalwire.event(calling.call.state) frame ready for /__mock__/push."""
    return {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "signalwire.event",
        "params": {
            "event_type": "calling.call.state",
            "params": {
                "call_id": call_id,
                "node_id": "mock-relay-node-1",
                "tag": tag,
                "call_state": call_state,
                "direction": direction,
                "device": {
                    "type": "phone",
                    "params": {
                        "from_number": "+15551110000",
                        "to_number": "+15552220000",
                    },
                },
            },
        },
    }


# ---------------------------------------------------------------------------
# Basic inbound-call handler dispatch
# ---------------------------------------------------------------------------


async def test_on_call_handler_fires_with_call_object(
    signalwire_relay_client, mock_relay
):
    """A pushed inbound call invokes the registered on_call handler."""
    seen: list[Call] = []
    handler_done = asyncio.Event()

    @signalwire_relay_client.on_call
    async def handle(call):
        seen.append(call)
        handler_done.set()

    mock_relay.inbound_call(
        call_id="c-handler",
        from_number="+15551110000",
        to_number="+15552220000",
        auto_states=["created"],
    )
    await asyncio.wait_for(handler_done.wait(), timeout=5)

    assert len(seen) == 1
    assert isinstance(seen[0], Call)
    assert seen[0].call_id == "c-handler"


async def test_inbound_call_object_has_correct_call_id_and_direction(
    signalwire_relay_client, mock_relay
):
    """The Call object exposes the inbound call_id and direction."""
    handler_done = asyncio.Event()
    seen: dict[str, str] = {}

    @signalwire_relay_client.on_call
    async def handle(call):
        seen["call_id"] = call.call_id
        seen["direction"] = call.direction
        handler_done.set()

    mock_relay.inbound_call(call_id="c-dir", auto_states=["created"])
    await asyncio.wait_for(handler_done.wait(), timeout=5)

    assert seen["call_id"] == "c-dir"
    assert seen["direction"] == "inbound"


async def test_inbound_call_carries_from_to_in_device(
    signalwire_relay_client, mock_relay
):
    """The Call's ``device`` reflects from_number/to_number from the wire."""
    handler_done = asyncio.Event()
    seen: dict = {}

    @signalwire_relay_client.on_call
    async def handle(call):
        seen["device"] = call.device
        handler_done.set()

    mock_relay.inbound_call(
        call_id="c-from-to",
        from_number="+15551112233",
        to_number="+15554445566",
        auto_states=["created"],
    )
    await asyncio.wait_for(handler_done.wait(), timeout=5)

    params = seen["device"].get("params", {})
    assert params.get("from_number") == "+15551112233"
    assert params.get("to_number") == "+15554445566"


async def test_inbound_call_initial_state_is_created(
    signalwire_relay_client, mock_relay
):
    """The Call's initial state matches the first auto_state pushed."""
    seen: dict[str, str] = {}
    done = asyncio.Event()

    @signalwire_relay_client.on_call
    async def handle(call):
        seen["state"] = call.state
        done.set()

    mock_relay.inbound_call(call_id="c-state", auto_states=["created"])
    await asyncio.wait_for(done.wait(), timeout=5)
    assert seen["state"] == "created"


# ---------------------------------------------------------------------------
# Handler answers — calling.answer journaled
# ---------------------------------------------------------------------------


async def test_answer_in_handler_journals_calling_answer(
    signalwire_relay_client, mock_relay
):
    """When the handler answers, calling.answer appears in the journal."""
    answered = asyncio.Event()

    @signalwire_relay_client.on_call
    async def handle(call):
        await call.answer()
        answered.set()

    mock_relay.inbound_call(call_id="c-ans", auto_states=["created"])
    await asyncio.wait_for(answered.wait(), timeout=5)
    # Allow the answer round-trip to land.
    await asyncio.sleep(0.1)

    answers = mock_relay.journal_recv(method="calling.answer")
    assert answers, "no calling.answer frame in journal"
    assert answers[-1].frame["params"]["call_id"] == "c-ans"


async def test_answer_then_state_event_advances_call_state(
    signalwire_relay_client, mock_relay
):
    """Pushing ``answered`` after the SDK answers updates Call.state."""
    captured: dict[str, Call] = {}
    handler_returned = asyncio.Event()

    @signalwire_relay_client.on_call
    async def handle(call):
        captured["call"] = call
        await call.answer()
        handler_returned.set()

    mock_relay.inbound_call(call_id="c-ans-state", auto_states=["created"])
    await asyncio.wait_for(handler_returned.wait(), timeout=5)

    # Now push a state(answered) update.
    mock_relay.push(_state_push_frame("c-ans-state", "answered"))
    # Wait for the SDK's recv loop to process.
    for _ in range(100):
        if captured["call"].state == "answered":
            break
        await asyncio.sleep(0.02)
    assert captured["call"].state == "answered"


# ---------------------------------------------------------------------------
# Handler hangs up / passes
# ---------------------------------------------------------------------------


async def test_hangup_in_handler_journals_calling_end(
    signalwire_relay_client, mock_relay
):
    """``call.hangup()`` from the handler journals a calling.end frame."""
    hung = asyncio.Event()

    @signalwire_relay_client.on_call
    async def handle(call):
        await call.hangup(reason="busy")
        hung.set()

    mock_relay.inbound_call(call_id="c-hangup", auto_states=["created"])
    await asyncio.wait_for(hung.wait(), timeout=5)
    await asyncio.sleep(0.1)

    ends = mock_relay.journal_recv(method="calling.end")
    assert ends, "no calling.end frame in journal"
    p = ends[-1].frame["params"]
    assert p["call_id"] == "c-hangup"
    assert p["reason"] == "busy"


async def test_pass_in_handler_journals_calling_pass(
    signalwire_relay_client, mock_relay
):
    """``call.pass_()`` from the handler journals a calling.pass frame."""
    passed = asyncio.Event()

    @signalwire_relay_client.on_call
    async def handle(call):
        await call.pass_()
        passed.set()

    mock_relay.inbound_call(call_id="c-pass", auto_states=["created"])
    await asyncio.wait_for(passed.wait(), timeout=5)
    await asyncio.sleep(0.1)

    passes = mock_relay.journal_recv(method="calling.pass")
    assert passes, "no calling.pass frame in journal"
    assert passes[-1].frame["params"]["call_id"] == "c-pass"


# ---------------------------------------------------------------------------
# Multiple inbound calls — independent state
# ---------------------------------------------------------------------------


async def test_multiple_inbound_calls_in_sequence_each_unique_object(
    signalwire_relay_client, mock_relay
):
    """Two inbound calls give the handler two distinct Call objects."""
    seen: list[Call] = []
    received = asyncio.Event()

    @signalwire_relay_client.on_call
    async def handle(call):
        seen.append(call)
        if len(seen) == 2:
            received.set()

    mock_relay.inbound_call(call_id="c-seq-1", auto_states=["created"])
    await asyncio.sleep(0.1)
    mock_relay.inbound_call(call_id="c-seq-2", auto_states=["created"])
    await asyncio.wait_for(received.wait(), timeout=5)

    assert seen[0].call_id == "c-seq-1"
    assert seen[1].call_id == "c-seq-2"
    assert seen[0] is not seen[1]


async def test_multiple_inbound_calls_no_state_bleed(
    signalwire_relay_client, mock_relay
):
    """State on one inbound call doesn't leak to another."""
    calls_by_id: dict[str, Call] = {}
    both_received = asyncio.Event()

    @signalwire_relay_client.on_call
    async def handle(call):
        calls_by_id[call.call_id] = call
        await call.answer()
        if len(calls_by_id) == 2:
            both_received.set()

    mock_relay.inbound_call(call_id="cb-1", auto_states=["created"])
    await asyncio.sleep(0.05)
    mock_relay.inbound_call(call_id="cb-2", auto_states=["created"])
    await asyncio.wait_for(both_received.wait(), timeout=5)

    # Push answered to only cb-1
    mock_relay.push(_state_push_frame("cb-1", "answered"))
    # Wait for state propagation.
    for _ in range(100):
        if calls_by_id["cb-1"].state == "answered":
            break
        await asyncio.sleep(0.02)
    # cb-1 advances; cb-2 stays put.
    assert calls_by_id["cb-1"].state == "answered"
    assert calls_by_id["cb-2"].state != "answered"


# ---------------------------------------------------------------------------
# Scripted state sequences
# ---------------------------------------------------------------------------


async def test_scripted_state_sequence_advances_call(
    signalwire_relay_client, mock_relay
):
    """Pushing answered then ended advances the Call state, then it's cleaned up."""
    captured: dict[str, Call] = {}
    handler_done = asyncio.Event()

    @signalwire_relay_client.on_call
    async def handle(call):
        captured["call"] = call
        await call.answer()
        handler_done.set()

    mock_relay.inbound_call(call_id="c-scripted", auto_states=["created"])
    await asyncio.wait_for(handler_done.wait(), timeout=5)

    mock_relay.push(_state_push_frame("c-scripted", "answered"))
    mock_relay.push(_state_push_frame("c-scripted", "ended"))
    # Wait for both events to flow.
    for _ in range(100):
        if captured["call"].state == "ended":
            break
        await asyncio.sleep(0.02)
    assert captured["call"].state == "ended"
    # Ended calls are dropped from the registry.
    assert "c-scripted" not in signalwire_relay_client._calls


# ---------------------------------------------------------------------------
# Handler patterns: async, sync, raise
# ---------------------------------------------------------------------------


async def test_async_handler_completes_normally(signalwire_relay_client, mock_relay):
    """Async handlers run to completion and observe the right call_id."""
    fired = asyncio.Event()
    seen: dict[str, str] = {}

    @signalwire_relay_client.on_call
    async def handle(call):
        await asyncio.sleep(0.01)
        seen["call_id"] = call.call_id
        fired.set()

    mock_relay.inbound_call(call_id="c-async", auto_states=["created"])
    await asyncio.wait_for(fired.wait(), timeout=5)
    assert seen["call_id"] == "c-async"


async def test_handler_exception_does_not_crash_client(
    signalwire_relay_client, mock_relay
):
    """A raising handler is caught; the client stays usable."""
    fired = asyncio.Event()

    @signalwire_relay_client.on_call
    async def handle(call):
        fired.set()
        raise RuntimeError("intentional from handler")

    mock_relay.inbound_call(call_id="c-raise", auto_states=["created"])
    await asyncio.wait_for(fired.wait(), timeout=5)
    # Give the handler exception time to be caught & logged.
    await asyncio.sleep(0.1)

    # The client is still alive.
    assert signalwire_relay_client._connected is True


# ---------------------------------------------------------------------------
# scenario_play — full inbound flow
# ---------------------------------------------------------------------------


async def test_scenario_play_full_inbound_flow(
    signalwire_relay_client, mock_relay
):
    """A scripted scenario_play timeline drives a full inbound-call flow."""
    handler_started = asyncio.Event()
    captured: dict[str, Call] = {}

    @signalwire_relay_client.on_call
    async def handle(call):
        captured["call"] = call
        await call.answer()
        handler_started.set()

    # The scenario:
    # 1. Push calling.call.receive(created)
    # 2. Wait for the SDK to send calling.answer
    # 3. Push calling.call.state(answered)
    # 4. Push calling.call.state(ended)
    timeline = [
        {
            "push": {
                "frame": {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "signalwire.event",
                    "params": {
                        "event_type": "calling.call.receive",
                        "params": {
                            "call_id": "c-scen",
                            "node_id": "mock-relay-node-1",
                            "tag": "",
                            "call_state": "created",
                            "direction": "inbound",
                            "device": {
                                "type": "phone",
                                "params": {
                                    "from_number": "+15551110000",
                                    "to_number": "+15552220000",
                                },
                            },
                            "context": "default",
                        },
                    },
                }
            }
        },
        {"expect_recv": {"method": "calling.answer", "timeout_ms": 5000}},
        {"push": {"frame": _state_push_frame("c-scen", "answered")}},
        {"sleep_ms": 50},
        {"push": {"frame": _state_push_frame("c-scen", "ended")}},
    ]
    result = await asyncio.to_thread(mock_relay.scenario_play, timeline)
    assert result["status"] == "completed", f"scenario didn't complete: {result}"
    assert handler_started.is_set()

    # Wait for the final state to land.
    for _ in range(100):
        if captured["call"].state == "ended":
            break
        await asyncio.sleep(0.02)
    assert captured["call"].state == "ended"


# ---------------------------------------------------------------------------
# Wire shape — calling.call.receive
# ---------------------------------------------------------------------------


async def test_inbound_call_journal_send_records_calling_call_receive(
    signalwire_relay_client, mock_relay
):
    """The mock's outbound journal contains the calling.call.receive frame."""
    handler_done = asyncio.Event()

    @signalwire_relay_client.on_call
    async def handle(call):
        handler_done.set()

    mock_relay.inbound_call(call_id="c-wire", auto_states=["created"])
    await asyncio.wait_for(handler_done.wait(), timeout=5)

    sends = mock_relay.journal_send(event_type="calling.call.receive")
    assert sends, "no calling.call.receive frame in journal"
    inner = sends[-1].frame["params"]["params"]
    assert inner["call_id"] == "c-wire"
    assert inner["direction"] == "inbound"


# ---------------------------------------------------------------------------
# Inbound without a registered handler — does not crash
# ---------------------------------------------------------------------------


async def test_inbound_without_handler_does_not_crash(mock_relay, relay_ws_redirect):
    """An inbound call when no @on_call is registered is logged, not raised."""
    _active_clients.clear()
    with relay_ws_redirect:
        client = RelayClient(
            project="p", token="t", host=mock_relay.relay_host, contexts=["default"]
        )
        try:
            await client.connect()
            # No on_call registered.
            mock_relay.inbound_call(call_id="c-nohandler", auto_states=["created"])
            # Give the recv loop time to process.
            await asyncio.sleep(0.2)
            # Client is still alive.
            assert client._connected is True
        finally:
            await client.disconnect()
    _active_clients.clear()
