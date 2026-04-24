"""Example: bind an inbound phone number to an SWML webhook (the happy path).

This is the simplest way to route a SignalWire phone number to a backend
that returns an SWML document per inbound call. You set ``call_handler``
on the phone number; the server auto-materializes a ``swml_webhook``
Fabric resource pointing at your URL. You do **not** need to create the
Fabric webhook resource manually; you do **not** call
``assign_phone_route``.

Set these env vars (or pass them directly to RestClient):
  SIGNALWIRE_PROJECT_ID   - your SignalWire project ID
  SIGNALWIRE_API_TOKEN    - your SignalWire API token
  SIGNALWIRE_SPACE        - your SignalWire space (e.g. example.signalwire.com)
  PHONE_NUMBER_SID        - SID of a phone number you own (pn-...)
  SWML_WEBHOOK_URL        - your backend's SWML endpoint
"""

import os

from signalwire.rest import RestClient, PhoneCallHandler


def main() -> None:
    pn_sid = os.environ["PHONE_NUMBER_SID"]
    webhook_url = os.environ["SWML_WEBHOOK_URL"]

    client = RestClient()

    # The typed helper — one line:
    print(f"Binding {pn_sid} to {webhook_url} ...")
    client.phone_numbers.set_swml_webhook(pn_sid, url=webhook_url)

    # The equivalent wire-level form (use this if you need unusual fields):
    #
    # client.phone_numbers.update(
    #     pn_sid,
    #     call_handler=PhoneCallHandler.RELAY_SCRIPT.value,
    #     call_relay_script_url=webhook_url,
    # )

    # Verify: the server auto-created a swml_webhook Fabric resource.
    pn = client.phone_numbers.get(pn_sid)
    print(f"  call_handler = {pn.get('call_handler')!r}")
    print(f"  call_relay_script_url = {pn.get('call_relay_script_url')!r}")
    print(f"  calling_handler_resource_id (server-derived) = "
          f"{pn.get('calling_handler_resource_id')!r}")

    # To route to something other than an SWML webhook, use:
    #   client.phone_numbers.set_cxml_webhook(sid, url=...)       # LAML / Twilio-compat
    #   client.phone_numbers.set_ai_agent(sid, agent_id=...)      # AI Agent
    #   client.phone_numbers.set_call_flow(sid, flow_id=...)      # Call Flow
    #   client.phone_numbers.set_relay_application(sid, name=...) # Named RELAY app
    #   client.phone_numbers.set_relay_topic(sid, topic=...)      # RELAY topic


if __name__ == "__main__":
    main()
