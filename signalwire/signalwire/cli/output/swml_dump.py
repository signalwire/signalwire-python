#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Handle SWML document dumping
"""

import sys
import json
import warnings
import argparse
from typing import TYPE_CHECKING
from ..simulation.data_generation import generate_fake_swml_post_data
from ..simulation.data_overrides import apply_convenience_mappings, apply_overrides
from ..simulation.mock_env import create_mock_request
from ..core.dynamic_config import apply_dynamic_config

if TYPE_CHECKING:
    from signalwire.core.agent_base import AgentBase


# Store the original print function for raw mode
original_print = print


def setup_output_suppression():
    """Set up output suppression for SWML dumping"""
    # The central logging system is already configured via environment variable
    # Just suppress any remaining warnings
    warnings.filterwarnings("ignore")
    
    # Capture and suppress print statements
    def suppressed_print(*args, **kwargs):
        # If file is specified (like stderr), allow it
        if 'file' in kwargs and kwargs['file'] is not sys.stdout:
            original_print(*args, **kwargs)
        else:
            # Suppress stdout prints
            pass
    
    # Replace print function globally
    import builtins
    builtins.print = suppressed_print


def handle_dump_swml(agent: 'AgentBase', args: argparse.Namespace) -> int:
    """
    Handle SWML dumping with fake post_data and mock request support
    
    Args:
        agent: The loaded agent instance
        args: Parsed CLI arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    if not args.raw:
        if args.verbose:
            print(f"Agent: {agent.get_name()}")
            print(f"Route: {agent.route}")
            
            # Show loaded skills
            skills = agent.list_skills()
            if skills:
                print(f"Skills: {', '.join(skills)}")
                
            # Show available functions
            functions = agent._tool_registry.get_all_functions() if hasattr(agent, '_tool_registry') else {}
            if functions:
                print(f"Functions: {', '.join(functions.keys())}")
            
            print("-" * 60)
    
    try:
        # Generate fake SWML post_data
        post_data = generate_fake_swml_post_data(
            call_type=args.call_type,
            call_direction=args.call_direction,
            call_state=args.call_state
        )
        
        # Apply convenience mappings from CLI args
        post_data = apply_convenience_mappings(post_data, args)
        
        # Apply explicit overrides
        post_data = apply_overrides(post_data, args.override, args.override_json)
        
        # Parse headers for mock request
        headers = {}
        for header in args.header:
            if '=' in header:
                key, value = header.split('=', 1)
                headers[key] = value
        
        # Parse query params for mock request (separate from userVariables)
        query_params = {}
        if args.query_params:
            try:
                query_params = json.loads(args.query_params)
            except json.JSONDecodeError as e:
                if not args.raw:
                    print(f"Warning: Invalid JSON in --query-params: {e}")
        
        # Parse request body
        request_body = {}
        if args.body:
            try:
                request_body = json.loads(args.body)
            except json.JSONDecodeError as e:
                if not args.raw:
                    print(f"Warning: Invalid JSON in --body: {e}")
        
        # Create mock request object
        mock_request = create_mock_request(
            method=args.method,
            headers=headers,
            query_params=query_params,
            body=request_body
        )
        
        if args.verbose and not args.raw:
            print(f"Using fake SWML post_data:")
            print(json.dumps(post_data, indent=2))
            print(f"\nMock request headers: {dict(mock_request.headers.items())}")
            print(f"Mock request query params: {dict(mock_request.query_params.items())}")
            print(f"Mock request method: {mock_request.method}")
            print("-" * 60)
        
        # Apply dynamic configuration with the mock request
        apply_dynamic_config(agent, mock_request, verbose=args.verbose and not args.raw)
        
        # For dynamic agents, call on_swml_request if available
        if hasattr(agent, 'on_swml_request'):
            try:
                # Dynamic agents expect (request_data, callback_path, request)
                call_id = post_data.get('call', {}).get('call_id', 'test-call-id')
                modifications = agent.on_swml_request(post_data, "/swml", mock_request)
                
                if args.verbose and not args.raw:
                    print(f"Dynamic agent modifications: {modifications}")
                
                # Generate SWML with modifications
                swml_doc = agent._render_swml(call_id, modifications)
            except Exception as e:
                if args.verbose and not args.raw:
                    print(f"Dynamic agent callback failed, falling back to static SWML: {e}")
                # Fall back to static SWML generation
                swml_doc = agent._render_swml()
        else:
            # Static agent - generate SWML normally
            swml_doc = agent._render_swml()
        
        if args.raw:
            # Output only the raw JSON for piping to jq/yq
            original_print(swml_doc)
        else:
            # Output formatted JSON (like raw but pretty-printed)
            try:
                swml_parsed = json.loads(swml_doc)
                original_print(json.dumps(swml_parsed, indent=2))
            except json.JSONDecodeError:
                # If not valid JSON, show raw
                original_print(swml_doc)
        
        return 0
        
    except Exception as e:
        if args.raw:
            # For raw mode, output error to stderr to not interfere with JSON output
            original_print(f"Error generating SWML: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc(file=sys.stderr)
        else:
            print(f"Error generating SWML: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
        return 1