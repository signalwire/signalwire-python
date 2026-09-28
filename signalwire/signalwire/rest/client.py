"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

RestClient — top-level REST client with namespaced sub-objects.

The SDK's installed documentation covers this module: run ``sw-pydocs rest``, or ``sw-pydocs`` for the index.
"""

import os
from typing import Any

from ._base import HttpClient
from ._request_options import RequestOptions
from .namespaces._client_tree_generated import _GeneratedResourceTree


class _MissingCredentialHttp:
    """Stands in for the HTTP client of a credential the ``RestClient`` was not given.

    Every request raises ``ValueError`` naming the missing credential, before anything is
    sent — so a client built with only a Personal Access Token fails loudly on a project
    resource (and a project-only client on ``client.space``) instead of sending a request
    the server can only refuse.
    """

    def __init__(self, message: str) -> None:
        self._message = message

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__"):
            raise AttributeError(name)

        def _refuse(*_args: Any, **_kwargs: Any) -> Any:
            raise ValueError(self._message)

        return _refuse


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

        # The Space Administration API (client.space) authenticates with a user's
        # Personal Access Token instead of a project token:
        admin = RestClient(
            personal_access_token="pat_...", host="your-space.signalwire.com"
        )
        admin.space.members.list()

    The resource object tree (flat resources + namespace containers) is generated from
    the specs (``_GeneratedResourceTree._wire_resources``); this class owns only auth.
    """

    def __init__(
        self,
        project: str | None = None,
        token: str | None = None,
        host: str | None = None,
        request_options: RequestOptions | None = None,
        personal_access_token: str | None = None,
    ) -> None:
        """Create a client for one project, one space's administration API, or both.

        Each argument falls back to its environment variable when omitted:
        ``SIGNALWIRE_PROJECT_ID``, ``SIGNALWIRE_API_TOKEN``, ``SIGNALWIRE_SPACE`` and
        ``SIGNALWIRE_PERSONAL_ACCESS_TOKEN``.

        ``project`` + ``token`` authenticate every project-scoped resource.
        ``personal_access_token`` (a user's ``pat_...`` token) authenticates
        ``client.space``, which prime-rails serves only to a Personal Access Token
        (HTTP Basic with an empty username). Either credential, or both, may be given;
        calling a resource whose credential is missing raises ``ValueError``.

        Raises ``ValueError`` if ``host`` is missing, or if neither a complete
        ``project`` + ``token`` pair nor a ``personal_access_token`` is given.
        """
        project = project or os.environ.get("SIGNALWIRE_PROJECT_ID", "")
        token = token or os.environ.get("SIGNALWIRE_API_TOKEN", "")
        host = host or os.environ.get("SIGNALWIRE_SPACE", "")
        pat = personal_access_token or os.environ.get(
            "SIGNALWIRE_PERSONAL_ACCESS_TOKEN", ""
        )

        has_project = bool(project and token)
        if not host or not (has_project or pat):
            raise ValueError(
                "project, token, and host are required. "
                "Provide them as arguments or set SIGNALWIRE_PROJECT_ID, "
                "SIGNALWIRE_API_TOKEN, and SIGNALWIRE_SPACE environment variables "
                "(or, for client.space only, host and personal_access_token / "
                "SIGNALWIRE_PERSONAL_ACCESS_TOKEN)."
            )

        self._project = project
        self._http: Any = (
            HttpClient(project, token, host, request_options=request_options)
            if has_project
            else _MissingCredentialHttp(
                "project and token are required for this resource "
                "(SIGNALWIRE_PROJECT_ID / SIGNALWIRE_API_TOKEN); this client has only "
                "a personal access token, which authenticates client.space"
            )
        )
        # A Personal Access Token is HTTP Basic with an EMPTY username
        # (prime-rails API::Space::BaseController -> Authenticators::PersonalAccessToken).
        self._pat_http: Any = (
            HttpClient("", pat, host, request_options=request_options)
            if pat
            else _MissingCredentialHttp(
                "personal_access_token is required for client.space "
                "(SIGNALWIRE_PERSONAL_ACCESS_TOKEN)"
            )
        )

        # Generated resource tree (flat resources + namespace containers).
        self._wire_resources(self._http, self._pat_http)
