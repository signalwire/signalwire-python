"""Full success + error coverage for the typed ``client.fabric.*`` resource
families that are plain CRUD(+addresses) wrappers.

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template: a SUCCESS test
(call the real SDK method against the live mock, assert the parsed body shape +
the journal entry's method/path/matched_route) and an ERROR test (arm a 4xx/5xx
via ``mock.push_scenario`` and assert the SDK raises ``SignalWireRestError`` with
the right ``status_code`` plus the journal recorded the error status) per route.

Covered here:
  - PUT-update CRUD(+addresses): swml_scripts, relay_applications,
    freeswitch_connectors, cxml_scripts, sip_endpoints
  - PATCH-update CRUD(+addresses): sip_gateways (no addresses — see note),
    cxml_webhooks, swml_webhooks (create emits a DeprecationWarning)
  - cxml_applications: read/update/delete(+addresses), create raises
    NotImplementedError (asserted; create is not a canonical route)
  - call_flows: CRUD + the custom call_flow/{id}/addresses|versions endpoints
  - conference_rooms: CRUD + the custom conference_room/{id}/addresses endpoint
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

_ID = "rid-1001"


# ---------------------------------------------------------------------------
# Reusable CRUD(+addresses) exercisers — keep the per-route assertions identical
# to the micro-template while avoiding ~50x copy/paste across families.
# ---------------------------------------------------------------------------


def _crud_success(client, mock, resource, base, *, update_method, prefix, addresses=True):
    """Drive list/create/get/update/delete (+addresses) and assert each route."""
    # list (some list endpoints return a JSON array, others a paged object)
    body = resource.list()
    assert isinstance(body, (dict, list))
    last = mock.last_request()
    assert last.method == "GET"
    assert last.path == base
    assert last.matched_route == f"fabric.list_{prefix}s", last.matched_route

    # create
    body = resource.create(name="thing")
    assert isinstance(body, dict)
    last = mock.last_request()
    assert last.method == "POST"
    assert last.path == base
    assert last.matched_route == f"fabric.create_{prefix}", last.matched_route
    assert last.body and last.body.get("name") == "thing"

    # get
    body = resource.get(_ID)
    assert isinstance(body, dict)
    last = mock.last_request()
    assert last.method == "GET"
    assert last.path == f"{base}/{_ID}"
    assert last.matched_route == f"fabric.get_{prefix}", last.matched_route

    # update
    body = resource.update(_ID, name="renamed")
    assert isinstance(body, dict)
    last = mock.last_request()
    assert last.method == update_method
    assert last.path == f"{base}/{_ID}"
    assert last.matched_route == f"fabric.update_{prefix}", last.matched_route
    assert last.body and last.body.get("name") == "renamed"

    # delete
    resource.delete(_ID)
    last = mock.last_request()
    assert last.method == "DELETE"
    assert last.path == f"{base}/{_ID}"
    assert last.matched_route == f"fabric.delete_{prefix}", last.matched_route

    if addresses:
        body = resource.list_addresses(_ID)
        assert isinstance(body, (dict, list))
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{base}/{_ID}/addresses"
        assert last.matched_route == f"fabric.list_{prefix}_addresses", (
            last.matched_route
        )


def _crud_errors(client, mock, resource, *, prefix, addresses=True):
    """Drive a representative error per CRUD route and assert SignalWireRestError."""
    mock.push_scenario(f"fabric.list_{prefix}s", 500, {"error": "internal"})
    with pytest.raises(SignalWireRestError) as exc:
        resource.list()
    assert exc.value.status_code == 500
    assert mock.last_request().response_status == 500
    assert mock.last_request().matched_route == f"fabric.list_{prefix}s"

    mock.push_scenario(f"fabric.create_{prefix}", 422, {"error": "bad input"})
    with pytest.raises(SignalWireRestError) as exc:
        resource.create()
    assert exc.value.status_code == 422
    assert mock.last_request().matched_route == f"fabric.create_{prefix}"
    assert mock.last_request().response_status == 422

    mock.push_scenario(f"fabric.get_{prefix}", 404, {"error": "not found"})
    with pytest.raises(SignalWireRestError) as exc:
        resource.get("missing")
    assert exc.value.status_code == 404
    assert mock.last_request().matched_route == f"fabric.get_{prefix}"
    assert mock.last_request().response_status == 404

    mock.push_scenario(f"fabric.update_{prefix}", 404, {"error": "not found"})
    with pytest.raises(SignalWireRestError) as exc:
        resource.update("missing", name="x")
    assert exc.value.status_code == 404
    assert mock.last_request().matched_route == f"fabric.update_{prefix}"
    assert mock.last_request().response_status == 404

    mock.push_scenario(f"fabric.delete_{prefix}", 404, {"error": "not found"})
    with pytest.raises(SignalWireRestError) as exc:
        resource.delete("missing")
    assert exc.value.status_code == 404
    assert mock.last_request().matched_route == f"fabric.delete_{prefix}"
    assert mock.last_request().response_status == 404

    if addresses:
        mock.push_scenario(f"fabric.list_{prefix}_addresses", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            resource.list_addresses("missing")
        assert exc.value.status_code == 404
        assert mock.last_request().matched_route == f"fabric.list_{prefix}_addresses"
        assert mock.last_request().response_status == 404


_BASE = "/api/fabric/resources"


class TestFabricPutResourceFamilies:
    """PUT-update CRUD(+addresses) families."""

    def test_swml_scripts(self, signalwire_client, mock):
        r = signalwire_client.fabric.swml_scripts
        _crud_success(
            signalwire_client, mock, r, f"{_BASE}/swml_scripts",
            update_method="PUT", prefix="swml_script",
        )

    def test_swml_scripts_errors(self, signalwire_client, mock):
        _crud_errors(signalwire_client, mock, signalwire_client.fabric.swml_scripts,
                     prefix="swml_script")

    def test_relay_applications(self, signalwire_client, mock):
        r = signalwire_client.fabric.relay_applications
        _crud_success(
            signalwire_client, mock, r, f"{_BASE}/relay_applications",
            update_method="PUT", prefix="relay_application",
        )

    def test_relay_applications_errors(self, signalwire_client, mock):
        _crud_errors(signalwire_client, mock,
                     signalwire_client.fabric.relay_applications,
                     prefix="relay_application")

    def test_freeswitch_connectors(self, signalwire_client, mock):
        r = signalwire_client.fabric.freeswitch_connectors
        _crud_success(
            signalwire_client, mock, r, f"{_BASE}/freeswitch_connectors",
            update_method="PUT", prefix="freeswitch_connector",
        )

    def test_freeswitch_connectors_errors(self, signalwire_client, mock):
        _crud_errors(signalwire_client, mock,
                     signalwire_client.fabric.freeswitch_connectors,
                     prefix="freeswitch_connector")

    def test_cxml_scripts(self, signalwire_client, mock):
        r = signalwire_client.fabric.cxml_scripts
        _crud_success(
            signalwire_client, mock, r, f"{_BASE}/cxml_scripts",
            update_method="PUT", prefix="cxml_script",
        )

    def test_cxml_scripts_errors(self, signalwire_client, mock):
        _crud_errors(signalwire_client, mock, signalwire_client.fabric.cxml_scripts,
                     prefix="cxml_script")

    def test_sip_endpoints(self, signalwire_client, mock):
        r = signalwire_client.fabric.sip_endpoints
        _crud_success(
            signalwire_client, mock, r, f"{_BASE}/sip_endpoints",
            update_method="PUT", prefix="sip_endpoint",
        )

    def test_sip_endpoints_errors(self, signalwire_client, mock):
        _crud_errors(signalwire_client, mock, signalwire_client.fabric.sip_endpoints,
                     prefix="sip_endpoint")


class TestFabricPatchResourceFamilies:
    """PATCH-update CRUD(+addresses) families."""

    def test_cxml_webhooks(self, signalwire_client, mock):
        r = signalwire_client.fabric.cxml_webhooks
        # cxml_webhooks.create is auto-materialized: direct create warns.
        with pytest.warns(DeprecationWarning):
            r.create(name="thing")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{_BASE}/cxml_webhooks"
        assert last.matched_route == "fabric.create_cxml_webhook", last.matched_route
        # remaining CRUD routes (list/get/update/delete/addresses)
        body = r.list()
        assert isinstance(body, (dict, list))
        assert mock.last_request().matched_route == "fabric.list_cxml_webhooks"
        r.get(_ID)
        assert mock.last_request().matched_route == "fabric.get_cxml_webhook"
        r.update(_ID, name="x")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "fabric.update_cxml_webhook"
        r.delete(_ID)
        assert mock.last_request().matched_route == "fabric.delete_cxml_webhook"
        r.list_addresses(_ID)
        assert mock.last_request().matched_route == "fabric.list_cxml_webhook_addresses"

    def test_cxml_webhooks_errors(self, signalwire_client, mock):
        r = signalwire_client.fabric.cxml_webhooks
        mock.push_scenario("fabric.list_cxml_webhooks", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            r.list()
        assert exc.value.status_code == 500
        assert mock.last_request().response_status == 500
        mock.push_scenario("fabric.get_cxml_webhook", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.get("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.update_cxml_webhook", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.update("missing", name="x")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.delete_cxml_webhook", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.delete("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.list_cxml_webhook_addresses", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.list_addresses("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.create_cxml_webhook", 422, {"error": "bad"})
        with pytest.warns(DeprecationWarning), pytest.raises(SignalWireRestError) as exc:
            r.create(name="thing")
        assert exc.value.status_code == 422
        assert mock.last_request().matched_route == "fabric.create_cxml_webhook"
        assert mock.last_request().response_status == 422

    def test_swml_webhooks(self, signalwire_client, mock):
        r = signalwire_client.fabric.swml_webhooks
        with pytest.warns(DeprecationWarning):
            r.create(name="thing")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{_BASE}/swml_webhooks"
        assert last.matched_route == "fabric.create_swml_webhook", last.matched_route
        body = r.list()
        assert isinstance(body, (dict, list))
        assert mock.last_request().matched_route == "fabric.list_swml_webhooks"
        r.get(_ID)
        assert mock.last_request().matched_route == "fabric.get_swml_webhook"
        r.update(_ID, name="x")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "fabric.update_swml_webhook"
        r.delete(_ID)
        assert mock.last_request().matched_route == "fabric.delete_swml_webhook"
        r.list_addresses(_ID)
        assert mock.last_request().matched_route == "fabric.list_swml_webhook_addresses"

    def test_swml_webhooks_errors(self, signalwire_client, mock):
        r = signalwire_client.fabric.swml_webhooks
        mock.push_scenario("fabric.list_swml_webhooks", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            r.list()
        assert exc.value.status_code == 500
        mock.push_scenario("fabric.get_swml_webhook", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.get("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.update_swml_webhook", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.update("missing", name="x")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.delete_swml_webhook", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.delete("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.list_swml_webhook_addresses", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.list_addresses("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.create_swml_webhook", 422, {"error": "bad"})
        with pytest.warns(DeprecationWarning), pytest.raises(SignalWireRestError) as exc:
            r.create(name="thing")
        assert exc.value.status_code == 422
        assert mock.last_request().matched_route == "fabric.create_swml_webhook"
        assert mock.last_request().response_status == 422


class TestFabricSipGateways:
    """sip_gateways: PATCH-update CRUD (no addresses route reachable — see GAP)."""

    def test_crud(self, signalwire_client, mock):
        r = signalwire_client.fabric.sip_gateways
        body = r.list()
        assert isinstance(body, (dict, list))
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/sip_gateways"
        assert last.matched_route == "fabric.list_sip_gateways", last.matched_route

        body = r.create(name="gw")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_sip_gateway", last.matched_route

        r.get(_ID)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/sip_gateways/{_ID}"
        assert last.matched_route == "fabric.get_sip_gateway", last.matched_route

        r.update(_ID, name="x")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "fabric.update_sip_gateway", last.matched_route

        r.delete(_ID)
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_sip_gateway", last.matched_route

    def test_crud_errors(self, signalwire_client, mock):
        r = signalwire_client.fabric.sip_gateways
        mock.push_scenario("fabric.list_sip_gateways", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            r.list()
        assert exc.value.status_code == 500
        assert mock.last_request().response_status == 500
        mock.push_scenario("fabric.create_sip_gateway", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            r.create()
        assert exc.value.status_code == 422
        mock.push_scenario("fabric.get_sip_gateway", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.get("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.update_sip_gateway", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.update("missing", name="x")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.delete_sip_gateway", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.delete("missing")
        assert exc.value.status_code == 404


class TestFabricCxmlApplications:
    """cxml_applications: read/update/delete(+addresses); create is unsupported."""

    def test_read_update_delete(self, signalwire_client, mock):
        r = signalwire_client.fabric.cxml_applications
        body = r.list()
        assert isinstance(body, (dict, list))
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/cxml_applications"
        assert last.matched_route == "fabric.list_cxml_applications", last.matched_route

        r.get(_ID)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_cxml_application", last.matched_route

        r.update(_ID, name="x")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_cxml_application", last.matched_route

        r.delete(_ID)
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_cxml_application", last.matched_route

        r.list_addresses(_ID)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_cxml_application_addresses", (
            last.matched_route
        )

    def test_create_not_implemented(self, signalwire_client, mock):
        # The cXML applications API has no create operation; the SDK raises
        # NotImplementedError rather than issuing a request. (Not a canonical route.)
        with pytest.raises(NotImplementedError):
            signalwire_client.fabric.cxml_applications.create(name="x")

    def test_errors(self, signalwire_client, mock):
        r = signalwire_client.fabric.cxml_applications
        mock.push_scenario("fabric.list_cxml_applications", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            r.list()
        assert exc.value.status_code == 500
        mock.push_scenario("fabric.get_cxml_application", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.get("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.update_cxml_application", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.update("missing", name="x")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.delete_cxml_application", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.delete("missing")
        assert exc.value.status_code == 404
        mock.push_scenario(
            "fabric.list_cxml_application_addresses", 404, {"error": "nf"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            r.list_addresses("missing")
        assert exc.value.status_code == 404


class TestFabricCallFlows:
    """call_flows: PUT CRUD + the custom call_flow/{id}/addresses|versions paths."""

    def test_crud(self, signalwire_client, mock):
        r = signalwire_client.fabric.call_flows
        body = r.list()
        assert isinstance(body, (dict, list))
        assert mock.last_request().matched_route == "fabric.list_call_flows"
        r.create(name="cf")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_call_flow", last.matched_route
        r.get(_ID)
        assert mock.last_request().matched_route == "fabric.get_call_flow"
        r.update(_ID, name="x")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_call_flow", last.matched_route
        r.delete(_ID)
        assert mock.last_request().matched_route == "fabric.delete_call_flow"

    def test_custom_subpaths(self, signalwire_client, mock):
        r = signalwire_client.fabric.call_flows
        # Note: addresses/versions use the SINGULAR 'call_flow' segment.
        r.list_addresses(_ID)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/call_flow/{_ID}/addresses"
        assert last.matched_route == "fabric.list_call_flow_addresses", (
            last.matched_route
        )
        r.list_versions(_ID)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/call_flow/{_ID}/versions"
        assert last.matched_route == "fabric.list_call_flow_versions", (
            last.matched_route
        )
        r.deploy_version(_ID, version="v2")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{_BASE}/call_flow/{_ID}/versions"
        assert last.matched_route == "fabric.deploy_call_flow_version", (
            last.matched_route
        )

    def test_errors(self, signalwire_client, mock):
        r = signalwire_client.fabric.call_flows
        mock.push_scenario("fabric.list_call_flows", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            r.list()
        assert exc.value.status_code == 500
        mock.push_scenario("fabric.create_call_flow", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            r.create()
        assert exc.value.status_code == 422
        mock.push_scenario("fabric.get_call_flow", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.get("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.update_call_flow", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.update("missing", name="x")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.delete_call_flow", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.delete("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.list_call_flow_addresses", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.list_addresses("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.list_call_flow_versions", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.list_versions("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.deploy_call_flow_version", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            r.deploy_version("missing", version="v2")
        assert exc.value.status_code == 422
        assert mock.last_request().matched_route == "fabric.deploy_call_flow_version"
        assert mock.last_request().response_status == 422


class TestFabricConferenceRooms:
    """conference_rooms: PUT CRUD + the custom conference_room/{id}/addresses path."""

    def test_crud(self, signalwire_client, mock):
        r = signalwire_client.fabric.conference_rooms
        body = r.list()
        assert isinstance(body, (dict, list))
        assert mock.last_request().matched_route == "fabric.list_conference_rooms"
        r.create(name="room")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_conference_room", last.matched_route
        r.get(_ID)
        assert mock.last_request().matched_route == "fabric.get_conference_room"
        r.update(_ID, name="x")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_conference_room", last.matched_route
        r.delete(_ID)
        assert mock.last_request().matched_route == "fabric.delete_conference_room"

    def test_list_addresses(self, signalwire_client, mock):
        # Note: uses the SINGULAR 'conference_room' segment.
        signalwire_client.fabric.conference_rooms.list_addresses(_ID)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/conference_room/{_ID}/addresses"
        assert last.matched_route == "fabric.list_conference_room_addresses", (
            last.matched_route
        )

    def test_errors(self, signalwire_client, mock):
        r = signalwire_client.fabric.conference_rooms
        mock.push_scenario("fabric.list_conference_rooms", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            r.list()
        assert exc.value.status_code == 500
        mock.push_scenario("fabric.create_conference_room", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            r.create()
        assert exc.value.status_code == 422
        mock.push_scenario("fabric.get_conference_room", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.get("missing")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.update_conference_room", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.update("missing", name="x")
        assert exc.value.status_code == 404
        mock.push_scenario("fabric.delete_conference_room", 404, {"error": "nf"})
        with pytest.raises(SignalWireRestError) as exc:
            r.delete("missing")
        assert exc.value.status_code == 404
        mock.push_scenario(
            "fabric.list_conference_room_addresses", 404, {"error": "nf"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            r.list_addresses("missing")
        assert exc.value.status_code == 404
