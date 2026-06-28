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
    VideoConferences,
    VideoConferenceTokens,
    VideoRoomRecordings,
    VideoRoomSessions,
    VideoRooms,
    VideoRoomTokens,
    VideoStreams,
)

__all__ = [
    "VideoConferenceTokens",
    "VideoConferences",
    "VideoNamespace",
    "VideoRoomRecordings",
    "VideoRoomSessions",
    "VideoRoomTokens",
    "VideoRooms",
    "VideoStreams",
]


class VideoNamespace:
    """Video API namespace."""

    def __init__(self, http: Any) -> None:
        self.rooms = VideoRooms(http)
        self.room_tokens = VideoRoomTokens(http)
        self.room_sessions = VideoRoomSessions(http)
        self.room_recordings = VideoRoomRecordings(http)
        self.conferences = VideoConferences(http)
        self.conference_tokens = VideoConferenceTokens(http)
        self.streams = VideoStreams(http)
