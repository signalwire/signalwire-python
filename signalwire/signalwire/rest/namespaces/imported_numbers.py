"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Imported Phone Numbers namespace — create only.
"""

from typing import TYPE_CHECKING, Any

from .._base import BaseResource

if TYPE_CHECKING:
    from .relay_rest_types_generated import PhoneNumberResponse


class ImportedNumbersResource(BaseResource):
    """Import externally-hosted phone numbers."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/imported_phone_numbers")

    def create(self, **kwargs: Any) -> "PhoneNumberResponse":
        return self._http.post(self._base_path, body=kwargs)
