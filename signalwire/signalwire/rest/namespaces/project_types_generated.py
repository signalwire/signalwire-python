# AUTO-GENERATED from porting-sdk/rest-apis/project/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class CreateTokenRequest(TypedDict, total=False):
    """Request body for creating a new API Token.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    permissions: list[TokenPermission]
    subproject_id: str


TokenPermission: TypeAlias = "Literal['calling', 'chat', 'datasphere', 'fax', 'management', 'messaging', 'numbers', 'pubsub', 'storage', 'tasking', 'video']"


class TokenResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: str
    name: str
    permissions: list[TokenPermission]
    token: str


class TokenStatusCode422(TypedDict, total=False):
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


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


class Types_StatusCodes_StatusCode404(TypedDict, total=False):
    """The server cannot find the requested resource.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Not Found"]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


class UpdateTokenRequest(TypedDict, total=False):
    """Request body for updating an API Token.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    permissions: list[TokenPermission]


CreateTokenResponse: TypeAlias = "TokenResponse"
UpdateTokenResponse: TypeAlias = "TokenResponse"
