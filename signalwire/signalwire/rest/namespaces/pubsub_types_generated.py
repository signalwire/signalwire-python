# AUTO-GENERATED from porting-sdk/rest-apis/pubsub/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


class NewPubSubToken(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ttl: int
    channels: PubSubChannels
    member_id: str
    state: PubSubState


PubSubChannels: TypeAlias = "dict[str, Any]"


class PubSubPermissionWithRead(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    read: bool
    write: bool


class PubSubPermissionWithWrite(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    read: bool
    write: bool


PubSubState: TypeAlias = "dict[str, Any]"


class PubSubToken(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    token: str


class PubSubToken422Error(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


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


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


CreateTokenRequest: TypeAlias = "NewPubSubToken"
CreateTokenResponse: TypeAlias = "PubSubToken"
