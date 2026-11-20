"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Appointments: a task pack that finds open times and books, moves and cancels
a caller's appointments, against a calendar you supply. Add it to an
``Operations`` or a ``ServiceAgent`` with ``add_to``.

The calendar is yours, as functions: what's open near when the caller would
like it, booking a slot, and the caller's own appointments, to move or
cancel. A slot or an appointment comes back with its ``label``, how it's said
("Tuesday the 3rd at 2 pm"): the pack never reads or writes a date itself, so
the time zone, the calendar and the language are the calendar's.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from signalwire.core.function_result import FunctionResult
from signalwire.operations.model import Change, Field, Need, Operation, Refuse, Write
from signalwire.operations.agent import Operations
from signalwire.operations.wording import _Wording


@dataclass(frozen=True)
class Slot:
    """A time open for an appointment."""

    id: str
    """The calendar's id for it."""
    label: str
    """How it's said, in the calendar's own time zone and words: "Tuesday the 3rd at 2 pm"."""


@dataclass(frozen=True)
class Appointment:
    """One of the caller's appointments."""

    id: str
    """The calendar's id for it."""
    label: str
    """How it's said: "your cleaning on Tuesday the 3rd at 2 pm"."""


APPOINTMENTS_WORDING: Mapping[str, str] = MappingProxyType(
    {
        "tool.openings": "Times open for an appointment, near when they'd like it.",
        "tool.openings.when": 'When they\'d like it, in their words, such as "Tuesday afternoon".',
        "tool.kind": "What the appointment is for.",
        "openings.found": "Open: {slots}",
        "openings.slot": "{label} (slot {id})",
        "openings.none": "Nothing is open then.",
        "openings.none.then": "Tell them, and ask about another time.",
        "openings.then": "Offer them these, and book the one they choose with {tool}.",
        "openings.ask": "When would they like it?",
        "tool.booked": "Their appointments.",
        "booked.found": "Their appointments: {appointments}",
        "booked.item": "{label} (appointment {id})",
        "booked.none": "They have no appointments.",
        "tool.book": "Book an appointment at a time found open.",
        "tool.book.slot": "The time to book, by its slot id from the openings.",
        "tool.book.note": "Anything they want noted on it, in their words.",
        "book.read_back": "Book {label}. Shall I go ahead?",
        "book.read_back.kind": "Book {label} for {kind}. Shall I go ahead?",
        "book.done": "It's booked: {label}.",
        "slot.unknown": "{slot} isn't one of the times found open.",
        "slot.unknown.then": "Look up the openings with {tool}, and offer those.",
        "tool.move": "Move one of their appointments to a time found open.",
        "tool.move.appointment": "The appointment to move, by its id.",
        "tool.move.slot": "The new time, by its slot id from the openings.",
        "move.read_back": "Move {appointment} to {label}. Shall I go ahead?",
        "move.done": "It's moved to {label}.",
        "tool.cancel": "Cancel one of their appointments.",
        "tool.cancel.appointment": "The appointment to cancel, by its id.",
        "cancel.read_back": "Cancel {appointment}. Shall I go ahead?",
        "cancel.done": "It's cancelled: {appointment}.",
        "appointment.unknown": "{appointment} isn't one of their appointments.",
        "appointment.unknown.then": "Look them up with {tool}.",
        "conflict": "an appointment can't be both moved and cancelled",
        "list.and": " and ",
        "list.or": " or ",
        "list.comma": ", ",
    }
)
"""Every key the ``Appointments`` pack's words come from, with its default."""

_TOOLS = MappingProxyType(
    {
        "openings": "find_openings",
        "booked": "my_appointments",
        "book": "book_appointment",
        "move": "move_appointment",
        "cancel": "cancel_appointment",
    }
)


class Appointments:
    """
    Book, move and cancel a caller's appointments against your calendar.

    Example:
        Appointments(
            openings=lambda call, when, kind: calendar.open_near(when, kind),
            book=lambda call, slot, kind, note: calendar.book(slot.id, call.account_id, kind, note),
            booked=lambda call: calendar.for_patient(call.account_id),
            move=lambda call, appointment, slot: calendar.move(appointment.id, slot.id),
            cancel=lambda call, appointment: calendar.cancel(appointment.id),
            kinds=["cleaning", "check-up"],
        ).add_to(agent)
    """

    def __init__(
        self,
        *,
        openings: Callable[[Any, str, str | None], Any],
        book: Callable[[Any, Slot, str | None, str | None], Any],
        booked: Callable[[Any], Any] | None = None,
        move: Callable[[Any, Appointment, Slot], Any] | None = None,
        cancel: Callable[[Any, Appointment], Any] | None = None,
        kinds: Sequence[str] | None = None,
        before_identity: bool = False,
        wording: Mapping[str, str] | None = None,
        tools: Mapping[str, str] | None = None,
        state_key: str = "appointments",
    ) -> None:
        """
        Args:
            openings: ``openings(call, when, kind)`` returns the ``Slot``s open
                near ``when``, the caller's words ("Tuesday afternoon");
                ``kind`` is one of ``kinds``, or None. May be ``async``, and
                may raise ``Refuse`` or ``Need``.
            book: ``book(call, slot, kind, note)`` books it, once the caller
                said yes; raise ``WriteFailed`` when the calendar refuses.
            booked: ``booked(call)`` returns the caller's ``Appointment``s.
                Needed to move or cancel.
            move: ``move(call, appointment, slot)`` moves one.
            cancel: ``cancel(call, appointment)`` cancels one.
            kinds: What an appointment can be for, as the caller would say
                it ("cleaning"); None for no choice.
            before_identity: True to find openings and book before the caller
                is identified, for new customers. Their own appointments
                always need an account.
            wording: Words in place of the defaults, by key; the keys are
                those of ``APPOINTMENTS_WORDING``.
            tools: Names in place of the tools' (``find_openings``,
                ``my_appointments``, ``book_appointment``,
                ``move_appointment``, ``cancel_appointment``), keyed by
                ``openings``, ``booked``, ``book``, ``move`` and ``cancel``.
            state_key: Where in ``call.state`` the pack keeps the slots it
                found, so a booking can only be for one of them.
        """
        if (move or cancel) and booked is None:
            raise ValueError(
                "moving or cancelling appointments needs booked=, to find the caller's"
            )
        unknown = sorted(set(tools or {}) - set(_TOOLS))
        if unknown:
            raise ValueError(
                f"tools= names no tool {', '.join(unknown)}; the keys are {', '.join(_TOOLS)}"
            )
        self._openings, self._book, self._booked = openings, book, booked
        self._move, self._cancel = move, cancel
        self._kinds = list(kinds) if kinds else None
        self._before_identity = before_identity
        self._w = _Wording(
            APPOINTMENTS_WORDING, wording, "Appointments", "APPOINTMENTS_WORDING"
        )
        self.tools: Mapping[str, str] = MappingProxyType({**_TOOLS, **(tools or {})})
        """The tools' names, by key."""
        self._key = state_key

    def add_to(self, target: Any) -> Any:
        """Register the pack's lookups and operations on an ``Operations`` or a ``ServiceAgent``; returns it."""
        ops = _operations_of(target)
        w, tools, pack = self._w, self.tools, self
        kind_field = (
            Field(
                {"type": "string", "enum": self._kinds}, w("tool.kind"), required=False
            )
            if self._kinds
            else None
        )
        openings_fields = {
            "when": Field(str, w("tool.openings.when"), ask=w("openings.ask"))
        }
        if kind_field is not None:
            openings_fields["kind"] = kind_field

        @ops.lookup(
            w("tool.openings"),
            tool=tools["openings"],
            fields=openings_fields,
            before_identity=self._before_identity,
        )
        async def find_openings(
            call: Any, when: str | None, kind: str | None = None
        ) -> Any:
            if not when:
                raise Need(w("openings.ask"), ["when"])
            slots = [
                _slot(s) for s in await _maybe(pack._openings(call, when, kind)) or []
            ]
            mine = dict(call.state.get(pack._key) or {})
            mine["offered"] = {
                **(mine.get("offered") or {}),
                **{s.id: s.label for s in slots},
            }
            call.state[pack._key] = mine
            if not slots:
                return FunctionResult(
                    tool_result=w("openings.none"), tool_prompt=w("openings.none.then")
                )
            listed = w.joined(
                [w("openings.slot", label=s.label, id=s.id) for s in slots]
            )
            return FunctionResult(
                tool_result=w("openings.found", slots=listed),
                tool_prompt=w("openings.then", tool=tools["book"]),
            )

        book_fields = {"slot": Field(str, w("tool.book.slot"))}
        if kind_field is not None:
            book_fields["kind"] = kind_field
        book_fields["note"] = Field(str, w("tool.book.note"), required=False)

        def book_prepare(self: Operation, call: Any, f: Any) -> Change:
            slot = pack._offered(call, f.slot)
            kind = f.get("kind")
            read_back = (
                w("book.read_back.kind", label=slot.label, kind=kind)
                if kind
                else w("book.read_back", label=slot.label)
            )
            return Change(
                read_back=read_back,
                touches=[f"slot:{slot.id}"],
                writes=[
                    Write(
                        "book_appointment",
                        slot=slot.id,
                        label=slot.label,
                        kind=kind,
                        note=f.get("note"),
                    )
                ],
                done=w("book.done", label=slot.label),
            )

        def book_apply(self: Operation, call: Any, write: Write) -> Any:
            a = write.args
            return pack._book(
                call,
                Slot(str(a["slot"]), str(a["label"])),
                a.get("kind"),
                a.get("note"),
            )

        ops.operation(
            _operation(
                "Book",
                w("tool.book"),
                book_fields,
                book_prepare,
                book_apply,
                before_identity=self._before_identity,
            ),
            tool=tools["book"],
            kind=tools["book"],
        )

        if self._booked is not None:

            @ops.lookup(w("tool.booked"), tool=tools["booked"], fields={})
            async def my_appointments(call: Any) -> Any:
                found = await pack._appointments(call)
                if not found:
                    return w("booked.none")
                return w(
                    "booked.found",
                    appointments=w.joined(
                        [w("booked.item", label=a.label, id=a.id) for a in found]
                    ),
                )

        if self._move is not None:

            async def move_prepare(self: Operation, call: Any, f: Any) -> Change:
                appointment = await pack._appointment(call, f.appointment)
                slot = pack._offered(call, f.slot)
                return Change(
                    read_back=w(
                        "move.read_back",
                        appointment=appointment.label,
                        label=slot.label,
                    ),
                    touches=[f"appointment:{appointment.id}", f"slot:{slot.id}"],
                    writes=[
                        Write(
                            "move_appointment",
                            appointment=appointment.id,
                            appointment_label=appointment.label,
                            slot=slot.id,
                            label=slot.label,
                        )
                    ],
                    done=w("move.done", label=slot.label),
                )

            def move_apply(self: Operation, call: Any, write: Write) -> Any:
                a = write.args
                assert pack._move is not None  # noqa: S101  # type narrowing: registered only with move
                return pack._move(
                    call,
                    Appointment(str(a["appointment"]), str(a["appointment_label"])),
                    Slot(str(a["slot"]), str(a["label"])),
                )

            ops.operation(
                _operation(
                    "Move",
                    w("tool.move"),
                    {
                        "appointment": Field(str, w("tool.move.appointment")),
                        "slot": Field(str, w("tool.move.slot")),
                    },
                    move_prepare,
                    move_apply,
                    conflict=w("conflict"),
                    rivals=(tools["move"], tools["cancel"]),
                ),
                tool=tools["move"],
                kind=tools["move"],
            )

        if self._cancel is not None:

            async def cancel_prepare(self: Operation, call: Any, f: Any) -> Change:
                appointment = await pack._appointment(call, f.appointment)
                return Change(
                    read_back=w("cancel.read_back", appointment=appointment.label),
                    touches=[f"appointment:{appointment.id}"],
                    writes=[
                        Write(
                            "cancel_appointment",
                            appointment=appointment.id,
                            appointment_label=appointment.label,
                        )
                    ],
                    done=w("cancel.done", appointment=appointment.label),
                )

            def cancel_apply(self: Operation, call: Any, write: Write) -> Any:
                a = write.args
                assert pack._cancel is not None  # noqa: S101  # type narrowing: registered only with cancel
                return pack._cancel(
                    call,
                    Appointment(str(a["appointment"]), str(a["appointment_label"])),
                )

            ops.operation(
                _operation(
                    "Cancel",
                    w("tool.cancel"),
                    {"appointment": Field(str, w("tool.cancel.appointment"))},
                    cancel_prepare,
                    cancel_apply,
                    conflict=w("conflict"),
                    rivals=(tools["move"], tools["cancel"]),
                ),
                tool=tools["cancel"],
                kind=tools["cancel"],
            )
        return target

    def _offered(self, call: Any, slot_id: str | None) -> Slot:
        offered = (call.state.get(self._key) or {}).get("offered") or {}
        if slot_id not in offered:
            raise Refuse(
                self._w("slot.unknown", slot=slot_id or "That"),
                self._w("slot.unknown.then", tool=self.tools["openings"]),
            )
        return Slot(str(slot_id), str(offered[slot_id]))

    async def _appointments(self, call: Any) -> list[Appointment]:
        assert self._booked is not None  # noqa: S101  # type narrowing: called only with booked
        return [_appointment(a) for a in await _maybe(self._booked(call)) or []]

    async def _appointment(self, call: Any, appointment_id: str | None) -> Appointment:
        for a in await self._appointments(call):
            if a.id == appointment_id:
                return a
        raise Refuse(
            self._w("appointment.unknown", appointment=appointment_id or "That"),
            self._w("appointment.unknown.then", tool=self.tools["booked"]),
        )


def _operation(
    name: str,
    description: str,
    fields: Mapping[str, Field],
    prepare: Callable[..., Any],
    apply: Callable[..., Any],
    *,
    before_identity: bool = False,
    conflict: str | None = None,
    rivals: Sequence[str] = (),
) -> type[Operation]:
    """An ``Operation`` class made for a pack: its fields, docstring, ``prepare`` and ``apply``."""
    body: dict[str, Any] = {
        "__doc__": description,
        "prepare": prepare,
        "apply": apply,
        "before_identity": before_identity,
        **fields,
    }
    if conflict is not None:

        def conflicts_with(
            self: Operation, other: str, mine: Change, theirs: Change
        ) -> str | None:
            # A move and a cancel of the same appointment: both take it, and they can't both happen
            return conflict if other in rivals and other != self.kind else None

        body["conflicts_with"] = conflicts_with
    return type(name, (Operation,), body)


def _slot(value: Any) -> Slot:
    if isinstance(value, Slot):
        return value
    if isinstance(value, Mapping):
        return Slot(str(value["id"]), str(value["label"]))
    raise TypeError(
        f"openings must return Slots (or mappings with id and label), got {type(value).__name__}"
    )


def _appointment(value: Any) -> Appointment:
    if isinstance(value, Appointment):
        return value
    if isinstance(value, Mapping):
        return Appointment(str(value["id"]), str(value["label"]))
    raise TypeError(
        f"booked must return Appointments (or mappings with id and label), got {type(value).__name__}"
    )


async def _maybe(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


def _operations_of(target: Any) -> Operations:
    """The ``Operations`` a pack is added to: the one given, or a ``ServiceAgent``'s."""
    ops = getattr(target, "ops", target)
    if not isinstance(ops, Operations):
        raise TypeError(
            f"add_to takes an Operations or a ServiceAgent, not {type(target).__name__}"
        )
    return ops


__all__ = ["APPOINTMENTS_WORDING", "Appointment", "Appointments", "Slot"]
