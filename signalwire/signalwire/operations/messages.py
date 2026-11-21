"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Messages: a task pack that takes a message for someone, read back to the
caller before it's passed on, with a number to reach them. Add it to an
``Operations`` or a ``ServiceAgent`` with ``add_to``; where the message goes
(an inbox, a text, an email, a ticket) is your ``save``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from signalwire.operations.model import Change, Field, Need, Operation, Write
from signalwire.operations.agent import Operations
from signalwire.operations.wording import _Wording


@dataclass(frozen=True)
class Message:
    """A message the caller left, as ``save`` gets it."""

    text: str
    """The message, in the caller's words."""
    name: str
    """Who it's from, as they said it, or ``""``."""
    number: str
    """A number to reach them on, as they gave it or agreed to, or ``""``."""
    to: str
    """Who it's for (one of ``recipients``), or ``""``."""
    call_id: str
    """The platform's id for the call."""
    account_id: str
    """The account identified, or ``""``."""


MESSAGES_WORDING: Mapping[str, str] = MappingProxyType(
    {
        "tool": "Take a message to pass on.",
        "tool.text": "The message, in their words.",
        "tool.name": "Who it's from, as they said it.",
        "tool.number": "A number to reach them on, as they said it.",
        "tool.to": "Who it's for.",
        "ask.text": "What would they like the message to say?",
        "ask.name": "Who is the message from?",
        "ask.number": "What's the best number to reach them on?",
        "ask.to": "Who is the message for?",
        "read_back": 'The message: "{text}"{parts}. Shall I pass it on?',
        "read_back.to": ", for {to}",
        "read_back.name": ", from {name}",
        "read_back.number": ", to call back on {number}",
        "read_back.caller_id": ", to call back on the number they're calling from, {number}",
        "done": "The message is passed on.",
    }
)
"""Every key the ``Messages`` pack's words come from, with its default."""


class Messages:
    """
    Take a message for someone and pass it on.

    Example:
        Messages(
            save=lambda call, message: inbox.add(message.to, message.text, message.name, message.number),
            recipients={"Dr. Lee": "the dentist", "the front desk": "bookings and bills"},
        ).add_to(agent)
    """

    def __init__(
        self,
        *,
        save: Callable[[Any, Message], Any],
        recipients: Mapping[str, str] | None = None,
        ask_for: Sequence[str] = ("name", "number"),
        caller_id: bool = True,
        tool: str = "take_message",
        wording: Mapping[str, str] | None = None,
        before_identity: bool = True,
    ) -> None:
        """
        Args:
            save: ``save(call, message)`` passes the ``Message`` on, once
                the caller said yes; raise ``WriteFailed`` when it can't. May
                be ``async``.
            recipients: Who a message can be for, by name, each with a few
                words on who they are; None when there's only one place it
                goes.
            ask_for: What's asked for when the caller hasn't said it, of
                ``name`` and ``number``; the message itself always is, and
                who it's for whenever there are ``recipients``.
            caller_id: True to offer the number they're calling from, read
                back for them to agree to, when they haven't given one.
            tool: The tool's name.
            wording: Words in place of the defaults, by key; the keys are
                those of ``MESSAGES_WORDING``.
            before_identity: False to take messages only from callers who
                are identified.
        """
        unknown = sorted(set(ask_for) - {"name", "number"})
        if unknown:
            raise ValueError(f"ask_for takes name and number, not {', '.join(unknown)}")
        self._save = save
        self._recipients = dict(recipients) if recipients else None
        self._ask_for = set(ask_for)
        self._caller_id = caller_id
        self.tool = tool
        """The tool's name."""
        self._w = _Wording(MESSAGES_WORDING, wording, "Messages", "MESSAGES_WORDING")
        self._before_identity = before_identity

    def add_to(self, target: Any) -> Any:
        """Register the pack's operation on an ``Operations`` or a ``ServiceAgent``; returns it."""
        ops = _operations_of(target)
        w, pack = self._w, self
        fields: dict[str, Field] = {}
        if self._recipients:
            fields["to"] = Field(
                {"type": "string", "enum": list(self._recipients)},
                w("tool.to")
                + " "
                + "; ".join(f"{k}: {v}" for k, v in self._recipients.items()),
                ask=w("ask.to"),
            )
        fields["text"] = Field(str, w("tool.text"), ask=w("ask.text"))
        fields["name"] = Field(
            str,
            w("tool.name"),
            required="name" in self._ask_for,
            ask=w("ask.name") if "name" in self._ask_for else None,
        )
        number_asked = "number" in self._ask_for and not self._caller_id
        fields["number"] = Field(
            str,
            w("tool.number"),
            required=number_asked,
            ask=w("ask.number") if number_asked else None,
        )

        def prepare(self: Operation, call: Any, f: Any) -> Change:
            number, parts = f.get("number"), ""
            to, name = f.get("to") or "", f.get("name") or ""
            if to:
                parts += w("read_back.to", to=to)
            if name:
                parts += w("read_back.name", name=name)
            if number:
                parts += w("read_back.number", number=number)
            elif pack._caller_id and "number" in pack._ask_for:
                number = str(call.raw_data.get("caller_id_num") or "")
                if not number:
                    raise Need(w("ask.number"), ["number"])
                parts += w("read_back.caller_id", number=number)
            return Change(
                read_back=w("read_back", text=f.text, parts=parts),
                # One message per person waiting for a yes: another for them amends it
                touches=[f"message:{to}"],
                writes=[
                    Write(
                        "take_message",
                        text=f.text,
                        name=name,
                        number=number or "",
                        to=to,
                    )
                ],
                done=w("done"),
            )

        def apply(self: Operation, call: Any, write: Write) -> Any:
            a = write.args
            return pack._save(
                call,
                Message(
                    text=str(a.get("text") or ""),
                    name=str(a.get("name") or ""),
                    number=str(a.get("number") or ""),
                    to=str(a.get("to") or ""),
                    call_id=call.call_id,
                    account_id=call.account_id,
                ),
            )

        cls = type(
            "TakeMessage",
            (Operation,),
            {
                "__doc__": w("tool"),
                "prepare": prepare,
                "apply": apply,
                "before_identity": self._before_identity,
                **fields,
            },
        )
        ops.operation(cls, tool=self.tool, kind=self.tool)
        return target


def _operations_of(target: Any) -> Operations:
    """The ``Operations`` a pack is added to: the one given, or a ``ServiceAgent``'s."""
    ops = getattr(target, "ops", target)
    if not isinstance(ops, Operations):
        raise TypeError(
            f"add_to takes an Operations or a ServiceAgent, not {type(target).__name__}"
        )
    return ops


__all__ = ["MESSAGES_WORDING", "Message", "Messages"]
