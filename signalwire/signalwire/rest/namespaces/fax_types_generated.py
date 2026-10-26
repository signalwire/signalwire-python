# AUTO-GENERATED from porting-sdk/rest-apis/fax/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``fax`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class ChargeDetail(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        description: Description for this charge.
        charge: Charged amount.
    """

    description: str
    charge: float


class FaxLog(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str | None``): The origin phone number in E.164 format.

    Attributes:
        id: A unique identifier for the log
        to: The destination phone number in E.164 format.
        status: The status of this fax call.
        direction: The direction of this fax call.
        source: Source of this log entry.
        type: Type of this log entry.
        url: URL for the associated fax resource with this log entry.
        remote_station: Represents a customer hosted Fax server.
        charge: The amount charged for this fax request.
        number_of_pages: The number of pages the fax document contained.
        quality: The quality that was set when the fax document was sent.
        charge_details: Details on charges associated with this log.
        created_at: Date and time when the fax was created.
        error_code: Error code for this resource (if available).
        error_message: The description of this error (if available).
    """

    id: uuid
    # non-identifier field 'from': str | None
    to: str | None
    status: Literal[
        "queued",
        "initiated",
        "ringing",
        "in-progress",
        "busy",
        "failed",
        "no-answer",
        "canceled",
        "completed",
    ]
    direction: Literal["inbound", "outbound-api", "outbound-dial"] | None
    source: Literal["laml"]
    type: Literal["laml_call"]
    url: str
    remote_station: str | None
    charge: float
    number_of_pages: int | None
    quality: Literal["fine", "standard", "superfine"] | None
    charge_details: list[ChargeDetail]
    created_at: str
    error_code: str | None
    error_message: str | None


class FaxLogShowStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class FaxLogsListStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class LogListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        links: Object containing pagination links
        data: Array of log data
    """

    links: LogPaginationResponse
    data: list[FaxLog]


class LogPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        self: URL for the current page of results.
        first: URL for the first page of results.
        next: URL for the next page of results. Only present when more results are
            available.
        prev: URL for the previous page of results. Only present when on page 1 or
            later.
    """

    self: str
    first: str
    next: str
    prev: str


class LogResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str | None``): The origin phone number in E.164 format.

    Attributes:
        id: A unique identifier for the log
        to: The destination phone number in E.164 format.
        status: The status of this fax call.
        direction: The direction of this fax call.
        source: Source of this log entry.
        type: Type of this log entry.
        url: URL for the associated fax resource with this log entry.
        remote_station: Represents a customer hosted Fax server.
        charge: The amount charged for this fax request.
        number_of_pages: The number of pages the fax document contained.
        quality: The quality that was set when the fax document was sent.
        charge_details: Details on charges associated with this log.
        created_at: Date and time when the fax was created.
        error_code: Error code for this resource (if available).
        error_message: The description of this error (if available).
    """

    id: uuid
    # non-identifier field 'from': str | None
    to: str | None
    status: Literal[
        "queued",
        "initiated",
        "ringing",
        "in-progress",
        "busy",
        "failed",
        "no-answer",
        "canceled",
        "completed",
    ]
    direction: Literal["inbound", "outbound-api", "outbound-dial"] | None
    source: Literal["laml"]
    type: Literal["laml_call"]
    url: str
    remote_station: str | None
    charge: float
    number_of_pages: int | None
    quality: Literal["fine", "standard", "superfine"] | None
    charge_details: list[ChargeDetail]
    created_at: str
    error_code: str | None
    error_message: str | None


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


uuid: TypeAlias = "str"

ListFaxLogsResponse: TypeAlias = "LogListResponse"
GetFaxLogResponse: TypeAlias = "LogResponse"
