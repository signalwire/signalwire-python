"""Full success + error coverage for ``client.compat.phone_numbers`` — the LaML
(Twilio-compatible) IncomingPhoneNumbers / ImportedPhoneNumbers /
AvailablePhoneNumbers resources.

Mirrors ``test_fabric_ai_agents_full_mock.py``: each canonical route gets a
SUCCESS test (real SDK call, body shape + journal method/path/matched_route)
and an ERROR test (``mock.push_scenario`` arms a 4xx/5xx; the SDK raises
``SignalWireRestError`` with the matching ``status_code``).  Paths resolve under
the conftest's pinned project ``test_proj``.

IMPLEMENTATION GAP: ``compatibility.list_available_phone_number_resources_by_country``
(``GET /AvailablePhoneNumbers/{IsoCountry}``) has NO corresponding SDK method —
``CompatPhoneNumbers`` only exposes ``list_available_countries`` (the collection),
``search_local`` and ``search_toll_free`` (the per-country Local/TollFree leaves),
with no method hitting the bare per-country resource.  No hollow test is written
for it; flagged for the orchestrator.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

INC = "/api/laml/2010-04-01/Accounts/test_proj/IncomingPhoneNumbers"
IMP = "/api/laml/2010-04-01/Accounts/test_proj/ImportedPhoneNumbers"
AVAIL = "/api/laml/2010-04-01/Accounts/test_proj/AvailablePhoneNumbers"


class TestCompatPhoneNumbersSuccess:
    def test_list_incoming_phone_numbers(self, signalwire_client, mock):
        body = signalwire_client.compat.phone_numbers.list()
        assert isinstance(body, dict)
        assert "incoming_phone_numbers" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == INC
        assert last.matched_route == "compatibility.list_incoming_phone_numbers"

    def test_create_incoming_phone_number(self, signalwire_client, mock):
        body = signalwire_client.compat.phone_numbers.purchase(PhoneNumber="+15551112222")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == INC
        assert last.matched_route == "compatibility.create_incoming_phone_number"
        assert last.body and last.body.get("PhoneNumber") == "+15551112222"

    def test_retrieve_incoming_phone_number(self, signalwire_client, mock):
        body = signalwire_client.compat.phone_numbers.get("PN1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{INC}/PN1"
        assert last.matched_route == "compatibility.retrieve_incoming_phone_number"

    def test_update_incoming_phone_number(self, signalwire_client, mock):
        body = signalwire_client.compat.phone_numbers.update("PN1", FriendlyName="renamed")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{INC}/PN1"
        assert last.matched_route == "compatibility.update_incoming_phone_number"
        assert last.body and last.body.get("FriendlyName") == "renamed"

    def test_delete_incoming_phone_number(self, signalwire_client, mock):
        signalwire_client.compat.phone_numbers.delete("PN1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{INC}/PN1"
        assert last.matched_route == "compatibility.delete_incoming_phone_number"

    def test_create_imported_phone_number(self, signalwire_client, mock):
        body = signalwire_client.compat.phone_numbers.import_number(PhoneNumber="+15551112222")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == IMP
        assert last.matched_route == "compatibility.create_imported_phone_number"
        assert last.body and last.body.get("PhoneNumber") == "+15551112222"

    def test_list_available_phone_number_resources(self, signalwire_client, mock):
        body = signalwire_client.compat.phone_numbers.list_available_countries()
        assert isinstance(body, dict)
        assert "countries" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == AVAIL
        assert last.matched_route == "compatibility.list_available_phone_number_resources"

    def test_search_local_available_phone_numbers(self, signalwire_client, mock):
        body = signalwire_client.compat.phone_numbers.search_local("US")
        assert isinstance(body, dict)
        assert "available_phone_numbers" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{AVAIL}/US/Local"
        assert last.matched_route == "compatibility.search_local_available_phone_numbers"

    def test_search_toll_free_available_phone_numbers(self, signalwire_client, mock):
        body = signalwire_client.compat.phone_numbers.search_toll_free("US")
        assert isinstance(body, dict)
        assert "available_phone_numbers" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{AVAIL}/US/TollFree"
        assert last.matched_route == "compatibility.search_toll_free_available_phone_numbers"


class TestCompatPhoneNumbersErrors:
    def test_list_incoming_phone_numbers_server_error(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_incoming_phone_numbers", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.phone_numbers.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_incoming_phone_numbers"
        assert last.response_status == 500

    def test_create_incoming_phone_number_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_incoming_phone_number", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.phone_numbers.purchase(PhoneNumber="+1")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_incoming_phone_number"
        assert last.response_status == 422

    def test_retrieve_incoming_phone_number_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.retrieve_incoming_phone_number", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.phone_numbers.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.retrieve_incoming_phone_number"
        assert last.response_status == 404

    def test_update_incoming_phone_number_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_incoming_phone_number", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.phone_numbers.update("missing", FriendlyName="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_incoming_phone_number"
        assert last.response_status == 404

    def test_delete_incoming_phone_number_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_incoming_phone_number", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.phone_numbers.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_incoming_phone_number"
        assert last.response_status == 404

    def test_create_imported_phone_number_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_imported_phone_number", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.phone_numbers.import_number(PhoneNumber="+1")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_imported_phone_number"
        assert last.response_status == 422

    def test_list_available_phone_number_resources_server_error(self, signalwire_client, mock):
        mock.push_scenario(
            "compatibility.list_available_phone_number_resources", 500, {"error": "internal"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.phone_numbers.list_available_countries()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_available_phone_number_resources"
        assert last.response_status == 500

    def test_search_local_available_phone_numbers_server_error(self, signalwire_client, mock):
        mock.push_scenario(
            "compatibility.search_local_available_phone_numbers", 500, {"error": "internal"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.phone_numbers.search_local("US")
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.search_local_available_phone_numbers"
        assert last.response_status == 500

    def test_search_toll_free_available_phone_numbers_server_error(self, signalwire_client, mock):
        mock.push_scenario(
            "compatibility.search_toll_free_available_phone_numbers", 500, {"error": "internal"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.phone_numbers.search_toll_free("US")
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.search_toll_free_available_phone_numbers"
        assert last.response_status == 500
