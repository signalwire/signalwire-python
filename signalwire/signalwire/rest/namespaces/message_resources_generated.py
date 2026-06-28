# AUTO-GENERATED from porting-sdk/rest-apis/message/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed create/update
# (explicit spec fields + an ``extras`` door), bound to the resource's spec
# types. Runtime body is a plain dict (open-tail, never validated).
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from .._base import ReadResource

if TYPE_CHECKING:
    from .message_types_generated import (
        LogListResponse,
        LogRetrieveResponse,
    )


class MessageLogs(ReadResource["LogListResponse", "LogRetrieveResponse"]):
    """Typed resource for ``/logs`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/messaging/logs")
