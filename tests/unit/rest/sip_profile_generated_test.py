"""AUTO-GENERATED REST wire tests for the `sip_profile` namespace — DO NOT EDIT.
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


class TestSipProfileWire:
    def test_sip_profile_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.sip_profile.get()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.retrieve_sip_profile"

    def test_sip_profile_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.retrieve_sip_profile", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.sip_profile.get()
        assert exc.value.status_code == 500

    def test_sip_profile_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.sip_profile.update()
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "relay-rest.update_sip_profile"

    def test_sip_profile_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.update_sip_profile", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.sip_profile.update()
        assert exc.value.status_code == 500
