# AUTO-GENERATED from porting-sdk/rest-apis/logs/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``logs`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class ChargeDetails(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        description: Description for this charge.
        charge: Charge amount in dollars.
    """

    description: str
    charge: str


class ConferenceLogPaginationLinks(TypedDict, total=False):
    """Pagination links for conference log list responses.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        self: Link to the current page.
        first: Link to the first page.
        next: Link to the next page. Only present when there are more results.
        prev: Link to the previous page. Only present when not on the first page.
    """

    self: str
    first: str
    next: str
    prev: str


class ConferenceLogsStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class ConferencesResponse(TypedDict, total=False):
    """Response containing a list of conferences.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: A list of conference logs.
    """

    links: ConferenceLogPaginationLinks
    data: list[CxmlConference | RelayConference | VideoRoomSessionConference]


class CxmlConference(TypedDict, total=False):
    """Core conference object.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique identifier for the conference.
        created_at: Creation timestamp.
        project_id: Project ID of the conference.
        region: Region of the conference.
        name: Name of the conference.
        status: Status of the conference.
        max_size: Maximum size of the conference.
        current_participants: Current participants in the conference.
        updated_at: Updated timestamp.
        type: Type of the conference.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique identifier for the conference.
        created_at: Creation timestamp.
        project_id: Project ID of the conference.
        region: Region of the conference.
        name: Name of the conference.
        status: Status of the conference.
        max_size: Maximum size of the conference.
        current_participants: Current participants in the conference.
        updated_at: Updated timestamp.
        type: Type of the conference.
        recording_url: Recording URL of the conference.
        recording_duration: Recording duration of the conference.
        recording_file_size: Recording file size of the conference.
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


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


class VideoRoomSessionConference(TypedDict, total=False):
    """Core conference object.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique identifier for the conference.
        created_at: Creation timestamp.
        source: Source of the conference.
        type: Type of the conference.
        url: URL of the conference room session.
        room_name: Name of the conference room.
        status: Status of the conference.
        locked: Whether the conference is locked.
        started_at: Timestamp when the conference started.
        ended_at: Timestamp when the conference ended.
        charge: Total charge amount of the conference in dollars.
        charge_details: Details on charges associated with this conference.
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
