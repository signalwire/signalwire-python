# AUTO-GENERATED from porting-sdk/rest-apis/projects/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``projects`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


class Project(TypedDict, total=False):
    """A project or subproject within the caller's project tree.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Project identifier.
        name: Project name.
        parent_project_id: The root project's ID; `null` for a root project.
        subproject: `true` if this project is a subproject.
        region_preference: Effective region preference. Returned in all responses; not
            currently settable via this API.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: Project name. **Required.** Max 250 characters.
    """

    name: str
    protect_recordings: bool
    protect_message_media: bool
    protect_fax_media: bool
    force_https_requests: bool


ProjectUpdate: TypeAlias = "ProjectCreate"


class ProjectList(TypedDict, total=False):
    """A page of projects.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: dict[str, Any]
    data: list[Project]


class ProjectStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters or violates a business rule.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation or business-rule errors.
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
        attribute: The request parameter that caused the error, or null for
            project-level errors.
        url: A link to documentation about this error.
    """

    type: str
    code: str
    message: str
    attribute: str | None
    url: str


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


class Types_StatusCodes_StatusCode403(TypedDict, total=False):
    """The API token lacks the required `Management` scope.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Forbidden"]


class Types_StatusCodes_StatusCode404(TypedDict, total=False):
    """The server cannot find the requested resource.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Not Found"]


ListProjectsResponse: TypeAlias = "ProjectList"
CreateSubprojectRequest: TypeAlias = "ProjectCreate"
CreateSubprojectResponse: TypeAlias = "ProjectWithSigningKey"
GetProjectResponse: TypeAlias = "Project"
UpdateProjectRequest: TypeAlias = "ProjectUpdate"
UpdateProjectResponse: TypeAlias = "Project"
RotateSigningKeyResponse: TypeAlias = "ProjectWithSigningKey"
