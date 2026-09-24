#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

MCP Server Mixin for AgentBase

Exposes @tool decorated functions as an MCP server endpoint at /mcp.
Handles the MCP JSON-RPC 2.0 protocol: initialize, tools/list, tools/call.
"""

import inspect
import logging
from collections.abc import Awaitable
from typing import Any

from signalwire.core._sync_handlers import is_async_callable

logger = logging.getLogger(__name__)


class MCPServerMixin:
    """Mixin that adds MCP server endpoint to an agent"""

    def _mcp_tools(self) -> dict[str, Any]:
        """The agent's tools that this endpoint can run, by name.

        DataMap tools run on SignalWire's servers, and external webhook tools
        run at their own URL, so neither can be called here.
        """
        registry = getattr(
            getattr(self, "_tool_registry", None), "_swaig_functions", {}
        )
        return {
            name: func
            for name, func in registry.items()
            if not isinstance(func, dict) and not getattr(func, "webhook_url", None)
        }

    def _build_mcp_tool_list(self) -> list[Any]:
        """Convert registered @tool functions to MCP tool format"""
        tools: list[dict[str, Any]] = []

        for func in self._mcp_tools().values():
            tool = {
                "name": func.name,
                "description": func.description or func.name,
            }

            # Convert SWAIG parameter format to MCP inputSchema
            if hasattr(func, "_ensure_parameter_structure"):
                tool["inputSchema"] = func._ensure_parameter_structure()
            elif func.parameters:
                tool["inputSchema"] = func.parameters
            else:
                tool["inputSchema"] = {"type": "object", "properties": {}}

            tools.append(tool)

        return tools

    def _mcp_request_runs_sync_code(self, body: dict[str, Any]) -> bool:
        """True when ``body`` is a tools/call for a synchronous handler."""
        if not isinstance(body, dict) or body.get("method") != "tools/call":
            return False
        params = body.get("params")
        name = params.get("name", "") if isinstance(params, dict) else ""
        tool = self._mcp_tools().get(name)
        return tool is not None and not is_async_callable(tool.handler)

    def _handle_mcp_request(
        self, body: dict[str, Any]
    ) -> dict[str, Any] | Awaitable[dict[str, Any]]:
        """Handle a single MCP JSON-RPC 2.0 request

        Returns the response, or, for a tools/call whose handler is
        ``async def``, an awaitable that resolves to it.
        """
        jsonrpc = body.get("jsonrpc", "")
        method = body.get("method", "")
        req_id = body.get("id")
        params = body.get("params", {})

        if jsonrpc != "2.0":
            return self._mcp_error(req_id, -32600, "Invalid JSON-RPC version")

        # Initialize handshake
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": getattr(self, "name", "signalwire-agent"),
                        "version": "1.0.0",
                    },
                },
            }

        # Initialized notification — no response needed
        if method == "notifications/initialized":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        # List tools
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self._build_mcp_tool_list()},
            }

        # Call tool
        if method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})

            tools = self._mcp_tools()
            if tool_name not in tools:
                return self._mcp_error(req_id, -32602, f"Unknown tool: {tool_name}")

            # Build minimal raw_data for the handler
            raw_data = {
                "function": tool_name,
                "argument": {"parsed": [arguments]},
            }

            try:
                # Registered handlers are already bound, so they take
                # (args, raw_data), the same as for /swaig.
                result = tools[tool_name].handler(arguments, raw_data)
            except Exception as e:
                return self._mcp_tool_error(req_id, tool_name, e)

            if inspect.isawaitable(result):
                return self._finish_async_mcp_call(req_id, tool_name, result)
            return self._mcp_tool_result(req_id, result)

        # Ping
        if method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        return self._mcp_error(req_id, -32601, f"Method not found: {method}")

    async def _finish_async_mcp_call(
        self, req_id: str | int | None, tool_name: str, pending: Awaitable[Any]
    ) -> dict[str, Any]:
        """Await an async handler and build its tools/call response."""
        try:
            result = await pending
        except Exception as e:
            return self._mcp_tool_error(req_id, tool_name, e)
        return self._mcp_tool_result(req_id, result)

    @staticmethod
    def _mcp_tool_result(req_id: str | int | None, result: Any) -> dict[str, Any]:
        """Build a tools/call response from a handler's return value."""
        # Extract text from FunctionResult
        response_text = ""
        if hasattr(result, "response"):
            response_text = result.response or ""
        elif isinstance(result, str):
            response_text = result
        elif isinstance(result, dict):
            response_text = result.get("response", str(result))

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": response_text}],
                "isError": False,
            },
        }

    @staticmethod
    def _mcp_tool_error(
        req_id: str | int | None, tool_name: str, error: Exception
    ) -> dict[str, Any]:
        """Build a tools/call response for a handler that raised."""
        logger.error(f"MCP tool call error: {tool_name}: {error}")
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": f"Error: {error!s}"}],
                "isError": True,
            },
        }

    @staticmethod
    def _mcp_error(req_id: str | int | None, code: int, message: str) -> dict[str, Any]:
        """Build a JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": code, "message": message},
        }
