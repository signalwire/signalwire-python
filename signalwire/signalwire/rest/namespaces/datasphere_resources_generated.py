# AUTO-GENERATED from porting-sdk/rest-apis/datasphere/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed create/update
# (explicit spec fields + an ``extras`` door), bound to the resource's spec
# types. Runtime body is a plain dict (open-tail, never validated).
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import CrudResource

if TYPE_CHECKING:
    from .datasphere_types_generated import (
        Document,
        DocumentCreateRequest,
        DocumentListResponse,
        DocumentUpdateRequest,
    )


class DatasphereDocumentsResource(
    CrudResource[
        "DocumentListResponse",
        "Document",
        "DocumentCreateRequest",
        "DocumentUpdateRequest",
    ]
):
    """Typed CRUD resource for ``/documents`` (generated)."""

    def create(  # type: ignore[override]
        self, body: DocumentCreateRequest, *, extras: Mapping[str, Any] | None = None
    ) -> Document:
        merged: dict[str, Any] = {**body, **(extras or {})}
        return cast("Document", self._http.post(self._base_path, body=merged))

    def update(  # type: ignore[override]
        self,
        id: str,
        /,
        *,
        tags: list[str] | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> Document:
        body: dict[str, Any] = {
            k: v for k, v in {"tags": tags}.items() if v is not None
        }
        if extras:
            body.update(extras)
        return cast("Document", self._http.patch(self._path(id), body=body))
