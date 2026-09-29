# AUTO-GENERATED from porting-sdk/rest-apis/fabric/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import BaseResource, CrudResource, FabricResource, ReadResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .fabric_types_generated import (
        AIAgentCreateRequest,
        AIAgentListResponse,
        AIAgentResponse,
        AIAgentUpdateRequest,
        AIParams,
        AIPostPrompt,
        AIPostPromptUpdate,
        AIPrompt,
        AIPromptUpdate,
        AliasAddress,
        AliasAddressCreateRequest,
        AliasAddressListResponse,
        AliasAddressUpdateRequest,
        CXMLScriptCreateRequest,
        CXMLScriptListResponse,
        CXMLScriptResponse,
        CXMLScriptUpdateRequest,
        CXMLWebhookCreateRequest,
        CXMLWebhookListResponse,
        CXMLWebhookResponse,
        CXMLWebhookUpdateRequest,
        CallFlowAddressListResponse,
        CallFlowCreateRequest,
        CallFlowListResponse,
        CallFlowResponse,
        CallFlowUpdateRequest,
        CallFlowVersionDeployRequest,
        CallFlowVersionDeployResponse,
        CallFlowVersionListResponse,
        CallHandlerType,
        Ciphers,
        Codecs,
        ConferenceRoomAddressListResponse,
        ConferenceRoomCreateRequest,
        ConferenceRoomListResponse,
        ConferenceRoomResponse,
        ConferenceRoomUpdateRequest,
        CxmlApplicationAddressListResponse,
        CxmlApplicationListResponse,
        CxmlApplicationResponse,
        DomainApplicationResponse,
        EmbedsTokensResponse,
        Encryption,
        FabricAddress,
        FabricAddressesResponse,
        FreeswitchConnectorCreateRequest,
        FreeswitchConnectorListResponse,
        FreeswitchConnectorResponse,
        FreeswitchConnectorUpdateRequest,
        Hint,
        Languages,
        Layout,
        PhoneNumberAddress,
        PhoneNumberAddressCreateRequest,
        PhoneNumberAddressListResponse,
        PhoneNumberAddressUpdateRequest,
        PhoneRouteResponse,
        Pronounce,
        RelayApplicationCreateRequest,
        RelayApplicationListResponse,
        RelayApplicationResponse,
        RelayApplicationUpdateRequest,
        ResourceAddressListResponse,
        ResourceListResponse,
        ResourceResponse,
        SWAIG,
        SWAIGUpdate,
        SWMLWebhookCreateRequest,
        SWMLWebhookListResponse,
        SWMLWebhookResponse,
        SWMLWebhookUpdateRequest,
        SipAddress,
        SipAddressCreateRequest,
        SipAddressListResponse,
        SipAddressUpdateRequest,
        SipEndpointCreateRequest,
        SipEndpointListResponse,
        SipEndpointResponse,
        SipEndpointUpdateRequest,
        SipGatewayListResponse,
        SipGatewayRequest,
        SipGatewayRequestUpdate,
        SipGatewayResponse,
        SubscriberGuestTokenCreateResponse,
        SubscriberInviteTokenCreateResponse,
        SubscriberListResponse,
        SubscriberRefreshTokenResponse,
        SubscriberRequest,
        SubscriberResponse,
        SubscriberSIPEndpoint,
        SubscriberSipEndpointListResponse,
        SubscriberTokenResponse,
        SubscriberUpdateRequest,
        SwmlScriptCreateRequest,
        SwmlScriptListResponse,
        SwmlScriptResponse,
        SwmlScriptUpdateRequest,
        UsedForType,
        WhatsappNumberAddressResponse,
        jwt,
        uuid,
    )


class AliasAddresses(
    CrudResource[
        "AliasAddressListResponse",
        "AliasAddress",
        "AliasAddressCreateRequest",
        "AliasAddressUpdateRequest",
    ]
):
    """Typed resource for ``/addresses/alias`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/addresses/alias")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        resource_id: uuid,
        display_name: str | None = None,
        channels: list[Literal["audio", "messaging", "video"]] | None = None,
        codecs: list[
            Literal[
                "OPUS",
                "OPUS@48000H@20I",
                "OPUS@24000H@20I",
                "OPUS@16000H@20I",
                "OPUS@8000H@20I",
                "G722",
                "PCMU",
                "PCMA",
                "G729",
                "VP8",
                "H264",
            ]
        ]
        | None = None,
        context: Literal["private", "public"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> AliasAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "display_name": display_name,
                "resource_id": resource_id,
                "channels": channels,
                "codecs": codecs,
                "context": context,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "AliasAddress",
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
        display_name: str | None = None,
        channels: list[Literal["audio", "messaging", "video"]] | None = None,
        codecs: list[
            Literal[
                "OPUS",
                "OPUS@48000H@20I",
                "OPUS@24000H@20I",
                "OPUS@16000H@20I",
                "OPUS@8000H@20I",
                "G722",
                "PCMU",
                "PCMA",
                "G729",
                "VP8",
                "H264",
            ]
        ]
        | None = None,
        context: Literal["private", "public"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> AliasAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "display_name": display_name,
                "channels": channels,
                "codecs": codecs,
                "context": context,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "AliasAddress",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class SipAddresses(
    CrudResource[
        "SipAddressListResponse",
        "SipAddress",
        "SipAddressCreateRequest",
        "SipAddressUpdateRequest",
    ]
):
    """Typed resource for ``/addresses/sip`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/addresses/sip")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        calling_handler_resource_id: uuid,
        user: str | None = None,
        context_id: uuid | None = None,
        ip_auth_enabled: bool | None = None,
        ip_auth: list[str] | None = None,
        codecs: list[
            Literal[
                "OPUS",
                "OPUS@48000H@20I",
                "OPUS@24000H@20I",
                "OPUS@16000H@20I",
                "OPUS@8000H@20I",
                "G722",
                "PCMU",
                "PCMA",
                "G729",
                "VP8",
                "H264",
            ]
        ]
        | None = None,
        ciphers: list[
            Literal[
                "AEAD_AES_256_GCM_8",
                "AES_256_CM_HMAC_SHA1_80",
                "AES_CM_128_HMAC_SHA1_80",
                "AES_256_CM_HMAC_SHA1_32",
                "AES_CM_128_HMAC_SHA1_32",
            ]
        ]
        | None = None,
        encryption: Literal["required", "optional", "forbidden"] | None = None,
        password: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "user": user,
                "context_id": context_id,
                "calling_handler_resource_id": calling_handler_resource_id,
                "ip_auth_enabled": ip_auth_enabled,
                "ip_auth": ip_auth,
                "codecs": codecs,
                "ciphers": ciphers,
                "encryption": encryption,
                "password": password,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipAddress",
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
        user: str | None = None,
        context_id: uuid | None = None,
        ip_auth_enabled: bool | None = None,
        ip_auth: list[str] | None = None,
        codecs: list[
            Literal[
                "OPUS",
                "OPUS@48000H@20I",
                "OPUS@24000H@20I",
                "OPUS@16000H@20I",
                "OPUS@8000H@20I",
                "G722",
                "PCMU",
                "PCMA",
                "G729",
                "VP8",
                "H264",
            ]
        ]
        | None = None,
        ciphers: list[
            Literal[
                "AEAD_AES_256_GCM_8",
                "AES_256_CM_HMAC_SHA1_80",
                "AES_CM_128_HMAC_SHA1_80",
                "AES_256_CM_HMAC_SHA1_32",
                "AES_CM_128_HMAC_SHA1_32",
            ]
        ]
        | None = None,
        encryption: Literal["required", "optional", "forbidden"] | None = None,
        password: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "user": user,
                "context_id": context_id,
                "ip_auth_enabled": ip_auth_enabled,
                "ip_auth": ip_auth,
                "codecs": codecs,
                "ciphers": ciphers,
                "encryption": encryption,
                "password": password,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipAddress",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class PhoneNumberAddresses(
    CrudResource[
        "PhoneNumberAddressListResponse",
        "PhoneNumberAddress",
        "PhoneNumberAddressCreateRequest",
        "PhoneNumberAddressUpdateRequest",
    ]
):
    """Typed resource for ``/addresses/phone`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/addresses/phone")

    def create(  # type: ignore[override]
        self,
        *,
        resource_id: uuid,
        handler_type: Literal["calling", "messaging"],
        phone_number_id: uuid | None = None,
        number: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneNumberAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "phone_number_id": phone_number_id,
                "number": number,
                "resource_id": resource_id,
                "handler_type": handler_type,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberAddress",
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
        resource_id: uuid | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneNumberAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "resource_id": resource_id}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberAddress",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class FabricAddresses(ReadResource["FabricAddressesResponse", "FabricAddress"]):
    """Typed resource for ``/addresses`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/addresses")

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )


class GenericResources(BaseResource):
    """Typed resource for ``/resources`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ResourceListResponse:
        return cast(
            "ResourceListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ResourceResponse:
        return cast(
            "ResourceResponse",
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

    def list_addresses(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ResourceAddressListResponse:
        return cast(
            "ResourceAddressListResponse",
            self._http.get(
                self._path(id, "addresses"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def assign_phone_route(
        self,
        id: str,
        *,
        phone_route_id: uuid,
        handler: UsedForType,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneRouteResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"phone_route_id": phone_route_id, "handler": handler}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneRouteResponse",
            self._http.post(
                self._path(id, "phone_routes"),
                body=body,
                request_options=request_options,
            ),
        )

    def assign_domain_application(
        self,
        id: str,
        *,
        domain_application_id: uuid,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> DomainApplicationResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"domain_application_id": domain_application_id}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "DomainApplicationResponse",
            self._http.post(
                self._path(id, "domain_applications"),
                body=body,
                request_options=request_options,
            ),
        )

    def assign_sip_endpoint(
        self,
        id: str,
        *,
        sip_endpoint_id: uuid,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> ResourceResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"sip_endpoint_id": sip_endpoint_id}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "ResourceResponse",
            self._http.post(
                self._path(id, "sip_endpoints"),
                body=body,
                request_options=request_options,
            ),
        )

    def assign_whatsapp_number(
        self,
        id: str,
        *,
        whatsapp_number_id: uuid,
        handler: UsedForType,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> WhatsappNumberAddressResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "whatsapp_number_id": whatsapp_number_id,
                "handler": handler,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "WhatsappNumberAddressResponse",
            self._http.post(
                self._path(id, "whatsapp_numbers"),
                body=body,
                request_options=request_options,
            ),
        )


class AiAgents(
    FabricResource[
        "AIAgentListResponse",
        "AIAgentResponse",
        "AIAgentCreateRequest",
        "AIAgentUpdateRequest",
    ]
):
    """Typed resource for ``/resources/ai_agents`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/ai_agents")

    def create(  # type: ignore[override]
        self,
        *,
        prompt: AIPrompt,
        name: str,
        global_data: dict[str, Any] | None = None,
        hints: list[str | Hint] | None = None,
        languages: list[Languages] | None = None,
        params: AIParams | None = None,
        post_prompt: AIPostPrompt | None = None,
        post_prompt_url: str | None = None,
        pronounce: list[Pronounce] | None = None,
        SWAIG: SWAIG | None = None,
        agent_id: uuid | None = None,
        post_prompt_auth_user: str | None = None,
        post_prompt_auth_password: str | None = None,
        multilingual: dict[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> AIAgentResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "global_data": global_data,
                "hints": hints,
                "languages": languages,
                "params": params,
                "post_prompt": post_prompt,
                "post_prompt_url": post_prompt_url,
                "pronounce": pronounce,
                "prompt": prompt,
                "SWAIG": SWAIG,
                "agent_id": agent_id,
                "name": name,
                "post_prompt_auth_user": post_prompt_auth_user,
                "post_prompt_auth_password": post_prompt_auth_password,
                "multilingual": multilingual,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "AIAgentResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        global_data: dict[str, Any] | None = None,
        hints: list[str | Hint] | None = None,
        languages: list[Languages] | None = None,
        params: AIParams | None = None,
        post_prompt: AIPostPromptUpdate | None = None,
        post_prompt_url: str | None = None,
        pronounce: list[Pronounce] | None = None,
        prompt: AIPromptUpdate | None = None,
        SWAIG: SWAIGUpdate | None = None,
        agent_id: uuid | None = None,
        name: str | None = None,
        post_prompt_auth_user: str | None = None,
        post_prompt_auth_password: str | None = None,
        multilingual: dict[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> AIAgentResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "global_data": global_data,
                "hints": hints,
                "languages": languages,
                "params": params,
                "post_prompt": post_prompt,
                "post_prompt_url": post_prompt_url,
                "pronounce": pronounce,
                "prompt": prompt,
                "SWAIG": SWAIG,
                "agent_id": agent_id,
                "name": name,
                "post_prompt_auth_user": post_prompt_auth_user,
                "post_prompt_auth_password": post_prompt_auth_password,
                "multilingual": multilingual,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "AIAgentResponse",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class CallFlows(
    FabricResource[
        "CallFlowListResponse",
        "CallFlowResponse",
        "CallFlowCreateRequest",
        "CallFlowUpdateRequest",
    ]
):
    """Typed resource for ``/resources/call_flows`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/call_flows")

    def create(  # type: ignore[override]
        self,
        *,
        title: str,
        flow_data: dict[str, Any] | str | None = None,
        relayml: dict[str, Any] | str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CallFlowResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "title": title,
                "flow_data": flow_data,
                "relayml": relayml,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CallFlowResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        title: str | None = None,
        document_version: int | None = None,
        flow_data: dict[str, Any] | str | None = None,
        relayml: dict[str, Any] | str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CallFlowResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "title": title,
                "document_version": document_version,
                "flow_data": flow_data,
                "relayml": relayml,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CallFlowResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_addresses(  # type: ignore[override]
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CallFlowAddressListResponse:
        return cast(
            "CallFlowAddressListResponse",
            self._http.get(
                f"/api/fabric/resources/call_flow/{id}/addresses",
                params=params or None,
                request_options=request_options,
            ),
        )

    def list_versions(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CallFlowVersionListResponse:
        return cast(
            "CallFlowVersionListResponse",
            self._http.get(
                f"/api/fabric/resources/call_flow/{id}/versions",
                params=params or None,
                request_options=request_options,
            ),
        )

    def deploy_version(
        self,
        id: str,
        body: CallFlowVersionDeployRequest,
        *,
        request_options: RequestOptions | None = None,
    ) -> CallFlowVersionDeployResponse:
        return cast(
            "CallFlowVersionDeployResponse",
            self._http.post(
                f"/api/fabric/resources/call_flow/{id}/versions",
                body=body,
                request_options=request_options,
            ),
        )


class ConferenceRooms(
    FabricResource[
        "ConferenceRoomListResponse",
        "ConferenceRoomResponse",
        "ConferenceRoomCreateRequest",
        "ConferenceRoomUpdateRequest",
    ]
):
    """Typed resource for ``/resources/conference_rooms`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/conference_rooms")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        enable_room_previews: bool,
        display_name: str | None = None,
        description: str | None = None,
        join_from: str | None = None,
        join_until: str | None = None,
        max_members: int | None = None,
        quality: Literal["1080p", "720p"] | None = None,
        remove_at: str | None = None,
        remove_after_seconds_elapsed: int | None = None,
        layout: Layout | None = None,
        record_on_start: bool | None = None,
        meta: dict[str, Any] | None = None,
        sync_audio_video: bool | None = None,
        tone_on_entry_and_exit: bool | None = None,
        room_join_video_off: bool | None = None,
        user_join_video_off: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> ConferenceRoomResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "display_name": display_name,
                "description": description,
                "join_from": join_from,
                "join_until": join_until,
                "max_members": max_members,
                "quality": quality,
                "remove_at": remove_at,
                "remove_after_seconds_elapsed": remove_after_seconds_elapsed,
                "layout": layout,
                "record_on_start": record_on_start,
                "enable_room_previews": enable_room_previews,
                "meta": meta,
                "sync_audio_video": sync_audio_video,
                "tone_on_entry_and_exit": tone_on_entry_and_exit,
                "room_join_video_off": room_join_video_off,
                "user_join_video_off": user_join_video_off,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "ConferenceRoomResponse",
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
        display_name: str | None = None,
        description: str | None = None,
        join_from: str | None = None,
        join_until: str | None = None,
        max_members: int | None = None,
        quality: Literal["1080p", "720p"] | None = None,
        remove_at: str | None = None,
        remove_after_seconds_elapsed: int | None = None,
        layout: Layout | None = None,
        record_on_start: bool | None = None,
        enable_room_previews: bool | None = None,
        meta: dict[str, Any] | None = None,
        sync_audio_video: bool | None = None,
        tone_on_entry_and_exit: bool | None = None,
        room_join_video_off: bool | None = None,
        user_join_video_off: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> ConferenceRoomResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "display_name": display_name,
                "description": description,
                "join_from": join_from,
                "join_until": join_until,
                "max_members": max_members,
                "quality": quality,
                "remove_at": remove_at,
                "remove_after_seconds_elapsed": remove_after_seconds_elapsed,
                "layout": layout,
                "record_on_start": record_on_start,
                "enable_room_previews": enable_room_previews,
                "meta": meta,
                "sync_audio_video": sync_audio_video,
                "tone_on_entry_and_exit": tone_on_entry_and_exit,
                "room_join_video_off": room_join_video_off,
                "user_join_video_off": user_join_video_off,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "ConferenceRoomResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_addresses(  # type: ignore[override]
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ConferenceRoomAddressListResponse:
        return cast(
            "ConferenceRoomAddressListResponse",
            self._http.get(
                f"/api/fabric/resources/conference_room/{id}/addresses",
                params=params or None,
                request_options=request_options,
            ),
        )


class CxmlApplications(BaseResource):
    """Typed resource for ``/resources/cxml_applications`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/cxml_applications")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CxmlApplicationListResponse:
        return cast(
            "CxmlApplicationListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CxmlApplicationResponse:
        return cast(
            "CxmlApplicationResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        *,
        display_name: str | None = None,
        account_sid: uuid | None = None,
        voice_url: str | None = None,
        voice_method: Literal["GET"] | Literal["POST"] | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        sms_url: str | None = None,
        sms_method: Literal["GET"] | Literal["POST"] | None = None,
        sms_fallback_url: str | None = None,
        sms_fallback_method: Literal["GET"] | Literal["POST"] | None = None,
        sms_status_callback: str | None = None,
        sms_status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        name: str | None = None,
        call_request_url: str | None = None,
        call_request_method: Literal["GET", "POST"] | None = None,
        call_fallback_url: str | None = None,
        call_fallback_method: Literal["GET", "POST"] | None = None,
        call_status_url: str | None = None,
        call_status_method: Literal["GET", "POST"] | None = None,
        message_request_url: str | None = None,
        message_request_method: Literal["GET", "POST"] | None = None,
        message_fallback_url: str | None = None,
        message_fallback_method: Literal["GET", "POST"] | None = None,
        message_status_url: str | None = None,
        message_status_method: Literal["GET", "POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CxmlApplicationResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "account_sid": account_sid,
                "voice_url": voice_url,
                "voice_method": voice_method,
                "voice_fallback_url": voice_fallback_url,
                "voice_fallback_method": voice_fallback_method,
                "status_callback": status_callback,
                "status_callback_method": status_callback_method,
                "sms_url": sms_url,
                "sms_method": sms_method,
                "sms_fallback_url": sms_fallback_url,
                "sms_fallback_method": sms_fallback_method,
                "sms_status_callback": sms_status_callback,
                "sms_status_callback_method": sms_status_callback_method,
                "name": name,
                "call_request_url": call_request_url,
                "call_request_method": call_request_method,
                "call_fallback_url": call_fallback_url,
                "call_fallback_method": call_fallback_method,
                "call_status_url": call_status_url,
                "call_status_method": call_status_method,
                "message_request_url": message_request_url,
                "message_request_method": message_request_method,
                "message_fallback_url": message_fallback_url,
                "message_fallback_method": message_fallback_method,
                "message_status_url": message_status_url,
                "message_status_method": message_status_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CxmlApplicationResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )

    def list_addresses(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CxmlApplicationAddressListResponse:
        return cast(
            "CxmlApplicationAddressListResponse",
            self._http.get(
                self._path(id, "addresses"),
                params=params or None,
                request_options=request_options,
            ),
        )


class CxmlScripts(
    FabricResource[
        "CXMLScriptListResponse",
        "CXMLScriptResponse",
        "CXMLScriptCreateRequest",
        "CXMLScriptUpdateRequest",
    ]
):
    """Typed resource for ``/resources/cxml_scripts`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/cxml_scripts")

    def create(  # type: ignore[override]
        self,
        *,
        contents: str,
        display_name: str | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        name: str | None = None,
        script_type: Literal["calling", "faxing", "messaging"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CXMLScriptResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "contents": contents,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
                "name": name,
                "script_type": script_type,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CXMLScriptResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        display_name: str | None = None,
        contents: str | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        name: str | None = None,
        script_type: Literal["calling", "faxing", "messaging"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CXMLScriptResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "contents": contents,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
                "name": name,
                "script_type": script_type,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CXMLScriptResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class CxmlWebhooks(
    FabricResource[
        "CXMLWebhookListResponse",
        "CXMLWebhookResponse",
        "CXMLWebhookCreateRequest",
        "CXMLWebhookUpdateRequest",
    ]
):
    """Typed resource for ``/resources/cxml_webhooks`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/cxml_webhooks")

    def create(  # type: ignore[override]
        self,
        *,
        primary_request_url: str,
        name: str | None = None,
        used_for: UsedForType | None = None,
        primary_request_method: Literal["GET"] | Literal["POST"] | None = None,
        fallback_request_url: str | None = None,
        fallback_request_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CXMLWebhookResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "used_for": used_for,
                "primary_request_url": primary_request_url,
                "primary_request_method": primary_request_method,
                "fallback_request_url": fallback_request_url,
                "fallback_request_method": fallback_request_method,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CXMLWebhookResponse",
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
        used_for: UsedForType | None = None,
        primary_request_url: str | None = None,
        primary_request_method: Literal["GET"] | Literal["POST"] | None = None,
        fallback_request_url: str | None = None,
        fallback_request_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CXMLWebhookResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "used_for": used_for,
                "primary_request_url": primary_request_url,
                "primary_request_method": primary_request_method,
                "fallback_request_url": fallback_request_url,
                "fallback_request_method": fallback_request_method,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CXMLWebhookResponse",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class FreeswitchConnectors(
    FabricResource[
        "FreeswitchConnectorListResponse",
        "FreeswitchConnectorResponse",
        "FreeswitchConnectorCreateRequest",
        "FreeswitchConnectorUpdateRequest",
    ]
):
    """Typed resource for ``/resources/freeswitch_connectors`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/freeswitch_connectors")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        token: uuid,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> FreeswitchConnectorResponse:
        body: dict[str, Any] = {
            k: v for k, v in {"name": name, "token": token}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "FreeswitchConnectorResponse",
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
        caller_id: str | None = None,
        send_as: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> FreeswitchConnectorResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "caller_id": caller_id,
                "send_as": send_as,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "FreeswitchConnectorResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class RelayApplications(
    FabricResource[
        "RelayApplicationListResponse",
        "RelayApplicationResponse",
        "RelayApplicationCreateRequest",
        "RelayApplicationUpdateRequest",
    ]
):
    """Typed resource for ``/resources/relay_applications`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/relay_applications")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        topic: str,
        call_status_callback_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> RelayApplicationResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "topic": topic,
                "call_status_callback_url": call_status_callback_url,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "RelayApplicationResponse",
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
        topic: str | None = None,
        call_status_callback_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> RelayApplicationResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "topic": topic,
                "call_status_callback_url": call_status_callback_url,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "RelayApplicationResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class SipEndpoints(
    FabricResource[
        "SipEndpointListResponse",
        "SipEndpointResponse",
        "SipEndpointCreateRequest",
        "SipEndpointUpdateRequest",
    ]
):
    """Typed resource for ``/resources/sip_endpoints`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/sip_endpoints")

    def create(  # type: ignore[override]
        self,
        *,
        username: str,
        id: uuid | None = None,
        caller_id: str | None = None,
        send_as: str | None = None,
        ciphers: list[Ciphers] | None = None,
        codecs: list[Codecs] | None = None,
        encryption: Encryption | None = None,
        call_handler: CallHandlerType | None = None,
        calling_handler_resource_id: uuid | None | None = None,
        password: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipEndpointResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "id": id,
                "username": username,
                "caller_id": caller_id,
                "send_as": send_as,
                "ciphers": ciphers,
                "codecs": codecs,
                "encryption": encryption,
                "call_handler": call_handler,
                "calling_handler_resource_id": calling_handler_resource_id,
                "password": password,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipEndpointResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        username: str | None = None,
        caller_id: str | None = None,
        send_as: str | None = None,
        ciphers: list[Ciphers] | None = None,
        codecs: list[Codecs] | None = None,
        encryption: Encryption | None = None,
        call_handler: CallHandlerType | None = None,
        calling_handler_resource_id: uuid | None | None = None,
        password: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipEndpointResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "username": username,
                "caller_id": caller_id,
                "send_as": send_as,
                "ciphers": ciphers,
                "codecs": codecs,
                "encryption": encryption,
                "call_handler": call_handler,
                "calling_handler_resource_id": calling_handler_resource_id,
                "password": password,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipEndpointResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class SipGateways(
    FabricResource[
        "SipGatewayListResponse",
        "SipGatewayResponse",
        "SipGatewayRequest",
        "SipGatewayRequestUpdate",
    ]
):
    """Typed resource for ``/resources/sip_gateways`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/sip_gateways")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        uri: str,
        encryption: Encryption,
        ciphers: list[Ciphers] | None = None,
        codecs: list[Codecs] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipGatewayResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "uri": uri,
                "encryption": encryption,
                "ciphers": ciphers,
                "codecs": codecs,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipGatewayResponse",
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
        uri: str | None = None,
        encryption: Encryption | None = None,
        ciphers: list[Ciphers] | None = None,
        codecs: list[Codecs] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipGatewayResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "uri": uri,
                "encryption": encryption,
                "ciphers": ciphers,
                "codecs": codecs,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipGatewayResponse",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class Subscribers(
    FabricResource[
        "SubscriberListResponse",
        "SubscriberResponse",
        "SubscriberRequest",
        "SubscriberUpdateRequest",
    ]
):
    """Typed resource for ``/resources/subscribers`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/subscribers")

    def create(  # type: ignore[override]
        self,
        *,
        email: str,
        password: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        display_name: str | None = None,
        job_title: str | None = None,
        timezone: str | None = None,
        country: str | None = None,
        region: str | None = None,
        company_name: str | None = None,
        time_zone: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "password": password,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "display_name": display_name,
                "job_title": job_title,
                "timezone": timezone,
                "country": country,
                "region": region,
                "company_name": company_name,
                "time_zone": time_zone,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        password: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        display_name: str | None = None,
        job_title: str | None = None,
        timezone: str | None = None,
        country: str | None = None,
        region: str | None = None,
        company_name: str | None = None,
        time_zone: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "password": password,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "display_name": display_name,
                "job_title": job_title,
                "timezone": timezone,
                "country": country,
                "region": region,
                "company_name": company_name,
                "time_zone": time_zone,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_sip_endpoints(
        self,
        fabric_subscriber_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> SubscriberSipEndpointListResponse:
        return cast(
            "SubscriberSipEndpointListResponse",
            self._http.get(
                self._path(fabric_subscriber_id, "sip_endpoints"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def create_sip_endpoint(
        self,
        fabric_subscriber_id: str,
        *,
        username: str,
        password: str,
        caller_id: str | None = None,
        send_as: str | None = None,
        ciphers: list[Ciphers] | None = None,
        codecs: list[Codecs] | None = None,
        encryption: Encryption | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberSIPEndpoint:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "username": username,
                "password": password,
                "caller_id": caller_id,
                "send_as": send_as,
                "ciphers": ciphers,
                "codecs": codecs,
                "encryption": encryption,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberSIPEndpoint",
            self._http.post(
                self._path(fabric_subscriber_id, "sip_endpoints"),
                body=body,
                request_options=request_options,
            ),
        )

    def get_sip_endpoint(
        self,
        fabric_subscriber_id: str,
        id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> SubscriberSIPEndpoint:
        return cast(
            "SubscriberSIPEndpoint",
            self._http.get(
                self._path(fabric_subscriber_id, "sip_endpoints", id),
                params=params or None,
                request_options=request_options,
            ),
        )

    def update_sip_endpoint(
        self,
        fabric_subscriber_id: str,
        id: str,
        *,
        username: str | None = None,
        password: str | None = None,
        caller_id: str | None = None,
        send_as: str | None = None,
        ciphers: list[Ciphers] | None = None,
        codecs: list[Codecs] | None = None,
        encryption: Encryption | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberSIPEndpoint:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "username": username,
                "password": password,
                "caller_id": caller_id,
                "send_as": send_as,
                "ciphers": ciphers,
                "codecs": codecs,
                "encryption": encryption,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberSIPEndpoint",
            self._http.patch(
                self._path(fabric_subscriber_id, "sip_endpoints", id),
                body=body,
                request_options=request_options,
            ),
        )

    def delete_sip_endpoint(
        self,
        fabric_subscriber_id: str,
        id: str,
        *,
        request_options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(
                self._path(fabric_subscriber_id, "sip_endpoints", id),
                request_options=request_options,
            ),
        )


class SwmlScripts(
    FabricResource[
        "SwmlScriptListResponse",
        "SwmlScriptResponse",
        "SwmlScriptCreateRequest",
        "SwmlScriptUpdateRequest",
    ]
):
    """Typed resource for ``/resources/swml_scripts`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/swml_scripts")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        contents: str | dict[str, Any],
        status_callback_url: str | None = None,
        script_type: Literal["calling", "messaging"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SwmlScriptResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "contents": contents,
                "status_callback_url": status_callback_url,
                "script_type": script_type,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SwmlScriptResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        display_name: str | None = None,
        contents: str | dict[str, Any] | None = None,
        status_callback_url: str | None = None,
        name: str | None = None,
        script_type: Literal["calling", "messaging"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SwmlScriptResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "contents": contents,
                "status_callback_url": status_callback_url,
                "name": name,
                "script_type": script_type,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SwmlScriptResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class SwmlWebhooks(
    FabricResource[
        "SWMLWebhookListResponse",
        "SWMLWebhookResponse",
        "SWMLWebhookCreateRequest",
        "SWMLWebhookUpdateRequest",
    ]
):
    """Typed resource for ``/resources/swml_webhooks`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/swml_webhooks")

    def create(  # type: ignore[override]
        self,
        *,
        primary_request_url: str,
        name: str | None = None,
        used_for: Literal["calling", "messaging"] | None = None,
        primary_request_method: Literal["GET"] | Literal["POST"] | None = None,
        fallback_request_url: str | None = None,
        fallback_request_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SWMLWebhookResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "used_for": used_for,
                "primary_request_url": primary_request_url,
                "primary_request_method": primary_request_method,
                "fallback_request_url": fallback_request_url,
                "fallback_request_method": fallback_request_method,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SWMLWebhookResponse",
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
        used_for: Literal["calling", "messaging"] | None = None,
        primary_request_url: str | None = None,
        primary_request_method: Literal["GET"] | Literal["POST"] | None = None,
        fallback_request_url: str | None = None,
        fallback_request_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SWMLWebhookResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "used_for": used_for,
                "primary_request_url": primary_request_url,
                "primary_request_method": primary_request_method,
                "fallback_request_url": fallback_request_url,
                "fallback_request_method": fallback_request_method,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SWMLWebhookResponse",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class FabricTokens(BaseResource):
    """Typed resource for ```` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric")

    def create_subscriber_token(
        self,
        *,
        reference: str,
        expire_at: int | None = None,
        application_id: uuid | None = None,
        password: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        display_name: str | None = None,
        job_title: str | None = None,
        time_zone: str | None = None,
        country: str | None = None,
        region: str | None = None,
        company_name: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberTokenResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "reference": reference,
                "expire_at": expire_at,
                "application_id": application_id,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "display_name": display_name,
                "job_title": job_title,
                "time_zone": time_zone,
                "country": country,
                "region": region,
                "company_name": company_name,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberTokenResponse",
            self._http.post(
                self._path("subscribers", "tokens"),
                body=body,
                request_options=request_options,
            ),
        )

    def refresh_subscriber_token(
        self,
        *,
        refresh_token: jwt,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberRefreshTokenResponse:
        body: dict[str, Any] = {
            k: v for k, v in {"refresh_token": refresh_token}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberRefreshTokenResponse",
            self._http.post(
                self._path("subscribers", "tokens", "refresh"),
                body=body,
                request_options=request_options,
            ),
        )

    def create_invite_token(
        self,
        *,
        address_id: uuid,
        expires_at: int | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberInviteTokenCreateResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"address_id": address_id, "expires_at": expires_at}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberInviteTokenCreateResponse",
            self._http.post(
                self._path("subscriber", "invites"),
                body=body,
                request_options=request_options,
            ),
        )

    def create_guest_token(
        self,
        *,
        allowed_addresses: list[uuid] | None = None,
        expire_at: int | None = None,
        ch: str | None = None,
        region: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        display_name: str | None = None,
        job_title: str | None = None,
        time_zone: str | None = None,
        country: str | None = None,
        company_name: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberGuestTokenCreateResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "allowed_addresses": allowed_addresses,
                "expire_at": expire_at,
                "ch": ch,
                "region": region,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "display_name": display_name,
                "job_title": job_title,
                "time_zone": time_zone,
                "country": country,
                "company_name": company_name,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberGuestTokenCreateResponse",
            self._http.post(
                self._path("guests", "tokens"),
                body=body,
                request_options=request_options,
            ),
        )

    def create_embed_token(
        self,
        *,
        token: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> EmbedsTokensResponse:
        body: dict[str, Any] = {
            k: v for k, v in {"token": token}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "EmbedsTokensResponse",
            self._http.post(
                self._path("embeds", "tokens"),
                body=body,
                request_options=request_options,
            ),
        )
