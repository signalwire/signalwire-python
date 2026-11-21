"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

LegStore: leg persistence and the id scheme that carries history across a
voice<->chat medium switch.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from signalwire.operations.infobot import LegStore


def test_root_and_next_leg_ids() -> None:
    assert LegStore.root_id("abc") == "abc"
    assert LegStore.root_id("abc.2") == "abc"
    assert LegStore.next_leg_id("abc", 1) == "abc.2"
    # a suffixed id is rooted first, so the next leg counts off the root
    assert LegStore.next_leg_id("abc.3", 3) == "abc.4"


def test_default_store_round_trips(tmp_path: Path) -> None:
    store = LegStore(cache_dir=str(tmp_path))
    assert store.legs("c1") == []
    assert store.record("c1", {"turns": ["a"]}) is True
    assert store.record("c1", {"turns": ["b"]}) is True
    assert [leg["turns"] for leg in store.legs("c1")] == [["a"], ["b"]]
    # a different conversation is isolated
    assert store.legs("c2") == []


def test_set_store_overrides_persistence() -> None:
    mem: dict[str, list[dict[str, Any]]] = {}

    def load(cid: str) -> list[dict[str, Any]]:
        return mem.get(cid, [])

    def append(cid: str, leg: dict[str, Any]) -> bool:
        mem.setdefault(cid, []).append(leg)
        return True

    store = LegStore().set_store(load=load, append=append)
    store.record("x", {"n": 1})
    assert store.legs("x") == [{"n": 1}]
