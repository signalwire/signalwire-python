"""Real-mock-backed tests for Action classes.

For each major action (Play, Record, Detect, Collect, PlayAndCollect, Pay,
Fax, Tap, Stream, Transcribe, AI), drive the SDK against the mock and
assert:

1. The on-wire ``calling.<verb>`` frame carries node_id/call_id/control_id
   per RELAY_IMPLEMENTATION_GUIDE.md.
2. Mock-pushed state events progress the action.
3. Terminal state events resolve ``await action.wait()``.
4. ``action.stop()`` (and pause/resume/volume where applicable) journals
   the right sub-command frame.
5. ``on_completed=callback`` fires on terminal events.
6. The play_and_collect gotcha — only the collect-side terminal event
   resolves (a play(finished) earlier doesn't).
7. The detect gotcha — detect resolves on first ``detect`` payload, not
   on a state(finished).
"""

from __future__ import annotations

import asyncio
import uuid

import pytest

from signalwire.relay.call import (
    AIAction,
    CollectAction,
    DetectAction,
    FaxAction,
    PayAction,
    PlayAction,
    RecordAction,
    StandaloneCollectAction,
    StreamAction,
    TapAction,
    TranscribeAction,
)
from signalwire.relay.event import RelayEvent

from .conftest import _RELAY_MOCK_AVAILABLE


pytestmark = pytest.mark.skipif(
    not _RELAY_MOCK_AVAILABLE,
    reason="mock_relay not adjacent — clone porting-sdk next to signalwire-python",
)


# ---------------------------------------------------------------------------
# Helpers — establish an inbound call we can issue actions on
# ---------------------------------------------------------------------------


async def _answered_inbound_call(client, mock_relay, call_id: str = "act-call-1"):
    """Push an inbound call, wait for the handler to capture it, return it."""
    captured: dict[str, object] = {}
    handler_returned = asyncio.Event()

    @client.on_call
    async def _handle(call):
        captured["call"] = call
        await call.answer()
        handler_returned.set()

    mock_relay.inbound_call(call_id=call_id, auto_states=["created"])
    await asyncio.wait_for(handler_returned.wait(), timeout=5)
    # Mark the call as answered so subsequent actions don't think it's gone.
    call = captured["call"]
    call.state = "answered"
    return call


# ---------------------------------------------------------------------------
# PlayAction
# ---------------------------------------------------------------------------


async def test_play_journals_calling_play(signalwire_relay_client, mock_relay):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-play"
    )
    await call.play(
        [{"type": "tts", "params": {"text": "hi"}}],
        control_id="play-ctl-1",
    )
    [entry] = mock_relay.journal_recv(method="calling.play")
    p = entry.frame["params"]
    assert p["call_id"] == "call-play"
    assert p["control_id"] == "play-ctl-1"
    assert p["play"][0]["type"] == "tts"


async def test_play_resolves_on_finished_event(signalwire_relay_client, mock_relay):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-play-fin"
    )
    mock_relay.arm_method(
        "calling.play",
        [
            {"emit": {"state": "playing"}, "delay_ms": 1},
            {"emit": {"state": "finished"}, "delay_ms": 5},
        ],
    )
    action = await call.play(
        [{"type": "silence", "params": {"duration": 1}}],
        control_id="play-ctl-fin",
    )
    assert isinstance(action, PlayAction)
    event = await action.wait(timeout=5)
    assert action.is_done is True
    assert event.params.get("state") == "finished"


async def test_play_stop_journals_play_stop(signalwire_relay_client, mock_relay):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-play-stop"
    )
    action = await call.play(
        [{"type": "silence", "params": {"duration": 60}}],
        control_id="play-ctl-stop",
    )
    await action.stop()
    stops = mock_relay.journal_recv(method="calling.play.stop")
    assert stops, "no calling.play.stop frame"
    assert stops[-1].frame["params"]["control_id"] == "play-ctl-stop"


async def test_play_pause_resume_volume_journal(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-play-prv"
    )
    action = await call.play(
        [{"type": "silence", "params": {"duration": 60}}],
        control_id="play-ctl-prv",
    )
    await action.pause()
    await action.resume()
    await action.volume(-3.0)

    assert mock_relay.journal_recv(method="calling.play.pause")
    assert mock_relay.journal_recv(method="calling.play.resume")
    vol = mock_relay.journal_recv(method="calling.play.volume")
    assert vol and vol[-1].frame["params"]["volume"] == -3.0


async def test_play_on_completed_callback_fires(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-play-cb"
    )
    mock_relay.arm_method(
        "calling.play",
        [{"emit": {"state": "finished"}, "delay_ms": 1}],
    )
    callback_fired = asyncio.Event()
    seen_event: dict[str, RelayEvent] = {}

    def on_done(event):
        seen_event["e"] = event
        callback_fired.set()

    action = await call.play(
        [{"type": "silence", "params": {"duration": 1}}],
        control_id="play-ctl-cb",
        on_completed=on_done,
    )
    await action.wait(timeout=5)
    await asyncio.wait_for(callback_fired.wait(), timeout=2)
    assert seen_event["e"].params.get("state") == "finished"


# ---------------------------------------------------------------------------
# RecordAction
# ---------------------------------------------------------------------------


async def test_record_journals_calling_record(signalwire_relay_client, mock_relay):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-rec"
    )
    await call.record(
        audio={"format": "mp3"},
        control_id="rec-ctl-1",
    )
    [entry] = mock_relay.journal_recv(method="calling.record")
    p = entry.frame["params"]
    assert p["call_id"] == "call-rec"
    assert p["control_id"] == "rec-ctl-1"
    assert p["record"]["audio"]["format"] == "mp3"


async def test_record_resolves_on_finished_event(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-rec-fin"
    )
    mock_relay.arm_method(
        "calling.record",
        [
            {"emit": {"state": "recording"}, "delay_ms": 1},
            {"emit": {"state": "finished", "url": "http://r.wav"}, "delay_ms": 5},
        ],
    )
    action = await call.record(
        audio={"format": "wav"}, control_id="rec-ctl-fin"
    )
    assert isinstance(action, RecordAction)
    event = await action.wait(timeout=5)
    assert event.params.get("state") == "finished"


async def test_record_stop_journals_record_stop(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-rec-stop"
    )
    action = await call.record(
        audio={"format": "wav"}, control_id="rec-ctl-stop"
    )
    await action.stop()
    stops = mock_relay.journal_recv(method="calling.record.stop")
    assert stops and stops[-1].frame["params"]["control_id"] == "rec-ctl-stop"


# ---------------------------------------------------------------------------
# DetectAction — gotcha: resolves on first detect payload
# ---------------------------------------------------------------------------


async def test_detect_resolves_on_first_detect_payload(
    signalwire_relay_client, mock_relay
):
    """Detect resolves on the first ``params.detect`` payload, not on state."""
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-det"
    )
    mock_relay.arm_method(
        "calling.detect",
        [
            # First payload: a real detect result. Should resolve.
            {
                "emit": {
                    "detect": {"type": "machine", "params": {"event": "MACHINE"}}
                },
                "delay_ms": 1,
            },
            # Then a finished — but we already resolved on the first.
            {"emit": {"state": "finished"}, "delay_ms": 10},
        ],
    )
    action = await call.detect(
        detect={"type": "machine", "params": {}},
        control_id="det-ctl-1",
    )
    assert isinstance(action, DetectAction)
    event = await action.wait(timeout=5)
    # Resolved with the detect payload, not the state(finished).
    assert event.params.get("detect", {}).get("type") == "machine"


async def test_detect_stop_journals_detect_stop(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-det-stop"
    )
    action = await call.detect(
        detect={"type": "fax", "params": {}}, control_id="det-stop"
    )
    await action.stop()
    stops = mock_relay.journal_recv(method="calling.detect.stop")
    assert stops and stops[-1].frame["params"]["control_id"] == "det-stop"


# ---------------------------------------------------------------------------
# CollectAction (play_and_collect) — gotcha: ignore play(finished)
# ---------------------------------------------------------------------------


async def test_play_and_collect_journals_play_and_collect(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-pac"
    )
    await call.play_and_collect(
        media=[{"type": "tts", "params": {"text": "Press 1"}}],
        collect={"digits": {"max": 1}},
        control_id="pac-ctl-1",
    )
    [entry] = mock_relay.journal_recv(method="calling.play_and_collect")
    p = entry.frame["params"]
    assert p["call_id"] == "call-pac"
    assert p["play"][0]["type"] == "tts"
    assert p["collect"]["digits"]["max"] == 1


async def test_play_and_collect_resolves_on_collect_event_only(
    signalwire_relay_client, mock_relay
):
    """Per RELAY_IMPLEMENTATION_GUIDE: ignore play(finished); resolve on collect.

    The mock's default event_type for ``calling.play_and_collect`` is
    ``calling.call.play_and_collect`` — but the SDK listens on
    ``calling.call.collect`` for collect terminal events. We simulate a real
    server here by pushing a ``calling.call.play(finished)`` first (must NOT
    resolve), then a ``calling.call.collect(result=...)`` (resolves).
    """
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-pac-go"
    )
    action = await call.play_and_collect(
        media=[{"type": "silence", "params": {"duration": 1}}],
        collect={"digits": {"max": 1}},
        control_id="pac-go",
    )
    assert isinstance(action, CollectAction)
    # Push a play(finished) — the action MUST NOT resolve.
    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "signalwire.event",
            "params": {
                "event_type": "calling.call.play",
                "params": {
                    "call_id": "call-pac-go",
                    "control_id": "pac-go",
                    "state": "finished",
                },
            },
        }
    )
    await asyncio.sleep(0.1)
    assert action.is_done is False, (
        "play_and_collect resolved on play(finished); should wait for collect"
    )

    # Now push the collect event — action resolves.
    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "signalwire.event",
            "params": {
                "event_type": "calling.call.collect",
                "params": {
                    "call_id": "call-pac-go",
                    "control_id": "pac-go",
                    "result": {"type": "digit", "params": {"digits": "1"}},
                },
            },
        }
    )
    event = await action.wait(timeout=2)
    assert event.event_type == "calling.call.collect"
    assert event.params.get("result", {}).get("type") == "digit"


async def test_play_and_collect_stop_journals_pac_stop(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-pac-stop"
    )
    action = await call.play_and_collect(
        media=[{"type": "silence", "params": {"duration": 1}}],
        collect={"digits": {"max": 1}},
        control_id="pac-stop",
    )
    await action.stop()
    stops = mock_relay.journal_recv(method="calling.play_and_collect.stop")
    assert stops and stops[-1].frame["params"]["control_id"] == "pac-stop"


# ---------------------------------------------------------------------------
# StandaloneCollectAction
# ---------------------------------------------------------------------------


async def test_collect_journals_calling_collect(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-col"
    )
    action = await call.collect(
        digits={"max": 4}, control_id="col-ctl"
    )
    assert isinstance(action, StandaloneCollectAction)
    [entry] = mock_relay.journal_recv(method="calling.collect")
    assert entry.frame["params"]["digits"] == {"max": 4}
    assert entry.frame["params"]["control_id"] == "col-ctl"


async def test_collect_stop_journals_collect_stop(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-col-stop"
    )
    action = await call.collect(
        digits={"max": 4}, control_id="col-stop"
    )
    await action.stop()
    stops = mock_relay.journal_recv(method="calling.collect.stop")
    assert stops and stops[-1].frame["params"]["control_id"] == "col-stop"


# ---------------------------------------------------------------------------
# PayAction
# ---------------------------------------------------------------------------


async def test_pay_journals_calling_pay(signalwire_relay_client, mock_relay):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-pay"
    )
    await call.pay(
        payment_connector_url="https://pay.example/connect",
        control_id="pay-ctl",
        charge_amount="9.99",
    )
    [entry] = mock_relay.journal_recv(method="calling.pay")
    p = entry.frame["params"]
    assert p["payment_connector_url"] == "https://pay.example/connect"
    assert p["control_id"] == "pay-ctl"
    assert p["charge_amount"] == "9.99"


async def test_pay_returns_pay_action(signalwire_relay_client, mock_relay):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-pay-act"
    )
    action = await call.pay(
        payment_connector_url="https://pay.example/connect",
        control_id="pay-act",
    )
    assert isinstance(action, PayAction)
    assert action.control_id == "pay-act"


async def test_pay_stop_journals_pay_stop(signalwire_relay_client, mock_relay):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-pay-stop"
    )
    action = await call.pay(
        payment_connector_url="https://pay.example/connect",
        control_id="pay-stop",
    )
    await action.stop()
    stops = mock_relay.journal_recv(method="calling.pay.stop")
    assert stops and stops[-1].frame["params"]["control_id"] == "pay-stop"


# ---------------------------------------------------------------------------
# FaxAction
# ---------------------------------------------------------------------------


async def test_send_fax_journals_calling_send_fax(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-sfax"
    )
    await call.send_fax(
        document="https://docs.example/test.pdf",
        identity="+15551112222",
        control_id="sfax-ctl",
    )
    [entry] = mock_relay.journal_recv(method="calling.send_fax")
    p = entry.frame["params"]
    assert p["document"] == "https://docs.example/test.pdf"
    assert p["identity"] == "+15551112222"
    assert p["control_id"] == "sfax-ctl"


async def test_receive_fax_returns_fax_action(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-rfax"
    )
    action = await call.receive_fax(control_id="rfax-ctl")
    assert isinstance(action, FaxAction)


# ---------------------------------------------------------------------------
# TapAction
# ---------------------------------------------------------------------------


async def test_tap_journals_calling_tap(signalwire_relay_client, mock_relay):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-tap"
    )
    await call.tap(
        tap={"type": "audio"},
        device={"type": "rtp", "params": {"addr": "203.0.113.1", "port": 4000}},
        control_id="tap-ctl",
    )
    [entry] = mock_relay.journal_recv(method="calling.tap")
    p = entry.frame["params"]
    assert p["tap"] == {"type": "audio"}
    assert p["device"]["params"]["port"] == 4000
    assert p["control_id"] == "tap-ctl"


async def test_tap_stop_journals_tap_stop(signalwire_relay_client, mock_relay):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-tap-stop"
    )
    action = await call.tap(
        tap={"type": "audio"},
        device={"type": "rtp", "params": {"addr": "203.0.113.1", "port": 4000}},
        control_id="tap-stop",
    )
    assert isinstance(action, TapAction)
    await action.stop()
    stops = mock_relay.journal_recv(method="calling.tap.stop")
    assert stops and stops[-1].frame["params"]["control_id"] == "tap-stop"


# ---------------------------------------------------------------------------
# StreamAction
# ---------------------------------------------------------------------------


async def test_stream_journals_calling_stream(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-strm"
    )
    await call.stream(
        url="wss://stream.example/audio",
        codec="OPUS@48000h",
        control_id="strm-ctl",
    )
    [entry] = mock_relay.journal_recv(method="calling.stream")
    p = entry.frame["params"]
    assert p["url"] == "wss://stream.example/audio"
    assert p["codec"] == "OPUS@48000h"
    assert p["control_id"] == "strm-ctl"


async def test_stream_stop_journals_stream_stop(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-strm-stop"
    )
    action = await call.stream(
        url="wss://stream.example/audio", control_id="strm-stop"
    )
    assert isinstance(action, StreamAction)
    await action.stop()
    stops = mock_relay.journal_recv(method="calling.stream.stop")
    assert stops and stops[-1].frame["params"]["control_id"] == "strm-stop"


# ---------------------------------------------------------------------------
# TranscribeAction
# ---------------------------------------------------------------------------


async def test_transcribe_journals_calling_transcribe(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-tr"
    )
    action = await call.transcribe(control_id="tr-ctl")
    assert isinstance(action, TranscribeAction)
    [entry] = mock_relay.journal_recv(method="calling.transcribe")
    assert entry.frame["params"]["control_id"] == "tr-ctl"


async def test_transcribe_stop_journals_transcribe_stop(
    signalwire_relay_client, mock_relay
):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-tr-stop"
    )
    action = await call.transcribe(control_id="tr-stop")
    await action.stop()
    stops = mock_relay.journal_recv(method="calling.transcribe.stop")
    assert stops and stops[-1].frame["params"]["control_id"] == "tr-stop"


# ---------------------------------------------------------------------------
# AIAction
# ---------------------------------------------------------------------------


async def test_ai_journals_calling_ai(signalwire_relay_client, mock_relay):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-ai"
    )
    action = await call.ai(
        prompt={"text": "You are helpful."},
        control_id="ai-ctl",
    )
    assert isinstance(action, AIAction)
    [entry] = mock_relay.journal_recv(method="calling.ai")
    p = entry.frame["params"]
    assert p["prompt"] == {"text": "You are helpful."}
    assert p["control_id"] == "ai-ctl"


async def test_ai_stop_journals_ai_stop(signalwire_relay_client, mock_relay):
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-ai-stop"
    )
    action = await call.ai(
        prompt={"text": "You are helpful."}, control_id="ai-stop"
    )
    await action.stop()
    stops = mock_relay.journal_recv(method="calling.ai.stop")
    assert stops and stops[-1].frame["params"]["control_id"] == "ai-stop"


# ---------------------------------------------------------------------------
# General — control_id correlation across multiple concurrent actions
# ---------------------------------------------------------------------------


async def test_concurrent_play_and_record_route_independently(
    signalwire_relay_client, mock_relay
):
    """Two actions with different control_ids resolve independently."""
    call = await _answered_inbound_call(
        signalwire_relay_client, mock_relay, "call-multi"
    )
    play_action = await call.play(
        [{"type": "silence", "params": {"duration": 60}}],
        control_id="ctl-play-x",
    )
    record_action = await call.record(
        audio={"format": "wav"}, control_id="ctl-rec-y"
    )
    assert play_action.control_id == "ctl-play-x"
    assert record_action.control_id == "ctl-rec-y"

    # Push a finished event for ONLY the play.
    mock_relay.push(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "signalwire.event",
            "params": {
                "event_type": "calling.call.play",
                "params": {
                    "call_id": "call-multi",
                    "control_id": "ctl-play-x",
                    "state": "finished",
                },
            },
        }
    )
    await play_action.wait(timeout=2)
    assert play_action.is_done is True
    assert record_action.is_done is False
