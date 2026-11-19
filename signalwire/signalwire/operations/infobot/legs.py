"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Per-conversation leg storage for voice<->chat continuity.
"""

from __future__ import annotations

import json
import re
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

Leg = dict[str, Any]


class LegStore:
    """Persistence for a conversation's legs across a medium switch.

    A conversation that moves between mediums (voice, chat) ends one leg and
    opens another; because an ended conversation cannot be reopened, the next
    leg gets a fresh id while the store keys every leg off the ROOT id, so the
    history travels across the switch. The default persistence is one JSON file
    per conversation under a temp dir; ``set_store`` replaces it (e.g. a
    database) with a ``load(id) -> [leg]`` / ``append(id, leg) -> ok`` pair.
    """

    SEP = "."

    def __init__(self, *, cache_dir: str | None = None) -> None:
        self._cache_dir = Path(
            cache_dir or (Path(tempfile.gettempdir()) / "infobot_conversations")
        )
        self._load: Callable[[str], list[Leg]] | None = None
        self._append: Callable[[str, Leg], bool] | None = None

    def set_store(
        self,
        *,
        load: Callable[[str], list[Leg]],
        append: Callable[[str, Leg], bool],
    ) -> LegStore:
        """Replace persistence: ``load(id) -> [leg]``; ``append(id, leg) -> ok``."""
        self._load = load
        self._append = append
        return self

    def legs(self, conversation_id: str) -> list[Leg]:
        """Every leg recorded for the conversation, oldest first."""
        return (self._load or self._default_load)(conversation_id)

    def record(self, conversation_id: str, leg: Leg) -> bool:
        """Append a leg; returns whether it was stored."""
        return (self._append or self._default_append)(conversation_id, leg)

    @classmethod
    def root_id(cls, conversation_id: str) -> str:
        """The conversation's root id, any per-leg suffix removed."""
        return (conversation_id or "").split(cls.SEP, 1)[0]

    @classmethod
    def next_leg_id(cls, conversation_id: str, leg_count: int) -> str:
        """A fresh id for the next leg of the same conversation."""
        return f"{cls.root_id(conversation_id)}{cls.SEP}{leg_count + 1}"

    def _path(self, conversation_id: str) -> Path:
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", conversation_id or "unknown")[:120]
        return self._cache_dir / f"conversation_{safe}.json"

    def _default_load(self, conversation_id: str) -> list[Leg]:
        try:
            data = json.loads(self._path(conversation_id).read_text())
        except (OSError, ValueError):
            return []
        legs = data.get("legs", []) if isinstance(data, dict) else []
        return list(legs) if isinstance(legs, list) else []

    def _default_append(self, conversation_id: str, leg: Leg) -> bool:
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            legs = self._default_load(conversation_id)
            legs.append(leg)
            self._path(conversation_id).write_text(json.dumps({"legs": legs}, indent=1))
        except OSError:
            return False
        return True
