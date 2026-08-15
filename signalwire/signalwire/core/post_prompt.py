#!/usr/bin/env python3
"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Post-prompt normalization.

One conversation can run over voice and over text chat, and both ends produce
"the post-prompt" -- but they do not produce the same shape, and the
differences are not documented anywhere a caller would find them. This module
absorbs that divergence so an application sees one artifact regardless of which
engine finished the conversation.

Known divergences between the two engines:

===================  =========================  ============================
field                voice                      chat
===================  =========================  ============================
``app_name``         ``"swml app"``             ``"ai_chat"``
``conversation_id``  absent                     present at top level
full log             ``raw_call_log``           ``raw_messages``
summary arrives as   ``summarize_conversation`` a bare ``role: assistant``
                     tool call                  turn inside ``call_log``
``post_prompt_data`` parsed object              ``{"raw": "```json ...```"}``
===================  =========================  ============================

``conversation_type`` is a reliable top-level discriminator on both.

There is also a *third* ``post_prompt_data`` shape seen from the voice engine:
``{"parsed": [ {...} ], "raw": "..."}`` -- the object wrapped in a list under
``parsed``. It survives structurally and misses every field lookup, so a caller
that does not handle it silently gets nothing while appearing to work.

What this module does NOT do is decide what a summary should contain. The
schema is the application's -- it is whatever its post-prompt text asked the
model to produce -- so parsing here is deliberately schema-agnostic and returns
the dict as found.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "DIALOGUE_ROLES",
    "NormalizedPostPrompt",
    "dialogue_turns",
    "normalize_post_prompt",
    "parse_post_prompt_data",
    "strip_json_fence",
]

# Roles that are actual dialogue. Everything else in a call log is machinery:
# ``system`` is the prompt, ``system-log`` is lifecycle and step tracing,
# ``tool`` is function output, and ``assistant-manual`` is filler speech
# ("let me look that up") that was spoken but carries nothing worth replaying.
DIALOGUE_ROLES: tuple[str, ...] = ("user", "assistant")

_FENCE_OPEN = re.compile(r"^```[a-zA-Z]*\s*")
_FENCE_CLOSE = re.compile(r"\s*```$")


@dataclass(frozen=True)
class NormalizedPostPrompt:
    """One finished conversation leg, in a shape that does not vary by engine.

    Attributes:
        medium: ``conversation_type`` as reported, e.g. ``"voice"`` or
            ``"chat"``. Empty string when the engine did not say.
        conversation_id: Present on chat, absent on voice. ``None`` when the
            engine did not supply one -- callers that need a stable key should
            fall back to their own (``global_data``, ``call_id``) rather than
            treating this as authoritative.
        summary: The parsed ``post_prompt_data``, whatever keys the
            application's post-prompt asked for. ``{}`` when there was none or
            it could not be parsed at all. A model that answered in prose
            instead of JSON yields ``{"summary": "<the prose>"}`` -- a usable
            paragraph is better than a discarded one.
        dialogue: ``user``/``assistant`` turns only, with tool calls and the
            chat engine's summary echo removed.
        call_id: The platform call id, when present.
        raw: The complete request body, untouched.
    """

    medium: str = ""
    conversation_id: str | None = None
    summary: dict[str, Any] = field(default_factory=dict)
    dialogue: list[dict[str, str]] = field(default_factory=list)
    call_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


def strip_json_fence(text: str) -> str:
    """Unwrap ```` ```json ... ``` ```` fencing.

    The chat engine hands the model's answer back verbatim, fence and all,
    where the voice engine parses it first.
    """
    stripped = (text or "").strip()
    if stripped.startswith("```"):
        stripped = _FENCE_OPEN.sub("", stripped)
        stripped = _FENCE_CLOSE.sub("", stripped)
    return stripped.strip()


def _unwrap_parsed(data: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the object out of a ``{"parsed": [...]}`` wrapper, if present.

    Checked before the generic sweep, which would otherwise happily return
    ``{"parsed": [...]}`` -- structurally fine, semantically empty, and every
    subsequent field lookup misses without anything indicating why.
    """
    parsed = data.get("parsed")
    if isinstance(parsed, dict):
        return parsed
    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict) and item:
                return item
    return None


def parse_post_prompt_data(data: Any) -> dict[str, Any]:
    """Return ``post_prompt_data`` as a plain dict, whichever shape it arrived in.

    Never raises. The conversation that produced this is already over and there
    is nobody to show an error to, so a malformed summary degrades rather than
    failing the request that delivered it.

    Args:
        data: The ``post_prompt_data`` value from a post-prompt body.

    Returns:
        The summary object, or ``{}`` when there is nothing usable.
    """
    if not isinstance(data, dict):
        return {}

    unwrapped = _unwrap_parsed(data)
    if unwrapped:
        return unwrapped

    # Flat shape: real keys already present (anything but raw/parsed).
    flat = {k: v for k, v in data.items() if k not in ("raw", "parsed")}
    if flat:
        return flat

    raw = data.get("raw")
    if not isinstance(raw, str) or not raw.strip():
        return {}
    unfenced = strip_json_fence(raw)
    try:
        loaded = json.loads(unfenced)
    except (ValueError, TypeError):
        # Prose instead of JSON. Still a summary.
        return {"summary": unfenced}
    return loaded if isinstance(loaded, dict) else {"summary": str(loaded)}


def dialogue_turns(
    call_log: Any,
    *,
    roles: tuple[str, ...] = DIALOGUE_ROLES,
    drop_echo: str | None = None,
) -> list[dict[str, str]]:
    """Extract the real dialogue from a call log.

    Drops everything that is machinery rather than speech: non-dialogue roles,
    entries carrying ``tool_calls``, and empty content.

    ``drop_echo`` exists for one specific engine behaviour. The chat engine
    appends its own post-prompt output to ``call_log`` as a bare
    ``role: assistant`` entry with no ``tool_calls`` -- by role alone it is
    indistinguishable from real assistant speech. Replayed into another medium,
    the agent appears to narrate a summary of itself in the third person. It is
    identifiable only by content, being byte-identical to
    ``post_prompt_data.raw``, which is what this parameter compares against.
    The voice engine delivers the same artifact as a ``summarize_conversation``
    tool call, which the ``tool_calls`` check already removes.

    Args:
        call_log: The log, as ``call_log`` / ``raw_call_log`` / ``raw_messages``.
        roles: Roles to keep.
        drop_echo: Exact content to treat as the summary echo and drop.

    Returns:
        ``[{"role": ..., "content": ...}, ...]`` in order.
    """
    # Guarded rather than relying on `call_log or []`: a non-iterable value
    # (an int, say, from a malformed body) is truthy and would raise on
    # iteration. Nothing in this module may raise -- the conversation that
    # produced the input is already over.
    if not isinstance(call_log, (list, tuple)):
        return []

    out: list[dict[str, str]] = []
    echo = (drop_echo or "").strip()
    for entry in call_log:
        if not isinstance(entry, dict):
            continue
        if entry.get("role") not in roles:
            continue
        if entry.get("tool_calls"):
            continue
        content = entry.get("content")
        if not isinstance(content, str) or not content.strip():
            continue
        if echo and content.strip() == echo:
            continue
        out.append({"role": entry["role"], "content": content})
    return out


def normalize_post_prompt(body: Any) -> NormalizedPostPrompt:
    """Normalize a post-prompt body from either engine.

    Args:
        body: The complete post-prompt request body.

    Returns:
        A :class:`NormalizedPostPrompt`. Never raises; a body this function
        cannot make sense of yields one with empty fields.

    Example:
        leg = normalize_post_prompt(raw_body)
        if leg.dialogue:
            store(leg.conversation_id, leg.medium, leg.summary, leg.dialogue)
    """
    if not isinstance(body, dict):
        return NormalizedPostPrompt()

    summary = parse_post_prompt_data(body.get("post_prompt_data"))

    # The echo is compared against the RAW string the engine returned, not the
    # parsed summary -- the assistant turn carries the fence too.
    raw_summary = ""
    ppd = body.get("post_prompt_data")
    if isinstance(ppd, dict) and isinstance(ppd.get("raw"), str):
        raw_summary = ppd["raw"]

    log = (
        body.get("call_log")
        or body.get("raw_call_log")
        or body.get("raw_messages")
        or []
    )

    return NormalizedPostPrompt(
        medium=str(body.get("conversation_type") or ""),
        conversation_id=body.get("conversation_id") or None,
        summary=summary,
        dialogue=dialogue_turns(log, drop_echo=raw_summary or None),
        call_id=body.get("call_id") or None,
        raw=body,
    )
