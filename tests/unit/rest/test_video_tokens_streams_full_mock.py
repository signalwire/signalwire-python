"""Full success + error coverage for ``client.video.conference_tokens`` and
``client.video.streams`` (the top-level stream resource).

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template: SUCCESS test
(real SDK call against the live mock, asserting body shape + journal
method/path/matched_route) and ERROR test (``mock.push_scenario`` arms a 4xx/5xx;
the SDK must raise ``SignalWireRestError`` with the right ``.status_code`` and the
journal records the error status).

``conference_tokens``: get / reset.  ``streams``: get / update (PUT) / delete.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError


class TestVideoConferenceTokensSuccess:
    """Happy path: each conference_token route hit with a 2xx on its canonical path."""

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.video.conference_tokens.get("tok-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/conference_tokens/tok-1"
        assert last.matched_route == "video.get_conference_token", (
            f"expected video.get_conference_token, got {last.matched_route!r}"
        )

    def test_reset(self, signalwire_client, mock):
        body = signalwire_client.video.conference_tokens.reset("tok-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/video/conference_tokens/tok-1/reset"
        assert last.matched_route == "video.reset_conference_token", (
            f"expected video.reset_conference_token, got {last.matched_route!r}"
        )


class TestVideoConferenceTokensErrors:
    """Failure path: each conference_token route exercised with a 4xx/5xx."""

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.get_conference_token", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conference_tokens.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.get_conference_token"
        assert last.response_status == 404

    def test_reset_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.reset_conference_token", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.conference_tokens.reset("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.reset_conference_token"
        assert last.response_status == 404


class TestVideoStreamsSuccess:
    """Happy path: each top-level stream route hit with a 2xx on its canonical path."""

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.video.streams.get("stream-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/video/streams/stream-1"
        assert last.matched_route == "video.get_stream", (
            f"expected video.get_stream, got {last.matched_route!r}"
        )

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.video.streams.update(
            "stream-1", url="rtmp://example.com/new"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == "/api/video/streams/stream-1"
        assert last.matched_route == "video.update_stream", (
            f"expected video.update_stream, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("url") == "rtmp://example.com/new"

    def test_delete(self, signalwire_client, mock):
        body = signalwire_client.video.streams.delete("stream-1")
        assert isinstance(body, dict)  # SDK turns 204/empty into {}
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/video/streams/stream-1"
        assert last.matched_route == "video.delete_stream", (
            f"expected video.delete_stream, got {last.matched_route!r}"
        )


class TestVideoStreamsErrors:
    """Failure path: each top-level stream route exercised with a 4xx/5xx."""

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.get_stream", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.streams.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.get_stream"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.update_stream", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.streams.update("missing", url="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.update_stream"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("video.delete_stream", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.video.streams.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "video.delete_stream"
        assert last.response_status == 404
