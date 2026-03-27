#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Type definitions for the CLI tools
"""

from typing import TypedDict, Dict, Any, Optional, List, Union


class CallData(TypedDict, total=False):
    """Call data structure for SWML post_data"""
    id: str
    node_id: str
    state: str
    type: str
    direction: str
    project_id: str
    space_id: str
    from_number: str
    to_number: str
    from_: str
    to: str
    from_name: str
    headers: Dict[str, str]
    timeout: int
    tag: str


class VarsData(TypedDict, total=False):
    """Variables data structure for SWML post_data"""
    userVariables: Dict[str, Any]
    environment: str
    call_data: Dict[str, Any]


class PostData(TypedDict, total=False):
    """Complete post_data structure for SWML requests"""
    call_id: str
    call: CallData
    vars: VarsData
    params: Dict[str, Any]
    project_id: str
    space_id: str
    meta_data: Dict[str, Any]
    post_prompt_data: Dict[str, Any]
    error: Optional[str]
    protocol_error: Optional[bool]
    parse_error: Optional[bool]


class DataMapConfig(TypedDict, total=False):
    """DataMap function configuration"""
    function: str
    data_map: Dict[str, Any]
    description: str
    parameters: Dict[str, Any]


class AgentInfo(TypedDict):
    """Information about a discovered agent"""
    class_name: str
    file_path: str
    is_instance: bool
    instance_name: Optional[str]


class FunctionInfo(TypedDict):
    """Information about a SWAIG function"""
    name: str
    description: str
    parameters: Dict[str, Any]
    type: str  # 'local', 'external', 'datamap'
    webhook_url: Optional[str]