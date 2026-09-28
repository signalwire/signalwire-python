#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Type definitions for the CLI tools
"""

from typing import TypedDict, Any


class DataMapConfig(TypedDict, total=False):
    """DataMap function configuration"""

    function: str
    data_map: dict[str, Any]
    description: str
    parameters: dict[str, Any]


class AgentInfo(TypedDict):
    """Information about a discovered agent"""

    class_name: str
    file_path: str
    is_instance: bool
    instance_name: str | None


class FunctionInfo(TypedDict):
    """Information about a SWAIG function"""

    name: str
    description: str
    parameters: dict[str, Any]
    type: str  # 'local', 'external', 'datamap'
    webhook_url: str | None
