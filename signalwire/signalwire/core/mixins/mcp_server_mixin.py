#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

MCP Server Mixin for AgentBase

Exposes @tool decorated functions as an MCP server endpoint at /mcp.
Handles the MCP JSON-RPC 2.0 protocol: initialize, tools/list, tools/call.
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MCPServerMixin:
    """Mixin that adds MCP server endpoint to an agent"""

    def _build_mcp_tool_list(self) -> list:
        """Convert registered @tool functions to MCP tool format"""
        tools = []

        if not hasattr(self, '_swaig_functions'):
            return tools

        for func in self._swaig_functions.values():
            tool = {
                "name": func.name,
                "description": func.description or func.name,
            }

            # Convert SWAIG parameter format to MCP inputSchema
            if hasattr(func, '_ensure_parameter_structure'):
                tool["inputSchema"] = func._ensure_parameter_structure()
            elif func.parameters:
                tool["inputSchema"] = func.parameters
            else:
                tool["inputSchema"] = {
                    "type": "object",
                    "properties": {}
                }

            tools.append(tool)

        return tools

    def _handle_mcp_request(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a single MCP JSON-RPC 2.0 request"""
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
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": getattr(self, 'name', 'signalwire-agent'),
                        "version": "1.0.0"
                    }
                }
            }

        # Initialized notification — no response needed
        if method == "notifications/initialized":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        # List tools
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": self._build_mcp_tool_list()
                }
            }

        # Call tool
        if method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})

            if not hasattr(self, '_swaig_functions') or tool_name not in self._swaig_functions:
                return self._mcp_error(req_id, -32602, f"Unknown tool: {tool_name}")

            func = self._swaig_functions[tool_name]

            try:
                # Build minimal raw_data for the handler
                raw_data = {
                    "function": tool_name,
                    "argument": {"parsed": [arguments]},
                }

                result = func.handler(self, arguments, raw_data)

                # Extract text from FunctionResult
                response_text = ""
                if hasattr(result, 'response'):
                    response_text = result.response or ""
                elif isinstance(result, str):
                    response_text = result
                elif isinstance(result, dict):
                    response_text = result.get("response", str(result))

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": response_text}
                        ],
                        "isError": False
                    }
                }
            except Exception as e:
                logger.error(f"MCP tool call error: {tool_name}: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": f"Error: {str(e)}"}
                        ],
                        "isError": True
                    }
                }

        # Ping
        if method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        return self._mcp_error(req_id, -32601, f"Method not found: {method}")

    @staticmethod
    def _mcp_error(req_id, code: int, message: str) -> Dict[str, Any]:
        """Build a JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": code,
                "message": message
            }
        }
