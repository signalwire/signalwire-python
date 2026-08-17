"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

RestClient — top-level REST client with namespaced sub-objects.
"""

import os

from ._base import HttpClient
from ._request_options import RequestOptions
from .namespaces._client_tree_generated import _GeneratedResourceTree


class RestClient(_GeneratedResourceTree):
    """REST client for the SignalWire platform APIs.

    Usage:
        client = RestClient(
            project="your-project-id",
            token="your-api-token",
            host="your-space.signalwire.com",
        )

        # Or use environment variables:
        #   SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN, SIGNALWIRE_SPACE
        client = RestClient()

        # Use namespaced resources
        client.fabric.ai_agents.list()
        client.calling.play(call_id, play=[...])
        client.phone_numbers.search(areacode="512")
        client.video.rooms.create(name="standup")

    The resource object tree (flat resources + namespace containers) is generated from
    the specs (``_GeneratedResourceTree._wire_resources``); this class owns only auth.
    """

    def __init__(
        self,
        project: str | None = None,
        token: str | None = None,
        host: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> None:
        project = project or os.environ.get("SIGNALWIRE_PROJECT_ID", "")
        token = token or os.environ.get("SIGNALWIRE_API_TOKEN", "")
        host = host or os.environ.get("SIGNALWIRE_SPACE", "")

        if not project or not token or not host:
            raise ValueError(
                "project, token, and host are required. "
                "Provide them as arguments or set SIGNALWIRE_PROJECT_ID, "
                "SIGNALWIRE_API_TOKEN, and SIGNALWIRE_SPACE environment variables."
            )

        self._project = project
        self._http = HttpClient(project, token, host, request_options=request_options)

        # Generated resource tree (flat resources + namespace containers).
        self._wire_resources(self._http)
