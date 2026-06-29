"""AUTO-GENERATED REST wire tests for the `queues` namespace — DO NOT EDIT.
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


class TestQueuesWire:
    def test_queues_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.queues.create()
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "relay-rest.create_queue"

    def test_queues_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.create_queue", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.create()
        assert exc.value.status_code == 500

    def test_queues_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.queues.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "relay-rest.delete_queue"

    def test_queues_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.delete_queue", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.delete("test-id")
        assert exc.value.status_code == 500

    def test_queues_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.queues.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.get_queue"

    def test_queues_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.get_queue", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.get("test-id")
        assert exc.value.status_code == 500

    def test_queues_get_member(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.queues.get_member("test-id", "test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.retrieve_queue_member"

    def test_queues_get_member_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.retrieve_queue_member", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.get_member("test-id", "test-id")
        assert exc.value.status_code == 500

    def test_queues_get_next_member(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.queues.get_next_member("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.retrieve_next_queue_member"

    def test_queues_get_next_member_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.retrieve_next_queue_member", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.get_next_member("test-id")
        assert exc.value.status_code == 500

    def test_queues_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.queues.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_queues"

    def test_queues_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.list_queues", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.list()
        assert exc.value.status_code == 500

    def test_queues_list_members(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.queues.list_members("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "relay-rest.list_queue_members"

    def test_queues_list_members_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.list_queue_members", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.list_members("test-id")
        assert exc.value.status_code == 500

    def test_queues_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.queues.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "relay-rest.update_queue"

    def test_queues_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.update_queue", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.update("test-id")
        assert exc.value.status_code == 500
