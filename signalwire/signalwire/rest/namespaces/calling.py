"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Calling namespace — the command-dispatch call-control resource (dial/play/record/
transfer/...), generated from the calling spec (see ``calling_resources_generated``).
"""

from .calling_resources_generated import CallingResource

# Back-compat alias for the historical namespace name.
CallingNamespace = CallingResource

__all__ = ["CallingNamespace", "CallingResource"]
