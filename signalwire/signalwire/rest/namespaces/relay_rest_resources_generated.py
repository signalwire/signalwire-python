# AUTO-GENERATED from porting-sdk/rest-apis/relay-rest/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import BaseResource, CrudResource, _required_via_extras

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .relay_rest_types_generated import (
        AddressCountryCode,
        AddressListResponse,
        AddressResponse,
        AddressType,
        AssignedNumberListResponse,
        AvailablePhoneNumbersResponse,
        BrandListResponse,
        BrandResponse,
        CampaignListResponse,
        CampaignResponse,
        CompanyVertical,
        CreateCspBrandRequest,
        CreateManagedBrandRequest,
        CreateManagedCampaignRequest,
        CreateNumberGroupRequest,
        CreatePartnerCampaignRequest,
        CreateQueueRequest,
        CreateVerifiedCallerIDRequest,
        HttpMethod,
        LegalEntityType,
        MfaResponse,
        MfaVerifyResponse,
        NumberGroupListResponse,
        NumberGroupMembershipListResponse,
        NumberGroupMembershipResponse,
        NumberGroupResponse,
        OrderListResponse,
        OrderResponse,
        PhoneNumberCallHandlerRequest,
        PhoneNumberCnamResponse,
        PhoneNumberListResponse,
        PhoneNumberLookupResponse,
        PhoneNumberMessageHandler,
        PhoneNumberResponse,
        PurchasePhoneNumberRequest,
        QueueListResponse,
        QueueMemberListResponse,
        QueueMemberResponse,
        QueueResponse,
        Recording,
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


class Addresses(BaseResource):
    """Typed resource for ``/addresses`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/addresses")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> AddressListResponse:
        return cast(
            "AddressListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    @_required_via_extras(
        "label",
        "country",
        "first_name",
        "last_name",
        "street_number",
        "street_name",
        "city",
        "state",
        "postal_code",
    )
    def create(
        self,
        *,
        label: str,
        country: AddressCountryCode,
        first_name: str,
        last_name: str,
        street_number: str,
        street_name: str,
        city: str,
        state: str,
        postal_code: str,
        address_type: AddressType | None = None,
        address_number: str | None = None,
        emergency_enabled: bool | None = None,
        auto_correct_address: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
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
                "emergency_enabled": emergency_enabled,
                "auto_correct_address": auto_correct_address,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "AddressResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> AddressResponse:
        return cast(
            "AddressResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        *,
        label: str | None = None,
        country: AddressCountryCode | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        street_number: str | None = None,
        street_name: str | None = None,
        address_type: AddressType | None = None,
        address_number: str | None = None,
        city: str | None = None,
        state: str | None = None,
        postal_code: str | None = None,
        emergency_enabled: bool | None = None,
        auto_correct_address: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
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
                "emergency_enabled": emergency_enabled,
                "auto_correct_address": auto_correct_address,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "AddressResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )


class ImportedNumbers(BaseResource):
    """Typed resource for ``/imported_phone_numbers`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/imported_phone_numbers")

    @_required_via_extras("number", "number_type")
    def create(
        self,
        *,
        number: str,
        number_type: Literal["longcode", "tollfree"],
        capabilities: list[Literal["sms", "voice", "fax", "mms"]] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
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
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )


class Lookup(BaseResource):
    """Typed resource for ``/lookup`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/lookup")

    def phone_number(
        self,
        e164_number: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> PhoneNumberLookupResponse:
        return cast(
            "PhoneNumberLookupResponse",
            self._http.get(
                self._path("phone_number", e164_number),
                params=params or None,
                request_options=request_options,
            ),
        )


class Mfa(BaseResource):
    """Typed resource for ``/mfa`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/mfa")

    @_required_via_extras("to")
    def sms(
        self,
        *,
        to: str,
        from_: str | None = None,
        message: str | None = None,
        token_length: int | None = None,
        valid_for: int | None = None,
        max_attempts: int | None = None,
        allow_alphas: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> MfaResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "to": to,
                "from": from_,
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
        body.update(_reserved_kw)
        return cast(
            "MfaResponse",
            self._http.post(
                self._path("sms"), body=body, request_options=request_options
            ),
        )

    @_required_via_extras("to")
    def call(
        self,
        *,
        to: str,
        from_: str | None = None,
        message: str | None = None,
        token_length: int | None = None,
        valid_for: int | None = None,
        max_attempts: int | None = None,
        allow_alphas: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> MfaResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "to": to,
                "from": from_,
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
        body.update(_reserved_kw)
        return cast(
            "MfaResponse",
            self._http.post(
                self._path("call"), body=body, request_options=request_options
            ),
        )

    @_required_via_extras("token")
    def verify(
        self,
        mfa_request_id: str,
        *,
        token: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> MfaVerifyResponse:
        body: dict[str, Any] = {
            k: v for k, v in {"token": token}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "MfaVerifyResponse",
            self._http.post(
                self._path(mfa_request_id, "verify"),
                body=body,
                request_options=request_options,
            ),
        )


class NumberGroups(
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

    @_required_via_extras("name")
    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        sticky_sender: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> NumberGroupResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "sticky_sender": sticky_sender}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "NumberGroupResponse",
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
        sticky_sender: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> NumberGroupResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "sticky_sender": sticky_sender}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "NumberGroupResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_memberships(
        self,
        number_group_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> NumberGroupMembershipListResponse:
        return cast(
            "NumberGroupMembershipListResponse",
            self._http.get(
                self._path(number_group_id, "number_group_memberships"),
                params=params or None,
                request_options=request_options,
            ),
        )

    @_required_via_extras("phone_number_id")
    def add_membership(
        self,
        number_group_id: str,
        *,
        phone_number_id: uuid,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> NumberGroupMembershipResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"phone_number_id": phone_number_id}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "NumberGroupMembershipResponse",
            self._http.post(
                self._path(number_group_id, "number_group_memberships"),
                body=body,
                request_options=request_options,
            ),
        )

    def get_membership(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> NumberGroupMembershipResponse:
        return cast(
            "NumberGroupMembershipResponse",
            self._http.get(
                f"/api/relay/rest/number_group_memberships/{id}",
                params=params or None,
                request_options=request_options,
            ),
        )

    def delete_membership(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(
                f"/api/relay/rest/number_group_memberships/{id}",
                request_options=request_options,
            ),
        )


class PhoneNumbers(
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

    @_required_via_extras("number")
    def create(  # type: ignore[override]
        self,
        *,
        number: str,
        number_type: Literal["local", "tollfree"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"number": number, "number_type": number_type}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberResponse",
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
        call_handler: PhoneNumberCallHandlerRequest | None = None,
        call_receive_mode: Literal["voice", "fax"] | None = None,
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
        call_relay_script_url_method: str | None = None,
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
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
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
                "call_relay_script_url_method": call_relay_script_url_method,
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
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def search(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> AvailablePhoneNumbersResponse:
        return cast(
            "AvailablePhoneNumbersResponse",
            self._http.get(
                self._path("search"),
                params=params or None,
                request_options=request_options,
            ),
        )

    @_required_via_extras("e911_address_id")
    def assign_e911_address(
        self,
        id: str,
        *,
        e911_address_id: uuid,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"e911_address_id": e911_address_id}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberResponse",
            self._http.post(
                self._path(id, "e911_address"),
                body=body,
                request_options=request_options,
            ),
        )

    def remove_e911_address(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> PhoneNumberResponse:
        return cast(
            "PhoneNumberResponse",
            self._http.delete(
                self._path(id, "e911_address"), request_options=request_options
            ),
        )

    def get_cnam(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> PhoneNumberCnamResponse:
        return cast(
            "PhoneNumberCnamResponse",
            self._http.get(
                self._path(id, "cnam"),
                params=params or None,
                request_options=request_options,
            ),
        )

    @_required_via_extras("name")
    def request_cnam(
        self,
        id: str,
        *,
        name: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneNumberCnamResponse:
        body: dict[str, Any] = {
            k: v for k, v in {"name": name}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberCnamResponse",
            self._http.post(
                self._path(id, "cnam"), body=body, request_options=request_options
            ),
        )

    def clear_cnam(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id, "cnam"), request_options=request_options),
        )

    def set_swml_webhook(
        self,
        resource_id: str,
        url: str,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "relay_script"}
        body["call_relay_script_url"] = url
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_cxml_webhook(
        self,
        resource_id: str,
        url: str,
        fallback_url: str | None = None,
        status_callback_url: str | None = None,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "laml_webhooks"}
        body["call_request_url"] = url
        if fallback_url is not None:
            body["call_fallback_url"] = fallback_url
        if status_callback_url is not None:
            body["call_status_callback_url"] = status_callback_url
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_cxml_application(
        self,
        resource_id: str,
        application_id: str,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "laml_application"}
        body["call_laml_application_id"] = application_id
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_ai_agent(
        self,
        resource_id: str,
        agent_id: uuid,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "ai_agent"}
        body["call_ai_agent_id"] = agent_id
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_call_flow(
        self,
        resource_id: str,
        flow_id: uuid,
        version: Literal["working_copy", "current_deployed"] | None = None,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "call_flow"}
        body["call_flow_id"] = flow_id
        if version is not None:
            body["call_flow_version"] = version
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_relay_application(
        self,
        resource_id: str,
        name: str,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "relay_application"}
        body["call_relay_application"] = name
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_relay_topic(
        self,
        resource_id: str,
        topic: str,
        status_callback_url: str | None = None,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        body: dict[str, Any] = {"call_handler": "relay_topic"}
        body["call_relay_topic"] = topic
        if status_callback_url is not None:
            body["call_relay_topic_status_callback_url"] = status_callback_url
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)


class Queues(
    CrudResource[
        "QueueListResponse", "QueueResponse", "CreateQueueRequest", "UpdateQueueRequest"
    ]
):
    """Typed resource for ``/queues`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/queues")

    @_required_via_extras("name")
    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        max_size: int | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> QueueResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "max_size": max_size}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "QueueResponse",
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
        max_size: int | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> QueueResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "max_size": max_size}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "QueueResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_members(
        self,
        queue_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> QueueMemberListResponse:
        return cast(
            "QueueMemberListResponse",
            self._http.get(
                self._path(queue_id, "members"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def get_next_member(
        self,
        queue_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> QueueMemberResponse:
        return cast(
            "QueueMemberResponse",
            self._http.get(
                self._path(queue_id, "members", "next"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def get_member(
        self,
        queue_id: str,
        id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> QueueMemberResponse:
        return cast(
            "QueueMemberResponse",
            self._http.get(
                self._path(queue_id, "members", id),
                params=params or None,
                request_options=request_options,
            ),
        )


class Recordings(BaseResource):
    """Typed resource for ``/recordings`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/recordings")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> RecordingListResponse:
        return cast(
            "RecordingListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> Recording:
        return cast(
            "Recording",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )

    def download(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> str:
        """Return the URL this endpoint redirects to (the ``Location`` of its
        redirect), without following it or downloading anything; fetch it with any
        HTTP client. Raises :class:`SignalWireRestError` for an error status.
        """
        return self._http.get_redirect_location(
            self._path(f"{id}.mp3"),
            params=params or None,
            request_options=request_options,
        )


class RegistryBrands(BaseResource):
    """Typed resource for ``/registry/beta/brands`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/registry/beta/brands")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> BrandListResponse:
        return cast(
            "BrandListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def create(
        self,
        body: CreateManagedBrandRequest | CreateCspBrandRequest,
        *,
        request_options: RequestOptions | None = None,
    ) -> BrandResponse:
        return cast(
            "BrandResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> BrandResponse:
        return cast(
            "BrandResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        *,
        name: str | None = None,
        company_name: str | None = None,
        contact_email: str | None = None,
        contact_phone: str | None = None,
        ein_issuing_country: str | None = None,
        legal_entity_type: LegalEntityType | None = None,
        ein: str | None = None,
        company_vertical: CompanyVertical | None = None,
        company_website: str | None = None,
        company_address: str | None = None,
        csp_brand_reference: str | None = None,
        status_callback_url: str | None = None,
        signalwire_contact_emails: builtins.list[str] | str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> BrandResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "company_name": company_name,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "ein_issuing_country": ein_issuing_country,
                "legal_entity_type": legal_entity_type,
                "ein": ein,
                "company_vertical": company_vertical,
                "company_website": company_website,
                "company_address": company_address,
                "csp_brand_reference": csp_brand_reference,
                "status_callback_url": status_callback_url,
                "signalwire_contact_emails": signalwire_contact_emails,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "BrandResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_campaigns(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CampaignListResponse:
        return cast(
            "CampaignListResponse",
            self._http.get(
                self._path(id, "campaigns"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def create_campaign(
        self,
        id: str,
        body: CreateManagedCampaignRequest | CreatePartnerCampaignRequest,
        *,
        request_options: RequestOptions | None = None,
    ) -> CampaignResponse:
        return cast(
            "CampaignResponse",
            self._http.post(
                self._path(id, "campaigns"), body=body, request_options=request_options
            ),
        )


class RegistryCampaigns(BaseResource):
    """Typed resource for ``/registry/beta/campaigns`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/registry/beta/campaigns")

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CampaignResponse:
        return cast(
            "CampaignResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        *,
        name: str | None = None,
        status_callback_url: str | None = None,
        signalwire_contact_emails: list[str] | str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CampaignResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "status_callback_url": status_callback_url,
                "signalwire_contact_emails": signalwire_contact_emails,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CampaignResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_numbers(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> AssignedNumberListResponse:
        return cast(
            "AssignedNumberListResponse",
            self._http.get(
                self._path(id, "numbers"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def list_orders(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> OrderListResponse:
        return cast(
            "OrderListResponse",
            self._http.get(
                self._path(id, "orders"),
                params=params or None,
                request_options=request_options,
            ),
        )

    @_required_via_extras("phone_numbers")
    def create_order(
        self,
        id: str,
        *,
        phone_numbers: list[str],
        status_callback_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> OrderResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "phone_numbers": phone_numbers,
                "status_callback_url": status_callback_url,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "OrderResponse",
            self._http.post(
                self._path(id, "orders"), body=body, request_options=request_options
            ),
        )


class RegistryNumbers(BaseResource):
    """Typed resource for ``/registry/beta/numbers`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/registry/beta/numbers")

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )


class RegistryOrders(BaseResource):
    """Typed resource for ``/registry/beta/orders`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/registry/beta/orders")

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> OrderResponse:
        return cast(
            "OrderResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )


class ShortCodes(BaseResource):
    """Typed resource for ``/short_codes`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/short_codes")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ShortCodeListResponse:
        return cast(
            "ShortCodeListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ShortCodeResponse:
        return cast(
            "ShortCodeResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        *,
        name: str | None = None,
        message_handler: ShortCodeMessageHandler | None = None,
        message_request_url: str | None = None,
        message_request_method: HttpMethod | None = None,
        message_fallback_url: str | None = None,
        message_fallback_method: HttpMethod | None = None,
        message_laml_application_id: uuid | None = None,
        message_relay_context: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
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
        body.update(_reserved_kw)
        return cast(
            "ShortCodeResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class SipProfile(BaseResource):
    """Typed resource for ``/sip_profile`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/sip_profile")

    def get(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> SipProfileResponse:
        return cast(
            "SipProfileResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        *,
        domain_identifier: str | None = None,
        default_codecs: list[str] | None = None,
        default_ciphers: list[str] | None = None,
        default_encryption: Literal["required", "optional"] | None = None,
        default_send_as: str | None = None,
        default_outbound_policy: Literal["passthrough", "block-pstn"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipProfileResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "domain_identifier": domain_identifier,
                "default_codecs": default_codecs,
                "default_ciphers": default_ciphers,
                "default_encryption": default_encryption,
                "default_send_as": default_send_as,
                "default_outbound_policy": default_outbound_policy,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipProfileResponse",
            self._http.put(self._base_path, body=body, request_options=request_options),
        )


class VerifiedCallers(
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

    @_required_via_extras("number")
    def create(  # type: ignore[override]
        self,
        *,
        number: str,
        name: str | None = None,
        extension: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> VerifiedCallerIDResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"number": number, "name": name, "extension": extension}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "VerifiedCallerIDResponse",
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
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> VerifiedCallerIDResponse:
        body: dict[str, Any] = {
            k: v for k, v in {"name": name}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "VerifiedCallerIDResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def redial_verification(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> VerifiedCallerIDResponse:
        return cast(
            "VerifiedCallerIDResponse",
            self._http.post(
                self._path(id, "verification"), request_options=request_options
            ),
        )

    @_required_via_extras("verification_code")
    def submit_verification(
        self,
        id: str,
        *,
        verification_code: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> VerifiedCallerIDResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"verification_code": verification_code}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "VerifiedCallerIDResponse",
            self._http.put(
                self._path(id, "verification"),
                body=body,
                request_options=request_options,
            ),
        )
