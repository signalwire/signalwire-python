"""
MCP Gateway Demo

Demonstrates connecting a SignalWire AI agent to MCP (Model Context Protocol)
servers through the mcp_gateway skill. The gateway bridges MCP tools so the
agent can use them as SWAIG functions.

Prerequisites:
    pip install "signalwire-sdk[mcp-gateway]"
    # Start a gateway server: mcp-gateway -c config.json

Environment variables:
    MCP_GATEWAY_URL - URL of the running MCP gateway service (required)
    MCP_GATEWAY_AUTH_TOKEN - Bearer token, or instead:
    MCP_GATEWAY_AUTH_USER - Basic auth username
    MCP_GATEWAY_AUTH_PASSWORD - Basic auth password
    MCP_GATEWAY_SERVICES - Comma-separated MCP services to expose
        (default: every service the gateway offers)

The skill refuses a gateway on a private or loopback address, such as
http://localhost:8080, unless SWML_ALLOW_PRIVATE_URLS=true is set. Set it
only for local development:

    SWML_ALLOW_PRIVATE_URLS=true MCP_GATEWAY_URL=http://localhost:8080 \\
        MCP_GATEWAY_AUTH_USER=... MCP_GATEWAY_AUTH_PASSWORD=... \\
        python examples/mcp_gateway_demo.py

Without MCP_GATEWAY_URL and credentials, the agent starts with no MCP tools
and prints how to configure the gateway.
"""

import os
import sys
from typing import Any

from signalwire import AgentBase


def gateway_params() -> dict[str, Any] | None:
    """The mcp_gateway skill's settings from the environment, or None."""
    url = os.environ.get("MCP_GATEWAY_URL")
    token = os.environ.get("MCP_GATEWAY_AUTH_TOKEN")
    user = os.environ.get("MCP_GATEWAY_AUTH_USER")
    password = os.environ.get("MCP_GATEWAY_AUTH_PASSWORD")
    if not url or not (token or (user and password)):
        return None

    params: dict[str, Any] = {"gateway_url": url}
    if token:
        params["auth_token"] = token
    else:
        params["auth_user"] = user
        params["auth_password"] = password

    services = os.environ.get("MCP_GATEWAY_SERVICES", "")
    names = [name.strip() for name in services.split(",") if name.strip()]
    if names:
        params["services"] = [{"name": name} for name in names]
    return params


class MCPGatewayAgent(AgentBase):
    def __init__(self):
        super().__init__(name="MCP Gateway Agent", route="/mcp-gateway")

        self.add_language("English", "en-US", "inworld.Mark")

        self.prompt_add_section(
            "Role",
            "You are a helpful assistant with access to external tools provided "
            "through MCP servers. Use the available tools to help users accomplish "
            "their tasks.",
        )

        # Connect to the MCP gateway; its tools are discovered automatically
        params = gateway_params()
        if params is None:
            print(
                "MCP gateway not configured, so the agent starts without MCP tools.\n"
                "Set MCP_GATEWAY_URL and either MCP_GATEWAY_AUTH_TOKEN or "
                "MCP_GATEWAY_AUTH_USER and MCP_GATEWAY_AUTH_PASSWORD. A private or "
                "localhost gateway URL also needs SWML_ALLOW_PRIVATE_URLS=true.",
                file=sys.stderr,
            )
            return
        try:
            self.add_skill("mcp_gateway", params)
        except ValueError as exc:
            print(
                f"Could not load the mcp_gateway skill ({exc}), so the agent starts "
                "without MCP tools. Check that the gateway is reachable, and set "
                "SWML_ALLOW_PRIVATE_URLS=true for a private or localhost URL.",
                file=sys.stderr,
            )


if __name__ == "__main__":
    agent = MCPGatewayAgent()
    agent.run()
