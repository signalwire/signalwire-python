#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Per-Question Function Whitelist Demo (gather_info)

This example exists to teach one specific gotcha: while a step's gather_info
is asking questions, ALL of the step's other functions are forcibly
deactivated. The only callable tools during a gather question are:

  - `gather_submit` (the native answer-submission tool, always active)
  - Whatever names you list in that question's `functions=[...]` arg

`next_step` and `change_context` are also filtered out — the model literally
cannot navigate away until the gather completes. This is by design: it
forces a tight ask → submit → next-question loop.

If a question needs to call out to a tool — for example, to validate an
email format, geocode a ZIP, or look up something from an external service
— you must list that tool name in the question's `functions` arg. The
function is active ONLY for that question.

Below: a customer-onboarding gather flow where each question unlocks a
different validation tool, and where the step's own non-gather tools
(escalate_to_human, lookup_existing_account) are LOCKED OUT during gather
because they aren't whitelisted on any question.

Run this file to see the resulting SWML.
"""

import json

from signalwire import AgentBase


class GatherPerQuestionFunctionsAgent(AgentBase):
    def __init__(self):
        super().__init__(name="gather_per_question_functions_demo", route="/")

        # Tools that the step would normally have available — but during
        # gather questioning, they're all locked out unless they appear in
        # a question's `functions` whitelist.
        self.define_tool(
            name="validate_email",
            description="Validate that an email address is well-formed and deliverable",
            parameters={"email": {"type": "string"}},
            handler=lambda args, raw_data: "valid",
        )
        self.define_tool(
            name="geocode_zip",
            description="Look up the city/state for a US ZIP code",
            parameters={"zip": {"type": "string"}},
            handler=lambda args, raw_data: '{"city":"...","state":"..."}',
        )
        self.define_tool(
            name="check_age_eligibility",
            description="Verify the customer is old enough for the product",
            parameters={"age": {"type": "integer"}},
            handler=lambda args, raw_data: "eligible",
        )
        # These tools are NOT whitelisted on any gather question. They are
        # registered on the agent and active outside the gather, but during
        # the gather they cannot be called — gather mode locks them out.
        self.define_tool(
            name="escalate_to_human",
            description="Transfer the conversation to a live agent",
            parameters={},
            handler=lambda args, raw_data: "transferred",
        )
        self.define_tool(
            name="lookup_existing_account",
            description="Search for an existing account by email",
            parameters={"email": {"type": "string"}},
            handler=lambda args, raw_data: "not found",
        )

        # Build a single-context agent with one onboarding step.
        contexts = self.define_contexts()
        ctx = contexts.add_context("default")

        ctx.add_step("onboard") \
            .set_text(
                "Onboard a new customer by collecting their details. Use "
                "gather_info to ask one question at a time. Each question "
                "may unlock a specific validation tool — only that tool "
                "and gather_submit are callable while answering it."
            ) \
            .set_functions([
                # Outside of the gather (which is the entire step here),
                # these would be available. During the gather they are
                # forcibly hidden in favor of the per-question whitelists.
                "escalate_to_human",
                "lookup_existing_account",
            ]) \
            .set_gather_info(
                output_key="customer",
                completion_action="next_step",
                prompt=(
                    "I'll need to collect a few details to set up your "
                    "account. I'll ask one question at a time."
                ),
            ) \
            .add_gather_question(
                key="email",
                question="What's your email address?",
                confirm=True,
                # Only validate_email + gather_submit are callable here.
                functions=["validate_email"],
            ) \
            .add_gather_question(
                key="zip",
                question="What's your ZIP code?",
                # Only geocode_zip + gather_submit are callable here.
                functions=["geocode_zip"],
            ) \
            .add_gather_question(
                key="age",
                question="How old are you?",
                type="integer",
                # Only check_age_eligibility + gather_submit are callable here.
                functions=["check_age_eligibility"],
            ) \
            .add_gather_question(
                key="referral_source",
                question="How did you hear about us?",
                # No functions arg → only gather_submit is callable.
                # The model cannot validate, lookup, escalate — nothing.
                # This is the right pattern when a question needs no tools.
            )

        # A simple confirmation step the gather auto-advances into.
        ctx.add_step("confirm") \
            .set_text(
                "Read the collected info back to the customer and "
                "confirm everything is correct."
            ) \
            .set_functions([]) \
            .set_end(True)


if __name__ == "__main__":
    agent = GatherPerQuestionFunctionsAgent()
    swml = agent.get_app().render_swml()
    print(json.dumps(swml, indent=2))
