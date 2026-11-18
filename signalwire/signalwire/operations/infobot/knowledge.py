"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

A knowledge-search layer an agent installs to answer callers from a corpus.
"""

from __future__ import annotations

from typing import Any, Callable

from signalwire import AgentBase, FunctionResult


class InfoBotKnowledge:
    """Knowledge search installed on an agent.

    ``search(query)`` returns the text the model answers from — already ranked
    and formatted. Governance (which results to keep, how to label them, what
    rule binds to them) is the caller's to supply inside ``search``, so any
    backend fits and nothing about ranking leaks into this layer.

    Compose with ``Operations`` by installing this FIRST, then ``Operations``::

        InfoBotKnowledge(search=my_search).install(agent)
        ops.install(agent)   # joins: main keeps search_knowledge, gains the op tools

    The generated ``main`` step then offers ``search_knowledge`` beside the
    operation tools, and the conscience carries this layer's per-turn record
    line (``${global_data.<namespace>.now}``) ahead of Operations' own.
    """

    def __init__(
        self,
        search: Callable[[str], str],
        *,
        tool: str = "search_knowledge",
        description: str = "Search the documentation and answer only from the results.",
        namespace: str = "infobot",
    ) -> None:
        self._search = search
        self._tool = tool
        self._description = description
        self._namespace = namespace

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
        return FunctionResult(self._search(query))

    def _ensure_main(self, agent: AgentBase) -> None:
        step = agent.define_contexts().add_context("default").add_step("main")
        step.add_section("Knowledge", f"Answer the caller's question from {self._tool}, not memory.")
        step.set_functions([self._tool])

    def _compose_conscience(self, agent: AgentBase) -> None:
        # Match Operations: append this layer's record line to whatever conscience
        # is already set, a blank line between, never replacing it.
        line = "${global_data.%s.now}" % self._namespace
        existing = getattr(agent, "_params", {}).get("conscience", "")
        agent.set_param("conscience", f"{existing}\n\n{line}" if existing else line)
