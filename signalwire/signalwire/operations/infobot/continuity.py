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

from signalwire import AgentBase

from signalwire.operations.infobot.legs import LegStore

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


def default_conversation_id(raw_data: dict[str, Any] | None) -> str:
    """The conversation id for a request: the chat conversation_id, else the
    platform call id. Never a page-supplied value."""
    d = raw_data or {}
    return str(
        d.get("conversation_id")
        or (d.get("call") or {}).get("call_id")
        or d.get("call_id")
        or ""
    )


class Continuity:
    """Carry a conversation across a voice<->chat switch.

    Install on any ``AgentBase``: on each request it seeds the resuming leg with
    the prior dialog (via :func:`build_seed`), and at each leg's end it records
    that leg's transcript so the next one can continue. Persistence is a
    :class:`LegStore` (swap its backend with ``store.set_store``); the medium and
    the switch directive come from :func:`medium_of` / ``switch_note``.
    """

    def __init__(
        self,
        *,
        store: LegStore | None = None,
        include_tools: bool = True,
        switch_note: Callable[[str, str], str] = default_switch_note,
        resolve_id: Callable[[dict[str, Any]], str] | None = None,
        report: Callable[[dict[str, Any]], None] | None = None,
        visitor_context: Callable[[dict[str, Any]], dict[str, Any] | None]
        | None = None,
    ) -> None:
        self._store = store or LegStore()
        self._include_tools = include_tools
        self._switch_note = switch_note
        self._resolve_id = resolve_id
        self._report = report
        self._visitor_context = visitor_context

    @property
    def store(self) -> LegStore:
        return self._store

    def resolve_conversation_id(self, raw_data: dict[str, Any] | None) -> str:
        return (self._resolve_id or default_conversation_id)(raw_data or {})

    def install(self, agent: AgentBase) -> AgentBase:
        agent.set_dynamic_config_callback(self._seed_callback)
        agent.on_call_end(self._capture_leg)
        return agent

    def _seed_callback(
        self,
        query_params: dict[str, Any],
        body: dict[str, Any],
        headers: dict[str, Any],
        agent: AgentBase,
    ) -> None:
        if self._visitor_context is not None:
            ctx = self._visitor_context(body)
            if ctx:
                agent.set_global_data(ctx)
        cid = self.resolve_conversation_id(body)
        if not cid:
            return
        legs = self._store.legs(LegStore.root_id(cid))
        convo = build_seed(
            legs,
            medium_of(body),
            include_tools=self._include_tools,
            switch_note=self._switch_note,
        )
        if convo:
            agent.set_params({"convo": convo})

    def _capture_leg(
        self, call_log: list[dict[str, Any]], raw_data: dict[str, Any]
    ) -> None:
        cid = self.resolve_conversation_id(raw_data)
        if not cid:
            return
        turns = [
            t
            for t in (call_log or [])
            if isinstance(t, dict)
            and t.get("role") in ("user", "assistant", "system", "tool")
        ]
        root = LegStore.root_id(cid)
        self._store.record(root, {"cid": cid, "turns": turns})
        # Hand the whole conversation so far to the report sink. The record is
        # complete at every leg end (the last one covers the full conversation),
        # so a sink can simply keep the latest. Default: no report.
        if self._report is not None:
            self._report({"conversation_id": root, "legs": self._store.legs(root)})
