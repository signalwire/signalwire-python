# AUTO-GENERATED from porting-sdk/rest-apis/chat/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``chat`` REST resources, generated from the OpenAPI spec.

One resource class per spec collection: closed, typed ``create`` / ``update``
parameters (the explicit spec fields) and typed sub-operation methods, plus an
``extras`` escape hatch and a ``**_reserved_kw`` tail for unknown or reserved-word
wire fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import BaseResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .chat_types_generated import (
        ChatChannel,
        ChatState,
        ChatToken,
    )


class Chat(BaseResource):
    """Typed resource for ``/tokens`` (generated).

    Bound to ``/api/chat/tokens``; construct it as ``Chat(http)`` with the client's HTTP
    transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/chat/tokens")

    def create_token(
        self,
        *,
        ttl: int,
        channels: ChatChannel,
        member_id: str | None = None,
        state: ChatState | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> ChatToken:
        """Generate a Chat Token to be used to authenticate clients to the Chat Service.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Chat_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            ttl: The maximum time, in minutes, that the access token will be valid for.
                Between 1 and 43,200 (30 days).
            channels: User-defined channel names with read/write permissions. Max of 500
                channels. Channel names cannot start with the reserved prefix `sw_` and
                can be up to 250 characters.
            member_id: The unique identifier of the member. Up to 250 characters. If not
                specified, a random UUID will be generated.
            state: An arbitrary JSON object available to store stateful application
                information in. Must be valid JSON and have a maximum size of 2,000
                characters.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "ttl": ttl,
                "channels": channels,
                "member_id": member_id,
                "state": state,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "ChatToken",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )
