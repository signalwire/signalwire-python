"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Conversation patterns built from the SDK's parts.

``Proposal`` reads a change back and gates the tool that carries it out on
the caller's yes. ``RequestList`` keeps what the caller asked for while the
agent was busy with something else, to come back to.
"""

from signalwire.patterns.proposal import Proposal, current

__all__ = ["Proposal", "current"]
