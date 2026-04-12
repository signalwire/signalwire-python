#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Test Agent for MCP Gateway Skill

This agent demonstrates using the MCP Gateway skill to interact with MCP services.
"""

import os
import sys

# Add parent directory to path to import signalwire
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from signalwire import AgentBase


class TestMCPAgent(AgentBase):
    """Test agent with MCP Gateway skill"""
    
    def __init__(self):
        super().__init__(
            name="MCP Test Agent",
            route="/mcp-test"
        )
        
        # Configure the agent
        self.prompt_add_section(
            "Role",
            "You are a helpful assistant with access to MCP services through a gateway. " +
            "You can manage todo lists and perform other tasks through these services."
        )
        
        self.prompt_add_section(
            "Instructions",
            bullets=[
                "Help users manage their todo lists",
                "Demonstrate the MCP gateway capabilities",
                "Explain what you're doing when calling MCP functions",
                "Handle errors gracefully"
            ]
        )
        
        # Add the MCP Gateway skill
        # Configure based on environment or use defaults
        gateway_url = os.getenv("MCP_GATEWAY_URL", "http://localhost:8100")
        auth_user = os.getenv("MCP_GATEWAY_USER", "admin")
        auth_password = os.getenv("MCP_GATEWAY_PASSWORD", "changeme")
        
        self.add_skill("mcp_gateway", {
            "gateway_url": gateway_url,
            "auth_user": auth_user,
            "auth_password": auth_password,
            "services": [
                {
                    "name": "todo",
                    "tools": "*"  # Load all todo tools
                }
            ],
            "session_timeout": 600,
            "tool_prefix": "mcp_",
            "verify_ssl": False  # For testing with self-signed certs
        })
        
        # Add some example usage in the prompt
        self.prompt_add_section(
            "Available MCP Services",
            "You have access to a todo list service with these capabilities:",
            bullets=[
                "Add new todo items with priority levels",
                "List all todos or filter by status",
                "Mark todos as completed",
                "Delete todos",
                "Clear all todos"
            ]
        )


def main():
    """Run the test agent"""
    print("=" * 60)
    print("MCP GATEWAY TEST AGENT")
    print("=" * 60)
    print()
    print("This agent demonstrates the MCP Gateway skill.")
    print("It connects to MCP services through a gateway.")
    print()
    print("Make sure the MCP Gateway is running at:")
    print(f"  {os.getenv('MCP_GATEWAY_URL', 'http://localhost:8100')}")
    print()
    print("Test with swaig-test:")
    print("  swaig-test test/test_agent.py --list-tools")
    print("  swaig-test test/test_agent.py --exec mcp_todo_add_todo --text 'Test item'")
    print("  swaig-test test/test_agent.py --exec mcp_todo_list_todos")
    print()
    print("Starting agent...")
    print("-" * 60)
    
    agent = TestMCPAgent()
    agent.run()


if __name__ == "__main__":
    main()