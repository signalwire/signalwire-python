# AUTO-GENERATED from porting-sdk/rest-apis/pubsub/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``pubsub`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


class NewPubSubToken(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        ttl: The maximum time, in minutes, for which the access token will be valid.
            Between 1 and 43,200 (30 days).
        channels: Each channel with `write` and `read` objects with boolean as values.
            Max of 500 channels inside main `channels`. Either `read`, `write`, or both
            are required inside each channel and default to false. Each channel name can
            be up to 250 characters. Must be valid JSON.
        member_id: The unique identifier of the member. Up to 250 characters. If not
            specified, a random UUID will be generated.
        state: An arbitrary JSON object available to store stateful application
            information in. Must be valid JSON and have a maximum size of 2,000
            characters.
    """

    ttl: int
    channels: PubSubChannels
    member_id: str
    state: PubSubState


PubSubChannels: TypeAlias = "dict[str, Any]"


class PubSubPermissionWithRead(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        read: Gives the token read access to the channel.
        write: Gives the token write access to the channel.
    """

    read: bool
    write: bool


class PubSubPermissionWithWrite(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        read: Gives the token read access to the channel.
        write: Gives the token write access to the channel.
    """

    read: bool
    write: bool


PubSubState: TypeAlias = "dict[str, Any]"


class PubSubToken(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        token: A PubSub Token to be used to authenticate clients to the PubSub Service.
    """

    token: str


class PubSubToken422Error(TypedDict, total=False):
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


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


CreateTokenRequest: TypeAlias = "NewPubSubToken"
CreateTokenResponse: TypeAlias = "PubSubToken"
