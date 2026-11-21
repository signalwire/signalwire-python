# AUTO-GENERATED from porting-sdk/rest-apis/messages/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``messages`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class CreateMessageRequest(TypedDict, total=False):
    """Request body for sending a new SMS or MMS message.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): Source phone number. Must be a purchased SignalWire phone
      number on the project in E.164 format, or a shortcode (5-6 digits). Verified
      caller IDs are not permitted.

    Attributes:
        to: Destination phone number in E.164 format (`+` followed by 5-17 digits). Also
            accepts passthrough numbers like `988`/`+988`.
        body: Message body text. Required if `media` is not provided. Subject to
            provider-specific character limits.
        media: Array of HTTP or HTTPS URLs for media attachments. Presence of media
            makes the message MMS. Maximum 8 items.
        send_as_mms: Force the message to be sent as MMS even when no media attachments
            are provided.
        status_callback: A valid URL to receive message status callback events at each
            state change. See the [Message status
            callback](https://signalwire.com/docs/apis/rest/messages/webhooks/message-status-callback)
            webhook for the payload your URL will receive.
        custom_variables: Your own key/value string pairs to attach to the message — for
            example, an order or case number you want to recognize later. When you also
            set `status_callback`, SignalWire includes these pairs as a
            `custom_variables` object in every status callback it sends to that URL, so
            you can match each callback to a record in your own system. If you don't set
            `status_callback`, there is nowhere for the variables to be delivered.

            Each value must be a non-empty string of at most 1024 bytes. You can send at
            most 20 pairs. Each key must start with a letter or underscore and contain
            only letters, numbers, and underscores, and cannot begin with the reserved
            prefixes `signalwire_`, `sw_`, `rtc_`, or `internal_` (case-insensitive).
            Keys are case-sensitive.
    """

    to: str
    # non-identifier field 'from': str
    body: str
    media: list[str]
    send_as_mms: bool
    status_callback: str
    custom_variables: dict[str, str]


class UpdateMessageRequest(TypedDict, total=False):
    """Request body for redacting the body of a previously sent message.

    Only `body` may be updated, and it must be an empty string.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        body: Must be an empty string (`""`) to redact the message. Any non-empty value
            is rejected with `body_must_be_empty`. This is the only field that can be
            updated.
    """

    body: str


class Message(TypedDict, total=False):
    """A message record.

    Returned by the create and update endpoints.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The source phone number.

    Attributes:
        id: The unique ID of the message. This is the `MessageSegment` ID, consistent
            with the dashboard and the `/api/messaging/logs` endpoint.
        to: The destination phone number.
        body: The message body text. Returns an empty string when the message has been
            redacted.
        media: Array of URLs for any media attachments on the message. Empty for SMS.
        number_of_segments: Number of segments the message body was split into for
            delivery.
        error_code: Provider-specific error code if delivery failed. Null when no error
            occurred.
        error_message: Human-readable error message if delivery failed. Null when no
            error occurred.
        created_at: Date and time when the message was created.
        project_id: The ID of the project the message belongs to.
        status_callback_url: Callback URL configured to receive message status events.
            Null if no callback was configured.
        message_uri: Relative URL for retrieving the message via the
            `/api/messaging/logs` endpoint.
    """

    id: uuid
    # non-identifier field 'from': str
    to: str
    body: str
    status: MessageStatus
    direction: MessageDirection
    kind: MessageKind
    media: list[str]
    number_of_segments: int
    error_code: str | None
    error_message: str | None
    created_at: str
    project_id: uuid
    status_callback_url: str | None
    message_uri: str


MessageStatus: TypeAlias = "Literal['queued', 'initiated', 'sent', 'delivered', 'undelivered', 'failed', 'read']"

MessageDirection: TypeAlias = "Literal['inbound', 'outbound']"

MessageKind: TypeAlias = "Literal['sms', 'mms']"


class MessagesCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class MessagesUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class Types_StatusCodes_RestApiErrorItem(TypedDict, total=False):
    """Details about a specific error.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        type: The category of error.
        code: A specific error code.
        message: A description of what caused the error.
        attribute: The request parameter that caused the error, if applicable.
        url: A link to documentation about this error.
    """

    type: str
    code: str
    message: str
    attribute: str | None
    url: str


class Types_StatusCodes_StatusCode400(TypedDict, total=False):
    """The request is invalid.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Bad Request"]


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


class Types_StatusCodes_StatusCode404(TypedDict, total=False):
    """The server cannot find the requested resource.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Not Found"]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


uuid: TypeAlias = "str"

CreateMessageResponse: TypeAlias = "Message"
UpdateMessageResponse: TypeAlias = "Message"
