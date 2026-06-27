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
        CreateNumberGroupRequest,
        CreateQueueRequest,
        CreateVerifiedCallerIDRequest,
        NumberGroupListResponse,
        NumberGroupResponse,
        PhoneNumberCallHandlerRequest,
        PhoneNumberListResponse,
        PhoneNumberMessageHandler,
        PhoneNumberResponse,
        PurchasePhoneNumberRequest,
        QueueListResponse,
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


class QueuesResource(
    CrudResource[
        "QueueListResponse", "QueueResponse", "CreateQueueRequest", "UpdateQueueRequest"
    ]
):
    """Typed CRUD resource for ``/queues`` (generated)."""

    _update_method = "PUT"

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
