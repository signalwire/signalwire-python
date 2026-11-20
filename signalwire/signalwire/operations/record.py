"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The call's record, kept in ``global_data``: the account found, what the caller
asked for, the change waiting for their yes, the changes set aside for after
it, and the changes settled. ``now`` puts it in words for the conscience and
the steps, and is worked out again on every update, so it is never behind.
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping, Sequence
from decimal import Decimal
from typing import Any

from signalwire.operations.model import Change
from signalwire.operations.money import amount_of
from signalwire.operations.wording import _Wording

RECORD = "ops"
"""The ``global_data`` key the record lives under (``ops_<name>`` for an
``Operations`` given a ``name``), so other layers' state sits beside it."""

RECORD_VERSION = 1
"""The record's ``v``. It goes up when a key is renamed or changes meaning,
never when one is added, so a reader can tell a record it understands."""

RECORD_KEYS = (
    "v",
    "account_id",
    "account",
    "asked",
    "waiting",
    "queued",
    "history",
    "proposals",
    "state",
    "medium",
    "now",
)
"""The keys of the record."""


def _opening(w: _Wording) -> dict[str, Any]:
    """The record as a call opens."""
    return _whole(
        w,
        {},
        v=RECORD_VERSION,
        account_id="",
        account="",
        asked="",
        waiting={},
        queued=[],
        history=[],
        proposals=0,
        state={},
        medium="",
    )


def _opening_data(key: str, w: _Wording) -> dict[str, Any]:
    """The ``global_data`` a call opens with: the record under its key."""
    return {key: _opening(w)}


def _record_of(raw_data: Mapping[str, Any] | None, key: str = RECORD) -> dict[str, Any]:
    """The call's record, as the platform sent it with a request."""
    data = raw_data.get("global_data") if isinstance(raw_data, Mapping) else None
    record = data.get(key) if isinstance(data, Mapping) else None
    return copy.deepcopy(dict(record)) if isinstance(record, Mapping) else {}


def _whole(w: _Wording, data: Mapping[str, Any], **changes: Any) -> dict[str, Any]:
    """The whole record after these changes, with ``now`` worked out after them."""
    record = {**data, **changes}
    return {**record, "now": _now_line(record, w)}


def _update(
    key: str, w: _Wording, data: Mapping[str, Any], **changes: Any
) -> dict[str, Any]:
    """
    The ``global_data`` update for these changes: the whole record under its
    key, since the platform replaces a top-level key whole.
    """
    return {key: _whole(w, data, **changes)}


def _now_line(data: Mapping[str, Any], w: _Wording) -> str:
    """Where the call stands, in words: what they asked for, what's done, what waits for their answer, and what's
    set aside for after it."""
    done = " ".join(h["done"] for h in data.get("history") or [] if h.get("done"))
    waiting, queued = data.get("waiting") or {}, data.get("queued") or []
    medium = data.get("medium")
    parts = [
        w(f"medium.{medium}") if medium in ("voice", "chat") else "",
        w("now.asked", asked=data["asked"]) if data.get("asked") else "",
        w("now.done", done=done) if done else "",
        w("now.waiting", read_back=waiting["read_back"])
        if waiting.get("read_back")
        else "",
        w(
            "now.queued",
            read_backs=" ".join(
                w("now.queued.item", read_back=q["read_back"]) for q in queued
            ),
        )
        if queued
        else "",
    ]
    return "\n".join(p for p in parts if p)


def _waiting_entry(
    kind: str,
    args: Mapping[str, Any],
    change: Change,
    revision: int,
    done_default: str,
    currency: str | None,
) -> dict[str, Any]:
    """A change as it waits for the caller's yes: everything needed to carry it out, frozen. Money is kept as
    exact decimal strings, with its currency."""
    return {
        "kind": kind,
        "read_back": change.read_back,
        "touches": list(change.touches),
        "writes": [w.to_dict() for w in change.writes],
        "money": [str(m) for m in change.money_moved()],
        "currency": change.currency or currency or "",
        "done": change.done_lines(done_default),
        "args": dict(args),
        "revision": revision,
    }


def _queued_entry(kind: str, args: Mapping[str, Any], change: Change) -> dict[str, Any]:
    """A change set aside for after the one waiting, kept with the arguments to build it again."""
    return {
        "kind": kind,
        "read_back": change.read_back,
        "touches": list(change.touches),
        "args": dict(args),
    }


def _settle(
    data: Mapping[str, Any],
    outcome: str,
    done: str = "",
    made: int = 0,
    reason: str = "",
) -> dict[str, Any]:
    """
    The change waiting, settled into history: how (``made``, ``not made``
    with the ``reason`` the backend gave, ``declined``, ``replaced``), what
    was done, and the money moved by the writes that went through (all of
    them once made, else the first ``made``).
    """
    waiting = data.get("waiting") or {}
    moved = [amount_of(m) for m in waiting.get("money") or []]
    entry = {
        "kind": waiting.get("kind", ""),
        "touches": list(waiting.get("touches") or []),
        "read_back": waiting.get("read_back", ""),
        "outcome": outcome,
        **({"reason": reason} if reason else {}),
        "done": done,
        "money": str(sum(moved if outcome == "made" else moved[:made], Decimal(0))),
        "currency": waiting.get("currency") or "",
    }
    return {"waiting": {}, "history": [*(data.get("history") or []), entry]}


def _in_all(
    history: Sequence[Mapping[str, Any]],
    w: _Wording,
    money: Callable[[Decimal, str | None], str],
) -> str:
    """What the changes made in the call come to, once more than one moved money: for each currency, what went
    back to them and what was charged. ``money(amount, currency)`` writes an amount."""
    moved = [
        (amount_of(h["money"]), h.get("currency") or None)
        for h in history
        if h.get("money") and amount_of(h["money"]) != 0
    ]  # only writes that went through count
    if len(moved) < 2:
        return ""
    parts: list[str] = []
    for code in dict.fromkeys(c for _, c in moved):
        back = -sum((a for a, c in moved if c == code and a < 0), Decimal(0))
        charged = sum((a for a, c in moved if c == code and a > 0), Decimal(0))
        if back > 0:
            parts.append(w("money.back", amount=money(back, code)))
        if charged > 0:
            parts.append(w("money.charged", amount=money(charged, code)))
    return w("money.in_all", amounts=w.joined(parts)) if parts else ""


def _next_up(data: Mapping[str, Any], tool_of: Mapping[str, str], w: _Wording) -> str:
    """What to do once the change waiting is settled: take up the first one set aside."""
    queued = data.get("queued") or []
    if not queued:
        return ""
    first = queued[0]
    return w(
        "then.next_up",
        tool=tool_of.get(first["kind"], w("then.its_tool")),
        read_back=first["read_back"],
    )


__all__ = ["RECORD", "RECORD_KEYS", "RECORD_VERSION"]
