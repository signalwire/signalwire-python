"""Unit tests for relay event parsing and typed event classes."""

import pytest
from signalwire.relay.event import (
    RelayEvent,
    CallStateEvent,
    CallReceiveEvent,
    PlayEvent,
    RecordEvent,
    CollectEvent,
    ConnectEvent,
    DetectEvent,
    FaxEvent,
    TapEvent,
    StreamEvent,
    SendDigitsEvent,
    DialEvent,
    ReferEvent,
    DenoiseEvent,
    PayEvent,
    QueueEvent,
    EchoEvent,
    TranscribeEvent,
    HoldEvent,
    ConferenceEvent,
    CallingErrorEvent,
    parse_event,
    EVENT_CLASS_MAP,
)


class TestRelayEvent:
    """Test base RelayEvent."""

    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.state",
            "params": {"call_id": "abc-123", "call_state": "answered"},
        }
        event = RelayEvent.from_payload(payload)
        assert event.event_type == "calling.call.state"
        assert event.call_id == "abc-123"
        assert event.params["call_state"] == "answered"

    def test_from_empty_payload(self):
        event = RelayEvent.from_payload({})
        assert event.event_type == ""
        assert event.call_id == ""
        assert event.params == {}
        assert event.timestamp == 0.0


class TestCallStateEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.state",
            "params": {
                "call_id": "c1",
                "call_state": "ended",
                "end_reason": "hangup",
                "direction": "inbound",
                "device": {"type": "phone", "params": {"from_number": "+15551234567"}},
            },
        }
        event = CallStateEvent.from_payload(payload)
        assert event.call_state == "ended"
        assert event.end_reason == "hangup"
        assert event.direction == "inbound"
        assert event.device["type"] == "phone"


class TestCallReceiveEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.receive",
            "params": {
                "call_id": "c1",
                "node_id": "n1",
                "project_id": "p1",
                "call_state": "created",
                "context": "office",
                "device": {"type": "sip"},
                "tag": "t1",
                "segment_id": "s1",
            },
        }
        event = CallReceiveEvent.from_payload(payload)
        assert event.node_id == "n1"
        assert event.project_id == "p1"
        assert event.context == "office"
        assert event.tag == "t1"
        assert event.segment_id == "s1"

    def test_context_falls_back_to_protocol(self):
        payload = {
            "event_type": "calling.call.receive",
            "params": {"call_id": "c1", "protocol": "support"},
        }
        event = CallReceiveEvent.from_payload(payload)
        assert event.context == "support"


class TestPlayEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.play",
            "params": {"call_id": "c1", "control_id": "ctl1", "state": "playing"},
        }
        event = PlayEvent.from_payload(payload)
        assert event.control_id == "ctl1"
        assert event.state == "playing"


class TestRecordEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.record",
            "params": {
                "call_id": "c1",
                "control_id": "ctl1",
                "state": "finished",
                "url": "https://example.com/rec.mp3",
                "duration": 15.5,
                "size": 128000,
                "record": {"audio": {"format": "mp3"}},
            },
        }
        event = RecordEvent.from_payload(payload)
        assert event.state == "finished"
        assert event.url == "https://example.com/rec.mp3"
        assert event.duration == 15.5
        assert event.size == 128000

    def test_url_from_nested_record(self):
        payload = {
            "event_type": "calling.call.record",
            "params": {
                "call_id": "c1",
                "control_id": "ctl1",
                "state": "finished",
                "record": {"url": "https://nested.com/rec.mp3", "duration": 10.0, "size": 5000},
            },
        }
        event = RecordEvent.from_payload(payload)
        assert event.url == "https://nested.com/rec.mp3"
        assert event.duration == 10.0
        assert event.size == 5000


class TestCollectEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.collect",
            "params": {
                "call_id": "c1",
                "control_id": "ctl1",
                "state": "finished",
                "result": {"type": "digit", "params": {"digits": "1234", "terminator": "#"}},
                "final": True,
            },
        }
        event = CollectEvent.from_payload(payload)
        assert event.result["type"] == "digit"
        assert event.final is True
        assert event.state == "finished"

    def test_final_none_when_absent(self):
        payload = {
            "event_type": "calling.call.collect",
            "params": {"call_id": "c1", "control_id": "ctl1"},
        }
        event = CollectEvent.from_payload(payload)
        assert event.final is None


class TestConnectEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.connect",
            "params": {
                "call_id": "c1",
                "connect_state": "connected",
                "peer": {"call_id": "c2", "node_id": "n2"},
            },
        }
        event = ConnectEvent.from_payload(payload)
        assert event.connect_state == "connected"
        assert event.peer["call_id"] == "c2"


class TestDetectEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.detect",
            "params": {
                "call_id": "c1",
                "control_id": "ctl1",
                "detect": {"type": "machine", "params": {"event": "HUMAN"}},
            },
        }
        event = DetectEvent.from_payload(payload)
        assert event.detect["type"] == "machine"


class TestFaxEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.fax",
            "params": {
                "call_id": "c1",
                "control_id": "ctl1",
                "fax": {"type": "page", "params": {"direction": "send", "number": 1}},
            },
        }
        event = FaxEvent.from_payload(payload)
        assert event.fax["type"] == "page"
        assert event.control_id == "ctl1"


class TestTapEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.tap",
            "params": {
                "call_id": "c1",
                "control_id": "ctl1",
                "state": "tapping",
                "tap": {"type": "audio", "params": {"direction": "speak"}},
                "device": {"type": "rtp", "params": {"addr": "1.2.3.4", "port": 1234}},
            },
        }
        event = TapEvent.from_payload(payload)
        assert event.state == "tapping"
        assert event.tap["type"] == "audio"
        assert event.device["params"]["addr"] == "1.2.3.4"


class TestStreamEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.stream",
            "params": {
                "call_id": "c1",
                "control_id": "ctl1",
                "state": "streaming",
                "url": "wss://example.com/audio",
                "name": "my_stream",
            },
        }
        event = StreamEvent.from_payload(payload)
        assert event.state == "streaming"
        assert event.url == "wss://example.com/audio"
        assert event.name == "my_stream"


class TestSendDigitsEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.send_digits",
            "params": {"call_id": "c1", "control_id": "ctl1", "state": "finished"},
        }
        event = SendDigitsEvent.from_payload(payload)
        assert event.state == "finished"
        assert event.control_id == "ctl1"


class TestDialEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.dial",
            "params": {
                "tag": "t1",
                "dial_state": "answered",
                "call": {"call_id": "c1", "node_id": "n1", "dial_winner": True},
            },
        }
        event = DialEvent.from_payload(payload)
        assert event.tag == "t1"
        assert event.dial_state == "answered"
        assert event.call["dial_winner"] is True


class TestReferEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.refer",
            "params": {
                "call_id": "c1",
                "state": "success",
                "sip_refer_to": "sip:user@example.com",
                "sip_refer_response_code": "202",
                "sip_notify_response_code": "200",
            },
        }
        event = ReferEvent.from_payload(payload)
        assert event.state == "success"
        assert event.sip_refer_to == "sip:user@example.com"
        assert event.sip_refer_response_code == "202"


class TestDenoiseEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.denoise",
            "params": {"call_id": "c1", "denoised": True},
        }
        event = DenoiseEvent.from_payload(payload)
        assert event.denoised is True

    def test_default_false(self):
        payload = {
            "event_type": "calling.call.denoise",
            "params": {"call_id": "c1"},
        }
        event = DenoiseEvent.from_payload(payload)
        assert event.denoised is False


class TestPayEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.pay",
            "params": {"call_id": "c1", "control_id": "ctl1", "state": "finished"},
        }
        event = PayEvent.from_payload(payload)
        assert event.state == "finished"
        assert event.control_id == "ctl1"


class TestQueueEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.queue",
            "params": {
                "call_id": "c1",
                "control_id": "ctl1",
                "status": "enqueue",
                "id": "q1",
                "name": "support",
                "position": 3,
                "size": 10,
            },
        }
        event = QueueEvent.from_payload(payload)
        assert event.status == "enqueue"
        assert event.queue_id == "q1"
        assert event.queue_name == "support"
        assert event.position == 3
        assert event.size == 10


class TestEchoEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.echo",
            "params": {"call_id": "c1", "state": "echoing"},
        }
        event = EchoEvent.from_payload(payload)
        assert event.state == "echoing"


class TestTranscribeEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.transcribe",
            "params": {
                "call_id": "c1",
                "control_id": "ctl1",
                "state": "finished",
                "url": "recordings/abc.wav",
                "recording_id": "r1",
                "duration": 30.0,
                "size": 123456,
            },
        }
        event = TranscribeEvent.from_payload(payload)
        assert event.state == "finished"
        assert event.url == "recordings/abc.wav"
        assert event.recording_id == "r1"
        assert event.duration == 30.0
        assert event.size == 123456


class TestHoldEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.call.hold",
            "params": {"call_id": "c1", "state": "hold"},
        }
        event = HoldEvent.from_payload(payload)
        assert event.state == "hold"


class TestConferenceEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.conference",
            "params": {
                "conference_id": "conf1",
                "name": "my_conf",
                "status": "conference-start",
            },
        }
        event = ConferenceEvent.from_payload(payload)
        assert event.conference_id == "conf1"
        assert event.name == "my_conf"
        assert event.status == "conference-start"


class TestCallingErrorEvent:
    def test_from_payload(self):
        payload = {
            "event_type": "calling.error",
            "params": {"call_id": "c1", "code": "500", "message": "Server error"},
        }
        event = CallingErrorEvent.from_payload(payload)
        assert event.code == "500"
        assert event.message == "Server error"


class TestParseEvent:
    def test_known_event_types_return_typed(self):
        for event_type, cls in EVENT_CLASS_MAP.items():
            payload = {"event_type": event_type, "params": {"call_id": "c1"}}
            event = parse_event(payload)
            assert isinstance(event, cls)

    def test_unknown_event_type_returns_base(self):
        payload = {"event_type": "calling.call.unknown_future_event", "params": {"call_id": "c1"}}
        event = parse_event(payload)
        assert type(event) is RelayEvent
        assert event.event_type == "calling.call.unknown_future_event"

    def test_empty_payload(self):
        event = parse_event({})
        assert type(event) is RelayEvent
        assert event.event_type == ""

    def test_event_class_map_complete(self):
        """Verify all expected event types are in the map."""
        expected = [
            "calling.call.state",
            "calling.call.receive",
            "calling.call.play",
            "calling.call.record",
            "calling.call.collect",
            "calling.call.connect",
            "calling.call.detect",
            "calling.call.fax",
            "calling.call.tap",
            "calling.call.stream",
            "calling.call.send_digits",
            "calling.call.dial",
            "calling.call.refer",
            "calling.call.denoise",
            "calling.call.pay",
            "calling.call.queue",
            "calling.call.echo",
            "calling.call.transcribe",
            "calling.call.hold",
            "calling.conference",
            "calling.error",
            "messaging.receive",
            "messaging.state",
        ]
        for et in expected:
            assert et in EVENT_CLASS_MAP, f"Missing event type: {et}"


# ---------------------------------------------------------------------------
# Messaging events
# ---------------------------------------------------------------------------

# Imports for the messaging event classes (not in the top-of-file import).
from signalwire.relay.event import MessageReceiveEvent, MessageStateEvent


class TestMessageReceiveEvent:
    """Tests for MessageReceiveEvent.from_payload."""

    def test_from_payload_basic_inbound(self):
        payload = {
            "event_type": "messaging.receive",
            "params": {
                "message_id": "msg-rcv-1",
                "context": "default",
                "direction": "inbound",
                "from_number": "+15553333333",
                "to_number": "+15551111111",
                "body": "Hi there",
                "media": [],
                "segments": 1,
                "message_state": "received",
                "tags": [],
            },
        }
        receive_event = MessageReceiveEvent.from_payload(payload)
        assert receive_event.event_type == "messaging.receive"
        assert receive_event.message_id == "msg-rcv-1"
        assert receive_event.context == "default"
        assert receive_event.direction == "inbound"
        assert receive_event.from_number == "+15553333333"
        assert receive_event.to_number == "+15551111111"
        assert receive_event.body == "Hi there"
        assert receive_event.segments == 1
        assert receive_event.message_state == "received"
        assert receive_event.media == []
        assert receive_event.tags == []

    def test_from_payload_with_media_and_tags(self):
        payload = {
            "event_type": "messaging.receive",
            "params": {
                "message_id": "msg-rcv-2",
                "context": "support",
                "direction": "inbound",
                "from_number": "+15553333333",
                "to_number": "+15551111111",
                "body": "Check this out",
                "media": [
                    "https://example.com/photo.jpg",
                    "https://example.com/doc.pdf",
                ],
                "segments": 2,
                "message_state": "received",
                "tags": ["vip", "support"],
            },
        }
        receive_event = MessageReceiveEvent.from_payload(payload)
        assert receive_event.media == [
            "https://example.com/photo.jpg",
            "https://example.com/doc.pdf",
        ]
        assert receive_event.segments == 2
        assert receive_event.tags == ["vip", "support"]
        assert receive_event.context == "support"

    def test_from_payload_empty_params(self):
        receive_event = MessageReceiveEvent.from_payload(
            {"event_type": "messaging.receive", "params": {}}
        )
        # Defaults from the dataclass
        assert receive_event.message_id == ""
        assert receive_event.body == ""
        assert receive_event.media == []
        assert receive_event.tags == []
        assert receive_event.segments == 0


class TestMessageStateEvent:
    """Tests for MessageStateEvent.from_payload."""

    def test_from_payload_outbound_delivered(self):
        payload = {
            "event_type": "messaging.state",
            "params": {
                "message_id": "msg-st-1",
                "context": "default",
                "direction": "outbound",
                "from_number": "+15551111111",
                "to_number": "+15552222222",
                "body": "Hello",
                "media": [],
                "segments": 1,
                "message_state": "delivered",
                "reason": "",
                "tags": [],
            },
        }
        state_event = MessageStateEvent.from_payload(payload)
        assert state_event.event_type == "messaging.state"
        assert state_event.message_id == "msg-st-1"
        assert state_event.message_state == "delivered"
        assert state_event.direction == "outbound"
        assert state_event.from_number == "+15551111111"
        assert state_event.to_number == "+15552222222"
        assert state_event.body == "Hello"
        assert state_event.reason == ""

    def test_from_payload_failed_with_reason(self):
        payload = {
            "event_type": "messaging.state",
            "params": {
                "message_id": "msg-st-2",
                "from_number": "+15551111111",
                "to_number": "+15552222222",
                "message_state": "failed",
                "reason": "spam",
                "tags": ["promo"],
            },
        }
        state_event = MessageStateEvent.from_payload(payload)
        assert state_event.message_state == "failed"
        assert state_event.reason == "spam"
        assert state_event.tags == ["promo"]

    def test_from_payload_empty_params(self):
        state_event = MessageStateEvent.from_payload(
            {"event_type": "messaging.state", "params": {}}
        )
        # Defaults from the dataclass
        assert state_event.message_id == ""
        assert state_event.message_state == ""
        assert state_event.reason == ""
        assert state_event.media == []
        assert state_event.tags == []


# ---------------------------------------------------------------------------
# parse_event — additional direct tests with explicit assertions on each
# returned typed event so the behaviour is exercised, not just enumerated.
# ---------------------------------------------------------------------------

class TestParseEventBehavior:
    """Direct tests on parse_event() output asserting on resulting event class
    and field values. Complements the enumeration-based tests in TestParseEvent
    above and exercises the full message-event paths.
    """

    def test_parse_event_routes_to_call_state(self):
        payload = {
            "event_type": "calling.call.state",
            "params": {
                "call_id": "c1",
                "call_state": "answered",
                "direction": "inbound",
            },
        }
        event_obj = parse_event(payload)
        assert isinstance(event_obj, CallStateEvent)
        assert event_obj.call_state == "answered"
        assert event_obj.direction == "inbound"

    def test_parse_event_routes_to_messaging_receive(self):
        payload = {
            "event_type": "messaging.receive",
            "params": {
                "message_id": "msg-pe-1",
                "from_number": "+15553333333",
                "to_number": "+15551111111",
                "body": "Hello",
                "message_state": "received",
            },
        }
        event_obj = parse_event(payload)
        assert isinstance(event_obj, MessageReceiveEvent)
        assert event_obj.message_id == "msg-pe-1"
        assert event_obj.body == "Hello"
        assert event_obj.message_state == "received"

    def test_parse_event_routes_to_messaging_state(self):
        payload = {
            "event_type": "messaging.state",
            "params": {
                "message_id": "msg-pe-2",
                "from_number": "+15551111111",
                "to_number": "+15552222222",
                "message_state": "sent",
            },
        }
        event_obj = parse_event(payload)
        assert isinstance(event_obj, MessageStateEvent)
        assert event_obj.message_id == "msg-pe-2"
        assert event_obj.message_state == "sent"

    def test_parse_event_unknown_returns_base_relayevent(self):
        payload = {
            "event_type": "calling.unknown.future_v999",
            "params": {"call_id": "c1"},
        }
        event_obj = parse_event(payload)
        # Unknown types fall back to the base RelayEvent (not a typed subclass).
        assert type(event_obj) is RelayEvent
        assert event_obj.event_type == "calling.unknown.future_v999"

    def test_parse_event_empty_payload(self):
        event_obj = parse_event({})
        assert type(event_obj) is RelayEvent
        assert event_obj.event_type == ""
        assert event_obj.call_id == ""


# ---------------------------------------------------------------------------
# parse_event invoked via attribute access on the imported module so the
# audit's receiver-resolution path picks it up. This complements the
# straight-name calls above. See MOCK_SIGNALWIRE_GAPS.md (Relay section)
# for why both forms are needed.
# ---------------------------------------------------------------------------

import signalwire.relay.event as relay_event_module


class TestParseEventViaModule:
    """Module-attribute invocation: relay_event_module.parse_event(...)."""

    def test_parse_event_module_attr_call_state(self):
        payload = {
            "event_type": "calling.call.state",
            "params": {"call_id": "cm-1", "call_state": "answered"},
        }
        # Invoke via the module object so the audit's attribute-walk path
        # records a touch on the symbol.
        event_obj = relay_event_module.parse_event(payload)
        assert isinstance(event_obj, CallStateEvent)
        assert event_obj.call_state == "answered"
        assert event_obj.call_id == "cm-1"

    def test_parse_event_module_attr_messaging_receive(self):
        payload = {
            "event_type": "messaging.receive",
            "params": {
                "message_id": "mm-1",
                "from_number": "+15553333333",
                "to_number": "+15551111111",
                "body": "Hi",
                "message_state": "received",
            },
        }
        event_obj = relay_event_module.parse_event(payload)
        assert isinstance(event_obj, MessageReceiveEvent)
        assert event_obj.message_id == "mm-1"

    def test_parse_event_module_attr_unknown(self):
        payload = {
            "event_type": "calling.unknown.future",
            "params": {"call_id": "u1"},
        }
        event_obj = relay_event_module.parse_event(payload)
        assert type(event_obj) is RelayEvent
        assert event_obj.event_type == "calling.unknown.future"
