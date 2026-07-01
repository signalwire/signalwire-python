"""AUTO-GENERATED REST wire tests for the `calling` namespace — DO NOT EDIT.
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


class TestCallingWire:
    def test_calling_ai_hold(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.calling.ai_hold("test-id")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "calling.call-commands"

    def test_calling_ai_hold_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("calling.call-commands", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.calling.ai_hold("test-id")
        assert exc.value.status_code == 500
