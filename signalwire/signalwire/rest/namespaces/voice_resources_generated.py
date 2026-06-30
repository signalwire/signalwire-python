# AUTO-GENERATED from porting-sdk/rest-apis/voice/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: create/update are FULLY CLOSED
# to the spec fields (no ``extras``/``**kwargs`` door — unknown fields aren't
# sendable through the typed method), bound to the resource's spec types.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from .._base import ReadResource

if TYPE_CHECKING:
    from .voice_types_generated import (
        LogEventsListResponse,
        LogListResponse,
        VoiceLog,
    )


class VoiceLogs(ReadResource["LogListResponse", "VoiceLog"]):
    """Typed resource for ``/logs`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/voice/logs")

    def list_events(self, id: str, **params: Any) -> LogEventsListResponse:
        return cast(
            "LogEventsListResponse",
            self._http.get(self._path(id, "events"), params=params or None),
        )
