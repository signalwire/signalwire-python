"""Full success + error coverage for ``client.video.room_recordings``.

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template: SUCCESS test
(real SDK call against the live mock, asserting body shape + journal
method/path/matched_route) and ERROR test (``mock.push_scenario`` arms a 4xx/5xx;
the SDK must raise ``SignalWireRestError`` with the right ``.status_code`` and the
journal records the error status).

``room_recordings`` is the top-level recordings collection: list / get / delete
plus the events sub-collection.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError


class TestVideoRoomRecordingsSuccess:
    """Happy path: each room_recording route hit with a 2xx on its canonical path."""

    def test_list(self, signalwire_client, mock):
        body = signalwire_client.video.room_recordings.list()
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_recordings"
        assert last.matched_route == "video.list_room_recordings", (
            f"expected video.list_room_recordings, got {last.matched_route!r}"
        )

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.video.room_recordings.get("rec-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_recordings/rec-1"
        assert last.matched_route == "video.get_room_recording", (
            f"expected video.get_room_recording, got {last.matched_route!r}"
        )

    def test_delete(self, signalwire_client, mock):
        body = signalwire_client.video.room_recordings.delete("rec-1")
        assert isinstance(body, dict)  # SDK turns 204/empty into {}
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/video/room_recordings/rec-1"
        assert last.matched_route == "video.delete_room_recording", (
            f"expected video.delete_room_recording, got {last.matched_route!r}"
        )

    def test_list_events(self, signalwire_client, mock):
        body = signalwire_client.video.room_recordings.list_events("rec-1")
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_recordings/rec-1/events"
        assert last.matched_route == "video.list_room_recording_events", (
            f"expected video.list_room_recording_events, got {last.matched_route!r}"
        )


class TestVideoRoomRecordingsErrors:
    """Failure path: each room_recording route exercised with a 4xx/5xx."""

    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("video.list_room_recordings", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_recordings.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "video.list_room_recordings"
        assert last.response_status == 500

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.get_room_recording", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_recordings.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.get_room_recording"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.delete_room_recording", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_recordings.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.delete_room_recording"
        assert last.response_status == 404

    def test_list_events_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.list_room_recording_events", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_recordings.list_events("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.list_room_recording_events"
        assert last.response_status == 404
