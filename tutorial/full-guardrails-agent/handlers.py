"""
Penny's tools. Each handler asks the reservation book to do something, then
tells two audiences what happened, separately:

* the model gets ``tool_result`` (what is true) and ``tool_prompt`` (what to say);
* the platform gets actions: step changes, session data, UI events, call control.

Nothing here trusts the model's claim that something happened. Handlers check
the store; the store checks the rules.

Copyright (c) 2025 SignalWire. Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from __future__ import annotations

import functools
import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from signalwire.core.function_result import FunctionResult

from reservations import (
    HOUSE_FACTS,
    LargePartyError,
    LockedOutError,
    PolicyError,
    ReservationStore,
    spoken_code,
    spoken_date,
    spoken_time,
)

log = logging.getLogger("penny")

GOODBYE = "Thanks for calling The Copper Pot. Have a wonderful evening!"
TRANSFER_NOTICE = "One moment, I'm connecting you with our host stand."

Handler = Callable[["PennyHandlers", dict[str, Any], dict[str, Any]], FunctionResult]


@dataclass(frozen=True)
class Settings:
    """Server configuration. The model can't choose any of these values."""

    host_number: str | None = None   # where request_human may send a call
    sms_from: str | None = None      # the restaurant's texting number


# region: guarded
def guarded(method: Handler) -> Handler:
    """Turn refusals into facts for the model, and never let a crash sound like success."""

    @functools.wraps(method)
    def wrapper(self: PennyHandlers, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        try:
            if not isinstance(args, dict) or not isinstance(raw_data, dict):
                raise PolicyError("The request was malformed.", "Ask the caller to say that again.")
            return method(self, args, raw_data)
        except PolicyError as refusal:
            return FunctionResult(tool_result=refusal.fact, tool_prompt=refusal.ask)
        except MissingCallContext:
            return FunctionResult(tool_result="Nothing was done: the request had no call context.",
                                  tool_prompt="Apologize and offer to take a message.")
        except Exception:
            log.exception("tool %s failed", method.__name__)
            return FunctionResult(
                tool_result="The system couldn't finish that, so the outcome is unknown.",
                tool_prompt="Don't say it worked. Apologize and offer to try again.")

    return wrapper
# endregion: guarded


class MissingCallContext(Exception):
    """A tool request arrived without the call it belongs to."""


class PennyHandlers:
    def __init__(self, store: ReservationStore, settings: Settings) -> None:
        self.store = store
        self.settings = settings

    @staticmethod
    def _call_id(raw_data: dict[str, Any]) -> str:
        call_id = raw_data.get("call_id")
        if not isinstance(call_id, str) or not call_id:
            raise MissingCallContext()
        return call_id

    @staticmethod
    def _gathered(raw_data: dict[str, Any], key: str) -> dict[str, Any]:
        """Answers gather mode stored in global_data. Caller-supplied, so untrusted."""
        value = (raw_data.get("global_data") or {}).get(key)
        return value if isinstance(value, dict) else {}

    # ── Routing: code, not the model, moves the conversation ────────────────

    # region: start-booking
    @guarded
    def start_booking(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        self.store.reset_request(self._call_id(raw_data))
        return (FunctionResult(tool_result="A new reservation has been started.",
                               tool_prompt="Tell the caller you'll take a few details.")
                .update_global_data({"booking": {}, "booking_request": {}})
                .swml_change_context("booking"))
    # endregion: start-booking

    @guarded
    def manage_booking(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        self._call_id(raw_data)
        return (FunctionResult(tool_result="Looking up an existing reservation.",
                               tool_prompt="Ask for the confirmation code and the last name on it.")
                .update_global_data({"manage": {}})
                .swml_change_context("manage"))

    @guarded
    def house_info(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        fact = HOUSE_FACTS.get(args.get("topic")) if isinstance(args.get("topic"), str) else None
        if fact is None:
            return FunctionResult(tool_result="There's no information on that topic.",
                                  tool_prompt="Say you don't have that information, then carry on.")
        return FunctionResult(tool_result=fact,
                              tool_prompt="Answer with this fact in your own words, then carry on.")

    # ── Booking ─────────────────────────────────────────────────────────────

    # region: find-tables
    @guarded
    def find_tables(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        call_id = self._call_id(raw_data)
        # The request so far: the last search on this call, or, for the first
        # search, the answers gather mode collected
        current = self.store.current_request(call_id) or self._gathered(raw_data, "booking_request")

        def detail(key: str) -> Any:
            # A correction passed as an argument changes only that detail.
            return args[key] if args.get(key) not in (None, "") else current.get(key)

        try:
            request, options = self.store.find_options(
                call_id, detail("party_size"), detail("date"), detail("time"), detail("name"))
        except LargePartyError as refusal:
            return FunctionResult(tool_result=refusal.fact, tool_prompt=refusal.ask)

        if options:
            listed = "; ".join(option.spoken() for option in options)
            result = FunctionResult(
                tool_result=f"Open for {request.party_size} on {spoken_date(request.day)}: {listed}.",
                tool_prompt="Offer these options by number. When the caller picks one, "
                            "call hold_table with its number.")
        else:
            result = FunctionResult(
                tool_result=f"Nothing is open for {request.party_size} on "
                            f"{spoken_date(request.day)} within an hour of "
                            f"{spoken_time(request.start)}. Seatings run 5 PM to 8:30 PM.",
                tool_prompt="Say so, and ask whether another time or date would work. "
                            "Then call find_tables with only what changed.")
        return (result
                .update_global_data({"booking": {"request": request.spoken()}})
                .swml_change_step("choose")
                .swml_user_event({"type": "options_offered", "day": request.day.isoformat(),
                                  "options": [{"number": o.number, "time": spoken_time(o.start)}
                                              for o in options]}))
    # endregion: find-tables

    # region: hold-table
    @guarded
    def hold_table(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        call_id = self._call_id(raw_data)
        proposal = self.store.hold_option(call_id, args.get("option"))
        return (FunctionResult(
                    tool_result=f"On hold for five minutes: {proposal.spoken()}. "
                                f"This is proposal revision {proposal.revision}.",
                    tool_prompt="Read the proposal back and ask the caller to confirm it. "
                                "If they clearly say yes, call confirm_booking with revision "
                                f"{proposal.revision}. If they want a change, call "
                                "find_tables with only what changed.")
                .update_global_data({"booking": {"proposal": proposal.spoken(),
                                                 "revision": proposal.revision}})
                .swml_change_step("review")
                .swml_user_event({"type": "table_held", "revision": proposal.revision,
                                  "day": proposal.day.isoformat(),
                                  "time": spoken_time(proposal.start),
                                  "party_size": proposal.party_size}))
    # endregion: hold-table

    # region: confirm-booking
    @guarded
    def confirm_booking(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        call_id = self._call_id(raw_data)
        booking = self.store.confirm(call_id, args.get("revision"))
        code = spoken_code(booking.code)
        return (FunctionResult(
                    tool_result=f"Confirmed: {booking.spoken()}. Confirmation code: {code}.",
                    tool_prompt="Tell the caller it's booked and read the confirmation code "
                                "slowly, one character at a time. Then offer to text the details.")
                .update_global_data({"booking": {"summary": booking.spoken(), "code_spoken": code}})
                .swml_change_step("booked")
                .swml_user_event({"type": "booking_confirmed", "code": booking.code,
                                  "day": booking.day.isoformat(),
                                  "time": spoken_time(booking.start),
                                  "party_size": booking.party_size}))
    # endregion: confirm-booking

    # region: send-text
    @guarded
    def send_confirmation_text(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        call_id = self._call_id(raw_data)
        booking = self.store.booking_for_call(call_id)
        if booking is None:
            raise PolicyError("This call hasn't booked a reservation.", "Say there's nothing to text yet.")
        if not self.settings.sms_from:
            raise PolicyError("Texting isn't set up at the restaurant.",
                              "Apologize, and make sure they have the confirmation code.")
        # The destination is the number this call comes from. The model can't supply one.
        caller = str(raw_data.get("caller_id_num") or "")
        if not re.fullmatch(r"\+[1-9]\d{9,14}", caller):
            raise PolicyError("The number this call comes from can't receive a text.",
                              "Say you can't text this number, and make sure they have the code.")
        # The platform sends the text after this returns, so "requested" is all
        # that can be said. Repeats within a short window are duplicates.
        decision = self.store.request_sms(booking.code)
        if decision == "duplicate":
            return FunctionResult(
                tool_result="A text for this booking was requested moments ago.",
                tool_prompt="Tell the caller it's on its way. If it hasn't arrived in a couple "
                            "of minutes, you can send it again.")
        if decision == "limit":
            raise PolicyError("This booking has been texted as many times as allowed.",
                              "Say you can't text it again, and make sure they have the code.")
        body = (f"The Copper Pot: {booking.spoken()}. Confirmation code {booking.code}. "
                "Call us to change or cancel.")
        return (FunctionResult(
                    tool_result=f"Asked for the details to be texted to the number ending in "
                                f"{caller[-4:]}.",
                    tool_prompt="Tell the caller the text is on its way.")
                .send_sms(to_number=caller, from_number=self.settings.sms_from, body=body))
    # endregion: send-text

    # ── An existing reservation ─────────────────────────────────────────────

    # region: verify-reservation
    @guarded
    def verify_reservation(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        call_id = self._call_id(raw_data)
        try:
            found = self.store.verify(call_id, args.get("confirmation_code", ""),
                                      args.get("last_name", ""))
        except LockedOutError as refusal:
            return (FunctionResult(tool_result=refusal.fact, tool_prompt=refusal.ask)
                    .swml_change_step("locked"))
        return (FunctionResult(tool_result=f"Verified: {found.spoken()}. Status: {found.status}.",
                               tool_prompt="Tell the caller the details and ask what they'd like to do.")
                .update_global_data({"manage": {"summary": found.spoken(), "status": found.status}})
                .swml_change_step("details")
                .swml_user_event({"type": "reservation_verified", "status": found.status}))
    # endregion: verify-reservation

    # region: cancel
    @guarded
    def request_cancel(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        call_id = self._call_id(raw_data)
        found, revision = self.store.request_cancel(call_id)
        return (FunctionResult(
                    tool_result=f"Ready to cancel {found.spoken()}. "
                                f"This is cancellation revision {revision}.",
                    tool_prompt="Read that back and ask if they're sure. If they clearly say "
                                f"yes, call confirm_cancel with revision {revision}. If not, "
                                "call keep_reservation.")
                .swml_change_step("confirm_cancel"))

    @guarded
    def confirm_cancel(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        call_id = self._call_id(raw_data)
        cancelled = self.store.confirm_cancel(call_id, args.get("revision"))
        return (FunctionResult(tool_result=f"Cancelled: {cancelled.spoken()}.",
                               tool_prompt="Tell the caller it's cancelled, then ask if there's "
                                           "anything else.")
                .update_global_data({"manage": {"summary": cancelled.spoken(), "status": "cancelled"}})
                .swml_change_step("cancelled")
                .swml_user_event({"type": "reservation_cancelled"}))
    # endregion: cancel

    @guarded
    def keep_reservation(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        call_id = self._call_id(raw_data)
        kept = self.store.keep_reservation(call_id)
        return (FunctionResult(tool_result=f"Nothing changed: {kept.spoken()} is still booked.",
                               tool_prompt="Tell the caller their reservation is unchanged.")
                .swml_change_step("details"))

    # ── People, messages and endings ────────────────────────────────────────

    # region: request-human
    @guarded
    def request_human(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        self._call_id(raw_data)
        if self.settings.host_number and self.store.host_stand_open():
            # say() is an action, so it finishes before connect() runs. The
            # response text is spoken by the model on its own schedule and
            # could be cut off by the transfer.
            return (FunctionResult(tool_result="The call is being transferred to the host stand.",
                                   tool_prompt="Say nothing more; the transfer notice is playing.")
                    .say(TRANSFER_NOTICE)
                    .connect(self.settings.host_number, final=True))
        return (FunctionResult(tool_result="Nobody is at the host stand right now.",
                               tool_prompt="Tell the caller nobody is at the host stand, and "
                                           "that you'll take a message for them.")
                .update_global_data({"message": {}})
                .swml_change_context("help"))
    # endregion: request-human

    # region: save-message
    @guarded
    def save_message(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        call_id = self._call_id(raw_data)
        taken = self._gathered(raw_data, "message")

        def detail(key: str) -> str:
            return str(args[key] if args.get(key) not in (None, "") else taken.get(key) or "")

        saved = self.store.save_message(call_id, detail("name"), detail("callback"), detail("body"))
        return (FunctionResult(
                    tool_result=f"Message saved for the host stand, with a callback number "
                                f"ending in {saved['callback'][-4:]}.",
                    tool_prompt="Tell the caller the host stand will call them back.")
                .swml_change_step("message_saved")
                .swml_user_event({"type": "message_taken"}))
    # endregion: save-message

    # region: finish
    @guarded
    def finish(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        # The goodbye is a say() action, not response text: actions run in order,
        # so the caller hears all of it before hangup() ends the call.
        return (FunctionResult(tool_result="The goodbye is playing and the call will end.",
                               tool_prompt="Say nothing more.")
                .say(GOODBYE)
                .hangup())
    # endregion: finish

    # region: capture-call
    def capture_call(self, call_log: list[dict[str, Any]], raw_data: dict[str, Any]) -> None:
        """on_call_end: record what the store says happened, not what the transcript says."""
        call_id = raw_data.get("call_id") if isinstance(raw_data, dict) else None
        if not isinstance(call_id, str) or not call_id:
            log.warning("call ended without a call id; nothing recorded")
            return
        outcome = self.store.record_call_end(call_id, len(call_log or []))
        log.info("call %s ended: %s", call_id, outcome)
    # endregion: capture-call
