"""Deprecated import path for ``video`` REST symbols.

These symbols moved out of ``namespaces.video`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.rest.namespaces.video import VideoRooms``
working but emits a :class:`DeprecationWarning`. Prefer ``client.video`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.rest.namespaces.video is deprecated; use client.video. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .video_resources_generated import (  # noqa: E402  (re-export after the deprecation warn — intentional)
    VideoConferenceTokens,
    VideoConferences,
    VideoRoomRecordings,
    VideoRoomSessions,
    VideoRoomTokens,
    VideoRooms,
    VideoStreams,
)
from ._client_tree_generated import VideoNamespace  # noqa: E402  (re-export after the deprecation warn — intentional)

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
