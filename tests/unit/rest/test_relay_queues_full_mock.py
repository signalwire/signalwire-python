"""Full success + error coverage for ``client.queues`` (relay-rest).

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template.  Queues is a
CRUD resource (PUT update) at ``/api/relay/rest/queues`` plus member reads:
``list_members``, ``get_next_member`` (.../members/next), ``get_member``.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

_BASE = "/api/relay/rest/queues"


class TestRelayQueuesSuccess:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.queues.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == _BASE
        assert last.matched_route == "relay-rest.list_queues"

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.queues.create(name="support")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == _BASE
        assert last.matched_route == "relay-rest.create_queue"
        assert last.body and last.body.get("name") == "support"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.queues.get("q-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/q-1"
        assert last.matched_route == "relay-rest.get_queue"

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.queues.update("q-1", name="renamed")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == f"{_BASE}/q-1"
        assert last.matched_route == "relay-rest.update_queue"
        assert last.body and last.body.get("name") == "renamed"

    def test_delete(self, signalwire_client, mock):
        signalwire_client.queues.delete("q-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{_BASE}/q-1"
        assert last.matched_route == "relay-rest.delete_queue"

    def test_list_members(self, signalwire_client, mock):
        body = signalwire_client.queues.list_members("q-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/q-1/members"
        assert last.matched_route == "relay-rest.list_queue_members"

    def test_get_next_member(self, signalwire_client, mock):
        body = signalwire_client.queues.get_next_member("q-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/q-1/members/next"
        assert last.matched_route == "relay-rest.retrieve_next_queue_member"

    def test_get_member(self, signalwire_client, mock):
        body = signalwire_client.queues.get_member("q-1", "m-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/q-1/members/m-1"
        assert last.matched_route == "relay-rest.retrieve_queue_member"


class TestRelayQueuesErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.list_queues", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_queues"
        assert last.response_status == 500

    def test_create_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.create_queue", 422, {"error": "name required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.create()
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.create_queue"
        assert last.response_status == 422

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.get_queue", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.get_queue"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.update_queue", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.update("missing", name="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.update_queue"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.delete_queue", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.delete_queue"
        assert last.response_status == 404

    def test_list_members_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.list_queue_members", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.list_members("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_queue_members"
        assert last.response_status == 404

    def test_get_next_member_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.retrieve_next_queue_member", 404, {"error": "empty"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.get_next_member("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.retrieve_next_queue_member"
        assert last.response_status == 404

    def test_get_member_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.retrieve_queue_member", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.queues.get_member("missing", "m-1")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.retrieve_queue_member"
        assert last.response_status == 404
