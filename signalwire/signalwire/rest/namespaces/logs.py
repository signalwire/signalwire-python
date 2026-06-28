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

from .fax_resources_generated import FaxLogsResource
from .logs_resources_generated import ConferenceLogsResource
from .message_resources_generated import MessageLogsResource
from .voice_resources_generated import VoiceLogsResource

# Back-compat aliases for the historical class names.
MessageLogs = MessageLogsResource
VoiceLogs = VoiceLogsResource
FaxLogs = FaxLogsResource
ConferenceLogs = ConferenceLogsResource

__all__ = [
    "ConferenceLogs",
    "ConferenceLogsResource",
    "FaxLogs",
    "FaxLogsResource",
    "LogsNamespace",
    "MessageLogs",
    "MessageLogsResource",
    "VoiceLogs",
    "VoiceLogsResource",
]


class LogsNamespace:
    """Logs API namespace — groups per-product log resources under ``client.logs``."""

    def __init__(self, http: Any) -> None:
        self.messages = MessageLogsResource(http)
        self.voice = VoiceLogsResource(http)
        self.fax = FaxLogsResource(http)
        self.conferences = ConferenceLogsResource(http)
