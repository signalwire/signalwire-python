# AUTO-GENERATED from porting-sdk/rest-apis/video/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``video`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


class ActiveSession(TypedDict, total=False):
    """Active session information for a room.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique ID of the session.
        room_id: Unique ID of the Room if the Session was created from a Room and was
            not an auto-created Session.
        name: The named identifier of room session.
        display_name: Display name of room, no character limitations. Maximum of 200
            characters. Defaults to the value of name.
        join_from: Room Session does not accept new Members before this time.
        join_until: Room Session stops accepting new Members at this time.
        remove_at: Remove Members from the Room Session at this time.
        remove_after_seconds_elapsed: Remove Members after they are in the Room Session
            for N seconds.
        layout: The Room Session's initial layout. See documentation for a full list of
            supported layouts.
        max_members: The maximum number of members allowed in the room at a time.
        fps: The Room Session's frames per second.
        quality: The Room Session's resolution.
        start_time: Start time of the session.
        end_time: End time of the session.
        duration: How long, in seconds, the Room Session lasted.
        status: Status of the session.
        record_on_start: Whether a recording was automatically started when this Room
            Session began.
        enable_room_previews: Whether a video with a preview of the content of the room
            is to be generated.
        preview_url: If room previews are enabled and the room session is in progress,
            this is the URL of the preview video.
        audio_video_sync: Enable/disable jitter buffer audio-video sync.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        description: Description for this charge.
        charge: Charged amount, in dollars.
    """

    description: str
    charge: float


class Conference(TypedDict, total=False):
    """Video conference response object.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique ID of the video conference.
        name: A named unique identifier for the conference. Allowed characters:
            `A-Za-z0-9_-`.
        display_name: Display name of the video conference. Maximum of 200 characters.
        description: Description of the conference. Maximum of 3000 characters.
        join_from: Conference does not accept new participants before this time.
        join_until: Conference stops accepting new participants at this time, but keeps
            running until all participants leave.
        quality: The conference's resolution.
        layout: The conference's initial layout.
        size: The size of the video conference.
        record_on_start: Whether to start recording when a conference session begins.
        tone_on_entry_and_exit: Whether a tone is played when a member enters or exits
            the conference.
        user_join_video_off: Whether participants join with video off by user setting.
        room_join_video_off: Whether participants join with video off by room setting.
        enable_chat: Whether group chat is enabled for conference participants.
        enable_room_previews: Whether a preview video of the conference content is
            generated.
        dark_primary: CTA buttons and selected items color (dark theme).
        dark_background: Main background color (dark theme).
        dark_foreground: Main foreground color (dark theme).
        dark_success: Success indication color (dark theme).
        dark_negative: Error indication color (dark theme).
        light_primary: CTA buttons and selected items color (light theme).
        light_background: Main background color (light theme).
        light_foreground: Main foreground color (light theme).
        light_success: Success indication color (light theme).
        light_negative: Error indication color (light theme).
        meta: User-defined metadata for the conference.
        created_at: Timestamp when the conference was created.
        updated_at: Timestamp when the conference was last updated.
        active_session: Active session information. Only present when requested via the
            `include_active_session` query parameter.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique identifier for the conference token.
        name: Name of the conference token.
        token: Conference token's randomly generated sequence.
        scopes: List of permissions.
    """

    id: str
    name: str | None
    token: str
    scopes: list[str]


class CreateConferenceRequest(TypedDict, total=False):
    """Request body for creating a conference.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: A named unique identifier for the conference. Allowed characters:
            `A-Za-z0-9_-`. Maximum of 100 characters.
        display_name: Display name of the video conference. Maximum of 200 characters.
        description: Description of the conference. Maximum of 3000 characters.
        join_from: Conference does not accept new participants before this time. Expects
            RFC 3339 datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be
            converted to `2022-01-01T00:00:00Z`.
        join_until: Conference stops accepting new participants at this time, but keeps
            running until all participants leave. Expects RFC 3339 datetime:
            `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted to
            `2022-01-01T00:00:00Z`.
        quality: The conference's resolution.
        layout: The conference's initial layout.
        size: The size of the video conference.
        record_on_start: Whether to start recording when a conference session begins.
        enable_room_previews: Whether a preview video of the conference content is
            generated.
        enable_chat: Whether group chat is enabled for conference participants.
        dark_primary: CTA buttons and selected items color (dark theme).
        dark_background: Main background color (dark theme).
        dark_foreground: Main foreground color (dark theme).
        dark_success: Success indication color (dark theme).
        dark_negative: Error indication color (dark theme).
        light_primary: CTA buttons and selected items color (light theme).
        light_background: Main background color (light theme).
        light_foreground: Main foreground color (light theme).
        light_success: Success indication color (light theme).
        light_negative: Error indication color (light theme).
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: A named unique identifier for the room. Allowed characters: `A-Za-z0-9_-`.
            Maximum of 100 characters.
        display_name: Display name of the room. Maximum of 200 characters. Defaults to
            the value of name.
        description: Description of the room. Maximum of 3000 characters.
        max_members: The maximum number of members in the room at a time. Must be at
            least 1 to a maximum of 300.
        quality: The room's resolution.
        join_from: Room does not accept new participants before this time. Expects RFC
            3339 datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be
            converted to `2022-01-01T00:00:00Z`.
        join_until: Room stops accepting new participants at this time, but keeps
            running until all participants leave. Expects RFC 3339 datetime:
            `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted to
            `2022-01-01T00:00:00Z`.
        remove_at: Remove users from the room at this time. Expects RFC 3339 datetime:
            `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted to
            `2022-01-01T00:00:00Z`.
        remove_after_seconds_elapsed: Remove users after they are in the room for N
            seconds.
        layout: The room's initial layout.
        record_on_start: Specifies whether to start recording a Room Session when one is
            started for this Room.
        enable_room_previews: Whether a video with a preview of the content of the room
            is to be generated.
        meta: User-defined metadata for the room. Must be a valid JSON object. Maximum
            of 2000 characters when serialized.
        sync_audio_video: Enable/disable jitter buffer audio-video sync.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        room_name: Room's unique named identifier. Allowed characters: A-Za-z0-9_-. Up
            to 100 characters. The room does not have to exist when the token is
            created, but must exist prior to joining, or ensure auto_create_room is set
            to true.
        user_name: A display name to use for the user. Up to 100 characters. (If not
            supplied, a random alphanumeric string will be returned for each
            authorization with this token.)
        permissions: A list of permissions, which define what user can do once they join
            the room. If `join_as` is `audience`, permissions are set to an empty array
            regardless of the value provided.
        join_from: The user can't join the room before this time. Expects RFC 3339
            datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted
            to `2022-01-01T00:00:00Z`
        join_until: The user can't join the room after this time. Expects RFC 3339
            datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted
            to `2022-01-01T00:00:00Z`
        remove_at: Remove user from the room at this time. Expects RFC 3339 datetime:
            `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted to
            `2022-01-01T00:00:00Z`
        remove_after_seconds_elapsed: Remove user after they are in the room for N
            seconds.
        join_audio_muted: Whether the user joins the room with their audio muted.
        join_video_muted: Whether the user joins the room with their video muted.
        auto_create_room: By default, if the user tries to use this token to join a room
            that doesn't exist, it will be created with default configuration. Set this
            to false to require the room to exist beforehand.
        enable_room_previews: Whether to generate a video with a preview of the content
            of the room. This parameter has effect only if this token auto-creates the
            room, thus it will be ignored if the room already exists.
        room_display_name: Display name used if a room is auto-created when the token
            joins. Maximum of 200 characters. Defaults to the value of room_name.
        end_room_session_on_leave: Whether to end the room session when the member using
            this token leaves the room.
        join_as: Whether the user should join as a member or as a non-interactive
            audience participant. Audience participants cannot send audio or video.
        media_allowed: Indicates what media the user is allowed to receive.
        room_meta: Set the room meta. Maximum of 2000 characters when serialized to
            JSON.
        meta: Set the member meta. Maximum of 2000 characters when serialized to JSON.
        sync_audio_video: Enable/disable jitter buffer audio-video sync.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        url: RTMP or RTMPS URL. This must be the address of a server accepting incoming
            RTMP/RTMPS streams.
    """

    url: str


class DiscardedLog(TypedDict, total=False):
    """A discarded/deleted video log entry.

    Returned when the log has been deleted. Only present when `include_deleted` is
    `true`.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: A unique identifier for the log.
        discarded_at: Date and time when the log was discarded.
        created_at: Date and time when the log was originally created.
    """

    id: str
    discarded_at: str
    created_at: str


JoinAsType: TypeAlias = "Literal['audience', 'member']"


class ListConferenceTokensResponse(TypedDict, total=False):
    """List conference tokens response.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of conference tokens.
    """

    links: PaginationLinks
    data: list[ConferenceToken]


class ListConferencesResponse(TypedDict, total=False):
    """List conferences response.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of conferences.
    """

    links: PaginationLinks
    data: list[Conference]


class ListLogsResponse(TypedDict, total=False):
    """List logs response.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of logs.
    """

    links: PaginationLinks
    data: list[VideoLog]


class ListRoomRecordingEventsResponse(TypedDict, total=False):
    """List room recording events response.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of room recording events.
    """

    links: PaginationLinks
    data: list[RoomSessionEvent]


class ListRoomRecordingsResponse(TypedDict, total=False):
    """List room recordings response.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of room recordings.
    """

    links: PaginationLinks
    data: list[RoomRecording]


class ListRoomSessionEventsResponse(TypedDict, total=False):
    """List room session events response.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of room session events.
    """

    links: PaginationLinks
    data: list[RoomSessionEvent]


class ListRoomSessionMembersResponse(TypedDict, total=False):
    """List room session members response.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of room session members.
    """

    links: PaginationLinks
    data: list[RoomSessionMember]


class ListRoomSessionRecordingsResponse(TypedDict, total=False):
    """List room session recordings response.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of room recordings.
    """

    links: PaginationLinks
    data: list[RoomRecording]


class ListRoomSessionsResponse(TypedDict, total=False):
    """List room sessions response.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of room sessions.
    """

    links: PaginationLinks
    data: list[RoomSession]


class ListRoomsResponse(TypedDict, total=False):
    """List rooms response.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of rooms.
    """

    links: PaginationLinks
    data: list[RoomResponse]


class ListStreamsResponse(TypedDict, total=False):
    """List streams response.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of streams.
    """

    links: PaginationLinks
    data: list[Stream]


class Log(TypedDict, total=False):
    """Log object representing a video activity entry.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: A unique identifier for the log.
        source: Source of this log entry.
        type: Type of this log entry.
        url: URL for the resource associated with this log entry.
        room_name: A named unique identifier for the room.
        status: Status of the log entry.
        locked: Whether the room session is locked.
        started_at: Start time of the activity.
        ended_at: End time of the activity.
        charge: Charge amount for this activity, in dollars.
        created_at: Timestamp when the log was created.
        charge_details: Details on charges associated with this log.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        self: Link to the current page.
        first: Link to the first page.
        next: Link to the next page.
        prev: Link to the previous page.
    """

    self: str
    first: str
    next: str
    prev: str


RoomLayout: TypeAlias = "Literal['grid-responsive', 'grid-responsive-mobile', 'highlight-1-responsive', '1x1', '2x1', '2x2', '5up', '3x3', '4x4', '5x5', '6x6', '8x8', '10x10']"


class RoomRecording(TypedDict, total=False):
    """Room recording response object.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique ID of the Room Recording.
        room_session_id: Unique ID of the Room Session the Room Recording was made in.
        status: Status of the recording.
        started_at: Timestamp of when the Room Recording started.
        finished_at: Timestamp of when the Room Recording stopped.
        duration: The length of the Room Recording in seconds.
        size_in_bytes: The number of bytes of the Room Recording file.
        format: The MIME type of the Room Recording file.
        cost_in_dollars: The cost of the recording in dollars.
        uri: A temporary URL for accessing the recording file. By default, valid for 15
            minutes.
        created_at: Timestamp when the recording was created.
        updated_at: Timestamp when the recording was last updated.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: A unique identifier for the room.
        name: A named unique identifier for the room.
        display_name: Display name of the room.
        description: Description of the room.
        max_members: The maximum number of members in the room at a time.
        quality: The room's resolution.
        fps: Frames per second parameter of room video quality.
        join_from: Room does not accept new participants before this time.
        join_until: Room stops accepting new participants at this time.
        remove_at: Remove users from the room at this time.
        remove_after_seconds_elapsed: Remove users after they are in the room for N
            seconds.
        layout: The room's initial layout.
        record_on_start: Specifies whether to start recording a Room Session when one is
            started for this Room.
        tone_on_entry_and_exit: Whether a tone is played when participants enter or exit
            the room.
        room_join_video_off: Whether the room's video is turned off when participants
            join.
        user_join_video_off: Whether a user's video is turned off when they join the
            room.
        enable_room_previews: Whether a video with a preview of the content of the room
            is to be generated.
        sync_audio_video: Enable/disable jitter buffer audio-video sync.
        meta: User-defined metadata for the room.
        prioritize_handraise: Whether hand raises are prioritized in the room layout.
        active_session: Active session information for the room.
        created_at: Timestamp when the room was created.
        updated_at: Timestamp when the room was last updated.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique ID of the session.
        room_id: Unique ID of the Room if the Session was created from a Room and was
            not an auto-created Session. Null if the room was set to delete on end.
        name: The named identifier of the room session.
        display_name: Display name of the room. Maximum of 200 characters. Defaults to
            the value of name.
        max_members: The maximum number of members allowed in the room at a time.
        quality: The room session's resolution.
        fps: The room session's frames per second.
        join_from: Room Session does not accept new Members before this time.
        join_until: Room Session stops accepting new Members at this time.
        remove_at: Remove Members from the Room Session at this time.
        remove_after_seconds_elapsed: Remove Members after they are in the Room Session
            for N seconds.
        layout: The room session's initial layout.
        record_on_start: Whether a recording was automatically started when this Room
            Session began.
        tone_on_entry_and_exit: Whether a tone is played when a member enters or exits
            the room session.
        room_join_video_off: Whether participants join with video off by room setting.
        user_join_video_off: Whether participants join with video off by user setting.
        locked: Whether the room session is locked.
        start_time: Start time of the session.
        end_time: End time of the session.
        duration: How long, in seconds, the Room Session lasted.
        status: Status of the session.
        created_at: Timestamp when the room session was created.
        updated_at: Timestamp when the room session was last updated.
        preview_url: If room previews are enabled and the room session is in progress,
            this is the URL of the preview video.
        prioritize_handraise: Whether raised hands are prioritized in the layout.
        sync_audio_video: Enable/disable jitter buffer audio-video sync.
        cost_in_dollars: The cost of the room session in dollars.
        enable_room_previews: Whether a video with a preview of the content of the room
            is to be generated.
        locked_cover: URL of the locked room cover image.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique ID of the event.
        project_id: The ID of the project.
        room_id: The ID of the room.
        room_session_id: The ID of the room session.
        room_recording_id: The ID of the associated room recording. Only present for
            recording-related events.
        room_participant_id: The ID of the associated room participant. Only present for
            participant-related events.
        level: The severity level of the event.
        name: The name of the event.
        payload: Event-specific payload data.
        created_at: Timestamp when the event was created.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique ID of the Member.
        room_session_id: Unique ID of the Room Session.
        name: Display name of the Member.
        join_time: Timestamp of when the Member joined the Room Session.
        leave_time: Timestamp of when the Member left the Room Session.
        duration: How long the Member stayed in the Room Session, in seconds. Null if
            the member has not yet joined.
        cost_in_dollars: The cost of the member's participation in dollars.
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
    """Room session summary, returned by the show endpoint.

    Omits list-only fields.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique ID of the session.
        room_id: Unique ID of the Room if the Session was created from a Room and was
            not an auto-created Session. Null if the room was set to delete on end.
        name: The named identifier of the room session.
        display_name: Display name of the room. Maximum of 200 characters. Defaults to
            the value of name.
        max_members: The maximum number of members allowed in the room at a time.
        quality: The room session's resolution.
        fps: The room session's frames per second.
        join_from: Room Session does not accept new Members before this time.
        join_until: Room Session stops accepting new Members at this time.
        remove_at: Remove Members from the Room Session at this time.
        remove_after_seconds_elapsed: Remove Members after they are in the Room Session
            for N seconds.
        layout: The room session's initial layout.
        record_on_start: Whether a recording was automatically started when this Room
            Session began.
        tone_on_entry_and_exit: Whether a tone is played when a member enters or exits
            the room session.
        room_join_video_off: Whether participants join with video off by room setting.
        user_join_video_off: Whether participants join with video off by user setting.
        locked: Whether the room session is locked.
        start_time: Start time of the session.
        end_time: End time of the session.
        duration: How long, in seconds, the Room Session lasted.
        status: Status of the session.
        created_at: Timestamp when the room session was created.
        updated_at: Timestamp when the room session was last updated.
        preview_url: If room previews are enabled and the room session is in progress,
            this is the URL of the preview video.
        prioritize_handraise: Whether raised hands are prioritized in the layout.
        sync_audio_video: Enable/disable jitter buffer audio-video sync.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        token: A Room Token to be used by clients to connect to the Room.
    """

    token: str


class Stream(TypedDict, total=False):
    """A video stream object.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique identifier for the stream.
        url: RTMP or RTMPS URL. This must be the address of a server accepting incoming
            RTMP/RTMPS streams.
        stream_type: The type of stream.
        width: The stream's width in pixels.
        height: The stream's height in pixels.
        fps: The stream's frames per second.
        created_at: Timestamp when the stream was created.
        updated_at: Timestamp when the stream was last updated.
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


class Types_StatusCodes_StatusCode403(TypedDict, total=False):
    """Access is forbidden.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Forbidden"]


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


class UpdateConferenceRequest(TypedDict, total=False):
    """Request body for updating a conference.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        display_name: Display name of the video conference. Maximum of 200 characters.
        description: Description of the conference. Maximum of 3000 characters.
        join_from: Conference does not accept new participants before this time. Expects
            RFC 3339 datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be
            converted to `2022-01-01T00:00:00Z`.
        join_until: Conference stops accepting new participants at this time, but keeps
            running until all participants leave. Expects RFC 3339 datetime:
            `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted to
            `2022-01-01T00:00:00Z`.
        quality: The conference's resolution.
        layout: The conference's initial layout.
        size: The size of the video conference.
        record_on_start: Whether to start recording when a conference session begins.
        tone_on_entry_and_exit: Whether a tone is played when a member enters or exits
            the conference.
        room_join_video_off: Whether participants join with video off by room setting.
        user_join_video_off: Whether participants join with video off by user setting.
        enable_room_previews: Whether a preview video of the conference content is
            generated.
        enable_chat: Whether group chat is enabled for conference participants.
        dark_primary: CTA buttons and selected items color (dark theme).
        dark_background: Main background color (dark theme).
        dark_foreground: Main foreground color (dark theme).
        dark_success: Success indication color (dark theme).
        dark_negative: Error indication color (dark theme).
        light_primary: CTA buttons and selected items color (light theme).
        light_background: Main background color (light theme).
        light_foreground: Main foreground color (light theme).
        light_success: Success indication color (light theme).
        light_negative: Error indication color (light theme).
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        display_name: Display name of the room. Maximum of 200 characters. Defaults to
            the value of name.
        description: Description of the room. Maximum of 3000 characters.
        max_members: The maximum number of members in the room at a time. Must be at
            least 1 to a maximum of 300.
        quality: The room's resolution.
        join_from: Room does not accept new participants before this time. Expects RFC
            3339 datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be
            converted to `2022-01-01T00:00:00Z`.
        join_until: Room stops accepting new participants at this time, but keeps
            running until all participants leave. Expects RFC 3339 datetime:
            `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted to
            `2022-01-01T00:00:00Z`.
        remove_at: Remove users from the room at this time. Expects RFC 3339 datetime:
            `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted to
            `2022-01-01T00:00:00Z`.
        remove_after_seconds_elapsed: Remove users after they are in the room for N
            seconds.
        layout: The room's initial layout.
        record_on_start: Specifies whether to start recording a Room Session when one is
            started for this Room.
        enable_room_previews: Whether a video with a preview of the content of the room
            is to be generated.
        meta: User-defined metadata for the room. Must be a valid JSON object. Maximum
            of 2000 characters when serialized.
        sync_audio_video: Enable/disable jitter buffer audio-video sync.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        url: RTMP or RTMPS URL. This must be the address of a server accepting incoming
            RTMP/RTMPS streams.
    """

    url: str


VideoFps: TypeAlias = "Literal[20, 30]"

VideoLayout: TypeAlias = "Literal['grid-responsive', 'grid-responsive-mobile', 'highlight-1-responsive', '1x1', '2x1', '2x2', '5up', '3x3', '4x4', '5x5', '6x6', '8x8', '10x10']"

VideoLog: TypeAlias = "Log | DiscardedLog"

VideoQuality: TypeAlias = "Literal['720p', '1080p']"


class VideoStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
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
