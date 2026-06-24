"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Phone Number Lookup namespace.
"""

from typing import TYPE_CHECKING, Any

from .._base import BaseResource

if TYPE_CHECKING:
    from .relay_rest_types_generated import PhoneNumberLookupResponse


class LookupResource(BaseResource):
    """Phone number lookup (carrier, CNAM)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/lookup")

    def phone_number(self, e164: str, **params: Any) -> "PhoneNumberLookupResponse":
        return self._http.get(self._path("phone_number", e164), params=params or None)
