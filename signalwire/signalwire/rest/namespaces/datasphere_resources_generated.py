# AUTO-GENERATED from porting-sdk/rest-apis/datasphere/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**kwargs`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import CrudResource

if TYPE_CHECKING:
    from .datasphere_types_generated import (
        ChunkListResponse,
        ChunkResponse,
        Document,
        DocumentCreateRequest,
        DocumentListResponse,
        DocumentUpdateRequest,
        SearchResponse,
        docid,
    )


class DatasphereDocuments(
    CrudResource[
        "DocumentListResponse",
        "Document",
        "DocumentCreateRequest",
        "DocumentUpdateRequest",
    ]
):
    """Typed resource for ``/documents`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/datasphere/documents")

    def create(  # type: ignore[override]
        self,
        body: DocumentCreateRequest,
        *,
        extras: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Document:
        merged: dict[str, Any] = {**body, **(extras or {}), **kwargs}
        return cast("Document", self._http.post(self._base_path, body=merged))

    def update(
        self,
        id: str,
        /,
        *,
        tags: list[str] | None = None,
        extras: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Document:
        body: dict[str, Any] = {
            k: v for k, v in {"tags": tags}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(kwargs)
        return cast("Document", self._http.patch(self._path(id), body=body))

    def search(
        self,
        *,
        query_string: str,
        tags: list[str] | None = None,
        document_id: docid | None = None,
        distance: float | None = None,
        count: int | None = None,
        language: str | None = None,
        pos_to_expand: list[str] | None = None,
        max_synonyms: int | None = None,
        extras: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> SearchResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "tags": tags,
                "document_id": document_id,
                "query_string": query_string,
                "distance": distance,
                "count": count,
                "language": language,
                "pos_to_expand": pos_to_expand,
                "max_synonyms": max_synonyms,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(kwargs)
        return cast("SearchResponse", self._http.post(self._path("search"), body=body))

    def list_chunks(self, document_id: str, **params: Any) -> ChunkListResponse:
        return cast(
            "ChunkListResponse",
            self._http.get(self._path(document_id, "chunks"), params=params or None),
        )

    def get_chunk(
        self, document_id: str, chunk_id: str, **params: Any
    ) -> ChunkResponse:
        return cast(
            "ChunkResponse",
            self._http.get(
                self._path(document_id, "chunks", chunk_id), params=params or None
            ),
        )

    def delete_chunk(self, document_id: str, chunk_id: str) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(document_id, "chunks", chunk_id)),
        )
