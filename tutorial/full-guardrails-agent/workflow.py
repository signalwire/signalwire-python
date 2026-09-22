"""
Penny's conversation, as configuration: which task is active, and what the
model may do while it is.

Two rules hold for every step, and both are enforced by ``scoped``:

1. The step names its tools explicitly. A step that names none would inherit
   the previous step's tools, so "no tools" is written ``[]``, never omitted.
2. The model cannot navigate. ``valid_steps`` and ``valid_contexts`` are empty,
   so the only way from one step to the next is a tool handler that has
   checked the real state and returned ``swml_change_step``/``_context``.

Copyright (c) 2025 SignalWire. Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from signalwire.core.contexts import ContextBuilder, Step

# Tools that may be offered in almost any step. Reading house facts or asking
# for a person can never change a booking, so they are safe to keep close by.
LOOKUPS = ["house_info", "request_human"]


# region: scoped
def scoped(step: Step, text: str, tools: list[str], history: str = "default") -> Step:
    """Give a step its task, its tools, and no way to leave on its own."""
    return (step.set_text(text)
            .set_functions(tools)
            .set_valid_steps([])
            .set_valid_contexts([])
            .set_history(history))
# endregion: scoped


def configure_workflow(builder: ContextBuilder) -> ContextBuilder:
    """Add Penny's four contexts to ``builder`` and validate them."""
    _triage(builder)
    _booking(builder)
    _manage(builder)
    _help(builder)
    builder.validate()
    return builder


# region: triage
def _triage(builder: ContextBuilder) -> None:
    ctx = builder.add_context("default")
    scoped(ctx.add_step("triage"),
           "The greeting has already been played; don't repeat it. The host stand is "
           "${global_data.host_stand} right now. As soon as the caller says what they want, "
           "act on it without asking again: for a new reservation call start_booking; to "
           "check, change or cancel one they already have, call manage_booking. Answer "
           "general questions with house_info. If they ask for a person, call "
           "request_human. If they're done, call finish.",
           ["start_booking", "manage_booking", *LOOKUPS, "finish"])
    ctx.set_initial_step("triage")
# endregion: triage


# region: booking
def _booking(builder: ContextBuilder) -> None:
    ctx = builder.add_context("booking")

    # region: collect
    # Gather mode asks one question at a time and stores the answers under
    # global_data.booking_request. While it runs, the only tools are
    # gather_submit and the escape hatches each question lists.
    collect = scoped(ctx.add_step("collect"), "Take the reservation details.", [])
    collect.set_gather_info(
        output_key="booking_request",
        completion_action="search",
        prompt="You're taking a reservation. Ask each question in turn, briefly.")
    collect.add_gather_question(
        key="party_size", question="How many people will be dining?",
        type="integer", functions=LOOKUPS)
    collect.add_gather_question(
        key="date", question="What date would you like?", functions=LOOKUPS,
        prompt="Submit the caller's own words for the date, such as 'Friday' or "
               "'the 26th'. Do not turn it into a calendar date yourself.")
    collect.add_gather_question(
        key="time", question="What time would you like?", functions=LOOKUPS,
        prompt="Submit the time in digits, such as '7:30 PM'.")
    collect.add_gather_question(
        key="name", question="What name should the reservation be under?",
        confirm=True, functions=LOOKUPS)
    # endregion: collect

    # region: booking-steps
    scoped(ctx.add_step("search"),
           "The details are collected. Call find_tables now. Say nothing about "
           "availability until it returns. If the caller changes a detail, pass only "
           "that detail to find_tables.",
           ["find_tables", *LOOKUPS])
    scoped(ctx.add_step("choose"),
           "Offer the options from the last find_tables result by number, and nothing "
           "else. When the caller picks one, call hold_table with its number. If they "
           "want a different time, date or party size, call find_tables with only what "
           "changed.",
           ["hold_table", "find_tables", *LOOKUPS])
    scoped(ctx.add_step("review"),
           "A table is on hold. Read the proposal back as the last tool result gave it "
           "and ask the caller to confirm. Only if they clearly say yes, call "
           "confirm_booking with the proposal's revision number. If they want a change, "
           "call find_tables with only what changed.",
           ["confirm_booking", "find_tables", *LOOKUPS])
    scoped(ctx.add_step("booked"),
           "The reservation is confirmed: ${global_data.booking.summary}. The "
           "confirmation code is ${global_data.booking.code_spoken}. Make sure the caller "
           "has the code, offer to text the details with send_confirmation_text, and "
           "answer last questions with house_info. When they're done, call finish.",
           ["send_confirmation_text", "house_info", "finish"])
    ctx.set_initial_step("collect")
    # endregion: booking-steps
# endregion: booking


# region: manage
def _manage(builder: ContextBuilder) -> None:
    ctx = builder.add_context("manage")
    scoped(ctx.add_step("verify"),
           "Ask for the six-character confirmation code and the last name on the "
           "reservation, then call verify_reservation. There is no other way to see a "
           "reservation, and you must not describe one before it is verified.",
           ["verify_reservation", *LOOKUPS])
    # "hide" drops the verification back-and-forth from the model's view; the one
    # thing this step needs is projected into its text instead.
    scoped(ctx.add_step("details"),
           "The caller verified this reservation: ${global_data.manage.summary}, status "
           "${global_data.manage.status}. Tell them the details. If they want to cancel, "
           "call request_cancel. To change a reservation, they can cancel it and book a "
           "new one. When they're done, call finish.",
           ["request_cancel", *LOOKUPS, "finish"], history="hide")
    scoped(ctx.add_step("confirm_cancel"),
           "Read back the cancellation as the last tool result gave it and ask if they're "
           "sure. Only if they clearly say yes, call confirm_cancel with its revision "
           "number. If they change their mind, call keep_reservation.",
           ["confirm_cancel", "keep_reservation", *LOOKUPS])
    scoped(ctx.add_step("cancelled"),
           "The reservation is cancelled. Answer last questions with house_info, then "
           "call finish.",
           ["house_info", "finish"])
    scoped(ctx.add_step("locked"),
           "Reservation lookups are locked for the rest of this call. Offer to connect "
           "the caller with a person (request_human), or call finish.",
           ["request_human", "finish"])
    ctx.set_initial_step("verify")
# endregion: manage


# region: help
def _help(builder: ContextBuilder) -> None:
    ctx = builder.add_context("help")
    # region: take-message
    take = scoped(ctx.add_step("take_message"), "Take a message for the host stand.", [])
    take.set_gather_info(
        output_key="message",
        completion_action="save_message",
        prompt="Nobody is at the host stand, so you're taking a message for them.")
    take.add_gather_question(key="name", question="What's your name?", functions=["finish"])
    take.add_gather_question(
        key="callback", question="What's the best number to call you back on?",
        confirm=True, functions=["finish"])
    take.add_gather_question(
        key="body", question="What would you like me to pass along?", functions=["finish"])
    # endregion: take-message

    scoped(ctx.add_step("save_message"),
           "Call save_message now. Don't tell the caller it's saved until it returns. If "
           "it asks for a correction, ask the caller and pass only the corrected detail.",
           ["save_message"])
    scoped(ctx.add_step("message_saved"),
           "The message is saved. Tell the caller the host stand will call them back, "
           "answer last questions with house_info, then call finish.",
           ["house_info", "finish"])
    ctx.set_initial_step("take_message")
# endregion: help
