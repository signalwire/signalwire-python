"""Logs namespace coverage against the in-process ``mock_signalwire`` server.

The Logs namespace fans out across four spec docs (message/voice/fax/logs)
because each kind of log lives at a different sub-API. Each sub-resource
has a small surface (``list``, ``get``, optional ``list_events``) and the
existing legacy tests only touched ``VoiceLogs.list_events``. This module
closes the rest of the gap.

Each test:
1. Calls the SDK against the live mock server.
2. Asserts the response body is a dict (logs endpoints return JSON objects).
3. Asserts the journal records the right (METHOD, PATH).
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Message Logs — /api/messaging/logs
# ---------------------------------------------------------------------------


class TestMessageLogs:
    """``client.logs.messages.*`` — list and per-id get."""

    def test_list_returns_dict(self, signalwire_client, mock):
        body = signalwire_client.logs.messages.list()
        assert isinstance(body, dict), f"expected dict, got {type(body).__name__}"

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/messaging/logs"
        assert last.matched_route == "message.list_message_logs", (
            f"expected message.list_message_logs, got {last.matched_route!r}"
        )

    def test_get_uses_id_in_path(self, signalwire_client, mock):
        body = signalwire_client.logs.messages.get("ml-42")
        assert isinstance(body, dict)
        # Single-log endpoint returns one resource object, not a collection.

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/messaging/logs/ml-42"
        assert last.matched_route is not None, "spec gap: message log retrieve"


# ---------------------------------------------------------------------------
# Voice Logs — /api/voice/logs
# ---------------------------------------------------------------------------


class TestVoiceLogs:
    """``client.logs.voice.*`` — list and per-id get (events covered elsewhere)."""

    def test_list_returns_dict(self, signalwire_client, mock):
        body = signalwire_client.logs.voice.list()
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/voice/logs"
        assert last.matched_route == "voice.list_voice_logs"

    def test_get_uses_id_in_path(self, signalwire_client, mock):
        body = signalwire_client.logs.voice.get("vl-99")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/voice/logs/vl-99"


# ---------------------------------------------------------------------------
# Fax Logs — /api/fax/logs
# ---------------------------------------------------------------------------


class TestFaxLogs:
    """``client.logs.fax.*`` — list and per-id get."""

    def test_list_returns_dict(self, signalwire_client, mock):
        body = signalwire_client.logs.fax.list()
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fax/logs"
        assert last.matched_route == "fax.list_fax_logs"

    def test_get_uses_id_in_path(self, signalwire_client, mock):
        body = signalwire_client.logs.fax.get("fl-7")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fax/logs/fl-7"


# ---------------------------------------------------------------------------
# Conference Logs — /api/logs/conferences
# ---------------------------------------------------------------------------


class TestConferenceLogs:
    """``client.logs.conferences.list`` — list-only resource."""

    def test_list_returns_dict(self, signalwire_client, mock):
        body = signalwire_client.logs.conferences.list()
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        # The conferences logs spec lives under /api/logs/conferences.
        assert last.path == "/api/logs/conferences"
        assert last.matched_route == "logs.list_conferences"
