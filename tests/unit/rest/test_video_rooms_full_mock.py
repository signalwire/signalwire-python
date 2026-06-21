"""Full success + error coverage for ``client.video.rooms`` and ``room_tokens``.

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template: every canonical
``video.*room*`` route gets a SUCCESS test (call the real SDK method against the
live mock, assert the parsed body shape AND the journal entry's method + exact
path + matched_route) and an ERROR test (arm a 4xx/5xx via
``mock.push_scenario`` and assert the SDK raises ``SignalWireRestError`` with the
right ``.status_code`` while the journal records the error status).

NOTE on ``video.get_room`` vs ``video.get_room_by_name``: the spec exposes two
operations on the SAME wire shape — ``GET /api/video/rooms/{id}`` and
``GET /api/video/rooms/{name}``. The mock router ranks templated routes by length
and resolves any ``GET /api/video/rooms/X`` to ``video.get_room_by_name`` (the
longer ``{name}`` template wins), so the SDK's ``rooms.get(id)`` is journaled as
``video.get_room_by_name``. ``video.get_room`` is therefore not independently
reachable on the wire (coverage ambiguity, reported to the orchestrator).
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError


class TestVideoRoomsSuccess:
    """Happy path: each room/room_token route hit with a 2xx on its canonical path."""

    def test_list_rooms(self, signalwire_client, mock):
        body = signalwire_client.video.rooms.list()
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/rooms"
        assert last.matched_route == "video.list_rooms", (
            f"expected video.list_rooms, got {last.matched_route!r}"
        )

    def test_create_room(self, signalwire_client, mock):
        body = signalwire_client.video.rooms.create(name="room-alpha")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/video/rooms"
        assert last.matched_route == "video.create_room", (
            f"expected video.create_room, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("name") == "room-alpha"

    def test_get_room_by_name(self, signalwire_client, mock):
        # rooms.get hits GET /api/video/rooms/{id}; the router resolves the
        # shared wire shape to the longer ``{name}`` template.
        body = signalwire_client.video.rooms.get("room-1001")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/rooms/room-1001"
        assert last.matched_route == "video.get_room_by_name", (
            f"expected video.get_room_by_name, got {last.matched_route!r}"
        )

    def test_update_room(self, signalwire_client, mock):
        body = signalwire_client.video.rooms.update("room-1001", display_name="renamed")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == "/api/video/rooms/room-1001"
        assert last.matched_route == "video.update_room", (
            f"expected video.update_room, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("display_name") == "renamed"

    def test_delete_room(self, signalwire_client, mock):
        signalwire_client.video.rooms.delete("room-1001")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/video/rooms/room-1001"
        assert last.matched_route == "video.delete_room", (
            f"expected video.delete_room, got {last.matched_route!r}"
        )

    def test_list_room_streams(self, signalwire_client, mock):
        body = signalwire_client.video.rooms.list_streams("room-1001")
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/rooms/room-1001/streams"
        assert last.matched_route == "video.list_room_streams", (
            f"expected video.list_room_streams, got {last.matched_route!r}"
        )

    def test_create_room_stream(self, signalwire_client, mock):
        body = signalwire_client.video.rooms.create_stream(
            "room-1001", url="rtmp://example.com/live"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/video/rooms/room-1001/streams"
        assert last.matched_route == "video.create_room_stream", (
            f"expected video.create_room_stream, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("url") == "rtmp://example.com/live"

    def test_create_room_token(self, signalwire_client, mock):
        body = signalwire_client.video.room_tokens.create(room_name="room-alpha")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/video/room_tokens"
        assert last.matched_route == "video.create_room_token", (
            f"expected video.create_room_token, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("room_name") == "room-alpha"


class TestVideoRoomsErrors:
    """Failure path: each room/room_token route exercised with a 4xx/5xx."""

    def test_list_rooms_server_error(self, signalwire_client, mock):
        mock.push_scenario("video.list_rooms", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "video.list_rooms"
        assert last.response_status == 500

    def test_create_room_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("video.create_room", 422, {"error": "name required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.create()
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "video.create_room"
        assert last.response_status == 422

    def test_get_room_by_name_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.get_room_by_name", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.get_room_by_name"
        assert last.response_status == 404

    def test_update_room_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.update_room", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.update("missing", display_name="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.update_room"
        assert last.response_status == 404

    def test_delete_room_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.delete_room", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.delete_room"
        assert last.response_status == 404

    def test_list_room_streams_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.list_room_streams", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.list_streams("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.list_room_streams"
        assert last.response_status == 404

    def test_create_room_stream_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("video.create_room_stream", 422, {"error": "url required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.rooms.create_stream("room-1001")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "video.create_room_stream"
        assert last.response_status == 422

    def test_create_room_token_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("video.create_room_token", 422, {"error": "room_name required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.room_tokens.create()
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "video.create_room_token"
        assert last.response_status == 422
