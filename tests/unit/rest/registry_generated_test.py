"""AUTO-GENERATED REST wire tests for the `registry` namespace — DO NOT EDIT.
Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py

Each route the SDK implements (captured from the real client by python_route_registry,
joined to the spec operationId) gets a SUCCESS test (call it, assert method/path/route on
the mock journal) and an ERROR test (arm a 5xx, assert SignalWireRestError). The assertion
oracle is the spec operationId — independent of the resource generator — so these catch
SDK-vs-contract drift, not just a generator self-snapshot. Full-mock harness fixtures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from signalwire.rest._base import SignalWireRestError

if TYPE_CHECKING:
    from signalwire.rest.client import RestClient

    from .conftest import _MockHarness


class TestRegistryWire:
    def test_brands_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.brands.create({})
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "relay-rest.create_brand"

    def test_brands_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.create_brand", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.brands.create({})
        assert exc.value.status_code == 500

    def test_brands_create_campaign(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.brands.create_campaign("test-id", {})
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "relay-rest.create_campaign"

    def test_brands_create_campaign_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.create_campaign", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.brands.create_campaign("test-id", {})
        assert exc.value.status_code == 500

    def test_brands_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.brands.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.retrieve_brand"

    def test_brands_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.retrieve_brand", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.brands.get("test-id")
        assert exc.value.status_code == 500

    def test_brands_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.brands.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_brands"

    def test_brands_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.list_brands", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.brands.list()
        assert exc.value.status_code == 500

    def test_brands_list_campaigns(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.brands.list_campaigns("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_campaigns"

    def test_brands_list_campaigns_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.list_campaigns", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.brands.list_campaigns("test-id")
        assert exc.value.status_code == 500

    def test_campaigns_create_order(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.campaigns.create_order("test-id")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "relay-rest.create_order"

    def test_campaigns_create_order_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.create_order", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.campaigns.create_order("test-id")
        assert exc.value.status_code == 500

    def test_campaigns_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.campaigns.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.retrieve_campaign"

    def test_campaigns_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.retrieve_campaign", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.campaigns.get("test-id")
        assert exc.value.status_code == 500

    def test_campaigns_list_numbers(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.campaigns.list_numbers("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_number_assignments"

    def test_campaigns_list_numbers_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.list_number_assignments", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.campaigns.list_numbers("test-id")
        assert exc.value.status_code == 500

    def test_campaigns_list_orders(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.campaigns.list_orders("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_orders"

    def test_campaigns_list_orders_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.list_orders", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.campaigns.list_orders("test-id")
        assert exc.value.status_code == 500

    def test_campaigns_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.campaigns.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "relay-rest.update_campaign"

    def test_campaigns_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.update_campaign", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.campaigns.update("test-id")
        assert exc.value.status_code == 500

    def test_numbers_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.numbers.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "relay-rest.delete_number_assignment"

    def test_numbers_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.delete_number_assignment", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.numbers.delete("test-id")
        assert exc.value.status_code == 500

    def test_orders_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.orders.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.retrieve_order"

    def test_orders_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.retrieve_order", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.orders.get("test-id")
        assert exc.value.status_code == 500
