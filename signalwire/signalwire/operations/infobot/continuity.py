"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Cross-medium continuity: seed a resuming leg with the prior conversation.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

Turn = dict[str, Any]


def medium_of(body: dict[str, Any] | None) -> str:
    """Which medium a request belongs to: ``"voice"`` or ``"chat"``.

    The platform sends ``conversation_type`` on the SWML request; it may also
    have been copied into user variables or global data for a later tool request
    that doesn't carry it. Anything unrecognised is voice, because voice is where
    getting it wrong is audible.
    """
    d = body or {}
    ct = (
        d.get("conversation_type")
        or ((d.get("vars") or {}).get("userVariables") or {}).get("conversation_type")
        or (d.get("global_data") or {}).get("conversation_type")
        or "voice"
    )
    return "chat" if str(ct).strip().lower() == "chat" else "voice"


def pair_tools(convo: list[Turn]) -> list[Turn]:
    """Enforce the convo tool-pairing rule: every assistant ``tool_calls`` turn
    must be followed by a ``tool`` result for each call id, and every ``tool``
    result must answer a call that is present. Orphan results are dropped, and an
    assistant turn whose results did not survive is dropped (an unanswered call
    is an invalid request). Plain turns pass through untouched.
    """
    result_ids = {
        m.get("tool_call_id")
        for m in convo
        if m.get("role") == "tool" and m.get("tool_call_id")
    }
    out: list[Turn] = []
    kept_call_ids: set[Any] = set()
    for m in convo:
        if m.get("role") == "assistant" and m.get("tool_calls"):
            kept = [tc for tc in m["tool_calls"] if tc.get("id") in result_ids]
            if not kept:
                continue
            m = {**m, "tool_calls": kept}
            kept_call_ids.update(tc.get("id") for tc in kept)
            out.append(m)
        elif m.get("role") == "tool":
            if m.get("tool_call_id") in kept_call_ids:
                out.append(m)
        else:
            out.append(m)
    return out


def default_switch_note(prev: str, now: str) -> str:
    """The trailing system directive after a medium switch."""
    return (
        f"The conversation has just switched from {prev} to {now}. Everything "
        f"above was already handled on {prev}. Do NOT re-answer, re-explain, or "
        f"re-search anything above. Briefly acknowledge the switch to {now}, then "
        f"ask what they would like to look at next."
    )


def build_seed(
    legs: list[dict[str, Any]],
    now_medium: str,
    *,
    include_tools: bool = True,
    switch_note: Callable[[str, str], str] = default_switch_note,
) -> list[Turn]:
    """Build the ``convo`` seed for a resuming leg from the prior legs.

    Seeds from the LATEST leg that has a dialog — each leg launched WITH the
    accumulated convo, so concatenating every leg would duplicate it and make the
    model re-answer. Dedupes, enforces tool pairing, then appends two trailing
    turns: a user turn recording the switch the caller just made (so the step's
    focus lines up with the switch, not the old question) and a system directive
    not to re-answer. Returns the convo list, or ``[]`` when there is nothing to
    carry.
    """
    dialog: list[Turn] = []
    for leg in reversed(legs or []):
        turns = leg.get("turns")
        if turns:
            dialog = turns
            break
    if not dialog:
        return []

    convo: list[Turn] = []
    seen: set[tuple[Any, ...]] = set()
    for t in dialog:
        role = t.get("role")
        if not include_tools and (role == "tool" or t.get("tool_calls")):
            continue
        content = t.get("content") or ""
        if (
            role in ("user", "assistant", "system")
            and not str(content).strip()
            and not t.get("tool_calls")
        ):
            continue
        key = (
            role,
            content,
            json.dumps(t.get("tool_calls") or ""),
            t.get("tool_call_id") or "",
        )
        if key in seen:
            continue
        seen.add(key)
        m: Turn = {"role": role, "content": content}
        if t.get("tool_calls"):
            m["tool_calls"] = t["tool_calls"]
        if t.get("tool_call_id"):
            m["tool_call_id"] = t["tool_call_id"]
        convo.append(m)

    convo = pair_tools(convo)
    if not convo:
        return []

    prev = "chat" if now_medium == "voice" else "voice"
    convo.append({"role": "user", "content": f"I want to switch to {now_medium}."})
    convo.append({"role": "system", "content": switch_note(prev, now_medium)})
    return convo
