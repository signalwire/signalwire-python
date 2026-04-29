#!/usr/bin/env python3
"""
swmlservice_swaig_standalone.py

Proves that SWMLService — by itself, with NO AgentBase — can host SWAIG
functions and serve them on its own /swaig endpoint.

This is the path you take when you want a SWAIG-callable HTTP service that
isn't an `<ai>` agent: the SWAIG verb is a generic LLM-tool surface and
SWMLService is the host. AgentBase is just a SWMLService subclass that
*also* layers in prompts, AI config, dynamic config, and token validation.

Run:
    python swmlservice_swaig_standalone.py

Then exercise the endpoints:
    curl -u user:pass http://localhost:3000/standalone        # GET SWML doc
    curl -u user:pass http://localhost:3000/standalone/swaig \\
        -H 'Content-Type: application/json' \\
        -d '{"function":"lookup_competitor","argument":{"parsed":[{"competitor":"ACME"}]}}'

Or drive it through the SDK CLI without standing up the server:
    swaig-test swmlservice_swaig_standalone.py --list-tools
    swaig-test swmlservice_swaig_standalone.py --exec lookup_competitor --param competitor=ACME
"""

from signalwire.core.swml_service import SWMLService


class StandaloneSWAIG(SWMLService):
    """SWMLService that registers SWAIG tools and serves them on /swaig."""

    def __init__(self, host: str = "0.0.0.0", port: int = 3000):
        super().__init__(
            name="standalone-swaig",
            route="/standalone",
            host=host,
            port=port,
        )

        # 1. Build a minimal SWML document. Any verbs are fine — the SWAIG
        #    HTTP surface is independent of what the document contains.
        self.add_verb("answer", {})
        self.add_verb("hangup", {})

        # 2. Register a SWAIG function. `define_tool` lives on SWMLService,
        #    not just AgentBase. The handler receives parsed arguments plus
        #    the raw POST body.
        self.define_tool(
            name="lookup_competitor",
            description=(
                "Look up competitor pricing by company name. Use this when "
                "the user asks how a competitor's price compares to ours."
            ),
            parameters={
                "competitor": {
                    "type": "string",
                    "description": "The competitor's company name, e.g. 'ACME'.",
                }
            },
            handler=self.handle_lookup,
            secure=False,  # standalone services don't validate session tokens by default
        )

    def handle_lookup(self, args, raw_data):
        competitor = args.get("competitor", "<unknown>")
        return {
            "response": f"{competitor} pricing is $99/seat; we're $79/seat.",
        }


if __name__ == "__main__":
    StandaloneSWAIG().run()
