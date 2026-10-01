# AUTO-GENERATED from porting-sdk/rest-apis/messages/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import BaseResource, _required_via_extras

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .messages_types_generated import (
        Message,
    )


class Messages(BaseResource):
    """Typed resource for ``/messages`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/messaging/messages")

    @_required_via_extras("to", from_="from")
    def create(
        self,
        *,
        to: str,
        from_: str,
        body: str | dict[str, Any] | list[dict[str, Any]] | None = None,
        media: list[str] | None = None,
        send_as_mms: bool | None = None,
        status_callback: str | None = None,
        custom_variables: dict[str, str] | None = None,
        message_type: Literal[
            "whatsapp_media_text",
            "whatsapp_media_contacts",
            "whatsapp_media_audio",
            "whatsapp_media_document",
            "whatsapp_media_image",
            "whatsapp_media_sticker",
            "whatsapp_media_video",
            "whatsapp_media_reaction",
            "whatsapp_media_location",
            "whatsapp_interactive_cta",
            "whatsapp_interactive_flow",
            "whatsapp_interactive_list",
            "whatsapp_interactive_location_request_message",
            "whatsapp_interactive_reply_button",
        ]
        | None = None,
        template_id: str | None = None,
        header_template_parameters: dict[str, Any] | list[Any] | str | None = None,
        body_template_parameters: dict[str, Any] | list[Any] | None = None,
        button_template_parameters: list[str] | None = None,
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
                "message_type": message_type,
                "template_id": template_id,
                "header_template_parameters": header_template_parameters,
                "body_template_parameters": body_template_parameters,
                "button_template_parameters": button_template_parameters,
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
        body: str | None = None,
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
