"""AUTO-GENERATED REST wire tests for the `whatsapp` namespace — DO NOT EDIT.
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


class TestWhatsappWire:
    def test_businesses_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.whatsapp.businesses.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "message.list_whatsapp_businesses"

    def test_businesses_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("message.list_whatsapp_businesses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.whatsapp.businesses.list()
        assert exc.value.status_code == 500

    def test_numbers_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.whatsapp.numbers.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "message.retrieve_whatsapp_number"

    def test_numbers_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("message.retrieve_whatsapp_number", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.whatsapp.numbers.get("test-id")
        assert exc.value.status_code == 500

    def test_numbers_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.whatsapp.numbers.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "message.list_whatsapp_numbers"

    def test_numbers_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("message.list_whatsapp_numbers", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.whatsapp.numbers.list()
        assert exc.value.status_code == 500

    def test_templates_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.whatsapp.templates.create(
            whatsapp_business_id="x",
            name="x",
            language="x",
            category="utility",
            parameter_format="named",
            components=[{}],
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "message.create_whatsapp_template"

    def test_templates_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("message.create_whatsapp_template", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.whatsapp.templates.create(
                whatsapp_business_id="x",
                name="x",
                language="x",
                category="utility",
                parameter_format="named",
                components=[{}],
            )
        assert exc.value.status_code == 500

    def test_templates_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.whatsapp.templates.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "message.delete_whatsapp_template"

    def test_templates_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("message.delete_whatsapp_template", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.whatsapp.templates.delete("test-id")
        assert exc.value.status_code == 500

    def test_templates_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.whatsapp.templates.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "message.retrieve_whatsapp_template"

    def test_templates_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("message.retrieve_whatsapp_template", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.whatsapp.templates.get("test-id")
        assert exc.value.status_code == 500

    def test_templates_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.whatsapp.templates.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "message.list_whatsapp_templates"

    def test_templates_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("message.list_whatsapp_templates", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.whatsapp.templates.list()
        assert exc.value.status_code == 500

    def test_templates_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.whatsapp.templates.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "message.update_whatsapp_template"

    def test_templates_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("message.update_whatsapp_template", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.whatsapp.templates.update("test-id")
        assert exc.value.status_code == 500
