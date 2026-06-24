"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Number Groups namespace — CRUD + membership management.
"""

from typing import TYPE_CHECKING, Any

from .._base import CrudResource

if TYPE_CHECKING:
    from .relay_rest_types_generated import (
        NumberGroupMembership,
        NumberGroupMembershipListResponse,
    )


class NumberGroupsResource(CrudResource):
    """Number group management with membership operations."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/number_groups")

    def list_memberships(
        self, group_id: str, **params: Any
    ) -> "NumberGroupMembershipListResponse":
        return self._http.get(
            self._path(group_id, "number_group_memberships"),
            params=params or None,
        )

    def add_membership(self, group_id: str, **kwargs: Any) -> "NumberGroupMembership":
        return self._http.post(
            self._path(group_id, "number_group_memberships"),
            body=kwargs,
        )

    def get_membership(self, membership_id: str) -> "NumberGroupMembership":
        return self._http.get(
            f"/api/relay/rest/number_group_memberships/{membership_id}"
        )

    def delete_membership(self, membership_id: str) -> dict[str, Any]:
        return self._http.delete(
            f"/api/relay/rest/number_group_memberships/{membership_id}"
        )
