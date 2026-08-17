"""AUTO-GENERATED REST wire tests for the `projects` namespace — DO NOT EDIT.
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


class TestProjectsWire:
    def test_projects_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.projects.create(name="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "projects.create_subproject"

    def test_projects_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("projects.create_subproject", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.projects.create(name="x")
        assert exc.value.status_code == 500

    def test_projects_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.projects.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "projects.delete_subproject"

    def test_projects_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("projects.delete_subproject", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.projects.delete("test-id")
        assert exc.value.status_code == 500

    def test_projects_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.projects.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "projects.get_project"

    def test_projects_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("projects.get_project", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.projects.get("test-id")
        assert exc.value.status_code == 500

    def test_projects_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.projects.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "projects.list_projects"

    def test_projects_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("projects.list_projects", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.projects.list()
        assert exc.value.status_code == 500

    def test_projects_rotate_signing_key(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.projects.rotate_signing_key("test-id")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "projects.rotate_signing_key"

    def test_projects_rotate_signing_key_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("projects.rotate_signing_key", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.projects.rotate_signing_key("test-id")
        assert exc.value.status_code == 500

    def test_projects_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.projects.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "projects.update_project"

    def test_projects_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("projects.update_project", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.projects.update("test-id")
        assert exc.value.status_code == 500
