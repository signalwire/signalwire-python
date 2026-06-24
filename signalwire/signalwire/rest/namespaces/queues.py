"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Queues namespace — CRUD + member management.
"""

from typing import TYPE_CHECKING, Any

from .._base import CrudResource

if TYPE_CHECKING:
    from .compatibility_types_generated import (
        CreateQueueRequest,
        Queue,
        QueueListResponse,
        QueueMemberListResponse,
        QueueMemberResponse,
        UpdateQueueRequest,
    )


class QueuesResource(
    CrudResource[
        "QueueListResponse", "Queue", "CreateQueueRequest", "UpdateQueueRequest"
    ]
):
    """Queue management with member operations."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/queues")

    def list_members(self, queue_id: str, **params: Any) -> "QueueMemberListResponse":
        return self._http.get(self._path(queue_id, "members"), params=params or None)

    def get_next_member(self, queue_id: str) -> "QueueMemberResponse":
        return self._http.get(self._path(queue_id, "members", "next"))

    def get_member(self, queue_id: str, member_id: str) -> "QueueMemberResponse":
        return self._http.get(self._path(queue_id, "members", member_id))
