# AUTO-GENERATED from porting-sdk/rest-apis/projects/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


class Project(TypedDict, total=False):
    """A project or subproject within the caller's project tree.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    name: str
    parent_project_id: str | None
    subproject: bool
    region_preference: str
    protect_recordings: bool
    protect_message_media: bool
    protect_fax_media: bool
    force_https_requests: bool
    created_at: str
    updated_at: str


ProjectWithSigningKey: TypeAlias = "dict[str, Any]"


class ProjectCreate(TypedDict, total=False):
    """Request body for creating a subproject.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    protect_recordings: bool
    protect_message_media: bool
    protect_fax_media: bool
    force_https_requests: bool


ProjectUpdate: TypeAlias = "ProjectCreate"


class ProjectList(TypedDict, total=False):
    """A page of projects.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: dict[str, Any]
    data: list[Project]


class ProjectStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters or violates a business rule. See errors for details.

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


class Types_StatusCodes_StatusCode403(TypedDict, total=False):
    """The API token lacks the required `Management` scope.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Forbidden"]


class Types_StatusCodes_StatusCode404(TypedDict, total=False):
    """The server cannot find the requested resource.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Not Found"]


ListProjectsResponse: TypeAlias = "ProjectList"
CreateSubprojectRequest: TypeAlias = "ProjectCreate"
CreateSubprojectResponse: TypeAlias = "ProjectWithSigningKey"
GetProjectResponse: TypeAlias = "Project"
UpdateProjectRequest: TypeAlias = "ProjectUpdate"
UpdateProjectResponse: TypeAlias = "Project"
RotateSigningKeyResponse: TypeAlias = "ProjectWithSigningKey"
