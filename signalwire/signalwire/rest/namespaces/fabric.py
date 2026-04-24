"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Fabric API namespace — resource composition, addresses, and tokens.
"""

import warnings

from .._base import BaseResource, CrudWithAddresses


class FabricResource(CrudWithAddresses):
    """Standard fabric resource with CRUD + addresses."""
    pass


class FabricResourcePUT(CrudWithAddresses):
    """Fabric resource that uses PUT for updates."""
    _update_method = "PUT"


class AutoMaterializedWebhook(FabricResource):
    """Fabric webhook resource that's normally auto-created by phone_numbers.set_*.

    Exposed for backwards compatibility. The binding model for these resources
    is on the phone number (see ``phone_numbers.set_swml_webhook`` /
    ``set_cxml_webhook``) — setting ``call_handler`` on a phone number
    auto-materializes the webhook. Calling ``create`` here produces an orphan
    resource that isn't bound to any phone number.
    """

    _auto_helper_name = "phone_numbers.set_*_webhook"

    def create(self, **kwargs):
        warnings.warn(
            f"Creating a webhook Fabric resource directly produces an orphan not "
            f"bound to any phone number. Use {self._auto_helper_name} instead; "
            f"it updates the phone number and the server auto-materializes the "
            f"resource. See porting-sdk's phone-binding.md.",
            DeprecationWarning,
            stacklevel=2,
        )
        return super().create(**kwargs)


class SwmlWebhooksResource(AutoMaterializedWebhook):
    _auto_helper_name = "phone_numbers.set_swml_webhook(sid, url=...)"


class CxmlWebhooksResource(AutoMaterializedWebhook):
    _auto_helper_name = "phone_numbers.set_cxml_webhook(sid, url=...)"


class CallFlowsResource(FabricResourcePUT):
    """Call flows with version management.

    Note: call_flow (singular) is used in address/version paths per the API spec.
    """

    def list_addresses(self, resource_id, **params):
        # API uses singular 'call_flow' for sub-resource paths
        path = self._base_path.replace("/call_flows", "/call_flow")
        return self._http.get(f"{path}/{resource_id}/addresses", params=params or None)

    def list_versions(self, resource_id, **params):
        path = self._base_path.replace("/call_flows", "/call_flow")
        return self._http.get(f"{path}/{resource_id}/versions", params=params or None)

    def deploy_version(self, resource_id, **kwargs):
        path = self._base_path.replace("/call_flows", "/call_flow")
        return self._http.post(f"{path}/{resource_id}/versions", body=kwargs)


class ConferenceRoomsResource(FabricResourcePUT):
    """Conference rooms — uses singular 'conference_room' for sub-resource paths."""

    def list_addresses(self, resource_id, **params):
        path = self._base_path.replace("/conference_rooms", "/conference_room")
        return self._http.get(f"{path}/{resource_id}/addresses", params=params or None)


class SubscribersResource(FabricResourcePUT):
    """Subscribers with SIP endpoint management."""

    def list_sip_endpoints(self, subscriber_id, **params):
        return self._http.get(
            self._path(subscriber_id, "sip_endpoints"),
            params=params or None,
        )

    def create_sip_endpoint(self, subscriber_id, **kwargs):
        return self._http.post(
            self._path(subscriber_id, "sip_endpoints"),
            body=kwargs,
        )

    def get_sip_endpoint(self, subscriber_id, endpoint_id):
        return self._http.get(
            self._path(subscriber_id, "sip_endpoints", endpoint_id),
        )

    def update_sip_endpoint(self, subscriber_id, endpoint_id, **kwargs):
        return self._http.patch(
            self._path(subscriber_id, "sip_endpoints", endpoint_id),
            body=kwargs,
        )

    def delete_sip_endpoint(self, subscriber_id, endpoint_id):
        return self._http.delete(
            self._path(subscriber_id, "sip_endpoints", endpoint_id),
        )


class CxmlApplicationsResource(FabricResourcePUT):
    """cXML applications — no create method (read/update/delete only)."""

    def create(self, **kwargs):
        raise NotImplementedError("cXML applications cannot be created via this API")


class GenericResources(BaseResource):
    """Generic resource operations across all fabric resource types."""

    def list(self, **params):
        return self._http.get(self._base_path, params=params or None)

    def get(self, resource_id):
        return self._http.get(self._path(resource_id))

    def delete(self, resource_id):
        return self._http.delete(self._path(resource_id))

    def list_addresses(self, resource_id, **params):
        return self._http.get(
            self._path(resource_id, "addresses"),
            params=params or None,
        )

    def assign_phone_route(self, resource_id, **kwargs):
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

    def assign_domain_application(self, resource_id, **kwargs):
        return self._http.post(self._path(resource_id, "domain_applications"), body=kwargs)


class FabricAddresses(BaseResource):
    """Read-only fabric addresses."""

    def list(self, **params):
        return self._http.get(self._base_path, params=params or None)

    def get(self, address_id):
        return self._http.get(self._path(address_id))


class FabricTokens(BaseResource):
    """Subscriber, guest, invite, and embed token creation."""

    def __init__(self, http):
        super().__init__(http, "/api/fabric")

    def create_subscriber_token(self, **kwargs):
        return self._http.post(self._path("subscribers", "tokens"), body=kwargs)

    def refresh_subscriber_token(self, **kwargs):
        return self._http.post(self._path("subscribers", "tokens", "refresh"), body=kwargs)

    def create_invite_token(self, **kwargs):
        return self._http.post(self._path("subscriber", "invites"), body=kwargs)

    def create_guest_token(self, **kwargs):
        return self._http.post(self._path("guests", "tokens"), body=kwargs)

    def create_embed_token(self, **kwargs):
        return self._http.post(self._path("embeds", "tokens"), body=kwargs)


class FabricNamespace:
    """Fabric API namespace grouping all resource types."""

    def __init__(self, http):
        base = "/api/fabric/resources"

        # PUT-update resources
        self.swml_scripts = FabricResourcePUT(http, f"{base}/swml_scripts")
        self.relay_applications = FabricResourcePUT(http, f"{base}/relay_applications")
        self.call_flows = CallFlowsResource(http, f"{base}/call_flows")
        self.conference_rooms = ConferenceRoomsResource(http, f"{base}/conference_rooms")
        self.freeswitch_connectors = FabricResourcePUT(http, f"{base}/freeswitch_connectors")
        self.subscribers = SubscribersResource(http, f"{base}/subscribers")
        self.sip_endpoints = FabricResourcePUT(http, f"{base}/sip_endpoints")
        self.cxml_scripts = FabricResourcePUT(http, f"{base}/cxml_scripts")
        self.cxml_applications = CxmlApplicationsResource(http, f"{base}/cxml_applications")

        # PATCH-update resources
        # swml_webhooks and cxml_webhooks are normally auto-materialized by
        # phone_numbers.set_swml_webhook / set_cxml_webhook. Direct create
        # still works for backcompat but emits a DeprecationWarning.
        self.swml_webhooks = SwmlWebhooksResource(http, f"{base}/swml_webhooks")
        self.ai_agents = FabricResource(http, f"{base}/ai_agents")
        self.sip_gateways = FabricResource(http, f"{base}/sip_gateways")
        self.cxml_webhooks = CxmlWebhooksResource(http, f"{base}/cxml_webhooks")

        # Special resources
        self.resources = GenericResources(http, base)
        self.addresses = FabricAddresses(http, "/api/fabric/addresses")
        self.tokens = FabricTokens(http)
