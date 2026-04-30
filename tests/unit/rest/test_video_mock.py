"""Video namespace coverage against the in-process ``mock_signalwire`` server.

These tests exercise the Video API surface that wasn't reached by the legacy
``test_namespaces.TestVideo`` cases: room sessions, room recordings, conference
tokens, conference streams, and individual stream lifecycle.

Each test uses the real ``signalwire-python`` ``RestClient`` (no transport
patching), drives a single SDK method, and then asserts on:

1. The shape of the parsed response body.
2. The ``mock`` request journal: HTTP method + path the SDK actually sent.

Both halves matter — body shape proves the SDK consumes a spec-conformant
response, and the journal proves the SDK built the right URL.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Rooms — streams sub-resource
# ---------------------------------------------------------------------------


class TestVideoRoomsStreams:
    """Streams that hang off a Video Room."""

    def test_list_streams_returns_data_collection(self, signalwire_client, mock):
        body = signalwire_client.video.rooms.list_streams("room-1")
        assert isinstance(body, dict), f"expected dict, got {type(body).__name__}"
        # /api/video/rooms/{id}/streams returns a paginated list ('data').
        assert "data" in body, f"missing 'data' in body keys {sorted(body)!r}"
        assert isinstance(body["data"], list)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/rooms/room-1/streams"
        assert last.matched_route is not None, "spec gap: rooms streams list"

    def test_create_stream_posts_kwargs_in_body(self, signalwire_client, mock):
        body = signalwire_client.video.rooms.create_stream(
            "room-1", url="rtmp://example.com/live"
        )
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/video/rooms/room-1/streams"
        assert isinstance(last.body, dict)
        assert last.body.get("url") == "rtmp://example.com/live"


# ---------------------------------------------------------------------------
# Room Sessions
# ---------------------------------------------------------------------------


class TestVideoRoomSessions:
    """``client.video.room_sessions.*`` — list, get, sub-collections."""

    def test_list_returns_data_collection(self, signalwire_client, mock):
        body = signalwire_client.video.room_sessions.list()
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in body keys {sorted(body)!r}"
        assert isinstance(body["data"], list)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_sessions"

    def test_get_returns_session_object(self, signalwire_client, mock):
        body = signalwire_client.video.room_sessions.get("sess-abc")
        assert isinstance(body, dict)
        # /room_sessions/{id} synthesises a single resource object.

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_sessions/sess-abc"
        assert last.matched_route is not None

    def test_list_events_uses_events_subpath(self, signalwire_client, mock):
        body = signalwire_client.video.room_sessions.list_events("sess-1")
        assert isinstance(body, dict)
        assert "data" in body and isinstance(body["data"], list)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_sessions/sess-1/events"

    def test_list_recordings_uses_recordings_subpath(self, signalwire_client, mock):
        body = signalwire_client.video.room_sessions.list_recordings("sess-2")
        assert isinstance(body, dict)
        assert "data" in body

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_sessions/sess-2/recordings"


# ---------------------------------------------------------------------------
# Room Recordings (different resource than session-scoped recordings)
# ---------------------------------------------------------------------------


class TestVideoRoomRecordings:
    """``client.video.room_recordings.*`` — top-level recordings collection."""

    def test_list_returns_data_collection(self, signalwire_client, mock):
        body = signalwire_client.video.room_recordings.list()
        assert isinstance(body, dict)
        assert "data" in body and isinstance(body["data"], list)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_recordings"

    def test_get_returns_single_recording(self, signalwire_client, mock):
        body = signalwire_client.video.room_recordings.get("rec-xyz")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_recordings/rec-xyz"

    def test_delete_returns_empty_dict_for_204(self, signalwire_client, mock):
        # The mock synthesises 204/empty for DELETE which the SDK turns into {}.
        body = signalwire_client.video.room_recordings.delete("rec-del")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/video/room_recordings/rec-del"
        assert last.matched_route is not None

    def test_list_events_uses_events_subpath(self, signalwire_client, mock):
        body = signalwire_client.video.room_recordings.list_events("rec-1")
        assert isinstance(body, dict)
        assert "data" in body

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/room_recordings/rec-1/events"


# ---------------------------------------------------------------------------
# Conferences — sub-collections (tokens, streams)
# ---------------------------------------------------------------------------


class TestVideoConferences:
    """Sub-collection endpoints on ``client.video.conferences``."""

    def test_list_conference_tokens(self, signalwire_client, mock):
        body = signalwire_client.video.conferences.list_conference_tokens("conf-1")
        assert isinstance(body, dict)
        # Token-collection endpoints return 'data' arrays.
        assert "data" in body and isinstance(body["data"], list)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/conferences/conf-1/conference_tokens"

    def test_list_streams(self, signalwire_client, mock):
        body = signalwire_client.video.conferences.list_streams("conf-2")
        assert isinstance(body, dict)
        assert "data" in body and isinstance(body["data"], list)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/conferences/conf-2/streams"


# ---------------------------------------------------------------------------
# Conference Tokens (top-level resource)
# ---------------------------------------------------------------------------


class TestVideoConferenceTokens:
    """``client.video.conference_tokens.*`` — get/reset for a token resource."""

    def test_get_returns_single_token(self, signalwire_client, mock):
        body = signalwire_client.video.conference_tokens.get("tok-1")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/conference_tokens/tok-1"
        assert last.matched_route is not None

    def test_reset_posts_to_reset_subpath(self, signalwire_client, mock):
        body = signalwire_client.video.conference_tokens.reset("tok-2")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/video/conference_tokens/tok-2/reset"
        # reset is a no-body POST — body should be None or empty dict.
        assert last.body in (None, {}, "")


# ---------------------------------------------------------------------------
# Streams (top-level)
# ---------------------------------------------------------------------------


class TestVideoStreams:
    """``client.video.streams.*`` — get / update (PUT) / delete by stream id."""

    def test_get_returns_stream_resource(self, signalwire_client, mock):
        body = signalwire_client.video.streams.get("stream-1")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/streams/stream-1"

    def test_update_uses_put_with_kwargs(self, signalwire_client, mock):
        # VideoStreams.update calls self._http.put(path, body=kwargs)
        body = signalwire_client.video.streams.update(
            "stream-2", url="rtmp://example.com/new"
        )
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == "/api/video/streams/stream-2"
        assert isinstance(last.body, dict)
        assert last.body.get("url") == "rtmp://example.com/new"

    def test_delete(self, signalwire_client, mock):
        body = signalwire_client.video.streams.delete("stream-3")
        assert isinstance(body, dict)  # SDK turns 204 into {}

        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/video/streams/stream-3"
        assert last.matched_route is not None
