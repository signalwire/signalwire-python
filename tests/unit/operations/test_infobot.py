"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

InfoBotKnowledge: a read/inform layer that installs on its own and composes
beside Operations on one agent.
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
    InfoBotKnowledge(search=lambda q: f"results for {q}").install(agent)

    main = _main_step(agent)
    assert "search_knowledge" in main["functions"]
    assert "search_knowledge" in main["text"]
    assert agent._params["conscience"] == "${global_data.infobot.now}"


def test_knowledge_composes_beside_operations() -> None:
    agent = AgentBase(name="both", route="/both", suppress_logs=True)
    InfoBotKnowledge(search=lambda q: "...").install(agent)

    ops = Operations(role="You help customers.")
    ops.writes_with(lambda call, w: None)

    @ops.operation(tool="cancel_order")
    class Cancel(Operation):
        """Cancel an order."""

        def prepare(self, call: Any, f: Any) -> Change:
            return Change(read_back="Cancel it. Shall I?")

    ops.install(agent)

    main = _main_step(agent)
    # search_knowledge (ours) is kept and the operation tool is unioned in.
    assert "search_knowledge" in main["functions"]
    assert "cancel_order" in main["functions"]
    assert "cancel_order" in main["text"]
    # each layer's record line survives, ours ahead of Operations'.
    assert agent._params["conscience"] == "${global_data.infobot.now}\n\n${global_data.ops.now}"


def test_blank_query_asks_rather_than_searches() -> None:
    seen: list[str] = []

    def search(q: str) -> str:
        seen.append(q)
        return "x"

    kb = InfoBotKnowledge(search=search)
    # an empty query returns a prompt and never calls search
    result = kb._handle_search({"query": "  "}, {})
    assert "no query" in str(result.response).lower()
    assert seen == []
    # a real query flows through to search
    assert kb._handle_search({"query": "pricing"}, {}).response == "x"
    assert seen == ["pricing"]
