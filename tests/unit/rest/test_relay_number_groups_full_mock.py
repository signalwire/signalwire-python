"""Full success + error coverage for ``client.number_groups`` (relay-rest).

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template.  Number groups
is a CRUD resource (PUT update) at ``/api/relay/rest/number_groups`` plus
membership operations.  Note the membership get/delete hit the *standalone*
``/api/relay/rest/number_group_memberships/{id}`` paths while list/add hang off
the parent group at ``.../number_groups/{id}/number_group_memberships``.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

_BASE = "/api/relay/rest/number_groups"
_MEMBERSHIPS = "/api/relay/rest/number_group_memberships"


class TestRelayNumberGroupsSuccess:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.number_groups.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == _BASE
        assert last.matched_route == "relay-rest.list_number_groups"

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.number_groups.create(name="group-a")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == _BASE
        assert last.matched_route == "relay-rest.create_number_group"
        assert last.body and last.body.get("name") == "group-a"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.number_groups.get("ng-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/ng-1"
        assert last.matched_route == "relay-rest.retrieve_number_group"

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.number_groups.update("ng-1", name="renamed")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == f"{_BASE}/ng-1"
        assert last.matched_route == "relay-rest.update_number_group"
        assert last.body and last.body.get("name") == "renamed"

    def test_delete(self, signalwire_client, mock):
        signalwire_client.number_groups.delete("ng-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{_BASE}/ng-1"
        assert last.matched_route == "relay-rest.delete_number_group"

    def test_list_memberships(self, signalwire_client, mock):
        body = signalwire_client.number_groups.list_memberships("ng-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/ng-1/number_group_memberships"
        assert last.matched_route == "relay-rest.list_number_group_memberships"

    def test_add_membership(self, signalwire_client, mock):
        body = signalwire_client.number_groups.add_membership(
            "ng-1", phone_number_id="pn-1"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{_BASE}/ng-1/number_group_memberships"
        assert last.matched_route == "relay-rest.create_number_group_membership"
        assert last.body and last.body.get("phone_number_id") == "pn-1"

    def test_get_membership(self, signalwire_client, mock):
        body = signalwire_client.number_groups.get_membership("ngm-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_MEMBERSHIPS}/ngm-1"
        assert last.matched_route == "relay-rest.retrieve_number_group_membership"

    def test_delete_membership(self, signalwire_client, mock):
        signalwire_client.number_groups.delete_membership("ngm-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{_MEMBERSHIPS}/ngm-1"
        assert last.matched_route == "relay-rest.delete_number_group_membership"


class TestRelayNumberGroupsErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.list_number_groups", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_number_groups"
        assert last.response_status == 500

    def test_create_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.create_number_group", 422, {"error": "name required"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.create()
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.create_number_group"
        assert last.response_status == 422

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.retrieve_number_group", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.retrieve_number_group"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.update_number_group", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.update("missing", name="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.update_number_group"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.delete_number_group", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.delete_number_group"
        assert last.response_status == 404

    def test_list_memberships_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.list_number_group_memberships", 404, {"error": "nope"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.list_memberships("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_number_group_memberships"
        assert last.response_status == 404

    def test_add_membership_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.create_number_group_membership", 422, {"error": "bad"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.add_membership("ng-1")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.create_number_group_membership"
        assert last.response_status == 422

    def test_get_membership_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.retrieve_number_group_membership", 404, {"error": "nope"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.get_membership("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.retrieve_number_group_membership"
        assert last.response_status == 404

    def test_delete_membership_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.delete_number_group_membership", 404, {"error": "nope"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.number_groups.delete_membership("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.delete_number_group_membership"
        assert last.response_status == 404
