"""Full success + error coverage for ``client.compat.messages`` and
``client.compat.faxes`` — the LaML (Twilio-compatible) Messages / Faxes
resources and their Media sub-resources.

Mirrors ``test_fabric_ai_agents_full_mock.py``: each canonical route gets a
SUCCESS test (real SDK call, body shape + journal method/path/matched_route)
and an ERROR test (``mock.push_scenario`` arms a 4xx/5xx; the SDK raises
``SignalWireRestError`` with the matching ``status_code``).  Paths resolve under
the conftest's pinned project ``test_proj``.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

MSG = "/api/laml/2010-04-01/Accounts/test_proj/Messages"
FAX = "/api/laml/2010-04-01/Accounts/test_proj/Faxes"


class TestCompatMessagesSuccess:
    def test_list_messages(self, signalwire_client, mock):
        body = signalwire_client.compat.messages.list()
        assert isinstance(body, dict)
        assert "messages" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == MSG
        assert last.matched_route == "compatibility.list_messages"

    def test_create_message(self, signalwire_client, mock):
        body = signalwire_client.compat.messages.create(
            To="+15551112222", From="+15553334444", Body="hi"
        )
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == MSG
        assert last.matched_route == "compatibility.create_message"
        assert last.body and last.body.get("Body") == "hi"

    def test_list_media(self, signalwire_client, mock):
        body = signalwire_client.compat.messages.list_media("MM1")
        assert isinstance(body, dict)
        assert "media_list" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{MSG}/MM1/Media"
        assert last.matched_route == "compatibility.list_media"

    def test_retrieve_media(self, signalwire_client, mock):
        body = signalwire_client.compat.messages.get_media("MM1", "ME1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{MSG}/MM1/Media/ME1"
        assert last.matched_route == "compatibility.retrieve_media"

    def test_delete_message_media(self, signalwire_client, mock):
        signalwire_client.compat.messages.delete_media("MM1", "ME1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{MSG}/MM1/Media/ME1"
        assert last.matched_route == "compatibility.delete_message_media"

    def test_retrieve_message(self, signalwire_client, mock):
        body = signalwire_client.compat.messages.get("MM1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{MSG}/MM1"
        assert last.matched_route == "compatibility.retrieve_message"

    def test_update_message(self, signalwire_client, mock):
        body = signalwire_client.compat.messages.update("MM1", Body="redacted")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{MSG}/MM1"
        assert last.matched_route == "compatibility.update_message"
        assert last.body and last.body.get("Body") == "redacted"

    def test_delete_message(self, signalwire_client, mock):
        signalwire_client.compat.messages.delete("MM1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{MSG}/MM1"
        assert last.matched_route == "compatibility.delete_message"


class TestCompatMessagesErrors:
    def test_list_messages_server_error(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_messages", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.messages.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_messages"
        assert last.response_status == 500

    def test_create_message_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_message", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.messages.create(To="+1", From="+1", Body="x")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_message"
        assert last.response_status == 422

    def test_list_media_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_media", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.messages.list_media("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_media"
        assert last.response_status == 404

    def test_retrieve_media_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_media", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.messages.get_media("MM1", "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_media"
        assert last.response_status == 404

    def test_delete_message_media_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_message_media", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.messages.delete_media("MM1", "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_message_media"
        assert last.response_status == 404

    def test_retrieve_message_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_message", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.messages.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_message"
        assert last.response_status == 404

    def test_update_message_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_message", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.messages.update("missing", Body="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_message"
        assert last.response_status == 404

    def test_delete_message_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_message", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.messages.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_message"
        assert last.response_status == 404


class TestCompatFaxesSuccess:
    def test_list_all_faxes(self, signalwire_client, mock):
        body = signalwire_client.compat.faxes.list()
        assert isinstance(body, dict)
        assert "faxes" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == FAX
        assert last.matched_route == "compatibility.list_all_faxes"

    def test_send_fax(self, signalwire_client, mock):
        body = signalwire_client.compat.faxes.create(
            To="+15551112222", From="+15553334444", MediaUrl="https://x/y.pdf"
        )
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == FAX
        assert last.matched_route == "compatibility.send_fax"
        assert last.body and last.body.get("MediaUrl") == "https://x/y.pdf"

    def test_list_all_fax_media(self, signalwire_client, mock):
        body = signalwire_client.compat.faxes.list_media("FX1")
        assert isinstance(body, dict)
        assert "media" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{FAX}/FX1/Media"
        assert last.matched_route == "compatibility.list_all_fax_media"

    def test_retrieve_medias(self, signalwire_client, mock):
        body = signalwire_client.compat.faxes.get_media("FX1", "ME1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{FAX}/FX1/Media/ME1"
        assert last.matched_route == "compatibility.retrieve_medias"

    def test_delete_fax_media(self, signalwire_client, mock):
        signalwire_client.compat.faxes.delete_media("FX1", "ME1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{FAX}/FX1/Media/ME1"
        assert last.matched_route == "compatibility.delete_fax_media"

    def test_retrieve_fax(self, signalwire_client, mock):
        body = signalwire_client.compat.faxes.get("FX1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{FAX}/FX1"
        assert last.matched_route == "compatibility.retrieve_fax"

    def test_update_fax(self, signalwire_client, mock):
        body = signalwire_client.compat.faxes.update("FX1", Status="canceled")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{FAX}/FX1"
        assert last.matched_route == "compatibility.update_fax"
        assert last.body and last.body.get("Status") == "canceled"

    def test_delete_fax(self, signalwire_client, mock):
        signalwire_client.compat.faxes.delete("FX1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{FAX}/FX1"
        assert last.matched_route == "compatibility.delete_fax"


class TestCompatFaxesErrors:
    def test_list_all_faxes_server_error(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_all_faxes", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.faxes.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_all_faxes"
        assert last.response_status == 500

    def test_send_fax_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("compatibility.send_fax", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.faxes.create(To="+1", From="+1", MediaUrl="u")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "compatibility.send_fax"
        assert last.response_status == 422

    def test_list_all_fax_media_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_all_fax_media", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.faxes.list_media("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_all_fax_media"
        assert last.response_status == 404

    def test_retrieve_medias_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_medias", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.faxes.get_media("FX1", "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_medias"
        assert last.response_status == 404

    def test_delete_fax_media_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_fax_media", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.faxes.delete_media("FX1", "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_fax_media"
        assert last.response_status == 404

    def test_retrieve_fax_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_fax", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.faxes.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_fax"
        assert last.response_status == 404

    def test_update_fax_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_fax", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.faxes.update("missing", Status="canceled")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_fax"
        assert last.response_status == 404

    def test_delete_fax_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_fax", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.faxes.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_fax"
        assert last.response_status == 404
