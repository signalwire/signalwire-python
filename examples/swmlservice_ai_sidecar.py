#!/usr/bin/env python3
"""
swmlservice_ai_sidecar.py

Proves that SWMLService can emit the `ai_sidecar` verb, register SWAIG
tools the sidecar's LLM can call, and dispatch them end-to-end — without
any AgentBase code path.

The `ai_sidecar` verb runs an AI listener alongside an in-progress call
(real-time copilot, transcription analyzer, compliance monitor, etc.). It
is NOT an agent — it does not own the call. So the right host is
SWMLService, not AgentBase.

Run:
    python swmlservice_ai_sidecar.py

What this serves:
    GET  /sales-sidecar           → SWML doc with the ai_sidecar verb
    POST /sales-sidecar/swaig     → SWAIG tool dispatch (used by the sidecar's LLM)

Drive the SWAIG path through the SDK CLI:
    swaig-test swmlservice_ai_sidecar.py --list-tools
    swaig-test swmlservice_ai_sidecar.py --exec lookup_competitor --param competitor=ACME
"""

from signalwire.core.swml_service import SWMLService


class SalesSidecar(SWMLService):
    """SWMLService that emits <ai_sidecar> and hosts the tools its LLM calls."""

    def __init__(
        self,
        public_url: str = "https://your-host.example.com/sales-sidecar",
        host: str = "0.0.0.0",
        port: int = 3000,
    ):
        super().__init__(
            name="sales-sidecar",
            route="/sales-sidecar",
            host=host,
            port=port,
        )

        # 1. Emit any SWML — including ai_sidecar. SWMLService's add_verb /
        #    add_verb_to_section accept arbitrary verb dicts, so new platform
        #    verbs work without an SDK release.
        self.add_verb("answer", {})
        self.add_verb_to_section(
            "main",
            "ai_sidecar",
            {
                "prompt": (
                    "You are a real-time sales copilot. Listen to the call "
                    "and surface competitor pricing comparisons when relevant."
                ),
                "lang": "en-US",
                "direction": ["remote-caller", "local-caller"],
                # Where the sidecar POSTs lifecycle/transcription events.
                # Optional — skip if you don't need an event sink.
                "url": f"{public_url}/events",
                # Where the sidecar's LLM POSTs SWAIG tool calls. This
                # SDK's /swaig route is what answers them.
                "SWAIG": {
                    "defaults": {"web_hook_url": f"{public_url}/swaig"},
                },
            },
        )
        self.add_verb("hangup", {})

        # 2. Register tools the sidecar's LLM can call. Same `define_tool`
        #    you'd use on AgentBase — it lives on SWMLService.
        self.define_tool(
            name="lookup_competitor",
            description=(
                "Look up competitor pricing by company name. The sidecar "
                "should call this whenever the caller mentions a competitor."
            ),
            parameters={
                "competitor": {
                    "type": "string",
                    "description": "The competitor's company name, e.g. 'ACME'.",
                }
            },
            handler=lambda args, raw: {
                "response": (
                    f"Pricing for {args.get('competitor', '<unknown>')}: "
                    "$99/seat. Our equivalent plan is $79/seat with the same SLA."
                ),
            },
            secure=False,
        )

        # 3. (Optional) Mount an event sink for ai_sidecar lifecycle events
        #    at POST /sales-sidecar/events. Comment this out if you don't
        #    need it. mod_openai POSTs each event as JSON.
        self.register_routing_callback(self.on_sidecar_event, path="/events")

    def on_sidecar_event(self, request, body):
        # body is a dict like {"type": "transcription", "text": "...", ...}
        event_type = body.get("type", "<unknown>")
        print(f"[sidecar event] type={event_type} body={body}")
        return None  # any non-redirect response


if __name__ == "__main__":
    SalesSidecar().run()
