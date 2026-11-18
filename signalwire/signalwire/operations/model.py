"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

What a developer writes for an operations agent: an operation's fields, the
change its ``prepare`` builds, the writes that carry it out, and the two ways
``prepare`` says no (``Need``, ``Refuse``).
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Literal, Union, get_args, get_origin, get_type_hints

try:  # Python 3.10 has is_typeddict in typing; keep the import local to one place
    from typing import is_typeddict as _is_typeddict
except ImportError:  # pragma: no cover - every supported Python has it
    _is_typeddict = None  # type: ignore[assignment]

NOT_SAID = "not said"
"""The value a field takes when the caller hasn't said it: the model's honest
answer, which the operation treats as missing rather than as a value."""


class Need(Exception):
    """
    Raised by ``prepare`` when something the operation needs wasn't said.

    Nothing is proposed. The model is told what to ask, and keeps everything
    the caller already gave for the next call.

    Example:
        if not fields.size:
            raise Need("Which size would they like: small, medium or large?", ["size"])
    """

    def __init__(self, ask: str, fields: Sequence[str] = ()) -> None:
        """
        Args:
            ask: The question to ask the caller, in the operation's words.
            fields: The fields still missing.
        """
        super().__init__(ask)
        self.ask = ask
        self.fields = list(fields)


class Refuse(Exception):
    """
    Raised by ``prepare`` (or a lookup) when the request breaks a rule.

    Nothing changes. The model is told why, and what can be done instead.

    Example:
        if order.status != "pending":
            raise Refuse("Only pending orders can be cancelled.", "Offer a return once it's delivered.")
    """

    def __init__(self, why: str, then: str | None = None, *, keep: bool = False) -> None:
        """
        Args:
            why: What is true now: nothing was changed, and why.
            then: What to do next. Defaults to telling the caller and asking
                how they'd like to go on.
            keep: True to keep it in the model's view however long it is,
                for a refusal that lists choices the caller picks from later.
        """
        super().__init__(why)
        self.why = why
        self.then = then
        self.keep = keep


class WriteFailed(Exception):
    """
    Raised by ``apply`` when a backend write was refused.

    The change stops at that write: the writes before it stay made, and the
    model is told exactly what went through.
    """

    def __init__(self, reason: str) -> None:
        """
        Args:
            reason: Why the backend refused it, in words the caller can hear.
        """
        super().__init__(reason)
        self.reason = reason


class Write:
    """
    One backend write a change carries out, kept as data.

    A change's writes are frozen when it is read back: a later amendment
    builds a new change, and never edits these.

    Example:
        Write("cancel_pending_order", order_id="#W1234567", reason="no longer needed")
    """

    __slots__ = ("name", "args")

    def __init__(self, name: str, /, **args: Any) -> None:
        """
        Args:
            name: What the write does, such as the backend call's name.
            **args: The write's arguments.
        """
        self.name = name
        self.args = dict(args)

    def to_dict(self) -> dict[str, Any]:
        """The write as it is kept in the call's record."""
        return {"name": self.name, "args": dict(self.args)}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Write:
        """A write from the call's record."""
        return cls(str(data.get("name") or ""), **dict(data.get("args") or {}))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Write) and (self.name, self.args) == (other.name, other.args)

    def __repr__(self) -> str:
        return f"Write({self.name!r}, **{self.args!r})"


@dataclass
class Change:
    """
    A change ``prepare`` built, ready to read back.

    Example:
        Change(
            read_back="Cancel order #W1234567, refunding $54.04 to the card it was paid with. Shall I go ahead?",
            touches=["order:#W1234567"],
            writes=[Write("cancel_pending_order", order_id="#W1234567", reason="no longer needed")],
            money=[-54.04],
            done=["Order #W1234567 is cancelled; $54.04 goes back to the card."],
        )
    """

    read_back: str
    """The words the platform says, and the caller says yes to. The change
    itself goes in the first clause: a read-back cut off by the caller's
    answer is judged on what they heard."""
    touches: Sequence[str] = ()
    """Stable keys for everything it acts on, such as ``order:#W1234567`` or
    ``item:9494281769``. A new request is weighed against the change waiting
    by these."""
    writes: Sequence[Write] = ()
    """The backend writes, in order."""
    money: Sequence[float] | None = None
    """The money each write moves: more than 0 charged, less than 0 back to
    the caller. Kept in the call's record for totals."""
    done: Sequence[str] | str | None = None
    """What to tell the caller once each write went through, one per write, or
    one sentence for the whole change."""

    def done_lines(self) -> list[str]:
        """What to say for each write once it went through."""
        n = max(len(self.writes), 1)
        if isinstance(self.done, str):
            return [""] * (n - 1) + [self.done]
        if self.done:
            lines = [str(d) for d in self.done]
            return (lines + [""] * n)[:n]
        return [""] * (n - 1) + [f"It's done: {_statement(self.read_back)}"]

    def money_moved(self) -> list[float]:
        """The money each write moves."""
        moved = [float(m) for m in (self.money or [])]
        return (moved + [0.0] * len(self.writes))[: len(self.writes)]


@dataclass(frozen=True)
class Field:
    """
    One thing an operation (or a lookup) takes from the caller.

    Example:
        reason = Field(Literal["no longer needed", "ordered by mistake"], "Why, in their words",
                       ask="Why are they cancelling it?")
    """

    kind: Any
    """The value's type: ``str``, ``int``, ``float``, ``bool``, a ``Literal``,
    ``list[...]``, ``dict[str, ...]``, a ``TypedDict``, or a JSON schema dict."""
    description: str
    """What it is, in the caller's terms. The model reads it."""
    required: bool = True
    """Whether the operation needs it."""
    ask: str | None = None
    """The question for the caller when it's missing. With it, a required
    field the model sends empty, null or as "not said" (a choice of values
    gets that option) is asked for before ``prepare`` runs, so the model is
    never pushed to invent it."""

    def schema(self) -> dict[str, Any]:
        """The field's JSON schema, with its description."""
        return {**_schema_of(self.kind), "description": self.description}


class Values:
    """
    An operation's fields as the model gave them: ``values.order_id``.

    A field that wasn't given (or came as null or "not said") is ``None``.
    ``values.args`` holds the arguments as they came.
    """

    def __init__(self, fields: Mapping[str, Field], args: Mapping[str, Any]) -> None:
        self.args = dict(args)
        self._fields = dict(fields)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_") or name not in self._fields:
            raise AttributeError(name)
        value = self.args.get(name)
        return None if _missing(value) else value

    def get(self, name: str, default: Any = None) -> Any:
        """A field's value, or ``default`` when it wasn't given."""
        value = self.args.get(name)
        return default if _missing(value) else value


class Operation:
    """
    Something the agent can change for a caller.

    Subclass it, declare its ``Field`` attributes, give it a docstring (what
    it does, as the model reads it), and write ``prepare``. Register it with
    ``ServiceAgent.operation``.

    Example:
        @agent.operation(tool="cancel_order")
        class Cancel(Operation):
            '''Cancel pending orders.'''
            order_ids = Field(list[str], "The orders to cancel")

            def prepare(self, call, f):
                ...
                return Change(read_back=..., touches=..., writes=...)
    """

    kind: ClassVar[str] = ""
    """Its name in the call's record and in ``confirm_change``: the class name
    in lower case unless set."""
    tool: ClassVar[str] = ""
    """The tool's name. Use the verb a caller would use."""
    combine: ClassVar[Sequence[str] | None] = None
    """When a request of this operation made "as well" merges into one of the
    same operation waiting for its yes: the fields that must be the same in
    both (such as where a refund goes). None: they are never merged."""
    goes_before: ClassVar[Sequence[str]] = ()
    """Kinds of change that must wait for this one when both are for the same
    things (an address change before an item change)."""
    guidance: ClassVar[str | None] = None
    """Instructions for a step of its own, entered when its ``prepare``
    raises ``Need``. None: no step of its own."""
    fillers: ClassVar[Sequence[str]] = ()
    """Short phrases said while its tool runs."""
    confirm: ClassVar[bool] = True
    """False for a change that goes through without a read-back and a yes,
    such as a move in a game. Its writes run when its tool is called."""
    before_identity: ClassVar[bool] = False
    """True for an operation a caller can use before they're identified, such
    as booking for a new customer."""
    ask_in_order: ClassVar[bool] = False
    """True to ask for one missing field at a time, in declaration order."""
    offered_in: ClassVar[Sequence[str] | None] = None
    """The steps that offer its tool, by name; None for every step, so a
    caller who asks for it anywhere is never stranded."""
    secure: ClassVar[bool] = True
    """Whether its tool takes the agent's per-call security token."""

    def fields(self) -> dict[str, Field]:
        """The operation's fields, in declaration order."""
        found: dict[str, Field] = {}
        for klass in reversed(type(self).__mro__):
            for name, value in vars(klass).items():
                if isinstance(value, Field):
                    found[name] = value
        return found

    def prepare(self, call: Any, values: Values) -> Any:
        """
        Check the request and build its change.

        Returns a ``Change``, or raises ``Need`` or ``Refuse``. It may look
        things up, and may be ``async``, but never writes.
        """
        raise NotImplementedError(f"{type(self).__name__}.prepare")

    def apply(self, call: Any, write: Write) -> Any:
        """
        Carry out one write; raise ``WriteFailed`` if the backend refuses it.

        Defaults to the service's writer (``Operations.writes_with``). May be
        ``async``.
        """
        return call.service.apply_write(call, write)

    def conflicts_with(self, other: str, mine: Change, theirs: Change) -> str | None:
        """
        Why this change and another can't both happen, or None.

        Args:
            other: The other change's kind.
            mine: This change.
            theirs: The other change.
        """
        return None

    def without(self, args: Mapping[str, Any], gone: set[str]) -> dict[str, Any] | None:
        """
        This operation's arguments with what ``gone`` names taken out, when
        another change takes those things over; None if it can't be split,
        and the whole change is replaced.

        Args:
            args: The arguments the change waiting was built from.
            gone: The ``touches`` keys the new change takes over.
        """
        return None

    def merge(self, held: Mapping[str, Any], new: Mapping[str, Any]) -> dict[str, Any]:
        """
        One request from the change waiting (``held``) and a request made as
        well (``new``). Lists are joined, and an item asked for again goes as
        asked now (``same_item``); other fields take the new value.
        """
        out = {**held, **{k: v for k, v in new.items() if not _missing(v)}}
        for name in self.fields():
            old, now = held.get(name), new.get(name)
            if isinstance(old, list) and isinstance(now, list):
                out[name] = [o for o in old if not any(self.same_item(name, o, n) for n in now)] + list(now)
        return out

    def same_item(self, field: str, a: Any, b: Any) -> bool:
        """Whether two entries of a list field are the same thing asked for twice."""
        return bool(a == b)

    @classmethod
    def describe(cls) -> str:
        """What it does, as the model reads it: its docstring's first paragraph."""
        doc = (cls.__doc__ or "").strip()
        return re.split(r"\n\s*\n", doc)[0].replace("\n", " ").strip() if doc else ""


def _missing(value: Any) -> bool:
    return value is None or value == "" or (isinstance(value, str) and value.strip().lower() == NOT_SAID)


def _statement(read_back: str) -> str:
    """A read-back without its closing question: "Cancel X. Shall I?" -> "Cancel X."."""
    sentences = re.split(r"(?<=[.!?])\s+", read_back.strip())
    kept = [s for s in sentences if not s.endswith("?")]
    return " ".join(kept) if kept else read_back.strip()


_SIMPLE: dict[Any, dict[str, Any]] = {
    str: {"type": "string"},
    bool: {"type": "boolean"},
    int: {"type": "integer"},
    float: {"type": "number"},
}


def _schema_of(kind: Any) -> dict[str, Any]:
    """The JSON schema of a Field's type."""
    if isinstance(kind, Mapping):
        return dict(kind)
    if kind in _SIMPLE:
        return dict(_SIMPLE[kind])
    origin, args = get_origin(kind), get_args(kind)
    if origin is Literal:
        return {"type": "string", "enum": [str(a) for a in args]}
    if origin in (list, Sequence, tuple) or kind in (list, tuple):
        return {"type": "array", "items": _schema_of(args[0]) if args else {}}
    if origin in (dict, Mapping) or kind is dict:
        return {"type": "object", "additionalProperties": _schema_of(args[1]) if len(args) == 2 else {}}
    if origin is Union:
        kinds = [a for a in args if a is not type(None)]
        if len(kinds) == 1:
            return _schema_of(kinds[0])
    if _is_typeddict is not None and _is_typeddict(kind):
        hints = get_type_hints(kind)
        required = sorted(getattr(kind, "__required_keys__", set(hints)))
        return {"type": "object", "properties": {k: _schema_of(v) for k, v in hints.items()}, "required": required}
    raise TypeError(f"a Field's kind must be a simple type, Literal, list, dict, TypedDict or JSON schema, got {kind!r}")


__all__ = ["NOT_SAID", "Change", "Field", "Need", "Operation", "Refuse", "Values", "Write", "WriteFailed"]
