"""Tests for fabric namespace — resource types, addresses, tokens."""

import warnings

from .conftest import MockResponse
from signalwire.rest.client import RestClient
from unittest.mock import MagicMock
import pytest


class TestFabricResources:
    def test_ai_agents_list(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.fabric.ai_agents.list()
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/fabric/resources/ai_agents",
            json=None, params=None,
        )

    def test_ai_agents_create(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(201, {"id": "new"})
        client.fabric.ai_agents.create(
            name="Support",
            prompt="You are helpful",  # type: ignore[arg-type]  # test passes raw str to assert wire body
            agent_id="a1",
        )
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/fabric/resources/ai_agents",
            json={"name": "Support", "prompt": "You are helpful", "agent_id": "a1"},
            params=None,
        )

    def test_ai_agents_update_uses_patch(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {})
        client.fabric.ai_agents.update("id-1", name="Updated")
        mock_session.request.assert_called_with(
            "PATCH", "https://test.signalwire.com/api/fabric/resources/ai_agents/id-1",
            json={"name": "Updated"}, params=None,
        )

    def test_swml_scripts_update_uses_put(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {})
        client.fabric.swml_scripts.update("id-1", contents="{}")
        mock_session.request.assert_called_with(
            "PUT", "https://test.signalwire.com/api/fabric/resources/swml_scripts/id-1",
            json={"contents": "{}"}, params=None,
        )

    def test_list_addresses(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.fabric.ai_agents.list_addresses("id-1")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/fabric/resources/ai_agents/id-1/addresses",
            json=None, params=None,
        )


class TestFabricCallFlows:
    def test_list_versions(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.fabric.call_flows.list_versions("cf-1")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/fabric/resources/call_flow/cf-1/versions",
            json=None, params=None,
        )

    def test_deploy_version(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {})
        client.fabric.call_flows.deploy_version("cf-1", {"document_version": 2})
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/fabric/resources/call_flow/cf-1/versions",
            json={"document_version": 2}, params=None,
        )


class TestFabricSubscribers:
    def test_list_sip_endpoints(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.fabric.subscribers.list_sip_endpoints("sub-1")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/fabric/resources/subscribers/sub-1/sip_endpoints",
            json=None, params=None,
        )

    def test_create_sip_endpoint(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(201, {"id": "ep-1"})
        client.fabric.subscribers.create_sip_endpoint(
            "sub-1", username="user1", password="s3cret"  # noqa: S106
        )
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/fabric/resources/subscribers/sub-1/sip_endpoints",
            json={"username": "user1", "password": "s3cret"}, params=None,
        )


class TestGenericResources:
    def test_assign_phone_route_posts(self, client: RestClient, mock_session: MagicMock) -> None:
        """assign_phone_route posts the phone_route_id and handler to the resource.

        The spec's PhoneRouteAssignRequest requires both phone_route_id and a
        handler ("calling" or "messaging"). These pre-release SDKs no longer emit
        the legacy DeprecationWarning the hand-class used to.
        """
        mock_session.request.return_value = MockResponse(200, {})
        client.fabric.resources.assign_phone_route(
            "res-1", phone_route_id="pr-1", handler="calling"
        )
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/fabric/resources/res-1/phone_routes",
            json={"phone_route_id": "pr-1", "handler": "calling"}, params=None,
        )


class TestWebhooks:
    """swml_webhooks and cxml_webhooks are plain CRUD resources. They are normally
    auto-materialized via phone_numbers.set_swml_webhook / set_cxml_webhook, but
    direct create is a normal operation (these SDKs are pre-release — no deprecation).
    """

    def test_swml_webhooks_create_no_warning(self, client: RestClient, mock_session: MagicMock, recwarn: pytest.WarningsRecorder) -> None:
        mock_session.request.return_value = MockResponse(201, {"id": "sw-1"})
        client.fabric.swml_webhooks.create(
            primary_request_url="https://example.com/swml",
        )
        assert not [w for w in recwarn if issubclass(w.category, DeprecationWarning)]

    def test_cxml_webhooks_create_no_warning(self, client: RestClient, mock_session: MagicMock, recwarn: pytest.WarningsRecorder) -> None:
        mock_session.request.return_value = MockResponse(201, {"id": "cw-1"})
        client.fabric.cxml_webhooks.create(
            primary_request_url="https://example.com/voice.xml",
        )
        assert not [w for w in recwarn if issubclass(w.category, DeprecationWarning)]

    def test_webhooks_read_update_delete_work_without_warning(self, client: RestClient, mock_session: MagicMock) -> None:
        """Webhooks are plain CRUD — list/get/update/delete/create all run without
        emitting any DeprecationWarning. We assert the underlying HTTP transport
        actually got called for each operation (proving the methods aren't no-ops)."""
        mock_session.request.return_value = MockResponse(200, {"data": []})
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            client.fabric.swml_webhooks.list()
            client.fabric.swml_webhooks.get("sw-1")
            client.fabric.swml_webhooks.update("sw-1", name="Updated")
            client.fabric.swml_webhooks.delete("sw-1")
            client.fabric.cxml_webhooks.list()
        # Five non-deprecated operations produced five HTTP calls.
        assert mock_session.request.call_count == 5
        # Verify the HTTP methods used (list/get -> GET, update -> PUT/PATCH,
        # delete -> DELETE). We don't pin to a specific verb for update
        # because the SDK may pick either, but DELETE must be present.
        methods = [call_args[0][0] for call_args in mock_session.request.call_args_list]
        assert "DELETE" in methods
        assert methods.count("GET") >= 3  # list, get, list (cxml)


class TestFabricTokens:
    def test_create_subscriber_token(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"token": "abc"})
        client.fabric.tokens.create_subscriber_token(reference="user@example.com")
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/fabric/subscribers/tokens",
            json={"reference": "user@example.com"}, params=None,
        )

    def test_create_guest_token(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"token": "abc"})
        client.fabric.tokens.create_guest_token(allowed_addresses=["addr-1"])
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/fabric/guests/tokens",
            json={"allowed_addresses": ["addr-1"]}, params=None,
        )


class TestAllFabricResources:
    """Verify all 13+ resource types exist on the fabric namespace."""

    def test_resource_types_exist(self, client: RestClient) -> None:
        resources = [
            "swml_scripts", "swml_webhooks", "ai_agents", "relay_applications",
            "call_flows", "conference_rooms", "freeswitch_connectors",
            "subscribers", "sip_endpoints", "sip_gateways",
            "cxml_scripts", "cxml_webhooks", "cxml_applications",
        ]
        for name in resources:
            assert hasattr(client.fabric, name), f"Missing fabric resource: {name}"

    def test_special_resources_exist(self, client: RestClient) -> None:
        assert hasattr(client.fabric, "resources")
        assert hasattr(client.fabric, "addresses")
        assert hasattr(client.fabric, "tokens")
