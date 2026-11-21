# AUTO-GENERATED from porting-sdk/rest-apis/voice/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``voice`` REST resources, generated from the OpenAPI spec.

One resource class per spec collection: closed, typed ``create`` / ``update``
parameters (the explicit spec fields) and typed sub-operation methods, plus an
``extras`` escape hatch and a ``**_reserved_kw`` tail for unknown or reserved-word
wire fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from .._base import ReadResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .voice_types_generated import (
        LogEventsListResponse,
        LogListResponse,
        VoiceLog,
    )


class VoiceLogs(ReadResource["LogListResponse", "VoiceLog"]):
    """Typed resource for ``/logs`` (generated).

    Bound to ``/api/voice/logs``; construct it as ``VoiceLogs(http)`` with the client's
    HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/voice/logs")

    def list_events(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> LogEventsListResponse:
        """List all events for a specific log.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the log. This is the segment_id you can find in Relay call
                details in your Dashboard UI or in return objects when using the SDK.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Response model for log events list endpoint
        """
        return cast(
            "LogEventsListResponse",
            self._http.get(
                self._path(id, "events"),
                params=params or None,
                request_options=request_options,
            ),
        )
