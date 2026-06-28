# AUTO-GENERATED from porting-sdk/rest-apis/logs/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed create/update
# (explicit spec fields + an ``extras`` door), bound to the resource's spec
# types. Runtime body is a plain dict (open-tail, never validated).
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from .._base import BaseResource

if TYPE_CHECKING:
    from .logs_types_generated import (
        ConferencesResponse,
    )


class ConferenceLogsResource(BaseResource):
    """Typed resource for ``/conferences`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/logs/conferences")

    def list(self, **params: Any) -> ConferencesResponse:
        return cast(
            "ConferencesResponse",
            self._http.get(self._base_path, params=params or None),
        )
