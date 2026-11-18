"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

InfoBotKnowledge: a read/inform layer that installs on its own, composes beside
Operations on one agent, and governs its search results.
"""

from __future__ import annotations

from typing import Any

from signalwire import AgentBase
from signalwire.operations import Change, Operation, Operations
from signalwire.operations.infobot import InfoBotKnowledge


def _main_step(agent: AgentBase) -> dict[str, Any]:
    contexts = agent.define_contexts().to_dict()
    return next(s for s in contexts["default"]["steps"] if s["name"] == "main")


def test_knowledge_installs_standalone() -> None:
    agent = AgentBase(name="kb", route="/kb", suppress_logs=True)
    InfoBotKnowledge(search=lambda q: []).install(agent)

    main = _main_step(agent)
    assert "search_knowledge" in main["functions"]
    assert "search_knowledge" in main["text"]
    assert agent._params["conscience"] == "${global_data.infobot.now}"


def test_knowledge_composes_beside_operations() -> None:
    agent = AgentBase(name="both", route="/both", suppress_logs=True)
    InfoBotKnowledge(search=lambda q: []).install(agent)

    ops = Operations(role="You help customers.")
    ops.writes_with(lambda call, w: None)

    @ops.operation(tool="cancel_order")
    class Cancel(Operation):
        """Cancel an order."""

        def prepare(self, call: Any, f: Any) -> Change:
            return Change(read_back="Cancel it. Shall I?")

    ops.install(agent)

    main = _main_step(agent)
    assert "search_knowledge" in main["functions"]
    assert "cancel_order" in main["functions"]
    assert "cancel_order" in main["text"]
    assert agent._params["conscience"] == "${global_data.infobot.now}\n\n${global_data.ops.now}"


def test_blank_query_asks_rather_than_searches() -> None:
    seen: list[str] = []

    def search(q: str) -> list[dict[str, Any]]:
        seen.append(q)
        return [{"content": "x", "score": 1.0}]

    kb = InfoBotKnowledge(search=search)
    result = kb._handle_search({"query": "  "}, {})
    assert "no query" in str(result.response).lower()
    assert seen == []


def test_governance_excludes_demotes_ranks_and_labels() -> None:
    def search(q: str) -> list[dict[str, Any]]:
        return [
            {"content": "low", "score": 0.4, "kind": "keep"},
            {"content": "high", "score": 0.9, "kind": "keep"},
            {"content": "commentary", "score": 0.95, "kind": "demote"},
            {"content": "spam", "score": 0.99, "kind": "drop"},
        ]

    kb = InfoBotKnowledge(search=search)
    kb.set_exclude(lambda r, q: r["kind"] == "drop")
    kb.set_demote(lambda r: r["kind"] == "demote")
    kb.set_result_context(lambda r: f"[{r['kind']}]")

    blob = str(kb._handle_search({"query": "anything"}, {}).response)
    assert "spam" not in blob  # excluded before the cut
    assert blob.index("high") < blob.index("low")  # higher score first
    assert blob.index("low") < blob.index("commentary")  # demoted ranks last
    assert "[keep]" in blob  # context labels present
    assert blob.startswith(kb._grounding)  # grounding leads


def test_governance_limits_and_empty_case() -> None:
    def search(q: str) -> list[dict[str, Any]]:
        return [{"content": f"r{i}", "score": i / 10} for i in range(10)]

    blob = str(InfoBotKnowledge(search=search, result_limit=3)._handle_search({"query": "q"}, {}).response)
    assert "r9" in blob and "r8" in blob and "r7" in blob  # top 3 by score
    assert "r6" not in blob  # cut by the limit

    empty = InfoBotKnowledge(search=lambda q: [])
    assert "do not cover it" in str(empty._handle_search({"query": "q"}, {}).response).lower()
