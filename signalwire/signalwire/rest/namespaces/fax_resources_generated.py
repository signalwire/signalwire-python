# AUTO-GENERATED from porting-sdk/rest-apis/fax/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``fax`` REST resources, generated from the OpenAPI spec.

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

    from .fax_types_generated import (
        LogListResponse,
        LogResponse,
    )


class FaxLogs(ReadResource["LogListResponse", "LogResponse"]):
    """Typed resource for ``/logs`` (generated).

    Bound to ``/api/fax/logs``; construct it as ``FaxLogs(http)`` with the client's HTTP
    transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fax/logs")
