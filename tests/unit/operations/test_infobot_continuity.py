"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Cross-medium continuity: medium detection, tool pairing, and the convo seed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from signalwire import AgentBase
from signalwire.operations.infobot import (
    Continuity,
    LegStore,
    build_seed,
    medium_of,
    pair_tools,
)


def test_medium_of() -> None:
    assert medium_of({"conversation_type": "chat"}) == "chat"
    assert medium_of({"conversation_type": "voice"}) == "voice"
    assert medium_of({}) == "voice"  # unknown -> voice
    assert medium_of(None) == "voice"
    assert medium_of({"global_data": {"conversation_type": "chat"}}) == "chat"
    assert (
        medium_of({"vars": {"userVariables": {"conversation_type": "chat"}}}) == "chat"
    )


def test_pair_tools_drops_orphans_and_unanswered_calls() -> None:
    convo: list[dict[str, Any]] = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "tool_calls": [{"id": "a"}, {"id": "b"}]},
        {"role": "tool", "tool_call_id": "a", "content": "ra"},  # answers a
        {"role": "tool", "tool_call_id": "z", "content": "orphan"},  # no call z
    ]
    out = pair_tools(convo)
    assert [m["role"] for m in out] == ["user", "assistant", "tool"]
    assert [tc["id"] for tc in out[1]["tool_calls"]] == ["a"]  # unanswered b dropped
    assert out[2]["tool_call_id"] == "a"  # orphan z dropped


def test_pair_tools_drops_assistant_with_no_surviving_result() -> None:
    convo: list[dict[str, Any]] = [
        {"role": "assistant", "tool_calls": [{"id": "x"}]},  # no result for x
        {"role": "user", "content": "hi"},
    ]
    assert [m["role"] for m in pair_tools(convo)] == ["user"]


def test_build_seed_uses_latest_leg_and_appends_switch_turns() -> None:
    legs = [
        {"turns": [{"role": "user", "content": "old"}]},
        {"turns": [{"role": "assistant", "content": "latest"}]},
    ]
    convo = build_seed(legs, "voice")
    contents = [m.get("content") for m in convo]
    assert "latest" in contents
    assert "old" not in contents  # only the latest leg with a dialog is seeded
    assert convo[-2] == {"role": "user", "content": "I want to switch to voice."}
    assert convo[-1]["role"] == "system"
    assert "switched from chat to voice" in convo[-1]["content"]


def test_build_seed_empty_and_dedupe() -> None:
    assert build_seed([], "chat") == []
    assert build_seed([{"turns": []}], "chat") == []

    legs = [
        {
            "turns": [
                {"role": "user", "content": "dup"},
                {"role": "user", "content": "dup"},
            ]
        }
    ]
    convo = build_seed(legs, "chat")
    users = [m["content"] for m in convo if m["role"] == "user"]
    assert users == ["dup", "I want to switch to chat."]  # duplicate collapsed


def test_build_seed_can_drop_tool_turns() -> None:
    legs = [
        {
            "turns": [
                {"role": "assistant", "tool_calls": [{"id": "a"}]},
                {"role": "tool", "tool_call_id": "a", "content": "r"},
                {"role": "assistant", "content": "answer"},
            ]
        }
    ]
    convo = build_seed(legs, "voice", include_tools=False)
    assert all(m["role"] != "tool" and "tool_calls" not in m for m in convo)
    assert any(m.get("content") == "answer" for m in convo)


def test_continuity_captures_then_seeds_across_a_switch(tmp_path: Path) -> None:
    c = Continuity(store=LegStore(cache_dir=str(tmp_path)))
    # a voice leg ends; its transcript is captured under the root
    c._capture_leg(
        [
            {"role": "user", "content": "q1"},
            {"role": "assistant", "content": "a1"},
        ],
        {"conversation_id": "root"},
    )
    # a resuming leg (new id off the root) renders; it is seeded with the prior
    agent = AgentBase(name="c", route="/c", suppress_logs=True)
    c._seed_callback(
        {}, {"conversation_id": "root.2", "conversation_type": "voice"}, {}, agent
    )
    convo = agent._params.get("convo")
    assert convo is not None
    contents = [m.get("content") for m in convo]
    assert "q1" in contents and "a1" in contents
    assert convo[-2]["content"] == "I want to switch to voice."
    assert convo[-1]["role"] == "system"


def test_capture_ignores_request_with_no_id(tmp_path: Path) -> None:
    c = Continuity(store=LegStore(cache_dir=str(tmp_path)))
    c._capture_leg([{"role": "user", "content": "x"}], {})
    assert c.store.legs("") == []


def test_continuity_install_wires_without_error() -> None:
    agent = AgentBase(name="ci", route="/ci", suppress_logs=True)
    assert Continuity().install(agent) is agent
