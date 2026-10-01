# AUTO-GENERATED from porting-sdk/rest-apis/voice/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


class ChargeDetail(TypedDict, total=False):
    """Details on charges associated with this log.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    charge: float


DialogflowVoiceLog = TypedDict(
    "DialogflowVoiceLog",
    {
        "id": "uuid",
        "from": "str",
        "to": "str",
        "source": "VoiceSources",
        "charge": "float",
        "charge_details": "list[ChargeDetail]",
        "created_at": "str",
        "type": "Literal['dialogflow_call']",
        "url": "None",
        "status": "VoiceLogStatus",
        "duration": "int | None",
    },
    total=False,
)
DialogflowVoiceLog.__doc__ = """Voice log for Dialogflow call types. Returned when `type` is `dialogflow_call`.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""


class DiscardedVoiceLog(TypedDict, total=False):
    """A discarded/deleted voice log entry. Returned when the log has been deleted. Only present when `include_deleted` is `true`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    discarded_at: str
    created_at: str


FabricVoiceLog = TypedDict(
    "FabricVoiceLog",
    {
        "id": "uuid",
        "from": "str",
        "to": "str",
        "source": "VoiceSources",
        "charge": "float",
        "charge_details": "list[ChargeDetail]",
        "created_at": "str",
        "type": "Literal['fabric_subscriber_device_leg']",
        "url": "None",
        "direction": "VoiceDirection",
        "status": "VoiceLogStatus | None",
    },
    total=False,
)
FabricVoiceLog.__doc__ = """Voice log for Fabric Subscriber Device call types. Returned when `type` is `fabric_subscriber_device_leg`.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""


class LogEvent(TypedDict, total=False):
    """Event entry for a voice log

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    event_at: str
    level: Literal["info", "warn", "error", "debug"]
    name: str
    details: dict[str, Any]
    project_id: uuid
    log_id: uuid


class LogEventsListResponse(TypedDict, total=False):
    """Response model for log events list endpoint

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    data: list[LogEvent]


class LogListResponse(TypedDict, total=False):
    """Response model for voice log list endpoint

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: LogPaginationResponse
    data: list[VoiceLogListItem]


class LogPaginationResponse(TypedDict, total=False):
    """Pagination links for voice log list responses

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    self: str
    first: str
    next: str
    prev: str


RelayVoiceLog = TypedDict(
    "RelayVoiceLog",
    {
        "id": "uuid",
        "from": "str",
        "to": "str",
        "source": "VoiceSources",
        "charge": "float",
        "charge_details": "list[ChargeDetail]",
        "created_at": "str",
        "type": "RelayVoiceType",
        "url": "str | None",
        "direction": "VoiceDirection",
        "status": "VoiceLogStatus",
        "duration": "int | None",
        "duration_ms": "int | None",
        "billing_ms": "int | None",
        "parent_id": "str | None",
        "audio_in_mos": "str | None",
        "audio_in_jitter_min": "float | str | None",
        "audio_in_jitter_max": "float | str | None",
        "audio_out_jitter_min": "float | str | None",
        "audio_out_jitter_max": "float | str | None",
        "audio_out_jitter_avg": "float | str | None",
        "audio_rtt_avg": "float | str | None",
        "audio_rtt_min": "float | str | None",
        "audio_rtt_max": "float | str | None",
        "audio_in_media_packet_count": "float | str | None",
        "audio_out_packet_count": "float | str | None",
        "audio_out_media_packet_count": "float | str | None",
        "audio_out_lost": "float | str | None",
        "audio_in_mean_interval": "float | str | None",
        "audio_in_dtmf_packet_count": "float | str | None",
        "audio_out_dtmf_packet_count": "float | str | None",
        "audio_in_skip_packet_count": "float | str | None",
        "audio_in_flush_packet_count": "float | str | None",
        "audio_in_largest_jb_size": "float | str | None",
    },
    total=False,
)
RelayVoiceLog.__doc__ = """Voice log for cXML and Relay call types. Returned when `type` is `laml_call`, `relay_pstn_call`, `relay_sip_call`, or `relay_webrtc_call`.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""

RelayVoiceType: TypeAlias = (
    "Literal['laml_call', 'relay_pstn_call', 'relay_sip_call', 'relay_webrtc_call']"
)


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


class Types_StatusCodes_StatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


VideoRoomVoiceLog = TypedDict(
    "VideoRoomVoiceLog",
    {
        "id": "uuid",
        "from": "str",
        "to": "str",
        "source": "VoiceSources",
        "charge": "float",
        "charge_details": "list[ChargeDetail]",
        "created_at": "str",
        "type": "VideoRoomVoiceType",
        "url": "None",
        "direction": "VoiceDirection",
        "status": "VoiceLogStatus",
        "duration": "int | None",
        "duration_ms": "int | None",
    },
    total=False,
)
VideoRoomVoiceLog.__doc__ = """Voice log for audio legs in a Video Room. Returned when `type` is `video_room_pstn_leg` or `video_room_sip_leg`.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""

VideoRoomVoiceType: TypeAlias = "Literal['video_room_pstn_leg', 'video_room_sip_leg']"

VoiceDirection: TypeAlias = (
    "Literal['inbound', 'outbound', 'outbound-api', 'outbound-dial']"
)

VoiceLog: TypeAlias = "RelayVoiceLog | VideoRoomVoiceLog | DialogflowVoiceLog | FabricVoiceLog | DiscardedVoiceLog"

VoiceLogListItem: TypeAlias = (
    "RelayVoiceLog | VideoRoomVoiceLog | DialogflowVoiceLog | FabricVoiceLog"
)

VoiceLogStatus: TypeAlias = "Literal['queued', 'initiated', 'ringing', 'in-progress', 'busy', 'failed', 'no-answer', 'canceled', 'completed', 'ended', 'answered', 'created', 'ending', 'joined']"


class VoiceLogsListStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


VoiceSources: TypeAlias = "Literal['dialogflow', 'laml', 'realtime_api']"

uuid: TypeAlias = "str"

ListVoiceLogsResponse: TypeAlias = "LogListResponse"
GetVoiceLogResponse: TypeAlias = "VoiceLog"
ListVoiceLogEventsResponse: TypeAlias = "LogEventsListResponse"
