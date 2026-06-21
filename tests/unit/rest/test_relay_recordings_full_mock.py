"""Full success + error coverage for ``client.recordings`` (relay-rest).

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template.  Recordings is a
read + delete resource (no create/update) at ``/api/relay/rest/recordings``.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

_BASE = "/api/relay/rest/recordings"


class TestRelayRecordingsSuccess:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.recordings.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == _BASE
        assert last.matched_route == "relay-rest.list_recordings"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.recordings.get("rec-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/rec-1"
        assert last.matched_route == "relay-rest.get_recording"

    def test_delete(self, signalwire_client, mock):
        signalwire_client.recordings.delete("rec-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{_BASE}/rec-1"
        assert last.matched_route == "relay-rest.delete_recording"


class TestRelayRecordingsErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.list_recordings", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.recordings.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_recordings"
        assert last.response_status == 500

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.get_recording", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.recordings.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.get_recording"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.delete_recording", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.recordings.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.delete_recording"
        assert last.response_status == 404
