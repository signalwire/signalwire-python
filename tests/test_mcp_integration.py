from typing import Any

#!/usr/bin/env python3
"""Tests for MCP server endpoint and add_mcp_server configuration."""

import pytest
from signalwire.core.agent_base import AgentBase
from signalwire.core.function_result import FunctionResult


def _sync_response(agent: "AgentBase", body: dict[str, Any]) -> dict[str, Any]:
    """Call the MCP handler, whose tools here are all synchronous."""
    response = agent._handle_mcp_request(body)
    assert isinstance(response, dict)
    return response


class TestMCPServerMixin:
    """Test the MCP server mixin directly"""

    def _make_agent(self) -> "AgentBase":
        """Create an agent with MCP server enabled and a tool.

        The tool is registered the way an application registers one, so the
        tests exercise the agent's real tool registry. (They once set a
        _swaig_functions attribute that no real agent has, which hid that
        the endpoint listed and called nothing.)
        """
        agent = AgentBase(name="test-mcp", route="/test")
        agent.enable_mcp_server()

        def weather_handler(args: dict[str, Any], raw: dict[str, Any]) -> Any:
            return FunctionResult(f"72F sunny in {args.get('location', 'unknown')}")

        agent.define_tool(
            name="get_weather",
            description="Get the weather for a location",
            parameters={"location": {"type": "string", "description": "City name"}},
            handler=weather_handler,
            required=["location"],
        )

        return agent

    def test_build_tool_list(self) -> None:
        """Tools are converted to MCP format correctly"""
        agent = self._make_agent()
        tools = agent._build_mcp_tool_list()

        assert len(tools) == 1
        assert tools[0]["name"] == "get_weather"
        assert tools[0]["description"] == "Get the weather for a location"
        assert "inputSchema" in tools[0]
        assert tools[0]["inputSchema"]["type"] == "object"
        assert "location" in tools[0]["inputSchema"].get("properties", {})

    def test_initialize_handshake(self) -> None:
        """Initialize returns protocol version and capabilities"""
        agent = self._make_agent()
        resp = _sync_response(
            agent,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"},
                },
            },
        )

        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 1
        assert "result" in resp
        assert resp["result"]["protocolVersion"] == "2025-06-18"
        assert "tools" in resp["result"]["capabilities"]

    def test_initialized_notification(self) -> None:
        """notifications/initialized returns empty result"""
        agent = self._make_agent()
        resp = _sync_response(
            agent, {"jsonrpc": "2.0", "method": "notifications/initialized"}
        )

        assert "result" in resp

    def test_tools_list(self) -> None:
        """tools/list returns registered tools in MCP format"""
        agent = self._make_agent()
        resp = _sync_response(
            agent, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        )

        assert resp["id"] == 2
        tools = resp["result"]["tools"]
        assert len(tools) == 1
        assert tools[0]["name"] == "get_weather"

    def test_tools_call(self) -> None:
        """tools/call invokes the handler and returns content"""
        agent = self._make_agent()
        resp = _sync_response(
            agent,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "get_weather", "arguments": {"location": "Orlando"}},
            },
        )

        assert resp["id"] == 3
        assert resp["result"]["isError"] == False
        content = resp["result"]["content"]
        assert len(content) == 1
        assert content[0]["type"] == "text"
        assert "Orlando" in content[0]["text"]

    def test_tools_call_unknown(self) -> None:
        """tools/call with unknown tool returns error"""
        agent = self._make_agent()
        resp = _sync_response(
            agent,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "nonexistent", "arguments": {}},
            },
        )

        assert "error" in resp
        assert resp["error"]["code"] == -32602
        assert "nonexistent" in resp["error"]["message"]

    def test_unknown_method(self) -> None:
        """Unknown method returns method not found error"""
        agent = self._make_agent()
        resp = _sync_response(
            agent, {"jsonrpc": "2.0", "id": 5, "method": "resources/list", "params": {}}
        )

        assert "error" in resp
        assert resp["error"]["code"] == -32601

    def test_ping(self) -> None:
        """ping returns empty result"""
        agent = self._make_agent()
        resp = _sync_response(agent, {"jsonrpc": "2.0", "id": 6, "method": "ping"})

        assert "result" in resp

    def test_invalid_jsonrpc_version(self) -> None:
        """Non-2.0 version returns error"""
        agent = self._make_agent()
        resp = _sync_response(
            agent, {"jsonrpc": "1.0", "id": 7, "method": "initialize"}
        )

        assert "error" in resp
        assert resp["error"]["code"] == -32600


class TestMCPServerEndpoint:
    """The /mcp endpoint on a real agent: auth, class tools, async and DataMap tools."""

    def _client(self) -> Any:
        import asyncio
        from fastapi.testclient import TestClient
        from signalwire.core.data_map import DataMap

        class WeatherAgent(AgentBase):
            def __init__(self) -> None:
                super().__init__(
                    name="weather", route="/agent", basic_auth=("user", "pass")
                )
                self.enable_mcp_server()
                self.register_swaig_function(
                    DataMap("lookup_remote")
                    .purpose("Runs on SignalWire's servers")
                    .parameter("q", "string", "Query")
                    .webhook("GET", "https://example.com/?q=${args.q}")
                    .output(FunctionResult("done"))
                    .to_swaig_function()
                )

            @AgentBase.tool(
                "get_weather",
                description="Weather",
                parameters={"location": {"type": "string", "description": "City"}},
            )
            def get_weather(
                self, args: dict[str, Any], raw_data: dict[str, Any]
            ) -> FunctionResult:
                return FunctionResult(f"72F in {args.get('location')}")

            @AgentBase.tool(
                "get_forecast",
                description="Forecast",
                parameters={"location": {"type": "string", "description": "City"}},
            )
            async def get_forecast(
                self, args: dict[str, Any], raw_data: dict[str, Any]
            ) -> FunctionResult:
                await asyncio.sleep(0)
                return FunctionResult(f"Rain in {args.get('location')}")

        return TestClient(WeatherAgent().get_app())

    @staticmethod
    def _rpc(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}

    def test_requires_basic_auth(self) -> None:
        client = self._client()
        assert (
            client.post("/agent/mcp", json=self._rpc("tools/list")).status_code == 401
        )
        wrong = client.post(
            "/agent/mcp", json=self._rpc("tools/list"), auth=("user", "nope")
        )
        assert wrong.status_code == 401

    def test_lists_class_tools_but_not_datamap_tools(self) -> None:
        response = self._client().post(
            "/agent/mcp", json=self._rpc("tools/list"), auth=("user", "pass")
        )
        names = sorted(t["name"] for t in response.json()["result"]["tools"])
        assert names == ["get_forecast", "get_weather"]

    def test_calls_a_class_tool(self) -> None:
        response = self._client().post(
            "/agent/mcp",
            auth=("user", "pass"),
            json=self._rpc(
                "tools/call",
                {"name": "get_weather", "arguments": {"location": "Paris"}},
            ),
        )
        assert response.json()["result"] == {
            "content": [{"type": "text", "text": "72F in Paris"}],
            "isError": False,
        }

    def test_calls_an_async_tool(self) -> None:
        response = self._client().post(
            "/agent/mcp",
            auth=("user", "pass"),
            json=self._rpc(
                "tools/call",
                {"name": "get_forecast", "arguments": {"location": "Oslo"}},
            ),
        )
        assert response.json()["result"]["content"][0]["text"] == "Rain in Oslo"

    def test_refuses_a_datamap_tool(self) -> None:
        response = self._client().post(
            "/agent/mcp",
            auth=("user", "pass"),
            json=self._rpc(
                "tools/call", {"name": "lookup_remote", "arguments": {"q": "x"}}
            ),
        )
        assert response.json()["error"]["code"] == -32602


class TestAddMCPServer:
    """Test the add_mcp_server config method"""

    def test_add_mcp_server_basic(self) -> None:
        """Basic MCP server config"""
        agent = AgentBase(name="test", route="/test")
        agent.add_mcp_server("https://mcp.example.com/tools")

        assert len(agent._mcp_servers) == 1
        assert agent._mcp_servers[0]["url"] == "https://mcp.example.com/tools"

    def test_add_mcp_server_with_headers(self) -> None:
        """MCP server with auth headers"""
        agent = AgentBase(name="test", route="/test")
        agent.add_mcp_server(
            "https://mcp.example.com/tools", headers={"Authorization": "Bearer sk-xxx"}
        )

        assert agent._mcp_servers[0]["headers"]["Authorization"] == "Bearer sk-xxx"

    def test_add_mcp_server_with_resources(self) -> None:
        """MCP server with resources enabled"""
        agent = AgentBase(name="test", route="/test")
        agent.add_mcp_server(
            "https://mcp.example.com/crm",
            resources=True,
            resource_vars={"caller_id": "${caller_id_number}"},
        )

        assert agent._mcp_servers[0]["resources"] == True
        assert (
            agent._mcp_servers[0]["resource_vars"]["caller_id"] == "${caller_id_number}"
        )

    def test_add_multiple_servers(self) -> None:
        """Multiple MCP servers"""
        agent = AgentBase(name="test", route="/test")
        agent.add_mcp_server("https://mcp1.example.com")
        agent.add_mcp_server("https://mcp2.example.com")

        assert len(agent._mcp_servers) == 2

    def test_method_chaining(self) -> None:
        """add_mcp_server returns self for chaining"""
        agent = AgentBase(name="test", route="/test")
        result = agent.add_mcp_server("https://mcp.example.com")

        assert result is agent

    def test_enable_mcp_server(self) -> None:
        """enable_mcp_server sets the flag"""
        agent = AgentBase(name="test", route="/test")
        assert agent._mcp_server_enabled == False

        result = agent.enable_mcp_server()
        assert agent._mcp_server_enabled == True
        assert result is agent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
