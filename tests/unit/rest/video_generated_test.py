"""AUTO-GENERATED REST wire tests for the `video` namespace — DO NOT EDIT.
Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py

Each route the SDK implements (captured from the real client by python_route_registry,
joined to the spec operationId) gets a SUCCESS test (call it, assert method/path/route on
the mock journal) and an ERROR test (arm a 5xx, assert SignalWireRestError). The assertion
oracle is the spec operationId — independent of the resource generator — so these catch
SDK-vs-contract drift, not just a generator self-snapshot. Full-mock harness fixtures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from signalwire.rest._base import SignalWireRestError

if TYPE_CHECKING:
    from signalwire.rest.client import RestClient

    from .conftest import _MockHarness


class TestVideoWire:
    def test_conference_tokens_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.conference_tokens.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.get_conference_token"

    def test_conference_tokens_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.get_conference_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conference_tokens.get("test-id")
        assert exc.value.status_code == 500

    def test_conference_tokens_reset(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.conference_tokens.reset("test-id")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "video.reset_conference_token"

    def test_conference_tokens_reset_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.reset_conference_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conference_tokens.reset("test-id")
        assert exc.value.status_code == 500

    def test_conferences_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.conferences.create(display_name="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "video.create_video_conference"

    def test_conferences_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.create_video_conference", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.create(display_name="x")
        assert exc.value.status_code == 500

    def test_conferences_create_stream(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.conferences.create_stream("test-id", url="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "video.create_conference_stream"

    def test_conferences_create_stream_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.create_conference_stream", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.create_stream("test-id", url="x")
        assert exc.value.status_code == 500

    def test_conferences_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.conferences.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "video.delete_video_conference"

    def test_conferences_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.delete_video_conference", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.delete("test-id")
        assert exc.value.status_code == 500

    def test_conferences_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.conferences.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.get_video_conference"

    def test_conferences_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.get_video_conference", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.get("test-id")
        assert exc.value.status_code == 500

    def test_conferences_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.conferences.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.list_video_conferences"

    def test_conferences_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.list_video_conferences", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.list()
        assert exc.value.status_code == 500

    def test_conferences_list_conference_tokens(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.conferences.list_conference_tokens("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.list_conference_tokens"

    def test_conferences_list_conference_tokens_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.list_conference_tokens", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.list_conference_tokens("test-id")
        assert exc.value.status_code == 500

    def test_conferences_list_streams(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.conferences.list_streams("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.list_conference_streams"

    def test_conferences_list_streams_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.list_conference_streams", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.list_streams("test-id")
        assert exc.value.status_code == 500

    def test_conferences_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.conferences.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "video.update_video_conference"

    def test_conferences_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.update_video_conference", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.update("test-id")
        assert exc.value.status_code == 500

    def test_room_recordings_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.room_recordings.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "video.delete_room_recording"

    def test_room_recordings_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.delete_room_recording", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_recordings.delete("test-id")
        assert exc.value.status_code == 500

    def test_room_recordings_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.room_recordings.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.get_room_recording"

    def test_room_recordings_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.get_room_recording", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_recordings.get("test-id")
        assert exc.value.status_code == 500

    def test_room_recordings_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.room_recordings.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.list_room_recordings"

    def test_room_recordings_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.list_room_recordings", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_recordings.list()
        assert exc.value.status_code == 500

    def test_room_recordings_list_events(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.room_recordings.list_events("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.list_room_recording_events"

    def test_room_recordings_list_events_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.list_room_recording_events", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_recordings.list_events("test-id")
        assert exc.value.status_code == 500

    def test_room_sessions_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.room_sessions.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.get_room_session"

    def test_room_sessions_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.get_room_session", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_sessions.get("test-id")
        assert exc.value.status_code == 500

    def test_room_sessions_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.room_sessions.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.list_room_sessions"

    def test_room_sessions_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.list_room_sessions", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_sessions.list()
        assert exc.value.status_code == 500

    def test_room_sessions_list_events(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.room_sessions.list_events("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.list_room_session_events"

    def test_room_sessions_list_events_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.list_room_session_events", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_sessions.list_events("test-id")
        assert exc.value.status_code == 500

    def test_room_sessions_list_members(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.room_sessions.list_members("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.list_room_session_members"

    def test_room_sessions_list_members_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.list_room_session_members", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_sessions.list_members("test-id")
        assert exc.value.status_code == 500

    def test_room_sessions_list_recordings(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.room_sessions.list_recordings("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.list_room_session_recordings"

    def test_room_sessions_list_recordings_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.list_room_session_recordings", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_sessions.list_recordings("test-id")
        assert exc.value.status_code == 500

    def test_room_tokens_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.room_tokens.create(room_name="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "video.create_room_token"

    def test_room_tokens_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.create_room_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_tokens.create(room_name="x")
        assert exc.value.status_code == 500

    def test_rooms_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.rooms.create(name="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "video.create_room"

    def test_rooms_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.create_room", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.create(name="x")
        assert exc.value.status_code == 500

    def test_rooms_create_stream(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.rooms.create_stream("test-id", url="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "video.create_room_stream"

    def test_rooms_create_stream_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.create_room_stream", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.create_stream("test-id", url="x")
        assert exc.value.status_code == 500

    def test_rooms_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.rooms.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "video.delete_room"

    def test_rooms_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.delete_room", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.delete("test-id")
        assert exc.value.status_code == 500

    def test_rooms_get(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.video.rooms.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.get_room_by_name"

    def test_rooms_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.get_room_by_name", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.get("test-id")
        assert exc.value.status_code == 500

    def test_rooms_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.rooms.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.list_rooms"

    def test_rooms_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.list_rooms", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.list()
        assert exc.value.status_code == 500

    def test_rooms_list_streams(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.rooms.list_streams("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.list_room_streams"

    def test_rooms_list_streams_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.list_room_streams", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.list_streams("test-id")
        assert exc.value.status_code == 500

    def test_rooms_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.rooms.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "video.update_room"

    def test_rooms_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.update_room", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.update("test-id")
        assert exc.value.status_code == 500

    def test_streams_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.streams.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "video.delete_stream"

    def test_streams_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.delete_stream", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.streams.delete("test-id")
        assert exc.value.status_code == 500

    def test_streams_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.streams.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "video.get_stream"

    def test_streams_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.get_stream", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.streams.get("test-id")
        assert exc.value.status_code == 500

    def test_streams_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.streams.update("test-id", url="x")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "video.update_stream"

    def test_streams_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("video.update_stream", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.streams.update("test-id", url="x")
        assert exc.value.status_code == 500
