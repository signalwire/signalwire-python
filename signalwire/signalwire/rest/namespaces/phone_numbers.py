"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Phone Numbers namespace — list, search, purchase, get, update, release, bind.
"""

from typing import Optional

from .._base import CrudResource
from ..call_handler import PhoneCallHandler


class PhoneNumbersResource(CrudResource):
    """Phone number management.

    Supports the standard CRUD surface plus typed helpers for binding an
    inbound call to a handler (SWML webhook, cXML webhook, AI agent, call
    flow, RELAY application/topic). The binding model is: set
    ``call_handler`` + the handler-specific companion field on the phone
    number; the server auto-materializes the matching Fabric resource.
    See :mod:`signalwire.rest.call_handler` for the enum, and the
    porting-sdk's ``phone-binding.md`` for the full model.
    """

    _update_method = "PUT"

    def __init__(self, http):
        super().__init__(http, "/api/relay/rest/phone_numbers")

    def search(self, **params):
        return self._http.get(self._path("search"), params=params or None)

    # -- Typed binding helpers -------------------------------------------
    #
    # Each helper is a one-line wrapper over ``update`` with the right
    # ``call_handler`` value and companion field already set. Pass through
    # extra kwargs for cases the helper doesn't name explicitly (e.g.
    # ``call_fallback_url`` on cXML webhooks).

    def set_swml_webhook(self, resource_id: str, url: str, **extra) -> dict:
        """Route inbound calls to an SWML webhook URL.

        Your backend returns an SWML document per call. The server
        auto-creates a ``swml_webhook`` Fabric resource keyed off this URL.
        """
        return self.update(
            resource_id,
            call_handler=PhoneCallHandler.RELAY_SCRIPT.value,
            call_relay_script_url=url,
            **extra,
        )

    def set_cxml_webhook(
        self,
        resource_id: str,
        url: str,
        fallback_url: Optional[str] = None,
        status_callback_url: Optional[str] = None,
        **extra,
    ) -> dict:
        """Route inbound calls to a cXML (Twilio-compat / LAML) webhook.

        Despite the wire value ``laml_webhooks`` being plural, this creates
        a single ``cxml_webhook`` Fabric resource. ``fallback_url`` is used
        when the primary URL fails; ``status_callback_url`` receives call
        status updates.
        """
        body = {
            "call_handler": PhoneCallHandler.LAML_WEBHOOKS.value,
            "call_request_url": url,
        }
        if fallback_url is not None:
            body["call_fallback_url"] = fallback_url
        if status_callback_url is not None:
            body["call_status_callback_url"] = status_callback_url
        body.update(extra)
        return self.update(resource_id, **body)

    def set_cxml_application(self, resource_id: str, application_id: str, **extra) -> dict:
        """Route inbound calls to an existing cXML application by ID."""
        return self.update(
            resource_id,
            call_handler=PhoneCallHandler.LAML_APPLICATION.value,
            call_laml_application_id=application_id,
            **extra,
        )

    def set_ai_agent(self, resource_id: str, agent_id: str, **extra) -> dict:
        """Route inbound calls to an AI Agent Fabric resource by ID."""
        return self.update(
            resource_id,
            call_handler=PhoneCallHandler.AI_AGENT.value,
            call_ai_agent_id=agent_id,
            **extra,
        )

    def set_call_flow(
        self,
        resource_id: str,
        flow_id: str,
        version: Optional[str] = None,
        **extra,
    ) -> dict:
        """Route inbound calls to a Call Flow by ID.

        ``version`` accepts ``"working_copy"`` or ``"current_deployed"``
        (server default when omitted).
        """
        body = {
            "call_handler": PhoneCallHandler.CALL_FLOW.value,
            "call_flow_id": flow_id,
        }
        if version is not None:
            body["call_flow_version"] = version
        body.update(extra)
        return self.update(resource_id, **body)

    def set_relay_application(self, resource_id: str, name: str, **extra) -> dict:
        """Route inbound calls to a named RELAY application."""
        return self.update(
            resource_id,
            call_handler=PhoneCallHandler.RELAY_APPLICATION.value,
            call_relay_application=name,
            **extra,
        )

    def set_relay_topic(
        self,
        resource_id: str,
        topic: str,
        status_callback_url: Optional[str] = None,
        **extra,
    ) -> dict:
        """Route inbound calls to a RELAY topic (client subscription)."""
        body = {
            "call_handler": PhoneCallHandler.RELAY_TOPIC.value,
            "call_relay_topic": topic,
        }
        if status_callback_url is not None:
            body["call_relay_topic_status_callback_url"] = status_callback_url
        body.update(extra)
        return self.update(resource_id, **body)
