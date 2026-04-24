"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
PhoneCallHandler — enum of ``call_handler`` values accepted by phone_numbers.update.

Named ``PhoneCallHandler`` (not ``CallHandler``) to avoid colliding with the
RELAY client's inbound-call-handler callback type.

Setting a phone number's ``call_handler`` + the handler-specific companion
field routes inbound calls and auto-materializes the matching Fabric
resource on the server. See the high-level helpers on
:class:`signalwire.rest.namespaces.phone_numbers.PhoneNumbersResource`.
"""

from enum import Enum


class PhoneCallHandler(str, Enum):
    """``call_handler`` values for ``phone_numbers.update``.

    Each value is a ``str`` subclass, so passing the enum member directly into
    ``phone_numbers.update(..., call_handler=PhoneCallHandler.RELAY_SCRIPT)``
    serializes to the wire value without ``.value`` indirection.

    ================= ============================= =======================
    Enum member       Companion field (required)    Auto-creates resource
    ================= ============================= =======================
    RELAY_SCRIPT      call_relay_script_url         swml_webhook
    LAML_WEBHOOKS     call_request_url              cxml_webhook
    LAML_APPLICATION  call_laml_application_id      cxml_application
    AI_AGENT          call_ai_agent_id              ai_agent
    CALL_FLOW         call_flow_id                  call_flow
    RELAY_APPLICATION call_relay_application        relay_application
    RELAY_TOPIC       call_relay_topic              (routes via RELAY)
    RELAY_CONTEXT     call_relay_context            (legacy, prefer topic)
    RELAY_CONNECTOR   (connector config)            (internal)
    VIDEO_ROOM        call_video_room_id            (routes to Video API)
    DIALOGFLOW        call_dialogflow_agent_id      (none)
    ================= ============================= =======================

    Note: ``LAML_WEBHOOKS`` (wire value ``laml_webhooks``) produces a **cXML**
    handler, not a generic webhook. For SWML, use ``RELAY_SCRIPT``.
    """

    RELAY_SCRIPT = "relay_script"
    LAML_WEBHOOKS = "laml_webhooks"
    LAML_APPLICATION = "laml_application"
    AI_AGENT = "ai_agent"
    CALL_FLOW = "call_flow"
    RELAY_APPLICATION = "relay_application"
    RELAY_TOPIC = "relay_topic"
    RELAY_CONTEXT = "relay_context"
    RELAY_CONNECTOR = "relay_connector"
    VIDEO_ROOM = "video_room"
    DIALOGFLOW = "dialogflow"
