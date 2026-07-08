# AUTO-GENERATED from porting-sdk/rest-apis/logs/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class ChargeDetails(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    charge: str


class ConferenceLogPaginationLinks(TypedDict, total=False):
    """Pagination links for conference log list responses.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    self: str
    first: str
    next: str
    prev: str


class ConferenceLogsStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class ConferencesResponse(TypedDict, total=False):
    """Response containing a list of conferences.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: ConferenceLogPaginationLinks
    data: list[CxmlConference | RelayConference | VideoRoomSessionConference]


class CxmlConference(TypedDict, total=False):
    """Core conference object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    created_at: str
    project_id: uuid
    region: str
    name: str | None
    status: str | None
    max_size: int | None
    current_participants: int
    updated_at: str
    type: Literal["cxml_conference"]


class RelayConference(TypedDict, total=False):
    """Core conference object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    created_at: str
    project_id: uuid
    region: str
    name: str | None
    status: str | None
    max_size: int | None
    current_participants: int
    updated_at: str
    type: Literal["relay_conference"]
    recording_url: str | None
    recording_duration: int | None
    recording_file_size: int | None


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


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


class VideoRoomSessionConference(TypedDict, total=False):
    """Core conference object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    created_at: str
    source: str
    type: Literal["video_conference_session", "video_room_session"]
    url: str
    room_name: str | None
    status: str | None
    locked: bool
    started_at: str | None
    ended_at: str | None
    charge: str
    charge_details: list[ChargeDetails]


uuid: TypeAlias = "str"

ListConferencesResponse: TypeAlias = "ConferencesResponse"
