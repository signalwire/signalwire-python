"""AUTO-GENERATED REST wire tests for the `number_groups` namespace — DO NOT EDIT.
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


class TestNumberGroupsWire:
    def test_number_groups_add_membership(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.number_groups.add_membership("test-id", phone_number_id="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "relay-rest.create_number_group_membership"

    def test_number_groups_add_membership_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "relay-rest.create_number_group_membership", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.add_membership(
                "test-id", phone_number_id="x"
            )
        assert exc.value.status_code == 500

    def test_number_groups_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.number_groups.create(name="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "relay-rest.create_number_group"

    def test_number_groups_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.create_number_group", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.create(name="x")
        assert exc.value.status_code == 500

    def test_number_groups_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.number_groups.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "relay-rest.delete_number_group"

    def test_number_groups_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.delete_number_group", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.delete("test-id")
        assert exc.value.status_code == 500

    def test_number_groups_delete_membership(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.number_groups.delete_membership("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "relay-rest.delete_number_group_membership"

    def test_number_groups_delete_membership_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "relay-rest.delete_number_group_membership", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.delete_membership("test-id")
        assert exc.value.status_code == 500

    def test_number_groups_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.number_groups.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.retrieve_number_group"

    def test_number_groups_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.retrieve_number_group", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.get("test-id")
        assert exc.value.status_code == 500

    def test_number_groups_get_membership(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.number_groups.get_membership("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.retrieve_number_group_membership"

    def test_number_groups_get_membership_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "relay-rest.retrieve_number_group_membership", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.get_membership("test-id")
        assert exc.value.status_code == 500

    def test_number_groups_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.number_groups.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_number_groups"

    def test_number_groups_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.list_number_groups", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.list()
        assert exc.value.status_code == 500

    def test_number_groups_list_memberships(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.number_groups.list_memberships("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_number_group_memberships"

    def test_number_groups_list_memberships_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "relay-rest.list_number_group_memberships", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.list_memberships("test-id")
        assert exc.value.status_code == 500

    def test_number_groups_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.number_groups.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "relay-rest.update_number_group"

    def test_number_groups_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.update_number_group", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.update("test-id")
        assert exc.value.status_code == 500
