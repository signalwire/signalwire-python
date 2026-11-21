"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The task packs: Appointments against a calendar of the test's own, and
Messages into an inbox, through the CallSimulator.
"""

from __future__ import annotations

from typing import Any

import pytest

from signalwire import AgentBase
from signalwire.operations import (
    Appointment,
    Appointments,
    Message,
    Messages,
    Operations,
    ServiceAgent,
    Slot,
    WriteFailed,
)
from signalwire.testing import CallSimulator


def said(args: dict[str, Any]) -> dict[str, Any]:
    return {**args, "data_supplied_by_user": True}


class Calendar:
    def __init__(self) -> None:
        self.open = {"s1": "Tuesday at 2 pm", "s2": "Wednesday at 10 am"}
        self.booked: dict[str, str] = {"a1": "your cleaning on Friday at 9 am"}
        self.log: list[tuple[Any, ...]] = []

    def openings(self, call: Any, when: str, kind: str | None) -> list[Slot]:
        self.log.append(("openings", when, kind))
        return [Slot(i, label) for i, label in self.open.items()] if "week" in when else []

    def book(self, call: Any, slot: Slot, kind: str | None, note: str | None) -> None:
        if slot.id == "s2":
            raise WriteFailed("that time was just taken")
        self.log.append(("book", slot, kind, note))

    async def mine(self, call: Any) -> list[Any]:
        return [Appointment(i, label) for i, label in self.booked.items()]

    def move(self, call: Any, appointment: Appointment, slot: Slot) -> None:
        self.log.append(("move", appointment.id, slot.id))

    def cancel(self, call: Any, appointment: Appointment) -> None:
        self.log.append(("cancel", appointment.id))


def desk(cal: Calendar, **kwargs: Any) -> ServiceAgent:
    agent = ServiceAgent("dentist", role="You answer the phone for a dental practice.", suppress_logs=True)
    Appointments(openings=cal.openings, book=cal.book, booked=cal.mine, move=cal.move, cancel=cal.cancel,
                 kinds=["cleaning", "check-up"], **kwargs).add_to(agent)
    return agent


def test_find_openings_then_book_one() -> None:
    cal = Calendar()
    sim = CallSimulator(desk(cal))
    found = sim.call("find_openings", {"when": "next week", "kind": "cleaning"})
    assert found.response == "Open: Tuesday at 2 pm (slot s1) and Wednesday at 10 am (slot s2)"
    assert found.tool_prompt == "Offer them these, and book the one they choose with book_appointment."
    asked = sim.call("book_appointment", said({"slot": "s1", "kind": "cleaning", "note": "sensitive teeth"}))
    assert asked.ran and sim.step == "confirm"
    assert sim.global_data["ops"]["waiting"]["read_back"] == "Book Tuesday at 2 pm for cleaning. Shall I go ahead?"
    sim.caller("yes")
    done = sim.call("confirm_change", {"change": "book_appointment"})
    assert done.response.startswith("Done. It's booked: Tuesday at 2 pm.")
    assert cal.log[-1] == ("book", Slot("s1", "Tuesday at 2 pm"), "cleaning", "sensitive teeth")


def test_only_a_time_found_open_can_be_booked() -> None:
    sim = CallSimulator(desk(Calendar()))
    out = sim.call("book_appointment", said({"slot": "s9"}))
    assert out.response == "Nothing is changed: s9 isn't one of the times found open."
    assert out.tool_prompt == "Look up the openings with find_openings, and offer those."
    none = sim.call("find_openings", {"when": "tomorrow"})
    assert none.response == "Nothing is open then."


def test_a_refused_booking_says_so() -> None:
    sim = CallSimulator(desk(Calendar()))
    sim.call("find_openings", {"when": "this week"})
    sim.call("book_appointment", said({"slot": "s2"}))
    sim.caller("yes")
    out = sim.call("confirm_change", {"change": "book_appointment"})
    assert out.response.startswith("The change didn't go through: that time was just taken.")


def test_move_and_cancel_their_own_appointments() -> None:
    cal = Calendar()
    sim = CallSimulator(desk(cal))
    mine = sim.call("my_appointments", {})
    assert mine.response == "Their appointments: your cleaning on Friday at 9 am (appointment a1)"
    sim.call("find_openings", {"when": "next week"})
    moving = sim.call("move_appointment", said({"appointment": "a1", "slot": "s1"}))
    assert moving.ran
    assert sim.global_data["ops"]["waiting"]["read_back"] == (
        "Move your cleaning on Friday at 9 am to Tuesday at 2 pm. Shall I go ahead?")
    # A cancel of the same appointment while the move waits takes its place
    cancelling = sim.call("cancel_appointment", said({"appointment": "a1"}))
    assert "takes the place of the change read back before" in cancelling.response
    assert "an appointment can't be both moved and cancelled" in cancelling.response
    sim.caller("yes")
    sim.call("confirm_change", {"change": "cancel_appointment"})
    assert cal.log[-1] == ("cancel", "a1") and not any(e[0] == "move" for e in cal.log)
    unknown = sim.call("cancel_appointment", said({"appointment": "a7"}))
    assert unknown.response == "Nothing is changed: a7 isn't one of their appointments."


def test_their_appointments_need_an_account_and_booking_can_go_before_it() -> None:
    cal = Calendar()
    agent = ServiceAgent("dentist", role="r", suppress_logs=True)
    agent.identify(any_of=[["phone"]], find=lambda call, keys: "p1", required=False)
    Appointments(openings=cal.openings, book=cal.book, booked=cal.mine, cancel=cal.cancel,
                 before_identity=True).add_to(agent)
    sim = CallSimulator(agent)
    assert sim.call("my_appointments", {}).response == "Their account isn't found yet."
    assert sim.call("find_openings", {"when": "next week"}).response.startswith("Open:")
    assert sim.call("book_appointment", said({"slot": "s1"})).ran


def test_the_pack_can_be_renamed_reworded_and_put_on_operations() -> None:
    cal = Calendar()
    ops = Operations(role="r")
    Appointments(openings=cal.openings, book=cal.book, tools={"book": "book_visit"},
                 wording={"book.read_back": "Reservo {label}. ¿Le parece bien?"}).add_to(ops)
    sim = CallSimulator(ops.install(AgentBase(name="t", suppress_logs=True)))
    sim.call("find_openings", {"when": "next week"})
    sim.call("book_visit", said({"slot": "s1"}))
    assert sim.global_data["ops"]["waiting"]["read_back"] == "Reservo Tuesday at 2 pm. ¿Le parece bien?"
    assert "my_appointments" not in sim.functions, "no booked=, no list of their own"
    with pytest.raises(ValueError, match="needs booked="):
        Appointments(openings=cal.openings, book=cal.book, cancel=cal.cancel)
    with pytest.raises(ValueError, match="no tool reschedule"):
        Appointments(openings=cal.openings, book=cal.book, tools={"reschedule": "x"})
    with pytest.raises(TypeError, match="Operations or a ServiceAgent"):
        Appointments(openings=cal.openings, book=cal.book).add_to(object())


def inbox_agent(saved: list[Message], **kwargs: Any) -> ServiceAgent:
    agent = ServiceAgent("office", role="You answer the phone for a small office.", suppress_logs=True)
    Messages(save=lambda call, message: saved.append(message),
             recipients={"Dr. Lee": "the dentist", "Sam": "the office manager"},
             **kwargs).add_to(agent)
    return agent


def test_take_a_message_with_the_number_they_call_from() -> None:
    saved: list[Message] = []
    sim = CallSimulator(inbox_agent(saved), request_fields={"caller_id_num": "+15551230000"})
    sim.call("take_message", said({"to": "Dr. Lee", "text": "Call me about the crown", "name": "Ann"}))
    assert sim.global_data["ops"]["waiting"]["read_back"] == (
        'The message: "Call me about the crown", for Dr. Lee, from Ann, to call back on the number they\'re '
        "calling from, +15551230000. Shall I pass it on?"
    )
    sim.caller("yes")
    done = sim.call("confirm_change", {"change": "take_message"})
    assert done.response.startswith("Done. The message is passed on.")
    assert saved == [Message(text="Call me about the crown", name="Ann", number="+15551230000", to="Dr. Lee",
                             call_id="simulated-call", account_id="")]


def test_a_message_asks_for_what_it_needs() -> None:
    saved: list[Message] = []
    sim = CallSimulator(inbox_agent(saved))
    asked = sim.call("take_message", said({"to": "Sam", "text": "Running late", "name": "Bo"}))
    assert (asked.tool_prompt or "").startswith("Ask them: What's the best number to reach them on?")
    missing = sim.call("take_message", said({"text": "hi"}))
    assert (missing.tool_prompt or "").startswith("Ask them: Who is the message for?")
    with pytest.raises(ValueError, match="ask_for"):
        Messages(save=lambda call, message: None, ask_for=("email",))


def test_a_second_message_for_the_same_person_amends_it() -> None:
    saved: list[Message] = []
    sim = CallSimulator(inbox_agent(saved), request_fields={"caller_id_num": "+15551230000"})
    sim.call("take_message", said({"to": "Sam", "text": "Running late", "name": "Bo"}))
    out = sim.call("take_message", said({"to": "Sam", "text": "Running very late", "name": "Bo"}))
    assert "takes the place of the change read back before" in out.response
    sim.caller("yes")
    sim.call("confirm_change", {"change": "take_message"})
    assert [m.text for m in saved] == ["Running very late"]
