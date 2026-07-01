"""AUTO-GENERATED REST wire tests for the `logs` namespace — DO NOT EDIT.
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


class TestLogsWire:
    def test_conferences_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.logs.conferences.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "logs.list_conferences"

    def test_conferences_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("logs.list_conferences", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.conferences.list()
        assert exc.value.status_code == 500

    def test_fax_get(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.logs.fax.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fax.get_fax_log"

    def test_fax_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fax.get_fax_log", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.fax.get("test-id")
        assert exc.value.status_code == 500

    def test_fax_list(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.logs.fax.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fax.list_fax_logs"

    def test_fax_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fax.list_fax_logs", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.fax.list()
        assert exc.value.status_code == 500

    def test_messages_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.logs.messages.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "message.get_message_log"

    def test_messages_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("message.get_message_log", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.messages.get("test-id")
        assert exc.value.status_code == 500

    def test_messages_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.logs.messages.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "message.list_message_logs"

    def test_messages_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("message.list_message_logs", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.messages.list()
        assert exc.value.status_code == 500

    def test_voice_get(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.logs.voice.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "voice.get_voice_log"

    def test_voice_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("voice.get_voice_log", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.voice.get("test-id")
        assert exc.value.status_code == 500

    def test_voice_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.logs.voice.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "voice.list_voice_logs"

    def test_voice_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("voice.list_voice_logs", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.voice.list()
        assert exc.value.status_code == 500

    def test_voice_list_events(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.logs.voice.list_events("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "voice.list_voice_log_events"

    def test_voice_list_events_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("voice.list_voice_log_events", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.logs.voice.list_events("test-id")
        assert exc.value.status_code == 500
