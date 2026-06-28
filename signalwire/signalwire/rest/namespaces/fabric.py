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
from .fabric_resources_generated import (
    AiAgentsResource,
    CallFlowsResource,
    ConferenceRoomsResource,
    CxmlApplicationsResource,
    CxmlScriptsResource,
    CxmlWebhooksResource,
    FabricAddressesResource,
    FabricTokensResource,
    FreeswitchConnectorsResource,
    GenericResourcesResource,
    RelayApplicationsResource,
    SipEndpointsResource,
    SipGatewaysResource,
    SubscribersResource,
    SwmlScriptsResource,
    SwmlWebhooksResource,
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


# ``SwmlWebhooksResource`` / ``CxmlWebhooksResource`` are now plain generated typed
# CRUD resources (see ``fabric_resources_generated``), imported above. The former
# ``AutoMaterializedWebhook`` deprecation-warning wrapper was removed — these SDKs are
# pre-release, so there is no back-compat to deprecate. The phone-number binding model
# (``phone_numbers.set_swml_webhook`` / ``set_cxml_webhook``) remains the documented way
# to auto-materialize a webhook; direct create is just a normal operation.


# Group-B resources (CallFlows/ConferenceRooms/Subscribers/CxmlApplications) and the
# fabric-root resources (GenericResources/FabricAddresses/FabricTokens) are now generated
# (see ``fabric_resources_generated``), imported above. Back-compat aliases keep the
# historical class names working.
GenericResources = GenericResourcesResource
FabricAddresses = FabricAddressesResource
FabricTokens = FabricTokensResource


class FabricNamespace:
    """Fabric API namespace grouping all resource types."""

    def __init__(self, http: Any) -> None:
        # Every fabric resource is generated (see ``fabric_resources_generated``) and
        # bakes its own base path into ``__init__``, so each constructs as
        # ``Resource(http)``.
        self.swml_scripts = SwmlScriptsResource(http)
        self.relay_applications = RelayApplicationsResource(http)
        self.call_flows = CallFlowsResource(http)
        self.conference_rooms = ConferenceRoomsResource(http)
        self.freeswitch_connectors = FreeswitchConnectorsResource(http)
        self.subscribers = SubscribersResource(http)
        self.sip_endpoints = SipEndpointsResource(http)
        self.cxml_scripts = CxmlScriptsResource(http)
        self.cxml_applications = CxmlApplicationsResource(http)

        # PATCH-update resources. ``swml_webhooks`` / ``cxml_webhooks`` are normally
        # auto-materialized via ``phone_numbers.set_swml_webhook`` /
        # ``set_cxml_webhook``; direct create is a normal operation.
        self.swml_webhooks = SwmlWebhooksResource(http)
        self.ai_agents = AiAgentsResource(http)
        self.sip_gateways = SipGatewaysResource(http)
        self.cxml_webhooks = CxmlWebhooksResource(http)

        # Fabric-root resources (not under /resources).
        self.resources = GenericResourcesResource(http)
        self.addresses = FabricAddressesResource(http)
        self.tokens = FabricTokensResource(http)
