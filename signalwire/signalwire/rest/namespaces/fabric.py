"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Fabric API namespace — resource composition, addresses, and tokens.
"""

import warnings
from typing import TYPE_CHECKING, Any

from .._base import (
    BaseResource,
    FabricResource,
    FabricResourcePUT,
    TCreate,
    TItem,
    TList,
    TUpdate,
)

if TYPE_CHECKING:
    from .fabric_types_generated import (
        AIAgentCreateRequest,
        AIAgentListResponse,
        AIAgentResponse,
        AIAgentUpdateRequest,
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
        CallFlowVersionDeployResponse,
        CallFlowVersionListResponse,
        ConferenceRoomAddressListResponse,
        ConferenceRoomCreateRequest,
        ConferenceRoomListResponse,
        ConferenceRoomResponse,
        ConferenceRoomUpdateRequest,
        CxmlApplicationListResponse,
        CxmlApplicationResponse,
        CxmlApplicationUpdateRequest,
        DomainApplicationResponse,
        EmbedsTokensResponse,
        FabricAddress,
        FabricAddressesResponse,
        FreeswitchConnectorCreateRequest,
        FreeswitchConnectorListResponse,
        FreeswitchConnectorResponse,
        FreeswitchConnectorUpdateRequest,
        PhoneRouteResponse,
        RelayApplicationCreateRequest,
        RelayApplicationListResponse,
        RelayApplicationResponse,
        RelayApplicationUpdateRequest,
        ResourceAddressListResponse,
        ResourceListResponse,
        ResourceResponse,
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
        SubscriberGuestTokenCreateResponse,
        SubscriberInviteTokenCreateResponse,
        SubscriberListResponse,
        SubscriberRefreshTokenResponse,
        SubscriberRequest,
        SubscriberResponse,
        SubscriberSIPEndpoint,
        SubscriberSipEndpointListResponse,
        SubscriberTokenResponse,
        SwmlScriptCreateRequest,
        SwmlScriptListResponse,
        SwmlScriptResponse,
        SwmlScriptUpdateRequest,
    )


# ``FabricResource`` / ``FabricResourcePUT`` are defined in ``.._base`` (imported
# above) so the generated ``fabric_resources_generated`` subclasses can inherit them
# without an import cycle. They remain importable from this module via that import.


class AutoMaterializedWebhook(FabricResource[TList, TItem, TCreate, TUpdate]):
    """Fabric webhook resource that's normally auto-created by phone_numbers.set_*.

    Exposed for backwards compatibility. The binding model for these resources
    is on the phone number (see ``phone_numbers.set_swml_webhook`` /
    ``set_cxml_webhook``) — setting ``call_handler`` on a phone number
    auto-materializes the webhook. Calling ``create`` here produces an orphan
    resource that isn't bound to any phone number.
    """

    _auto_helper_name = "phone_numbers.set_*_webhook"

    def create(self, **kwargs: Any) -> TItem:
        # Deprecated direct-create override (body-only: adds an orphan-warning, then
        # delegates to super). Returns TItem to stay LSP-compatible with the generic
        # base; the enumerator drops this TypeVar-returning intermediate override
        # from the oracle (the concrete subclasses publish the typed create).
        warnings.warn(
            f"Creating a webhook Fabric resource directly produces an orphan not "
            f"bound to any phone number. Use {self._auto_helper_name} instead; "
            f"it updates the phone number and the server auto-materializes the "
            f"resource. See porting-sdk's phone-binding.md.",
            DeprecationWarning,
            stacklevel=2,
        )
        return super().create(**kwargs)


class SwmlWebhooksResource(
    AutoMaterializedWebhook[
        "SWMLWebhookListResponse",
        "SWMLWebhookResponse",
        "SWMLWebhookCreateRequest",
        "SWMLWebhookUpdateRequest",
    ]
):
    _auto_helper_name = "phone_numbers.set_swml_webhook(sid, url=...)"


class CxmlWebhooksResource(
    AutoMaterializedWebhook[
        "CXMLWebhookListResponse",
        "CXMLWebhookResponse",
        "CXMLWebhookCreateRequest",
        "CXMLWebhookUpdateRequest",
    ]
):
    _auto_helper_name = "phone_numbers.set_cxml_webhook(sid, url=...)"


class CallFlowsResource(
    FabricResourcePUT[
        "CallFlowListResponse",
        "CallFlowResponse",
        "CallFlowCreateRequest",
        "CallFlowUpdateRequest",
    ]
):
    """Call flows with version management.

    Note: call_flow (singular) is used in address/version paths per the API spec.
    """

    def list_addresses(
        self, resource_id: str, **params: Any
    ) -> "CallFlowAddressListResponse":
        # API uses singular 'call_flow' for sub-resource paths
        path = self._base_path.replace("/call_flows", "/call_flow")
        return self._http.get(f"{path}/{resource_id}/addresses", params=params or None)

    def list_versions(
        self, resource_id: str, **params: Any
    ) -> "CallFlowVersionListResponse":
        path = self._base_path.replace("/call_flows", "/call_flow")
        return self._http.get(f"{path}/{resource_id}/versions", params=params or None)

    def deploy_version(
        self, resource_id: str, **kwargs: Any
    ) -> "CallFlowVersionDeployResponse":
        path = self._base_path.replace("/call_flows", "/call_flow")
        return self._http.post(f"{path}/{resource_id}/versions", body=kwargs)


class ConferenceRoomsResource(
    FabricResourcePUT[
        "ConferenceRoomListResponse",
        "ConferenceRoomResponse",
        "ConferenceRoomCreateRequest",
        "ConferenceRoomUpdateRequest",
    ]
):
    """Conference rooms — uses singular 'conference_room' for sub-resource paths."""

    def list_addresses(
        self, resource_id: str, **params: Any
    ) -> "ConferenceRoomAddressListResponse":
        path = self._base_path.replace("/conference_rooms", "/conference_room")
        return self._http.get(f"{path}/{resource_id}/addresses", params=params or None)


class SubscribersResource(
    FabricResourcePUT[
        "SubscriberListResponse",
        "SubscriberResponse",
        "SubscriberRequest",
        "SubscriberRequest",
    ]
):
    """Subscribers with SIP endpoint management."""

    def list_sip_endpoints(
        self, subscriber_id: str, **params: Any
    ) -> "SubscriberSipEndpointListResponse":
        return self._http.get(
            self._path(subscriber_id, "sip_endpoints"),
            params=params or None,
        )

    def create_sip_endpoint(
        self, subscriber_id: str, **kwargs: Any
    ) -> "SubscriberSIPEndpoint":
        return self._http.post(
            self._path(subscriber_id, "sip_endpoints"),
            body=kwargs,
        )

    def get_sip_endpoint(
        self, subscriber_id: str, endpoint_id: str
    ) -> "SubscriberSIPEndpoint":
        return self._http.get(
            self._path(subscriber_id, "sip_endpoints", endpoint_id),
        )

    def update_sip_endpoint(
        self, subscriber_id: str, endpoint_id: str, **kwargs: Any
    ) -> "SubscriberSIPEndpoint":
        return self._http.patch(
            self._path(subscriber_id, "sip_endpoints", endpoint_id),
            body=kwargs,
        )

    def delete_sip_endpoint(
        self, subscriber_id: str, endpoint_id: str
    ) -> dict[str, Any]:
        return self._http.delete(
            self._path(subscriber_id, "sip_endpoints", endpoint_id),
        )


class CxmlApplicationsResource(
    FabricResourcePUT[
        "CxmlApplicationListResponse",
        "CxmlApplicationResponse",
        Any,
        "CxmlApplicationUpdateRequest",
    ]
):
    """cXML applications — no create method (read/update/delete only).

    Mirrors the TS port's
    ``CxmlApplicationsResource extends FabricResourcePUT<…, never, …>``.
    The create slot has no faithful generated request type (create is
    disallowed and raises ``NotImplementedError``), so it is bound to ``Any``
    — Python's closest equivalent to TS ``never`` for this position.
    """

    def create(self, **kwargs: Any) -> Any:
        raise NotImplementedError("cXML applications cannot be created via this API")


class GenericResources(BaseResource):
    """Generic resource operations across all fabric resource types."""

    def list(self, **params: Any) -> "ResourceListResponse":
        return self._http.get(self._base_path, params=params or None)

    def get(self, resource_id: str) -> "ResourceResponse":
        return self._http.get(self._path(resource_id))

    def delete(self, resource_id: str) -> dict[str, Any]:
        return self._http.delete(self._path(resource_id))

    def list_addresses(
        self, resource_id: str, **params: Any
    ) -> "ResourceAddressListResponse":
        return self._http.get(
            self._path(resource_id, "addresses"),
            params=params or None,
        )

    def assign_phone_route(
        self, resource_id: str, **kwargs: Any
    ) -> "PhoneRouteResponse":
        """Deprecated for the common binding cases. Use ``phone_numbers.set_*`` helpers.

        This endpoint (``POST /api/fabric/resources/{id}/phone_routes``) accepts
        only a narrow set of legacy resource types as the attach target. It
        **does not work** for ``swml_webhook`` / ``cxml_webhook`` / ``ai_agent``
        bindings — those are configured on the phone number and the Fabric
        resource is auto-materialized (see ``phone_numbers.set_swml_webhook``
        etc.). The authoritative list of accepting resource types lives in the
        OpenAPI spec; routing here for those types returns 404 or 422.
        """
        warnings.warn(
            "assign_phone_route does not bind phone numbers to "
            "swml_webhook/cxml_webhook/ai_agent resources — those are "
            "configured via phone_numbers.set_swml_webhook / set_cxml_webhook "
            "/ set_ai_agent. This method applies only to a narrow set of "
            "legacy resource types. See porting-sdk's phone-binding.md.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._http.post(self._path(resource_id, "phone_routes"), body=kwargs)

    def assign_domain_application(
        self, resource_id: str, **kwargs: Any
    ) -> "DomainApplicationResponse":
        return self._http.post(
            self._path(resource_id, "domain_applications"), body=kwargs
        )


class FabricAddresses(BaseResource):
    """Read-only fabric addresses."""

    def list(self, **params: Any) -> "FabricAddressesResponse":
        return self._http.get(self._base_path, params=params or None)

    def get(self, address_id: str) -> "FabricAddress":
        return self._http.get(self._path(address_id))


class FabricTokens(BaseResource):
    """Subscriber, guest, invite, and embed token creation."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric")

    def create_subscriber_token(self, **kwargs: Any) -> "SubscriberTokenResponse":
        return self._http.post(self._path("subscribers", "tokens"), body=kwargs)

    def refresh_subscriber_token(
        self, **kwargs: Any
    ) -> "SubscriberRefreshTokenResponse":
        return self._http.post(
            self._path("subscribers", "tokens", "refresh"), body=kwargs
        )

    def create_invite_token(
        self, **kwargs: Any
    ) -> "SubscriberInviteTokenCreateResponse":
        return self._http.post(self._path("subscriber", "invites"), body=kwargs)

    def create_guest_token(self, **kwargs: Any) -> "SubscriberGuestTokenCreateResponse":
        return self._http.post(self._path("guests", "tokens"), body=kwargs)

    def create_embed_token(self, **kwargs: Any) -> "EmbedsTokensResponse":
        return self._http.post(self._path("embeds", "tokens"), body=kwargs)


class FabricNamespace:
    """Fabric API namespace grouping all resource types."""

    def __init__(self, http: Any) -> None:
        base = "/api/fabric/resources"

        # PUT-update resources. The bare FabricResourcePUT / FabricResource
        # resources carry their concrete per-operation shapes via an attribute
        # annotation (mirrors the TS port's typed ``readonly`` fields), so the
        # signature oracle resolves each one's real list/item/create/update
        # types rather than the unbound TypeVars.
        self.swml_scripts: FabricResourcePUT[
            SwmlScriptListResponse,
            SwmlScriptResponse,
            SwmlScriptCreateRequest,
            SwmlScriptUpdateRequest,
        ] = FabricResourcePUT(http, f"{base}/swml_scripts")
        self.relay_applications: FabricResourcePUT[
            RelayApplicationListResponse,
            RelayApplicationResponse,
            RelayApplicationCreateRequest,
            RelayApplicationUpdateRequest,
        ] = FabricResourcePUT(http, f"{base}/relay_applications")
        self.call_flows = CallFlowsResource(http, f"{base}/call_flows")
        self.conference_rooms = ConferenceRoomsResource(
            http, f"{base}/conference_rooms"
        )
        self.freeswitch_connectors: FabricResourcePUT[
            FreeswitchConnectorListResponse,
            FreeswitchConnectorResponse,
            FreeswitchConnectorCreateRequest,
            FreeswitchConnectorUpdateRequest,
        ] = FabricResourcePUT(http, f"{base}/freeswitch_connectors")
        self.subscribers = SubscribersResource(http, f"{base}/subscribers")
        self.sip_endpoints: FabricResourcePUT[
            SipEndpointListResponse,
            SipEndpointResponse,
            SipEndpointCreateRequest,
            SipEndpointUpdateRequest,
        ] = FabricResourcePUT(http, f"{base}/sip_endpoints")
        self.cxml_scripts: FabricResourcePUT[
            CXMLScriptListResponse,
            CXMLScriptResponse,
            CXMLScriptCreateRequest,
            CXMLScriptUpdateRequest,
        ] = FabricResourcePUT(http, f"{base}/cxml_scripts")
        self.cxml_applications = CxmlApplicationsResource(
            http, f"{base}/cxml_applications"
        )

        # PATCH-update resources
        # swml_webhooks and cxml_webhooks are normally auto-materialized by
        # phone_numbers.set_swml_webhook / set_cxml_webhook. Direct create
        # still works for backcompat but emits a DeprecationWarning.
        self.swml_webhooks = SwmlWebhooksResource(http, f"{base}/swml_webhooks")
        self.ai_agents: FabricResource[
            AIAgentListResponse,
            AIAgentResponse,
            AIAgentCreateRequest,
            AIAgentUpdateRequest,
        ] = FabricResource(http, f"{base}/ai_agents")
        self.sip_gateways: FabricResource[
            SipGatewayListResponse,
            SipGatewayResponse,
            SipGatewayRequest,
            SipGatewayRequestUpdate,
        ] = FabricResource(http, f"{base}/sip_gateways")
        self.cxml_webhooks = CxmlWebhooksResource(http, f"{base}/cxml_webhooks")

        # Special resources
        self.resources = GenericResources(http, base)
        self.addresses = FabricAddresses(http, "/api/fabric/addresses")
        self.tokens = FabricTokens(http)
