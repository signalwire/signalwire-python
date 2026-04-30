"""Compat Calls stream + recording tests.

Covers the gap entries for ``CompatCalls`` that aren't already exercised by
``test_namespaces.py`` (start_stream, stop_stream, update_recording).
"""

from __future__ import annotations


class TestCompatCallsStartStream:
    """``CompatCalls.start_stream`` -> POST /Calls/{sid}/Streams."""

    def test_returns_stream_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.calls.start_stream(
            "CA_TEST",
            Url="wss://example.com/stream",
            Name="my-stream",
        )
        assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
        # Stream resources carry a 'sid' or 'name' identifier.
        assert "sid" in result or "name" in result, (
            f"expected stream sid/name in body, got keys {sorted(result)!r}"
        )

    def test_journal_records_post_to_streams_collection(self, signalwire_client, mock):
        signalwire_client.compat.calls.start_stream(
            "CA_JX1", Url="wss://a.b/s", Name="strm-x"
        )
        j = mock.last_request()
        assert j.method == "POST"
        # The path is /api/laml/.../Calls/{sid}/Streams (no specific stream sid).
        assert j.path == "/api/laml/2010-04-01/Accounts/test_proj/Calls/CA_JX1/Streams"
        assert isinstance(j.body, dict)
        assert j.body.get("Url") == "wss://a.b/s"
        assert j.body.get("Name") == "strm-x"


class TestCompatCallsStopStream:
    """``CompatCalls.stop_stream(call_sid, stream_sid, **kw)`` -> POST .../Streams/{stream_sid}."""

    def test_returns_stream_resource_with_status(self, signalwire_client, mock):
        result = signalwire_client.compat.calls.stop_stream(
            "CA_T1", "ST_T1", Status="stopped"
        )
        assert isinstance(result, dict)
        # The stop endpoint synthesises a stream resource (sid + status).
        assert "sid" in result or "status" in result

    def test_journal_records_post_to_specific_stream(self, signalwire_client, mock):
        signalwire_client.compat.calls.stop_stream(
            "CA_S1", "ST_S1", Status="stopped"
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Calls/CA_S1/Streams/ST_S1"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("Status") == "stopped"


class TestCompatCallsUpdateRecording:
    """``CompatCalls.update_recording(call_sid, rec_sid, **kw)``."""

    def test_returns_recording_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.calls.update_recording(
            "CA_T2", "RE_T2", Status="paused"
        )
        assert isinstance(result, dict)
        # Recording resources carry a sid plus duration/status fields.
        assert "sid" in result or "status" in result

    def test_journal_records_post_to_specific_recording(self, signalwire_client, mock):
        signalwire_client.compat.calls.update_recording(
            "CA_R1", "RE_R1", Status="paused"
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Calls/CA_R1/Recordings/RE_R1"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("Status") == "paused"
