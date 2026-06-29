"""AUTO-GENERATED REST wire tests for the `project` namespace — DO NOT EDIT.
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


class TestProjectWire:
    def test_tokens_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.project.tokens.create(name="x", permissions="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "project.create_token"

    def test_tokens_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("project.create_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.project.tokens.create(name="x", permissions="x")
        assert exc.value.status_code == 500

    def test_tokens_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.project.tokens.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "project.delete_token"

    def test_tokens_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("project.delete_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.project.tokens.delete("test-id")
        assert exc.value.status_code == 500

    def test_tokens_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.project.tokens.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "project.update_token"

    def test_tokens_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("project.update_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.project.tokens.update("test-id")
        assert exc.value.status_code == 500
