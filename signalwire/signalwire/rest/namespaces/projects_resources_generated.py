# AUTO-GENERATED from porting-sdk/rest-apis/projects/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import CrudResource

if TYPE_CHECKING:
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
    """Typed resource for ``/projects`` (generated)."""

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
        **_reserved_kw: Any,
    ) -> Project:
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
        return cast("Project", self._http.post(self._base_path, body=body))

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
        **_reserved_kw: Any,
    ) -> Project:
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
        return cast("Project", self._http.patch(self._path(id), body=body))

    def rotate_signing_key(self, id: str) -> ProjectWithSigningKey:
        return cast(
            "ProjectWithSigningKey",
            self._http.post(self._path(id, "signing-key", "rotate")),
        )
