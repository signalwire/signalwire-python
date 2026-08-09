"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Async client for the SignalWire AI Chat service — see
:mod:`signalwire.ai_chat.client` for the full protocol notes.
"""

from .gateway import ChatGateway, GatewayRejection
from .client import (
    AIChatClient,
    AIChatError,
    AuthenticationError,
    ChatInProgressError,
    ChatLog,
    ChatResponse,
    ConversationInfo,
    ConversationNotFoundError,
    RateLimitError,
    SummaryError,
)

__all__ = [
    "AIChatClient",
    "ChatGateway",
    "GatewayRejection",
    "AIChatError",
    "AuthenticationError",
    "ChatInProgressError",
    "ChatLog",
    "ChatResponse",
    "ConversationInfo",
    "ConversationNotFoundError",
    "RateLimitError",
    "SummaryError",
]
