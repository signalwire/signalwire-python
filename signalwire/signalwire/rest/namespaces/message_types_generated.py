# AUTO-GENERATED from porting-sdk/rest-apis/message/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``message`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class ChargeDetail(TypedDict, total=False):
    """Details on charges associated with this log.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        description: Description for this charge.
        charge: Charged amount.
    """

    description: str
    charge: float


class LogListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        links: Object containing pagination links
        data: Array of message log entries
    """

    links: LogPaginationResponse
    data: list[MessageLog]


class LogPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        self: URL to current page
        first: URL to first page
        next: URL to next page (if available)
        prev: URL to previous page (if available)
    """

    self: str
    first: str
    next: str
    prev: str


class LogRetrieveResponse(TypedDict, total=False):
    """Response model for message log retrieve endpoint.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The origin phone number.

    Attributes:
        id: A unique identifier for the log.
        to: The destination phone number.
        status: The status of the message.
        direction: The direction of the message.
        kind: The kind of message.
        source: Source of this log entry.
        type: Type of this log entry.
        url: URL for the resource associated with this log entry. Null for Relay
            messages.
        number_of_segments: The number of segments.
        charge: The charge in dollars.
        charge_details: Details on charges associated with this log.
        created_at: Date and time when the message entry was created.
    """

    id: uuid
    # non-identifier field 'from': str
    to: str
    status: Literal[
        "queued", "initiated", "delivered", "sent", "received", "undelivered", "failed"
    ]
    direction: Literal[
        "inbound", "outbound", "outbound-api", "outbound-call", "outbound-reply"
    ]
    kind: Literal["sms", "mms"]
    source: Literal["realtime_api", "laml"]
    type: Literal["relay_message", "laml_message"]
    url: str | None
    number_of_segments: int
    charge: float
    charge_details: list[ChargeDetail]
    created_at: str


class MessageLog(TypedDict, total=False):
    """Message log entry with all activity details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The origin phone number.

    Attributes:
        id: A unique identifier for the log.
        to: The destination phone number.
        status: The status of the message.
        direction: The direction of the message.
        kind: The kind of message.
        source: Source of this log entry.
        type: Type of this log entry.
        url: URL for the resource associated with this log entry. Null for Relay
            messages.
        number_of_segments: The number of segments.
        charge: The charge in dollars.
        charge_details: Details on charges associated with this log.
        created_at: Date and time when the message entry was created.
    """

    id: uuid
    # non-identifier field 'from': str
    to: str
    status: Literal[
        "queued", "initiated", "delivered", "sent", "received", "undelivered", "failed"
    ]
    direction: Literal[
        "inbound", "outbound", "outbound-api", "outbound-call", "outbound-reply"
    ]
    kind: Literal["sms", "mms"]
    source: Literal["realtime_api", "laml"]
    type: Literal["relay_message", "laml_message"]
    url: str | None
    number_of_segments: int
    charge: float
    charge_details: list[ChargeDetail]
    created_at: str


class MessageLogShowStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class MessageLogsListStatusCode422(TypedDict, total=False):
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


uuid: TypeAlias = "str"

ListMessageLogsResponse: TypeAlias = "LogListResponse"
GetMessageLogResponse: TypeAlias = "LogRetrieveResponse"
