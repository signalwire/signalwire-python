"""AUTO-GENERATED REST wire tests for the `short_codes` namespace — DO NOT EDIT.
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


class TestShortCodesWire:
    def test_short_codes_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.short_codes.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.retrieve_short_code"

    def test_short_codes_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.retrieve_short_code", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.short_codes.get("test-id")
        assert exc.value.status_code == 500

    def test_short_codes_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.short_codes.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_short_codes"

    def test_short_codes_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.list_short_codes", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.short_codes.list()
        assert exc.value.status_code == 500

    def test_short_codes_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.short_codes.update("test-id", name="x", message_handler="x")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "relay-rest.update_short_code"

    def test_short_codes_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.update_short_code", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.short_codes.update(
                "test-id", name="x", message_handler="x"
            )
        assert exc.value.status_code == 500
