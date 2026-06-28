"""Full success + error coverage for the small REST specs (#56).

Mirrors the micro-template ``test_fabric_ai_agents_full_mock.py`` EXACTLY for the
remaining small spec groups, each route getting a 2xx SUCCESS test (real SDK call
+ journal method/path/matched_route) and a 4xx/5xx ERROR test (``push_scenario``
+ ``SignalWireRestError`` status_code + journal error status):

  - project    (3): client.project.tokens.create / update / delete
  - voice      (3): client.logs.voice.list / get / list_events
  - fax        (2): client.logs.fax.list / get
  - message    (2): client.logs.messages.list / get
  - calling    (1): client.calling.dial -> POST /api/calling/calls (command dispatch).
                    The happy path for calling is already covered exhaustively in
                    test_calling_mock.py; here we add the matched_route assertion
                    and the error case so calling.call-commands is fully covered.
  - chat       (1): client.chat.create_token
  - logs       (1): client.logs.conferences.list  (logs.list_conferences)
  - pubsub     (1): client.pubsub.create_token
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError


# ---------------------------------------------------------------------------
# project — API token management (create / update / delete)
# ---------------------------------------------------------------------------


class TestProjectTokensSuccess:
    def test_create(self, signalwire_client, mock):
        body = signalwire_client.project.tokens.create(
            name="ci-token", permissions=["calling"],
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/project/tokens"
        assert last.matched_route == "project.create_token", (
            f"expected project.create_token, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("name") == "ci-token"

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.project.tokens.update("tok-1", name="renamed")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.path == "/api/project/tokens/tok-1"
        assert last.matched_route == "project.update_token", (
            f"expected project.update_token, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("name") == "renamed"

    def test_delete(self, signalwire_client, mock):
        signalwire_client.project.tokens.delete("tok-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/project/tokens/tok-1"
        assert last.matched_route == "project.delete_token", (
            f"expected project.delete_token, got {last.matched_route!r}"
        )


class TestProjectTokensErrors:
    def test_create_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("project.create_token", 422, {"error": "name required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.project.tokens.create(name="x", permissions=["calling"])
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "project.create_token"
        assert last.response_status == 422

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario("project.update_token", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.project.tokens.update("missing", name="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "project.update_token"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("project.delete_token", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.project.tokens.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "project.delete_token"
        assert last.response_status == 404


# ---------------------------------------------------------------------------
# voice — voice logs (list / get / list_events)
# ---------------------------------------------------------------------------


class TestVoiceLogsSuccess:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.logs.voice.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/voice/logs"
        assert last.matched_route == "voice.list_voice_logs", (
            f"expected voice.list_voice_logs, got {last.matched_route!r}"
        )

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.logs.voice.get("vl-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/voice/logs/vl-1"
        assert last.matched_route == "voice.get_voice_log", (
            f"expected voice.get_voice_log, got {last.matched_route!r}"
        )

    def test_list_events(self, signalwire_client, mock):
        body = signalwire_client.logs.voice.list_events("vl-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/voice/logs/vl-1/events"
        assert last.matched_route == "voice.list_voice_log_events", (
            f"expected voice.list_voice_log_events, got {last.matched_route!r}"
        )


class TestVoiceLogsErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("voice.list_voice_logs", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.voice.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "voice.list_voice_logs"
        assert last.response_status == 500

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("voice.get_voice_log", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.voice.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "voice.get_voice_log"
        assert last.response_status == 404

    def test_list_events_not_found(self, signalwire_client, mock):
        mock.push_scenario("voice.list_voice_log_events", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.voice.list_events("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "voice.list_voice_log_events"
        assert last.response_status == 404


# ---------------------------------------------------------------------------
# fax — fax logs (list / get)
# ---------------------------------------------------------------------------


class TestFaxLogsSuccess:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.logs.fax.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fax/logs"
        assert last.matched_route == "fax.list_fax_logs", (
            f"expected fax.list_fax_logs, got {last.matched_route!r}"
        )

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.logs.fax.get("fl-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fax/logs/fl-1"
        assert last.matched_route == "fax.get_fax_log", (
            f"expected fax.get_fax_log, got {last.matched_route!r}"
        )


class TestFaxLogsErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("fax.list_fax_logs", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.fax.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "fax.list_fax_logs"
        assert last.response_status == 500

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("fax.get_fax_log", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.fax.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fax.get_fax_log"
        assert last.response_status == 404


# ---------------------------------------------------------------------------
# message — message logs (list / get)
# ---------------------------------------------------------------------------


class TestMessageLogsSuccess:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.logs.messages.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/messaging/logs"
        assert last.matched_route == "message.list_message_logs", (
            f"expected message.list_message_logs, got {last.matched_route!r}"
        )

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.logs.messages.get("ml-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/messaging/logs/ml-1"
        assert last.matched_route == "message.get_message_log", (
            f"expected message.get_message_log, got {last.matched_route!r}"
        )


class TestMessageLogsErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("message.list_message_logs", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.messages.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "message.list_message_logs"
        assert last.response_status == 500

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("message.get_message_log", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.messages.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "message.get_message_log"
        assert last.response_status == 404


# ---------------------------------------------------------------------------
# calling — command dispatch (POST /api/calling/calls). Happy path is covered
# in test_calling_mock.py; here we pin matched_route + add the error case.
# ---------------------------------------------------------------------------


class TestCallingCommandSuccess:
    def test_dial(self, signalwire_client, mock):
        body = signalwire_client.calling.dial(to="+15551112222", from_="+15553334444")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/calling/calls"
        assert last.matched_route == "calling.call-commands", (
            f"expected calling.call-commands, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("command") == "dial"


class TestCallingCommandErrors:
    def test_dial_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("calling.call-commands", 422, {"error": "bad command"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.calling.dial(to="+15551112222", from_="+15553334444")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "calling.call-commands"
        assert last.response_status == 422


# ---------------------------------------------------------------------------
# chat — token creation
# ---------------------------------------------------------------------------


class TestChatTokenSuccess:
    def test_create_token(self, signalwire_client, mock):
        body = signalwire_client.chat.create_token(ttl=60, channels={"room": {}})
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/chat/tokens"
        assert last.matched_route == "chat.create_chat_token", (
            f"expected chat.create_chat_token, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("channels") == {"room": {}}


class TestChatTokenErrors:
    def test_create_token_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("chat.create_chat_token", 422, {"error": "channels required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.chat.create_token(ttl=60, channels={"room": {}})
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "chat.create_chat_token"
        assert last.response_status == 422


# ---------------------------------------------------------------------------
# logs — conference logs (list)
# ---------------------------------------------------------------------------


class TestConferenceLogsSuccess:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.logs.conferences.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/logs/conferences"
        assert last.matched_route == "logs.list_conferences", (
            f"expected logs.list_conferences, got {last.matched_route!r}"
        )


class TestConferenceLogsErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("logs.list_conferences", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.conferences.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "logs.list_conferences"
        assert last.response_status == 500


# ---------------------------------------------------------------------------
# pubsub — token creation
# ---------------------------------------------------------------------------


class TestPubSubTokenSuccess:
    def test_create_token(self, signalwire_client, mock):
        body = signalwire_client.pubsub.create_token(ttl=15, channels={"news": {}})
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/pubsub/tokens"
        assert last.matched_route == "pubsub.create_token", (
            f"expected pubsub.create_token, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("channels") == {"news": {}}


class TestPubSubTokenErrors:
    def test_create_token_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("pubsub.create_token", 422, {"error": "channels required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.pubsub.create_token(ttl=15, channels={"news": {}})
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "pubsub.create_token"
        assert last.response_status == 422
