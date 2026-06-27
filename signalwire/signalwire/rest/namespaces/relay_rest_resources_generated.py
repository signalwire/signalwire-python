# AUTO-GENERATED from porting-sdk/rest-apis/relay-rest/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed create/update
# (explicit spec fields + an ``extras`` door), bound to the resource's spec
# types. Runtime body is a plain dict (open-tail, never validated).
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import CrudResource

if TYPE_CHECKING:
    from .relay_rest_types_generated import (
        AvailablePhoneNumbersResponse,
        CreateNumberGroupRequest,
        CreateQueueRequest,
        CreateVerifiedCallerIDRequest,
        NumberGroupListResponse,
        NumberGroupMembershipListResponse,
        NumberGroupMembershipResponse,
        NumberGroupResponse,
        PhoneNumberCallHandlerRequest,
        PhoneNumberListResponse,
        PhoneNumberMessageHandler,
        PhoneNumberResponse,
        PurchasePhoneNumberRequest,
        QueueListResponse,
        QueueMemberListResponse,
        QueueMemberResponse,
        QueueResponse,
        UpdateNumberGroupRequest,
        UpdatePhoneNumberRequest,
        UpdateQueueRequest,
        UpdateVerifiedCallerIDRequest,
        VerifiedCallerIDListResponse,
        VerifiedCallerIDResponse,
        uuid,
    )


class NumberGroupsResource(
    CrudResource[
        "NumberGroupListResponse",
        "NumberGroupResponse",
        "CreateNumberGroupRequest",
        "UpdateNumberGroupRequest",
    ]
):
    """Typed CRUD resource for ``/number_groups`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/number_groups")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        sticky_sender: bool | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> NumberGroupResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "sticky_sender": sticky_sender}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("NumberGroupResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        sticky_sender: bool | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> NumberGroupResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "sticky_sender": sticky_sender}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("NumberGroupResponse", self._http.put(self._path(id), body=body))

    def list_memberships(
        self, number_group_id: str
    ) -> NumberGroupMembershipListResponse:
        return cast(
            "NumberGroupMembershipListResponse",
            self._http.get(
                self._path("number_groups", number_group_id, "number_group_memberships")
            ),
        )

    def add_membership(
        self,
        number_group_id: str,
        *,
        phone_number_id: uuid,
        extras: Mapping[str, Any] | None = None,
    ) -> NumberGroupMembershipResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"phone_number_id": phone_number_id}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast(
            "NumberGroupMembershipResponse",
            self._http.post(
                self._path(
                    "number_groups", number_group_id, "number_group_memberships"
                ),
                body=body,
            ),
        )

    def get_membership(self, id: str) -> NumberGroupMembershipResponse:
        return cast(
            "NumberGroupMembershipResponse",
            self._http.get(self._path("number_group_memberships", id)),
        )

    def delete_membership(self, id: str) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path("number_group_memberships", id)),
        )


class PhoneNumbersResource(
    CrudResource[
        "PhoneNumberListResponse",
        "PhoneNumberResponse",
        "PurchasePhoneNumberRequest",
        "UpdatePhoneNumberRequest",
    ]
):
    """Typed CRUD resource for ``/phone_numbers`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/phone_numbers")

    def create(  # type: ignore[override]
        self, *, number: str, extras: Mapping[str, Any] | None = None
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {
            k: v for k, v in {"number": number}.items() if v is not None
        }
        if extras:
            body.update(extras)
        return cast("PhoneNumberResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        call_handler: PhoneNumberCallHandlerRequest | None = None,
        call_receive_mode: str | None = None,
        call_request_url: str | None = None,
        call_request_method: Literal["GET", "POST"] | None = None,
        call_fallback_url: str | None = None,
        call_fallback_method: Literal["GET", "POST"] | None = None,
        call_status_callback_url: str | None = None,
        call_status_callback_method: Literal["GET", "POST"] | None = None,
        call_laml_application_id: str | None = None,
        call_dialogflow_agent_id: str | None = None,
        call_relay_topic: str | None = None,
        call_relay_topic_status_callback_url: str | None = None,
        call_relay_script_url: str | None = None,
        call_relay_context: str | None = None,
        call_relay_context_status_callback_url: str | None = None,
        call_relay_application: str | None = None,
        call_relay_connector_id: str | None = None,
        call_sip_endpoint_id: str | None = None,
        call_verto_resource: str | None = None,
        call_video_room_id: uuid | None = None,
        call_ai_agent_id: uuid | None = None,
        call_flow_id: uuid | None = None,
        call_flow_version: Literal["working_copy", "current_deployed"] | None = None,
        message_handler: PhoneNumberMessageHandler | None = None,
        message_request_url: str | None = None,
        message_request_method: Literal["GET", "POST"] | None = None,
        message_fallback_url: str | None = None,
        message_fallback_method: Literal["GET", "POST"] | None = None,
        message_laml_application_id: str | None = None,
        message_relay_topic: str | None = None,
        message_relay_context: str | None = None,
        message_relay_application: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "call_handler": call_handler,
                "call_receive_mode": call_receive_mode,
                "call_request_url": call_request_url,
                "call_request_method": call_request_method,
                "call_fallback_url": call_fallback_url,
                "call_fallback_method": call_fallback_method,
                "call_status_callback_url": call_status_callback_url,
                "call_status_callback_method": call_status_callback_method,
                "call_laml_application_id": call_laml_application_id,
                "call_dialogflow_agent_id": call_dialogflow_agent_id,
                "call_relay_topic": call_relay_topic,
                "call_relay_topic_status_callback_url": call_relay_topic_status_callback_url,
                "call_relay_script_url": call_relay_script_url,
                "call_relay_context": call_relay_context,
                "call_relay_context_status_callback_url": call_relay_context_status_callback_url,
                "call_relay_application": call_relay_application,
                "call_relay_connector_id": call_relay_connector_id,
                "call_sip_endpoint_id": call_sip_endpoint_id,
                "call_verto_resource": call_verto_resource,
                "call_video_room_id": call_video_room_id,
                "call_ai_agent_id": call_ai_agent_id,
                "call_flow_id": call_flow_id,
                "call_flow_version": call_flow_version,
                "message_handler": message_handler,
                "message_request_url": message_request_url,
                "message_request_method": message_request_method,
                "message_fallback_url": message_fallback_url,
                "message_fallback_method": message_fallback_method,
                "message_laml_application_id": message_laml_application_id,
                "message_relay_topic": message_relay_topic,
                "message_relay_context": message_relay_context,
                "message_relay_application": message_relay_application,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("PhoneNumberResponse", self._http.put(self._path(id), body=body))

    def search(self) -> AvailablePhoneNumbersResponse:
        return cast(
            "AvailablePhoneNumbersResponse",
            self._http.get(self._path("phone_numbers", "search")),
        )


class QueuesResource(
    CrudResource[
        "QueueListResponse", "QueueResponse", "CreateQueueRequest", "UpdateQueueRequest"
    ]
):
    """Typed CRUD resource for ``/queues`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/queues")

    def create(  # type: ignore[override]
        self,
        *,
        name: str | None = None,
        max_size: int | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> QueueResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "max_size": max_size}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("QueueResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        max_size: int | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> QueueResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "max_size": max_size}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("QueueResponse", self._http.put(self._path(id), body=body))

    def list_members(self, queue_id: str) -> QueueMemberListResponse:
        return cast(
            "QueueMemberListResponse",
            self._http.get(self._path("queues", queue_id, "members")),
        )

    def get_next_member(self, queue_id: str) -> QueueMemberResponse:
        return cast(
            "QueueMemberResponse",
            self._http.get(self._path("queues", queue_id, "members", "next")),
        )

    def get_member(self, queue_id: str, id: str) -> QueueMemberResponse:
        return cast(
            "QueueMemberResponse",
            self._http.get(self._path("queues", queue_id, "members", id)),
        )


class VerifiedCallersResource(
    CrudResource[
        "VerifiedCallerIDListResponse",
        "VerifiedCallerIDResponse",
        "CreateVerifiedCallerIDRequest",
        "UpdateVerifiedCallerIDRequest",
    ]
):
    """Typed CRUD resource for ``/verified_caller_ids`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/verified_caller_ids")

    def create(  # type: ignore[override]
        self,
        *,
        number: str,
        name: str | None = None,
        extension: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> VerifiedCallerIDResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"number": number, "name": name, "extension": extension}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast(
            "VerifiedCallerIDResponse", self._http.post(self._base_path, body=body)
        )

    def update(  # type: ignore[override]
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> VerifiedCallerIDResponse:
        body: dict[str, Any] = {
            k: v for k, v in {"name": name}.items() if v is not None
        }
        if extras:
            body.update(extras)
        return cast(
            "VerifiedCallerIDResponse", self._http.put(self._path(id), body=body)
        )

    def redial_verification(self, id: str) -> VerifiedCallerIDResponse:
        return cast(
            "VerifiedCallerIDResponse",
            self._http.post(self._path("verified_caller_ids", id, "verification")),
        )

    def submit_verification(
        self,
        id: str,
        *,
        verification_code: str,
        extras: Mapping[str, Any] | None = None,
    ) -> VerifiedCallerIDResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"verification_code": verification_code}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast(
            "VerifiedCallerIDResponse",
            self._http.put(
                self._path("verified_caller_ids", id, "verification"), body=body
            ),
        )
