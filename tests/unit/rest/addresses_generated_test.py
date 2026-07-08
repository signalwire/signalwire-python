"""AUTO-GENERATED REST wire tests for the `addresses` namespace — DO NOT EDIT.
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


class TestAddressesWire:
    def test_addresses_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.addresses.create(
            label="x",
            country="x",
            first_name="x",
            last_name="x",
            street_number="x",
            street_name="x",
            city="x",
            state="x",
            postal_code="x",
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "relay-rest.create_address"

    def test_addresses_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.create_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.addresses.create(
                label="x",
                country="x",
                first_name="x",
                last_name="x",
                street_number="x",
                street_name="x",
                city="x",
                state="x",
                postal_code="x",
            )
        assert exc.value.status_code == 500

    def test_addresses_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.addresses.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "relay-rest.delete_address"

    def test_addresses_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.delete_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.addresses.delete("test-id")
        assert exc.value.status_code == 500

    def test_addresses_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.addresses.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.get_address"

    def test_addresses_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.get_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.addresses.get("test-id")
        assert exc.value.status_code == 500

    def test_addresses_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.addresses.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_addresses"

    def test_addresses_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.list_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.addresses.list()
        assert exc.value.status_code == 500
