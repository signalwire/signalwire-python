#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Handle CLI overrides and mapping to nested data
"""

import json
import uuid
import argparse
from typing import Dict, Any, List


def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> None:
    """
    Set a nested value using dot notation path
    
    Args:
        data: Dictionary to modify
        path: Dot-notation path (e.g., "call.call_id" or "vars.userVariables.custom")
        value: Value to set
    """
    keys = path.split('.')
    current = data
    
    # Navigate to the parent of the target key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Set the final value
    current[keys[-1]] = value


def parse_value(value_str: str) -> Any:
    """
    Parse a string value into appropriate Python type
    
    Args:
        value_str: String representation of value
        
    Returns:
        Parsed value (str, int, float, bool, None, or JSON object)
    """
    # Handle special values
    if value_str.lower() == 'null':
        return None
    elif value_str.lower() == 'true':
        return True
    elif value_str.lower() == 'false':
        return False
    
    # Try parsing as number
    try:
        if '.' in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        pass
    
    # Try parsing as JSON (for objects/arrays)
    try:
        return json.loads(value_str)
    except json.JSONDecodeError:
        pass
    
    # Return as string
    return value_str


def apply_overrides(data: Dict[str, Any], overrides: List[str], 
                   json_overrides: List[str]) -> Dict[str, Any]:
    """
    Apply override values to data using dot notation paths
    
    Args:
        data: Data dictionary to modify
        overrides: List of "path=value" strings
        json_overrides: List of "path=json_value" strings
        
    Returns:
        Modified data dictionary
    """
    data = data.copy()
    
    # Apply simple overrides
    for override in overrides:
        if '=' not in override:
            continue
        path, value_str = override.split('=', 1)
        value = parse_value(value_str)
        set_nested_value(data, path, value)
    
    # Apply JSON overrides
    for json_override in json_overrides:
        if '=' not in json_override:
            continue
        path, json_str = json_override.split('=', 1)
        try:
            value = json.loads(json_str)
            set_nested_value(data, path, value)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in override '{json_override}': {e}")
    
    return data


def apply_convenience_mappings(data: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    """
    Apply convenience CLI arguments to data structure
    
    Args:
        data: Data dictionary to modify
        args: Parsed CLI arguments
        
    Returns:
        Modified data dictionary
    """
    data = data.copy()
    
    # Map high-level arguments to specific paths
    if hasattr(args, 'call_id') and args.call_id:
        # Set at root level for SWAIG functions
        data["call_id"] = args.call_id
        # Also set in call object if it exists
        if "call" in data:
            set_nested_value(data, "call.call_id", args.call_id)
            set_nested_value(data, "call.tag", args.call_id)  # tag often matches call_id
    
    if hasattr(args, 'project_id') and args.project_id:
        set_nested_value(data, "call.project_id", args.project_id)
    
    if hasattr(args, 'space_id') and args.space_id:
        set_nested_value(data, "call.space_id", args.space_id)
    
    if hasattr(args, 'call_state') and args.call_state:
        set_nested_value(data, "call.state", args.call_state)
    
    if hasattr(args, 'call_direction') and args.call_direction:
        set_nested_value(data, "call.direction", args.call_direction)
    
    # Handle from/to addresses with fake generation if needed
    if hasattr(args, 'from_number') and args.from_number:
        # If looks like phone number, use as-is, otherwise generate fake
        if args.from_number.startswith('+') or args.from_number.isdigit():
            set_nested_value(data, "call.from", args.from_number)
        else:
            # Generate fake phone number or SIP address
            call_type = getattr(args, 'call_type', 'webrtc')
            if call_type == 'sip':
                set_nested_value(data, "call.from", f"+1555{uuid.uuid4().hex[:7]}")
            else:
                set_nested_value(data, "call.from", f"{args.from_number}@test.domain")
    
    if hasattr(args, 'to_extension') and args.to_extension:
        # Similar logic for 'to' address
        if args.to_extension.startswith('+') or args.to_extension.isdigit():
            set_nested_value(data, "call.to", args.to_extension)
        else:
            call_type = getattr(args, 'call_type', 'webrtc')
            if call_type == 'sip':
                set_nested_value(data, "call.to", f"+1444{uuid.uuid4().hex[:7]}")
            else:
                set_nested_value(data, "call.to", f"{args.to_extension}@test.domain")
    
    # Merge user variables
    user_vars = {}
    
    # Add user_vars if provided
    if hasattr(args, 'user_vars') and args.user_vars:
        try:
            user_vars.update(json.loads(args.user_vars))
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in --user-vars: {e}")
    
    # Add query_params if provided (merged into userVariables)
    if hasattr(args, 'query_params') and args.query_params:
        try:
            user_vars.update(json.loads(args.query_params))
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in --query-params: {e}")
    
    # Apply user variables
    if user_vars:
        if "vars" not in data:
            data["vars"] = {}
        if "userVariables" not in data["vars"]:
            data["vars"]["userVariables"] = {}
        data["vars"]["userVariables"].update(user_vars)
    
    return data