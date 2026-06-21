"""Full success + error coverage for ``client.registry`` (relay-rest 10DLC).

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template.  The 10DLC
Campaign Registry lives under ``/api/relay/rest/registry/beta`` and is split
across four sub-resources: ``brands``, ``campaigns``, ``orders``, ``numbers``.

The existing ``test_registry_mock.py`` covers the happy path only; this file
adds the matched-route + error-case coverage the full-coverage bar requires.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

_BASE = "/api/relay/rest/registry/beta"


class TestRelayRegistryBrandsSuccess:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.registry.brands.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/brands"
        assert last.matched_route == "relay-rest.list_brands"

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.registry.brands.create(entity_type="PRIVATE_PROFIT")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{_BASE}/brands"
        assert last.matched_route == "relay-rest.create_brand"
        assert last.body and last.body.get("entity_type") == "PRIVATE_PROFIT"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.registry.brands.get("brand-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/brands/brand-1"
        assert last.matched_route == "relay-rest.retrieve_brand"

    def test_list_campaigns(self, signalwire_client, mock):
        body = signalwire_client.registry.brands.list_campaigns("brand-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/brands/brand-1/campaigns"
        assert last.matched_route == "relay-rest.list_campaigns"

    def test_create_campaign(self, signalwire_client, mock):
        body = signalwire_client.registry.brands.create_campaign(
            "brand-1", usecase="LOW_VOLUME"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{_BASE}/brands/brand-1/campaigns"
        assert last.matched_route == "relay-rest.create_campaign"
        assert last.body and last.body.get("usecase") == "LOW_VOLUME"


class TestRelayRegistryBrandsErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.list_brands", 500, {"error": "boom"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.brands.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_brands"
        assert last.response_status == 500

    def test_create_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.create_brand", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.brands.create()
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.create_brand"
        assert last.response_status == 422

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.retrieve_brand", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.brands.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.retrieve_brand"
        assert last.response_status == 404

    def test_list_campaigns_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.list_campaigns", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.brands.list_campaigns("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_campaigns"
        assert last.response_status == 404

    def test_create_campaign_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.create_campaign", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.brands.create_campaign("brand-1")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.create_campaign"
        assert last.response_status == 422


class TestRelayRegistryCampaignsSuccess:
    def test_get(self, signalwire_client, mock):
        body = signalwire_client.registry.campaigns.get("camp-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/campaigns/camp-1"
        assert last.matched_route == "relay-rest.retrieve_campaign"

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.registry.campaigns.update("camp-1", description="x")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == f"{_BASE}/campaigns/camp-1"
        assert last.matched_route == "relay-rest.update_campaign"
        assert last.body and last.body.get("description") == "x"

    def test_list_numbers(self, signalwire_client, mock):
        body = signalwire_client.registry.campaigns.list_numbers("camp-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/campaigns/camp-1/numbers"
        assert last.matched_route == "relay-rest.list_number_assignments"

    def test_list_orders(self, signalwire_client, mock):
        body = signalwire_client.registry.campaigns.list_orders("camp-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/campaigns/camp-1/orders"
        assert last.matched_route == "relay-rest.list_orders"

    def test_create_order(self, signalwire_client, mock):
        body = signalwire_client.registry.campaigns.create_order(
            "camp-1", numbers=["pn-1"]
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{_BASE}/campaigns/camp-1/orders"
        assert last.matched_route == "relay-rest.create_order"
        assert last.body and last.body.get("numbers") == ["pn-1"]


class TestRelayRegistryCampaignsErrors:
    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.retrieve_campaign", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.campaigns.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.retrieve_campaign"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.update_campaign", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.campaigns.update("missing", description="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.update_campaign"
        assert last.response_status == 404

    def test_list_numbers_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.list_number_assignments", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.campaigns.list_numbers("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_number_assignments"
        assert last.response_status == 404

    def test_list_orders_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.list_orders", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.campaigns.list_orders("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_orders"
        assert last.response_status == 404

    def test_create_order_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.create_order", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.campaigns.create_order("camp-1")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.create_order"
        assert last.response_status == 422


class TestRelayRegistryOrdersSuccess:
    def test_get(self, signalwire_client, mock):
        body = signalwire_client.registry.orders.get("order-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/orders/order-1"
        assert last.matched_route == "relay-rest.retrieve_order"


class TestRelayRegistryOrdersErrors:
    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.retrieve_order", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.orders.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.retrieve_order"
        assert last.response_status == 404


class TestRelayRegistryNumbersSuccess:
    def test_delete(self, signalwire_client, mock):
        signalwire_client.registry.numbers.delete("num-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{_BASE}/numbers/num-1"
        assert last.matched_route == "relay-rest.delete_number_assignment"


class TestRelayRegistryNumbersErrors:
    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.delete_number_assignment", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.registry.numbers.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.delete_number_assignment"
        assert last.response_status == 404
