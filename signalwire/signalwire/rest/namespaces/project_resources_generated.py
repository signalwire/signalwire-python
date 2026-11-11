# AUTO-GENERATED from porting-sdk/rest-apis/project/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``project`` REST resources, generated from the OpenAPI spec.

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

    from .project_types_generated import (
        TokenPermission,
        TokenResponse,
    )


class ProjectTokens(BaseResource):
    """Typed resource for ``/tokens`` (generated).

    Bound to ``/api/project/tokens``; construct it as ``ProjectTokens(http)`` with the
    client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/project/tokens")

    def create(
        self,
        *,
        name: str,
        permissions: list[TokenPermission],
        subproject_id: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> TokenResponse:
        """Generate an API Token for a project to be used to authenticate requests within the project.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Management_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        **Token Permissions**

        You must set the functions allowed by this API Token by selecting which types of
        requests this API Token is allowed to make.

        Valid options are: calling, chat, datasphere, fax, management, messaging,
        numbers, pubsub, storage, tasking, and video

        Args:
            name: The name representing the API token.
            permissions: The permissions you would like to enable for this token. Valid
                permissions are calling, chat, datasphere, fax, management, messaging,
                numbers, pubsub, storage, tasking, and video
            subproject_id: The unique identifier of the subproject you would like to
                create a token for. The subproject passed must be a child of the project
                used to authenticate the request.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "permissions": permissions,
                "subproject_id": subproject_id,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "TokenResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        token_id: str,
        *,
        name: str | None = None,
        permissions: list[TokenPermission] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> TokenResponse:
        """Update an API Token's name or permissions.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Management_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        **Token Permissions**

        You can modify the functions allowed by this API Token by selecting which types
        of requests this API Token is allowed to make.

        Valid options are: calling, chat, datasphere, fax, management, messaging,
        numbers, pubsub, storage, tasking, and video

        Args:
            token_id: The unique identifier of the token to update.
            name: The name representing the API token.
            permissions: The permissions you would like to enable for this token. Valid
                permissions are calling, chat, datasphere, fax, management, messaging,
                numbers, pubsub, storage, tasking, and video
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "permissions": permissions}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "TokenResponse",
            self._http.patch(
                self._path(token_id), body=body, request_options=request_options
            ),
        )

    def delete(
        self, token_id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        """Delete an API Token.

        This action cannot be undone.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Management_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            token_id: The unique identifier of the token that you want to delete.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The decoded JSON response (an empty dict when the server sends no body).
        """
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(token_id), request_options=request_options),
        )
