# AUTO-GENERATED from porting-sdk/rest-apis/video/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import BaseResource, CrudResource, ReadResource

if TYPE_CHECKING:
    from .video_types_generated import (
        Conference,
        ConferenceSize,
        ConferenceToken,
        CreateConferenceRequest,
        CreateRoomRequest,
        JoinAsType,
        ListConferenceTokensResponse,
        ListConferencesResponse,
        ListRoomRecordingEventsResponse,
        ListRoomRecordingsResponse,
        ListRoomSessionEventsResponse,
        ListRoomSessionMembersResponse,
        ListRoomSessionRecordingsResponse,
        ListRoomSessionsResponse,
        ListRoomsResponse,
        ListStreamsResponse,
        MediaAllowedType,
        RoomLayout,
        RoomRecording,
        RoomResponse,
        RoomSessionSummary,
        RoomTokenPermission,
        RoomTokenResponse,
        Stream,
        UpdateConferenceRequest,
        UpdateRoomRequest,
        VideoLayout,
        VideoQuality,
    )


class VideoConferenceTokens(BaseResource):
    """Typed resource for ``/conference_tokens`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/video/conference_tokens")

    def get(self, id: str, **params: Any) -> ConferenceToken:
        return cast(
            "ConferenceToken", self._http.get(self._path(id), params=params or None)
        )

    def reset(self, id: str) -> ConferenceToken:
        return cast("ConferenceToken", self._http.post(self._path(id, "reset")))


class VideoConferences(
    CrudResource[
        "ListConferencesResponse",
        "Conference",
        "CreateConferenceRequest",
        "UpdateConferenceRequest",
    ]
):
    """Typed resource for ``/conferences`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/video/conferences")

    def create(  # type: ignore[override]
        self,
        *,
        display_name: str,
        name: str | None = None,
        description: str | None = None,
        join_from: str | None = None,
        join_until: str | None = None,
        quality: VideoQuality | None = None,
        layout: VideoLayout | None = None,
        size: ConferenceSize | None = None,
        record_on_start: bool | None = None,
        enable_room_previews: bool | None = None,
        enable_chat: bool | None = None,
        dark_primary: str | None = None,
        dark_background: str | None = None,
        dark_foreground: str | None = None,
        dark_success: str | None = None,
        dark_negative: str | None = None,
        light_primary: str | None = None,
        light_background: str | None = None,
        light_foreground: str | None = None,
        light_success: str | None = None,
        light_negative: str | None = None,
        extras: Mapping[str, Any] | None = None,
        **_reserved_kw: Any,
    ) -> Conference:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "display_name": display_name,
                "description": description,
                "join_from": join_from,
                "join_until": join_until,
                "quality": quality,
                "layout": layout,
                "size": size,
                "record_on_start": record_on_start,
                "enable_room_previews": enable_room_previews,
                "enable_chat": enable_chat,
                "dark_primary": dark_primary,
                "dark_background": dark_background,
                "dark_foreground": dark_foreground,
                "dark_success": dark_success,
                "dark_negative": dark_negative,
                "light_primary": light_primary,
                "light_background": light_background,
                "light_foreground": light_foreground,
                "light_success": light_success,
                "light_negative": light_negative,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast("Conference", self._http.post(self._base_path, body=body))

    def update(
        self,
        id: str,
        /,
        *,
        display_name: str | None = None,
        description: str | None = None,
        join_from: str | None = None,
        join_until: str | None = None,
        quality: VideoQuality | None = None,
        layout: VideoLayout | None = None,
        size: ConferenceSize | None = None,
        record_on_start: bool | None = None,
        tone_on_entry_and_exit: bool | None = None,
        room_join_video_off: bool | None = None,
        user_join_video_off: bool | None = None,
        enable_room_previews: bool | None = None,
        enable_chat: bool | None = None,
        dark_primary: str | None = None,
        dark_background: str | None = None,
        dark_foreground: str | None = None,
        dark_success: str | None = None,
        dark_negative: str | None = None,
        light_primary: str | None = None,
        light_background: str | None = None,
        light_foreground: str | None = None,
        light_success: str | None = None,
        light_negative: str | None = None,
        extras: Mapping[str, Any] | None = None,
        **_reserved_kw: Any,
    ) -> Conference:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "description": description,
                "join_from": join_from,
                "join_until": join_until,
                "quality": quality,
                "layout": layout,
                "size": size,
                "record_on_start": record_on_start,
                "tone_on_entry_and_exit": tone_on_entry_and_exit,
                "room_join_video_off": room_join_video_off,
                "user_join_video_off": user_join_video_off,
                "enable_room_previews": enable_room_previews,
                "enable_chat": enable_chat,
                "dark_primary": dark_primary,
                "dark_background": dark_background,
                "dark_foreground": dark_foreground,
                "dark_success": dark_success,
                "dark_negative": dark_negative,
                "light_primary": light_primary,
                "light_background": light_background,
                "light_foreground": light_foreground,
                "light_success": light_success,
                "light_negative": light_negative,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast("Conference", self._http.put(self._path(id), body=body))

    def list_conference_tokens(
        self, id: str, **params: Any
    ) -> ListConferenceTokensResponse:
        return cast(
            "ListConferenceTokensResponse",
            self._http.get(self._path(id, "conference_tokens"), params=params or None),
        )

    def list_streams(self, id: str, **params: Any) -> ListStreamsResponse:
        return cast(
            "ListStreamsResponse",
            self._http.get(self._path(id, "streams"), params=params or None),
        )

    def create_stream(
        self,
        id: str,
        *,
        url: str,
        extras: Mapping[str, Any] | None = None,
        **_reserved_kw: Any,
    ) -> Stream:
        body: dict[str, Any] = {k: v for k, v in {"url": url}.items() if v is not None}
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast("Stream", self._http.post(self._path(id, "streams"), body=body))


class VideoRoomRecordings(BaseResource):
    """Typed resource for ``/room_recordings`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/video/room_recordings")

    def list(self, **params: Any) -> ListRoomRecordingsResponse:
        return cast(
            "ListRoomRecordingsResponse",
            self._http.get(self._base_path, params=params or None),
        )

    def get(self, id: str, **params: Any) -> RoomRecording:
        return cast(
            "RoomRecording", self._http.get(self._path(id), params=params or None)
        )

    def delete(self, id: str) -> dict[str, Any]:
        return cast("dict[str, Any]", self._http.delete(self._path(id)))

    def list_events(self, id: str, **params: Any) -> ListRoomRecordingEventsResponse:
        return cast(
            "ListRoomRecordingEventsResponse",
            self._http.get(self._path(id, "events"), params=params or None),
        )


class VideoRoomSessions(ReadResource["ListRoomSessionsResponse", "RoomSessionSummary"]):
    """Typed resource for ``/room_sessions`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/video/room_sessions")

    def list_events(self, id: str, **params: Any) -> ListRoomSessionEventsResponse:
        return cast(
            "ListRoomSessionEventsResponse",
            self._http.get(self._path(id, "events"), params=params or None),
        )

    def list_members(self, id: str, **params: Any) -> ListRoomSessionMembersResponse:
        return cast(
            "ListRoomSessionMembersResponse",
            self._http.get(self._path(id, "members"), params=params or None),
        )

    def list_recordings(
        self, id: str, **params: Any
    ) -> ListRoomSessionRecordingsResponse:
        return cast(
            "ListRoomSessionRecordingsResponse",
            self._http.get(self._path(id, "recordings"), params=params or None),
        )


class VideoRoomTokens(BaseResource):
    """Typed resource for ``/room_tokens`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/video/room_tokens")

    def create(
        self,
        *,
        room_name: str,
        user_name: str | None = None,
        permissions: list[RoomTokenPermission] | None = None,
        join_from: str | None = None,
        join_until: str | None = None,
        remove_at: str | None = None,
        remove_after_seconds_elapsed: int | None = None,
        join_audio_muted: bool | None = None,
        join_video_muted: bool | None = None,
        auto_create_room: bool | None = None,
        enable_room_previews: bool | None = None,
        room_display_name: str | None = None,
        end_room_session_on_leave: bool | None = None,
        join_as: JoinAsType | None = None,
        media_allowed: MediaAllowedType | None = None,
        room_meta: dict[str, Any] | None = None,
        meta: dict[str, Any] | None = None,
        sync_audio_video: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        **_reserved_kw: Any,
    ) -> RoomTokenResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "room_name": room_name,
                "user_name": user_name,
                "permissions": permissions,
                "join_from": join_from,
                "join_until": join_until,
                "remove_at": remove_at,
                "remove_after_seconds_elapsed": remove_after_seconds_elapsed,
                "join_audio_muted": join_audio_muted,
                "join_video_muted": join_video_muted,
                "auto_create_room": auto_create_room,
                "enable_room_previews": enable_room_previews,
                "room_display_name": room_display_name,
                "end_room_session_on_leave": end_room_session_on_leave,
                "join_as": join_as,
                "media_allowed": media_allowed,
                "room_meta": room_meta,
                "meta": meta,
                "sync_audio_video": sync_audio_video,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast("RoomTokenResponse", self._http.post(self._base_path, body=body))


class VideoRooms(
    CrudResource[
        "ListRoomsResponse", "RoomResponse", "CreateRoomRequest", "UpdateRoomRequest"
    ]
):
    """Typed resource for ``/rooms`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/video/rooms")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        display_name: str | None = None,
        description: str | None = None,
        max_members: int | None = None,
        quality: VideoQuality | None = None,
        join_from: str | None = None,
        join_until: str | None = None,
        remove_at: str | None = None,
        remove_after_seconds_elapsed: int | None = None,
        layout: RoomLayout | None = None,
        record_on_start: bool | None = None,
        enable_room_previews: bool | None = None,
        meta: dict[str, Any] | None = None,
        sync_audio_video: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        **_reserved_kw: Any,
    ) -> RoomResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "display_name": display_name,
                "description": description,
                "max_members": max_members,
                "quality": quality,
                "join_from": join_from,
                "join_until": join_until,
                "remove_at": remove_at,
                "remove_after_seconds_elapsed": remove_after_seconds_elapsed,
                "layout": layout,
                "record_on_start": record_on_start,
                "enable_room_previews": enable_room_previews,
                "meta": meta,
                "sync_audio_video": sync_audio_video,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast("RoomResponse", self._http.post(self._base_path, body=body))

    def update(
        self,
        id: str,
        /,
        *,
        display_name: str | None = None,
        description: str | None = None,
        max_members: int | None = None,
        quality: VideoQuality | None = None,
        join_from: str | None = None,
        join_until: str | None = None,
        remove_at: str | None = None,
        remove_after_seconds_elapsed: int | None = None,
        layout: RoomLayout | None = None,
        record_on_start: bool | None = None,
        enable_room_previews: bool | None = None,
        meta: dict[str, Any] | None = None,
        sync_audio_video: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        **_reserved_kw: Any,
    ) -> RoomResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "description": description,
                "max_members": max_members,
                "quality": quality,
                "join_from": join_from,
                "join_until": join_until,
                "remove_at": remove_at,
                "remove_after_seconds_elapsed": remove_after_seconds_elapsed,
                "layout": layout,
                "record_on_start": record_on_start,
                "enable_room_previews": enable_room_previews,
                "meta": meta,
                "sync_audio_video": sync_audio_video,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast("RoomResponse", self._http.put(self._path(id), body=body))

    def list_streams(self, id: str, **params: Any) -> ListStreamsResponse:
        return cast(
            "ListStreamsResponse",
            self._http.get(self._path(id, "streams"), params=params or None),
        )

    def create_stream(
        self,
        id: str,
        *,
        url: str,
        extras: Mapping[str, Any] | None = None,
        **_reserved_kw: Any,
    ) -> Stream:
        body: dict[str, Any] = {k: v for k, v in {"url": url}.items() if v is not None}
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast("Stream", self._http.post(self._path(id, "streams"), body=body))


class VideoStreams(BaseResource):
    """Typed resource for ``/streams`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/video/streams")

    def get(self, id: str, **params: Any) -> Stream:
        return cast("Stream", self._http.get(self._path(id), params=params or None))

    def update(
        self,
        id: str,
        *,
        url: str,
        extras: Mapping[str, Any] | None = None,
        **_reserved_kw: Any,
    ) -> Stream:
        body: dict[str, Any] = {k: v for k, v in {"url": url}.items() if v is not None}
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast("Stream", self._http.put(self._path(id), body=body))

    def delete(self, id: str) -> dict[str, Any]:
        return cast("dict[str, Any]", self._http.delete(self._path(id)))
