"""AUTO-GENERATED REST wire tests for the `verified_callers` namespace — DO NOT EDIT.
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


class TestVerifiedCallersWire:
    def test_verified_callers_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.verified_callers.create(number="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "relay-rest.create_verified_caller_id"

    def test_verified_callers_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.create_verified_caller_id", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.create(number="x")
        assert exc.value.status_code == 500

    def test_verified_callers_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.verified_callers.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "relay-rest.delete_verified_caller_id"

    def test_verified_callers_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.delete_verified_caller_id", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.delete("test-id")
        assert exc.value.status_code == 500

    def test_verified_callers_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.verified_callers.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.retrieve_verified_caller_id"

    def test_verified_callers_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "relay-rest.retrieve_verified_caller_id", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.get("test-id")
        assert exc.value.status_code == 500

    def test_verified_callers_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.verified_callers.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_verified_caller_ids"

    def test_verified_callers_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.list_verified_caller_ids", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.list()
        assert exc.value.status_code == 500

    def test_verified_callers_redial_verification(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.verified_callers.redial_verification("test-id")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "relay-rest.redial_verification_call"

    def test_verified_callers_redial_verification_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.redial_verification_call", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.redial_verification("test-id")
        assert exc.value.status_code == 500

    def test_verified_callers_submit_verification(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.verified_callers.submit_verification(
            "test-id", verification_code="x"
        )
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "relay-rest.validate_verification_code"

    def test_verified_callers_submit_verification_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.validate_verification_code", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.submit_verification(
                "test-id", verification_code="x"
            )
        assert exc.value.status_code == 500

    def test_verified_callers_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.verified_callers.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "relay-rest.update_verified_caller_id"

    def test_verified_callers_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.update_verified_caller_id", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.update("test-id")
        assert exc.value.status_code == 500
