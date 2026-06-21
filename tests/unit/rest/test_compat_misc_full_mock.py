"""Full success + error coverage for the remaining LaML (Twilio-compatible)
resources: ``client.compat.laml_bins`` (cXML scripts), ``client.compat.queues``
(+ members), ``client.compat.recordings`` and ``client.compat.transcriptions``.

Mirrors ``test_fabric_ai_agents_full_mock.py``: each canonical route gets a
SUCCESS test (real SDK call, body shape + journal method/path/matched_route)
and an ERROR test (``mock.push_scenario`` arms a 4xx/5xx; the SDK raises
``SignalWireRestError`` with the matching ``status_code``).  Paths resolve under
the conftest's pinned project ``test_proj``.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

BINS = "/api/laml/2010-04-01/Accounts/test_proj/LamlBins"
QUEUES = "/api/laml/2010-04-01/Accounts/test_proj/Queues"
RECS = "/api/laml/2010-04-01/Accounts/test_proj/Recordings"
TRANS = "/api/laml/2010-04-01/Accounts/test_proj/Transcriptions"


class TestCompatLamlBinsSuccess:
    def test_list_cxml_scripts(self, signalwire_client, mock):
        body = signalwire_client.compat.laml_bins.list()
        assert isinstance(body, dict)
        assert "laml_bins" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == BINS
        assert last.matched_route == "compatibility.list_cxml_scripts"

    def test_create_cxml_script(self, signalwire_client, mock):
        body = signalwire_client.compat.laml_bins.create(Name="bin-a", Contents="<Response/>")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == BINS
        assert last.matched_route == "compatibility.create_cxml_script"
        assert last.body and last.body.get("Name") == "bin-a"

    def test_retrieve_cxml_script(self, signalwire_client, mock):
        body = signalwire_client.compat.laml_bins.get("LB1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{BINS}/LB1"
        assert last.matched_route == "compatibility.retrieve_cxml_script"

    def test_update_cxml_script(self, signalwire_client, mock):
        body = signalwire_client.compat.laml_bins.update("LB1", Name="renamed")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{BINS}/LB1"
        assert last.matched_route == "compatibility.update_cxml_script"
        assert last.body and last.body.get("Name") == "renamed"

    def test_delete_cxml_script(self, signalwire_client, mock):
        signalwire_client.compat.laml_bins.delete("LB1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{BINS}/LB1"
        assert last.matched_route == "compatibility.delete_cxml_script"


class TestCompatLamlBinsErrors:
    def test_list_cxml_scripts_server_error(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_cxml_scripts", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.laml_bins.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_cxml_scripts"
        assert last.response_status == 500

    def test_create_cxml_script_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_cxml_script", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.laml_bins.create(Name="x")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_cxml_script"
        assert last.response_status == 422

    def test_retrieve_cxml_script_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_cxml_script", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.laml_bins.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_cxml_script"
        assert last.response_status == 404

    def test_update_cxml_script_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_cxml_script", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.laml_bins.update("missing", Name="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_cxml_script"
        assert last.response_status == 404

    def test_delete_cxml_script_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_cxml_script", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.laml_bins.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_cxml_script"
        assert last.response_status == 404


class TestCompatQueuesSuccess:
    def test_list_queues(self, signalwire_client, mock):
        body = signalwire_client.compat.queues.list()
        assert isinstance(body, dict)
        assert "queues" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == QUEUES
        assert last.matched_route == "compatibility.list_queues"

    def test_create_queue(self, signalwire_client, mock):
        body = signalwire_client.compat.queues.create(FriendlyName="q-a")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == QUEUES
        assert last.matched_route == "compatibility.create_queue"
        assert last.body and last.body.get("FriendlyName") == "q-a"

    def test_list_all_queue_members(self, signalwire_client, mock):
        body = signalwire_client.compat.queues.list_members("QU1")
        assert isinstance(body, dict)
        assert "queue_members" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{QUEUES}/QU1/Members"
        assert last.matched_route == "compatibility.list_all_queue_members"

    def test_retrieve_queue_member(self, signalwire_client, mock):
        body = signalwire_client.compat.queues.get_member("QU1", "CA1")
        assert isinstance(body, dict)
        assert "call_sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{QUEUES}/QU1/Members/CA1"
        assert last.matched_route == "compatibility.retrieve_queue_member"

    def test_update_queue_member(self, signalwire_client, mock):
        body = signalwire_client.compat.queues.dequeue_member("QU1", "CA1", Url="https://x/y")
        assert isinstance(body, dict)
        assert "call_sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{QUEUES}/QU1/Members/CA1"
        assert last.matched_route == "compatibility.update_queue_member"
        assert last.body and last.body.get("Url") == "https://x/y"

    def test_retrieve_queue(self, signalwire_client, mock):
        body = signalwire_client.compat.queues.get("QU1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{QUEUES}/QU1"
        assert last.matched_route == "compatibility.retrieve_queue"

    def test_update_queue(self, signalwire_client, mock):
        body = signalwire_client.compat.queues.update("QU1", FriendlyName="renamed")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{QUEUES}/QU1"
        assert last.matched_route == "compatibility.update_queue"
        assert last.body and last.body.get("FriendlyName") == "renamed"

    def test_delete_queue(self, signalwire_client, mock):
        signalwire_client.compat.queues.delete("QU1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{QUEUES}/QU1"
        assert last.matched_route == "compatibility.delete_queue"


class TestCompatQueuesErrors:
    def test_list_queues_server_error(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_queues", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.queues.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_queues"
        assert last.response_status == 500

    def test_create_queue_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_queue", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.queues.create(FriendlyName="x")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_queue"
        assert last.response_status == 422

    def test_list_all_queue_members_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_all_queue_members", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.queues.list_members("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_all_queue_members"
        assert last.response_status == 404

    def test_retrieve_queue_member_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_queue_member", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.queues.get_member("QU1", "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_queue_member"
        assert last.response_status == 404

    def test_update_queue_member_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_queue_member", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.queues.dequeue_member("QU1", "missing", Url="https://x/y")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_queue_member"
        assert last.response_status == 404

    def test_retrieve_queue_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_queue", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.queues.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_queue"
        assert last.response_status == 404

    def test_update_queue_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_queue", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.queues.update("missing", FriendlyName="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_queue"
        assert last.response_status == 404

    def test_delete_queue_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_queue", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.queues.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_queue"
        assert last.response_status == 404


class TestCompatRecordingsSuccess:
    def test_list_recordings(self, signalwire_client, mock):
        body = signalwire_client.compat.recordings.list()
        assert isinstance(body, dict)
        assert "recordings" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == RECS
        assert last.matched_route == "compatibility.list_recordings"

    def test_retrieve_recording(self, signalwire_client, mock):
        body = signalwire_client.compat.recordings.get("RE1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{RECS}/RE1"
        assert last.matched_route == "compatibility.retrieve_recording"

    def test_delete_recording(self, signalwire_client, mock):
        signalwire_client.compat.recordings.delete("RE1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{RECS}/RE1"
        assert last.matched_route == "compatibility.delete_recording"


class TestCompatRecordingsErrors:
    def test_list_recordings_server_error(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_recordings", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.recordings.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_recordings"
        assert last.response_status == 500

    def test_retrieve_recording_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_recording", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.recordings.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_recording"
        assert last.response_status == 404

    def test_delete_recording_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_recording", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.recordings.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_recording"
        assert last.response_status == 404


class TestCompatTranscriptionsSuccess:
    def test_list_transcriptions(self, signalwire_client, mock):
        body = signalwire_client.compat.transcriptions.list()
        assert isinstance(body, dict)
        assert "transcriptions" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == TRANS
        assert last.matched_route == "compatibility.list_transcriptions"

    def test_retrieve_transcription(self, signalwire_client, mock):
        body = signalwire_client.compat.transcriptions.get("TR1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{TRANS}/TR1"
        assert last.matched_route == "compatibility.retrieve_transcription"

    def test_delete_transcription(self, signalwire_client, mock):
        signalwire_client.compat.transcriptions.delete("TR1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{TRANS}/TR1"
        assert last.matched_route == "compatibility.delete_transcription"


class TestCompatTranscriptionsErrors:
    def test_list_transcriptions_server_error(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_transcriptions", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.transcriptions.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_transcriptions"
        assert last.response_status == 500

    def test_retrieve_transcription_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_transcription", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.transcriptions.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_transcription"
        assert last.response_status == 404

    def test_delete_transcription_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_transcription", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.transcriptions.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_transcription"
        assert last.response_status == 404
