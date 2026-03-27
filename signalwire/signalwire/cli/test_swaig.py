#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
SWAIG Function CLI Testing Tool

This tool loads an agent application and calls SWAIG functions with comprehensive
simulation of the SignalWire environment. It supports both webhook and DataMap functions.
"""

# CRITICAL: Set environment variable BEFORE any imports to suppress logs for --raw and --dump-swml
import sys
import os
if "--raw" in sys.argv or "--dump-swml" in sys.argv:
    os.environ['SIGNALWIRE_LOG_MODE'] = 'off'

import json
import argparse
import warnings
from pathlib import Path
from typing import Dict, Any, Optional

# Import submodules
from .config import (
    ERROR_MISSING_AGENT, ERROR_MULTIPLE_AGENTS, ERROR_NO_AGENTS,
    ERROR_AGENT_NOT_FOUND, ERROR_FUNCTION_NOT_FOUND, ERROR_CGI_HOST_REQUIRED,
    HELP_DESCRIPTION, HELP_EPILOG_SHORT
)
from .core.argparse_helpers import CustomArgumentParser, parse_function_arguments
from .core.agent_loader import discover_agents_in_file, load_agent_from_file, load_service_from_file
from .core.dynamic_config import apply_dynamic_config
from .simulation.mock_env import ServerlessSimulator, create_mock_request, load_env_file
from .simulation.data_generation import (
    generate_fake_swml_post_data, generate_comprehensive_post_data,
    generate_minimal_post_data
)
from .simulation.data_overrides import apply_overrides, apply_convenience_mappings
from .execution.datamap_exec import execute_datamap_function
from .execution.webhook_exec import execute_external_webhook_function
from .output.swml_dump import handle_dump_swml, setup_output_suppression
from .output.output_formatter import display_agent_tools, format_result


def print_help_platforms():
    """Print detailed help for serverless platform options"""
    print("""
Serverless Platform Configuration Options
========================================

AWS Lambda Configuration:
  --aws-function-name NAME     AWS Lambda function name (overrides default)
  --aws-function-url URL       AWS Lambda function URL (overrides default)
  --aws-region REGION          AWS region (overrides default)
  --aws-api-gateway-id ID      AWS API Gateway ID for API Gateway URLs
  --aws-stage STAGE            AWS API Gateway stage (default: prod)

CGI Configuration:
  --cgi-host HOST              CGI server hostname (required for CGI simulation)
  --cgi-script-name NAME       CGI script name/path (overrides default)
  --cgi-https                  Use HTTPS for CGI URLs
  --cgi-path-info PATH         CGI PATH_INFO value

Google Cloud Platform Configuration:
  --gcp-project ID             Google Cloud project ID (overrides default)
  --gcp-function-url URL       Google Cloud Function URL (overrides default)
  --gcp-region REGION          Google Cloud region (overrides default)
  --gcp-service NAME           Google Cloud service name (overrides default)

Azure Functions Configuration:
  --azure-env ENV              Azure Functions environment (overrides default)
  --azure-function-url URL     Azure Function URL (overrides default)

Examples:
  # AWS Lambda with custom configuration
  swaig-test agent.py --simulate-serverless lambda \\
    --aws-function-name prod-agent \\
    --aws-region us-west-2 \\
    --dump-swml

  # CGI with HTTPS
  swaig-test agent.py --simulate-serverless cgi \\
    --cgi-host example.com \\
    --cgi-https \\
    --exec my_function
""")


def print_help_examples():
    """Print comprehensive usage examples"""
    print("""
Comprehensive Usage Examples
===========================

Basic Function Testing
---------------------
# Test a function with CLI-style arguments
swaig-test agent.py --exec search --query "AI" --limit 5

# Test with verbose output
swaig-test agent.py --verbose --exec search --query "test"

# Legacy JSON syntax (still supported)
swaig-test agent.py search '{"query":"test"}'

SWML Document Generation
-----------------------
# Generate basic SWML
swaig-test agent.py --dump-swml

# Generate SWML with raw JSON output (for piping)
swaig-test agent.py --dump-swml --raw | jq '.'

# Extract specific fields with jq
swaig-test agent.py --dump-swml --raw | jq '.sections.main[1].ai.SWAIG.functions'

# Generate SWML with comprehensive fake data
swaig-test agent.py --dump-swml --fake-full-data

# Customize call configuration
swaig-test agent.py --dump-swml --call-type sip --from-number +15551234567

Multi-Agent Files
----------------
# List available agents
swaig-test multi_agent.py --list-agents

# Use specific agent
swaig-test multi_agent.py --agent-class MattiAgent --list-tools
swaig-test multi_agent.py --agent-class MattiAgent --exec transfer --name sigmond

Dynamic Agent Testing
--------------------
# Test with query parameters
swaig-test dynamic_agent.py --dump-swml --query-params '{"tier":"premium"}'

# Test with headers
swaig-test dynamic_agent.py --dump-swml --header "Authorization=Bearer token"

# Test with custom request body
swaig-test dynamic_agent.py --dump-swml --method POST --body '{"custom":"data"}'

# Combined dynamic configuration
swaig-test dynamic_agent.py --dump-swml \\
  --query-params '{"tier":"premium","region":"eu"}' \\
  --header "X-Customer-ID=12345" \\
  --user-vars '{"preferences":{"language":"es"}}'

Serverless Environment Simulation
--------------------------------
# AWS Lambda simulation
swaig-test agent.py --simulate-serverless lambda --dump-swml
swaig-test agent.py --simulate-serverless lambda --exec my_function --param value

# With environment variables
swaig-test agent.py --simulate-serverless lambda \\
  --env API_KEY=secret \\
  --env DEBUG=1 \\
  --exec my_function

# With environment file
swaig-test agent.py --simulate-serverless lambda \\
  --env-file production.env \\
  --exec my_function

# CGI simulation
swaig-test agent.py --simulate-serverless cgi \\
  --cgi-host example.com \\
  --cgi-https \\
  --exec my_function

# Google Cloud Functions
swaig-test agent.py --simulate-serverless cloud_function \\
  --gcp-project my-project \\
  --exec my_function

# Azure Functions
swaig-test agent.py --simulate-serverless azure_function \\
  --azure-env production \\
  --exec my_function

Advanced Data Overrides
----------------------
# Override specific values
swaig-test agent.py --dump-swml \\
  --override call.state=answered \\
  --override call.timeout=60

# Override with JSON values
swaig-test agent.py --dump-swml \\
  --override-json vars.custom='{"key":"value","nested":{"data":true}}'

# Combine multiple override types
swaig-test agent.py --dump-swml \\
  --call-type sip \\
  --user-vars '{"vip":"true"}' \\
  --header "X-Source=test" \\
  --override call.project_id=my-project \\
  --verbose

Cross-Platform Testing
---------------------
# Test across all platforms
for platform in lambda cgi cloud_function azure_function; do
  echo "Testing $platform..."
  swaig-test agent.py --simulate-serverless $platform \\
    --exec my_function --param value
done

# Compare webhook URLs across platforms
swaig-test agent.py --simulate-serverless lambda --dump-swml | grep web_hook_url
swaig-test agent.py --simulate-serverless cgi --cgi-host example.com --dump-swml | grep web_hook_url
""")


def main():
    """Main entry point for the CLI tool"""
    # Set up suppression early if we're dumping SWML
    if "--dump-swml" in sys.argv:
        setup_output_suppression()
    
    # Check for help sections early
    if "--help-platforms" in sys.argv:
        print_help_platforms()
        sys.exit(0)
    
    if "--help-examples" in sys.argv:
        print_help_examples()
        sys.exit(0)
    
    # Check for --exec and split arguments  
    cli_args = sys.argv[1:]
    function_args_list = []
    exec_function_name = None
    
    if '--exec' in sys.argv:
        exec_index = sys.argv.index('--exec')
        if exec_index + 1 < len(sys.argv):
            exec_function_name = sys.argv[exec_index + 1]
            # CLI args: everything before --exec
            cli_args = sys.argv[1:exec_index]
            # Function args: everything after the function name
            function_args_list = sys.argv[exec_index + 2:]
        else:
            print("Error: --exec requires a function name")
            return 1
    
    # Temporarily modify sys.argv for argparse (exclude --exec and its args)
    original_argv = sys.argv[:]
    sys.argv = [sys.argv[0]] + cli_args
    
    parser = CustomArgumentParser(
        description=HELP_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage="%(prog)s <agent_path> [options]",
        epilog=HELP_EPILOG_SHORT
    )
    
    # Positional arguments
    parser.add_argument(
        "agent_path",
        help="Path to Python file containing the agent"
    )
    
    # Common options
    common = parser.add_argument_group('common options')
    common.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    common.add_argument(
        "--raw",
        action="store_true",
        help="Output raw JSON only (for piping to jq)"
    )
    common.add_argument(
        "--agent-class",
        help="Specify agent class (required if file has multiple agents)"
    )
    common.add_argument(
        "--route",
        help="Specify service by route (e.g., /healthcare, /finance)"
    )
    
    # Actions (choose one)
    actions = parser.add_argument_group('actions (choose one)')
    actions.add_argument(
        "--list-agents",
        action="store_true",
        help="List all agents in file"
    )
    actions.add_argument(
        "--list-tools",
        action="store_true",
        help="List all tools in agent"
    )
    actions.add_argument(
        "--dump-swml",
        action="store_true",
        help="Generate and output SWML document"
    )
    actions.add_argument(
        "--exec",
        metavar="FUNCTION",
        help="Execute function with CLI args (e.g., --exec search --query 'AI')"
    )
    
    # Function execution options
    func_group = parser.add_argument_group('function execution options')
    func_group.add_argument(
        "--custom-data",
        help="JSON string with custom post_data overrides",
        default="{}"
    )
    func_group.add_argument(
        "--minimal",
        action="store_true",
        help="Use minimal post_data for function execution"
    )
    func_group.add_argument(
        "--fake-full-data",
        action="store_true",
        help="Use comprehensive fake post_data"
    )
    
    # SWML generation options
    swml_group = parser.add_argument_group('swml generation options')
    swml_group.add_argument(
        "--call-type",
        choices=["sip", "webrtc"],
        default="webrtc",
        help="Call type (default: webrtc)"
    )
    swml_group.add_argument(
        "--call-direction",
        choices=["inbound", "outbound"],
        default="inbound",
        help="Call direction (default: inbound)"
    )
    swml_group.add_argument(
        "--call-state",
        default="created",
        help="Call state (default: created)"
    )
    swml_group.add_argument(
        "--from-number",
        help="Override from number"
    )
    swml_group.add_argument(
        "--to-extension",
        help="Override to extension"
    )
    
    # Data customization
    data_group = parser.add_argument_group('data customization')
    data_group.add_argument(
        "--user-vars",
        help="JSON string for userVariables"
    )
    data_group.add_argument(
        "--query-params",
        help="JSON string for query parameters"
    )
    data_group.add_argument(
        "--override",
        action="append",
        default=[],
        help="Override value (e.g., --override call.state=answered)"
    )
    data_group.add_argument(
        "--header",
        action="append",
        default=[],
        help="Add HTTP header (e.g., --header Authorization=Bearer token)"
    )
    
    # Serverless simulation (basic)
    serverless_group = parser.add_argument_group('serverless simulation (use --help-platforms for platform options)')
    serverless_group.add_argument(
        "--simulate-serverless",
        choices=["lambda", "cgi", "cloud_function", "azure_function"],
        help="Simulate serverless platform"
    )
    serverless_group.add_argument(
        "--env",
        action="append",
        default=[],
        help="Set environment variable (e.g., --env KEY=VALUE)"
    )
    serverless_group.add_argument(
        "--env-file",
        help="Load environment from file"
    )
    
    # Hidden/advanced options (not shown in main help)
    parser.add_argument("--call-id", help=argparse.SUPPRESS)
    parser.add_argument("--project-id", help=argparse.SUPPRESS)
    parser.add_argument("--space-id", help=argparse.SUPPRESS)
    parser.add_argument("--method", default="POST", help=argparse.SUPPRESS)
    parser.add_argument("--body", help=argparse.SUPPRESS)
    parser.add_argument("--override-json", action="append", default=[], help=argparse.SUPPRESS)
    
    # Platform-specific options (hidden from main help)
    parser.add_argument("--aws-function-name", help=argparse.SUPPRESS)
    parser.add_argument("--aws-function-url", help=argparse.SUPPRESS)
    parser.add_argument("--aws-region", help=argparse.SUPPRESS)
    parser.add_argument("--aws-api-gateway-id", help=argparse.SUPPRESS)
    parser.add_argument("--aws-stage", help=argparse.SUPPRESS)
    parser.add_argument("--cgi-host", help=argparse.SUPPRESS)
    parser.add_argument("--cgi-script-name", help=argparse.SUPPRESS)
    parser.add_argument("--cgi-https", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--cgi-path-info", help=argparse.SUPPRESS)
    parser.add_argument("--gcp-project", help=argparse.SUPPRESS)
    parser.add_argument("--gcp-function-url", help=argparse.SUPPRESS)
    parser.add_argument("--gcp-region", help=argparse.SUPPRESS)
    parser.add_argument("--gcp-service", help=argparse.SUPPRESS)
    parser.add_argument("--azure-env", help=argparse.SUPPRESS)
    parser.add_argument("--azure-function-url", help=argparse.SUPPRESS)
    
    # Help extension options
    parser.add_argument(
        "--help-platforms",
        action="store_true",
        help="Show platform-specific serverless options"
    )
    parser.add_argument(
        "--help-examples",
        action="store_true",
        help="Show comprehensive usage examples"
    )
    
    args = parser.parse_args()
    
    # Restore original sys.argv
    sys.argv = original_argv
    
    # Handle --exec vs positional tool_name
    if exec_function_name:
        args.tool_name = exec_function_name
    else:
        args.tool_name = None
    
    # Validate arguments
    if args.route and args.agent_class:
        parser.error("Cannot specify both --route and --agent-class. Choose one.")
    
    if not args.list_tools and not args.dump_swml and not args.list_agents:
        if not args.tool_name:
            # If no tool_name and no special flags, default to listing tools
            args.list_tools = True
    
    # ===== SERVERLESS SIMULATION SETUP =====
    serverless_simulator = None
    
    if args.simulate_serverless:
        # Validate CGI requirements
        if args.simulate_serverless == 'cgi' and not args.cgi_host:
            parser.error(ERROR_CGI_HOST_REQUIRED)
        
        # Collect environment variable overrides
        env_overrides = {}
        
        # Load from environment file first
        if args.env_file:
            try:
                file_env = load_env_file(args.env_file)
                env_overrides.update(file_env)
                if args.verbose and not args.raw:
                    print(f"Loaded {len(file_env)} environment variables from {args.env_file}")
            except FileNotFoundError as e:
                print(f"Error: {e}")
                return 1
        
        # Apply individual env overrides
        for env_var in args.env:
            if '=' in env_var:
                key, value = env_var.split('=', 1)
                env_overrides[key] = value
        
        # Apply platform-specific overrides
        if args.simulate_serverless == 'lambda':
            if args.aws_function_name:
                env_overrides['AWS_LAMBDA_FUNCTION_NAME'] = args.aws_function_name
            if args.aws_function_url:
                env_overrides['AWS_LAMBDA_FUNCTION_URL'] = args.aws_function_url
            if args.aws_region:
                env_overrides['AWS_REGION'] = args.aws_region
        elif args.simulate_serverless == 'cgi':
            if args.cgi_host:
                env_overrides['HTTP_HOST'] = args.cgi_host
                env_overrides['SERVER_NAME'] = args.cgi_host
            if args.cgi_script_name:
                env_overrides['SCRIPT_NAME'] = args.cgi_script_name
            if args.cgi_https:
                env_overrides['HTTPS'] = 'on'
            if args.cgi_path_info:
                env_overrides['PATH_INFO'] = args.cgi_path_info
        elif args.simulate_serverless == 'cloud_function':
            if args.gcp_project:
                env_overrides['GOOGLE_CLOUD_PROJECT'] = args.gcp_project
            if args.gcp_function_url:
                env_overrides['FUNCTION_URL'] = args.gcp_function_url
            if args.gcp_region:
                env_overrides['GOOGLE_CLOUD_REGION'] = args.gcp_region
            if args.gcp_service:
                env_overrides['K_SERVICE'] = args.gcp_service
        elif args.simulate_serverless == 'azure_function':
            if args.azure_env:
                env_overrides['AZURE_FUNCTIONS_ENVIRONMENT'] = args.azure_env
            if args.azure_function_url:
                env_overrides['AZURE_FUNCTION_URL'] = args.azure_function_url
        
        # Create and activate simulator
        serverless_simulator = ServerlessSimulator(args.simulate_serverless, env_overrides)
        serverless_simulator.activate(args.verbose and not args.raw)
    
    # ===== MAIN EXECUTION =====
    try:
        # Check if agent file exists
        agent_path = Path(args.agent_path)
        if not agent_path.exists():
            print(f"Error: Agent file not found: {args.agent_path}")
            return 1
        
        # Handle --list-agents
        if args.list_agents:
            try:
                agents = discover_agents_in_file(args.agent_path)
                if not agents:
                    print(ERROR_NO_AGENTS.format(file_path=args.agent_path))
                    return 1
                
                print(f"\nAgents found in {args.agent_path}:")
                for agent_info in agents:
                    agent_type = "instance" if agent_info['type'] == 'instance' else "class"
                    print(f"  {agent_info['class_name']} ({agent_type})")
                    if agent_info['type'] == 'instance':
                        print(f"    Name: {agent_info['agent_name']}")
                        print(f"    Route: {agent_info['route']}")
                    if agent_info['description']:
                        # Clean up description
                        desc = agent_info['description'].strip()
                        if desc:
                            # Take first line only
                            desc_lines = desc.split('\n')
                            first_line = desc_lines[0].strip()
                            if first_line:
                                print(f"    Description: {first_line}")
                return 0
            except Exception as e:
                print(f"Error discovering agents: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
                return 1
        
        # Load the agent
        try:
            # Determine which identifier to use
            service_identifier = args.route if args.route else args.agent_class
            prefer_route = bool(args.route)
            
            # Use load_service_from_file which handles both routes and class names
            from signalwire.cli.core.agent_loader import load_service_from_file
            agent = load_service_from_file(args.agent_path, service_identifier, prefer_route)
        except ValueError as e:
            error_msg = str(e)
            if "Multiple agent classes found" in error_msg and args.list_tools and not args.agent_class:
                # When listing tools and multiple agents exist, show all agents with their tools
                try:
                    agents = discover_agents_in_file(args.agent_path)
                    if agents:
                        print(f"\nMultiple agents found in {args.agent_path}:")
                        print("=" * 60)
                        
                        for agent_info in agents:
                            if agent_info['type'] == 'class':
                                print(f"\n{agent_info['class_name']}:")
                                if agent_info['description']:
                                    desc = agent_info['description'].strip().split('\n')[0]
                                    if desc:
                                        print(f"  Description: {desc}")
                                
                                # Try to load this specific agent and show its tools
                                try:
                                    specific_agent = load_agent_from_file(args.agent_path, agent_info['class_name'])
                                    
                                    # Apply dynamic configuration if the agent has it
                                    # Create a basic mock request for dynamic config
                                    try:
                                        basic_mock_request = create_mock_request(
                                            method="POST",
                                            headers={},
                                            query_params={},
                                            body={}
                                        )
                                        apply_dynamic_config(specific_agent, basic_mock_request, verbose=False)
                                    except Exception as dc_error:
                                        if args.verbose:
                                            print(f"    (Warning: Dynamic config failed: {dc_error})")
                                    
                                    functions = specific_agent._tool_registry.get_all_functions() if hasattr(specific_agent, '_tool_registry') else {}
                                    
                                    
                                    if functions:
                                        print(f"  Tools:")
                                        for name, func in functions.items():
                                            if isinstance(func, dict):
                                                description = func.get('description', 'DataMap function')
                                                print(f"    - {name}: {description}")
                                            else:
                                                print(f"    - {name}: {func.description}")
                                    else:
                                        print(f"  Tools: (none)")
                                except Exception as load_error:
                                    print(f"  Tools: (error loading agent: {load_error})")
                                    if args.verbose:
                                        import traceback
                                        traceback.print_exc()
                        
                        print("\n" + "=" * 60)
                        print(f"\nTo use a specific agent, run:")
                        print(f"  swaig-test {args.agent_path} --agent-class <AgentClassName>")
                        print(f"  swaig-test {args.agent_path} --route <route>")
                        return 0
                except Exception as discover_error:
                    print(f"Error discovering agents: {discover_error}")
                    return 1
            elif "Multiple agent classes found" in error_msg:
                print(f"\n{ERROR_MULTIPLE_AGENTS}")
                print(error_msg)
            elif "not found" in error_msg and args.agent_class:
                print(ERROR_AGENT_NOT_FOUND.format(
                    class_name=args.agent_class,
                    file_path=args.agent_path
                ))
            else:
                print(f"Error: {error_msg}")
            return 1
        
        # Create mock request for dynamic configuration
        headers = {}
        for header in args.header:
            if '=' in header:
                key, value = header.split('=', 1)
                headers[key] = value
        
        query_params = {}
        if args.query_params:
            try:
                query_params = json.loads(args.query_params)
            except json.JSONDecodeError as e:
                if not args.raw:
                    print(f"Warning: Invalid JSON in --query-params: {e}")
        
        request_body = {}
        if args.body:
            try:
                request_body = json.loads(args.body)
            except json.JSONDecodeError as e:
                if not args.raw:
                    print(f"Warning: Invalid JSON in --body: {e}")
        
        mock_request = create_mock_request(
            method=args.method,
            headers=headers,
            query_params=query_params,
            body=request_body
        )
        
        # Apply dynamic configuration
        apply_dynamic_config(agent, mock_request, verbose=args.verbose and not args.raw)
        
        # Handle --list-tools
        if args.list_tools:
            display_agent_tools(agent, verbose=args.verbose)
            return 0
        
        # Handle --dump-swml
        if args.dump_swml:
            return handle_dump_swml(agent, args)
        
        # Handle function execution
        if args.tool_name:
            # Get the function
            functions = agent._tool_registry.get_all_functions() if hasattr(agent, '_tool_registry') else {}
            
            if args.tool_name not in functions:
                print(ERROR_FUNCTION_NOT_FOUND.format(function_name=args.tool_name))
                display_agent_tools(agent, verbose=False)
                return 1
            
            func = functions[args.tool_name]
            
            # Parse function arguments
            try:
                function_args = parse_function_arguments(function_args_list, func)
            except ValueError as e:
                print(f"Error parsing arguments: {e}")
                return 1
            
            # Check if this is a DataMap function
            is_datamap = isinstance(func, dict) and 'data_map' in func
            
            # Check if this is an external webhook function
            is_external_webhook = (hasattr(func, 'webhook_url') and 
                                 func.webhook_url and 
                                 hasattr(func, 'is_external') and 
                                 func.is_external)
            
            if is_datamap:
                if args.verbose:
                    print(f"\nCalling DataMap function: {args.tool_name}")
                    print(f"Arguments: {json.dumps(function_args, indent=2)}")
                    print(f"Function type: DataMap (serverless)")
                    print("-" * 60)
                
                # Execute DataMap function
                result = execute_datamap_function(func, function_args, args.verbose)
                print("RESULT:")
                print(format_result(result))
            else:
                # Regular SWAIG function
                if args.verbose:
                    print(f"\nCalling function: {args.tool_name}")
                    print(f"Arguments: {json.dumps(function_args, indent=2)}")
                    if is_external_webhook:
                        print(f"Function type: EXTERNAL webhook")
                        print(f"External URL: {func.webhook_url}")
                    else:
                        print(f"Function type: LOCAL webhook")
                
                # Generate post_data based on options
                if args.minimal:
                    post_data = generate_minimal_post_data(args.tool_name, function_args)
                    if args.custom_data:
                        custom_data = json.loads(args.custom_data)
                        post_data.update(custom_data)
                elif args.fake_full_data or args.custom_data:
                    custom_data = json.loads(args.custom_data) if args.custom_data else None
                    post_data = generate_comprehensive_post_data(args.tool_name, function_args, custom_data)
                else:
                    # Default behavior - minimal data
                    post_data = generate_minimal_post_data(args.tool_name, function_args)
                
                # Apply convenience mappings from CLI args (e.g., --call-id)
                post_data = apply_convenience_mappings(post_data, args)
                
                # Apply explicit overrides
                post_data = apply_overrides(post_data, args.override, args.override_json)
                
                if args.verbose:
                    print(f"Post data: {json.dumps(post_data, indent=2)}")
                    print("-" * 60)
                
                # Call the function
                try:
                    if is_external_webhook:
                        # For external webhook functions, make HTTP request to external service
                        result = execute_external_webhook_function(func, args.tool_name, function_args, post_data, args.verbose)
                    else:
                        # For local webhook functions, call the agent's handler
                        result = agent.on_function_call(args.tool_name, function_args, post_data)
                    
                    print("RESULT:")
                    print(format_result(result))
                    
                    if args.verbose:
                        print(f"\nRaw result type: {type(result).__name__}")
                        print(f"Raw result: {repr(result)}")
                    
                except Exception as e:
                    print(f"Error calling function: {e}")
                    if args.verbose:
                        import traceback
                        traceback.print_exc()
                    return 1
            
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        # Clean up serverless simulation
        if serverless_simulator:
            serverless_simulator.deactivate(args.verbose and not args.raw)
    
    return 0


def console_entry_point():
    """Console script entry point for pip installation"""
    # Check for --dump-swml or --raw BEFORE imports happen
    if "--raw" in sys.argv or "--dump-swml" in sys.argv:
        os.environ['SIGNALWIRE_LOG_MODE'] = 'off'
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())