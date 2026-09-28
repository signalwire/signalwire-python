#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Generate fake SWML post_data and related helpers
"""

import uuid
import json
from datetime import datetime
from typing import Any


def generate_fake_uuid() -> str:
    """Generate a fake UUID for testing"""
    return str(uuid.uuid4())


def generate_fake_node_id() -> str:
    """Generate a fake node ID for testing"""
    return f"test-node-{uuid.uuid4().hex[:8]}"


#: The ``call.type`` device variants the engine writes in a SWML webhook request:
#: each carries a different key set.
CALL_TYPES = ("phone", "sip", "webrtc")


def _fake_e164(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().int % 10**7:07d}"


def generate_fake_sip_from(call_type: str) -> str:
    """Generate a fake ``call.from`` address for a device type."""
    if call_type == "phone":
        return _fake_e164("+1555")
    if call_type == "sip":
        return f"sip:caller-{uuid.uuid4().hex[:8]}@test.sip.domain"
    # webrtc
    return f"user-{uuid.uuid4().hex[:8]}@test.domain"


def generate_fake_sip_to(call_type: str) -> str:
    """Generate a fake ``call.to`` address for a device type."""
    if call_type == "phone":
        return _fake_e164("+1444")
    if call_type == "sip":
        return f"sip:agent-{uuid.uuid4().hex[:8]}@test.sip.domain"
    # webrtc
    return f"agent-{uuid.uuid4().hex[:8]}@test.domain"


def _sip_uri_parts(address: str) -> tuple[str, str]:
    """(user, host) of a ``sip:user@host`` address."""
    user, _, host = address.removeprefix("sip:").partition("@")
    return user, host


def adapt_for_call_type(call_data: dict[str, Any], call_type: str) -> dict[str, Any]:
    """
    Add the device-variant keys the engine writes for ``call_type``.

    The engine's ``call`` object is closed and its key set depends on the device
    type (the per-device-type variants of the engine's SWML webhook request):

    - ``phone``: ``type``, ``from``, ``to``, ``from_number``, ``to_number`` (``from``
      and ``to`` repeat the numbers), optional ``headers``;
    - ``sip``: ``type``, ``from``, ``to``, optional ``headers`` (an array of
      ``{name, value}``) and ``sip_data``;
    - ``webrtc``: ``type``, ``from``, ``to``.

    Args:
        call_data: Base call data structure (the keys common to every device type)
        call_type: "phone", "sip" or "webrtc"

    Returns:
        A copy of ``call_data`` with that variant's keys added
    """
    if call_type not in CALL_TYPES:
        raise ValueError(f"call_type must be one of {CALL_TYPES}, got {call_type!r}")
    call_data = call_data.copy()
    call_data["type"] = call_type
    call_data["from"] = generate_fake_sip_from(call_type)
    call_data["to"] = generate_fake_sip_to(call_type)

    if call_type == "phone":
        call_data["from_number"] = call_data["from"]
        call_data["to_number"] = call_data["to"]
    elif call_type == "sip":
        call_data["headers"] = [
            {"name": "X-Test-Client", "value": "swaig-test"},
        ]
        from_user, from_host = _sip_uri_parts(call_data["from"])
        to_user, to_host = _sip_uri_parts(call_data["to"])
        call_data["sip_data"] = {
            "sip_req_user": to_user,
            "sip_req_host": to_host,
            "sip_req_uri": f"{to_user}@{to_host}",
            "sip_from_user": from_user,
            "sip_from_host": from_host,
            "sip_from_uri": f"{from_user}@{from_host}",
            "sip_to_user": to_user,
            "sip_to_host": to_host,
            "sip_to_uri": f"{to_user}@{to_host}",
        }

    return call_data


def generate_fake_swml_post_data(
    call_type: str = "webrtc",
    call_direction: str = "inbound",
    call_state: str = "created",
) -> dict[str, Any]:
    """
    Generate a fake SWML webhook request body in the engine's shape

    The shape is the body the SignalWire engine POSTs to a SWML webhook (the
    same contract ``SwmlRequestData`` types): a closed ``call`` object carrying ``call_id``, ``node_id``, ``call_state`` and
    ``direction`` plus its device variant's keys, the ``vars`` bag (always
    present) and ``envs``.

    Args:
        call_type: "phone", "sip" or "webrtc" (default: webrtc)
        call_direction: "inbound" or "outbound" (default: inbound)
        call_state: Call state (default: created)

    Returns:
        Fake request body with call, vars, and envs
    """
    call_data: dict[str, Any] = {
        "project_id": generate_fake_uuid(),
        "space_id": generate_fake_uuid(),
        "call_id": generate_fake_uuid(),
        "node_id": generate_fake_node_id(),
        "segment_id": generate_fake_uuid(),
        "call_state": call_state,
        "direction": call_direction,
    }

    return {
        "call": adapt_for_call_type(call_data, call_type),
        "vars": {
            "userVariables": {}  # Empty by default, can be filled via overrides
        },
        "envs": {},  # Empty by default, can be filled via overrides
    }


def generate_comprehensive_post_data(
    function_name: str,
    args: dict[str, Any],
    custom_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate comprehensive post_data that matches what SignalWire would send

    Args:
        function_name: Name of the SWAIG function being called
        args: Function arguments
        custom_data: Optional custom data to override defaults

    Returns:
        Complete post_data dict with all possible keys
    """
    call_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    project_id = str(uuid.uuid4())
    space_id = str(uuid.uuid4())
    space_name = "test-space"
    environment = "production"

    current_time = datetime.now().isoformat()

    # Base structure with all keys
    post_data: dict[str, Any] = {
        "call_id": call_id,
        "call": {
            "call_id": call_id,
            "node_id": f"test-node-{uuid.uuid4().hex[:8]}",
            "segment_id": str(uuid.uuid4()),
            "call_session_id": str(uuid.uuid4()),
            "to": "+15551234567",
            "from": "+15559876543",
            "direction": "inbound",
            "state": "answered",
            "tag": call_id,
            "project_id": project_id,
            "space_id": space_id,
            "headers": {"User-Agent": "SignalWire/1.0"},
            "type": "phone",
            "timeout": 30,
            "answer_on_bridge": False,
            "created_at": current_time,
            "updated_at": current_time,
        },
        "vars": {
            "environment": environment,
            "space_id": space_id,
            "userVariables": {},
            "call_data": {
                "id": call_id,
                "state": "answered",
                "type": "phone",
                "from": "+15559876543",
                "to": "+15551234567",
                "project_id": project_id,
                "created_at": current_time,
            },
        },
        "params": args,
        "space_id": space_id,
        "project_id": project_id,
        "meta_data": {
            "application": {"name": "SignalWire AI Agent", "version": "1.0.0"},
            "swml": {"version": "1.0.0", "session_id": session_id},
            "ai": {
                "call_id": call_id,
                "session_id": session_id,
                "conversation_id": session_id,
            },
            "request": {
                "method": "POST",
                "source_ip": "192.168.1.1",
                "user_agent": "SignalWire-AI-Agent/1.0",
            },
            "timing": {"request_start": current_time, "function_start": current_time},
            "user": {
                "id": f"user-{uuid.uuid4().hex[:8]}",
                "session_start": current_time,
                "last_updated": current_time,
            },
        },
        # Global application data
        "global_data": {
            "app_name": "test_application",
            "environment": "test",
            "user_preferences": {"language": "en"},
            "session_data": {"start_time": current_time},
        },
        # Conversation context
        "call_log": [
            {
                "role": "system",
                "content": "You are a helpful AI assistant created with SignalWire AI Agents.",
            },
            {"role": "user", "content": f"Please call the {function_name} function"},
            {
                "role": "assistant",
                "content": f"I'll call the {function_name} function for you.",
                "tool_calls": [
                    {
                        "id": f"call_{call_id[:8]}",
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "arguments": json.dumps(args),
                        },
                    }
                ],
            },
        ],
        "raw_call_log": [
            {
                "role": "system",
                "content": "You are a helpful AI assistant created with SignalWire AI Agents.",
            },
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hello! How can I help you today?"},
            {"role": "user", "content": f"Please call the {function_name} function"},
            {
                "role": "assistant",
                "content": f"I'll call the {function_name} function for you.",
                "tool_calls": [
                    {
                        "id": f"call_{call_id[:8]}",
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "arguments": json.dumps(args),
                        },
                    }
                ],
            },
        ],
        # SWML and prompt variables
        "prompt_vars": {
            # From SWML prompt variables
            "ai_instructions": "You are a helpful assistant",
            "temperature": 0.7,
            "max_tokens": 1000,
            # From global_data
            "app_name": "test_application",
            "environment": "test",
            "user_preferences": {"language": "en"},
            "session_data": {"start_time": current_time},
            # SWML system variables
            "current_timestamp": current_time,
            "call_duration": "00:02:15",
            "caller_number": "+15551234567",
            "to_number": "+15559876543",
        },
        # Permission flags (from SWML parameters)
        "swaig_allow_swml": True,
        "swaig_post_conversation": True,
        "swaig_post_swml_vars": True,
        # Additional context
        "http_method": "POST",
        "webhook_url": f"https://test.example.com/webhook/{function_name}",
        "user_agent": "SignalWire-AI-Agent/1.0",
        "request_headers": {
            "Content-Type": "application/json",
            "User-Agent": "SignalWire-AI-Agent/1.0",
            "X-Signalwire-Call-Id": call_id,
            "X-Signalwire-Session-Id": session_id,
        },
        # SignalWire environment data
        "swml_env": {
            "space_id": space_id,
            "project_id": project_id,
            "environment": environment,
            "space_name": space_name,
            "api_version": "1.0.0",
        },
    }

    # Apply custom data overrides if provided
    if custom_data:
        # Deep merge custom_data into post_data
        for key, value in custom_data.items():
            if (
                key in post_data
                and isinstance(post_data[key], dict)
                and isinstance(value, dict)
            ):
                # Merge dictionaries
                post_data[key].update(value)
            else:
                # Replace value
                post_data[key] = value

    return post_data


def generate_minimal_post_data(
    function_name: str, args: dict[str, Any]
) -> dict[str, Any]:
    """
    Generate minimal post_data with only essential keys

    Args:
        function_name: Name of the SWAIG function being called
        args: Function arguments

    Returns:
        Minimal post_data dict
    """
    call_id = str(uuid.uuid4())

    return {"call_id": call_id, "params": args}
