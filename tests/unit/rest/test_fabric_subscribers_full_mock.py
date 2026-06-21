"""Full success + error coverage for ``client.fabric.subscribers``
(``SubscribersResource``).

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template: a SUCCESS test
(call the real SDK method against the live mock, assert the parsed body shape +
the journal entry's method/path/matched_route) and an ERROR test (arm a 4xx/5xx
via ``mock.push_scenario`` and assert the SDK raises ``SignalWireRestError`` with
the right ``status_code`` plus the journal recorded the error status) per route.

Subscribers are a PUT-update CRUD resource (+ addresses) AND own a nested
``sip_endpoints`` sub-resource with its own CRUD (PATCH-update).
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

_SUB = "sub-1001"
_EP = "ep-2002"


class TestFabricSubscribersSuccess:
    """Happy-path: subscriber CRUD + addresses on the exact canonical paths."""

    def test_list(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.list()
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/resources/subscribers"
        assert last.matched_route == "fabric.list_subscribers", (
            f"expected fabric.list_subscribers, got {last.matched_route!r}"
        )

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.create(email="a@b.c")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/resources/subscribers"
        assert last.matched_route == "fabric.create_subscriber", (
            f"expected fabric.create_subscriber, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("email") == "a@b.c"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.get(_SUB)
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"/api/fabric/resources/subscribers/{_SUB}"
        assert last.matched_route == "fabric.get_subscriber", (
            f"expected fabric.get_subscriber, got {last.matched_route!r}"
        )

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.update(_SUB, email="x@y.z")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == f"/api/fabric/resources/subscribers/{_SUB}"
        assert last.matched_route == "fabric.update_subscriber", (
            f"expected fabric.update_subscriber, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("email") == "x@y.z"

    def test_delete(self, signalwire_client, mock):
        signalwire_client.fabric.subscribers.delete(_SUB)
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"/api/fabric/resources/subscribers/{_SUB}"
        assert last.matched_route == "fabric.delete_subscriber", (
            f"expected fabric.delete_subscriber, got {last.matched_route!r}"
        )

    def test_list_addresses(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.list_addresses(_SUB)
        assert isinstance(body, (dict, list))
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"/api/fabric/resources/subscribers/{_SUB}/addresses"
        assert last.matched_route == "fabric.list_subscriber_addresses", (
            f"expected fabric.list_subscriber_addresses, got {last.matched_route!r}"
        )


class TestFabricSubscriberSipEndpointsSuccess:
    """Happy-path: the nested subscriber sip_endpoints CRUD."""

    def test_list(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.list_sip_endpoints(_SUB)
        assert isinstance(body, (dict, list))
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"/api/fabric/resources/subscribers/{_SUB}/sip_endpoints"
        assert last.matched_route == "fabric.list_subscriber_sip_endpoints", (
            f"expected fabric.list_subscriber_sip_endpoints, got {last.matched_route!r}"
        )

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.create_sip_endpoint(
            _SUB, username="alice"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"/api/fabric/resources/subscribers/{_SUB}/sip_endpoints"
        assert last.matched_route == "fabric.create_subscriber_sip_endpoint", (
            f"expected fabric.create_subscriber_sip_endpoint, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("username") == "alice"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.get_sip_endpoint(_SUB, _EP)
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == (
            f"/api/fabric/resources/subscribers/{_SUB}/sip_endpoints/{_EP}"
        )
        assert last.matched_route == "fabric.get_subscriber_sip_endpoint", (
            f"expected fabric.get_subscriber_sip_endpoint, got {last.matched_route!r}"
        )

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.fabric.subscribers.update_sip_endpoint(
            _SUB, _EP, username="bob"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.path == (
            f"/api/fabric/resources/subscribers/{_SUB}/sip_endpoints/{_EP}"
        )
        assert last.matched_route == "fabric.update_subscriber_sip_endpoint", (
            f"expected fabric.update_subscriber_sip_endpoint, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("username") == "bob"

    def test_delete(self, signalwire_client, mock):
        signalwire_client.fabric.subscribers.delete_sip_endpoint(_SUB, _EP)
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == (
            f"/api/fabric/resources/subscribers/{_SUB}/sip_endpoints/{_EP}"
        )
        assert last.matched_route == "fabric.delete_subscriber_sip_endpoint", (
            f"expected fabric.delete_subscriber_sip_endpoint, got {last.matched_route!r}"
        )


class TestFabricSubscribersErrors:
    """Failure path: subscriber CRUD + addresses surface 4xx/5xx errors."""

    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("fabric.list_subscribers", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "fabric.list_subscribers"
        assert last.response_status == 500

    def test_create_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("fabric.create_subscriber", 422, {"error": "email required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.create()
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "fabric.create_subscriber"
        assert last.response_status == 422

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("fabric.get_subscriber", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.get_subscriber"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario("fabric.update_subscriber", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.update("missing", email="x@y.z")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.update_subscriber"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("fabric.delete_subscriber", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.delete_subscriber"
        assert last.response_status == 404

    def test_list_addresses_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.list_subscriber_addresses", 404, {"error": "not found"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.list_addresses("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.list_subscriber_addresses"
        assert last.response_status == 404


class TestFabricSubscriberSipEndpointsErrors:
    """Failure path: the nested sip_endpoints CRUD surfaces 4xx/5xx errors."""

    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.list_subscriber_sip_endpoints", 500, {"error": "internal"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.list_sip_endpoints(_SUB)
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "fabric.list_subscriber_sip_endpoints"
        assert last.response_status == 500

    def test_create_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.create_subscriber_sip_endpoint", 422, {"error": "username required"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.create_sip_endpoint(_SUB)
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "fabric.create_subscriber_sip_endpoint"
        assert last.response_status == 422

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.get_subscriber_sip_endpoint", 404, {"error": "not found"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.get_sip_endpoint(_SUB, "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.get_subscriber_sip_endpoint"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.update_subscriber_sip_endpoint", 404, {"error": "not found"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.update_sip_endpoint(
                _SUB, "missing", username="bob"
            )
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.update_subscriber_sip_endpoint"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.delete_subscriber_sip_endpoint", 404, {"error": "not found"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.delete_sip_endpoint(_SUB, "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.delete_subscriber_sip_endpoint"
        assert last.response_status == 404
