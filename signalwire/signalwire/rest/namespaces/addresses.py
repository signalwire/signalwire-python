"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Addresses namespace — list, create, get, delete (no update).
"""

from typing import TYPE_CHECKING, Any

from .._base import BaseResource

if TYPE_CHECKING:
    from .relay_rest_types_generated import (
        AddressListResponse,
        AddressResponse,
    )


class AddressesResource(BaseResource):
    """Address management (no update endpoint)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/addresses")

    def list(self, **params: Any) -> "AddressListResponse":
        return self._http.get(self._base_path, params=params or None)

    def create(self, **kwargs: Any) -> "AddressResponse":
        return self._http.post(self._base_path, body=kwargs)

    def get(self, address_id: str) -> "AddressResponse":
        return self._http.get(self._path(address_id))

    def delete(self, address_id: str) -> dict[str, Any]:
        return self._http.delete(self._path(address_id))
