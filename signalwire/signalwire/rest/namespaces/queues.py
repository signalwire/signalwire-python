"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Queues namespace — CRUD + member management.

The ``QueuesResource`` class is generated from the canonical spec (see
``relay_rest_resources_generated``); it is re-exported here so existing imports keep
working.
"""

from .relay_rest_resources_generated import QueuesResource

__all__ = ["QueuesResource"]
