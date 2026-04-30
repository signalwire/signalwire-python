"""Compat Conferences resource tests.

Covers all 12 uncovered Conference symbols: list/get/update on the
conference itself, plus the participant, recording, and stream
sub-resources.
"""

from __future__ import annotations


# ---- Conference itself ---------------------------------------------------


class TestCompatConferencesList:
    def test_returns_paginated_list(self, signalwire_client, mock):
        result = signalwire_client.compat.conferences.list()
        assert isinstance(result, dict)
        # Compat list bodies always carry a 'page' int and a collection key
        # named after the resource ('conferences').
        assert "conferences" in result, (
            f"expected 'conferences' key, got {sorted(result)!r}"
        )
        assert isinstance(result["conferences"], list)
        assert isinstance(result["page"], int)

    def test_journal_records_get_to_conferences(self, signalwire_client, mock):
        signalwire_client.compat.conferences.list()
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == "/api/laml/2010-04-01/Accounts/test_proj/Conferences"
        assert j.matched_route is not None, "spec gap: conferences.list"


class TestCompatConferencesGet:
    def test_returns_conference_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.conferences.get("CF_TEST")
        assert isinstance(result, dict)
        # Conference resources carry friendly_name + status.
        assert "friendly_name" in result or "status" in result

    def test_journal_records_get_with_sid(self, signalwire_client, mock):
        signalwire_client.compat.conferences.get("CF_GETSID")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Conferences/CF_GETSID"
        )


class TestCompatConferencesUpdate:
    def test_returns_updated_conference(self, signalwire_client, mock):
        result = signalwire_client.compat.conferences.update(
            "CF_X", Status="completed"
        )
        assert isinstance(result, dict)
        assert "friendly_name" in result or "status" in result

    def test_journal_records_post_with_status(self, signalwire_client, mock):
        signalwire_client.compat.conferences.update(
            "CF_UPD", Status="completed", AnnounceUrl="https://a.b"
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Conferences/CF_UPD"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("Status") == "completed"
        assert j.body.get("AnnounceUrl") == "https://a.b"


# ---- Participants --------------------------------------------------------


class TestCompatConferencesGetParticipant:
    def test_returns_participant(self, signalwire_client, mock):
        result = signalwire_client.compat.conferences.get_participant(
            "CF_P", "CA_P"
        )
        assert isinstance(result, dict)
        # Participant resources expose call_sid + conference_sid.
        assert "call_sid" in result or "conference_sid" in result

    def test_journal_records_get_to_participant(self, signalwire_client, mock):
        signalwire_client.compat.conferences.get_participant("CF_GP", "CA_GP")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Conferences/CF_GP"
            "/Participants/CA_GP"
        )


class TestCompatConferencesUpdateParticipant:
    def test_returns_participant_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.conferences.update_participant(
            "CF_UP", "CA_UP", Muted=True
        )
        assert isinstance(result, dict)
        assert "call_sid" in result or "conference_sid" in result

    def test_journal_records_post_with_mute_flag(self, signalwire_client, mock):
        signalwire_client.compat.conferences.update_participant(
            "CF_M", "CA_M", Muted=True, Hold=False
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Conferences/CF_M"
            "/Participants/CA_M"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("Muted") is True
        assert j.body.get("Hold") is False


class TestCompatConferencesRemoveParticipant:
    def test_returns_empty_or_object(self, signalwire_client, mock):
        # 204-style deletes return {} from the SDK; a synthesized
        # response may also return a body.  Either is acceptable - what
        # we care about is no exception was raised.
        result = signalwire_client.compat.conferences.remove_participant(
            "CF_R", "CA_R"
        )
        assert isinstance(result, dict)

    def test_journal_records_delete_call(self, signalwire_client, mock):
        signalwire_client.compat.conferences.remove_participant("CF_RM", "CA_RM")
        j = mock.last_request()
        assert j.method == "DELETE"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Conferences/CF_RM"
            "/Participants/CA_RM"
        )


# ---- Recordings ----------------------------------------------------------


class TestCompatConferencesListRecordings:
    def test_returns_paginated_recordings(self, signalwire_client, mock):
        result = signalwire_client.compat.conferences.list_recordings("CF_LR")
        assert isinstance(result, dict)
        assert "recordings" in result, f"expected 'recordings' key, got {sorted(result)!r}"
        assert isinstance(result["recordings"], list)

    def test_journal_records_get_recordings(self, signalwire_client, mock):
        signalwire_client.compat.conferences.list_recordings("CF_LRX")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Conferences/CF_LRX/Recordings"
        )


class TestCompatConferencesGetRecording:
    def test_returns_recording_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.conferences.get_recording(
            "CF_GR", "RE_GR"
        )
        assert isinstance(result, dict)
        # Recording resources carry call_sid plus channel/status.
        assert "sid" in result or "call_sid" in result

    def test_journal_records_get_recording(self, signalwire_client, mock):
        signalwire_client.compat.conferences.get_recording("CF_GRX", "RE_GRX")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Conferences/CF_GRX"
            "/Recordings/RE_GRX"
        )


class TestCompatConferencesUpdateRecording:
    def test_returns_recording_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.conferences.update_recording(
            "CF_URC", "RE_URC", Status="paused"
        )
        assert isinstance(result, dict)
        assert "sid" in result or "status" in result

    def test_journal_records_post_with_status(self, signalwire_client, mock):
        signalwire_client.compat.conferences.update_recording(
            "CF_UR", "RE_UR", Status="paused"
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Conferences/CF_UR"
            "/Recordings/RE_UR"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("Status") == "paused"


class TestCompatConferencesDeleteRecording:
    def test_no_exception_on_delete(self, signalwire_client, mock):
        result = signalwire_client.compat.conferences.delete_recording(
            "CF_DR", "RE_DR"
        )
        assert isinstance(result, dict)

    def test_journal_records_delete(self, signalwire_client, mock):
        signalwire_client.compat.conferences.delete_recording("CF_DRX", "RE_DRX")
        j = mock.last_request()
        assert j.method == "DELETE"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Conferences/CF_DRX"
            "/Recordings/RE_DRX"
        )


# ---- Streams -------------------------------------------------------------


class TestCompatConferencesStartStream:
    def test_returns_stream_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.conferences.start_stream(
            "CF_SS", Url="wss://a.b/s"
        )
        assert isinstance(result, dict)
        assert "sid" in result or "name" in result

    def test_journal_records_post_to_streams(self, signalwire_client, mock):
        signalwire_client.compat.conferences.start_stream(
            "CF_SSX", Url="wss://a.b/s", Name="strm"
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Conferences/CF_SSX/Streams"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("Url") == "wss://a.b/s"


class TestCompatConferencesStopStream:
    def test_returns_stream_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.conferences.stop_stream(
            "CF_TS", "ST_TS", Status="stopped"
        )
        assert isinstance(result, dict)
        assert "sid" in result or "status" in result

    def test_journal_records_post_to_specific_stream(self, signalwire_client, mock):
        signalwire_client.compat.conferences.stop_stream(
            "CF_TSX", "ST_TSX", Status="stopped"
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Conferences/CF_TSX"
            "/Streams/ST_TSX"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("Status") == "stopped"
