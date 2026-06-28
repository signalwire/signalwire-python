"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Logs namespace — a convenience view that groups each product's logs under one
``client.logs`` accessor. The log resources themselves live with their product APIs
(messaging/voice/fax) and the standalone logs API (conferences); each is generated
from its own spec (``x-sdk-resource`` with ``namespace: logs``) and composed here.
"""

from typing import Any

from .fax_resources_generated import FaxLogs
from .logs_resources_generated import ConferenceLogs
from .message_resources_generated import MessageLogs
from .voice_resources_generated import VoiceLogs

__all__ = [
    "ConferenceLogs",
    "FaxLogs",
    "LogsNamespace",
    "MessageLogs",
    "VoiceLogs",
]


class LogsNamespace:
    """Logs API namespace — groups per-product log resources under ``client.logs``."""

    def __init__(self, http: Any) -> None:
        self.messages = MessageLogs(http)
        self.voice = VoiceLogs(http)
        self.fax = FaxLogs(http)
        self.conferences = ConferenceLogs(http)
