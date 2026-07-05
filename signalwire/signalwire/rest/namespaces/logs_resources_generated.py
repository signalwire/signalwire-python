# AUTO-GENERATED from porting-sdk/rest-apis/logs/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from .._base import BaseResource

if TYPE_CHECKING:
    from .logs_types_generated import (
        ConferencesResponse,
    )


class ConferenceLogs(BaseResource):
    """Typed resource for ``/conferences`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/logs/conferences")

    def list(self, **params: Any) -> ConferencesResponse:
        return cast(
            "ConferencesResponse",
            self._http.get(self._base_path, params=params or None),
        )
