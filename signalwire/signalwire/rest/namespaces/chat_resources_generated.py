# AUTO-GENERATED from porting-sdk/rest-apis/chat/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed create/update
# (explicit spec fields + an ``extras`` door), bound to the resource's spec
# types. Runtime body is a plain dict (open-tail, never validated).
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import BaseResource

if TYPE_CHECKING:
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
        return cast("ChatToken", self._http.post(self._base_path, body=body))
