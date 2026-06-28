"""Full success + error coverage for ``client.phone_numbers`` (relay-rest).

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template: every canonical
relay-rest phone-numbers route gets a SUCCESS test (call the real SDK method
against the live mock, assert the parsed body shape AND the journal entry:
method + exact canonical path + ``matched_route``) and an ERROR test (arm a
4xx/5xx via ``mock.push_scenario``, assert the SDK raises ``SignalWireRestError``
with the right ``status_code`` and the journal records the error status).

Base path: ``/api/relay/rest/phone_numbers``.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

_BASE = "/api/relay/rest/phone_numbers"


class TestRelayPhoneNumbersSuccess:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.phone_numbers.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == _BASE
        assert last.matched_route == "relay-rest.list_phone_numbers"

    def test_search(self, signalwire_client, mock):
        body = signalwire_client.phone_numbers.search(area_code="512")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/search"
        assert last.matched_route == "relay-rest.search_available_phone_numbers"

    def test_purchase(self, signalwire_client, mock):
        body = signalwire_client.phone_numbers.create(number="+15551230000")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == _BASE
        assert last.matched_route == "relay-rest.purchase_phone_number"
        assert last.body and last.body.get("number") == "+15551230000"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.phone_numbers.get("pn-1001")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/pn-1001"
        assert last.matched_route == "relay-rest.retrieve_phone_number"

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.phone_numbers.update("pn-1001", name="main line")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == f"{_BASE}/pn-1001"
        assert last.matched_route == "relay-rest.update_phone_number"
        assert last.body and last.body.get("name") == "main line"

    def test_release(self, signalwire_client, mock):
        signalwire_client.phone_numbers.delete("pn-1001")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{_BASE}/pn-1001"
        assert last.matched_route == "relay-rest.release_phone_number"


class TestRelayPhoneNumbersErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.list_phone_numbers", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_phone_numbers"
        assert last.response_status == 500

    def test_search_server_error(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.search_available_phone_numbers", 500, {"error": "internal"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.search(area_code="512")
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "relay-rest.search_available_phone_numbers"
        assert last.response_status == 500

    def test_purchase_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.purchase_phone_number", 422, {"error": "number required"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.create(number="+15558675309")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.purchase_phone_number"
        assert last.response_status == 422

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.retrieve_phone_number", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.retrieve_phone_number"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.update_phone_number", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.update("missing", name="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.update_phone_number"
        assert last.response_status == 404

    def test_release_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.release_phone_number", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.release_phone_number"
        assert last.response_status == 404
