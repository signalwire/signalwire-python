"""Full success + error coverage for the generic ``client.fabric.resources``
(``GenericResources``) and ``client.fabric.addresses`` (``FabricAddresses``).

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template: a SUCCESS test
(call the real SDK method against the live mock, assert the parsed body shape +
the journal entry's method/path/matched_route) and an ERROR test (arm a 4xx/5xx
via ``mock.push_scenario`` and assert the SDK raises ``SignalWireRestError`` with
the right ``status_code`` plus the journal recorded the error status) per route.

``resources`` is the cross-type generic resource (list/get/delete/list_addresses
plus the ``assign_*`` binding endpoints); ``addresses`` is read-only (list/get).
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError


class TestFabricResourcesSuccess:
    """Happy-path: each generic-resource route hit with a 2xx on its canonical path."""

    def test_list(self, signalwire_client, mock):
        body = signalwire_client.fabric.resources.list()
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/resources"
        assert last.matched_route == "fabric.list_resources", (
            f"expected fabric.list_resources, got {last.matched_route!r}"
        )

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.fabric.resources.get("res-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/resources/res-1"
        assert last.matched_route == "fabric.get_resource", (
            f"expected fabric.get_resource, got {last.matched_route!r}"
        )

    def test_delete(self, signalwire_client, mock):
        signalwire_client.fabric.resources.delete("res-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/fabric/resources/res-1"
        assert last.matched_route == "fabric.delete_resource", (
            f"expected fabric.delete_resource, got {last.matched_route!r}"
        )

    def test_list_addresses(self, signalwire_client, mock):
        body = signalwire_client.fabric.resources.list_addresses("res-1")
        assert isinstance(body, (dict, list))
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/resources/res-1/addresses"
        assert last.matched_route == "fabric.list_resource_addresses", (
            f"expected fabric.list_resource_addresses, got {last.matched_route!r}"
        )

    def test_assign_phone_route(self, signalwire_client, mock):
        # assign_phone_route is deprecated and emits a DeprecationWarning; the
        # call itself still hits POST /resources/{id}/phone_routes.
        with pytest.warns(DeprecationWarning):
            body = signalwire_client.fabric.resources.assign_phone_route(
                "res-1", phone_number="+15551230000"
            )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/resources/res-1/phone_routes"
        assert last.matched_route == "fabric.assign_resource_phone_route", (
            f"expected fabric.assign_resource_phone_route, got {last.matched_route!r}"
        )

    def test_assign_domain_application(self, signalwire_client, mock):
        body = signalwire_client.fabric.resources.assign_domain_application(
            "res-1", domain="example.test"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/resources/res-1/domain_applications"
        assert last.matched_route == "fabric.assign_resource_domain_application", (
            f"expected fabric.assign_resource_domain_application, got {last.matched_route!r}"
        )


class TestFabricAddressesSuccess:
    """Happy-path: read-only fabric addresses."""

    def test_list(self, signalwire_client, mock):
        body = signalwire_client.fabric.addresses.list()
        assert isinstance(body, (dict, list))
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/addresses"
        assert last.matched_route == "fabric.list_fabric_addresses", (
            f"expected fabric.list_fabric_addresses, got {last.matched_route!r}"
        )

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.fabric.addresses.get("addr-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/addresses/addr-1"
        assert last.matched_route == "fabric.get_fabric_address", (
            f"expected fabric.get_fabric_address, got {last.matched_route!r}"
        )


class TestFabricResourcesErrors:
    """Failure path: each route surfaces a 4xx/5xx as SignalWireRestError."""

    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("fabric.list_resources", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "fabric.list_resources"
        assert last.response_status == 500

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("fabric.get_resource", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.get_resource"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("fabric.delete_resource", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.delete_resource"
        assert last.response_status == 404

    def test_list_addresses_not_found(self, signalwire_client, mock):
        mock.push_scenario("fabric.list_resource_addresses", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.list_addresses("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.list_resource_addresses"
        assert last.response_status == 404

    def test_assign_phone_route_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.assign_resource_phone_route", 422, {"error": "bad target"}
        )
        with pytest.warns(DeprecationWarning), pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.assign_phone_route(
                "res-1", phone_number="+15551230000"
            )
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "fabric.assign_resource_phone_route"
        assert last.response_status == 422

    def test_assign_domain_application_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.assign_resource_domain_application", 422, {"error": "bad domain"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.assign_domain_application(
                "res-1", domain="bad"
            )
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "fabric.assign_resource_domain_application"
        assert last.response_status == 422


class TestFabricAddressesErrors:
    """Failure path for read-only addresses."""

    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("fabric.list_fabric_addresses", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.addresses.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "fabric.list_fabric_addresses"
        assert last.response_status == 500

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("fabric.get_fabric_address", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.addresses.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.get_fabric_address"
        assert last.response_status == 404
