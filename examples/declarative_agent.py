#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Declarative Agent Example

This example demonstrates how to create an agent using the declarative PROMPT_SECTIONS 
approach, which allows defining the entire prompt structure as a class attribute.

Key concepts demonstrated:
1. Defining prompts declaratively using class attributes
2. Automatic prompt generation from PROMPT_SECTIONS
3. Different formatting options for prompt sections
4. Multiple approaches to structuring prompt data
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path so we can import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from signalwire import AgentBase
from signalwire.core.function_result import FunctionResult


class DeclarativeAgent(AgentBase):
    """
    A simple agent defined using the declarative PROMPT_SECTIONS approach
    
    Instead of calling set_personality(), add_instruction(), etc. in __init__,
    we define the entire prompt structure as a class attribute.
    
    Benefits of this approach:
    1. Separates prompt definition from agent implementation logic
    2. Makes the prompt structure more visible and maintainable
    3. Allows for easier reuse of prompt templates across agent classes
    4. Reduces the amount of code in the constructor
    """
    
    #------------------------------------------------------------------------
    # DECLARATIVE PROMPT DEFINITION
    # Define the entire prompt structure as a class attribute
    #------------------------------------------------------------------------
    
    # Define the entire prompt structure declaratively as a class attribute
    # This will be automatically processed by AgentBase when the class is instantiated
    PROMPT_SECTIONS = {
        # Simple string sections are rendered as-is
        "Personality": "You are a friendly and helpful AI assistant who responds in a casual, conversational tone.",
        
        # Short sections can be defined with a simple string
        "Goal": "Help users with their questions about time and weather.",
        
        # Lists are automatically rendered as bullet points
        "Instructions": [
            "Be concise and direct in your responses.",
            "If you don't know something, say so clearly.",
            "Use the get_time function when asked about the current time.",
            "Use the get_weather function when asked about the weather."
        ],
        
        # Complex sections can have subsections with their own titles and content
        "Examples": {
            # The main section body
            "body": "Here are examples of how to respond to common requests:",
            # Subsections with their own titles and content
            "subsections": [
                {
                    "title": "Time request",
                    "body": "User: What time is it?\nAssistant: Let me check for you. [call get_time]"
                },
                {
                    "title": "Weather request",
                    "body": "User: What's the weather like in Paris?\nAssistant: Let me check the weather for you. [call get_weather with {\"location\": \"Paris\"}]"
                }
            ]
        }
    }
    
    def __init__(self):
        """
        Initialize the DeclarativeAgent
        
        When using the declarative PROMPT_SECTIONS approach, there's no need to
        manually build the prompt in the constructor. The AgentBase class will
        automatically process the PROMPT_SECTIONS and build the prompt for you.
        """
        #------------------------------------------------------------------------
        # BASIC AGENT CONFIGURATION
        # Set up the HTTP server and other basic settings
        #------------------------------------------------------------------------
        
        # Initialize the agent with a name and route
        # The PROMPT_SECTIONS will be automatically processed
        super().__init__(
            name="declarative",        # Agent identifier used in logs
            route="/declarative",      # HTTP endpoint path
            host="0.0.0.0",            # Listen on all interfaces
            port=3000                  # HTTP port number
        )
        
        # Notice we don't need any prompt building calls here - they're handled
        # automatically by the declarative PROMPT_SECTIONS
        # This is different from the conventional approach using prompt_add_section:
        #   self.prompt_add_section("Personality", body="You are a friendly AI assistant...")
        #   self.prompt_add_section("Goal",        body="Help users with their questions...")
        #   self.prompt_add_section("Instructions", bullets=["Be concise and direct..."])
        #   ...
        
        #------------------------------------------------------------------------
        # POST-PROMPT CONFIGURATION
        # Define what summary information to collect after conversations
        #------------------------------------------------------------------------
        
        # Add a post-prompt for summary
        # This defines the structure of data we want the AI to return
        # after completing a conversation
        self.set_post_prompt("""
        Return a JSON summary of the conversation:
        {
            "topic": "MAIN_TOPIC",
            "satisfied": true/false,
            "follow_up_needed": true/false
        }
        """)
    
    #------------------------------------------------------------------------
    # TOOL DEFINITIONS
    # Define the functions that the AI can use during conversations
    #------------------------------------------------------------------------
    
    @AgentBase.tool(
        name="get_time",
        description="Get the current time",
        parameters={}  # No parameters needed for this function
    )
    def get_time(self, args, raw_data):
        """
        Get the current time
        
        A simple function with no parameters that returns the current time.
        This demonstrates the most basic SWAIG function implementation.
        
        Args:
            args: Empty dictionary (no parameters)
            raw_data: The complete request data
            
        Returns:
            FunctionResult with current time
        """
        # Get the current time
        now = datetime.now()
        # Format it as HH:MM:SS
        formatted_time = now.strftime("%H:%M:%S")
        # Return a result that will be shown to the user
        return FunctionResult(f"The current time is {formatted_time}")
    
    @AgentBase.tool(
        name="get_weather",
        description="Get the current weather for a location",
        parameters={
            "location": {
                "type": "string",
                "description": "The city or location to get weather for"
            }
        }
    )
    def get_weather(self, args, raw_data):
        """
        Get the current weather for a location
        
        This function demonstrates a SWAIG function with parameters.
        In a real implementation, this would call a weather API,
        but here we just return a mock response.
        
        Args:
            args: Dictionary containing the "location" parameter 
            raw_data: The complete request data
            
        Returns:
            FunctionResult with weather information
        """
        # Extract location from the args dictionary
        location = args.get("location", "Unknown location")
        
        # In a real implementation, this would call a weather API
        # For demonstration purposes, we return a mock response
        return FunctionResult(f"It's sunny and 72°F in {location}.")
    
    def on_summary(self, summary, raw_data=None):
        """
        Process the conversation summary
        
        This method is called after a conversation has completed and the
        post-prompt has generated a summary. It allows you to perform
        actions based on the conversation outcome.
        
        Args:
            summary: Dictionary containing the structured summary data
            raw_data: The complete request data (optional)
        """
        # Log the summary with pretty-printing
        print(f"Conversation summary received: {json.dumps(summary, indent=2)}")
        
        # In a real implementation, you might:
        # - Save the summary to a database
        # - Trigger follow-up actions if needed
        # - Analyze conversation patterns


# Alternative example using the POM format directly
class PomFormatAgent(AgentBase):
    """
    An agent using the direct POM format for PROMPT_SECTIONS
    
    This approach uses the raw POM dictionary format directly.
    It's an alternative to the more user-friendly key-value format
    and provides more control over the exact structure of the prompt.
    """
    
    #------------------------------------------------------------------------
    # DIRECT POM FORMAT
    # Define the prompt using the low-level POM dictionary format
    #------------------------------------------------------------------------
    
    # Define the prompt using the direct POM format (list of sections)
    # This format matches the internal representation used by the POM
    # and provides more control over the exact structure
    PROMPT_SECTIONS = [
        {
            "title": "Assistant Role",    # Section title
            "body": "You are a technical support agent for SignalWire products.",
            "numbered": True              # This section will be numbered (1.)
        },
        {
            "title": "Knowledge Base",
            "bullets": [                  # These will be rendered as bullet points
                "You know about SignalWire Voice, Video, and Messaging APIs.",
                "You can help with SWML (SignalWire Markup Language) issues.",
                "You can provide code examples in Python, JavaScript, and Ruby."
            ]
        },
        {
            "title": "Response Format",
            "body": "When providing code examples, use markdown code blocks with the language specified.",
            "subsections": [              # Nested subsection
                {
                    "title": "Example Format",
                    "body": "```python\n# Python example\nfrom signalwire.rest import Client\n```"
                }
            ]
        }
    ]
    
    def __init__(self):
        """
        Initialize the PomFormatAgent
        
        This agent demonstrates the direct POM format, which uses
        the internal representation format rather than the simpler
        key-value format used by DeclarativeAgent.
        """
        super().__init__(
            name="pom_format",          # Agent identifier
            route="/pom_format",        # HTTP endpoint path
            host="0.0.0.0",             # Listen on all interfaces
            port=3001                   # Different port from the first agent
        )


def main():
    #------------------------------------------------------------------------
    # AGENT STARTUP
    # Create and run the declarative agent
    #------------------------------------------------------------------------
    
    # Create and start the agent
    agent = DeclarativeAgent()
    print("\nStarting agent server...")
    print("Note: Works in any deployment mode (server/CGI/Lambda)")
    agent.run()


if __name__ == "__main__":
    main() 