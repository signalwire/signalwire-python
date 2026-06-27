"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Video API namespace — rooms, sessions, recordings, conferences, tokens, streams.
"""

from typing import TYPE_CHECKING, Any

from .._base import BaseResource, CrudResource
from .video_resources_generated import VideoConferencesResource, VideoRoomsResource

if TYPE_CHECKING:
    from .video_types_generated import (
        Conference,
        ConferenceToken,
        CreateConferenceRequest,
        CreateRoomRequest,
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
        RoomRecording,
        RoomResponse,
        RoomSessionSummary,
        RoomTokenResponse,
        Stream,
        UpdateConferenceRequest,
        UpdateRoomRequest,
    )


# ``VideoRooms`` / ``VideoConferences`` are generated from the spec (see
# ``video_resources_generated``), imported below. Back-compat aliases keep the old
# names working.
VideoRooms = VideoRoomsResource
VideoConferences = VideoConferencesResource


class VideoRoomTokens(BaseResource):
    """Video room token generation."""

    def create(self, **kwargs: Any) -> "RoomTokenResponse":
        return self._http.post(self._base_path, body=kwargs)


class VideoRoomSessions(BaseResource):
    """Video room session management."""

    def list(self, **params: Any) -> "ListRoomSessionsResponse":
        return self._http.get(self._base_path, params=params or None)

    def get(self, session_id: str) -> "RoomSessionSummary":
        return self._http.get(self._path(session_id))

    def list_events(
        self, session_id: str, **params: Any
    ) -> "ListRoomSessionEventsResponse":
        return self._http.get(self._path(session_id, "events"), params=params or None)

    def list_members(
        self, session_id: str, **params: Any
    ) -> "ListRoomSessionMembersResponse":
        return self._http.get(self._path(session_id, "members"), params=params or None)

    def list_recordings(
        self, session_id: str, **params: Any
    ) -> "ListRoomSessionRecordingsResponse":
        return self._http.get(
            self._path(session_id, "recordings"), params=params or None
        )


class VideoRoomRecordings(BaseResource):
    """Video room recording management."""

    def list(self, **params: Any) -> "ListRoomRecordingsResponse":
        return self._http.get(self._base_path, params=params or None)

    def get(self, recording_id: str) -> "RoomRecording":
        return self._http.get(self._path(recording_id))

    def delete(self, recording_id: str) -> dict[str, Any]:
        return self._http.delete(self._path(recording_id))

    def list_events(
        self, recording_id: str, **params: Any
    ) -> "ListRoomRecordingEventsResponse":
        return self._http.get(self._path(recording_id, "events"), params=params or None)


class VideoConferenceTokens(BaseResource):
    """Video conference token management."""

    def get(self, token_id: str) -> "ConferenceToken":
        return self._http.get(self._path(token_id))

    def reset(self, token_id: str) -> "ConferenceToken":
        return self._http.post(self._path(token_id, "reset"))


class VideoStreams(BaseResource):
    """Video stream management."""

    def get(self, stream_id: str) -> "Stream":
        return self._http.get(self._path(stream_id))

    def update(self, stream_id: str, **kwargs: Any) -> "Stream":
        return self._http.put(self._path(stream_id), body=kwargs)

    def delete(self, stream_id: str) -> dict[str, Any]:
        return self._http.delete(self._path(stream_id))


class VideoNamespace:
    """Video API namespace."""

    def __init__(self, http: Any) -> None:
        base = "/api/video"
        self.rooms = VideoRoomsResource(http)
        self.room_tokens = VideoRoomTokens(http, f"{base}/room_tokens")
        self.room_sessions = VideoRoomSessions(http, f"{base}/room_sessions")
        self.room_recordings = VideoRoomRecordings(http, f"{base}/room_recordings")
        self.conferences = VideoConferencesResource(http)
        self.conference_tokens = VideoConferenceTokens(
            http, f"{base}/conference_tokens"
        )
        self.streams = VideoStreams(http, f"{base}/streams")
