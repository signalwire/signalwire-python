"""AUTO-GENERATED REST wire tests for the `phone_numbers` namespace — DO NOT EDIT.
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


class TestPhoneNumbersWire:
    def test_phone_numbers_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.phone_numbers.create(number="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "relay-rest.purchase_phone_number"

    def test_phone_numbers_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.purchase_phone_number", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.create(number="x")
        assert exc.value.status_code == 500

    def test_phone_numbers_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.phone_numbers.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "relay-rest.release_phone_number"

    def test_phone_numbers_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.release_phone_number", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.delete("test-id")
        assert exc.value.status_code == 500

    def test_phone_numbers_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.phone_numbers.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.retrieve_phone_number"

    def test_phone_numbers_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.retrieve_phone_number", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.get("test-id")
        assert exc.value.status_code == 500

    def test_phone_numbers_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.phone_numbers.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_phone_numbers"

    def test_phone_numbers_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.list_phone_numbers", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.list()
        assert exc.value.status_code == 500

    def test_phone_numbers_search(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.phone_numbers.search()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.search_available_phone_numbers"

    def test_phone_numbers_search_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "relay-rest.search_available_phone_numbers", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.search()
        assert exc.value.status_code == 500

    def test_phone_numbers_set_ai_agent(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.phone_numbers.set_ai_agent("test-id", "test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "relay-rest.update_phone_number"

    def test_phone_numbers_set_ai_agent_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.update_phone_number", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.phone_numbers.set_ai_agent("test-id", "test-id")
        assert exc.value.status_code == 500
