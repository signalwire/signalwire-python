# AUTO-GENERATED from porting-sdk/rest-apis/chat/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
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
    """Typed resource for ``/tokens`` (generated)."""

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
