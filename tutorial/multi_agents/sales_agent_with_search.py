#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Sales Agent with Knowledge Base - Morgan
A PC building sales specialist with access to product knowledge
"""

from signalwire import AgentBase

class SalesAgentWithSearch(AgentBase):
    def __init__(self):
        super().__init__(
            name="PC Builder Sales Agent - Morgan (Enhanced)",
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
        
        # Define the sales workflow with search integration
        self.prompt_add_section(
            "Your Tasks",
            body="Complete sales process workflow with passion and expertise:",
            bullets=[
                "Greet customers warmly and introduce yourself",
                "Understand their specific PC building requirements",
                "Ask about budget, intended use, and preferences",
                "Use search_sales_knowledge to find relevant product information",
                "Provide knowledgeable recommendations based on search results",
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
        
        # Tool usage instructions
        self.prompt_add_section(
            "Tools Available",
            body="Use these tools to assist customers:",
            bullets=[
                "search_sales_knowledge: Find current product information and build recommendations",
                "Search when customers ask about specific budgets or use cases",
                "Use search results to provide accurate, up-to-date information"
            ]
        )
        
        # Important guidelines
        self.prompt_add_section(
            "Important",
            body="Key guidelines for using knowledge search:",
            bullets=[
                "Always search when customers mention specific budgets",
                "Search for compatibility information when needed",
                "Use search results to support your recommendations",
                "Acknowledge when searching: 'Let me find the perfect options for you'"
            ]
        )
        
        # Configure language and voice
        self.add_language(
            name="English",
            code="en-US",
            voice="rime.marsh"
        )
        
        # Add search capability
        self.add_skill("native_vector_search", {
            "tool_name": "search_sales_knowledge",
            "description": "Search sales and product information",
            "index_file": "tutorial/sales_knowledge.swsearch",
            "count": 3
        })

def main():
    """Main function to run the enhanced agent"""
    agent = SalesAgentWithSearch()
    
    print("Starting PC Builder Sales Agent - Morgan (Enhanced)")
    print("=" * 60)
    print("Agent running at: http://localhost:3000/")
    print("Knowledge base: sales_knowledge.swsearch")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nShutting down agent...")

if __name__ == "__main__":
    main()