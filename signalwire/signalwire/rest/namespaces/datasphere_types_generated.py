# AUTO-GENERATED from porting-sdk/rest-apis/datasphere/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``datasphere`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class Chunk(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        text: A search result.
        document_id: Unique ID of the Document.
    """

    text: str
    document_id: docid


class ChunkListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        data: A list of chunks.
        links: Pagination links.
    """

    data: list[ChunkResponse]
    links: ChunkPaginationResponse


class ChunkPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        self: Link of the current page.
        first: Link to the first page.
        next: Link to the next page. Only present when there are more results.
        prev: Link to the previous page. Only present when not on the first page.
    """

    self: str
    first: str
    next: str
    prev: str


class ChunkResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: Unique ID of the chunk.
        datasphere_document_id: Unique ID of the chunk's datasphere document.
        project_id: Unique ID of the project.
        status: Status of the chunk.
        tags: The tags of the document associated with the chunk.
        content: Content of the chunk.
        created_at: Chunk Creation Date.
        updated_at: Chunk Update Date.
    """

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
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class Document(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: Unique ID of the Document.
        filename: Name of the Document.
        status: Status of the Document.
        tags: Document tags.
        chunking_strategy: Strategy used to chunk the document.
        max_sentences_per_chunk: Max Sentences per Chunk. Only present when chunking
            strategy is 'sentence', null otherwise.
        split_newlines: Split on Newlines. Only present when chunking strategy is
            'sentence', null otherwise.
        overlap_size: Overlap Size. Only present when chunking strategy is 'sliding',
            null otherwise.
        chunk_size: Chunk Size. Only present when chunking strategy is 'sliding', null
            otherwise.
        number_of_chunks: Number of Chunks in the Document.
        chunks_uri: URI path to the chunks for this document.
        created_at: Document Creation Date.
        updated_at: Document Update Date.
    """

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
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        url: URL of the document.
        tags: Document tags.
    """

    url: str
    tags: list[str]


DocumentCreateSentenceRequest: TypeAlias = "DocumentCreateRequestBase"

DocumentCreateSlidingRequest: TypeAlias = "DocumentCreateRequestBase"


class DocumentListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        data: A list of documents.
        links: Pagination links.
    """

    data: list[Document]
    links: PaginationResponse


class DocumentSearchRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        tags: Document tags.
        document_id: Unique ID of a Document.
        query_string: Search term.
        distance: Specifies how closely related the query is to the document. Low
            distance means high relevance and similarity. High distance means low
            relevance and similarity.
        count: Specifies number of returned Chunks.
        language: Language of the Document.
        pos_to_expand: Part of Speech considered for expansion or analysis.
        max_synonyms: Maximum number of synonyms to consider.
    """

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
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        tags: Document tags.
    """

    tags: list[str]


class ListStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class PaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        self: Link of the current page.
        first: Link to the first page.
        next: Link to the next page. Only present when there are more results.
        prev: Link to the previous page. Only present when not on the first page.
    """

    self: str
    first: str
    next: str
    prev: str


class SearchResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        chunks: A list of search result chunks.
    """

    chunks: list[Chunk]


class SearchStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class Types_StatusCodes_RestApiErrorItem(TypedDict, total=False):
    """Details about a specific error.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        type: The category of error.
        code: A specific error code.
        message: A description of what caused the error.
        attribute: The request parameter that caused the error, if applicable.
        url: A link to documentation about this error.
    """

    type: str
    code: str
    message: str
    attribute: str | None
    url: str


class Types_StatusCodes_StatusCode400(TypedDict, total=False):
    """The request is invalid.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Bad Request"]


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


class Types_StatusCodes_StatusCode404(TypedDict, total=False):
    """The server cannot find the requested resource.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Not Found"]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


class UpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
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
