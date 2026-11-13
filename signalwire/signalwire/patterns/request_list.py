"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

What the caller asked for while the agent was busy with something else.

A caller in the middle of one task often asks for another: "and can you also
check my balance?" Taking it up at once loses the first task; ignoring it
loses the second. A tool notes the request, and the agent tells the caller
it's noted for right after this. When the first task is done, the step's
text, which shows the list, has the agent take up the next one.

The list lives in the call's ``global_data``, so it lasts for the call and a
step's text can show it, as ``${global_data.<key>_text}``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from signalwire.core.function_result import FunctionResult


class RequestList:
    """
    The caller's requests to come back to, in the order they asked.

    Example:
        later = RequestList("later", openers={
            "balance": "You also asked about your balance.",
            "question": "You had a question: {about}.",
        })

        agent.set_global_data(later.defaults())

        def note_request(args, raw_data):
            return later.note(raw_data, args["kind"], args["about"])

        ctx.add_step("take_order").set_text(
            "Take the caller's order.\\n\\n${global_data.later_text}")

    A step's text is expanded when the step is entered, so the list it
    shows is the one from then; the model hears of each new request in the
    tool result. Return ``refresh_step()`` with the note to show it at once.
    """

    def __init__(
        self,
        global_key: str,
        *,
        openers: Mapping[str, str] | None = None,
        heading: str = "Noted for right after this:",
    ) -> None:
        """
        Args:
            global_key: The ``global_data`` key the list is kept under. Its
                text for step text is kept under ``<global_key>_text``.
            openers: How the agent opens each kind of request when it takes
                it up, keyed by kind, with ``{about}`` for what it's about.
                A kind without one opens with what it's about.
            heading: The first line of the list's text.
        """
        self.global_key = global_key
        self.text_key = f"{global_key}_text"
        self.openers = dict(openers or {})
        self.heading = heading

    def defaults(self) -> dict[str, Any]:
        """The ``global_data`` to start a call with, an empty list, so step
        text that shows it has a value before anything is noted."""
        return {self.global_key: [], self.text_key: ""}

    def pending(self, raw_data: Mapping[str, Any] | None) -> list[dict[str, str]]:
        """The requests a call has noted, oldest first, from its request's
        ``global_data``."""
        if not isinstance(raw_data, Mapping):
            return []
        global_data = raw_data.get("global_data")
        stored = (
            global_data.get(self.global_key)
            if isinstance(global_data, Mapping)
            else None
        )
        if not isinstance(stored, list):
            return []
        return [
            {"kind": str(r.get("kind", "")), "about": str(r.get("about", ""))}
            for r in stored
            if isinstance(r, Mapping)
        ]

    def note(
        self,
        raw_data: Mapping[str, Any] | None,
        kind: str,
        about: str,
        result: FunctionResult | None = None,
    ) -> FunctionResult:
        """
        Note a request to come back to, and tell the model so.

        The model gets "Noted for right after this: <about>.", with a tool
        prompt to tell the caller and carry on with what it was doing. The
        same request noted twice is kept once.

        Args:
            raw_data: The noting call's request.
            kind: The kind of request, one of the app's (it picks the
                opener).
            about: What it's about, in a few words.
            result: A result to add to.
        """
        requests = self.pending(raw_data)
        entry = {"kind": kind, "about": about}
        if entry not in requests:
            requests.append(entry)
        result = result if result is not None else FunctionResult()
        result.set_tool_response(
            tool_result=f"Noted for right after this: {about}.",
            tool_prompt=(
                "Tell the caller you've noted it for right after this, and carry on "
                "with what you were doing."
            ),
        )
        return self._store(result, requests)

    def next(self, raw_data: Mapping[str, Any] | None) -> dict[str, str] | None:
        """The oldest request not yet taken up, with its ``opener``, or None."""
        requests = self.pending(raw_data)
        if not requests:
            return None
        first = requests[0]
        return {**first, "opener": self.opener(first)}

    def done(
        self,
        raw_data: Mapping[str, Any] | None,
        result: FunctionResult | None = None,
    ) -> FunctionResult:
        """
        Remove the oldest request, once it has been taken up.

        Args:
            raw_data: The call's request.
            result: A result to add to.
        """
        requests = self.pending(raw_data)[1:]
        return self._store(result if result is not None else FunctionResult(), requests)

    def opener(self, request: Mapping[str, str]) -> str:
        """How the agent opens a request when it takes it up."""
        about = str(request.get("about", ""))
        template = self.openers.get(str(request.get("kind", "")))
        return template.replace("{about}", about) if template else about

    def as_text(self, requests: list[dict[str, str]]) -> str:
        """The list as step text: the heading and one numbered line a
        request, or "" when there are none."""
        if not requests:
            return ""
        lines = [self.heading]
        lines += [f"{n}. {self.opener(r)}" for n, r in enumerate(requests, 1)]
        lines.append(
            "When the current task is done, take these up in order, then ask if "
            "there's anything else."
        )
        return "\n".join(lines)

    def _store(
        self, result: FunctionResult, requests: list[dict[str, str]]
    ) -> FunctionResult:
        return result.update_global_data(
            {self.global_key: requests, self.text_key: self.as_text(requests)}
        )
