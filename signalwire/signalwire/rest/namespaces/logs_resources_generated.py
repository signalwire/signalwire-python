# AUTO-GENERATED from porting-sdk/rest-apis/logs/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``logs`` REST resources, generated from the OpenAPI spec.

One resource class per spec collection: closed, typed ``create`` / ``update``
parameters (the explicit spec fields) and typed sub-operation methods, plus an
``extras`` escape hatch and a ``**_reserved_kw`` tail for unknown or reserved-word
wire fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from .._base import BaseResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .logs_types_generated import (
        ConferencesResponse,
    )


class ConferenceLogs(BaseResource):
    """Typed resource for ``/conferences`` (generated).

    Bound to ``/api/logs/conferences``; construct it as ``ConferenceLogs(http)`` with
    the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/logs/conferences")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ConferencesResponse:
        """A list of Conferences.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_ or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``include_deleted``: Include logs for deleted activity.
                - ``created_on``: Return logs for activity on this date. Accepts a date
                  (YYYY-MM-DD) or ISO 8601 timestamp.
                - ``created_before``: Return logs for activity prior to this date.
                  Accepts a date (YYYY-MM-DD) or ISO 8601 timestamp.
                - ``created_after``: Return logs for activity after this date. Accepts a
                  date (YYYY-MM-DD) or ISO 8601 timestamp.
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: Specify the number of results to return on a single
                  page. The default page size is `50` and the maximum is `1000`.
                - ``page_token``: Token for cursor-based pagination. Required when
                  `page_number` > 0.

        Returns:
            Response containing a list of conferences.
        """
        return cast(
            "ConferencesResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )
