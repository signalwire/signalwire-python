# AUTO-GENERATED from porting-sdk/rest-apis/message/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class ChargeDetail(TypedDict, total=False):
    """Details on charges associated with this log.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    charge: float


class LogListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    links: LogPaginationResponse
    data: list[MessageLog]


class LogPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class LogRetrieveResponse(TypedDict, total=False):
    """Response model for message log retrieve endpoint

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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
    """Message log entry with all activity details

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class MessageLogsListStatusCode422(TypedDict, total=False):
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


uuid: TypeAlias = "str"

ListMessageLogsResponse: TypeAlias = "LogListResponse"
GetMessageLogResponse: TypeAlias = "LogRetrieveResponse"
