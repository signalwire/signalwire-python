"""AUTO-GENERATED REST wire tests for the `chat` namespace — DO NOT EDIT.
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


class TestChatWire:
    def test_chat_create_token(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.chat.create_token(ttl="x", channels="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "chat.create_chat_token"

    def test_chat_create_token_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("chat.create_chat_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.chat.create_token(ttl="x", channels="x")
        assert exc.value.status_code == 500
