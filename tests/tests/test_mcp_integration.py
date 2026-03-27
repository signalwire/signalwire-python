#!/usr/bin/env python3
"""Tests for MCP server endpoint and add_mcp_server configuration."""

import json
import pytest
from signalwire import AgentBase
from signalwire.core.function_result import FunctionResult
from signalwire.core.mixins.mcp_server_mixin import MCPServerMixin


class TestMCPServerMixin:
    """Test the MCP server mixin directly"""

    def _make_agent(self):
        """Create an agent with MCP server enabled and a tool"""
        agent = AgentBase(name="test-mcp", route="/test")
        agent._mcp_server_enabled = True

        # Register a tool manually for testing
        from signalwire.core.swaig_function import SWAIGFunction

        def weather_handler(agent_self, args, raw):
            return FunctionResult(f"72F sunny in {args.get('location', 'unknown')}")

        func = SWAIGFunction(
            name="get_weather",
            handler=weather_handler,
            description="Get the weather for a location",
            parameters={
                "location": {"type": "string", "description": "City name"}
            },
            required=["location"]
        )
        agent._swaig_functions = {"get_weather": func}

        return agent

    def test_build_tool_list(self):
        """Tools are converted to MCP format correctly"""
        agent = self._make_agent()
        tools = agent._build_mcp_tool_list()

        assert len(tools) == 1
        assert tools[0]["name"] == "get_weather"
        assert tools[0]["description"] == "Get the weather for a location"
        assert "inputSchema" in tools[0]
        assert tools[0]["inputSchema"]["type"] == "object"
        assert "location" in tools[0]["inputSchema"].get("properties", {})

    def test_initialize_handshake(self):
        """Initialize returns protocol version and capabilities"""
        agent = self._make_agent()
        resp = agent._handle_mcp_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        })

        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 1
        assert "result" in resp
        assert resp["result"]["protocolVersion"] == "2025-06-18"
        assert "tools" in resp["result"]["capabilities"]

    def test_initialized_notification(self):
        """notifications/initialized returns empty result"""
        agent = self._make_agent()
        resp = agent._handle_mcp_request({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })

        assert "result" in resp

    def test_tools_list(self):
        """tools/list returns registered tools in MCP format"""
        agent = self._make_agent()
        resp = agent._handle_mcp_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        })

        assert resp["id"] == 2
        tools = resp["result"]["tools"]
        assert len(tools) == 1
        assert tools[0]["name"] == "get_weather"

    def test_tools_call(self):
        """tools/call invokes the handler and returns content"""
        agent = self._make_agent()
        resp = agent._handle_mcp_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_weather",
                "arguments": {"location": "Orlando"}
            }
        })

        assert resp["id"] == 3
        assert resp["result"]["isError"] == False
        content = resp["result"]["content"]
        assert len(content) == 1
        assert content[0]["type"] == "text"
        assert "Orlando" in content[0]["text"]

    def test_tools_call_unknown(self):
        """tools/call with unknown tool returns error"""
        agent = self._make_agent()
        resp = agent._handle_mcp_request({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "nonexistent", "arguments": {}}
        })

        assert "error" in resp
        assert resp["error"]["code"] == -32602
        assert "nonexistent" in resp["error"]["message"]

    def test_unknown_method(self):
        """Unknown method returns method not found error"""
        agent = self._make_agent()
        resp = agent._handle_mcp_request({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "resources/list",
            "params": {}
        })

        assert "error" in resp
        assert resp["error"]["code"] == -32601

    def test_ping(self):
        """ping returns empty result"""
        agent = self._make_agent()
        resp = agent._handle_mcp_request({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "ping"
        })

        assert "result" in resp

    def test_invalid_jsonrpc_version(self):
        """Non-2.0 version returns error"""
        agent = self._make_agent()
        resp = agent._handle_mcp_request({
            "jsonrpc": "1.0",
            "id": 7,
            "method": "initialize"
        })

        assert "error" in resp
        assert resp["error"]["code"] == -32600


class TestAddMCPServer:
    """Test the add_mcp_server config method"""

    def test_add_mcp_server_basic(self):
        """Basic MCP server config"""
        agent = AgentBase(name="test", route="/test")
        agent.add_mcp_server("https://mcp.example.com/tools")

        assert len(agent._mcp_servers) == 1
        assert agent._mcp_servers[0]["url"] == "https://mcp.example.com/tools"

    def test_add_mcp_server_with_headers(self):
        """MCP server with auth headers"""
        agent = AgentBase(name="test", route="/test")
        agent.add_mcp_server(
            "https://mcp.example.com/tools",
            headers={"Authorization": "Bearer sk-xxx"}
        )

        assert agent._mcp_servers[0]["headers"]["Authorization"] == "Bearer sk-xxx"

    def test_add_mcp_server_with_resources(self):
        """MCP server with resources enabled"""
        agent = AgentBase(name="test", route="/test")
        agent.add_mcp_server(
            "https://mcp.example.com/crm",
            resources=True,
            resource_vars={"caller_id": "${caller_id_number}"}
        )

        assert agent._mcp_servers[0]["resources"] == True
        assert agent._mcp_servers[0]["resource_vars"]["caller_id"] == "${caller_id_number}"

    def test_add_multiple_servers(self):
        """Multiple MCP servers"""
        agent = AgentBase(name="test", route="/test")
        agent.add_mcp_server("https://mcp1.example.com")
        agent.add_mcp_server("https://mcp2.example.com")

        assert len(agent._mcp_servers) == 2

    def test_method_chaining(self):
        """add_mcp_server returns self for chaining"""
        agent = AgentBase(name="test", route="/test")
        result = agent.add_mcp_server("https://mcp.example.com")

        assert result is agent

    def test_enable_mcp_server(self):
        """enable_mcp_server sets the flag"""
        agent = AgentBase(name="test", route="/test")
        assert agent._mcp_server_enabled == False

        result = agent.enable_mcp_server()
        assert agent._mcp_server_enabled == True
        assert result is agent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
