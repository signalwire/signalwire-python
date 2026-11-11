# AUTO-GENERATED from porting-sdk/rest-apis/projects/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``projects`` REST resources, generated from the OpenAPI spec.

One resource class per spec collection: closed, typed ``create`` / ``update``
parameters (the explicit spec fields) and typed sub-operation methods, plus an
``extras`` escape hatch and a ``**_reserved_kw`` tail for unknown or reserved-word
wire fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import CrudResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .projects_types_generated import (
        Project,
        ProjectCreate,
        ProjectList,
        ProjectUpdate,
        ProjectWithSigningKey,
    )


class Projects(
    CrudResource["ProjectList", "Project", "ProjectCreate", "ProjectUpdate"]
):
    """Typed resource for ``/projects`` (generated).

    Bound to ``/api/projects``; construct it as ``Projects(http)`` with the client's
    HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/projects")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        protect_recordings: bool | None = None,
        protect_message_media: bool | None = None,
        protect_fax_media: bool | None = None,
        force_https_requests: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Project:
        """Creates a subproject under the authenticated root project.

        Only allowed when authenticated as a top-level project. The response includes
        the `signing_key`, which is not retrievable afterward.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Management_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            name: Project name. **Required.** Max 250 characters.
            protect_recordings: The ``protect_recordings`` request field.
            protect_message_media: The ``protect_message_media`` request field.
            protect_fax_media: The ``protect_fax_media`` request field.
            force_https_requests: The ``force_https_requests`` request field.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            A project as returned by create and signing-key rotate, including the
            signing key.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "protect_recordings": protect_recordings,
                "protect_message_media": protect_message_media,
                "protect_fax_media": protect_fax_media,
                "force_https_requests": force_https_requests,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "Project",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        protect_recordings: bool | None = None,
        protect_message_media: bool | None = None,
        protect_fax_media: bool | None = None,
        force_https_requests: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Project:
        """Updates the project's name and settings.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Management_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: The project or subproject ID.
            name: Project name. **Required.** Max 250 characters.
            protect_recordings: The ``protect_recordings`` request field.
            protect_message_media: The ``protect_message_media`` request field.
            protect_fax_media: The ``protect_fax_media`` request field.
            force_https_requests: The ``force_https_requests`` request field.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            A project or subproject within the caller's project tree.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "protect_recordings": protect_recordings,
                "protect_message_media": protect_message_media,
                "protect_fax_media": protect_fax_media,
                "force_https_requests": force_https_requests,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "Project",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )

    def rotate_signing_key(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> ProjectWithSigningKey:
        """Rotates the project's signing key and returns the project with the new `signing_key`.

        The previous key may take 1-2 minutes to stop working.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Management_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: The project or subproject ID.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            A project as returned by create and signing-key rotate, including the
            signing key.
        """
        return cast(
            "ProjectWithSigningKey",
            self._http.post(
                self._path(id, "signing-key", "rotate"), request_options=request_options
            ),
        )
