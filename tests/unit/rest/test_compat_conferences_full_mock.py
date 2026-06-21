"""Full success + error coverage for ``client.compat.conferences`` — the LaML
(Twilio-compatible) Conferences resource plus its Participants, Recordings and
Streams sub-resources.

Mirrors ``test_fabric_ai_agents_full_mock.py``: each canonical route gets a
SUCCESS test (real SDK call, body shape + journal method/path/matched_route)
and an ERROR test (``mock.push_scenario`` arms a 4xx/5xx; the SDK raises
``SignalWireRestError`` with the matching ``status_code``).  Paths resolve under
the conftest's pinned project ``test_proj``.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

CONF = "/api/laml/2010-04-01/Accounts/test_proj/Conferences"


class TestCompatConferencesSuccess:
    def test_list_all_conferences(self, signalwire_client, mock):
        body = signalwire_client.compat.conferences.list()
        assert isinstance(body, dict)
        assert "conferences" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == CONF
        assert last.matched_route == "compatibility.list_all_conferences"

    def test_retrieve_conference(self, signalwire_client, mock):
        body = signalwire_client.compat.conferences.get("CF1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{CONF}/CF1"
        assert last.matched_route == "compatibility.retrieve_conference"

    def test_update_conference(self, signalwire_client, mock):
        body = signalwire_client.compat.conferences.update("CF1", Status="completed")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{CONF}/CF1"
        assert last.matched_route == "compatibility.update_conference"
        assert last.body and last.body.get("Status") == "completed"

    def test_list_all_participants(self, signalwire_client, mock):
        body = signalwire_client.compat.conferences.list_participants("CF1")
        assert isinstance(body, dict)
        assert "participants" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{CONF}/CF1/Participants"
        assert last.matched_route == "compatibility.list_all_participants"

    def test_retrieve_participant(self, signalwire_client, mock):
        body = signalwire_client.compat.conferences.get_participant("CF1", "CA1")
        assert isinstance(body, dict)
        assert "call_sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{CONF}/CF1/Participants/CA1"
        assert last.matched_route == "compatibility.retrieve_participant"

    def test_update_participant(self, signalwire_client, mock):
        body = signalwire_client.compat.conferences.update_participant(
            "CF1", "CA1", Muted="true"
        )
        assert isinstance(body, dict)
        assert "call_sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{CONF}/CF1/Participants/CA1"
        assert last.matched_route == "compatibility.update_participant"
        assert last.body and last.body.get("Muted") == "true"

    def test_delete_participant(self, signalwire_client, mock):
        signalwire_client.compat.conferences.remove_participant("CF1", "CA1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{CONF}/CF1/Participants/CA1"
        assert last.matched_route == "compatibility.delete_participant"

    def test_list_conference_recordings(self, signalwire_client, mock):
        body = signalwire_client.compat.conferences.list_recordings("CF1")
        assert isinstance(body, dict)
        assert "recordings" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{CONF}/CF1/Recordings"
        assert last.matched_route == "compatibility.list_conference_recordings"

    def test_get_conference_recording(self, signalwire_client, mock):
        body = signalwire_client.compat.conferences.get_recording("CF1", "RE1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{CONF}/CF1/Recordings/RE1"
        assert last.matched_route == "compatibility.get_conference_recording"

    def test_update_conference_recording(self, signalwire_client, mock):
        body = signalwire_client.compat.conferences.update_recording(
            "CF1", "RE1", Status="paused"
        )
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{CONF}/CF1/Recordings/RE1"
        assert last.matched_route == "compatibility.update_conference_recording"
        assert last.body and last.body.get("Status") == "paused"

    def test_delete_conference_recording(self, signalwire_client, mock):
        signalwire_client.compat.conferences.delete_recording("CF1", "RE1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{CONF}/CF1/Recordings/RE1"
        assert last.matched_route == "compatibility.delete_conference_recording"

    def test_create_conference_stream(self, signalwire_client, mock):
        body = signalwire_client.compat.conferences.start_stream("CF1", Url="wss://a.b/s")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{CONF}/CF1/Streams"
        assert last.matched_route == "compatibility.create_conference_stream"
        assert last.body and last.body.get("Url") == "wss://a.b/s"

    def test_update_conference_stream(self, signalwire_client, mock):
        body = signalwire_client.compat.conferences.stop_stream("CF1", "ST1", Status="stopped")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{CONF}/CF1/Streams/ST1"
        assert last.matched_route == "compatibility.update_conference_stream"
        assert last.body and last.body.get("Status") == "stopped"


class TestCompatConferencesErrors:
    def test_list_all_conferences_server_error(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_all_conferences", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_all_conferences"
        assert last.response_status == 500

    def test_retrieve_conference_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_conference", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_conference"
        assert last.response_status == 404

    def test_update_conference_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_conference", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.update("missing", Status="completed")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_conference"
        assert last.response_status == 404

    def test_list_all_participants_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_all_participants", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.list_participants("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_all_participants"
        assert last.response_status == 404

    def test_retrieve_participant_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_participant", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.get_participant("CF1", "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_participant"
        assert last.response_status == 404

    def test_update_participant_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_participant", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.update_participant("CF1", "missing", Muted="true")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_participant"
        assert last.response_status == 404

    def test_delete_participant_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_participant", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.remove_participant("CF1", "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_participant"
        assert last.response_status == 404

    def test_list_conference_recordings_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_conference_recordings", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.list_recordings("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_conference_recordings"
        assert last.response_status == 404

    def test_get_conference_recording_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.get_conference_recording", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.get_recording("CF1", "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.get_conference_recording"
        assert last.response_status == 404

    def test_update_conference_recording_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_conference_recording", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.update_recording("CF1", "missing", Status="paused")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_conference_recording"
        assert last.response_status == 404

    def test_delete_conference_recording_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_conference_recording", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.delete_recording("CF1", "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_conference_recording"
        assert last.response_status == 404

    def test_create_conference_stream_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_conference_stream", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.start_stream("missing", Url="wss://a.b/s")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_conference_stream"
        assert last.response_status == 404

    def test_update_conference_stream_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_conference_stream", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.conferences.stop_stream("missing", "ST1", Status="stopped")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_conference_stream"
        assert last.response_status == 404
