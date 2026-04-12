"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Prompt Object Model (POM)
=========================

A structured data format for organizing and rendering LLM prompts.

Vendored from the signalwire-pom package so the SDK has no external
signalwire-pom dependency.
"""

from signalwire.pom.pom import PromptObjectModel, Section

__all__ = ["PromptObjectModel", "Section"]
