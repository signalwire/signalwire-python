# AUTO-GENERATED from porting-sdk/rest-apis/chat/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``chat`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict

ChatChannel: TypeAlias = "dict[str, Any]"


class ChatPermissionWithRead(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        read: Gives the token read access to the channel.
        write: Gives the token write access to the channel.
    """

    read: bool
    write: bool


class ChatPermissionWithWrite(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        read: Gives the token read access to the channel.
        write: Gives the token write access to the channel.
    """

    read: bool
    write: bool


ChatState: TypeAlias = "dict[str, Any]"


class ChatToken(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        token: The generated Chat Token.
    """

    token: str


class ChatToken422Error(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class NewChatToken(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        ttl: The maximum time, in minutes, that the access token will be valid for.
            Between 1 and 43,200 (30 days).
        channels: User-defined channel names with read/write permissions. Max of 500
            channels. Channel names cannot start with the reserved prefix `sw_` and can
            be up to 250 characters.
        member_id: The unique identifier of the member. Up to 250 characters. If not
            specified, a random UUID will be generated.
        state: An arbitrary JSON object available to store stateful application
            information in. Must be valid JSON and have a maximum size of 2,000
            characters.
    """

    ttl: int
    channels: ChatChannel
    member_id: str
    state: ChatState


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


CreateChatTokenRequest: TypeAlias = "NewChatToken"
CreateChatTokenResponse: TypeAlias = "ChatToken"
