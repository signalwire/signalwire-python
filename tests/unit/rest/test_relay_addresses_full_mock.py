"""Full success + error coverage for ``client.addresses`` (relay-rest).

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template.  Addresses is a
list/create/get/delete resource (no update) at ``/api/relay/rest/addresses``.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

_BASE = "/api/relay/rest/addresses"


class TestRelayAddressesSuccess:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.addresses.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == _BASE
        assert last.matched_route == "relay-rest.list_addresses"

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.addresses.create(
            label="HQ",
            country="US",
            first_name="Ada",
            last_name="Lovelace",
            street_number="123",
            street_name="Main St",
            city="Austin",
            state="TX",
            postal_code="78701",
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == _BASE
        assert last.matched_route == "relay-rest.create_address"
        assert last.body and last.body.get("label") == "HQ"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.addresses.get("addr-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/addr-1"
        assert last.matched_route == "relay-rest.get_address"

    def test_delete(self, signalwire_client, mock):
        signalwire_client.addresses.delete("addr-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{_BASE}/addr-1"
        assert last.matched_route == "relay-rest.delete_address"


class TestRelayAddressesErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.list_addresses", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.addresses.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_addresses"
        assert last.response_status == 500

    def test_create_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.create_address", 422, {"error": "name required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.addresses.create(
                label="HQ",
                country="US",
                first_name="Ada",
                last_name="Lovelace",
                street_number="123",
                street_name="Main St",
                city="Austin",
                state="TX",
                postal_code="78701",
            )
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.create_address"
        assert last.response_status == 422

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.get_address", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.addresses.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.get_address"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.delete_address", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.addresses.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.delete_address"
        assert last.response_status == 404
