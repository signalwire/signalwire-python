# AUTO-GENERATED from porting-sdk/rest-apis/video/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed create/update
# (explicit spec fields + an ``extras`` door), bound to the resource's spec
# types. Runtime body is a plain dict (open-tail, never validated).
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import CrudResource

if TYPE_CHECKING:
    from .video_types_generated import (
        Conference,
        ConferenceSize,
        CreateConferenceRequest,
        CreateRoomRequest,
        ListConferenceTokensResponse,
        ListConferencesResponse,
        ListRoomsResponse,
        ListStreamsResponse,
        RoomLayout,
        RoomResponse,
        Stream,
        UpdateConferenceRequest,
        UpdateRoomRequest,
        VideoLayout,
        VideoQuality,
    )


class VideoConferencesResource(
    CrudResource[
        "ListConferencesResponse",
        "Conference",
        "CreateConferenceRequest",
        "UpdateConferenceRequest",
    ]
):
    """Typed CRUD resource for ``/conferences`` (generated)."""

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
        return cast("Conference", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
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
        self, id: str, *, url: str, extras: Mapping[str, Any] | None = None
    ) -> Stream:
        body: dict[str, Any] = {k: v for k, v in {"url": url}.items() if v is not None}
        if extras:
            body.update(extras)
        return cast("Stream", self._http.post(self._path(id, "streams"), body=body))


class VideoRoomsResource(
    CrudResource[
        "ListRoomsResponse", "RoomResponse", "CreateRoomRequest", "UpdateRoomRequest"
    ]
):
    """Typed CRUD resource for ``/rooms`` (generated)."""

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
        return cast("RoomResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
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
        return cast("RoomResponse", self._http.put(self._path(id), body=body))

    def list_streams(self, id: str, **params: Any) -> ListStreamsResponse:
        return cast(
            "ListStreamsResponse",
            self._http.get(self._path(id, "streams"), params=params or None),
        )

    def create_stream(
        self, id: str, *, url: str, extras: Mapping[str, Any] | None = None
    ) -> Stream:
        body: dict[str, Any] = {k: v for k, v in {"url": url}.items() if v is not None}
        if extras:
            body.update(extras)
        return cast("Stream", self._http.post(self._path(id, "streams"), body=body))
