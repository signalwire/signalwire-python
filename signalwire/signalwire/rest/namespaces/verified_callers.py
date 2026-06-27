"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Verified Caller IDs namespace — CRUD + verification flow.

``VerifiedCallersResource`` is generated from the canonical spec (see
``relay_rest_resources_generated``) and re-exported here so existing imports keep
working.
"""

from .relay_rest_resources_generated import VerifiedCallersResource

__all__ = ["VerifiedCallersResource"]
