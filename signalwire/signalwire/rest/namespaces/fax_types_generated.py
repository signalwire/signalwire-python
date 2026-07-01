# AUTO-GENERATED from porting-sdk/rest-apis/fax/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class ChargeDetail(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    charge: float


class FaxLog(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

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
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class FaxLogsListStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class LogListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    links: LogPaginationResponse
    data: list[FaxLog]


class LogPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class LogResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

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

ListFaxLogsResponse: TypeAlias = "LogListResponse"
GetFaxLogResponse: TypeAlias = "LogResponse"
