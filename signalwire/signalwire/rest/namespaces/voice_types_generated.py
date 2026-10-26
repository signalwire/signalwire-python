# AUTO-GENERATED from porting-sdk/rest-apis/voice/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``voice`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


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


class DialogflowVoiceLog(TypedDict, total=False):
    """Voice log for Dialogflow call types.

    Returned when `type` is `dialogflow_call`.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The origin phone number.

    Attributes:
        id: A unique identifier for the log.
        to: The destination phone number.
        source: Source of this log entry.
        charge: The charge in dollars.
        charge_details: Details on charges associated with this log.
        created_at: Date and time when the call entry was created.
        type: Type of this log entry.
        url: Always null for this call type.
        status: The status of the voice activity.
        duration: The duration of the voice activity in seconds.
    """

    id: uuid
    # non-identifier field 'from': str
    to: str
    source: VoiceSources
    charge: float
    charge_details: list[ChargeDetail]
    created_at: str
    type: Literal["dialogflow_call"]
    url: None
    status: VoiceLogStatus
    duration: int | None


class DiscardedVoiceLog(TypedDict, total=False):
    """A discarded/deleted voice log entry.

    Returned when the log has been deleted. Only present when `include_deleted` is
    `true`.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: A unique identifier for the log.
        discarded_at: Date and time when the log was discarded.
        created_at: Date and time when the log was originally created.
    """

    id: uuid
    discarded_at: str
    created_at: str


class FabricVoiceLog(TypedDict, total=False):
    """Voice log for Fabric Subscriber Device call types.

    Returned when `type` is `fabric_subscriber_device_leg`.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The origin phone number.

    Attributes:
        id: A unique identifier for the log.
        to: The destination phone number.
        source: Source of this log entry.
        charge: The charge in dollars.
        charge_details: Details on charges associated with this log.
        created_at: Date and time when the call entry was created.
        type: Type of this log entry.
        url: Always null for this call type.
        direction: The direction of the voice activity.
        status: The status of the voice activity. Always null for this call type.
    """

    id: uuid
    # non-identifier field 'from': str
    to: str
    source: VoiceSources
    charge: float
    charge_details: list[ChargeDetail]
    created_at: str
    type: Literal["fabric_subscriber_device_leg"]
    url: None
    direction: VoiceDirection
    status: VoiceLogStatus | None


class LogEvent(TypedDict, total=False):
    """Event entry for a voice log.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        event_at: Timestamp when the event occurred.
        level: Log level of the event.
        name: Name of the event.
        details: Additional details about the event. Structure varies by event type.
        project_id: Unique identifier for the project.
        log_id: Unique identifier for the log.
    """

    event_at: str
    level: Literal["info", "warn", "error", "debug"]
    name: str
    details: dict[str, Any]
    project_id: uuid
    log_id: uuid


class LogEventsListResponse(TypedDict, total=False):
    """Response model for log events list endpoint.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        data: Array of event entries for the log
    """

    data: list[LogEvent]


class LogListResponse(TypedDict, total=False):
    """Response model for voice log list endpoint.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links
        data: Array of voice log entries
    """

    links: LogPaginationResponse
    data: list[VoiceLog]


class LogPaginationResponse(TypedDict, total=False):
    """Pagination links for voice log list responses.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        self: URL of the current page.
        first: URL of the first page.
        next: URL of the next page. Absent on the last page.
        prev: URL of the previous page. Absent on the first page.
    """

    self: str
    first: str
    next: str
    prev: str


class RelayVoiceLog(TypedDict, total=False):
    """Voice log for Compatibility and Relay call types.

    Returned when `type` is `laml_call`, `relay_pstn_call`, `relay_sip_call`, or
    `relay_webrtc_call`.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The origin phone number.

    Attributes:
        id: A unique identifier for the log.
        to: The destination phone number.
        source: Source of this log entry.
        charge: The charge in dollars.
        charge_details: Details on charges associated with this log.
        created_at: Date and time when the call entry was created.
        type: Type of this log entry.
        url: URL for the resource associated with this log entry. Present for LAML
            calls, null for Relay calls.
        direction: The direction of the voice activity.
        status: The status of the voice activity.
        duration: The duration of the voice activity in seconds.
        duration_ms: The duration of the voice activity in milliseconds.
        billing_ms: The billable duration of the voice activity in milliseconds.
        parent_id: Parent log identifier for related call entries.
    """

    id: uuid
    # non-identifier field 'from': str
    to: str
    source: VoiceSources
    charge: float
    charge_details: list[ChargeDetail]
    created_at: str
    type: RelayVoiceType
    url: str | None
    direction: VoiceDirection
    status: VoiceLogStatus
    duration: int | None
    duration_ms: int | None
    billing_ms: int | None
    parent_id: str | None


RelayVoiceType: TypeAlias = (
    "Literal['laml_call', 'relay_pstn_call', 'relay_sip_call', 'relay_webrtc_call']"
)


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


class Types_StatusCodes_StatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


class VideoRoomVoiceLog(TypedDict, total=False):
    """Voice log for audio legs in a Video Room.

    Returned when `type` is `video_room_pstn_leg` or `video_room_sip_leg`.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The origin phone number.

    Attributes:
        id: A unique identifier for the log.
        to: The destination phone number.
        source: Source of this log entry.
        charge: The charge in dollars.
        charge_details: Details on charges associated with this log.
        created_at: Date and time when the call entry was created.
        type: Type of this log entry.
        url: Always null for this call type.
        direction: The direction of the voice activity.
        status: The status of the voice activity.
        duration: The duration of the voice activity in seconds.
        duration_ms: The duration of the voice activity in milliseconds.
    """

    id: uuid
    # non-identifier field 'from': str
    to: str
    source: VoiceSources
    charge: float
    charge_details: list[ChargeDetail]
    created_at: str
    type: VideoRoomVoiceType
    url: None
    direction: VoiceDirection
    status: VoiceLogStatus
    duration: int | None
    duration_ms: int | None


VideoRoomVoiceType: TypeAlias = "Literal['video_room_pstn_leg', 'video_room_sip_leg']"

VoiceDirection: TypeAlias = (
    "Literal['inbound', 'outbound', 'outbound-api', 'outbound-dial']"
)

VoiceLog: TypeAlias = "RelayVoiceLog | VideoRoomVoiceLog | DialogflowVoiceLog | FabricVoiceLog | DiscardedVoiceLog"

VoiceLogStatus: TypeAlias = "Literal['queued', 'initiated', 'ringing', 'in-progress', 'busy', 'failed', 'no-answer', 'canceled', 'completed', 'ended', 'answered', 'created', 'ending', 'joined']"


class VoiceLogsListStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


VoiceSources: TypeAlias = "Literal['dialogflow', 'laml', 'realtime_api']"

uuid: TypeAlias = "str"

ListVoiceLogsResponse: TypeAlias = "LogListResponse"
GetVoiceLogResponse: TypeAlias = "VoiceLog"
ListVoiceLogEventsResponse: TypeAlias = "LogEventsListResponse"
