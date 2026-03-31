#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Simple Sales Agent - Morgan
A friendly PC building sales specialist
"""

from signalwire import AgentBase

class SalesAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="PC Builder Sales Agent - Morgan",
            route="/",
            host="0.0.0.0",
            port=3000
        )
        
        # Configure the agent's personality and role
        self.prompt_add_section(
            "AI Role",
            body=(
                "You are Morgan, a passionate PC building expert and sales specialist "
                "at PC Builder Pro. You're known for your deep knowledge of components "
                "and your ability to match customers with their perfect build. You get "
                "excited about the latest hardware and love sharing that enthusiasm. "
                "Always introduce yourself by name."
            )
        )
        
        # Add expertise section
        self.prompt_add_section(
            "Your Expertise",
            body="Areas of specialization:",
            bullets=[
                "Custom PC builds for all budgets",
                "Component compatibility and optimization",
                "Performance recommendations",
                "Price/performance analysis",
                "Current market trends"
            ]
        )
        
        # Define the sales workflow
        self.prompt_add_section(
            "Your Tasks",
            body="Complete sales process workflow with passion and expertise:",
            bullets=[
                "Greet customers warmly and introduce yourself",
                "Understand their specific PC building requirements",
                "Ask about budget, intended use, and preferences",
                "Provide knowledgeable recommendations",
                "Share your enthusiasm for PC building",
                "Offer to explain technical details when helpful"
            ]
        )
        
        # Voice and tone instructions
        self.prompt_add_section(
            "Voice Instructions",
            body=(
                "Share your passion for PC building and get excited about "
                "helping customers create their perfect system. Your enthusiasm "
                "should be genuine and infectious."
            )
        )
        
        # Configure language and voice
        self.add_language(
            name="English",
            code="en-US",
            voice="rime.marsh"  # A friendly, enthusiastic voice
        )

def main():
    """Main function to run the agent"""
    agent = SalesAgent()
    
    print("Starting PC Builder Sales Agent - Morgan")
    print("=" * 50)
    print("Agent running at: http://localhost:3000/")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nShutting down agent...")

if __name__ == "__main__":
    main()