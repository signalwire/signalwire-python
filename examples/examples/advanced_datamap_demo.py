#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

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
- Fallback chains
"""

from signalwire.core.data_map import DataMap
from signalwire.core.function_result import FunctionResult

def create_expression_demo():
    """Demonstrate expression-based responses with test values and patterns"""
    return (DataMap('command_processor')
        .description('Process user commands with pattern matching')
        .parameter('command', 'string', 'User command to process', required=True)
        .parameter('target', 'string', 'Optional target for the command', required=False)
        
        # Expression with pattern matching
        .expression('${args.command}', r'^start', 
                   FunctionResult('Starting process: ${args.target}').add_action('start_process', {'target': '${args.target}'}))
        .expression('${args.command}', r'^stop', 
                   FunctionResult('Stopping process: ${args.target}').add_action('stop_process', {'target': '${args.target}'}))
        .expression('${args.command}', r'^status', 
                   FunctionResult('Checking status of: ${args.target}').add_action('check_status', {'target': '${args.target}'}),
                   nomatch_output=FunctionResult('Unknown command: ${args.command}. Try start, stop, or status.'))
    )

def create_advanced_webhook_demo():
    """Demonstrate advanced webhook features"""
    return (DataMap('advanced_api_tool')
        .description('API tool with advanced webhook features')
        .parameter('action', 'string', 'Action to perform', required=True)
        .parameter('data', 'string', 'Data to send', required=False)
        .parameter('format', 'string', 'Response format', required=False)
        
        # Primary API with all advanced features
        .webhook('POST', 'https://api.example.com/advanced',
                headers={
                    'Authorization': 'Bearer ${token}',
                    'User-Agent': 'SignalWire-Agent/1.0'
                },
                input_args_as_params=True,  # Merge function args into params
                require_args=['action'],    # Only execute if action is provided
                form_param='payload')       # Send as form data
        
        # Add post-webhook expressions
        .webhook_expressions([
            {
                "string": "${response.status}",
                "pattern": "^success$",
                "output": {"response": "Operation completed successfully"}
            },
            {
                "string": "${response.error_code}",
                "pattern": "^(404|500)$",
                "output": {"response": "API Error: ${response.error_message}"}
            }
        ])
        
        # Fallback API without form encoding
        .webhook('GET', 'https://backup-api.example.com/simple',
                headers={'Accept': 'application/json'})
        .params({'q': '${args.action}'})
        .output(FunctionResult('Backup result: ${response.data}'))
        
        # Global fallback
        .fallback_output(FunctionResult('All APIs are currently unavailable'))
        .global_error_keys(['error', 'fault', 'exception'])
    )

def create_form_encoding_demo():
    """Demonstrate form parameter encoding"""
    return (DataMap('form_submission_tool')
        .description('Submit form data using form encoding')
        .parameter('name', 'string', 'User name', required=True)
        .parameter('email', 'string', 'User email', required=True)
        .parameter('message', 'string', 'Message content', required=True)
        
        .webhook('POST', 'https://forms.example.com/submit',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-API-Key': '${api_key}'
                },
                form_param='form_data')  # Sends entire JSON as form_data parameter
        .params({
            'name': '${args.name}',
            'email': '${args.email}',
            'message': '${args.message}',
            'timestamp': '@{strftime_tz UTC %Y-%m-%d %H:%M:%S}'
        })
        .output(FunctionResult('Form submitted successfully for ${args.name}'))
        .error_keys(['error', 'validation_errors'])
    )

def create_array_processing_demo():
    """Demonstrate array processing with foreach"""
    return (DataMap('search_results_tool')
        .description('Search and format results from API')
        .parameter('query', 'string', 'Search query', required=True)
        .parameter('limit', 'string', 'Maximum results', required=False)
        
        .webhook('GET', 'https://search-api.example.com/search',
                headers={'Authorization': 'Bearer ${search_token}'})
        .params({
            'q': '${args.query}',
            'max_results': '@{expr ${args.limit} > 10 ? 10 : ${args.limit}}'
        })
        .foreach({
            "input_key": "results",
            "output_key": "formatted_results",
            "max": 5,
            "append": "Title: ${this.title}\n${this.summary}\nURL: ${this.url}\n\n"
        })
        .output(FunctionResult('Found @{expr ${response.total}} results for "${args.query}":\n\n${formatted_results}'))
        .error_keys(['error'])
    )

def create_conditional_logic_demo():
    """Demonstrate complex conditional logic with expressions and functions"""
    return (DataMap('smart_calculator')
        .description('Smart calculator with conditional responses')
        .parameter('expression', 'string', 'Mathematical expression', required=True)
        .parameter('format', 'string', 'Output format (simple/detailed)', required=False)
        
        # Check if expression is simple arithmetic
        .expression('${args.expression}', r'^\s*\d+\s*[+\-*/]\s*\d+\s*$',
                   FunctionResult('Quick calculation: ${args.expression} = @{expr ${args.expression}}'))
        
        # Check if requesting detailed format
        .expression('${args.format}', r'^detailed$',
                   FunctionResult().add_action('detailed_calc', {
                       'expression': '${args.expression}',
                       'result': '@{expr ${args.expression}}',
                       'timestamp': '@{strftime_tz UTC %Y-%m-%d %H:%M:%S}'
                   }))
        
        # Fallback for complex expressions
        .fallback_output(FunctionResult(
            'Expression: ${args.expression}\n' +
            'Result: @{expr ${args.expression}}\n' +
            'Calculated at: @{strftime_tz UTC %Y-%m-%d %H:%M:%S}'
        ))
    )

if __name__ == "__main__":
    # Create and display all demo tools
    demos = [
        ("Expression Demo", create_expression_demo()),
        ("Advanced Webhook Demo", create_advanced_webhook_demo()),
        ("Form Encoding Demo", create_form_encoding_demo()),
        ("Array Processing Demo", create_array_processing_demo()),
        ("Conditional Logic Demo", create_conditional_logic_demo())
    ]
    
    for name, demo in demos:
        print(f"\n{'='*50}")
        print(f"{name}")
        print('='*50)
        
        import json
        print(json.dumps(demo.to_swaig_function(), indent=2)) 