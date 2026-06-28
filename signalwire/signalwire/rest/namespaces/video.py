"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Video API namespace — rooms, sessions, recordings, conferences, tokens, streams. All
resources are generated from the canonical spec (see ``video_resources_generated``);
this is the thin namespace that groups them under ``client.video``.
"""

from typing import Any

from .video_resources_generated import (
    VideoConferencesResource,
    VideoConferenceTokensResource,
    VideoRoomRecordingsResource,
    VideoRoomSessionsResource,
    VideoRoomsResource,
    VideoRoomTokensResource,
    VideoStreamsResource,
)

# Back-compat aliases for the historical class names.
VideoRooms = VideoRoomsResource
VideoConferences = VideoConferencesResource
VideoRoomTokens = VideoRoomTokensResource
VideoRoomSessions = VideoRoomSessionsResource
VideoRoomRecordings = VideoRoomRecordingsResource
VideoConferenceTokens = VideoConferenceTokensResource
VideoStreams = VideoStreamsResource

__all__ = [
    "VideoConferenceTokens",
    "VideoConferenceTokensResource",
    "VideoConferences",
    "VideoConferencesResource",
    "VideoNamespace",
    "VideoRoomRecordings",
    "VideoRoomRecordingsResource",
    "VideoRoomSessions",
    "VideoRoomSessionsResource",
    "VideoRoomTokens",
    "VideoRoomTokensResource",
    "VideoRooms",
    "VideoRoomsResource",
    "VideoStreams",
    "VideoStreamsResource",
]


class VideoNamespace:
    """Video API namespace."""

    def __init__(self, http: Any) -> None:
        self.rooms = VideoRoomsResource(http)
        self.room_tokens = VideoRoomTokensResource(http)
        self.room_sessions = VideoRoomSessionsResource(http)
        self.room_recordings = VideoRoomRecordingsResource(http)
        self.conferences = VideoConferencesResource(http)
        self.conference_tokens = VideoConferenceTokensResource(http)
        self.streams = VideoStreamsResource(http)
