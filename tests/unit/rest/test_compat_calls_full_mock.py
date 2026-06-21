"""Full success + error coverage for ``client.compat.calls`` — the LaML
(Twilio-compatible) Calls resource and its Recordings / Streams sub-resources.

Mirrors ``test_fabric_ai_agents_full_mock.py``: each canonical route gets a
SUCCESS test (real SDK call, body shape + journal method/path/matched_route)
and an ERROR test (``mock.push_scenario`` arms a 4xx/5xx; the SDK raises
``SignalWireRestError`` with the matching ``status_code`` and the journal records
the route hit with that status).  Paths resolve under the conftest's pinned
project ``test_proj``.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

BASE = "/api/laml/2010-04-01/Accounts/test_proj/Calls"


class TestCompatCallsSuccess:
    def test_list_all_calls(self, signalwire_client, mock):
        body = signalwire_client.compat.calls.list()
        assert isinstance(body, dict)
        assert "calls" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == BASE
        assert last.matched_route == "compatibility.list_all_calls"

    def test_create_a_call(self, signalwire_client, mock):
        body = signalwire_client.compat.calls.create(To="+15551112222", From="+15553334444")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == BASE
        assert last.matched_route == "compatibility.create_a_call"
        assert last.body and last.body.get("To") == "+15551112222"

    def test_retrieve_a_call(self, signalwire_client, mock):
        body = signalwire_client.compat.calls.get("CA1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{BASE}/CA1"
        assert last.matched_route == "compatibility.retrieve_a_call"

    def test_update_a_call(self, signalwire_client, mock):
        body = signalwire_client.compat.calls.update("CA1", Status="completed")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{BASE}/CA1"
        assert last.matched_route == "compatibility.update_a_call"
        assert last.body and last.body.get("Status") == "completed"

    def test_delete_a_call(self, signalwire_client, mock):
        signalwire_client.compat.calls.delete("CA1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{BASE}/CA1"
        assert last.matched_route == "compatibility.delete_a_call"

    def test_create_recording(self, signalwire_client, mock):
        body = signalwire_client.compat.calls.start_recording("CA1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{BASE}/CA1/Recordings"
        assert last.matched_route == "compatibility.create_recording"

    def test_update_recording(self, signalwire_client, mock):
        body = signalwire_client.compat.calls.update_recording("CA1", "RE1", Status="paused")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{BASE}/CA1/Recordings/RE1"
        assert last.matched_route == "compatibility.update_recording"
        assert last.body and last.body.get("Status") == "paused"

    def test_create_stream(self, signalwire_client, mock):
        body = signalwire_client.compat.calls.start_stream("CA1", Url="wss://a.b/s")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{BASE}/CA1/Streams"
        assert last.matched_route == "compatibility.create_stream"
        assert last.body and last.body.get("Url") == "wss://a.b/s"

    def test_update_stream(self, signalwire_client, mock):
        body = signalwire_client.compat.calls.stop_stream("CA1", "ST1", Status="stopped")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{BASE}/CA1/Streams/ST1"
        assert last.matched_route == "compatibility.update_stream"
        assert last.body and last.body.get("Status") == "stopped"


class TestCompatCallsErrors:
    def test_list_all_calls_server_error(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_all_calls", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.calls.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_all_calls"
        assert last.response_status == 500

    def test_create_a_call_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_a_call", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.calls.create(To="+1", From="+1")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_a_call"
        assert last.response_status == 422

    def test_retrieve_a_call_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_a_call", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.calls.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_a_call"
        assert last.response_status == 404

    def test_update_a_call_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_a_call", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.calls.update("missing", Status="completed")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_a_call"
        assert last.response_status == 404

    def test_delete_a_call_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_a_call", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.calls.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_a_call"
        assert last.response_status == 404

    def test_create_recording_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_recording", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.calls.start_recording("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_recording"
        assert last.response_status == 404

    def test_update_recording_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_recording", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.calls.update_recording("missing", "RE1", Status="paused")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_recording"
        assert last.response_status == 404

    def test_create_stream_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_stream", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.calls.start_stream("missing", Url="wss://a.b/s")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_stream"
        assert last.response_status == 404

    def test_update_stream_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_stream", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.calls.stop_stream("missing", "ST1", Status="stopped")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_stream"
        assert last.response_status == 404
