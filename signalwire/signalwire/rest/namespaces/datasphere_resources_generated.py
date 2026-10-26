# AUTO-GENERATED from porting-sdk/rest-apis/datasphere/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``datasphere`` REST resources, generated from the OpenAPI spec.

One resource class per spec collection: closed, typed ``create`` / ``update``
parameters (the explicit spec fields) and typed sub-operation methods, plus an
``extras`` escape hatch and a ``**_reserved_kw`` tail for unknown or reserved-word
wire fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import CrudResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

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
    """Typed resource for ``/documents`` (generated).

    Bound to ``/api/datasphere/documents``; construct it as
    ``DatasphereDocuments(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/datasphere/documents")

    def create(  # type: ignore[override]
        self,
        body: DocumentCreateRequest,
        *,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Document:
        """Creates a Datasphere Document.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _DataSphere_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            body: The request body (a ``DocumentCreateRequest``).
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        merged: dict[str, Any] = {**body, **(extras or {}), **_reserved_kw}
        return cast(
            "Document",
            self._http.post(
                self._base_path, body=merged, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        tags: list[str] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Document:
        """Updates a Datasphere Document by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _DataSphere_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a Document.
            tags: Document tags.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v for k, v in {"tags": tags}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "Document",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )

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
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SearchResponse:
        """Search Datasphere Documents.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _DataSphere_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            query_string: Search term.
            tags: Document tags.
            document_id: Unique ID of a Document.
            distance: Specifies how closely related the query is to the document. Low
                distance means high relevance and similarity. High distance means low
                relevance and similarity.
            count: Specifies number of returned Chunks.
            language: Language of the Document.
            pos_to_expand: Part of Speech considered for expansion or analysis.
            max_synonyms: Maximum number of synonyms to consider.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
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
        body.update(_reserved_kw)
        return cast(
            "SearchResponse",
            self._http.post(
                self._path("search"), body=body, request_options=request_options
            ),
        )

    def list_chunks(
        self,
        document_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> ChunkListResponse:
        """A list of chunks for a Datasphere Document.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _DataSphere_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            document_id: Unique ID of the Document.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: Specify the number of results to return on a single
                  page. The default page size is `50` and the maximum is `1000`.
                - ``page_token``: Token for cursor-based pagination. Required when
                  `page_number` > 0.

        Returns:
            The request has succeeded.
        """
        return cast(
            "ChunkListResponse",
            self._http.get(
                self._path(document_id, "chunks"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def get_chunk(
        self,
        document_id: str,
        chunk_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> ChunkResponse:
        """Retrieves a specific chunk for a Datasphere Document by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _DataSphere_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            document_id: Unique ID of the parent Document.
            chunk_id: Unique ID of a Chunk.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            The request has succeeded.
        """
        return cast(
            "ChunkResponse",
            self._http.get(
                self._path(document_id, "chunks", chunk_id),
                params=params or None,
                request_options=request_options,
            ),
        )

    def delete_chunk(
        self,
        document_id: str,
        chunk_id: str,
        *,
        request_options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        """Deletes a specific chunk for a Datasphere Document by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _DataSphere_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            document_id: Unique ID of the parent Document.
            chunk_id: Unique ID of a Chunk.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The decoded JSON response (an empty dict when the server sends no body).
        """
        return cast(
            "dict[str, Any]",
            self._http.delete(
                self._path(document_id, "chunks", chunk_id),
                request_options=request_options,
            ),
        )
