"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Short Codes namespace — list, get, update (no create/delete).
"""

from typing import TYPE_CHECKING, Any

from .._base import BaseResource

if TYPE_CHECKING:
    from .relay_rest_types_generated import (
        ShortCodeListResponse,
        ShortCodeResponse,
    )


class ShortCodesResource(BaseResource):
    """Short code management (read + update only)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/short_codes")

    def list(self, **params: Any) -> "ShortCodeListResponse":
        return self._http.get(self._base_path, params=params or None)

    def get(self, short_code_id: str) -> "ShortCodeResponse":
        return self._http.get(self._path(short_code_id))

    def update(self, short_code_id: str, **kwargs: Any) -> "ShortCodeResponse":
        return self._http.put(self._path(short_code_id), body=kwargs)
