"""Fabric namespace coverage against the in-process ``mock_signalwire`` server.

Closes the audit gaps that the legacy ``test_fabric.py`` (which patches
``requests.Session``) leaves open: addresses, generic resources operations,
SIP-endpoint sub-resources on subscribers, the call-flows / conference-rooms
addresses sub-paths, the full ``FabricTokens`` surface, and the
``CxmlApplicationsResource.create`` deliberate-failure path.

Each test:

1. Calls the SDK against a live HTTP mock backed by the OpenAPI specs.
2. Asserts on the parsed body shape so the synthesised response shape is
   what the SDK actually consumes.
3. Asserts on the ``mock`` request journal (method + path + body) so the
   on-the-wire URL the SDK built is exactly what the spec advertises.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Fabric Addresses (read-only top-level resource)
# ---------------------------------------------------------------------------


class TestFabricAddresses:
    """``client.fabric.addresses.*`` — list and get only."""

    def test_list_returns_data_collection(self, signalwire_client, mock):
        body = signalwire_client.fabric.addresses.list()
        assert isinstance(body, dict), f"expected dict, got {type(body).__name__}"
        # Fabric addresses list returns 'data' arrays.
        assert "data" in body, f"missing 'data' in body keys {sorted(body)!r}"
        assert isinstance(body["data"], list)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/addresses"
        assert last.matched_route == "fabric.list_fabric_addresses", (
            f"expected fabric.list_fabric_addresses, got {last.matched_route!r}"
        )

    def test_get_uses_address_id(self, signalwire_client, mock):
        body = signalwire_client.fabric.addresses.get("addr-9001")
        assert isinstance(body, dict)
        # The retrieve endpoint synthesises a single address resource.

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/addresses/addr-9001"
        assert last.matched_route is not None, "spec gap: address get"


# ---------------------------------------------------------------------------
# CxmlApplicationsResource.create — deliberate NotImplementedError
# ---------------------------------------------------------------------------


class TestCxmlApplicationsCreate:
    """``cxml_applications`` is read-only by design.

    The SDK raises ``NotImplementedError`` rather than POSTing because the API
    has no create endpoint for cXML applications (verify in
    porting-sdk/rest-apis/fabric: only PUT/GET/DELETE on
    ``/api/fabric/resources/cxml_applications/{id}``).
    """

    def test_create_raises_not_implemented(self, signalwire_client, mock):
        with pytest.raises(NotImplementedError, match="cXML applications cannot"):
            signalwire_client.fabric.cxml_applications.create(name="never_built")
        # Nothing should have hit the wire.
        assert mock.journal == [], (
            f"expected no journal entries, got {mock.journal}"
        )


# ---------------------------------------------------------------------------
# CallFlowsResource.list_addresses — singular 'call_flow' subpath
# ---------------------------------------------------------------------------


class TestCallFlowsAddresses:
    """``call_flows.list_addresses`` walks a different (singular) URL.

    The SDK rewrites ``/call_flows`` to ``/call_flow`` for sub-collection
    paths because that's what the API spec uses.
    """

    def test_list_addresses_uses_singular_path(self, signalwire_client, mock):
        body = signalwire_client.fabric.call_flows.list_addresses("cf-1")
        assert isinstance(body, dict)
        assert "data" in body and isinstance(body["data"], list)

        last = mock.last_request()
        assert last.method == "GET"
        # singular 'call_flow' (NOT 'call_flows') in the addresses sub-path.
        assert last.path == "/api/fabric/resources/call_flow/cf-1/addresses"
        assert last.matched_route is not None, (
            "spec gap: call-flow addresses sub-path"
        )


# ---------------------------------------------------------------------------
# ConferenceRoomsResource.list_addresses — singular 'conference_room' subpath
# ---------------------------------------------------------------------------


class TestConferenceRoomsAddresses:
    """``conference_rooms.list_addresses`` rewrites ``/conference_rooms``
    to ``/conference_room`` for sub-collections, mirroring call_flows."""

    def test_list_addresses_uses_singular_path(self, signalwire_client, mock):
        body = signalwire_client.fabric.conference_rooms.list_addresses("cr-1")
        assert isinstance(body, dict)
        assert "data" in body

        last = mock.last_request()
        assert last.method == "GET"
        # singular 'conference_room'.
        assert last.path == "/api/fabric/resources/conference_room/cr-1/addresses"
        assert last.matched_route is not None


# ---------------------------------------------------------------------------
# Subscribers — SIP endpoint per-id ops (get / update / delete)
# ---------------------------------------------------------------------------


class TestSubscribersSipEndpointOps:
    """``subscribers.{get,update,delete}_sip_endpoint(sub_id, ep_id)``."""

    def test_get_sip_endpoint(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.get_sip_endpoint(
            "sub-1", "ep-1"
        )
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == (
            "/api/fabric/resources/subscribers/sub-1/sip_endpoints/ep-1"
        )
        assert last.matched_route is not None

    def test_update_sip_endpoint_uses_patch(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.update_sip_endpoint(
            "sub-1", "ep-1", username="renamed"
        )
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.path == (
            "/api/fabric/resources/subscribers/sub-1/sip_endpoints/ep-1"
        )
        assert isinstance(last.body, dict)
        assert last.body.get("username") == "renamed"

    def test_delete_sip_endpoint(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.delete_sip_endpoint(
            "sub-1", "ep-1"
        )
        assert isinstance(body, dict)  # SDK normalises 204 to {}

        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == (
            "/api/fabric/resources/subscribers/sub-1/sip_endpoints/ep-1"
        )
        assert last.matched_route is not None


# ---------------------------------------------------------------------------
# FabricTokens — every token-creation endpoint
# ---------------------------------------------------------------------------


class TestFabricTokens:
    """The remaining token endpoints not covered by the legacy test_fabric.py:

    - ``create_invite_token`` -> POST /api/fabric/subscriber/invites
    - ``create_embed_token``  -> POST /api/fabric/embeds/tokens
    - ``refresh_subscriber_token`` -> POST /api/fabric/subscribers/tokens/refresh
    """

    def test_create_invite_token(self, signalwire_client, mock):
        body = signalwire_client.fabric.tokens.create_invite_token(
            email="invitee@example.com"
        )
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "POST"
        # subscriber/invites uses the singular 'subscriber' path segment.
        assert last.path == "/api/fabric/subscriber/invites"
        assert isinstance(last.body, dict)
        assert last.body.get("email") == "invitee@example.com"

    def test_create_embed_token(self, signalwire_client, mock):
        body = signalwire_client.fabric.tokens.create_embed_token(
            allowed_addresses=["addr-1", "addr-2"]
        )
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/embeds/tokens"
        assert isinstance(last.body, dict)
        assert last.body.get("allowed_addresses") == ["addr-1", "addr-2"]

    def test_refresh_subscriber_token(self, signalwire_client, mock):
        body = signalwire_client.fabric.tokens.refresh_subscriber_token(
            refresh_token="abc-123"
        )
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/subscribers/tokens/refresh"
        assert isinstance(last.body, dict)
        assert last.body.get("refresh_token") == "abc-123"


# ---------------------------------------------------------------------------
# GenericResources — generic /api/fabric/resources operations
# ---------------------------------------------------------------------------


class TestGenericResources:
    """``client.fabric.resources.*`` — list/get/delete/list_addresses across
    every resource type, plus assign_domain_application."""

    def test_list_returns_data_collection(self, signalwire_client, mock):
        body = signalwire_client.fabric.resources.list()
        assert isinstance(body, dict)
        # /api/fabric/resources returns data array.
        assert "data" in body and isinstance(body["data"], list)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/resources"
        assert last.matched_route is not None

    def test_get_returns_single_resource(self, signalwire_client, mock):
        body = signalwire_client.fabric.resources.get("res-1")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/resources/res-1"

    def test_delete(self, signalwire_client, mock):
        body = signalwire_client.fabric.resources.delete("res-2")
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/fabric/resources/res-2"
        assert last.matched_route is not None

    def test_list_addresses(self, signalwire_client, mock):
        body = signalwire_client.fabric.resources.list_addresses("res-3")
        assert isinstance(body, dict)
        assert "data" in body and isinstance(body["data"], list)

        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/resources/res-3/addresses"

    def test_assign_domain_application(self, signalwire_client, mock):
        body = signalwire_client.fabric.resources.assign_domain_application(
            "res-4", domain_application_id="da-7"
        )
        assert isinstance(body, dict)

        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/resources/res-4/domain_applications"
        assert isinstance(last.body, dict)
        assert last.body.get("domain_application_id") == "da-7"
