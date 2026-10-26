# AUTO-GENERATED from porting-sdk/rest-apis/video/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``video`` REST resources, generated from the OpenAPI spec.

One resource class per spec collection: closed, typed ``create`` / ``update``
parameters (the explicit spec fields) and typed sub-operation methods, plus an
``extras`` escape hatch and a ``**_reserved_kw`` tail for unknown or reserved-word
wire fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import BaseResource, CrudResource, ReadResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

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
    """Typed resource for ``/conference_tokens`` (generated).

    Bound to ``/api/video/conference_tokens``; construct it as
    ``VideoConferenceTokens(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/video/conference_tokens")

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ConferenceToken:
        """Find a conference token by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the conference token.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            A conference token object.
        """
        return cast(
            "ConferenceToken",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def reset(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> ConferenceToken:
        """Reset a conference token by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the conference token.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            A conference token object.
        """
        return cast(
            "ConferenceToken",
            self._http.post(self._path(id, "reset"), request_options=request_options),
        )


class VideoConferences(
    CrudResource[
        "ListConferencesResponse",
        "Conference",
        "CreateConferenceRequest",
        "UpdateConferenceRequest",
    ]
):
    """Typed resource for ``/conferences`` (generated).

    Bound to ``/api/video/conferences``; construct it as ``VideoConferences(http)`` with
    the client's HTTP transport.
    """

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
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Conference:
        """Create a Video Conference.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            display_name: Display name of the video conference. Maximum of 200
                characters.
            name: A named unique identifier for the conference. Allowed characters:
                `A-Za-z0-9_-`. Maximum of 100 characters.
            description: Description of the conference. Maximum of 3000 characters.
            join_from: Conference does not accept new participants before this time.
                Expects RFC 3339 datetime: `2022-01-01T23:59:60Z`. Date only:
                `2022-01-01` will be converted to `2022-01-01T00:00:00Z`.
            join_until: Conference stops accepting new participants at this time, but
                keeps running until all participants leave. Expects RFC 3339 datetime:
                `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted to
                `2022-01-01T00:00:00Z`.
            quality: The conference's resolution.
            layout: The conference's initial layout.
            size: The size of the video conference.
            record_on_start: Whether to start recording when a conference session
                begins.
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
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Video conference response object.
        """
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
        return cast(
            "Conference",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

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
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Conference:
        """Update a Video Conference.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the video conference.
            display_name: Display name of the video conference. Maximum of 200
                characters.
            description: Description of the conference. Maximum of 3000 characters.
            join_from: Conference does not accept new participants before this time.
                Expects RFC 3339 datetime: `2022-01-01T23:59:60Z`. Date only:
                `2022-01-01` will be converted to `2022-01-01T00:00:00Z`.
            join_until: Conference stops accepting new participants at this time, but
                keeps running until all participants leave. Expects RFC 3339 datetime:
                `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted to
                `2022-01-01T00:00:00Z`.
            quality: The conference's resolution.
            layout: The conference's initial layout.
            size: The size of the video conference.
            record_on_start: Whether to start recording when a conference session
                begins.
            tone_on_entry_and_exit: Whether a tone is played when a member enters or
                exits the conference.
            room_join_video_off: Whether participants join with video off by room
                setting.
            user_join_video_off: Whether participants join with video off by user
                setting.
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
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Video conference response object.
        """
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
        return cast(
            "Conference",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_conference_tokens(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ListConferenceTokensResponse:
        """List conference tokens.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the video conference.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: Page number to return. Requires `page_token` for
                  values greater than 0.
                - ``page_size``: Specify the number of results to return on a single
                  page. The default page size is `50` and the maximum is `1000`.
                - ``page_token``: Token for cursor-based pagination. Required when
                  `page_number` is greater than 0.

        Returns:
            List conference tokens response.
        """
        return cast(
            "ListConferenceTokensResponse",
            self._http.get(
                self._path(id, "conference_tokens"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def list_streams(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ListStreamsResponse:
        """**Permissions**.

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique id of a video conference
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            List streams response.
        """
        return cast(
            "ListStreamsResponse",
            self._http.get(
                self._path(id, "streams"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def create_stream(
        self,
        id: str,
        *,
        url: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Stream:
        """**Permissions**.

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique id of a video conference
            url: RTMP or RTMPS URL. This must be the address of a server accepting
                incoming RTMP/RTMPS streams.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            A video stream object.
        """
        body: dict[str, Any] = {k: v for k, v in {"url": url}.items() if v is not None}
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "Stream",
            self._http.post(
                self._path(id, "streams"), body=body, request_options=request_options
            ),
        )


class VideoRoomRecordings(BaseResource):
    """Typed resource for ``/room_recordings`` (generated).

    Bound to ``/api/video/room_recordings``; construct it as
    ``VideoRoomRecordings(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/video/room_recordings")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ListRoomRecordingsResponse:
        """A list of all Room Recordings.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``media_ttl``: Generated media links will be valid for this many
                  seconds. Default is 900 (15 minutes).
                - ``page_number``: Page number to return. Requires `page_token` for
                  values greater than 0.
                - ``page_size``: Specify the number of results to return on a single
                  page. The default page size is `50` and the maximum is `1000`.
                - ``page_token``: Token for cursor-based pagination. Required when
                  `page_number` is greater than 0.

        Returns:
            List room recordings response.
        """
        return cast(
            "ListRoomRecordingsResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> RoomRecording:
        """A detailed summary of a particular Room Recording.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the Room Recording.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``media_ttl``: Generated media links will be valid for this many
                  seconds. Default is 900 (15 minutes).

        Returns:
            Room recording response object.
        """
        return cast(
            "RoomRecording",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        """Delete a Room Recording.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the Room Recording.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The decoded JSON response (an empty dict when the server sends no body).
        """
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )

    def list_events(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ListRoomRecordingEventsResponse:
        """A list of Events for a particular Room Recording.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the Room Recording.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: Page number to return. Requires `page_token` for
                  values greater than 0.
                - ``page_size``: Specify the number of results to return on a single
                  page. The default page size is `50` and the maximum is `1000`.
                - ``page_token``: Token for cursor-based pagination. Required when
                  `page_number` is greater than 0.

        Returns:
            List room recording events response.
        """
        return cast(
            "ListRoomRecordingEventsResponse",
            self._http.get(
                self._path(id, "events"),
                params=params or None,
                request_options=request_options,
            ),
        )


class VideoRoomSessions(ReadResource["ListRoomSessionsResponse", "RoomSessionSummary"]):
    """Typed resource for ``/room_sessions`` (generated).

    Bound to ``/api/video/room_sessions``; construct it as ``VideoRoomSessions(http)``
    with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/video/room_sessions")

    def list_events(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ListRoomSessionEventsResponse:
        """A list of Events for a particular Room Session.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the Room Session.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: Page number to return. Requires `page_token` for
                  values greater than 0.
                - ``page_size``: Specify the number of results to return on a single
                  page. The default page size is `50` and the maximum is `1000`.
                - ``page_token``: Token for cursor-based pagination. Required when
                  `page_number` is greater than 0.

        Returns:
            List room session events response.
        """
        return cast(
            "ListRoomSessionEventsResponse",
            self._http.get(
                self._path(id, "events"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def list_members(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ListRoomSessionMembersResponse:
        """A list of Members for a particular Room Session.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the Room Session.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: Page number to return. Requires `page_token` for
                  values greater than 0.
                - ``page_size``: Specify the number of results to return on a single
                  page. The default page size is `50` and the maximum is `1000`.
                - ``page_token``: Token for cursor-based pagination. Required when
                  `page_number` is greater than 0.

        Returns:
            List room session members response.
        """
        return cast(
            "ListRoomSessionMembersResponse",
            self._http.get(
                self._path(id, "members"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def list_recordings(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ListRoomSessionRecordingsResponse:
        """A list of Room Recordings for a particular Room Session.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the Room Session.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``media_ttl``: Generated media links will be valid for this many
                  seconds. Default is 900 (15 minutes).
                - ``page_number``: Page number to return. Requires `page_token` for
                  values greater than 0.
                - ``page_size``: Specify the number of results to return on a single
                  page. The default page size is `50` and the maximum is `1000`.
                - ``page_token``: Token for cursor-based pagination. Required when
                  `page_number` is greater than 0.

        Returns:
            List room session recordings response.
        """
        return cast(
            "ListRoomSessionRecordingsResponse",
            self._http.get(
                self._path(id, "recordings"),
                params=params or None,
                request_options=request_options,
            ),
        )


class VideoRoomTokens(BaseResource):
    """Typed resource for ``/room_tokens`` (generated).

    Bound to ``/api/video/room_tokens``; construct it as ``VideoRoomTokens(http)`` with
    the client's HTTP transport.
    """

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
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> RoomTokenResponse:
        """Generate a Room Token allowing a client to join a Room.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            room_name: Room's unique named identifier. Allowed characters: A-Za-z0-9_-.
                Up to 100 characters. The room does not have to exist when the token is
                created, but must exist prior to joining, or ensure auto_create_room is
                set to true.
            user_name: A display name to use for the user. Up to 100 characters. (If not
                supplied, a random alphanumeric string will be returned for each
                authorization with this token.)
            permissions: A list of permissions, which define what user can do once they
                join the room. If `join_as` is `audience`, permissions are set to an
                empty array regardless of the value provided.
            join_from: The user can't join the room before this time. Expects RFC 3339
                datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be
                converted to `2022-01-01T00:00:00Z`
            join_until: The user can't join the room after this time. Expects RFC 3339
                datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be
                converted to `2022-01-01T00:00:00Z`
            remove_at: Remove user from the room at this time. Expects RFC 3339
                datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be
                converted to `2022-01-01T00:00:00Z`
            remove_after_seconds_elapsed: Remove user after they are in the room for N
                seconds.
            join_audio_muted: Whether the user joins the room with their audio muted.
            join_video_muted: Whether the user joins the room with their video muted.
            auto_create_room: By default, if the user tries to use this token to join a
                room that doesn't exist, it will be created with default configuration.
                Set this to false to require the room to exist beforehand.
            enable_room_previews: Whether to generate a video with a preview of the
                content of the room. This parameter has effect only if this token
                auto-creates the room, thus it will be ignored if the room already
                exists.
            room_display_name: Display name used if a room is auto-created when the
                token joins. Maximum of 200 characters. Defaults to the value of
                room_name.
            end_room_session_on_leave: Whether to end the room session when the member
                using this token leaves the room.
            join_as: Whether the user should join as a member or as a non-interactive
                audience participant. Audience participants cannot send audio or video.
            media_allowed: Indicates what media the user is allowed to receive.
            room_meta: Set the room meta. Maximum of 2000 characters when serialized to
                JSON.
            meta: Set the member meta. Maximum of 2000 characters when serialized to
                JSON.
            sync_audio_video: Enable/disable jitter buffer audio-video sync.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Room token response object.
        """
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
        return cast(
            "RoomTokenResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )


class VideoRooms(
    CrudResource[
        "ListRoomsResponse", "RoomResponse", "CreateRoomRequest", "UpdateRoomRequest"
    ]
):
    """Typed resource for ``/rooms`` (generated).

    Bound to ``/api/video/rooms``; construct it as ``VideoRooms(http)`` with the
    client's HTTP transport.
    """

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
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> RoomResponse:
        """Create a room.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            name: A named unique identifier for the room. Allowed characters:
                `A-Za-z0-9_-`. Maximum of 100 characters.
            display_name: Display name of the room. Maximum of 200 characters. Defaults
                to the value of name.
            description: Description of the room. Maximum of 3000 characters.
            max_members: The maximum number of members in the room at a time. Must be at
                least 1 to a maximum of 300.
            quality: The room's resolution.
            join_from: Room does not accept new participants before this time. Expects
                RFC 3339 datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will
                be converted to `2022-01-01T00:00:00Z`.
            join_until: Room stops accepting new participants at this time, but keeps
                running until all participants leave. Expects RFC 3339 datetime:
                `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted to
                `2022-01-01T00:00:00Z`.
            remove_at: Remove users from the room at this time. Expects RFC 3339
                datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be
                converted to `2022-01-01T00:00:00Z`.
            remove_after_seconds_elapsed: Remove users after they are in the room for N
                seconds.
            layout: The room's initial layout.
            record_on_start: Specifies whether to start recording a Room Session when
                one is started for this Room.
            enable_room_previews: Whether a video with a preview of the content of the
                room is to be generated.
            meta: User-defined metadata for the room. Must be a valid JSON object.
                Maximum of 2000 characters when serialized.
            sync_audio_video: Enable/disable jitter buffer audio-video sync.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Room response object.
        """
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
        return cast(
            "RoomResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

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
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> RoomResponse:
        """Update a room.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the room.
            display_name: Display name of the room. Maximum of 200 characters. Defaults
                to the value of name.
            description: Description of the room. Maximum of 3000 characters.
            max_members: The maximum number of members in the room at a time. Must be at
                least 1 to a maximum of 300.
            quality: The room's resolution.
            join_from: Room does not accept new participants before this time. Expects
                RFC 3339 datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will
                be converted to `2022-01-01T00:00:00Z`.
            join_until: Room stops accepting new participants at this time, but keeps
                running until all participants leave. Expects RFC 3339 datetime:
                `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be converted to
                `2022-01-01T00:00:00Z`.
            remove_at: Remove users from the room at this time. Expects RFC 3339
                datetime: `2022-01-01T23:59:60Z`. Date only: `2022-01-01` will be
                converted to `2022-01-01T00:00:00Z`.
            remove_after_seconds_elapsed: Remove users after they are in the room for N
                seconds.
            layout: The room's initial layout.
            record_on_start: Specifies whether to start recording a Room Session when
                one is started for this Room.
            enable_room_previews: Whether a video with a preview of the content of the
                room is to be generated.
            meta: User-defined metadata for the room. Must be a valid JSON object.
                Maximum of 2000 characters when serialized.
            sync_audio_video: Enable/disable jitter buffer audio-video sync.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Room response object.
        """
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
        return cast(
            "RoomResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_streams(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ListStreamsResponse:
        """**Permissions**.

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the video room.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            List streams response.
        """
        return cast(
            "ListStreamsResponse",
            self._http.get(
                self._path(id, "streams"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def create_stream(
        self,
        id: str,
        *,
        url: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Stream:
        """**Permissions**.

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the video room.
            url: RTMP or RTMPS URL. This must be the address of a server accepting
                incoming RTMP/RTMPS streams.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            A video stream object.
        """
        body: dict[str, Any] = {k: v for k, v in {"url": url}.items() if v is not None}
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "Stream",
            self._http.post(
                self._path(id, "streams"), body=body, request_options=request_options
            ),
        )


class VideoStreams(BaseResource):
    """Typed resource for ``/streams`` (generated).

    Bound to ``/api/video/streams``; construct it as ``VideoStreams(http)`` with the
    client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/video/streams")

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> Stream:
        """**Permissions**.

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the stream.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            A video stream object.
        """
        return cast(
            "Stream",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        *,
        url: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Stream:
        """**Permissions**.

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the stream.
            url: RTMP or RTMPS URL. This must be the address of a server accepting
                incoming RTMP/RTMPS streams.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            A video stream object.
        """
        body: dict[str, Any] = {k: v for k, v in {"url": url}.items() if v is not None}
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "Stream",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        """**Permissions**.

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the stream.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The decoded JSON response (an empty dict when the server sends no body).
        """
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )
