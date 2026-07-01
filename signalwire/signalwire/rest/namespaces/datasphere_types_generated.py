# AUTO-GENERATED from porting-sdk/rest-apis/datasphere/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class Chunk(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    text: str
    document_id: docid


class ChunkListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[ChunkResponse]
    links: ChunkPaginationResponse


class ChunkPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class ChunkResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    datasphere_document_id: uuid
    project_id: uuid
    status: ChunkStatus
    tags: list[str]
    content: str
    created_at: str
    updated_at: str


ChunkStatus: TypeAlias = "Literal['submitted', 'in_progress', 'completed', 'failed']"

ChunkingStrategy: TypeAlias = "Literal['sentence', 'paragraph', 'page', 'sliding']"


class CreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class Document(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: docid
    filename: str
    status: DocumentStatus
    tags: list[str]
    chunking_strategy: ChunkingStrategy
    max_sentences_per_chunk: int | None
    split_newlines: bool | None
    overlap_size: int | None
    chunk_size: int | None
    number_of_chunks: int
    chunks_uri: str
    created_at: str
    updated_at: str


DocumentCreatePageRequest: TypeAlias = "DocumentCreateRequestBase"

DocumentCreateParagraphRequest: TypeAlias = "DocumentCreateRequestBase"

DocumentCreateRequest: TypeAlias = "DocumentCreateSentenceRequest | DocumentCreateSlidingRequest | DocumentCreatePageRequest | DocumentCreateParagraphRequest"


class DocumentCreateRequestBase(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    url: str
    tags: list[str]


DocumentCreateSentenceRequest: TypeAlias = "DocumentCreateRequestBase"

DocumentCreateSlidingRequest: TypeAlias = "DocumentCreateRequestBase"


class DocumentListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[Document]
    links: PaginationResponse


class DocumentSearchRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    tags: list[str]
    document_id: docid
    query_string: str
    distance: float
    count: int
    language: str
    pos_to_expand: list[str]
    max_synonyms: int


DocumentStatus: TypeAlias = "Literal['submitted', 'in_progress', 'completed', 'failed']"


class DocumentUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    tags: list[str]


class ListStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class PaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SearchResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    chunks: list[Chunk]


class SearchStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class Types_StatusCodes_RestApiErrorItem(TypedDict, total=False):
    """Details about a specific error.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: str
    code: str
    message: str
    attribute: str | None
    url: str


class Types_StatusCodes_StatusCode400(TypedDict, total=False):
    """The request is invalid.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Bad Request"]


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


class Types_StatusCodes_StatusCode404(TypedDict, total=False):
    """The server cannot find the requested resource.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Not Found"]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


class UpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


docid: TypeAlias = "str"

uuid: TypeAlias = "str"

ListDocumentsResponse: TypeAlias = "DocumentListResponse"
CreateDocumentRequest: TypeAlias = "DocumentCreateRequest"
CreateDocumentResponse: TypeAlias = "Document"
SearchDocumentsRequest: TypeAlias = "DocumentSearchRequest"
SearchDocumentsResponse: TypeAlias = "SearchResponse"
ListDocumentChunksResponse: TypeAlias = "ChunkListResponse"
GetDocumentChunkResponse: TypeAlias = "ChunkResponse"
GetDocumentResponse: TypeAlias = "Document"
UpdateDocumentRequest: TypeAlias = "DocumentUpdateRequest"
UpdateDocumentResponse: TypeAlias = "Document"
