#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Advanced DataMap Features Demo

This example demonstrates all the comprehensive DataMap features including:
- Expressions with test values and patterns
- Advanced webhook features (form_param, input_args_as_params, require_args)
- Post-webhook expressions
- Form parameter encoding
- Choosing a webhook with require_args, and a fallback output
"""

from signalwire.core.data_map import DataMap
from signalwire.core.function_result import FunctionResult


def create_expression_demo():
    """Demonstrate expression-based responses with test values and patterns"""
    return (
        DataMap("command_processor")
        .description("Process user commands with pattern matching")
        .parameter("command", "string", "User command to process", required=True)
        .parameter(
            "target", "string", "Optional target for the command", required=False
        )
        # Expression with pattern matching
        .expression(
            "${args.command}",
            r"^start",
            FunctionResult("Starting process: ${args.target}").add_action(
                "start_process", {"target": "${args.target}"}
            ),
        )
        .expression(
            "${args.command}",
            r"^stop",
            FunctionResult("Stopping process: ${args.target}").add_action(
                "stop_process", {"target": "${args.target}"}
            ),
        )
        .expression(
            "${args.command}",
            r"^status",
            FunctionResult("Checking status of: ${args.target}").add_action(
                "check_status", {"target": "${args.target}"}
            ),
            nomatch_output=FunctionResult(
                "Unknown command: ${args.command}. Try start, stop, or status."
            ),
        )
    )


def create_advanced_webhook_demo():
    """Demonstrate advanced webhook features

    The platform requests one webhook per call: the first whose require_args
    are met. Here the first webhook runs when the AI supplies data to send,
    and the second when it supplies only the action. When the webhook that
    ran fails, the fallback output runs; the platform doesn't try the other.
    """
    return (
        DataMap("advanced_api_tool")
        .description("API tool with advanced webhook features")
        .parameter("action", "string", "Action to perform", required=True)
        .parameter("data", "string", "Data to send", required=False)
        .parameter("format", "string", "Response format", required=False)
        # Requested when there's data to send
        .webhook(
            "POST",
            "https://api.example.com/advanced",
            headers={"Authorization": "Bearer YOUR_TOKEN"},
            input_args_as_params=True,  # The arguments become the body
            require_args=["data"],  # Only when data is provided
            form_param="payload",  # Send the body as one form field
        )
        # Post-webhook expressions pick a reply from the response
        .webhook_expressions(
            [
                {
                    "string": "${status}",
                    "pattern": "^success$",
                    "output": {"response": "Operation completed successfully"},
                },
                {
                    "string": "${error_code}",
                    "pattern": "^(404|500)$",
                    "output": {"response": "API Error: ${error_message}"},
                },
            ]
        )
        # Used when neither expression matches
        .output(FunctionResult("The API returned ${status} for ${input.args.action}"))
        .error_keys(["fault", "exception"])
        # Requested when there's no data: the action goes in the URL
        .webhook(
            "GET",
            "https://api.example.com/simple?q=${enc:args.action}",
            headers={"Accept": "application/json"},
        )
        .output(FunctionResult("Result: ${data}"))
        .error_keys(["error", "fault", "exception"])
        # Used when the webhook that ran fails
        .fallback_output(FunctionResult("The API is unavailable right now"))
    )


def create_form_encoding_demo():
    """Demonstrate form parameter encoding"""
    return (
        DataMap("form_submission_tool")
        .description("Submit form data using form encoding")
        .parameter("name", "string", "User name", required=True)
        .parameter("email", "string", "User email", required=True)
        .parameter("message", "string", "Message content", required=True)
        .webhook(
            "POST",
            "https://forms.example.com/submit",
            # With form_param, the platform sets the form Content-Type itself
            headers={"X-API-Key": "YOUR_API_KEY"},
            form_param="form_data",
        )  # Sends entire JSON as form_data parameter
        .params(
            {
                "name": "${args.name}",
                "email": "${args.email}",
                "message": "${args.message}",
                "timestamp": "@{strftime_tz UTC %Y-%m-%d %H:%M:%S}",
            }
        )
        .output(FunctionResult("Form submitted successfully for ${input.args.name}"))
        .error_keys(["error", "validation_errors"])
    )


def create_array_processing_demo():
    """Demonstrate array processing with foreach"""
    return (
        DataMap("search_results_tool")
        .description("Search and format results from API")
        .parameter("query", "string", "Search query", required=True)
        .parameter("limit", "string", "Maximum results", required=False)
        # A GET's query goes in the URL: params would be a JSON body, and
        # make the request a POST
        .webhook(
            "GET",
            "https://search-api.example.com/search?q=${enc:args.query}&max_results=${enc:args.limit}",
            headers={"Authorization": "Bearer YOUR_SEARCH_TOKEN"},
        )
        .foreach(
            {
                "input_key": "results",
                "output_key": "formatted_results",
                "max": 5,
                "append": "Title: ${this.title}\n${this.summary}\nURL: ${this.url}\n\n",
            }
        )
        .output(
            FunctionResult(
                'Found ${total} results for "${input.args.query}":\n\n${formatted_results}'
            )
        )
        .error_keys(["error"])
    )


def create_conditional_logic_demo():
    """Demonstrate complex conditional logic with expressions and functions"""
    return (
        DataMap("smart_calculator")
        .description("Smart calculator with conditional responses")
        .parameter("expression", "string", "Mathematical expression", required=True)
        .parameter(
            "format", "string", "Output format (simple/detailed)", required=False
        )
        # Check if expression is simple arithmetic
        .expression(
            "${args.expression}",
            r"^\s*\d+\s*[+\-*/]\s*\d+\s*$",
            FunctionResult(
                "Quick calculation: ${args.expression} = @{expr ${args.expression}}"
            ),
        )
        # Check if requesting detailed format
        .expression(
            "${args.format}",
            r"^detailed$",
            FunctionResult().add_action(
                "detailed_calc",
                {
                    "expression": "${args.expression}",
                    "result": "@{expr ${args.expression}}",
                    "timestamp": "@{strftime_tz UTC %Y-%m-%d %H:%M:%S}",
                },
            ),
        )
        # Fallback for complex expressions
        .fallback_output(
            FunctionResult(
                "Expression: ${args.expression}\n"
                + "Result: @{expr ${args.expression}}\n"
                + "Calculated at: @{strftime_tz UTC %Y-%m-%d %H:%M:%S}"
            )
        )
    )


if __name__ == "__main__":
    # Create and display all demo tools
    demos = [
        ("Expression Demo", create_expression_demo()),
        ("Advanced Webhook Demo", create_advanced_webhook_demo()),
        ("Form Encoding Demo", create_form_encoding_demo()),
        ("Array Processing Demo", create_array_processing_demo()),
        ("Conditional Logic Demo", create_conditional_logic_demo()),
    ]

    for name, demo in demos:
        print(f"\n{'=' * 50}")
        print(f"{name}")
        print("=" * 50)

        import json

        print(json.dumps(demo.to_swaig_function(), indent=2))
