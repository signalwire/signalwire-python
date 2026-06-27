"""Full success + error coverage for ``client.fabric.ai_agents`` — the
micro-template for the REST full-coverage build (#56).

Every canonical route gets BOTH:
  - a SUCCESS test: call the real SDK method against the live mock, assert the
    parsed body shape AND the journal entry (method + exact path + matched_route)
    so the on-the-wire URL is exactly what the spec advertises.
  - an ERROR test: arm the mock to return a 4xx/5xx for that endpoint via
    ``mock.push_scenario(endpoint_id, status, body)``, call the SDK method, assert
    the SDK surfaces the error (raises an HTTPError) AND the journal recorded the
    route hit with the error status.

``ai_agents`` is a plain ``FabricResource`` CRUD at /api/fabric/resources/ai_agents:
list / create / get / update (PATCH) / delete, plus list_addresses. This file is the
shape that the rest of the fabric resources (and the other namespaces) replicate.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError


class TestFabricAIAgentsSuccess:
    """Happy-path: each route hit with a 2xx on the exact canonical path."""

    def test_list(self, signalwire_client, mock):
        body = signalwire_client.fabric.ai_agents.list()
        assert isinstance(body, dict)
        assert "data" in body, f"missing 'data' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/resources/ai_agents"
        assert last.matched_route == "fabric.list_ai_agents", (
            f"expected fabric.list_ai_agents, got {last.matched_route!r}"
        )

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.fabric.ai_agents.create(
            name="agent-alpha", prompt="be helpful", agent_id="a1"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/resources/ai_agents"
        assert last.matched_route == "fabric.create_ai_agent", (
            f"expected fabric.create_ai_agent, got {last.matched_route!r}"
        )
        # the request body the SDK serialized is what we sent
        assert last.body and last.body.get("name") == "agent-alpha"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.fabric.ai_agents.get("aa-1001")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/resources/ai_agents/aa-1001"
        assert last.matched_route == "fabric.get_ai_agent", (
            f"expected fabric.get_ai_agent, got {last.matched_route!r}"
        )

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.fabric.ai_agents.update("aa-1001", name="renamed")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.path == "/api/fabric/resources/ai_agents/aa-1001"
        assert last.matched_route == "fabric.update_ai_agent", (
            f"expected fabric.update_ai_agent, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("name") == "renamed"

    def test_delete(self, signalwire_client, mock):
        signalwire_client.fabric.ai_agents.delete("aa-1001")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/fabric/resources/ai_agents/aa-1001"
        assert last.matched_route == "fabric.delete_ai_agent", (
            f"expected fabric.delete_ai_agent, got {last.matched_route!r}"
        )

    def test_list_addresses(self, signalwire_client, mock):
        body = signalwire_client.fabric.ai_agents.list_addresses("aa-1001")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/fabric/resources/ai_agents/aa-1001/addresses"
        assert last.matched_route == "fabric.list_ai_agent_addresses", (
            f"expected fabric.list_ai_agent_addresses, got {last.matched_route!r}"
        )


class TestFabricAIAgentsErrors:
    """Failure path: each route is exercised with a 4xx/5xx the SDK must surface.

    The mock's scenario injection (``mock.push_scenario``) arms the next call to
    the endpoint with the given status/body; on a non-2xx the SDK's transport
    raises ``SignalWireRestError`` (carrying ``.status_code`` + the error body) —
    NOT ``requests.HTTPError``. We assert that exception AND its status_code, and
    the journal still records the route hit with the error status — which is what
    the coverage checker counts as the route's error case.
    """

    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("fabric.list_ai_agents", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "fabric.list_ai_agents"
        assert last.response_status == 500

    def test_create_unprocessable(self, signalwire_client, mock):
        # 422 = server-side rejection. The client signature enforces the spec-required
        # fields, so we send a complete body and the armed scenario returns the 422
        # (modelling a server-side validation failure, e.g. a bad field value).
        mock.push_scenario("fabric.create_ai_agent", 422, {"error": "unprocessable"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.create(
                name="x", prompt="p", agent_id="a1"
            )
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "fabric.create_ai_agent"
        assert last.response_status == 422

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("fabric.get_ai_agent", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.get_ai_agent"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario("fabric.update_ai_agent", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.update("missing", name="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.update_ai_agent"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("fabric.delete_ai_agent", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.delete_ai_agent"
        assert last.response_status == 404

    def test_list_addresses_not_found(self, signalwire_client, mock):
        mock.push_scenario("fabric.list_ai_agent_addresses", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.ai_agents.list_addresses("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.list_ai_agent_addresses"
        assert last.response_status == 404
