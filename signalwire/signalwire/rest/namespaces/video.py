"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

Deprecated import path. The REST layer is spec-generated; these symbols moved out of
``namespaces.video`` (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.video import VideoRooms`` working
but emits a DeprecationWarning. Prefer ``client.video`` (no import needed). PYTHON-ONLY: the
surface oracle skips this file, so no other port implements these.
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.video is deprecated; use client.video. "
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
