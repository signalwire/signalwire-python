"""Full success + error coverage for ``client.video.conferences``.

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template: SUCCESS test
(real SDK call against the live mock, asserting body shape + journal
method/path/matched_route) and ERROR test (``mock.push_scenario`` arms a 4xx/5xx;
the SDK must raise ``SignalWireRestError`` with the right ``.status_code`` and the
journal records the error status).

``conferences`` is a CRUD resource (PUT update) plus the conference_tokens and
streams sub-collections (and create_stream).
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError


class TestVideoConferencesSuccess:
    """Happy path: each conference route hit with a 2xx on its canonical path."""

    def test_list(self, signalwire_client, mock):
        body = signalwire_client.video.conferences.list()
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/conferences"
        assert last.matched_route == "video.list_video_conferences", (
            f"expected video.list_video_conferences, got {last.matched_route!r}"
        )

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.video.conferences.create(
            name="conf-alpha", display_name="Conf Alpha"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/video/conferences"
        assert last.matched_route == "video.create_video_conference", (
            f"expected video.create_video_conference, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("name") == "conf-alpha"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.video.conferences.get("conf-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/conferences/conf-1"
        assert last.matched_route == "video.get_video_conference", (
            f"expected video.get_video_conference, got {last.matched_route!r}"
        )

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.video.conferences.update(
            "conf-1", display_name="renamed"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == "/api/video/conferences/conf-1"
        assert last.matched_route == "video.update_video_conference", (
            f"expected video.update_video_conference, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("display_name") == "renamed"

    def test_delete(self, signalwire_client, mock):
        signalwire_client.video.conferences.delete("conf-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/video/conferences/conf-1"
        assert last.matched_route == "video.delete_video_conference", (
            f"expected video.delete_video_conference, got {last.matched_route!r}"
        )

    def test_list_conference_tokens(self, signalwire_client, mock):
        body = signalwire_client.video.conferences.list_conference_tokens("conf-1")
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/conferences/conf-1/conference_tokens"
        assert last.matched_route == "video.list_conference_tokens", (
            f"expected video.list_conference_tokens, got {last.matched_route!r}"
        )

    def test_list_streams(self, signalwire_client, mock):
        body = signalwire_client.video.conferences.list_streams("conf-1")
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/conferences/conf-1/streams"
        assert last.matched_route == "video.list_conference_streams", (
            f"expected video.list_conference_streams, got {last.matched_route!r}"
        )

    def test_create_stream(self, signalwire_client, mock):
        body = signalwire_client.video.conferences.create_stream(
            "conf-1", url="rtmp://example.com/live"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/video/conferences/conf-1/streams"
        assert last.matched_route == "video.create_conference_stream", (
            f"expected video.create_conference_stream, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("url") == "rtmp://example.com/live"


class TestVideoConferencesErrors:
    """Failure path: each conference route exercised with a 4xx/5xx."""

    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("video.list_video_conferences", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "video.list_video_conferences"
        assert last.response_status == 500

    def test_create_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("video.create_video_conference", 422, {"error": "name required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.create(display_name="x")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "video.create_video_conference"
        assert last.response_status == 422

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.get_video_conference", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.get_video_conference"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.update_video_conference", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.update("missing", display_name="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.update_video_conference"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.delete_video_conference", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.delete_video_conference"
        assert last.response_status == 404

    def test_list_conference_tokens_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.list_conference_tokens", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.list_conference_tokens("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.list_conference_tokens"
        assert last.response_status == 404

    def test_list_streams_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.list_conference_streams", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.list_streams("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.list_conference_streams"
        assert last.response_status == 404

    def test_create_stream_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("video.create_conference_stream", 422, {"error": "url required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conferences.create_stream(
                "conf-1", url="rtmp://example.com/live"
            )
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "video.create_conference_stream"
        assert last.response_status == 422
