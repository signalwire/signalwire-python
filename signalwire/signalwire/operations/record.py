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

from collections.abc import Mapping, Sequence
from typing import Any

from signalwire.operations.model import Change

RECORD_KEYS = ("account_id", "account", "asked", "waiting", "queued", "history", "proposals", "now")
"""The ``global_data`` keys the record owns."""


def _opening() -> dict[str, Any]:
    """The record as a call opens."""
    return _update({}, account_id="", account="", asked="", waiting={}, queued=[], history=[], proposals=0)


def _record_of(raw_data: Mapping[str, Any] | None) -> dict[str, Any]:
    """The call's ``global_data``, as the platform sent it with a request."""
    data = raw_data.get("global_data") if isinstance(raw_data, Mapping) else None
    return dict(data) if isinstance(data, Mapping) else {}


def _update(data: Mapping[str, Any], **changes: Any) -> dict[str, Any]:
    """The ``global_data`` update for these changes, with ``now`` worked out after them."""
    return {**changes, "now": _now_line({**data, **changes})}


def _now_line(data: Mapping[str, Any]) -> str:
    """Where the call stands, in words: what they asked for, what's done, what waits for their answer, and what's
    set aside for after it."""
    done = " ".join(h["done"] for h in data.get("history") or [] if h.get("done"))
    waiting, queued = data.get("waiting") or {}, data.get("queued") or []
    parts = [
        f"What they asked for: {data['asked']}" if data.get("asked") else "",
        f"Done in this call: {done}" if done else "",
        f'Waiting for their answer: "{waiting["read_back"]}"' if waiting.get("read_back") else "",
        ("Set aside, to do next: " + " ".join(f'"{q["read_back"]}"' for q in queued)) if queued else "",
    ]
    return "\n".join(p for p in parts if p)


def _waiting_entry(kind: str, args: Mapping[str, Any], change: Change, revision: int) -> dict[str, Any]:
    """A change as it waits for the caller's yes: everything needed to carry it out, frozen."""
    return {
        "kind": kind,
        "read_back": change.read_back,
        "touches": list(change.touches),
        "writes": [w.to_dict() for w in change.writes],
        "money": change.money_moved(),
        "done": change.done_lines(),
        "args": dict(args),
        "revision": revision,
    }


def _queued_entry(kind: str, args: Mapping[str, Any], change: Change) -> dict[str, Any]:
    """A change set aside for after the one waiting, kept with the arguments to build it again."""
    return {"kind": kind, "read_back": change.read_back, "touches": list(change.touches), "args": dict(args)}


def _settle(data: Mapping[str, Any], outcome: str, done: str = "", made: int = 0) -> dict[str, Any]:
    """
    The change waiting, settled into history: how (made, not made, declined,
    replaced), what was done, and the money moved by the writes that went
    through (all of them once made, else the first ``made``).
    """
    waiting = data.get("waiting") or {}
    moved = [float(m) for m in waiting.get("money") or []]
    entry = {
        "kind": waiting.get("kind", ""),
        "touches": list(waiting.get("touches") or []),
        "read_back": waiting.get("read_back", ""),
        "outcome": outcome,
        "done": done,
        "money": round(sum(moved if outcome == "made" else moved[:made]), 2),
    }
    return {"waiting": {}, "history": list(data.get("history") or []) + [entry]}


def _money(amount: float) -> str:
    return f"${abs(amount):,.2f}"


def _joined(parts: Sequence[str]) -> str:
    parts = [p for p in parts if p]
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1] if parts else ""


def _in_all(history: Sequence[Mapping[str, Any]]) -> str:
    """What the changes made in the call come to, once more than one moved money."""
    moved = [float(h.get("money") or 0) for h in history if h.get("money")]  # only writes that went through count
    if len(moved) < 2:
        return ""
    back, charged = -sum(m for m in moved if m < 0), sum(m for m in moved if m > 0)
    parts = ([f"{_money(back)} back to them"] if back > 0.005 else []) + (
        [f"{_money(charged)} charged"] if charged > 0.005 else []
    )
    return f" In all, the changes made in this call come to {_joined(parts)}." if parts else ""


def _next_up(data: Mapping[str, Any], tool_of: Mapping[str, str]) -> str:
    """What to do once the change waiting is settled: take up the first one set aside."""
    queued = data.get("queued") or []
    if not queued:
        return ""
    first = queued[0]
    return f' Then, as they asked, call {tool_of.get(first["kind"], "its tool")} again for the change set aside: "{first["read_back"]}"'


__all__ = ["RECORD_KEYS"]
