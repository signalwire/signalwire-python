"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Verified Caller IDs namespace — CRUD + verification flow.
"""

from typing import TYPE_CHECKING, Any

from .._base import CrudResource

if TYPE_CHECKING:
    from .relay_rest_types_generated import (
        CreateVerifiedCallerIDRequest,
        UpdateVerifiedCallerIDRequest,
        VerifiedCallerID,
        VerifiedCallerIDListResponse,
        VerifiedCallerIDResponse,
    )


class VerifiedCallersResource(
    CrudResource[
        "VerifiedCallerIDListResponse",
        "VerifiedCallerID",
        "CreateVerifiedCallerIDRequest",
        "UpdateVerifiedCallerIDRequest",
    ]
):
    """Verified caller ID management with verification flow."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/verified_caller_ids")

    def redial_verification(self, caller_id: str) -> "VerifiedCallerIDResponse":
        return self._http.post(self._path(caller_id, "verification"))

    def submit_verification(
        self, caller_id: str, **kwargs: Any
    ) -> "VerifiedCallerIDResponse":
        return self._http.put(self._path(caller_id, "verification"), body=kwargs)
