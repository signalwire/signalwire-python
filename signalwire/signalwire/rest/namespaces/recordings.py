"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Recordings namespace — list, get, delete (no create/update).
"""

from typing import TYPE_CHECKING, Any

from .._base import BaseResource

if TYPE_CHECKING:
    from .compatibility_types_generated import (
        Recording,
        RecordingListResponse,
    )


class RecordingsResource(BaseResource):
    """Recording management (read-only + delete)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/recordings")

    def list(self, **params: Any) -> "RecordingListResponse":
        return self._http.get(self._base_path, params=params or None)

    def get(self, recording_id: str) -> "Recording":
        return self._http.get(self._path(recording_id))

    def delete(self, recording_id: str) -> dict[str, Any]:
        return self._http.delete(self._path(recording_id))
