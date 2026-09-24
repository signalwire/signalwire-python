#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Data Map Demo - Shows how to use DataMap class for various SWAIG data_map patterns

This demo creates an agent with multiple data_map tools showing:
1. Simple API calls (weather)
2. Expression-based pattern matching (file control) 
3. API with array processing (search with foreach)
4. Complex API with auth headers (knowledge search)

Each tool generates SWAIG JSON with data_map instead of webhook URLs,
letting the SignalWire server handle all the REST API calls and processing.
"""

from signalwire import AgentBase
from signalwire.core.data_map import (
    DataMap,
    create_simple_api_tool,
    create_expression_tool,
)
from signalwire.core.function_result import FunctionResult


class DataMapDemoAgent(AgentBase):
    """
    Demo agent showing different data_map patterns
    """

    def __init__(self):
        super().__init__(name="datamap-demo", route="/datamap-demo")
        self.setup()

    def setup(self):
        """Set up the agent with data_map tools"""

        # Add a regular SWAIG function for comparison
        self.define_tool(
            name="echo_test",
            description="A simple echo function for testing",
            parameters={
                "message": {"type": "string", "description": "Message to echo back"},
                "repeat": {
                    "type": "integer",
                    "description": "Number of times to repeat",
                },
            },
            handler=self.echo_handler,
        )

        # 1. Simple weather API - basic pattern
        weather_tool = create_simple_api_tool(
            name="get_weather",
            url="https://api.weather.com/v1/current?key=API_KEY&q=${enc:args.location}",
            response_template="Current weather in ${args.location}: ${current.condition.text}, ${current.temp_f}°F",
            parameters={
                "location": {
                    "type": "string",
                    "description": "City name or location",
                    "required": True,
                }
            },
            error_keys=["error", "message"],
        )

        # 2. Expression-based file control - no API calls
        file_control_tool = (
            DataMap("file_control")
            .description("Control audio/video playback")
            .parameter("command", "string", "Playback command", required=True)
            .parameter("filename", "string", "File to control", required=False)
            .expression(
                "${args.command}",
                r"start.*",
                FunctionResult("Starting playback").add_action(
                    "start_playback", {"file": "${args.filename}"}
                ),
            )
            .expression(
                "${args.command}",
                r"stop.*",
                FunctionResult("Stopping playback").add_action("stop_playback", True),
            )
            .expression(
                "${args.command}",
                r"pause.*",
                FunctionResult("Pausing playback").add_action("pause_playback", True),
            )
            .expression(
                "${args.command}",
                r"resume.*",
                FunctionResult("Resuming playback").add_action("resume_playback", True),
            )
        )

        # 3. Knowledge search with foreach - processes arrays
        knowledge_tool = (
            DataMap("search_knowledge")
            .description("Search knowledge base and return multiple results")
            .parameter("query", "string", "Search query", required=True)
            .parameter("limit", "number", "Max results to return", required=False)
            .webhook(
                "POST",
                "https://api.knowledge.com/search",
                headers={
                    "Authorization": "Bearer YOUR_TOKEN",
                    "Content-Type": "application/json",
                },
            )
            .params({"query": "${args.query}", "limit": "${args.limit}"})
            # Builds one line per result, under "found", from the response's
            # "results" array
            .foreach(
                {
                    "input_key": "results",
                    "output_key": "found",
                    "max": 5,
                    "append": "${this.title}: ${this.summary}\n",
                }
            )
            .output(FunctionResult("Found:\n${found}"))
            .error_keys(["error", "status"])
        )

        # 4. Random joke API - handles array responses differently
        joke_tool = (
            DataMap("get_joke")
            .description("Get a random joke from specific category")
            .parameter(
                "category",
                "string",
                "Joke category",
                enum=["programming", "dad", "general"],
                required=False,
            )
            .webhook(
                "GET", "https://api.jokes.com/random?category=${enc:args.category}"
            )
            .output(FunctionResult("Here's a ${category} joke: ${joke}"))
            .error_keys(["error"])
        )

        # 5. Complex API with multiple webhooks and fallback
        complex_search_tool = (
            DataMap("complex_search")
            .description("Search with fallback APIs")
            .parameter("query", "string", "Search query", required=True)
            .parameter(
                "priority",
                "string",
                "Search priority",
                enum=["fast", "comprehensive"],
                required=False,
            )
            # First try fast API
            .webhook(
                "GET",
                "https://api.fastsearch.com/q?term=${enc:args.query}",
                headers={"X-API-Key": "FAST_KEY"},
            )
            .output(FunctionResult("Top result: ${items[0].title}"))
            # Fallback to comprehensive API if first fails
            .webhook(
                "GET",
                "https://api.comprehensive.com/search?q=${enc:args.query}&detail=full",
                headers={"Authorization": "Bearer COMPREHENSIVE_TOKEN"},
            )
            .foreach(
                {
                    "input_key": "items",
                    "output_key": "found",
                    "max": 5,
                    "append": "${this.title} (score ${this.relevance})\n",
                }
            )
            .output(FunctionResult("Search results:\n${found}"))
            .error_keys(["error", "failed", "unavailable"])
        )

        # Register all tools with the agent
        self.register_data_map_tool(weather_tool)
        self.register_data_map_tool(file_control_tool)
        self.register_data_map_tool(knowledge_tool)
        self.register_data_map_tool(joke_tool)
        self.register_data_map_tool(complex_search_tool)

        # Add some context about the capabilities
        self.prompt_add_section(
            "Available data_map tools for testing:",
            "- get_weather(location): Get current weather for a city",
            "- file_control(command, filename): Control audio/video playback",
            "- search_knowledge(query, limit): Search knowledge base",
            "- get_joke(category): Get random jokes",
            "- complex_search(query, priority): Multi-API search with fallback",
        )

    def register_data_map_tool(self, data_map: DataMap):
        """
        Register a DataMap as a SWAIG function

        Args:
            data_map: DataMap object to register
        """
        # Convert DataMap to SWAIG function definition
        function_def = data_map.to_swaig_function()

        # Register the raw function dictionary directly
        self.register_swaig_function(function_def)

    def echo_handler(self, args, raw_data):
        """Handle echo function calls"""
        message = args.get("message", "")
        repeat = args.get("repeat", 1)
        result = (message + " ") * repeat
        return {"response": f"Echo: {result.strip()}"}


def print_data_map_examples():
    """Print example data_map JSON structures"""

    print("=" * 80)
    print("DATA MAP EXAMPLES - Generated SWAIG Function Definitions")
    print("=" * 80)

    # Simple weather API
    weather = create_simple_api_tool(
        "get_weather",
        "https://api.weather.com/v1/current?key=API_KEY&q=${enc:args.location}",
        "Weather in ${args.location}: ${current.condition.text}, ${current.temp_f}°F",
        parameters={
            "location": {"type": "string", "description": "City name", "required": True}
        },
    )

    print("\n1. Simple API Tool (Weather):")
    print(f"   Generated SWAIG: {weather.to_swaig_function()}")

    # Expression tool — patterns map a test_value to a (regex, FunctionResult) tuple
    patterns = {
        "${args.command}": (
            r"start.*",
            FunctionResult().add_action("start_playback", {"file": "${args.filename}"}),
        ),
    }

    file_control = create_expression_tool(
        "file_control",
        patterns,
        parameters={
            "command": {"type": "string", "description": "Command", "required": True}
        },
    )

    print("\n2. Expression Tool (File Control):")
    print(f"   Generated SWAIG: {file_control.to_swaig_function()}")

    # Complex tool with foreach
    search_tool = (
        DataMap("search_docs")
        .description("Search documentation")
        .parameter("query", "string", "Search query", required=True)
        .webhook(
            "POST",
            "https://api.docs.com/search",
            headers={"Authorization": "Bearer TOKEN"},
        )
        .params({"query": "${args.query}", "limit": 3})
        .foreach(
            {
                "input_key": "results",
                "output_key": "found",
                "max": 3,
                "append": "${this.title}: ${this.summary}\n",
            }
        )
        .output(FunctionResult("Found:\n${found}"))
        .error_keys(["error"])
    )

    print("\n3. Complex Tool (Search with Foreach):")
    print(f"   Generated SWAIG: {search_tool.to_swaig_function()}")

    print("\n" + "=" * 80)
    print("These tools generate SWAIG functions with 'data_map' instead of 'url'")
    print("SignalWire server handles all REST API calls, variable expansion,")
    print("array processing, and response formatting automatically.")
    print("=" * 80)


# Create the agent instance for testing
agent = DataMapDemoAgent()

if __name__ == "__main__":
    # Print examples first
    print_data_map_examples()

    print("\n" + "=" * 80)
    print("All examples above show the pattern:")
    print("SUCCESS: Uses DataMap class with FunctionResult for outputs")
    print("SUCCESS: Generates SWAIG JSON with 'data_map' instead of 'url'")
    print("SUCCESS: SignalWire server handles REST API calls automatically")
    print("SUCCESS: Supports expressions, foreach, webhooks, error handling")
    print("=" * 80)

    print("\nKey benefits of this approach:")
    print("- Familiar FunctionResult pattern for all outputs")
    print("- Method chaining like: DataMap('name').webhook().output().foreach()")
    print("- No webhook servers needed - everything runs on SignalWire")
    print("- Covers all data_map patterns from real examples")
    print("- Progressive complexity: simple helpers + full builder API")

    print("\nThis provides a clean SDK for data_map without reinventing")
    print("the wheel - just extends existing patterns developers know!")
