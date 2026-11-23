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
from signalwire.operations.appointments import (
    APPOINTMENTS_WORDING,
    Appointment,
    Appointments,
    Slot,
)
from signalwire.operations.messages import MESSAGES_WORDING, Message, Messages
from signalwire.operations.money import CURRENCIES, format_money
from signalwire.operations.payments import (
    PAYMENTS_WORDING,
    Charge,
    PaymentResult,
    Payments,
)
from signalwire.operations.record import RECORD, RECORD_KEYS, RECORD_VERSION
from signalwire.operations.wording import DEFAULT_WORDING

__all__ = [
    "APPOINTMENTS_WORDING",
    "CURRENCIES",
    "DEFAULT_RULES",
    "DEFAULT_WORDING",
    "MESSAGES_WORDING",
    "NOT_SAID",
    "PAYMENTS_WORDING",
    "RECORD",
    "RECORD_KEYS",
    "RECORD_VERSION",
    "Appointment",
    "Appointments",
    "CallContext",
    "Change",
    "Charge",
    "Field",
    "Message",
    "Messages",
    "Need",
    "Operation",
    "Operations",
    "PaymentResult",
    "Payments",
    "Refuse",
    "ServiceAgent",
    "Slot",
    "Values",
    "Write",
    "WriteFailed",
    "format_money",
]
