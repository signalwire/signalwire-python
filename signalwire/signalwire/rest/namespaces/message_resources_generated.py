# AUTO-GENERATED from porting-sdk/rest-apis/message/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``message`` REST resources, generated from the OpenAPI spec.

One resource class per spec collection: closed, typed ``create`` / ``update``
parameters (the explicit spec fields) and typed sub-operation methods, plus an
``extras`` escape hatch and a ``**_reserved_kw`` tail for unknown or reserved-word
wire fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from .._base import ReadResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .message_types_generated import (
        LogListResponse,
        LogRetrieveResponse,
    )


class MessageLogs(ReadResource["LogListResponse", "LogRetrieveResponse"]):
    """Typed resource for ``/logs`` (generated).

    Bound to ``/api/messaging/logs``; construct it as ``MessageLogs(http)`` with the
    client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/messaging/logs")
