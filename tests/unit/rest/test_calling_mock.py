"""Calling namespace command-dispatch coverage against the mock server.

Every command in ``signalwire.rest.namespaces.calling.CallingNamespace`` is
exercised here with the real ``signalwire-python`` ``RestClient`` wired to
the in-process ``mock_signalwire`` server.  Each test:

1. Calls the SDK method (no transport patching).
2. Asserts on the response body shape that the mock returns from the spec.
3. Asserts on ``mock.last_request()`` so we know the SDK sent the right
   wire request — method, path, command field, and (where applicable) the
   ``id`` and any keyword params.
"""

from __future__ import annotations


CALLS_PATH = "/api/calling/calls"


# ---------------------------------------------------------------------------
# Lifecycle commands
# ---------------------------------------------------------------------------


class TestCallingLifecycle:
    def test_update(self, signalwire_client, mock):
        body = signalwire_client.calling.update(id="call-1", state="hold")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.matched_route is not None
        assert last.body.get("command") == "update"
        assert "id" not in last.body
        assert last.body.get("params", {}).get("id") == "call-1"
        assert last.body.get("params", {}).get("state") == "hold"

    def test_transfer(self, signalwire_client, mock):
        body = signalwire_client.calling.transfer(
            "call-123", destination="+15551234567", from_number="+15559876543",
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.transfer"
        assert last.body.get("id") == "call-123"
        assert last.body.get("params", {}).get("destination") == "+15551234567"
        assert last.body.get("params", {}).get("from_number") == "+15559876543"

    def test_disconnect(self, signalwire_client, mock):
        body = signalwire_client.calling.disconnect("call-456", reason="busy")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.disconnect"
        assert last.body.get("id") == "call-456"
        assert last.body.get("params", {}).get("reason") == "busy"


# ---------------------------------------------------------------------------
# Play commands
# ---------------------------------------------------------------------------


class TestCallingPlay:
    def test_play_pause(self, signalwire_client, mock):
        body = signalwire_client.calling.play_pause("call-1", control_id="ctrl-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.play.pause"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "ctrl-1"

    def test_play_resume(self, signalwire_client, mock):
        body = signalwire_client.calling.play_resume("call-1", control_id="ctrl-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.play.resume"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "ctrl-1"

    def test_play_stop(self, signalwire_client, mock):
        body = signalwire_client.calling.play_stop("call-1", control_id="ctrl-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.play.stop"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "ctrl-1"

    def test_play_volume(self, signalwire_client, mock):
        body = signalwire_client.calling.play_volume(
            "call-1", control_id="ctrl-1", volume=2.5,
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.play.volume"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("volume") == 2.5


# ---------------------------------------------------------------------------
# Record commands
# ---------------------------------------------------------------------------


class TestCallingRecord:
    def test_record(self, signalwire_client, mock):
        body = signalwire_client.calling.record("call-1", record={"format": "mp3"})
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.record"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("record") == {"format": "mp3"}

    def test_record_pause(self, signalwire_client, mock):
        body = signalwire_client.calling.record_pause("call-1", control_id="rec-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.record.pause"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "rec-1"

    def test_record_resume(self, signalwire_client, mock):
        body = signalwire_client.calling.record_resume("call-1", control_id="rec-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.record.resume"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "rec-1"


# ---------------------------------------------------------------------------
# Collect commands
# ---------------------------------------------------------------------------


class TestCallingCollect:
    def test_collect(self, signalwire_client, mock):
        body = signalwire_client.calling.collect(
            "call-1", initial_timeout=5, digits={"max": 4},
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.collect"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("initial_timeout") == 5

    def test_collect_stop(self, signalwire_client, mock):
        body = signalwire_client.calling.collect_stop("call-1", control_id="col-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.collect.stop"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "col-1"

    def test_collect_start_input_timers(self, signalwire_client, mock):
        body = signalwire_client.calling.collect_start_input_timers(
            "call-1", control_id="col-1",
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.collect.start_input_timers"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "col-1"


# ---------------------------------------------------------------------------
# Detect / tap / stream / denoise / transcribe
# ---------------------------------------------------------------------------


class TestCallingDetect:
    def test_detect(self, signalwire_client, mock):
        body = signalwire_client.calling.detect(
            "call-1", detect={"type": "machine", "params": {}},
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.detect"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("detect", {}).get("type") == "machine"

    def test_detect_stop(self, signalwire_client, mock):
        body = signalwire_client.calling.detect_stop("call-1", control_id="det-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.detect.stop"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "det-1"


class TestCallingTap:
    def test_tap(self, signalwire_client, mock):
        body = signalwire_client.calling.tap(
            "call-1", tap={"type": "audio"}, device={"type": "rtp"},
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.tap"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("tap") == {"type": "audio"}

    def test_tap_stop(self, signalwire_client, mock):
        body = signalwire_client.calling.tap_stop("call-1", control_id="tap-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.tap.stop"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "tap-1"


class TestCallingStream:
    def test_stream(self, signalwire_client, mock):
        body = signalwire_client.calling.stream(
            "call-1", url="wss://example.com/audio",
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.stream"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("url") == "wss://example.com/audio"

    def test_stream_stop(self, signalwire_client, mock):
        body = signalwire_client.calling.stream_stop("call-1", control_id="stream-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.stream.stop"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "stream-1"


class TestCallingDenoise:
    def test_denoise(self, signalwire_client, mock):
        body = signalwire_client.calling.denoise("call-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.denoise"
        assert last.body.get("id") == "call-1"

    def test_denoise_stop(self, signalwire_client, mock):
        body = signalwire_client.calling.denoise_stop("call-1", control_id="dn-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.denoise.stop"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "dn-1"


class TestCallingTranscribe:
    def test_transcribe(self, signalwire_client, mock):
        body = signalwire_client.calling.transcribe(
            "call-1", language="en-US", transcribe={"engine": "google"},
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.transcribe"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("language") == "en-US"

    def test_transcribe_stop(self, signalwire_client, mock):
        body = signalwire_client.calling.transcribe_stop("call-1", control_id="tr-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.transcribe.stop"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("control_id") == "tr-1"


# ---------------------------------------------------------------------------
# AI commands
# ---------------------------------------------------------------------------


class TestCallingAI:
    def test_ai_hold(self, signalwire_client, mock):
        body = signalwire_client.calling.ai_hold("call-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.ai_hold"
        assert last.body.get("id") == "call-1"

    def test_ai_unhold(self, signalwire_client, mock):
        body = signalwire_client.calling.ai_unhold("call-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.ai_unhold"
        assert last.body.get("id") == "call-1"

    def test_ai_stop(self, signalwire_client, mock):
        body = signalwire_client.calling.ai_stop("call-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.ai.stop"
        assert last.body.get("id") == "call-1"


# ---------------------------------------------------------------------------
# Live transcribe / translate
# ---------------------------------------------------------------------------


class TestCallingLive:
    def test_live_transcribe(self, signalwire_client, mock):
        body = signalwire_client.calling.live_transcribe(
            "call-1", language="en-US",
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.live_transcribe"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("language") == "en-US"

    def test_live_translate(self, signalwire_client, mock):
        body = signalwire_client.calling.live_translate(
            "call-1", source_language="en", target_language="es",
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.live_translate"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("source_language") == "en"
        assert last.body.get("params", {}).get("target_language") == "es"


# ---------------------------------------------------------------------------
# Fax commands
# ---------------------------------------------------------------------------


class TestCallingFax:
    def test_send_fax_stop(self, signalwire_client, mock):
        body = signalwire_client.calling.send_fax_stop("call-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.send_fax.stop"
        assert last.body.get("id") == "call-1"

    def test_receive_fax_stop(self, signalwire_client, mock):
        body = signalwire_client.calling.receive_fax_stop("call-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.receive_fax.stop"
        assert last.body.get("id") == "call-1"


# ---------------------------------------------------------------------------
# SIP refer + custom user_event
# ---------------------------------------------------------------------------


class TestCallingMisc:
    def test_refer(self, signalwire_client, mock):
        body = signalwire_client.calling.refer(
            "call-1", to="sip:other@example.com",
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.refer"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("to") == "sip:other@example.com"

    def test_user_event(self, signalwire_client, mock):
        body = signalwire_client.calling.user_event(
            "call-1", event_name="my-event", payload={"foo": "bar"},
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == CALLS_PATH
        assert last.body.get("command") == "calling.user_event"
        assert last.body.get("id") == "call-1"
        assert last.body.get("params", {}).get("event_name") == "my-event"
        assert last.body.get("params", {}).get("payload") == {"foo": "bar"}
