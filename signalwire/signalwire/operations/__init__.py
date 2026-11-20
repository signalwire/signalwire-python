"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Operations: an agent written as what it can do for a caller.

A ``ServiceAgent`` holds operations (what it can change: cancel an order, move
a booking), lookups (what it can read) and how it identifies the caller. Each
operation is written once, for any caller: its fields, ``prepare`` (the rules:
check, look up, build the change) and ``apply`` (one backend write). The agent
runs the rest the same way for every operation: the read-back, one yes, the
writes, the call's record, and a request made while another change waits.
"""

from signalwire.operations.agent import (
    DEFAULT_RULES,
    CallContext,
    Operations,
    ServiceAgent,
)
from signalwire.operations.model import (
    NOT_SAID,
    Change,
    Field,
    Need,
    Operation,
    Refuse,
    Values,
    Write,
    WriteFailed,
)
from signalwire.operations.wording import DEFAULT_WORDING

__all__ = [
    "DEFAULT_RULES",
    "DEFAULT_WORDING",
    "NOT_SAID",
    "CallContext",
    "Change",
    "Field",
    "Need",
    "Operation",
    "Operations",
    "Refuse",
    "ServiceAgent",
    "Values",
    "Write",
    "WriteFailed",
]
