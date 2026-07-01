# AUTO-GENERATED from porting-sdk/rest-apis/video/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


class ActiveSession(TypedDict, total=False):
    """Active session information for a room.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    room_id: str
    name: str
    display_name: str
    join_from: str
    join_until: str
    remove_at: str
    remove_after_seconds_elapsed: int
    layout: str
    max_members: int
    fps: VideoFps
    quality: VideoQuality
    start_time: str
    end_time: str
    duration: int
    status: RoomSessionStatus
    record_on_start: bool
    enable_room_previews: bool
    preview_url: str
    audio_video_sync: bool


class ChargeDetail(TypedDict, total=False):
    """Charge detail item for logs.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    charge: float


class Conference(TypedDict, total=False):
    """Video conference response object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    name: str
    display_name: str | None
    description: str | None
    join_from: str | None
    join_until: str | None
    quality: VideoQuality
    layout: VideoLayout
    size: ConferenceSize | None
    record_on_start: bool
    tone_on_entry_and_exit: bool
    user_join_video_off: bool
    room_join_video_off: bool
    enable_chat: bool
    enable_room_previews: bool | None
    dark_primary: str | None
    dark_background: str | None
    dark_foreground: str | None
    dark_success: str | None
    dark_negative: str | None
    light_primary: str | None
    light_background: str | None
    light_foreground: str | None
    light_success: str | None
    light_negative: str | None
    meta: dict[str, Any] | None
    created_at: str
    updated_at: str
    active_session: ActiveSession


ConferenceSize: TypeAlias = "Literal['small', 'medium', 'large']"


class ConferenceToken(TypedDict, total=False):
    """A conference token object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    name: str | None
    token: str
    scopes: list[str]


class CreateConferenceRequest(TypedDict, total=False):
    """Request body for creating a conference.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    display_name: str
    description: str
    join_from: str
    join_until: str
    quality: VideoQuality
    layout: VideoLayout
    size: ConferenceSize
    record_on_start: bool
    enable_room_previews: bool
    enable_chat: bool
    dark_primary: str
    dark_background: str
    dark_foreground: str
    dark_success: str
    dark_negative: str
    light_primary: str
    light_background: str
    light_foreground: str
    light_success: str
    light_negative: str


class CreateRoomRequest(TypedDict, total=False):
    """Request body for creating a room.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    display_name: str
    description: str
    max_members: int
    quality: VideoQuality
    join_from: str
    join_until: str
    remove_at: str
    remove_after_seconds_elapsed: int
    layout: RoomLayout
    record_on_start: bool
    enable_room_previews: bool
    meta: dict[str, Any]
    sync_audio_video: bool


class CreateRoomTokenRequest(TypedDict, total=False):
    """Request body for creating a room token.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    room_name: str
    user_name: str
    permissions: list[RoomTokenPermission]
    join_from: str
    join_until: str
    remove_at: str
    remove_after_seconds_elapsed: int
    join_audio_muted: bool
    join_video_muted: bool
    auto_create_room: bool
    enable_room_previews: bool
    room_display_name: str
    end_room_session_on_leave: bool
    join_as: JoinAsType
    media_allowed: MediaAllowedType
    room_meta: dict[str, Any]
    meta: dict[str, Any]
    sync_audio_video: bool


class CreateStreamRequest(TypedDict, total=False):
    """Request body for creating a stream.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    url: str


class DiscardedLog(TypedDict, total=False):
    """A discarded/deleted video log entry. Returned when the log has been deleted. Only present when `include_deleted` is `true`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    discarded_at: str
    created_at: str


JoinAsType: TypeAlias = "Literal['audience', 'member']"


class ListConferenceTokensResponse(TypedDict, total=False):
    """List conference tokens response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[ConferenceToken]


class ListConferencesResponse(TypedDict, total=False):
    """List conferences response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[Conference]


class ListLogsResponse(TypedDict, total=False):
    """List logs response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[VideoLog]


class ListRoomRecordingEventsResponse(TypedDict, total=False):
    """List room recording events response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[RoomSessionEvent]


class ListRoomRecordingsResponse(TypedDict, total=False):
    """List room recordings response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[RoomRecording]


class ListRoomSessionEventsResponse(TypedDict, total=False):
    """List room session events response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[RoomSessionEvent]


class ListRoomSessionMembersResponse(TypedDict, total=False):
    """List room session members response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[RoomSessionMember]


class ListRoomSessionRecordingsResponse(TypedDict, total=False):
    """List room session recordings response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[RoomRecording]


class ListRoomSessionsResponse(TypedDict, total=False):
    """List room sessions response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[RoomSession]


class ListRoomsResponse(TypedDict, total=False):
    """List rooms response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[RoomResponse]


class ListStreamsResponse(TypedDict, total=False):
    """List streams response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[Stream]


class Log(TypedDict, total=False):
    """Log object representing a video activity entry.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    source: LogSource
    type: LogType
    url: str
    room_name: str | None
    status: LogStatus | None
    locked: bool
    started_at: str | None
    ended_at: str | None
    charge: float
    created_at: str
    charge_details: list[ChargeDetail]


LogSource: TypeAlias = "Literal['realtime_api']"

LogStatus: TypeAlias = "Literal['in-progress', 'completed']"

LogType: TypeAlias = "Literal['video_room_session', 'video_conference_session']"

MediaAllowedType: TypeAlias = "Literal['all', 'video-only', 'audio-only']"


class PaginationLinks(TypedDict, total=False):
    """Pagination links for list responses.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    self: str
    first: str
    next: str
    prev: str


RoomLayout: TypeAlias = "Literal['grid-responsive', 'grid-responsive-mobile', 'highlight-1-responsive', '1x1', '2x1', '2x2', '5up', '3x3', '4x4', '5x5', '6x6', '8x8', '10x10']"


class RoomRecording(TypedDict, total=False):
    """Room recording response object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    room_session_id: str
    status: RoomRecordingStatus | None
    started_at: str | None
    finished_at: str | None
    duration: int | None
    size_in_bytes: int | None
    format: str | None
    cost_in_dollars: float
    uri: str | None
    created_at: str
    updated_at: str


RoomRecordingStatus: TypeAlias = (
    "Literal['recording', 'paused', 'processing', 'completed']"
)


class RoomResponse(TypedDict, total=False):
    """Room response object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    name: str
    display_name: str | None
    description: str | None
    max_members: int
    quality: VideoQuality
    fps: int
    join_from: str | None
    join_until: str | None
    remove_at: str | None
    remove_after_seconds_elapsed: int | None
    layout: RoomLayout
    record_on_start: bool
    tone_on_entry_and_exit: bool
    room_join_video_off: bool
    user_join_video_off: bool
    enable_room_previews: bool | None
    sync_audio_video: bool | None
    meta: dict[str, Any] | None
    prioritize_handraise: bool
    active_session: ActiveSession
    created_at: str
    updated_at: str


class RoomSession(TypedDict, total=False):
    """Room session response object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    room_id: str | None
    name: str | None
    display_name: str | None
    max_members: int | None
    quality: VideoQuality | None
    fps: VideoFps | None
    join_from: str | None
    join_until: str | None
    remove_at: str | None
    remove_after_seconds_elapsed: int | None
    layout: str | None
    record_on_start: bool
    tone_on_entry_and_exit: bool
    room_join_video_off: bool
    user_join_video_off: bool
    locked: bool
    start_time: str | None
    end_time: str | None
    duration: int | None
    status: RoomSessionStatus | None
    created_at: str
    updated_at: str
    preview_url: str | None
    prioritize_handraise: bool | None
    sync_audio_video: bool | None
    cost_in_dollars: float
    enable_room_previews: bool
    locked_cover: str


class RoomSessionEvent(TypedDict, total=False):
    """Room session event response object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    project_id: str
    room_id: str
    room_session_id: str
    room_recording_id: str
    room_participant_id: str
    level: str
    name: str
    payload: dict[str, Any]
    created_at: str


class RoomSessionMember(TypedDict, total=False):
    """Room session member response object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    room_session_id: str
    name: str | None
    join_time: str | None
    leave_time: str | None
    duration: int | None
    cost_in_dollars: float


RoomSessionStatus: TypeAlias = "Literal['in-progress', 'completed']"


class RoomSessionSummary(TypedDict, total=False):
    """Room session summary, returned by the show endpoint. Omits list-only fields.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    room_id: str | None
    name: str | None
    display_name: str | None
    max_members: int | None
    quality: VideoQuality | None
    fps: VideoFps | None
    join_from: str | None
    join_until: str | None
    remove_at: str | None
    remove_after_seconds_elapsed: int | None
    layout: str | None
    record_on_start: bool
    tone_on_entry_and_exit: bool
    room_join_video_off: bool
    user_join_video_off: bool
    locked: bool
    start_time: str | None
    end_time: str | None
    duration: int | None
    status: RoomSessionStatus | None
    created_at: str
    updated_at: str
    preview_url: str | None
    prioritize_handraise: bool | None
    sync_audio_video: bool | None


RoomTokenPermission: TypeAlias = "Literal['room.member.audio_mute', 'room.member.audio_unmute', 'room.member.video_mute', 'room.member.video_unmute', 'room.member.deaf', 'room.member.undeaf', 'room.member.set_input_volume', 'room.member.set_output_volume', 'room.member.set_input_sensitivity', 'room.member.set_position', 'room.member.set_meta', 'room.member.raisehand', 'room.member.lowerhand', 'room.member.remove', 'room.member.promote', 'room.member.demote', 'room.hide_video_muted', 'room.list_available_layouts', 'room.lock', 'room.playback', 'room.playback_seek', 'room.prioritize_handraise', 'room.recording', 'room.set_layout', 'room.set_position', 'room.set_meta', 'room.show_video_muted', 'room.stream', 'room.unlock', 'room.self.audio_mute', 'room.self.audio_unmute', 'room.self.video_mute', 'room.self.video_unmute', 'room.self.deaf', 'room.self.undeaf', 'room.self.set_input_volume', 'room.self.set_output_volume', 'room.self.set_input_sensitivity', 'room.self.set_position', 'room.self.set_meta', 'room.self.raisehand', 'room.self.lowerhand', 'room.self.screenshare', 'room.self.additional_source']"


class RoomTokenResponse(TypedDict, total=False):
    """Room token response object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    token: str


class Stream(TypedDict, total=False):
    """A video stream object.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    url: str | None
    stream_type: str | None
    width: int | None
    height: int | None
    fps: int | None
    created_at: str
    updated_at: str


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


class Types_StatusCodes_StatusCode403(TypedDict, total=False):
    """Access is forbidden.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Forbidden"]


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


class UpdateConferenceRequest(TypedDict, total=False):
    """Request body for updating a conference.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    display_name: str
    description: str
    join_from: str
    join_until: str
    quality: VideoQuality
    layout: VideoLayout
    size: ConferenceSize
    record_on_start: bool
    tone_on_entry_and_exit: bool
    room_join_video_off: bool
    user_join_video_off: bool
    enable_room_previews: bool
    enable_chat: bool
    dark_primary: str
    dark_background: str
    dark_foreground: str
    dark_success: str
    dark_negative: str
    light_primary: str
    light_background: str
    light_foreground: str
    light_success: str
    light_negative: str


class UpdateRoomRequest(TypedDict, total=False):
    """Request body for updating a room.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    display_name: str
    description: str
    max_members: int
    quality: VideoQuality
    join_from: str
    join_until: str
    remove_at: str
    remove_after_seconds_elapsed: int
    layout: RoomLayout
    record_on_start: bool
    enable_room_previews: bool
    meta: dict[str, Any]
    sync_audio_video: bool


class UpdateStreamRequest(TypedDict, total=False):
    """Request body for updating a stream.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    url: str


VideoFps: TypeAlias = "Literal[20, 30]"

VideoLayout: TypeAlias = "Literal['grid-responsive', 'grid-responsive-mobile', 'highlight-1-responsive', '1x1', '2x1', '2x2', '5up', '3x3', '4x4', '5x5', '6x6', '8x8', '10x10']"

VideoLog: TypeAlias = "Log | DiscardedLog"

VideoQuality: TypeAlias = "Literal['720p', '1080p']"


class VideoStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


GetConferenceTokenResponse: TypeAlias = "ConferenceToken"
ResetConferenceTokenResponse: TypeAlias = "ConferenceToken"
CreateVideoConferenceRequest: TypeAlias = "CreateConferenceRequest"
CreateVideoConferenceResponse: TypeAlias = "Conference"
ListVideoConferencesResponse: TypeAlias = "ListConferencesResponse"
GetVideoConferenceResponse: TypeAlias = "Conference"
UpdateVideoConferenceRequest: TypeAlias = "UpdateConferenceRequest"
UpdateVideoConferenceResponse: TypeAlias = "Conference"
ListConferenceStreamsResponse: TypeAlias = "ListStreamsResponse"
CreateConferenceStreamRequest: TypeAlias = "CreateStreamRequest"
CreateConferenceStreamResponse: TypeAlias = "Stream"
GetLogResponse: TypeAlias = "VideoLog"
GetRoomRecordingResponse: TypeAlias = "RoomRecording"
GetRoomSessionResponse: TypeAlias = "RoomSessionSummary"
CreateRoomTokenResponse: TypeAlias = "RoomTokenResponse"
CreateRoomResponse: TypeAlias = "RoomResponse"
GetRoomResponse: TypeAlias = "RoomResponse"
UpdateRoomResponse: TypeAlias = "RoomResponse"
ListRoomStreamsResponse: TypeAlias = "ListStreamsResponse"
CreateRoomStreamRequest: TypeAlias = "CreateStreamRequest"
CreateRoomStreamResponse: TypeAlias = "Stream"
GetRoomByNameResponse: TypeAlias = "RoomResponse"
GetStreamResponse: TypeAlias = "Stream"
UpdateStreamResponse: TypeAlias = "Stream"
