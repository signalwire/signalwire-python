"""Tests for phone_numbers namespace — CRUD, search, and typed binding helpers.

The typed helpers wrap ``phone_numbers.update`` with the correct
``call_handler`` + companion field combination for each handler type. A
regression test asserts the full happy-path binding flow does NOT require
pre-creating a Fabric webhook resource and does NOT call
``assign_phone_route`` — the two traps found in the phone-binding
post-mortem.
"""

import warnings

import pytest

from signalwire.rest import PhoneCallHandler

from .conftest import MockResponse


BASE = "https://test.signalwire.com/api/relay/rest/phone_numbers"


class TestPhoneNumbersCrud:
    def test_list(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.phone_numbers.list()
        mock_session.request.assert_called_with(
            "GET", BASE, json=None, params=None,
        )

    def test_search(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.phone_numbers.search(area_code="512")
        mock_session.request.assert_called_with(
            "GET", f"{BASE}/search", json=None, params={"area_code": "512"},
        )

    def test_update_uses_put(self, client, mock_session):
        """phone_numbers uses PUT for update (not PATCH)."""
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.update("pn-1", name="Main")
        mock_session.request.assert_called_with(
            "PUT", f"{BASE}/pn-1", json={"name": "Main"}, params=None,
        )


class TestPhoneCallHandlerEnum:
    def test_all_wire_values_present(self):
        """Every call_handler value accepted by the API is in the enum."""
        expected = {
            "relay_script", "laml_webhooks", "laml_application",
            "ai_agent", "call_flow", "relay_application",
            "relay_topic", "relay_context", "relay_connector",
            "video_room", "dialogflow",
        }
        assert {h.value for h in PhoneCallHandler} == expected

    def test_enum_members_are_strings(self):
        """Members are str subclasses so they serialize without .value."""
        assert PhoneCallHandler.RELAY_SCRIPT == "relay_script"
        assert f"{PhoneCallHandler.AI_AGENT}" == "PhoneCallHandler.AI_AGENT"

    def test_no_collision_with_relay_callhandler(self):
        """PhoneCallHandler is explicitly named to dodge the RELAY CallHandler type."""
        # Just assert the import path is the rest module; RELAY has its own
        # callback types elsewhere and won't reuse this symbol.
        from signalwire.rest.call_handler import PhoneCallHandler as ReimportedHandler
        assert ReimportedHandler is PhoneCallHandler


class TestSetSwmlWebhook:
    def test_happy_path(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_swml_webhook(
            "pn-1", url="https://example.com/swml",
        )
        mock_session.request.assert_called_with(
            "PUT", f"{BASE}/pn-1",
            json={
                "call_handler": "relay_script",
                "call_relay_script_url": "https://example.com/swml",
            },
            params=None,
        )

    def test_extra_kwargs_pass_through(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_swml_webhook(
            "pn-1", url="https://example.com/swml", name="Support Line",
        )
        body = mock_session.request.call_args.kwargs["json"]
        assert body["name"] == "Support Line"
        assert body["call_handler"] == "relay_script"
        assert body["call_relay_script_url"] == "https://example.com/swml"


class TestSetCxmlWebhook:
    def test_minimal(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_cxml_webhook(
            "pn-1", url="https://example.com/voice.xml",
        )
        mock_session.request.assert_called_with(
            "PUT", f"{BASE}/pn-1",
            json={
                "call_handler": "laml_webhooks",
                "call_request_url": "https://example.com/voice.xml",
            },
            params=None,
        )

    def test_with_fallback_and_status(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_cxml_webhook(
            "pn-1",
            url="https://example.com/voice.xml",
            fallback_url="https://example.com/fallback.xml",
            status_callback_url="https://example.com/status",
        )
        body = mock_session.request.call_args.kwargs["json"]
        assert body == {
            "call_handler": "laml_webhooks",
            "call_request_url": "https://example.com/voice.xml",
            "call_fallback_url": "https://example.com/fallback.xml",
            "call_status_callback_url": "https://example.com/status",
        }


class TestSetCxmlApplication:
    def test_happy_path(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_cxml_application("pn-1", application_id="app-1")
        body = mock_session.request.call_args.kwargs["json"]
        assert body == {
            "call_handler": "laml_application",
            "call_laml_application_id": "app-1",
        }


class TestSetAiAgent:
    def test_happy_path(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_ai_agent("pn-1", agent_id="agent-1")
        body = mock_session.request.call_args.kwargs["json"]
        assert body == {
            "call_handler": "ai_agent",
            "call_ai_agent_id": "agent-1",
        }


class TestSetCallFlow:
    def test_minimal(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_call_flow("pn-1", flow_id="cf-1")
        body = mock_session.request.call_args.kwargs["json"]
        assert body == {
            "call_handler": "call_flow",
            "call_flow_id": "cf-1",
        }

    def test_with_version(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_call_flow(
            "pn-1", flow_id="cf-1", version="current_deployed",
        )
        body = mock_session.request.call_args.kwargs["json"]
        assert body == {
            "call_handler": "call_flow",
            "call_flow_id": "cf-1",
            "call_flow_version": "current_deployed",
        }


class TestSetRelayApplication:
    def test_happy_path(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_relay_application("pn-1", name="my-app")
        body = mock_session.request.call_args.kwargs["json"]
        assert body == {
            "call_handler": "relay_application",
            "call_relay_application": "my-app",
        }


class TestSetRelayTopic:
    def test_minimal(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_relay_topic("pn-1", topic="office")
        body = mock_session.request.call_args.kwargs["json"]
        assert body == {
            "call_handler": "relay_topic",
            "call_relay_topic": "office",
        }

    def test_with_status_callback(self, client, mock_session):
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_relay_topic(
            "pn-1", topic="office",
            status_callback_url="https://example.com/status",
        )
        body = mock_session.request.call_args.kwargs["json"]
        assert body == {
            "call_handler": "relay_topic",
            "call_relay_topic": "office",
            "call_relay_topic_status_callback_url": "https://example.com/status",
        }


class TestBindingRegressionPostMortem:
    """Guards against the phone-binding post-mortem anti-patterns.

    The post-mortem identified two traps:
      1. ``fabric.swml_webhooks.create(...)`` looks right but produces orphans
      2. ``fabric.resources.assign_phone_route(...)`` rejects swml_webhook bindings

    The correct happy-path binding is entirely through ``phone_numbers.update``
    (directly or via the typed helpers). This test pins that contract.
    """

    def test_swml_binding_uses_only_phone_numbers_update(self, client, mock_session):
        """The full happy path is a single PUT to /api/relay/rest/phone_numbers/{sid}."""
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.set_swml_webhook(
            "pn-1", url="https://example.com/swml",
        )

        calls = mock_session.request.call_args_list
        # Exactly one HTTP call
        assert len(calls) == 1
        method, url = calls[0].args[0], calls[0].args[1]
        # PUT on phone_numbers
        assert method == "PUT"
        assert url == f"{BASE}/pn-1"
        # No fabric.swml_webhooks.create (that URL would be
        # /api/fabric/resources/swml_webhooks)
        assert "/api/fabric/resources/swml_webhooks" not in url
        # No assign_phone_route (that URL would be
        # /api/fabric/resources/.../phone_routes)
        assert "/phone_routes" not in url

    def test_wire_level_form_works_without_enum(self, client, mock_session):
        """Passing the raw string value also works — for users who don't import the enum."""
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.update(
            "pn-1",
            call_handler="relay_script",
            call_relay_script_url="https://example.com/swml",
        )
        body = mock_session.request.call_args.kwargs["json"]
        assert body["call_handler"] == "relay_script"
        assert body["call_relay_script_url"] == "https://example.com/swml"

    def test_enum_value_is_accepted_by_update(self, client, mock_session):
        """Passing PhoneCallHandler.RELAY_SCRIPT.value serializes identically."""
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.update(
            "pn-1",
            call_handler=PhoneCallHandler.RELAY_SCRIPT.value,
            call_relay_script_url="https://example.com/swml",
        )
        body = mock_session.request.call_args.kwargs["json"]
        assert body["call_handler"] == "relay_script"


class TestHelperCoverage:
    """Every PhoneCallHandler member that maps to a helper has one."""

    def test_all_helpers_present(self, client):
        expected = {
            "set_swml_webhook",
            "set_cxml_webhook",
            "set_cxml_application",
            "set_ai_agent",
            "set_call_flow",
            "set_relay_application",
            "set_relay_topic",
        }
        for name in expected:
            assert hasattr(client.phone_numbers, name), (
                f"phone_numbers missing binding helper: {name}"
            )
