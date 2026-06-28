"""Registry namespace coverage against the in-process ``mock_signalwire`` server.

The 10DLC Campaign Registry namespace exposes four sub-resources:
``brands``, ``campaigns``, ``orders``, and ``numbers``.  The legacy tests
only touched ``brands.create`` and ``campaigns.list_orders``; this module
closes the rest.

Each test:
1. Calls the SDK against the live mock server.
2. Asserts on the parsed response body shape.
3. Asserts on the journal: HTTP method + path the SDK actually hit.

All registry endpoints sit under ``/api/relay/rest/registry/beta``.
"""

from __future__ import annotations


_REG_BASE = "/api/relay/rest/registry/beta"


# ---------------------------------------------------------------------------
# Brands
# ---------------------------------------------------------------------------


class TestRegistryBrands:
    """``client.registry.brands.*`` — list, get, list_campaigns, create_campaign."""

    def test_list_returns_dict(self, signalwire_client, mock):
        body = signalwire_client.registry.brands.list()
        assert isinstance(body, dict), f"expected dict, got {type(body).__name__}"

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_REG_BASE}/brands"
        assert last.matched_route is not None, "spec gap: brand list"

    def test_get_uses_id_in_path(self, signalwire_client, mock):
        body = signalwire_client.registry.brands.get("brand-77")
        assert isinstance(body, dict)
        # Single-brand endpoint synthesises one resource object.

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_REG_BASE}/brands/brand-77"

    def test_list_campaigns_uses_brand_subpath(self, signalwire_client, mock):
        body = signalwire_client.registry.brands.list_campaigns("brand-1")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_REG_BASE}/brands/brand-1/campaigns"
        assert last.matched_route is not None

    def test_create_campaign_posts_to_brand_subpath(self, signalwire_client, mock):
        # create_campaign takes the full CreateManagedCampaignRequest body; the
        # managed-campaign schema requires every field below.
        body = signalwire_client.registry.brands.create_campaign(
            "brand-2",
            {
                "name": "My Campaign",
                "brand_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "sms_use_case": "MARKETING",
                "description": "This campaign sends appointment reminders to opted-in patients.",
                "sample1": "Hi John, your appointment is tomorrow. Reply STOP to unsubscribe.",
                "sample2": "Your prescription is ready for pickup. Reply STOP to unsubscribe.",
                "message_flow": "Users opt in via a written form and receive an opt-in message.",
                "opt_out_message": "You have successfully been opted out. Reply START to opt back in.",
                "help_message": "For help contact support@example.com. Reply STOP to unsubscribe.",
                "number_pooling_required": False,
                "direct_lending": False,
                "embedded_link": False,
                "embedded_phone": False,
                "age_gated_content": False,
                "lead_generation": False,
                "terms_and_conditions": True,
            },
        )
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{_REG_BASE}/brands/brand-2/campaigns"
        assert isinstance(last.body, dict)
        assert last.body.get("sms_use_case") == "MARKETING"
        assert last.body.get("name") == "My Campaign"


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------


class TestRegistryCampaigns:
    """``client.registry.campaigns.*`` — get, update (PUT), list_numbers, create_order."""

    def test_get_uses_id_in_path(self, signalwire_client, mock):
        body = signalwire_client.registry.campaigns.get("camp-1")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_REG_BASE}/campaigns/camp-1"

    def test_update_uses_put(self, signalwire_client, mock):
        # RegistryCampaigns.update calls self._http.put(...) — distinct from
        # the generic CrudResource which uses PATCH.
        # UpdateCampaignRequest exposes only ``name``.
        body = signalwire_client.registry.campaigns.update(
            "camp-2", name="Updated Campaign"
        )
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == f"{_REG_BASE}/campaigns/camp-2"
        assert isinstance(last.body, dict)
        assert last.body.get("name") == "Updated Campaign"

    def test_list_numbers_uses_numbers_subpath(self, signalwire_client, mock):
        body = signalwire_client.registry.campaigns.list_numbers("camp-3")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_REG_BASE}/campaigns/camp-3/numbers"
        assert last.matched_route is not None

    def test_create_order_posts_to_orders_subpath(self, signalwire_client, mock):
        body = signalwire_client.registry.campaigns.create_order(
            "camp-4", phone_numbers=["+15558675309", "+15558675310"]
        )
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{_REG_BASE}/campaigns/camp-4/orders"
        assert isinstance(last.body, dict)
        assert last.body.get("phone_numbers") == ["+15558675309", "+15558675310"]


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------


class TestRegistryOrders:
    """``client.registry.orders.get`` — read-only, retrieve by id."""

    def test_get_uses_id_in_path(self, signalwire_client, mock):
        body = signalwire_client.registry.orders.get("order-1")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_REG_BASE}/orders/order-1"
        assert last.matched_route is not None, "spec gap: order retrieve"


# ---------------------------------------------------------------------------
# Numbers (10DLC assigned phone numbers)
# ---------------------------------------------------------------------------


class TestRegistryNumbers:
    """``client.registry.numbers.delete`` — release a number."""

    def test_delete_uses_id_in_path(self, signalwire_client, mock):
        body = signalwire_client.registry.numbers.delete("num-1")
        # SDK turns 204/empty into {} so we still get a dict back.
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{_REG_BASE}/numbers/num-1"
        assert last.matched_route is not None
