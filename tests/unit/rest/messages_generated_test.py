"""AUTO-GENERATED REST wire tests for the `messages` namespace — DO NOT EDIT.
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


class TestMessagesWire:
    def test_messages_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.messages.create(to="x", from_="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "messages.create_message"

    def test_messages_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("messages.create_message", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.messages.create(to="x", from_="x")
        assert exc.value.status_code == 500

    def test_messages_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.messages.update("test-id", body="x")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "messages.update_message"

    def test_messages_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("messages.update_message", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.messages.update("test-id", body="x")
        assert exc.value.status_code == 500
