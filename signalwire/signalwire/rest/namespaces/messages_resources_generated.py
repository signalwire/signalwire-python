# AUTO-GENERATED from porting-sdk/rest-apis/messages/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``messages`` REST resources, generated from the OpenAPI spec.

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

    from .messages_types_generated import (
        Message,
    )


class Messages(BaseResource):
    """Typed resource for ``/messages`` (generated).

    Bound to ``/api/messaging/messages``; construct it as ``Messages(http)`` with the
    client's HTTP transport.
    """

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
        """Create and queue an outbound SMS or MMS message for delivery.

        The system determines whether the message is SMS or MMS based on the presence of
        `media` or the `send_as_mms` flag. The `from` number must be a purchased
        SignalWire phone number on the authenticated project.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Messaging_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            to: Destination phone number in E.164 format (`+` followed by 5-17 digits).
                Also accepts passthrough numbers like `988`/`+988`.
            from_: Source phone number. Must be a purchased SignalWire phone number on
                the project in E.164 format, or a shortcode (5-6 digits). Verified
                caller IDs are not permitted. Sent as the wire key ``from``.
            body: Message body text. Required if `media` is not provided. Subject to
                provider-specific character limits.
            media: Array of HTTP or HTTPS URLs for media attachments. Presence of media
                makes the message MMS. Maximum 8 items.
            send_as_mms: Force the message to be sent as MMS even when no media
                attachments are provided.
            status_callback: A valid URL to receive message status callback events at
                each state change. See the [Message status
                callback](https://signalwire.com/docs/apis/rest/messages/webhooks/message-status-callback)
                webhook for the payload your URL will receive.
            custom_variables: Your own key/value string pairs to attach to the message —
                for example, an order or case number you want to recognize later. When
                you also set `status_callback`, SignalWire includes these pairs as a
                `custom_variables` object in every status callback it sends to that URL,
                so you can match each callback to a record in your own system. If you
                don't set `status_callback`, there is nowhere for the variables to be
                delivered.

                Each value must be a non-empty string of at most 1024 bytes. You can
                send at most 20 pairs. Each key must start with a letter or underscore
                and contain only letters, numbers, and underscores, and cannot begin
                with the reserved prefixes `signalwire_`, `sw_`, `rtc_`, or `internal_`
                (case-insensitive). Keys are case-sensitive.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            A message record.
        """
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
        """Redact the body of a previously sent message.

        This endpoint clears the message body for compliance, privacy, or moderation
        purposes — it does not support arbitrary updates to message attributes. The only
        accepted value for `body` is an empty string (`""`); any other value is
        rejected.

        Messages that are still in progress (`queued` or `initiated`) cannot be
        redacted. Messages in terminal states such as `delivered`, `undelivered`, or
        `failed` are eligible. Once redacted, the original body is overwritten and
        cannot be recovered.

        The `message_id` path parameter is the message segment ID — the same ID returned
        by the create endpoint and shown in `/api/messaging/logs`.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Messaging_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            message_id: The message segment ID — the same ID returned by the create
                endpoint and shown in `/api/messaging/logs`.
            body: Must be an empty string (`""`) to redact the message. Any non-empty
                value is rejected with `body_must_be_empty`. This is the only field that
                can be updated.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            A message record.
        """
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
