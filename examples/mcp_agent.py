#!/usr/bin/env python3
"""
Example: MCP Integration — Client and Server

This agent demonstrates both MCP features:

1. MCP Server: Exposes @tool functions at /mcp so external MCP clients
   (Claude Desktop, other agents) can discover and invoke them.

2. MCP Client: Connects to an external MCP server to pull in additional
   tools for voice calls. Resources are fetched into global_data for
   use in the system prompt.

Usage:
    python mcp_agent.py

    Then:
    - Point a SignalWire phone number at http://your-server:3000/agent
    - Connect Claude Desktop to http://your-server:3000/agent/mcp
"""

from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult


class MCPAgent(AgentBase):
    def __init__(self):
        super().__init__(name="mcp-agent", route="/agent")

        # ── MCP Server ──────────────────────────────────────────────
        # Adds a /mcp endpoint that speaks JSON-RPC 2.0 (MCP protocol).
        # Any MCP client can connect and use our @tool functions.
        # This does NOT affect the agent's own SWML — it only adds
        # the endpoint for external clients.
        self.enable_mcp_server()

        # ── MCP Client ──────────────────────────────────────────────
        # Connect to an external MCP server. Tools are discovered
        # automatically at call start and added to the AI's tool list.
        # Headers are sent on every request for authentication.
        self.add_mcp_server(
            "https://mcp.example.com/tools",
            headers={
                "Authorization": "Bearer sk-your-mcp-api-key"
            }
        )

        # ── MCP Client with Resources ──────────────────────────────
        # This server also exposes resources (read-only data).
        # With resources=True, data is fetched into global_data at
        # session start. resource_vars substitutes caller info into
        # URI templates (e.g. crm://customer/{caller_id}).
        self.add_mcp_server(
            "https://mcp.example.com/crm",
            headers={
                "Authorization": "Bearer sk-your-crm-key"
            },
            resources=True,
            resource_vars={
                "caller_id": "${caller_id_number}",
                "tenant": "acme-corp"
            }
        )

        # ── Agent Configuration ─────────────────────────────────────
        self.prompt_add_section("Role", body=(
            "You are a helpful customer support agent. "
            "You have access to the customer's profile via global_data. "
            "Use the available tools to look up information and assist the caller."
        ))

        # Reference MCP resource data in the prompt
        self.prompt_add_section("Customer Context", body=(
            "Customer name: ${global_data.customer_name}\n"
            "Account status: ${global_data.account_status}\n"
            "If customer data is not available, ask the caller for their name."
        ))

        self.set_params({
            "attention_timeout": 15000,
            "conscience": "Be helpful and concise.",
        })

    # ── Local Tools ─────────────────────────────────────────────────
    # These are available both as SWAIG webhooks (voice calls) AND
    # as MCP tools (Claude Desktop, other agents).

    @AgentBase.tool(
        "get_weather",
        description="Get the current weather for a location",
        parameters={
            "location": {
                "type": "string",
                "description": "City name or zip code"
            }
        }
    )
    def get_weather(self, args, raw_data):
        """Look up weather — available via both SWAIG and MCP"""
        location = args.get("location", "unknown")
        return SwaigFunctionResult(
            f"Currently 72°F and sunny in {location}."
        )

    @AgentBase.tool(
        "create_ticket",
        description="Create a support ticket for the customer",
        parameters={
            "subject": {
                "type": "string",
                "description": "Ticket subject"
            },
            "description": {
                "type": "string",
                "description": "Detailed description of the issue"
            }
        }
    )
    def create_ticket(self, args, raw_data):
        """Create a support ticket — available via both SWAIG and MCP"""
        subject = args.get("subject", "No subject")
        return SwaigFunctionResult(
            f"Ticket created: '{subject}'. Reference number: TK-12345."
        )


if __name__ == "__main__":
    agent = MCPAgent()
    agent.run()
