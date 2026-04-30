"""Compat Recordings + Transcriptions tests.

Both resources expose the same surface (list / get / delete) and use the
account-scoped LAML path.  Six gap entries total:

  - CompatRecordings:    list, get, delete
  - CompatTranscriptions: list, get, delete
"""

from __future__ import annotations


# ---- Recordings ----------------------------------------------------------


class TestCompatRecordingsList:
    def test_returns_paginated_recordings(self, signalwire_client, mock):
        result = signalwire_client.compat.recordings.list()
        assert isinstance(result, dict)
        assert "recordings" in result, (
            f"expected 'recordings' key, got {sorted(result)!r}"
        )
        assert isinstance(result["recordings"], list)

    def test_journal_records_get(self, signalwire_client, mock):
        signalwire_client.compat.recordings.list()
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == "/api/laml/2010-04-01/Accounts/test_proj/Recordings"


class TestCompatRecordingsGet:
    def test_returns_recording_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.recordings.get("RE_TEST")
        assert isinstance(result, dict)
        # Recording resources carry call_sid + duration + sid.
        assert "sid" in result or "call_sid" in result

    def test_journal_records_get_with_sid(self, signalwire_client, mock):
        signalwire_client.compat.recordings.get("RE_GET")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Recordings/RE_GET"
        )


class TestCompatRecordingsDelete:
    def test_no_exception_on_delete(self, signalwire_client, mock):
        result = signalwire_client.compat.recordings.delete("RE_D")
        assert isinstance(result, dict)

    def test_journal_records_delete(self, signalwire_client, mock):
        signalwire_client.compat.recordings.delete("RE_DEL")
        j = mock.last_request()
        assert j.method == "DELETE"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Recordings/RE_DEL"
        )


# ---- Transcriptions ------------------------------------------------------


class TestCompatTranscriptionsList:
    def test_returns_paginated_transcriptions(self, signalwire_client, mock):
        result = signalwire_client.compat.transcriptions.list()
        assert isinstance(result, dict)
        assert "transcriptions" in result, (
            f"expected 'transcriptions' key, got {sorted(result)!r}"
        )
        assert isinstance(result["transcriptions"], list)

    def test_journal_records_get(self, signalwire_client, mock):
        signalwire_client.compat.transcriptions.list()
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Transcriptions"
        )


class TestCompatTranscriptionsGet:
    def test_returns_transcription_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.transcriptions.get("TR_TEST")
        assert isinstance(result, dict)
        # Transcription resources carry duration + transcription_text + sid.
        assert "sid" in result or "duration" in result

    def test_journal_records_get_with_sid(self, signalwire_client, mock):
        signalwire_client.compat.transcriptions.get("TR_GET")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Transcriptions/TR_GET"
        )


class TestCompatTranscriptionsDelete:
    def test_no_exception_on_delete(self, signalwire_client, mock):
        result = signalwire_client.compat.transcriptions.delete("TR_D")
        assert isinstance(result, dict)

    def test_journal_records_delete(self, signalwire_client, mock):
        signalwire_client.compat.transcriptions.delete("TR_DEL")
        j = mock.last_request()
        assert j.method == "DELETE"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Transcriptions/TR_DEL"
        )
