"""Full success + error coverage for ``client.video.room_sessions``.

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template: SUCCESS test
(real SDK call against the live mock, asserting body shape + journal
method/path/matched_route) and ERROR test (``mock.push_scenario`` arms a 4xx/5xx;
the SDK must raise ``SignalWireRestError`` with the right ``.status_code`` and the
journal records the error status).

``room_sessions`` is read-only: list / get plus the events, members, and
recordings sub-collections.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError


class TestVideoRoomSessionsSuccess:
    """Happy path: each room_session route hit with a 2xx on its canonical path."""

    def test_list(self, signalwire_client, mock):
        body = signalwire_client.video.room_sessions.list()
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_sessions"
        assert last.matched_route == "video.list_room_sessions", (
            f"expected video.list_room_sessions, got {last.matched_route!r}"
        )

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.video.room_sessions.get("sess-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_sessions/sess-1"
        assert last.matched_route == "video.get_room_session", (
            f"expected video.get_room_session, got {last.matched_route!r}"
        )

    def test_list_events(self, signalwire_client, mock):
        body = signalwire_client.video.room_sessions.list_events("sess-1")
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_sessions/sess-1/events"
        assert last.matched_route == "video.list_room_session_events", (
            f"expected video.list_room_session_events, got {last.matched_route!r}"
        )

    def test_list_members(self, signalwire_client, mock):
        body = signalwire_client.video.room_sessions.list_members("sess-1")
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_sessions/sess-1/members"
        assert last.matched_route == "video.list_room_session_members", (
            f"expected video.list_room_session_members, got {last.matched_route!r}"
        )

    def test_list_recordings(self, signalwire_client, mock):
        body = signalwire_client.video.room_sessions.list_recordings("sess-1")
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_sessions/sess-1/recordings"
        assert last.matched_route == "video.list_room_session_recordings", (
            f"expected video.list_room_session_recordings, got {last.matched_route!r}"
        )


class TestVideoRoomSessionsErrors:
    """Failure path: each room_session route exercised with a 4xx/5xx."""

    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("video.list_room_sessions", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_sessions.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "video.list_room_sessions"
        assert last.response_status == 500

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.get_room_session", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_sessions.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.get_room_session"
        assert last.response_status == 404

    def test_list_events_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.list_room_session_events", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_sessions.list_events("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.list_room_session_events"
        assert last.response_status == 404

    def test_list_members_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.list_room_session_members", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_sessions.list_members("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.list_room_session_members"
        assert last.response_status == 404

    def test_list_recordings_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.list_room_session_recordings", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_sessions.list_recordings("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.list_room_session_recordings"
        assert last.response_status == 404
