"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

This module path and the *Resource / *Namespace names below were superseded when the
REST layer became spec-generated (classes moved to ``*_resources_generated.py`` and lost
their suffixes). This thin re-export keeps old Python imports
(``from signalwire.signalwire.rest.namespaces.video import VideoRooms``) working. New code
should import from the generated module / use ``client.video`` instead. PYTHON-ONLY: the
surface oracle skips this file (the marker above), so no other port implements these.
"""

from .video_resources_generated import VideoConferenceTokens, VideoConferences, VideoRoomRecordings, VideoRoomSessions, VideoRoomTokens, VideoRooms, VideoStreams
from ._client_tree_generated import VideoNamespace

__all__ = ["VideoConferenceTokens", "VideoConferences", "VideoNamespace", "VideoRoomRecordings", "VideoRoomSessions", "VideoRoomTokens", "VideoRooms", "VideoStreams"]
