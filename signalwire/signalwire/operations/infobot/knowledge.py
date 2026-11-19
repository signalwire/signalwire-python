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

    With ``contact`` set, a second tool records a caller's details for a human
    follow-up. Both tools re-enable back-to-back calls on their result, so a
    refused gate elsewhere in a composed agent does not strand the model
    one-tool-per-turn.

    Compose with ``Operations`` by installing this FIRST, then ``Operations``;
    the generated ``main`` step keeps these tools and gains the operation ones,
    and each layer's record line stays in its own ``global_data`` namespace.
    """

    _GROUNDING = (
        "Answer only from these results. If they do not cover it, say so plainly "
        "- do not fill the gap from general knowledge."
    )

    def __init__(
        self,
        search: Callable[[str], list[Result]] | None = None,
        *,
        tool: str = "search_knowledge",
        description: str = "Search the documentation and answer only from the results.",
        namespace: str = "infobot",
        result_limit: int = 5,
        grounding: str = _GROUNDING,
        contact: Callable[[dict[str, Any]], None] | None = None,
        contact_tool: str = "collect_contact",
    ) -> None:
        self._search = search
        self._tool = tool
        self._description = description
        self._namespace = namespace
        self._result_limit = result_limit
        self._grounding = grounding
        self._contact = contact
        self._contact_tool = contact_tool
        self._exclude: Callable[[Result, str], bool] | None = None
        self._demote: Callable[[Result], bool] | None = None
        self._context: Callable[[Result], str | None] | None = None
        self._rules: list[tuple[str, str]] = []
        self._result_rules: list[tuple[Callable[[str, list[Result]], bool], str]] = []
        self._query_types: dict[str, str] = {}
        self._query_type_help: str = ""

    # -- governance hooks --------------------------------------------------

    def set_exclude(self, fn: Callable[[Result, str], bool]) -> InfoBotKnowledge:
        """Drop a result before the cut when ``fn(result, query)`` is true."""
        self._exclude = fn
        return self

    def set_demote(self, fn: Callable[[Result], bool]) -> InfoBotKnowledge:
        """Rank a result after all non-demoted ones when ``fn(result)`` is true."""
        self._demote = fn
        return self

    def set_result_context(
        self, fn: Callable[[Result], str | None]
    ) -> InfoBotKnowledge:
        """A label line shown above a result's passage; ``None`` adds none."""
        self._context = fn
        return self

    def add_rule(self, text: str, *, when: str = "results") -> InfoBotKnowledge:
        """A grounding line added to the block. ``when`` is "results" (only when
        there are results), "empty" (only when there are none), or "always".
        With no rules added, the ``grounding`` line is used as the default."""
        self._rules.append((text, when))
        return self

    def add_result_rule(
        self, predicate: Callable[[str, list[Result]], bool], text: str
    ) -> InfoBotKnowledge:
        """A line added after the passages when ``predicate(query, results)`` is true."""
        self._result_rules.append((predicate, text))
        return self

    def _rules_for(self, state: str) -> list[str]:
        lines = [t for t, w in self._rules if w in (state, "always")]
        return lines or [self._grounding]

    def add_query_type(self, kind: str, qualifier: str) -> InfoBotKnowledge:
        """Register a query kind whose ``qualifier`` is appended to the search
        query (not the grounding) when the model picks it. Exposes a
        ``query_type`` argument on the search tool once any kind is registered."""
        self._query_types[kind] = qualifier
        return self

    def set_query_type_help(self, text: str) -> InfoBotKnowledge:
        """How the model should choose a ``query_type`` (the argument's description)."""
        self._query_type_help = text
        return self

    def use_search_service(
        self,
        url: str,
        *,
        user: str = "",
        password: str = "",
        index_name: str = "default",
        count: int = 10,
        timeout: float = 10.0,
    ) -> InfoBotKnowledge:
        """Use a SignalWire search service at ``url`` as the backend instead of a
        hand-written ``search`` callable: an HTTP ``POST <url>/search`` of
        ``{query, index_name, count}`` (optional basic auth) returning ``results``."""
        endpoint = url.rstrip("/")
        if not endpoint.endswith("/search"):
            endpoint += "/search"
        auth = (user, password) if (user or password) else None

        def backend(query: str) -> list[Result]:
            import requests

            resp = requests.post(
                endpoint,
                json={"query": query, "index_name": index_name, "count": count},
                auth=auth,
                timeout=timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results") if isinstance(data, dict) else data
            return list(results or [])

        self._search = backend
        return self

    # -- install -----------------------------------------------------------

    def install(self, agent: AgentBase) -> AgentBase:
        """Add the tools, the ``main`` step and the conscience line."""
        if self._search is None:
            raise ValueError(
                "InfoBotKnowledge needs a search backend: pass search=fn or call "
                "use_search_service(...) before install()."
            )
        self._define_search(agent)
        if self._contact is not None:
            self._define_contact(agent)
        self._ensure_main(agent)
        self._compose_conscience(agent)
        return agent

    def _define_search(self, agent: AgentBase) -> None:
        params: dict[str, Any] = {
            "query": {
                "type": "string",
                "description": "What to look up, in the caller's words.",
            }
        }
        if self._query_types:
            params["query_type"] = {
                "type": "string",
                "enum": sorted(self._query_types),
                "description": self._query_type_help or "The kind of lookup.",
            }
        agent.define_tool(
            self._tool,
            f"{self._description} Changes nothing.",
            params,
            self._handle_search,
            required=["query"],
        )

    def _handle_search(self, args: dict[str, Any], raw: Any) -> FunctionResult:
        args = args or {}
        query = (args.get("query") or "").strip()
        if not query:
            return FunctionResult("Ask them what to look up - there was no query.")
        search = self._search
        if search is None:
            return FunctionResult("Search isn't configured.")
        # The qualifier aids retrieval only; grounding stays the caller's own words.
        qualifier = self._query_types.get((args.get("query_type") or "").strip())
        effective = f"{query} {qualifier}" if qualifier else query
        blob = self._format(query, list(search(effective) or []))
        return FunctionResult(blob).back_to_back_functions("forever")

    def _format(self, query: str, results: list[Result]) -> str:
        kept = [r for r in results if not (self._exclude and self._exclude(r, query))]
        # Highest score first; a demoted result always sorts after a kept one.
        kept.sort(
            key=lambda r: (1 if (self._demote and self._demote(r)) else 0, -_score(r))
        )
        kept = kept[: self._result_limit]
        if not kept:
            return "\n\n".join(
                [*self._rules_for("empty"), "The results do not cover it."]
            )
        blocks = self._rules_for("results")
        for r in kept:
            label = self._context(r) if self._context else None
            passage = str(r.get("content") or r.get("text") or "").strip()
            blocks.append(f"{label}\n{passage}" if label else passage)
        for predicate, text in self._result_rules:
            if predicate(query, kept):
                blocks.append(text)
        return "\n\n".join(blocks)

    def _define_contact(self, agent: AgentBase) -> None:
        agent.define_tool(
            self._contact_tool,
            "Record the caller's contact details for a human follow-up. Call this "
            "only after they have agreed they would like someone to follow up.",
            {
                "name": {"type": "string", "description": "The caller's name."},
                "email": {
                    "type": "string",
                    "description": "An email address to reach them.",
                },
                "topic": {
                    "type": "string",
                    "description": "What they want followed up, in brief.",
                },
            },
            self._handle_contact,
            required=["email"],
        )

    def _handle_contact(self, args: dict[str, Any], raw: Any) -> FunctionResult:
        fields: dict[str, Any] = {
            k: str((args or {}).get(k) or "").strip()
            for k in ("name", "email", "topic")
        }
        if not fields["email"]:
            return FunctionResult("Ask them for an email address to reach them at.")
        if self._contact is not None:
            self._contact(fields)
        return FunctionResult(
            "Thanks - I've passed that along and someone will follow up."
        ).back_to_back_functions("forever")

    def _ensure_main(self, agent: AgentBase) -> None:
        step = agent.define_contexts().add_context("default").add_step("main")
        step.add_section(
            "Knowledge", f"Answer the caller's question from {self._tool}, not memory."
        )
        tools = [self._tool]
        if self._contact is not None:
            tools.append(self._contact_tool)
        step.set_functions(tools)

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
