"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

A knowledge-search layer an agent installs to answer callers from a corpus.
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Mapping, Sequence
from types import MappingProxyType
from typing import Any, cast

from signalwire import AgentBase, FunctionResult
from signalwire.operations.model import Field
from signalwire.operations.wording import _Wording

Result = dict[str, Any]

KNOWLEDGE_WORDING: Mapping[str, str] = MappingProxyType(
    {
        "tool.search": "{description} Changes nothing.",
        "tool.search.query": "What to look up, in the caller's words.",
        "tool.search.query_type": "The kind of lookup.",
        "search.no_query": "Ask them what to look up - there was no query.",
        "search.unconfigured": "Search isn't configured.",
        "search.not_covered": "The results do not cover it.",
        "step.section": "Knowledge",
        "step.text": "Answer the caller's question from {tool}, not memory.",
        "tool.contact": "Record the caller's contact details for a human follow-up. Call this only after they "
        "have agreed they would like someone to follow up.",
        "contact.ask": "Ask them for {field}.",
        "contact.any_of": "Ask them for {choices}.",
        "contact.thanks": "Thanks - I've passed that along and someone will follow up.",
        "list.and": " and ",
        "list.or": " or ",
        "list.comma": ", ",
    }
)
"""Every key ``InfoBotKnowledge``'s words come from, with its default."""

CONTACT_FIELDS: Mapping[str, Field] = MappingProxyType(
    {
        "name": Field(str, "The caller's name.", required=False),
        "email": Field(
            str,
            "An email address to reach them.",
            ask="Ask them for an email address to reach them at.",
        ),
        "topic": Field(str, "What they want followed up, in brief.", required=False),
    }
)
"""The contact tool's fields unless ``contact_fields`` replaces them."""


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

    It installs beside ``Operations`` on one agent, in either order: both
    add to the same ``main`` step, which keeps every layer's text and tools.
    """

    _GROUNDING = (
        "Answer only from these results. If they do not cover it, say so plainly "
        "- do not fill the gap from general knowledge."
    )

    def __init__(
        self,
        search: Callable[[str], list[Result] | Awaitable[list[Result]]] | None = None,
        *,
        tool: str = "search_knowledge",
        description: str = "Search the documentation and answer only from the results.",
        result_limit: int = 5,
        grounding: str = _GROUNDING,
        contact: Callable[[dict[str, Any]], None] | None = None,
        contact_tool: str = "collect_contact",
        contact_fields: Mapping[str, Field] | None = None,
        contact_any_of: Sequence[Sequence[str]] | None = None,
        wording: Mapping[str, str] | None = None,
        context: str = "default",
        step: str = "main",
    ) -> None:
        """
        Args:
            search: ``search(query)`` returns the raw results; it may be
                ``async``. Or call ``use_search_service``.
            tool: The search tool's name.
            description: What the search tool does, as the model reads it.
            result_limit: The most results handed to the model.
            grounding: The line that goes with the results, unless rules
                are added.
            contact: ``contact(fields)`` takes the details the contact tool
                collects; without it there's no contact tool.
            contact_tool: The contact tool's name.
            contact_fields: The contact tool's fields, in place of
                ``CONTACT_FIELDS`` (name, email and topic). A field's
                ``ask`` is what the model is told when it's missing.
            contact_any_of: Sets of fields, any one of which is enough, such
                as ``[["email"], ["phone"]]``. Defaults to the required
                fields, all of them.
            wording: Words to use in place of the defaults, by key; the keys
                are those of ``KNOWLEDGE_WORDING``.
            context: The context of the step its tools go in.
            step: The step its tools go in, made if it isn't there, added to
                if it is.
        """
        self._search = search
        self._tool = tool
        self._description = description
        self._result_limit = result_limit
        self._grounding = grounding
        self._contact = contact
        self._contact_tool = contact_tool
        self._contact_fields = dict(contact_fields or CONTACT_FIELDS)
        self._contact_any_of = [
            list(s)
            for s in (
                contact_any_of
                if contact_any_of is not None
                else [[k for k, f in self._contact_fields.items() if f.required]]
            )
        ]
        unknown = sorted(
            {k for s in self._contact_any_of for k in s} - set(self._contact_fields)
        )
        if unknown:
            raise ValueError(
                f"contact_any_of names fields there aren't: {', '.join(unknown)}"
            )
        self._w = _Wording(
            KNOWLEDGE_WORDING, wording, "InfoBotKnowledge", "KNOWLEDGE_WORDING"
        )
        self._context_name = context
        self._step_name = step
        self._exclude: Callable[[Result, str], bool] | None = None
        self._demote: Callable[[Result], bool] | None = None
        self._context: Callable[[Result], str | None] | None = None
        self._rules: list[tuple[str, str]] = []
        self._result_rules: list[tuple[Callable[[str, list[Result]], bool], str]] = []
        self._query_types: dict[str, str] = {}
        self._query_type_help: str = ""
        self._authority: Callable[[Result], int | None] | None = None
        self._query_transform: Callable[[str], str] | None = None
        self._fallback: Callable[[str], str | None] | None = None
        self._expander: Callable[[list[Result]], list[Result]] | None = None

    @property
    def tools(self) -> list[str]:
        """The tools it adds: the search tool, and the contact tool when there's ``contact``."""
        return [
            self._tool,
            *([self._contact_tool] if self._contact is not None else []),
        ]

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

    def set_authority(self, fn: Callable[[Result], int | None]) -> InfoBotKnowledge:
        """A ranking tier for a result; higher ranks first among non-demoted ones."""
        self._authority = fn
        return self

    def set_query_transform(self, fn: Callable[[str], str]) -> InfoBotKnowledge:
        """Rewrite the SEARCH query (aliases, glossary, stopwords, …) before it
        runs; the grounding still uses the caller's own words."""
        self._query_transform = fn
        return self

    def set_fallback(self, fn: Callable[[str], str | None]) -> InfoBotKnowledge:
        """Called with the query when nothing clears the cut; its text, if any, is
        returned in place of the not-covered line (e.g. a web search)."""
        self._fallback = fn
        return self

    def set_expander(
        self, fn: Callable[[list[Result]], list[Result]]
    ) -> InfoBotKnowledge:
        """Transform the kept results before they're rendered, e.g. widen each to
        its full section."""
        self._expander = fn
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
        """Add the tools, and the step that offers them."""
        if self._search is None:
            raise ValueError(
                "InfoBotKnowledge needs a search backend: pass search=fn or call "
                "use_search_service(...) before install()."
            )
        self._define_search(agent)
        if self._contact is not None:
            self._define_contact(agent)
        self._ensure_main(agent)
        return agent

    def _define_search(self, agent: AgentBase) -> None:
        w = self._w
        params: dict[str, Any] = {
            "query": {
                "type": "string",
                "description": w("tool.search.query"),
            }
        }
        if self._query_types:
            params["query_type"] = {
                "type": "string",
                "enum": sorted(self._query_types),
                "description": self._query_type_help or w("tool.search.query_type"),
            }
        # An async search gets a handler on the event loop; a sync one stays
        # sync, run in a worker thread like any sync handler
        handler = (
            self._handle_search_async
            if inspect.iscoroutinefunction(self._search)
            else self._handle_search
        )
        agent.define_tool(
            self._tool,
            w("tool.search", description=self._description),
            params,
            handler,
            required=["query"],
        )

    def _query_of(self, args: dict[str, Any]) -> tuple[str, str]:
        """The caller's query, and the one searched: transformed, with its qualifier."""
        query = (args.get("query") or "").strip()
        # The qualifier aids retrieval only; grounding stays the caller's own words.
        base = self._query_transform(query) if self._query_transform else query
        qualifier = self._query_types.get((args.get("query_type") or "").strip())
        return query, f"{base} {qualifier}" if qualifier else base

    def _handle_search(self, args: dict[str, Any], raw: Any) -> FunctionResult:
        query, effective = self._query_of(args or {})
        if not query:
            return FunctionResult(self._w("search.no_query"))
        search = self._search
        if search is None:
            return FunctionResult(self._w("search.unconfigured"))
        # Registered for a sync search: the async one has a handler of its own
        found = cast("list[Result]", search(effective))
        blob = self._format(query, list(found or []))
        return FunctionResult(blob).back_to_back_functions("forever")

    async def _handle_search_async(
        self, args: dict[str, Any], raw: Any
    ) -> FunctionResult:
        query, effective = self._query_of(args or {})
        if not query:
            return FunctionResult(self._w("search.no_query"))
        search = self._search
        if search is None:
            return FunctionResult(self._w("search.unconfigured"))
        found = search(effective)
        if inspect.isawaitable(found):
            found = await found
        blob = self._format(query, list(found or []))
        return FunctionResult(blob).back_to_back_functions("forever")

    def _rank_key(self, r: Result) -> tuple[int, int, float]:
        demoted = 1 if (self._demote and self._demote(r)) else 0
        authority = (self._authority(r) or 0) if self._authority else 0
        return (demoted, -authority, -_score(r))

    def _format(self, query: str, results: list[Result]) -> str:
        kept = [r for r in results if not (self._exclude and self._exclude(r, query))]
        # Demoted last; then higher authority; then higher score.
        kept.sort(key=self._rank_key)
        kept = kept[: self._result_limit]
        if self._expander and kept:
            kept = list(self._expander(kept))
        if not kept:
            if self._fallback:
                # The fallback supplies its own answer from another source, so
                # the "answer only from these results" grounding does not apply.
                text = self._fallback(query)
                if text:
                    return str(text)
            return "\n\n".join(
                [*self._rules_for("empty"), self._w("search.not_covered")]
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
        sets = self._contact_any_of
        required = [
            k for k in self._contact_fields if sets and all(k in s for s in sets)
        ]
        agent.define_tool(
            self._contact_tool,
            self._w("tool.contact"),
            {k: f.schema() for k, f in self._contact_fields.items()},
            self._handle_contact,
            required=required or None,
        )

    def _handle_contact(self, args: dict[str, Any], raw: Any) -> FunctionResult:
        fields: dict[str, Any] = {
            k: str((args or {}).get(k) or "").strip() for k in self._contact_fields
        }
        sets = self._contact_any_of
        if sets and not any(all(fields[k] for k in s) for s in sets):
            return FunctionResult(self._missing_contact(fields))
        if self._contact is not None:
            self._contact(fields)
        return FunctionResult(self._w("contact.thanks")).back_to_back_functions(
            "forever"
        )

    def _missing_contact(self, fields: Mapping[str, str]) -> str:
        """What to ask for: the missing fields of the one set, or a choice of the sets."""
        w = self._w

        def ask(k: str) -> str:
            f = self._contact_fields[k]
            return f.ask or w("contact.ask", field=k.replace("_", " "))

        if len(self._contact_any_of) == 1:
            return " ".join(ask(k) for k in self._contact_any_of[0] if not fields[k])
        choices = [
            w.joined([k.replace("_", " ") for k in s]) for s in self._contact_any_of
        ]
        return w("contact.any_of", choices=w.joined(choices, "list.or"))

    def _ensure_main(self, agent: AgentBase) -> None:
        builder = agent.define_contexts()
        ctx = builder.get_context(self._context_name) or builder.add_context(
            self._context_name
        )
        tools = [self._tool]
        if self._contact is not None:
            tools.append(self._contact_tool)
        title = self._w("step.section")
        text = self._w("step.text", tool=self._tool)
        step = ctx.get_step(self._step_name)
        if step is None:
            ctx.add_step(self._step_name).add_section(title, text).set_functions(tools)
        else:
            step._extend(text, tools, section=title)


def _score(result: Result) -> float:
    try:
        return float(result.get("score") or 0.0)
    except (TypeError, ValueError):
        return 0.0
