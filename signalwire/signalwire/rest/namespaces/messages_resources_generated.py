# AUTO-GENERATED from porting-sdk/rest-apis/messages/openapi.yaml — DO NOT EDIT.
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

    from .messages_types_generated import (
        Message,
    )


class Messages(BaseResource):
    """Typed resource for ``/messages`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/messaging/messages")

    def create(
        self,
        *,
        to: str,
        from_: str,
        body: str | None = None,
        media: list[str] | None = None,
        send_as_mms: bool | None = None,
        status_callback: str | None = None,
        custom_variables: dict[str, str] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Message:
        body_: dict[str, Any] = {
            k: v
            for k, v in {
                "to": to,
                "from": from_,
                "body": body,
                "media": media,
                "send_as_mms": send_as_mms,
                "status_callback": status_callback,
                "custom_variables": custom_variables,
            }.items()
            if v is not None
        }
        if extras:
            body_.update(extras)
        body_.update(_reserved_kw)
        return cast(
            "Message",
            self._http.post(
                self._base_path, body=body_, request_options=request_options
            ),
        )

    def update(
        self,
        message_id: str,
        *,
        body: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Message:
        body_: dict[str, Any] = {
            k: v for k, v in {"body": body}.items() if v is not None
        }
        if extras:
            body_.update(extras)
        body_.update(_reserved_kw)
        return cast(
            "Message",
            self._http.patch(
                self._path(message_id), body=body_, request_options=request_options
            ),
        )
