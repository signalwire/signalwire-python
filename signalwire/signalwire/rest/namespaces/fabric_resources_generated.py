# AUTO-GENERATED from porting-sdk/rest-apis/fabric/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed create/update
# (explicit spec fields + an ``extras`` door), bound to the resource's spec
# types. Runtime body is a plain dict (open-tail, never validated).
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import FabricResource

if TYPE_CHECKING:
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
        CXMLScriptCreateRequest,
        CXMLScriptListResponse,
        CXMLScriptResponse,
        CXMLScriptUpdateRequest,
        CXMLWebhookCreateRequest,
        CXMLWebhookListResponse,
        CXMLWebhookResponse,
        CXMLWebhookUpdateRequest,
        CallFlowCreateRequest,
        CallFlowListResponse,
        CallFlowResponse,
        CallFlowUpdateRequest,
        CallHandlerType,
        Ciphers,
        Codecs,
        ConferenceRoomCreateRequest,
        ConferenceRoomListResponse,
        ConferenceRoomResponse,
        ConferenceRoomUpdateRequest,
        Encryption,
        FreeswitchConnectorCreateRequest,
        FreeswitchConnectorListResponse,
        FreeswitchConnectorResponse,
        FreeswitchConnectorUpdateRequest,
        Hint,
        Languages,
        Layout,
        Pronounce,
        RelayApplicationCreateRequest,
        RelayApplicationListResponse,
        RelayApplicationResponse,
        RelayApplicationUpdateRequest,
        SWAIG,
        SWAIGUpdate,
        SWMLWebhookCreateRequest,
        SWMLWebhookListResponse,
        SWMLWebhookResponse,
        SWMLWebhookUpdateRequest,
        SipEndpointCreateRequest,
        SipEndpointListResponse,
        SipEndpointResponse,
        SipEndpointUpdateRequest,
        SipGatewayListResponse,
        SipGatewayRequest,
        SipGatewayRequestUpdate,
        SipGatewayResponse,
        SubscriberListResponse,
        SubscriberRequest,
        SubscriberResponse,
        SwmlScriptCreateRequest,
        SwmlScriptListResponse,
        SwmlScriptResponse,
        SwmlScriptUpdateRequest,
        UsedForType,
        uuid,
    )


class AiAgentsResource(
    FabricResource[
        "AIAgentListResponse",
        "AIAgentResponse",
        "AIAgentCreateRequest",
        "AIAgentUpdateRequest",
    ]
):
    """Typed CRUD resource for ``/resources/ai_agents`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/ai_agents")

    def create(  # type: ignore[override]
        self,
        *,
        prompt: AIPrompt,
        agent_id: uuid,
        name: str,
        global_data: dict[str, Any] | None = None,
        hints: list[str | Hint] | None = None,
        languages: list[Languages] | None = None,
        params: AIParams | None = None,
        post_prompt: AIPostPrompt | None = None,
        post_prompt_url: str | None = None,
        pronounce: list[Pronounce] | None = None,
        SWAIG: SWAIG | None = None,
        extras: Mapping[str, Any] | None = None,
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
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("AIAgentResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
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
        extras: Mapping[str, Any] | None = None,
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
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("AIAgentResponse", self._http.patch(self._path(id), body=body))


class CallFlowsResource(
    FabricResource[
        "CallFlowListResponse",
        "CallFlowResponse",
        "CallFlowCreateRequest",
        "CallFlowUpdateRequest",
    ]
):
    """Typed CRUD resource for ``/resources/call_flows`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/call_flows")

    def create(  # type: ignore[override]
        self, *, title: str, extras: Mapping[str, Any] | None = None
    ) -> CallFlowResponse:
        body: dict[str, Any] = {
            k: v for k, v in {"title": title}.items() if v is not None
        }
        if extras:
            body.update(extras)
        return cast("CallFlowResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
        self,
        id: str,
        /,
        *,
        title: str | None = None,
        document_version: int | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CallFlowResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {"title": title, "document_version": document_version}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("CallFlowResponse", self._http.put(self._path(id), body=body))


class ConferenceRoomsResource(
    FabricResource[
        "ConferenceRoomListResponse",
        "ConferenceRoomResponse",
        "ConferenceRoomCreateRequest",
        "ConferenceRoomUpdateRequest",
    ]
):
    """Typed CRUD resource for ``/resources/conference_rooms`` (generated)."""

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
        return cast(
            "ConferenceRoomResponse", self._http.post(self._base_path, body=body)
        )

    def update(  # type: ignore[override]
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
        return cast("ConferenceRoomResponse", self._http.put(self._path(id), body=body))


class CxmlScriptsResource(
    FabricResource[
        "CXMLScriptListResponse",
        "CXMLScriptResponse",
        "CXMLScriptCreateRequest",
        "CXMLScriptUpdateRequest",
    ]
):
    """Typed CRUD resource for ``/resources/cxml_scripts`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/cxml_scripts")

    def create(  # type: ignore[override]
        self,
        *,
        display_name: str,
        contents: str,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CXMLScriptResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "contents": contents,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("CXMLScriptResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
        self,
        id: str,
        /,
        *,
        display_name: str | None = None,
        contents: str | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CXMLScriptResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "contents": contents,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("CXMLScriptResponse", self._http.put(self._path(id), body=body))


class CxmlWebhooksResource(
    FabricResource[
        "CXMLWebhookListResponse",
        "CXMLWebhookResponse",
        "CXMLWebhookCreateRequest",
        "CXMLWebhookUpdateRequest",
    ]
):
    """Typed CRUD resource for ``/resources/cxml_webhooks`` (generated)."""

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
        return cast("CXMLWebhookResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
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
        return cast("CXMLWebhookResponse", self._http.patch(self._path(id), body=body))


class FreeswitchConnectorsResource(
    FabricResource[
        "FreeswitchConnectorListResponse",
        "FreeswitchConnectorResponse",
        "FreeswitchConnectorCreateRequest",
        "FreeswitchConnectorUpdateRequest",
    ]
):
    """Typed CRUD resource for ``/resources/freeswitch_connectors`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/freeswitch_connectors")

    def create(  # type: ignore[override]
        self, *, name: str, token: uuid, extras: Mapping[str, Any] | None = None
    ) -> FreeswitchConnectorResponse:
        body: dict[str, Any] = {
            k: v for k, v in {"name": name, "token": token}.items() if v is not None
        }
        if extras:
            body.update(extras)
        return cast(
            "FreeswitchConnectorResponse", self._http.post(self._base_path, body=body)
        )

    def update(  # type: ignore[override]
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        caller_id: str | None = None,
        send_as: str | None = None,
        extras: Mapping[str, Any] | None = None,
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
        return cast(
            "FreeswitchConnectorResponse", self._http.put(self._path(id), body=body)
        )


class RelayApplicationsResource(
    FabricResource[
        "RelayApplicationListResponse",
        "RelayApplicationResponse",
        "RelayApplicationCreateRequest",
        "RelayApplicationUpdateRequest",
    ]
):
    """Typed CRUD resource for ``/resources/relay_applications`` (generated)."""

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
        return cast(
            "RelayApplicationResponse", self._http.post(self._base_path, body=body)
        )

    def update(  # type: ignore[override]
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        topic: str | None = None,
        call_status_callback_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
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
        return cast(
            "RelayApplicationResponse", self._http.put(self._path(id), body=body)
        )


class SipEndpointsResource(
    FabricResource[
        "SipEndpointListResponse",
        "SipEndpointResponse",
        "SipEndpointCreateRequest",
        "SipEndpointUpdateRequest",
    ]
):
    """Typed CRUD resource for ``/resources/sip_endpoints`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/sip_endpoints")

    def create(  # type: ignore[override]
        self,
        *,
        id: uuid,
        username: str,
        caller_id: str,
        send_as: str,
        ciphers: list[Ciphers],
        codecs: list[Codecs],
        encryption: Encryption,
        call_handler: CallHandlerType,
        calling_handler_resource_id: uuid | None,
        extras: Mapping[str, Any] | None = None,
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
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("SipEndpointResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
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
        extras: Mapping[str, Any] | None = None,
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
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("SipEndpointResponse", self._http.put(self._path(id), body=body))


class SipGatewaysResource(
    FabricResource[
        "SipGatewayListResponse",
        "SipGatewayResponse",
        "SipGatewayRequest",
        "SipGatewayRequestUpdate",
    ]
):
    """Typed CRUD resource for ``/resources/sip_gateways`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/sip_gateways")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        uri: str,
        encryption: Encryption,
        ciphers: list[Ciphers],
        codecs: list[Codecs],
        extras: Mapping[str, Any] | None = None,
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
        return cast("SipGatewayResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
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
        return cast("SipGatewayResponse", self._http.patch(self._path(id), body=body))


class SubscribersResource(
    FabricResource[
        "SubscriberListResponse",
        "SubscriberResponse",
        "SubscriberRequest",
        "SubscriberRequest",
    ]
):
    """Typed CRUD resource for ``/resources/subscribers`` (generated)."""

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
        extras: Mapping[str, Any] | None = None,
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
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("SubscriberResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
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
        extras: Mapping[str, Any] | None = None,
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
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("SubscriberResponse", self._http.put(self._path(id), body=body))


class SwmlScriptsResource(
    FabricResource[
        "SwmlScriptListResponse",
        "SwmlScriptResponse",
        "SwmlScriptCreateRequest",
        "SwmlScriptUpdateRequest",
    ]
):
    """Typed CRUD resource for ``/resources/swml_scripts`` (generated)."""

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/swml_scripts")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        contents: str,
        status_callback_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> SwmlScriptResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "contents": contents,
                "status_callback_url": status_callback_url,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("SwmlScriptResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
        self,
        id: str,
        /,
        *,
        display_name: str | None = None,
        contents: str | None = None,
        status_callback_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> SwmlScriptResponse:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "contents": contents,
                "status_callback_url": status_callback_url,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        return cast("SwmlScriptResponse", self._http.put(self._path(id), body=body))


class SwmlWebhooksResource(
    FabricResource[
        "SWMLWebhookListResponse",
        "SWMLWebhookResponse",
        "SWMLWebhookCreateRequest",
        "SWMLWebhookUpdateRequest",
    ]
):
    """Typed CRUD resource for ``/resources/swml_webhooks`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/swml_webhooks")

    def create(  # type: ignore[override]
        self,
        *,
        primary_request_url: str,
        name: str | None = None,
        used_for: Literal["calling"] | None = None,
        primary_request_method: Literal["GET"] | Literal["POST"] | None = None,
        fallback_request_url: str | None = None,
        fallback_request_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
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
        return cast("SWMLWebhookResponse", self._http.post(self._base_path, body=body))

    def update(  # type: ignore[override]
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        used_for: Literal["calling"] | None = None,
        primary_request_url: str | None = None,
        primary_request_method: Literal["GET"] | Literal["POST"] | None = None,
        fallback_request_url: str | None = None,
        fallback_request_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
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
        return cast("SWMLWebhookResponse", self._http.patch(self._path(id), body=body))
