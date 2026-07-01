# AUTO-GENERATED from porting-sdk/rest-apis/chat/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict

ChatChannel: TypeAlias = "dict[str, Any]"


class ChatPermissionWithRead(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    read: bool
    write: bool


class ChatPermissionWithWrite(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    read: bool
    write: bool


ChatState: TypeAlias = "dict[str, Any]"


class ChatToken(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    token: str


class ChatToken422Error(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class NewChatToken(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ttl: int
    channels: ChatChannel
    member_id: str
    state: ChatState


class Types_StatusCodes_RestApiErrorItem(TypedDict, total=False):
    """Details about a specific error.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: str
    code: str
    message: str
    attribute: str | None
    url: str


class Types_StatusCodes_StatusCode400(TypedDict, total=False):
    """The request is invalid.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Bad Request"]


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


CreateChatTokenRequest: TypeAlias = "NewChatToken"
CreateChatTokenResponse: TypeAlias = "ChatToken"
