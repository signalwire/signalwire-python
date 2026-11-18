"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

A knowledge-search layer an agent installs to answer callers from a corpus.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from signalwire import AgentBase, FunctionResult

Result = dict[str, Any]


class InfoBotKnowledge:
    """Knowledge search installed on an agent.

    ``search(query)`` returns the raw results (each a dict with at least a
    ``content`` string and a ``score``); the layer governs them — drops some,
    ranks some last, labels each — and hands the model one grounded block. The
    backend stays the caller's (``search`` can be pgvector, HTTP, DataSphere),
    and the *policy* is three optional hooks, so nothing about a particular
    corpus is baked in here:

    - ``set_exclude(fn)``  — ``fn(result, query) -> bool``: drop the result.
    - ``set_demote(fn)``   — ``fn(result) -> bool``: rank it after the rest.
    - ``set_result_context(fn)`` — ``fn(result) -> str | None``: a label line
      shown above the passage (authority, kind, title, source url…).

    Compose with ``Operations`` by installing this FIRST, then ``Operations``;
    the generated ``main`` step keeps ``search_knowledge`` and gains the
    operation tools, and each layer's record line stays in its own
    ``global_data`` namespace.
    """

    _GROUNDING = (
        "Answer only from these results. If they do not cover it, say so plainly "
        "- do not fill the gap from general knowledge."
    )

    def __init__(
        self,
        search: Callable[[str], list[Result]],
        *,
        tool: str = "search_knowledge",
        description: str = "Search the documentation and answer only from the results.",
        namespace: str = "infobot",
        result_limit: int = 5,
        grounding: str = _GROUNDING,
    ) -> None:
        self._search = search
        self._tool = tool
        self._description = description
        self._namespace = namespace
        self._result_limit = result_limit
        self._grounding = grounding
        self._exclude: Callable[[Result, str], bool] | None = None
        self._demote: Callable[[Result], bool] | None = None
        self._context: Callable[[Result], str | None] | None = None

    # -- governance hooks --------------------------------------------------

    def set_exclude(self, fn: Callable[[Result, str], bool]) -> InfoBotKnowledge:
        """Drop a result before the cut when ``fn(result, query)`` is true."""
        self._exclude = fn
        return self

    def set_demote(self, fn: Callable[[Result], bool]) -> InfoBotKnowledge:
        """Rank a result after all non-demoted ones when ``fn(result)`` is true."""
        self._demote = fn
        return self

    def set_result_context(self, fn: Callable[[Result], str | None]) -> InfoBotKnowledge:
        """A label line shown above a result's passage; ``None`` adds none."""
        self._context = fn
        return self

    # -- install -----------------------------------------------------------

    def install(self, agent: AgentBase) -> AgentBase:
        """Add the search tool, the ``main`` step and the conscience line."""
        self._define_search(agent)
        self._ensure_main(agent)
        self._compose_conscience(agent)
        return agent

    def _define_search(self, agent: AgentBase) -> None:
        agent.define_tool(
            self._tool,
            f"{self._description} Changes nothing.",
            {"query": {"type": "string", "description": "What to look up, in the caller's words."}},
            self._handle_search,
            required=["query"],
        )

    def _handle_search(self, args: dict[str, Any], raw: Any) -> FunctionResult:
        query = ((args or {}).get("query") or "").strip()
        if not query:
            return FunctionResult("Ask them what to look up - there was no query.")
        return FunctionResult(self._format(query, list(self._search(query) or [])))

    def _format(self, query: str, results: list[Result]) -> str:
        kept = [r for r in results if not (self._exclude and self._exclude(r, query))]
        # Highest score first; a demoted result always sorts after a kept one.
        kept.sort(key=lambda r: (1 if (self._demote and self._demote(r)) else 0, -_score(r)))
        kept = kept[: self._result_limit]
        if not kept:
            return f"{self._grounding}\n\nThe results do not cover it."
        blocks = [self._grounding]
        for r in kept:
            label = self._context(r) if self._context else None
            passage = str(r.get("content") or r.get("text") or "").strip()
            blocks.append(f"{label}\n{passage}" if label else passage)
        return "\n\n".join(blocks)

    def _ensure_main(self, agent: AgentBase) -> None:
        step = agent.define_contexts().add_context("default").add_step("main")
        step.add_section("Knowledge", f"Answer the caller's question from {self._tool}, not memory.")
        step.set_functions([self._tool])

    def _compose_conscience(self, agent: AgentBase) -> None:
        # Match Operations: append this layer's record line to whatever conscience
        # is already set, a blank line between, never replacing it.
        line = f"${{global_data.{self._namespace}.now}}"
        existing = getattr(agent, "_params", {}).get("conscience", "")
        agent.set_param("conscience", f"{existing}\n\n{line}" if existing else line)


def _score(result: Result) -> float:
    try:
        return float(result.get("score") or 0.0)
    except (TypeError, ValueError):
        return 0.0
