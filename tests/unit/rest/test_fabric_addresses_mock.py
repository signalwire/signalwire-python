"""Fabric address-management resources against the in-process ``mock_signalwire``.

Covers the three resources folded into ``client.fabric`` by the
``rest-apis/fabric-addresses`` spec:

* ``client.fabric.sip_addresses``
* ``client.fabric.phone_number_addresses``
* ``client.fabric.alias_addresses``

Each resource is exercised end-to-end over the shared HTTP mock (no
``requests`` mock.patch): every CRUD op asserts the on-the-wire
``(method, path, matched_route)`` the SDK built matches the spec, plus a
structured ``401 Unauthorized`` and ``404 Not Found`` error path (Q2 error
bodies) is proven to surface as ``SignalWireRestError`` with the right
``status_code``.
"""

from __future__ import annotations

import pytest

from signalwire.rest.client import RestClient
from signalwire.rest._base import SignalWireRestError
from .conftest import _MockHarness


class TestSipAddresses:
    """``client.fabric.sip_addresses.*`` — full CRUD, PATCH update."""

    def test_list(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        body = signalwire_client.fabric.sip_addresses.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/sip_addresses"
        assert last.matched_route == "fabric-addresses.list_sip_addresses"

    def test_create(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.fabric.sip_addresses.create(
            name="support-line", calling_handler_resource_id="res-1"
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/sip_addresses"
        assert last.matched_route == "fabric-addresses.create_sip_address"
        assert last.body["name"] == "support-line"
        assert last.body["calling_handler_resource_id"] == "res-1"

    def test_get(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.fabric.sip_addresses.get("sip-1")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/sip_addresses/sip-1"
        assert last.matched_route == "fabric-addresses.get_sip_address"

    def test_update_uses_patch(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_addresses.update("sip-1", name="renamed")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.path == "/api/fabric/sip_addresses/sip-1"
        assert last.matched_route == "fabric-addresses.update_sip_address"
        assert last.body["name"] == "renamed"

    def test_delete(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.fabric.sip_addresses.delete("sip-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/fabric/sip_addresses/sip-1"
        assert last.matched_route == "fabric-addresses.delete_sip_address"

    def test_unauthorized_401(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric-addresses.list_sip_addresses", 401, {"error": "Unauthorized"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_addresses.list()
        assert exc.value.status_code == 401

    def test_not_found_404(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric-addresses.get_sip_address", 404, {"error": "Not Found"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_addresses.get("missing")
        assert exc.value.status_code == 404


class TestPhoneNumberAddresses:
    """``client.fabric.phone_number_addresses.*`` — assign-only CRUD, PATCH update."""

    def test_list(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.fabric.phone_number_addresses.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/phone_number_addresses"
        assert last.matched_route == "fabric-addresses.list_phone_number_addresses"

    def test_create(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.fabric.phone_number_addresses.create(
            resource_id="res-1", handler_type="calling"
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/phone_number_addresses"
        assert last.matched_route == "fabric-addresses.create_phone_number_address"
        assert last.body["resource_id"] == "res-1"
        assert last.body["handler_type"] == "calling"

    def test_get(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.fabric.phone_number_addresses.get("pn-1")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/phone_number_addresses/pn-1"
        assert last.matched_route == "fabric-addresses.get_phone_number_address"

    def test_update_uses_patch(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.phone_number_addresses.update("pn-1", name="renamed")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.path == "/api/fabric/phone_number_addresses/pn-1"
        assert last.matched_route == "fabric-addresses.update_phone_number_address"

    def test_delete(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.fabric.phone_number_addresses.delete("pn-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/fabric/phone_number_addresses/pn-1"
        assert last.matched_route == "fabric-addresses.delete_phone_number_address"

    def test_unauthorized_401(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric-addresses.list_phone_number_addresses",
            401,
            {"error": "Unauthorized"},
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.phone_number_addresses.list()
        assert exc.value.status_code == 401

    def test_not_found_404(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric-addresses.get_phone_number_address", 404, {"error": "Not Found"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.phone_number_addresses.get("missing")
        assert exc.value.status_code == 404


class TestAliasAddresses:
    """``client.fabric.alias_addresses.*`` — full CRUD, PATCH update."""

    def test_list(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.fabric.alias_addresses.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/alias_addresses"
        assert last.matched_route == "fabric-addresses.list_alias_addresses"

    def test_create(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.fabric.alias_addresses.create(
            name="support", resource_id="res-1"
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/alias_addresses"
        assert last.matched_route == "fabric-addresses.create_alias_address"
        assert last.body["name"] == "support"
        assert last.body["resource_id"] == "res-1"

    def test_get(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.fabric.alias_addresses.get("al-1")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/alias_addresses/al-1"
        assert last.matched_route == "fabric-addresses.get_alias_address"

    def test_update_uses_patch(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.alias_addresses.update("al-1", name="renamed")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.path == "/api/fabric/alias_addresses/al-1"
        assert last.matched_route == "fabric-addresses.update_alias_address"

    def test_delete(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.fabric.alias_addresses.delete("al-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/fabric/alias_addresses/al-1"
        assert last.matched_route == "fabric-addresses.delete_alias_address"

    def test_unauthorized_401(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric-addresses.list_alias_addresses", 401, {"error": "Unauthorized"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.alias_addresses.list()
        assert exc.value.status_code == 401

    def test_not_found_404(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric-addresses.get_alias_address", 404, {"error": "Not Found"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.alias_addresses.get("missing")
        assert exc.value.status_code == 404
