# AUTO-GENERATED from porting-sdk/rest-apis/relay-rest/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed create/update
# (explicit spec fields + an ``extras`` door), bound to the resource's spec
# types. Runtime body is a plain dict (open-tail, never validated).
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import BaseResource, CrudResource

if TYPE_CHECKING:
    from .relay_rest_types_generated import (
        AddressListResponse,
        AddressResponse,
        AddressType,
        AvailablePhoneNumbersResponse,
        CreateNumberGroupRequest,
        CreateQueueRequest,
        CreateVerifiedCallerIDRequest,
        HttpMethod,
        MfaResponse,
        MfaVerifyResponse,
        NumberGroupListResponse,
        NumberGroupMembershipListResponse,
        NumberGroupMembershipResponse,
        NumberGroupResponse,
        PhoneNumberCallHandlerRequest,
        PhoneNumberListResponse,
        PhoneNumberLookupResponse,
        PhoneNumberMessageHandler,
        PhoneNumberResponse,
        PurchasePhoneNumberRequest,
        QueueListResponse,
        QueueMemberListResponse,
        QueueMemberResponse,
        QueueResponse,
        RecordingListResponse,
        ShortCodeListResponse,
        ShortCodeMessageHandler,
        ShortCodeResponse,
        SipProfileResponse,
        UpdateNumberGroupRequest,
        UpdatePhoneNumberRequest,
        UpdateQueueRequest,
        UpdateVerifiedCallerIDRequest,
        VerifiedCallerIDListResponse,
        VerifiedCallerIDResponse,
        uuid,
    )


class AddressesResource(BaseResource):
    """Typed resource for ``/addresses`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/addresses")

    def list(self, **params: Any) -> AddressListResponse:
        return cast(
            "AddressListResponse",
            self._http.get(self._base_path, params=params or None),
        )

    def create(
        self,
        *,
        label: str,
        country: str,
        first_name: str,
        last_name: str,
        street_number: str,
        street_name: str,
        city: str,
        state: str,
        postal_code: str,
        address_type: AddressType | None = None,
        address_number: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> AddressResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "label": label,
                "country": country,
                "first_name": first_name,
                "last_name": last_name,
                "street_number": street_number,
                "street_name": street_name,
                "address_type": address_type,
                "address_number": address_number,
                "city": city,
                "state": state,
                "postal_code": postal_code,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("AddressResponse", self._http.post(self._base_path, body=body))

    def get(self, id: str, **params: Any) -> AddressResponse:
        return cast(
            "AddressResponse", self._http.get(self._path(id), params=params or None)
        )

    def delete(self, id: str) -> dict[str, Any]:
        return cast("dict[str, Any]", self._http.delete(self._path(id)))


class ImportedNumbersResource(BaseResource):
    """Typed resource for ``/imported_phone_numbers`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/imported_phone_numbers")

    def create(
        self,
        *,
        number: str,
        number_type: Literal["longcode", "tollfree"],
        capabilities: list[Literal["sms", "voice", "fax", "mms"]] | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "number": number,
                "number_type": number_type,
                "capabilities": capabilities,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("PhoneNumberResponse", self._http.post(self._base_path, body=body))


class LookupResource(BaseResource):
    """Typed resource for ``/lookup`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/lookup")

    def phone_number(
        self, e164_number: str, **params: Any
    ) -> PhoneNumberLookupResponse:
        return cast(
            "PhoneNumberLookupResponse",
            self._http.get(
                self._path("phone_number", e164_number), params=params or None
            ),
        )


class MfaResource(BaseResource):
    """Typed resource for ``/mfa`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/mfa")

    def sms(
        self,
        *,
        to: str,
        message: str | None = None,
        token_length: int | None = None,
        valid_for: int | None = None,
        max_attempts: int | None = None,
        allow_alphas: bool | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> MfaResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "to": to,
                "message": message,
                "token_length": token_length,
                "valid_for": valid_for,
                "max_attempts": max_attempts,
                "allow_alphas": allow_alphas,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("MfaResponse", self._http.post(self._path("sms"), body=body))

    def call(
        self,
        *,
        to: str,
        message: str | None = None,
        token_length: int | None = None,
        valid_for: int | None = None,
        max_attempts: int | None = None,
        allow_alphas: bool | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> MfaResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "to": to,
                "message": message,
                "token_length": token_length,
                "valid_for": valid_for,
                "max_attempts": max_attempts,
                "allow_alphas": allow_alphas,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("MfaResponse", self._http.post(self._path("call"), body=body))

    def verify(
        self,
        mfa_request_id: str,
        *,
        token: str,
        extras: Mapping[str, Any] | None = None,
    ) -> MfaVerifyResponse:
        body: dict[str, Any] = {
            k: v for k, v in {"token": token}.items() if v is not None
        }
        if extras:
            body.update(extras)
        return cast(
            "MfaVerifyResponse",
            self._http.post(self._path(mfa_request_id, "verify"), body=body),
        )


class NumberGroupsResource(
    CrudResource[
        "NumberGroupListResponse",
        "NumberGroupResponse",
        "CreateNumberGroupRequest",
        "UpdateNumberGroupRequest",
    ]
):
    """Typed resource for ``/number_groups`` (generated)."""

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
        self, number_group_id: str, **params: Any
    ) -> NumberGroupMembershipListResponse:
        return cast(
            "NumberGroupMembershipListResponse",
            self._http.get(
                self._path(number_group_id, "number_group_memberships"),
                params=params or None,
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
                self._path(number_group_id, "number_group_memberships"), body=body
            ),
        )

    def get_membership(self, id: str, **params: Any) -> NumberGroupMembershipResponse:
        return cast(
            "NumberGroupMembershipResponse",
            self._http.get(
                f"/api/relay/rest/number_group_memberships/{id}", params=params or None
            ),
        )

    def delete_membership(self, id: str) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(f"/api/relay/rest/number_group_memberships/{id}"),
        )


class PhoneNumbersResource(
    CrudResource[
        "PhoneNumberListResponse",
        "PhoneNumberResponse",
        "PurchasePhoneNumberRequest",
        "UpdatePhoneNumberRequest",
    ]
):
    """Typed resource for ``/phone_numbers`` (generated)."""

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

    def search(self, **params: Any) -> AvailablePhoneNumbersResponse:
        return cast(
            "AvailablePhoneNumbersResponse",
            self._http.get(self._path("search"), params=params or None),
        )

    def set_swml_webhook(
        self, resource_id: str, url: str, **extra: Any
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "relay_script"}
        body["call_relay_script_url"] = url
        body.update(extra)
        return cast("PhoneNumberResponse", self.update(resource_id, **body))

    def set_cxml_webhook(
        self,
        resource_id: str,
        url: str,
        fallback_url: str | None = None,
        status_callback_url: str | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "laml_webhooks"}
        body["call_request_url"] = url
        if fallback_url is not None:
            body["call_fallback_url"] = fallback_url
        if status_callback_url is not None:
            body["call_status_callback_url"] = status_callback_url
        body.update(extra)
        return cast("PhoneNumberResponse", self.update(resource_id, **body))

    def set_cxml_application(
        self, resource_id: str, application_id: str, **extra: Any
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "laml_application"}
        body["call_laml_application_id"] = application_id
        body.update(extra)
        return cast("PhoneNumberResponse", self.update(resource_id, **body))

    def set_ai_agent(
        self, resource_id: str, agent_id: uuid, **extra: Any
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "ai_agent"}
        body["call_ai_agent_id"] = agent_id
        body.update(extra)
        return cast("PhoneNumberResponse", self.update(resource_id, **body))

    def set_call_flow(
        self,
        resource_id: str,
        flow_id: uuid,
        version: Literal["working_copy", "current_deployed"] | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "call_flow"}
        body["call_flow_id"] = flow_id
        if version is not None:
            body["call_flow_version"] = version
        body.update(extra)
        return cast("PhoneNumberResponse", self.update(resource_id, **body))

    def set_relay_application(
        self, resource_id: str, name: str, **extra: Any
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "relay_application"}
        body["call_relay_application"] = name
        body.update(extra)
        return cast("PhoneNumberResponse", self.update(resource_id, **body))

    def set_relay_topic(
        self,
        resource_id: str,
        topic: str,
        status_callback_url: str | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "relay_topic"}
        body["call_relay_topic"] = topic
        if status_callback_url is not None:
            body["call_relay_topic_status_callback_url"] = status_callback_url
        body.update(extra)
        return cast("PhoneNumberResponse", self.update(resource_id, **body))


class QueuesResource(
    CrudResource[
        "QueueListResponse", "QueueResponse", "CreateQueueRequest", "UpdateQueueRequest"
    ]
):
    """Typed resource for ``/queues`` (generated)."""

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

    def list_members(self, queue_id: str, **params: Any) -> QueueMemberListResponse:
        return cast(
            "QueueMemberListResponse",
            self._http.get(self._path(queue_id, "members"), params=params or None),
        )

    def get_next_member(self, queue_id: str, **params: Any) -> QueueMemberResponse:
        return cast(
            "QueueMemberResponse",
            self._http.get(
                self._path(queue_id, "members", "next"), params=params or None
            ),
        )

    def get_member(self, queue_id: str, id: str, **params: Any) -> QueueMemberResponse:
        return cast(
            "QueueMemberResponse",
            self._http.get(self._path(queue_id, "members", id), params=params or None),
        )


class RecordingsResource(BaseResource):
    """Typed resource for ``/recordings`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/recordings")

    def list(self, **params: Any) -> RecordingListResponse:
        return cast(
            "RecordingListResponse",
            self._http.get(self._base_path, params=params or None),
        )

    def get(self, id: str, **params: Any) -> dict[str, Any]:
        return cast(
            "dict[str, Any]", self._http.get(self._path(id), params=params or None)
        )

    def delete(self, id: str) -> dict[str, Any]:
        return cast("dict[str, Any]", self._http.delete(self._path(id)))


class ShortCodesResource(BaseResource):
    """Typed resource for ``/short_codes`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/short_codes")

    def list(self, **params: Any) -> ShortCodeListResponse:
        return cast(
            "ShortCodeListResponse",
            self._http.get(self._base_path, params=params or None),
        )

    def get(self, id: str, **params: Any) -> ShortCodeResponse:
        return cast(
            "ShortCodeResponse", self._http.get(self._path(id), params=params or None)
        )

    def update(
        self,
        id: str,
        *,
        name: str,
        message_handler: ShortCodeMessageHandler,
        message_request_url: str | None = None,
        message_request_method: HttpMethod | None = None,
        message_fallback_url: str | None = None,
        message_fallback_method: HttpMethod | None = None,
        message_laml_application_id: uuid | None = None,
        message_relay_context: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> ShortCodeResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "message_handler": message_handler,
                "message_request_url": message_request_url,
                "message_request_method": message_request_method,
                "message_fallback_url": message_fallback_url,
                "message_fallback_method": message_fallback_method,
                "message_laml_application_id": message_laml_application_id,
                "message_relay_context": message_relay_context,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("ShortCodeResponse", self._http.put(self._path(id), body=body))


class SipProfileResource(BaseResource):
    """Typed resource for ``/sip_profile`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/sip_profile")

    def get(self, **params: Any) -> SipProfileResponse:
        return cast(
            "SipProfileResponse", self._http.get(self._base_path, params=params or None)
        )

    def update(
        self,
        *,
        domain_identifier: str | None = None,
        default_codecs: list[str] | None = None,
        default_ciphers: list[str] | None = None,
        default_encryption: Literal["required", "optional"] | None = None,
        default_send_as: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> SipProfileResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "domain_identifier": domain_identifier,
                "default_codecs": default_codecs,
                "default_ciphers": default_ciphers,
                "default_encryption": default_encryption,
                "default_send_as": default_send_as,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("SipProfileResponse", self._http.put(self._base_path, body=body))


class VerifiedCallersResource(
    CrudResource[
        "VerifiedCallerIDListResponse",
        "VerifiedCallerIDResponse",
        "CreateVerifiedCallerIDRequest",
        "UpdateVerifiedCallerIDRequest",
    ]
):
    """Typed resource for ``/verified_caller_ids`` (generated)."""

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
            "VerifiedCallerIDResponse", self._http.post(self._path(id, "verification"))
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
            self._http.put(self._path(id, "verification"), body=body),
        )
