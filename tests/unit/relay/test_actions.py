"""Unit tests for relay Action subclasses — direct construction and stop()/control methods.

These tests exercise the Action subclass __init__ methods directly and the
stop()/start_input_timers()/volume() commands they expose, complementing the
flow-based tests in test_call.py that go via Call.{play,record,...}().
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from signalwire.relay.call import (
    Action,
    AIAction,
    Call,
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
from signalwire.relay.constants import (
    CALL_STATE_ANSWERED,
    EVENT_CALL_COLLECT,
    EVENT_CALL_DETECT,
    EVENT_CALL_FAX,
    EVENT_CALL_PAY,
    EVENT_CALL_PLAY,
    EVENT_CALL_RECORD,
    EVENT_CALL_STREAM,
    EVENT_CALL_TAP,
    EVENT_CALL_TRANSCRIBE,
    PLAY_STATE_FINISHED,
    PLAY_STATE_ERROR,
    RECORD_STATE_FINISHED,
    RECORD_STATE_NO_INPUT,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_client():
    client = MagicMock()
    client.execute = AsyncMock(return_value={"code": "200", "message": "OK"})
    return client


@pytest.fixture
async def call(mock_client):
    return Call(
        client=mock_client,
        call_id="call-1",
        node_id="node-1",
        project_id="proj-1",
        context="office",
        state=CALL_STATE_ANSWERED,
        direction="inbound",
    )


# ---------------------------------------------------------------------------
# Base Action.__init__
# ---------------------------------------------------------------------------

class TestActionInit:
    """Direct construction of the base Action class — covers Action.__init__."""

    @pytest.mark.asyncio
    async def test_action_init_stores_attributes(self, call):
        base_action = Action(
            call,
            control_id="base-1",
            terminal_event="custom.event",
            terminal_states=("done", "error"),
        )
        assert base_action.call is call
        assert base_action.control_id == "base-1"
        assert base_action._terminal_event == "custom.event"
        assert base_action._terminal_states == ("done", "error")
        assert base_action.completed is False
        assert base_action.result is None
        assert base_action._on_completed is None
        assert not base_action.is_done


# ---------------------------------------------------------------------------
# PlayAction direct construction
# ---------------------------------------------------------------------------

class TestPlayActionInit:
    """PlayAction.__init__ via direct construction (not via Call.play)."""

    @pytest.mark.asyncio
    async def test_play_action_init(self, call):
        play_action = PlayAction(call, "ctl-play-1")
        assert play_action.control_id == "ctl-play-1"
        assert play_action.call is call
        assert play_action._terminal_event == EVENT_CALL_PLAY
        assert PLAY_STATE_FINISHED in play_action._terminal_states
        assert PLAY_STATE_ERROR in play_action._terminal_states
        assert not play_action.is_done


# ---------------------------------------------------------------------------
# RecordAction direct construction + pause/resume/stop
# ---------------------------------------------------------------------------

class TestRecordActionInit:
    @pytest.mark.asyncio
    async def test_record_action_init(self, call):
        record_action = RecordAction(call, "rec-1")
        assert record_action.control_id == "rec-1"
        assert record_action._terminal_event == EVENT_CALL_RECORD
        assert RECORD_STATE_FINISHED in record_action._terminal_states
        assert RECORD_STATE_NO_INPUT in record_action._terminal_states

    @pytest.mark.asyncio
    async def test_record_action_stop_sends_correct_rpc(self, call, mock_client):
        record_action = RecordAction(call, "rec-2")
        await record_action.stop()
        mock_client.execute.assert_called_once_with(
            "calling.record.stop",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "rec-2"},
        )

    @pytest.mark.asyncio
    async def test_record_action_pause_sends_correct_rpc(self, call, mock_client):
        record_action = RecordAction(call, "rec-3")
        await record_action.pause(behavior="silence")
        mock_client.execute.assert_called_once_with(
            "calling.record.pause",
            {
                "node_id": "node-1",
                "call_id": "call-1",
                "control_id": "rec-3",
                "behavior": "silence",
            },
        )

    @pytest.mark.asyncio
    async def test_record_action_pause_no_behavior(self, call, mock_client):
        record_action = RecordAction(call, "rec-4")
        await record_action.pause()
        mock_client.execute.assert_called_once_with(
            "calling.record.pause",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "rec-4"},
        )

    @pytest.mark.asyncio
    async def test_record_action_resume_sends_correct_rpc(self, call, mock_client):
        record_action = RecordAction(call, "rec-5")
        await record_action.resume()
        mock_client.execute.assert_called_once_with(
            "calling.record.resume",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "rec-5"},
        )


# ---------------------------------------------------------------------------
# DetectAction direct construction + stop
# ---------------------------------------------------------------------------

class TestDetectActionInit:
    @pytest.mark.asyncio
    async def test_detect_action_init(self, call):
        detect_action = DetectAction(call, "det-1")
        assert detect_action.control_id == "det-1"
        assert detect_action._terminal_event == EVENT_CALL_DETECT
        assert "finished" in detect_action._terminal_states
        assert "error" in detect_action._terminal_states

    @pytest.mark.asyncio
    async def test_detect_action_stop_sends_correct_rpc(self, call, mock_client):
        detect_action = DetectAction(call, "det-2")
        await detect_action.stop()
        mock_client.execute.assert_called_once_with(
            "calling.detect.stop",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "det-2"},
        )


# ---------------------------------------------------------------------------
# CollectAction (play_and_collect) direct construction + stop/volume/start_input_timers
# ---------------------------------------------------------------------------

class TestCollectActionInit:
    @pytest.mark.asyncio
    async def test_collect_action_init(self, call):
        collect_action = CollectAction(call, "col-1")
        assert collect_action.control_id == "col-1"
        assert collect_action._terminal_event == EVENT_CALL_COLLECT
        assert "finished" in collect_action._terminal_states
        assert "no_input" in collect_action._terminal_states
        assert "no_match" in collect_action._terminal_states

    @pytest.mark.asyncio
    async def test_collect_action_stop_uses_play_and_collect_method(
        self, call, mock_client
    ):
        collect_action = CollectAction(call, "col-2")
        await collect_action.stop()
        mock_client.execute.assert_called_once_with(
            "calling.play_and_collect.stop",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "col-2"},
        )

    @pytest.mark.asyncio
    async def test_collect_action_volume_sends_correct_rpc(self, call, mock_client):
        collect_action = CollectAction(call, "col-3")
        await collect_action.volume(7.5)
        mock_client.execute.assert_called_once_with(
            "calling.play_and_collect.volume",
            {
                "node_id": "node-1",
                "call_id": "call-1",
                "control_id": "col-3",
                "volume": 7.5,
            },
        )

    @pytest.mark.asyncio
    async def test_collect_action_start_input_timers(self, call, mock_client):
        collect_action = CollectAction(call, "col-4")
        await collect_action.start_input_timers()
        mock_client.execute.assert_called_once_with(
            "calling.collect.start_input_timers",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "col-4"},
        )


# ---------------------------------------------------------------------------
# StandaloneCollectAction direct construction + stop/start_input_timers
# ---------------------------------------------------------------------------

class TestStandaloneCollectActionInit:
    @pytest.mark.asyncio
    async def test_standalone_collect_action_init(self, call):
        standalone_action = StandaloneCollectAction(call, "scol-1")
        assert standalone_action.control_id == "scol-1"
        assert standalone_action._terminal_event == EVENT_CALL_COLLECT
        assert "finished" in standalone_action._terminal_states
        assert "no_input" in standalone_action._terminal_states

    @pytest.mark.asyncio
    async def test_standalone_collect_action_stop_uses_collect_stop(
        self, call, mock_client
    ):
        standalone_action = StandaloneCollectAction(call, "scol-2")
        await standalone_action.stop()
        mock_client.execute.assert_called_once_with(
            "calling.collect.stop",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "scol-2"},
        )

    @pytest.mark.asyncio
    async def test_standalone_collect_action_start_input_timers(
        self, call, mock_client
    ):
        standalone_action = StandaloneCollectAction(call, "scol-3")
        await standalone_action.start_input_timers()
        mock_client.execute.assert_called_once_with(
            "calling.collect.start_input_timers",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "scol-3"},
        )


# ---------------------------------------------------------------------------
# FaxAction direct construction
# ---------------------------------------------------------------------------

class TestFaxActionInit:
    @pytest.mark.asyncio
    async def test_fax_action_init_send_fax_prefix(self, call):
        fax_action = FaxAction(call, "fax-1", "send_fax")
        assert fax_action.control_id == "fax-1"
        assert fax_action._method_prefix == "send_fax"
        assert fax_action._terminal_event == EVENT_CALL_FAX

    @pytest.mark.asyncio
    async def test_fax_action_init_receive_fax_prefix(self, call):
        fax_action = FaxAction(call, "fax-2", "receive_fax")
        assert fax_action._method_prefix == "receive_fax"


# ---------------------------------------------------------------------------
# TapAction direct construction + stop
# ---------------------------------------------------------------------------

class TestTapActionInit:
    @pytest.mark.asyncio
    async def test_tap_action_init(self, call):
        tap_action = TapAction(call, "tap-1")
        assert tap_action.control_id == "tap-1"
        assert tap_action._terminal_event == EVENT_CALL_TAP
        assert "finished" in tap_action._terminal_states

    @pytest.mark.asyncio
    async def test_tap_action_stop_sends_correct_rpc(self, call, mock_client):
        tap_action = TapAction(call, "tap-2")
        await tap_action.stop()
        mock_client.execute.assert_called_once_with(
            "calling.tap.stop",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "tap-2"},
        )


# ---------------------------------------------------------------------------
# StreamAction direct construction + stop
# ---------------------------------------------------------------------------

class TestStreamActionInit:
    @pytest.mark.asyncio
    async def test_stream_action_init(self, call):
        stream_action = StreamAction(call, "stream-1")
        assert stream_action.control_id == "stream-1"
        assert stream_action._terminal_event == EVENT_CALL_STREAM
        assert "finished" in stream_action._terminal_states

    @pytest.mark.asyncio
    async def test_stream_action_stop_sends_correct_rpc(self, call, mock_client):
        stream_action = StreamAction(call, "stream-2")
        await stream_action.stop()
        mock_client.execute.assert_called_once_with(
            "calling.stream.stop",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "stream-2"},
        )


# ---------------------------------------------------------------------------
# PayAction direct construction + stop
# ---------------------------------------------------------------------------

class TestPayActionInit:
    @pytest.mark.asyncio
    async def test_pay_action_init(self, call):
        pay_action = PayAction(call, "pay-1")
        assert pay_action.control_id == "pay-1"
        assert pay_action._terminal_event == EVENT_CALL_PAY
        assert "finished" in pay_action._terminal_states
        assert "error" in pay_action._terminal_states

    @pytest.mark.asyncio
    async def test_pay_action_stop_sends_correct_rpc(self, call, mock_client):
        pay_action = PayAction(call, "pay-2")
        await pay_action.stop()
        mock_client.execute.assert_called_once_with(
            "calling.pay.stop",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "pay-2"},
        )


# ---------------------------------------------------------------------------
# TranscribeAction direct construction + stop
# ---------------------------------------------------------------------------

class TestTranscribeActionInit:
    @pytest.mark.asyncio
    async def test_transcribe_action_init(self, call):
        transcribe_action = TranscribeAction(call, "trn-1")
        assert transcribe_action.control_id == "trn-1"
        assert transcribe_action._terminal_event == EVENT_CALL_TRANSCRIBE
        assert "finished" in transcribe_action._terminal_states

    @pytest.mark.asyncio
    async def test_transcribe_action_stop_sends_correct_rpc(self, call, mock_client):
        transcribe_action = TranscribeAction(call, "trn-2")
        await transcribe_action.stop()
        mock_client.execute.assert_called_once_with(
            "calling.transcribe.stop",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "trn-2"},
        )


# ---------------------------------------------------------------------------
# AIAction direct construction + stop
# ---------------------------------------------------------------------------

class TestAIActionInit:
    @pytest.mark.asyncio
    async def test_ai_action_init(self, call):
        ai_action = AIAction(call, "ai-1")
        assert ai_action.control_id == "ai-1"
        # AI uses a custom terminal_event string
        assert ai_action._terminal_event == "calling.call.ai"
        assert "finished" in ai_action._terminal_states
        assert "error" in ai_action._terminal_states

    @pytest.mark.asyncio
    async def test_ai_action_stop_sends_correct_rpc(self, call, mock_client):
        ai_action = AIAction(call, "ai-2")
        await ai_action.stop()
        mock_client.execute.assert_called_once_with(
            "calling.ai.stop",
            {"node_id": "node-1", "call_id": "call-1", "control_id": "ai-2"},
        )


# ---------------------------------------------------------------------------
# Call.__repr__
# ---------------------------------------------------------------------------

class TestCallRepr:
    """Direct __repr__ invocation so the audit picks up Call.__repr__ as covered."""

    @pytest.mark.asyncio
    async def test_call_repr_contains_id_state_direction(self, call):
        # Invoke __repr__ explicitly (the audit doesn't follow repr() builtin).
        rendered = call.__repr__()
        assert "call-1" in rendered
        assert "answered" in rendered
        assert "inbound" in rendered

    @pytest.mark.asyncio
    async def test_call_repr_changes_with_state(self, call):
        call.state = "ended"
        rendered = call.__repr__()
        assert "ended" in rendered
        assert "call-1" in rendered
