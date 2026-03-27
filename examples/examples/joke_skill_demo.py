#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Joke Skill Demo - Using the modular skills system with DataMap

This demo shows how to use the joke skill which integrates with API Ninjas
using DataMap for serverless execution. Compare this with the raw joke_agent.py
example to see the benefits of the skills system.

Run with: API_NINJAS_KEY=your_api_key python examples/joke_skill_demo.py
"""

import os
import sys
from signalwire import AgentBase


class JokeSkillAgent(AgentBase):
    """Demo agent using the joke skill"""
    
    def __init__(self):
        super().__init__(
            name="Joke Skill Demo Agent",
            route="/joke-skill-demo"
        )
        
        # Get API key from environment variable
        api_key = os.environ.get("API_NINJAS_KEY")
        if not api_key:
            print("Error: API_NINJAS_KEY environment variable is required")
            print("Get your free API key from https://api.api-ninjas.com/")
            print("Then run: API_NINJAS_KEY=your_api_key python examples/joke_skill_demo.py")
            sys.exit(1)
        
        # Configure the agent's personality
        self.prompt_add_section("Personality", body="You are a cheerful comedian who loves sharing jokes and making people laugh.")
        self.prompt_add_section("Goal", body="Entertain users with great jokes and spread joy.")
        self.prompt_add_section("Instructions", bullets=[
            "When users ask for jokes, use your joke functions to provide them",
            "Be enthusiastic and fun in your responses", 
            "You can tell both regular jokes and dad jokes"
        ])
        
        # Add joke skill with API key from environment
        self.add_skill("joke", {
            "api_key": api_key
        })
        
        # Optional: Add multiple joke instances for different types
        # self.add_skill("joke", {
        #     "api_key": api_key,
        #     "tool_name": "get_dad_joke",
        #     "default_joke_type": "dadjokes"
        # })


def main():
    """Run the joke skill demo agent"""
    print("=" * 60)
    print("JOKE SKILL DEMO - Using Modular Skills System")
    print("=" * 60)
    print("\nThis agent demonstrates:")
    print("• Using the joke skill with the modular skills system")
    print("• DataMap integration for serverless API execution")
    print("• Automatic skill discovery and registration")
    print("• No custom webhook endpoints required")
    
    print("\nBenefits of Skills vs Raw DataMap:")
    print("• One-liner integration: agent.add_skill('joke', config)")
    print("• Automatic validation and error handling")
    print("• Reusable across multiple agents")
    print("• Built-in documentation and hints")
    print("• Standardized configuration interface")
    
    print("\nAPI Key Setup:")
    print("1. Sign up at https://api.api-ninjas.com/")
    print("2. Get your free API key")
    print("3. Set environment variable: export API_NINJAS_KEY=your_api_key")
    print("4. Or run with: API_NINJAS_KEY=your_api_key python examples/joke_skill_demo.py")
    
    print("\nStarting agent...")
    print("Ask for jokes like:")
    print("• 'Tell me a joke'")
    print("• 'I want to hear a dad joke'")
    print("• 'Make me laugh!'")
    
    agent = JokeSkillAgent()
    
    try:
        agent.run(host="0.0.0.0", port=3000)
    except KeyboardInterrupt:
        print("\nShutting down joke skill demo agent...")


if __name__ == "__main__":
    main() 