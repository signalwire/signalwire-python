#!/usr/bin/env python3
"""
Test BedrockAgent as a SWML server
"""

from signalwire import BedrockAgent

# Create a Bedrock agent
agent = BedrockAgent(
    name="bedrock_server",
    system_prompt="You are a helpful AI assistant.",
    voice_id="inworld.Mark",
)


# Add a simple tool
@agent.tool
def hello_world(name: str = "World"):
    """Say hello to someone"""
    return f"Hello, {name}!"


print("Starting BedrockAgent server...")
print("Route: /bedrock")
print("URL: http://localhost:3000/bedrock")
print("Auth: dev:w00t")
print("\nTo test:")
print("  curl -u dev:w00t http://localhost:3000/bedrock")
print("  swaig-test examples/bedrock_server_test.py --list")
print("\nPress Ctrl+C to stop")

if __name__ == "__main__":
    agent.run()
