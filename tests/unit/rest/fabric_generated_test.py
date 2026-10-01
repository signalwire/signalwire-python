"""AUTO-GENERATED REST wire tests for the `fabric` namespace — DO NOT EDIT.
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


class TestFabricWire:
    def test_addresses_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.addresses.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_fabric_address"

    def test_addresses_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_fabric_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.addresses.get("test-id")
        assert exc.value.status_code == 500

    def test_addresses_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.addresses.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_fabric_addresses"

    def test_addresses_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_fabric_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.addresses.list()
        assert exc.value.status_code == 500

    def test_ai_agents_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.ai_agents.create(prompt={}, name="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_ai_agent"

    def test_ai_agents_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_ai_agent", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.create(prompt={}, name="x")
        assert exc.value.status_code == 500

    def test_ai_agents_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.ai_agents.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_ai_agent"

    def test_ai_agents_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_ai_agent", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.delete("test-id")
        assert exc.value.status_code == 500

    def test_ai_agents_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.ai_agents.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_ai_agent"

    def test_ai_agents_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_ai_agent", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.get("test-id")
        assert exc.value.status_code == 500

    def test_ai_agents_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.ai_agents.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_ai_agents"

    def test_ai_agents_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_ai_agents", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.list()
        assert exc.value.status_code == 500

    def test_ai_agents_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.ai_agents.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_ai_agent_addresses"

    def test_ai_agents_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_ai_agent_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_ai_agents_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.ai_agents.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "fabric.update_ai_agent"

    def test_ai_agents_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_ai_agent", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.update("test-id")
        assert exc.value.status_code == 500

    def test_alias_addresses_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.alias_addresses.create(name="x", resource_id="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric-addresses.create_alias_address"

    def test_alias_addresses_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric-addresses.create_alias_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.alias_addresses.create(name="x", resource_id="x")
        assert exc.value.status_code == 500

    def test_alias_addresses_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.alias_addresses.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric-addresses.delete_alias_address"

    def test_alias_addresses_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric-addresses.delete_alias_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.alias_addresses.delete("test-id")
        assert exc.value.status_code == 500

    def test_alias_addresses_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.alias_addresses.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric-addresses.get_alias_address"

    def test_alias_addresses_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric-addresses.get_alias_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.alias_addresses.get("test-id")
        assert exc.value.status_code == 500

    def test_alias_addresses_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.alias_addresses.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric-addresses.list_alias_addresses"

    def test_alias_addresses_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric-addresses.list_alias_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.alias_addresses.list()
        assert exc.value.status_code == 500

    def test_alias_addresses_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.alias_addresses.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "fabric-addresses.update_alias_address"

    def test_alias_addresses_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric-addresses.update_alias_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.alias_addresses.update("test-id")
        assert exc.value.status_code == 500

    def test_call_flows_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.call_flows.create(title="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_call_flow"

    def test_call_flows_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_call_flow", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.call_flows.create(title="x")
        assert exc.value.status_code == 500

    def test_call_flows_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.call_flows.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_call_flow"

    def test_call_flows_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_call_flow", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.call_flows.delete("test-id")
        assert exc.value.status_code == 500

    def test_call_flows_deploy_version(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.call_flows.deploy_version("test-id", {})
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.deploy_call_flow_version"

    def test_call_flows_deploy_version_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.deploy_call_flow_version", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.call_flows.deploy_version("test-id", {})
        assert exc.value.status_code == 500

    def test_call_flows_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.call_flows.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_call_flow"

    def test_call_flows_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_call_flow", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.call_flows.get("test-id")
        assert exc.value.status_code == 500

    def test_call_flows_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.call_flows.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_call_flows"

    def test_call_flows_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_call_flows", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.call_flows.list()
        assert exc.value.status_code == 500

    def test_call_flows_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.call_flows.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_call_flow_addresses"

    def test_call_flows_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_call_flow_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.call_flows.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_call_flows_list_versions(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.call_flows.list_versions("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_call_flow_versions"

    def test_call_flows_list_versions_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_call_flow_versions", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.call_flows.list_versions("test-id")
        assert exc.value.status_code == 500

    def test_call_flows_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.call_flows.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_call_flow"

    def test_call_flows_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_call_flow", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.call_flows.update("test-id")
        assert exc.value.status_code == 500

    def test_conference_rooms_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.conference_rooms.create(
            name="x", enable_room_previews=True
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_conference_room"

    def test_conference_rooms_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_conference_room", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.conference_rooms.create(
                name="x", enable_room_previews=True
            )
        assert exc.value.status_code == 500

    def test_conference_rooms_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.conference_rooms.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_conference_room"

    def test_conference_rooms_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_conference_room", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.conference_rooms.delete("test-id")
        assert exc.value.status_code == 500

    def test_conference_rooms_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.conference_rooms.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_conference_room"

    def test_conference_rooms_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_conference_room", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.conference_rooms.get("test-id")
        assert exc.value.status_code == 500

    def test_conference_rooms_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.conference_rooms.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_conference_rooms"

    def test_conference_rooms_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_conference_rooms", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.conference_rooms.list()
        assert exc.value.status_code == 500

    def test_conference_rooms_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.conference_rooms.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_conference_room_addresses"

    def test_conference_rooms_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_conference_room_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.conference_rooms.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_conference_rooms_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.conference_rooms.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_conference_room"

    def test_conference_rooms_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_conference_room", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.conference_rooms.update("test-id")
        assert exc.value.status_code == 500

    def test_cxml_applications_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_applications.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_cxml_application"

    def test_cxml_applications_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_cxml_application", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_applications.delete("test-id")
        assert exc.value.status_code == 500

    def test_cxml_applications_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_applications.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_cxml_application"

    def test_cxml_applications_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_cxml_application", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_applications.get("test-id")
        assert exc.value.status_code == 500

    def test_cxml_applications_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_applications.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_cxml_applications"

    def test_cxml_applications_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_cxml_applications", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_applications.list()
        assert exc.value.status_code == 500

    def test_cxml_applications_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_applications.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_cxml_application_addresses"

    def test_cxml_applications_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric.list_cxml_application_addresses", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_applications.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_cxml_applications_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_applications.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_cxml_application"

    def test_cxml_applications_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_cxml_application", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_applications.update("test-id")
        assert exc.value.status_code == 500

    def test_cxml_scripts_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_scripts.create(display_name="x", contents="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_cxml_script"

    def test_cxml_scripts_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_cxml_script", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_scripts.create(display_name="x", contents="x")
        assert exc.value.status_code == 500

    def test_cxml_scripts_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_scripts.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_cxml_script"

    def test_cxml_scripts_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_cxml_script", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_scripts.delete("test-id")
        assert exc.value.status_code == 500

    def test_cxml_scripts_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_scripts.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_cxml_script"

    def test_cxml_scripts_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_cxml_script", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_scripts.get("test-id")
        assert exc.value.status_code == 500

    def test_cxml_scripts_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_scripts.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_cxml_scripts"

    def test_cxml_scripts_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_cxml_scripts", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_scripts.list()
        assert exc.value.status_code == 500

    def test_cxml_scripts_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_scripts.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_cxml_script_addresses"

    def test_cxml_scripts_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_cxml_script_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_scripts.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_cxml_scripts_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_scripts.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_cxml_script"

    def test_cxml_scripts_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_cxml_script", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_scripts.update("test-id")
        assert exc.value.status_code == 500

    def test_cxml_webhooks_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_webhooks.create(primary_request_url="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_cxml_webhook"

    def test_cxml_webhooks_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_cxml_webhook", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_webhooks.create(primary_request_url="x")
        assert exc.value.status_code == 500

    def test_cxml_webhooks_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_webhooks.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_cxml_webhook"

    def test_cxml_webhooks_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_cxml_webhook", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_webhooks.delete("test-id")
        assert exc.value.status_code == 500

    def test_cxml_webhooks_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_webhooks.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_cxml_webhook"

    def test_cxml_webhooks_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_cxml_webhook", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_webhooks.get("test-id")
        assert exc.value.status_code == 500

    def test_cxml_webhooks_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_webhooks.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_cxml_webhooks"

    def test_cxml_webhooks_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_cxml_webhooks", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_webhooks.list()
        assert exc.value.status_code == 500

    def test_cxml_webhooks_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_webhooks.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_cxml_webhook_addresses"

    def test_cxml_webhooks_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_cxml_webhook_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_webhooks.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_cxml_webhooks_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_webhooks.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "fabric.update_cxml_webhook"

    def test_cxml_webhooks_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_cxml_webhook", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.cxml_webhooks.update("test-id")
        assert exc.value.status_code == 500

    def test_freeswitch_connectors_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.freeswitch_connectors.create(name="x", token="x")  # noqa: S106
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_freeswitch_connector"

    def test_freeswitch_connectors_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_freeswitch_connector", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.freeswitch_connectors.create(name="x", token="x")  # noqa: S106
        assert exc.value.status_code == 500

    def test_freeswitch_connectors_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.freeswitch_connectors.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_freeswitch_connector"

    def test_freeswitch_connectors_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_freeswitch_connector", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.freeswitch_connectors.delete("test-id")
        assert exc.value.status_code == 500

    def test_freeswitch_connectors_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.freeswitch_connectors.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_freeswitch_connector"

    def test_freeswitch_connectors_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_freeswitch_connector", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.freeswitch_connectors.get("test-id")
        assert exc.value.status_code == 500

    def test_freeswitch_connectors_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.freeswitch_connectors.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_freeswitch_connectors"

    def test_freeswitch_connectors_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_freeswitch_connectors", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.freeswitch_connectors.list()
        assert exc.value.status_code == 500

    def test_freeswitch_connectors_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.freeswitch_connectors.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_freeswitch_connector_addresses"

    def test_freeswitch_connectors_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric.list_freeswitch_connector_addresses", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.freeswitch_connectors.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_freeswitch_connectors_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.freeswitch_connectors.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_freeswitch_connector"

    def test_freeswitch_connectors_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_freeswitch_connector", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.freeswitch_connectors.update("test-id")
        assert exc.value.status_code == 500

    def test_phone_number_addresses_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.phone_number_addresses.create(
            resource_id="x", handler_type="calling"
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric-addresses.create_phone_number_address"

    def test_phone_number_addresses_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric-addresses.create_phone_number_address", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.phone_number_addresses.create(
                resource_id="x", handler_type="calling"
            )
        assert exc.value.status_code == 500

    def test_phone_number_addresses_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.phone_number_addresses.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric-addresses.delete_phone_number_address"

    def test_phone_number_addresses_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric-addresses.delete_phone_number_address", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.phone_number_addresses.delete("test-id")
        assert exc.value.status_code == 500

    def test_phone_number_addresses_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.phone_number_addresses.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric-addresses.get_phone_number_address"

    def test_phone_number_addresses_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric-addresses.get_phone_number_address", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.phone_number_addresses.get("test-id")
        assert exc.value.status_code == 500

    def test_phone_number_addresses_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.phone_number_addresses.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric-addresses.list_phone_number_addresses"

    def test_phone_number_addresses_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric-addresses.list_phone_number_addresses", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.phone_number_addresses.list()
        assert exc.value.status_code == 500

    def test_phone_number_addresses_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.phone_number_addresses.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "fabric-addresses.update_phone_number_address"

    def test_phone_number_addresses_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric-addresses.update_phone_number_address", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.phone_number_addresses.update("test-id")
        assert exc.value.status_code == 500

    def test_relay_applications_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.relay_applications.create(name="x", topic="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_relay_application"

    def test_relay_applications_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_relay_application", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.relay_applications.create(name="x", topic="x")
        assert exc.value.status_code == 500

    def test_relay_applications_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.relay_applications.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_relay_application"

    def test_relay_applications_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_relay_application", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.relay_applications.delete("test-id")
        assert exc.value.status_code == 500

    def test_relay_applications_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.relay_applications.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_relay_application"

    def test_relay_applications_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_relay_application", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.relay_applications.get("test-id")
        assert exc.value.status_code == 500

    def test_relay_applications_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.relay_applications.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_relay_applications"

    def test_relay_applications_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_relay_applications", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.relay_applications.list()
        assert exc.value.status_code == 500

    def test_relay_applications_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.relay_applications.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_relay_application_addresses"

    def test_relay_applications_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric.list_relay_application_addresses", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.relay_applications.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_relay_applications_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.relay_applications.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_relay_application"

    def test_relay_applications_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_relay_application", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.relay_applications.update("test-id")
        assert exc.value.status_code == 500

    def test_resources_assign_domain_application(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.resources.assign_domain_application(
            "test-id", domain_application_id="x"
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.assign_resource_domain_application"

    def test_resources_assign_domain_application_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "fabric.assign_resource_domain_application", 500, {"error": "x"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.assign_domain_application(
                "test-id", domain_application_id="x"
            )
        assert exc.value.status_code == 500

    def test_resources_assign_phone_route(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.resources.assign_phone_route(
            "test-id", phone_route_id="x", handler="calling"
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.assign_resource_phone_route"

    def test_resources_assign_phone_route_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.assign_resource_phone_route", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.assign_phone_route(
                "test-id", phone_route_id="x", handler="calling"
            )
        assert exc.value.status_code == 500

    def test_resources_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.resources.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_resource"

    def test_resources_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_resource", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.delete("test-id")
        assert exc.value.status_code == 500

    def test_resources_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.resources.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_resource"

    def test_resources_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_resource", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.get("test-id")
        assert exc.value.status_code == 500

    def test_resources_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.resources.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_resources"

    def test_resources_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_resources", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.list()
        assert exc.value.status_code == 500

    def test_resources_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.resources.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_resource_addresses"

    def test_resources_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_resource_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.resources.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_sip_addresses_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_addresses.create(
            name="x", calling_handler_resource_id="x"
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric-addresses.create_sip_address"

    def test_sip_addresses_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric-addresses.create_sip_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_addresses.create(
                name="x", calling_handler_resource_id="x"
            )
        assert exc.value.status_code == 500

    def test_sip_addresses_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_addresses.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric-addresses.delete_sip_address"

    def test_sip_addresses_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric-addresses.delete_sip_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_addresses.delete("test-id")
        assert exc.value.status_code == 500

    def test_sip_addresses_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_addresses.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric-addresses.get_sip_address"

    def test_sip_addresses_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric-addresses.get_sip_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_addresses.get("test-id")
        assert exc.value.status_code == 500

    def test_sip_addresses_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_addresses.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric-addresses.list_sip_addresses"

    def test_sip_addresses_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric-addresses.list_sip_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_addresses.list()
        assert exc.value.status_code == 500

    def test_sip_addresses_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_addresses.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "fabric-addresses.update_sip_address"

    def test_sip_addresses_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric-addresses.update_sip_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_addresses.update("test-id")
        assert exc.value.status_code == 500

    def test_sip_endpoints_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_endpoints.create(
            username="x",
            caller_id="x",
            send_as="x",
            ciphers=["AEAD_AES_256_GCM_8"],
            codecs=["PCMU"],
            encryption="required",
            call_handler="default",
            calling_handler_resource_id="x",
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_sip_endpoint"

    def test_sip_endpoints_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_sip_endpoint", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_endpoints.create(
                username="x",
                caller_id="x",
                send_as="x",
                ciphers=["AEAD_AES_256_GCM_8"],
                codecs=["PCMU"],
                encryption="required",
                call_handler="default",
                calling_handler_resource_id="x",
            )
        assert exc.value.status_code == 500

    def test_sip_endpoints_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_endpoints.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_sip_endpoint"

    def test_sip_endpoints_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_sip_endpoint", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_endpoints.delete("test-id")
        assert exc.value.status_code == 500

    def test_sip_endpoints_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_endpoints.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_sip_endpoint"

    def test_sip_endpoints_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_sip_endpoint", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_endpoints.get("test-id")
        assert exc.value.status_code == 500

    def test_sip_endpoints_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_endpoints.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_sip_endpoints"

    def test_sip_endpoints_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_sip_endpoints", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_endpoints.list()
        assert exc.value.status_code == 500

    def test_sip_endpoints_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_endpoints.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_sip_endpoint_addresses"

    def test_sip_endpoints_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_sip_endpoint_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_endpoints.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_sip_endpoints_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_endpoints.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_sip_endpoint"

    def test_sip_endpoints_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_sip_endpoint", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_endpoints.update("test-id")
        assert exc.value.status_code == 500

    def test_sip_gateways_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_gateways.create(
            name="x",
            uri="x",
            encryption="required",
            ciphers=["AEAD_AES_256_GCM_8"],
            codecs=["PCMU"],
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_sip_gateway"

    def test_sip_gateways_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_sip_gateway", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_gateways.create(
                name="x",
                uri="x",
                encryption="required",
                ciphers=["AEAD_AES_256_GCM_8"],
                codecs=["PCMU"],
            )
        assert exc.value.status_code == 500

    def test_sip_gateways_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_gateways.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_sip_gateway"

    def test_sip_gateways_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_sip_gateway", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_gateways.delete("test-id")
        assert exc.value.status_code == 500

    def test_sip_gateways_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_gateways.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_sip_gateway"

    def test_sip_gateways_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_sip_gateway", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_gateways.get("test-id")
        assert exc.value.status_code == 500

    def test_sip_gateways_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_gateways.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_sip_gateways"

    def test_sip_gateways_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_sip_gateways", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_gateways.list()
        assert exc.value.status_code == 500

    def test_sip_gateways_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_gateways.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_sip_gateway_addresses"

    def test_sip_gateways_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_sip_gateway_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_gateways.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_sip_gateways_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_gateways.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "fabric.update_sip_gateway"

    def test_sip_gateways_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_sip_gateway", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.sip_gateways.update("test-id")
        assert exc.value.status_code == 500

    def test_subscribers_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.create(email="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_subscriber"

    def test_subscribers_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_subscriber", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.create(email="x")
        assert exc.value.status_code == 500

    def test_subscribers_create_sip_endpoint(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.create_sip_endpoint(
            "test-id", username="x", password="x"
        )  # noqa: S106
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_subscriber_sip_endpoint"

    def test_subscribers_create_sip_endpoint_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_subscriber_sip_endpoint", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.create_sip_endpoint(
                "test-id", username="x", password="x"
            )  # noqa: S106
        assert exc.value.status_code == 500

    def test_subscribers_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_subscriber"

    def test_subscribers_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_subscriber", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.delete("test-id")
        assert exc.value.status_code == 500

    def test_subscribers_delete_sip_endpoint(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.delete_sip_endpoint("test-id", "test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_subscriber_sip_endpoint"

    def test_subscribers_delete_sip_endpoint_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_subscriber_sip_endpoint", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.delete_sip_endpoint(
                "test-id", "test-id"
            )
        assert exc.value.status_code == 500

    def test_subscribers_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_subscriber"

    def test_subscribers_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_subscriber", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.get("test-id")
        assert exc.value.status_code == 500

    def test_subscribers_get_sip_endpoint(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.get_sip_endpoint("test-id", "test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_subscriber_sip_endpoint"

    def test_subscribers_get_sip_endpoint_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_subscriber_sip_endpoint", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.get_sip_endpoint("test-id", "test-id")
        assert exc.value.status_code == 500

    def test_subscribers_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_subscribers"

    def test_subscribers_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_subscribers", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.list()
        assert exc.value.status_code == 500

    def test_subscribers_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_subscriber_addresses"

    def test_subscribers_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_subscriber_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_subscribers_list_sip_endpoints(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.list_sip_endpoints("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_subscriber_sip_endpoints"

    def test_subscribers_list_sip_endpoints_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_subscriber_sip_endpoints", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.list_sip_endpoints("test-id")
        assert exc.value.status_code == 500

    def test_subscribers_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_subscriber"

    def test_subscribers_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_subscriber", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.update("test-id")
        assert exc.value.status_code == 500

    def test_subscribers_update_sip_endpoint(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.update_sip_endpoint("test-id", "test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "fabric.update_subscriber_sip_endpoint"

    def test_subscribers_update_sip_endpoint_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_subscriber_sip_endpoint", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.subscribers.update_sip_endpoint(
                "test-id", "test-id"
            )
        assert exc.value.status_code == 500

    def test_swml_scripts_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_scripts.create(name="x", contents="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_swml_script"

    def test_swml_scripts_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_swml_script", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_scripts.create(name="x", contents="x")
        assert exc.value.status_code == 500

    def test_swml_scripts_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_scripts.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_swml_script"

    def test_swml_scripts_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_swml_script", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_scripts.delete("test-id")
        assert exc.value.status_code == 500

    def test_swml_scripts_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_scripts.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_swml_script"

    def test_swml_scripts_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_swml_script", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_scripts.get("test-id")
        assert exc.value.status_code == 500

    def test_swml_scripts_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_scripts.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_swml_scripts"

    def test_swml_scripts_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_swml_scripts", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_scripts.list()
        assert exc.value.status_code == 500

    def test_swml_scripts_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_scripts.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_swml_script_addresses"

    def test_swml_scripts_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_swml_script_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_scripts.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_swml_scripts_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_scripts.update("test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "fabric.update_swml_script"

    def test_swml_scripts_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_swml_script", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_scripts.update("test-id")
        assert exc.value.status_code == 500

    def test_swml_webhooks_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_webhooks.create(primary_request_url="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_swml_webhook"

    def test_swml_webhooks_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_swml_webhook", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_webhooks.create(primary_request_url="x")
        assert exc.value.status_code == 500

    def test_swml_webhooks_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_webhooks.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "fabric.delete_swml_webhook"

    def test_swml_webhooks_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.delete_swml_webhook", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_webhooks.delete("test-id")
        assert exc.value.status_code == 500

    def test_swml_webhooks_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_webhooks.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.get_swml_webhook"

    def test_swml_webhooks_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.get_swml_webhook", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_webhooks.get("test-id")
        assert exc.value.status_code == 500

    def test_swml_webhooks_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_webhooks.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_swml_webhooks"

    def test_swml_webhooks_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_swml_webhooks", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_webhooks.list()
        assert exc.value.status_code == 500

    def test_swml_webhooks_list_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_webhooks.list_addresses("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "fabric.list_swml_webhook_addresses"

    def test_swml_webhooks_list_addresses_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.list_swml_webhook_addresses", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_webhooks.list_addresses("test-id")
        assert exc.value.status_code == 500

    def test_swml_webhooks_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.swml_webhooks.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "fabric.update_swml_webhook"

    def test_swml_webhooks_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.update_swml_webhook", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.swml_webhooks.update("test-id")
        assert exc.value.status_code == 500

    def test_tokens_create_embed_token(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.tokens.create_embed_token(token="x")  # noqa: S106
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_embeds_token"

    def test_tokens_create_embed_token_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_embeds_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.tokens.create_embed_token(token="x")  # noqa: S106
        assert exc.value.status_code == 500

    def test_tokens_create_guest_token(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.tokens.create_guest_token(allowed_addresses=["x"])
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_subscriber_guest_token"

    def test_tokens_create_guest_token_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_subscriber_guest_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.tokens.create_guest_token(allowed_addresses=["x"])
        assert exc.value.status_code == 500

    def test_tokens_create_invite_token(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.tokens.create_invite_token(address_id="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_subscriber_invite_token"

    def test_tokens_create_invite_token_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_subscriber_invite_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.tokens.create_invite_token(address_id="x")
        assert exc.value.status_code == 500

    def test_tokens_create_subscriber_token(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.tokens.create_subscriber_token(reference="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.create_subscriber_token"

    def test_tokens_create_subscriber_token_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.create_subscriber_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.tokens.create_subscriber_token(reference="x")
        assert exc.value.status_code == 500

    def test_tokens_refresh_subscriber_token(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.tokens.refresh_subscriber_token(refresh_token="x")  # noqa: S106
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "fabric.refresh_subscriber_token"

    def test_tokens_refresh_subscriber_token_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("fabric.refresh_subscriber_token", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.tokens.refresh_subscriber_token(refresh_token="x")  # noqa: S106
        assert exc.value.status_code == 500
