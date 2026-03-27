#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Joke Agent Example

This agent demonstrates using a raw data_map configuration 
to integrate with the API Ninjas joke API.

Run with: API_NINJAS_KEY=your_api_key python examples/joke_agent.py
"""

import os
import sys
from signalwire import AgentBase


class JokeAgent(AgentBase):
    """Simple agent that can tell jokes using data_map"""
    
    def __init__(self):
        super().__init__(
            name="Joke Agent",
            route="/joke-agent"
        )
        
        # Get API key from environment variable
        api_key = os.environ.get("API_NINJAS_KEY")
        if not api_key:
            print("Error: API_NINJAS_KEY environment variable is required")
            print("Get your free API key from https://api.api-ninjas.com/")
            print("Then run: API_NINJAS_KEY=your_api_key python examples/joke_agent.py")
            sys.exit(1)
        
        # Configure the agent's personality and behavior
        self.prompt_add_section("Personality", body="You are a funny assistant who loves to tell jokes.")
        self.prompt_add_section("Goal", body="Make people laugh with great jokes.")
        self.prompt_add_section("Instructions", bullets=[
            "Use the get_joke function to tell jokes when asked",
            "You can tell either regular jokes or dad jokes",
            "Be enthusiastic about sharing humor"
        ])
        
        # Register the joke function with raw data_map configuration
        self._add_joke_function(api_key)
    
    def _add_joke_function(self, api_key):
        """Add the joke function using raw data_map configuration"""
        joke_function = {
            "function": "get_joke",
            "description": "tell a joke",
            "data_map": {
                "webhooks": [
                    {
                        "url": "https://api.api-ninjas.com/v1/%{args.type}",
                        "headers": {
                            "X-Api-Key": api_key
                        },
                        "output": {
                            "response": "Tell the user: %{array[0].joke}",
                            "action": [
                                {
                                    "SWML": {
                                        "sections": {
                                            "main": [
                                                {
                                                    "set": {
                                                        "dad_joke": "%{array[0].joke}"
                                                    }
                                                }
                                            ]
                                        },
                                        "version": "1.0.0"
                                    }
                                }
                            ]
                        },
                        "error_keys": "error",
                        "method": "GET"
                    }
                ],
                "output": {
                    "response": "Tell the user that the joke service is not working right now and just make up a joke on your own"
                }
            },
            "parameters": {
                "properties": {
                    "type": {
                        "description": "must either be 'jokes' or 'dadjokes'",
                        "type": "string"
                    }
                },
                "type": "object"
            }
        }
        
        # Register the function with the agent
        self.register_swaig_function(joke_function)


def main():
    """Run the joke agent"""
    print("Starting Joke Agent...")
    print("\nThis agent can tell jokes using the API Ninjas service!")
    print("Just ask for a joke and specify either 'jokes' or 'dadjokes' type.")
    print("\nAvailable function:")
    print("  get_joke - Tell a joke (jokes or dadjokes)")
    print("Note: Works in any deployment mode (server/CGI/Lambda)")
    
    agent = JokeAgent()
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nShutting down joke agent...")


if __name__ == "__main__":
    main() 
