#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Custom argument parsing and function argument parsing
"""

import sys
import argparse
from typing import List, Dict, Any


class CustomArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser with better error handling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._suppress_usage = False
    
    def _print_message(self, message, file=None):
        """Override to suppress usage output for specific errors"""
        if self._suppress_usage:
            return
        super()._print_message(message, file)
    
    def error(self, message):
        """Override error method to provide user-friendly error messages"""
        if "required" in message.lower() and "agent_path" in message:
            self._suppress_usage = True
            print("Error: Missing required argument.")
            print()
            print(f"Usage: {self.prog} <agent_path> [options]")
            print()
            print("Examples:")
            print(f"  {self.prog} examples/my_agent.py --list-tools")
            print(f"  {self.prog} examples/my_agent.py --dump-swml")
            print(f"  {self.prog} examples/my_agent.py --exec my_function --param value")
            print()
            print(f"For full help: {self.prog} --help")
            sys.exit(2)
        else:
            # For other errors, use the default behavior
            super().error(message)
    
    def print_usage(self, file=None):
        """Override print_usage to suppress output when we want custom error handling"""
        if self._suppress_usage:
            return
        super().print_usage(file)
    
    def parse_args(self, args=None, namespace=None):
        """Override parse_args to provide custom error handling for missing arguments"""
        # Check if no arguments provided (just the program name)
        if args is None:
            args = sys.argv[1:]
        
        # If no arguments provided, show custom error
        if not args:
            print("Error: Missing required argument.")
            print()
            print(f"Usage: {self.prog} <agent_path> [options]")
            print()
            print("Examples:")
            print(f"  {self.prog} examples/my_agent.py --list-tools")
            print(f"  {self.prog} examples/my_agent.py --dump-swml")
            print(f"  {self.prog} examples/my_agent.py --exec my_function --param value")
            print()
            print(f"For full help: {self.prog} --help")
            sys.exit(2)
        
        # Otherwise, use default parsing
        return super().parse_args(args, namespace)


def parse_function_arguments(function_args_list: List[str], func_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse function arguments from command line with type coercion based on schema
    
    Args:
        function_args_list: List of command line arguments after --args
        func_schema: Function schema with parameter definitions
        
    Returns:
        Dictionary of parsed function arguments
    """
    parsed_args = {}
    i = 0
    
    # Get parameter schema
    parameters = {}
    required_params = []
    
    if isinstance(func_schema, dict):
        # DataMap function
        if 'parameters' in func_schema:
            params = func_schema['parameters']
            if 'properties' in params:
                parameters = params['properties']
                required_params = params.get('required', [])
            else:
                parameters = params
        else:
            parameters = func_schema
    else:
        # Regular SWAIG function
        if hasattr(func_schema, 'parameters') and func_schema.parameters:
            params = func_schema.parameters
            if 'properties' in params:
                parameters = params['properties']
                required_params = params.get('required', [])
            else:
                parameters = params
    
    # Parse arguments
    while i < len(function_args_list):
        arg = function_args_list[i]
        
        if arg.startswith('--'):
            param_name = arg[2:]  # Remove --
            
            # Convert kebab-case to snake_case for parameter lookup
            param_key = param_name.replace('-', '_')
            
            # Check if this parameter exists in schema
            param_schema = parameters.get(param_key, {})
            param_type = param_schema.get('type', 'string')
            
            if param_type == 'boolean':
                # Check if next arg is a boolean value or if this is a flag
                if i + 1 < len(function_args_list) and function_args_list[i + 1].lower() in ['true', 'false']:
                    parsed_args[param_key] = function_args_list[i + 1].lower() == 'true'
                    i += 2
                else:
                    # Treat as flag (present = true)
                    parsed_args[param_key] = True
                    i += 1
            else:
                # Need a value
                if i + 1 >= len(function_args_list):
                    # Check if this looks like a CLI flag that was misplaced
                    if param_name in ['verbose', 'raw', 'help', 'list-tools', 'list-agents', 'dump-swml', 
                                      'minimal', 'fake-full-data', 'simulate-serverless', 'agent-class', 'route']:
                        raise ValueError(f"CLI flag --{param_name} must come BEFORE --exec, not after.\n"
                                       f"Example: swaig-test file.py --{param_name} --exec function_name")
                    else:
                        raise ValueError(f"Parameter --{param_name} requires a value")
                
                value = function_args_list[i + 1]
                
                # Type coercion
                if param_type == 'integer':
                    try:
                        parsed_args[param_key] = int(value)
                    except ValueError:
                        raise ValueError(f"Parameter --{param_name} must be an integer, got: {value}")
                elif param_type == 'number':
                    try:
                        parsed_args[param_key] = float(value)
                    except ValueError:
                        raise ValueError(f"Parameter --{param_name} must be a number, got: {value}")
                elif param_type == 'array':
                    # Handle comma-separated arrays
                    parsed_args[param_key] = [item.strip() for item in value.split(',')]
                else:
                    # String (default)
                    parsed_args[param_key] = value
                
                i += 2
        else:
            raise ValueError(f"Expected parameter name starting with --, got: {arg}")
    
    return parsed_args