"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Chat API namespace — token creation.
"""

from typing import TYPE_CHECKING, Any

from .._base import BaseResource

if TYPE_CHECKING:
    from .chat_types_generated import ChatToken


class ChatResource(BaseResource):
    """Chat token generation."""

    def __init__(self, http):
        super().__init__(http, "/api/chat/tokens")

    def create_token(self, **kwargs: Any) -> "ChatToken":
        return self._http.post(self._base_path, body=kwargs)
