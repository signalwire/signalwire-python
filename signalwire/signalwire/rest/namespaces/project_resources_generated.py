# AUTO-GENERATED from porting-sdk/rest-apis/project/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed create/update
# (explicit spec fields + an ``extras`` door), bound to the resource's spec
# types. Runtime body is a plain dict (open-tail, never validated).
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import BaseResource

if TYPE_CHECKING:
    from .project_types_generated import (
        TokenPermission,
        TokenResponse,
    )


class ProjectTokens(BaseResource):
    """Typed resource for ``/tokens`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/project/tokens")

    def create(
        self,
        *,
        name: str,
        permissions: list[TokenPermission],
        subproject_id: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> TokenResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "permissions": permissions,
                "subproject_id": subproject_id,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("TokenResponse", self._http.post(self._base_path, body=body))

    def update(
        self,
        token_id: str,
        *,
        name: str | None = None,
        permissions: list[TokenPermission] | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> TokenResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "permissions": permissions}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("TokenResponse", self._http.patch(self._path(token_id), body=body))

    def delete(self, token_id: str) -> dict[str, Any]:
        return cast("dict[str, Any]", self._http.delete(self._path(token_id)))
