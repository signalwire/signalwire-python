#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Handle CLI overrides and mapping to nested data
"""

import json
import uuid
import argparse
from typing import Any


def set_nested_value(data: dict[str, Any], path: str, value: Any) -> None:
    """
    Set a nested value using dot notation path

    Args:
        data: Dictionary to modify
        path: Dot-notation path (e.g., "call.call_id" or "vars.userVariables.custom")
        value: Value to set
    """
    keys = path.split(".")
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
    if value_str.lower() == "null":
        return None
    if value_str.lower() == "true":
        return True
    if value_str.lower() == "false":
        return False

    # Try parsing as number
    try:
        if "." in value_str:
            return float(value_str)
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


def apply_overrides(
    data: dict[str, Any], overrides: list[str], json_overrides: list[str]
) -> dict[str, Any]:
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
        if "=" not in override:
            continue
        path, value_str = override.split("=", 1)
        value = parse_value(value_str)
        set_nested_value(data, path, value)

    # Apply JSON overrides
    for json_override in json_overrides:
        if "=" not in json_override:
            continue
        path, json_str = json_override.split("=", 1)
        try:
            value = json.loads(json_str)
            set_nested_value(data, path, value)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in override '{json_override}': {e}")

    return data


def _address(value: str, call_type: str, fake_prefix: str) -> str:
    """A ``call.from``/``call.to`` value for a device type: a phone number or a full
    address (``user@host``) is used as-is; otherwise a phone call gets a fake number
    and a sip/webrtc call gets ``value`` as the user part of an address."""
    if value.startswith("+") or value.isdigit() or "@" in value:
        return value
    if call_type == "phone":
        return f"{fake_prefix}{uuid.uuid4().int % 10**7:07d}"
    if call_type == "sip":
        return f"sip:{value}@test.sip.domain"
    return f"{value}@test.domain"


def apply_convenience_mappings(
    data: dict[str, Any], args: argparse.Namespace
) -> dict[str, Any]:
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
    if hasattr(args, "call_id") and args.call_id:
        # A SWAIG function request carries call_id at the ROOT; a SWML webhook
        # request carries it only inside its closed ``call`` object (a root call_id
        # is a key the engine never writes there).
        if "call" not in data or "call_id" in data:
            data["call_id"] = args.call_id
        if "call" in data:
            data["call"] = {**data["call"], "call_id": args.call_id}

    # The call.* keys below belong to the SWML webhook request's ``call`` object
    # (engine shape: porting-sdk combined-specs/swml.yaml ``webhook_request``). They
    # are applied only to a body that HAS one — never fabricated into a body (e.g. a
    # SWAIG function request) whose contract carries no ``call`` object.
    if "call" in data:
        call = data["call"] = dict(data["call"])
        call_type = call.get("type", getattr(args, "call_type", "webrtc"))

        if hasattr(args, "project_id") and args.project_id:
            call["project_id"] = args.project_id

        if hasattr(args, "space_id") and args.space_id:
            call["space_id"] = args.space_id

        if hasattr(args, "call_state") and args.call_state:
            call["call_state"] = args.call_state

        if hasattr(args, "call_direction") and args.call_direction:
            call["direction"] = args.call_direction

        # from/to addresses; a phone call carries each number twice (from +
        # from_number, to + to_number), so both are kept in step.
        if hasattr(args, "from_number") and args.from_number:
            call["from"] = _address(args.from_number, call_type, "+1555")
            if call_type == "phone":
                call["from_number"] = call["from"]

        if hasattr(args, "to_extension") and args.to_extension:
            call["to"] = _address(args.to_extension, call_type, "+1444")
            if call_type == "phone":
                call["to_number"] = call["to"]

    # Merge user variables
    user_vars = {}

    # Add user_vars if provided
    if hasattr(args, "user_vars") and args.user_vars:
        try:
            user_vars.update(json.loads(args.user_vars))
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in --user-vars: {e}")

    # Add query_params if provided (merged into userVariables)
    if hasattr(args, "query_params") and args.query_params:
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
