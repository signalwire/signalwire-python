"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

AGENTS.md mirrors CLAUDE.md for coding agents that read AGENTS.md instead.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _body(name: str) -> str:
    """The file after its title and one-paragraph introduction."""
    text = (REPO / name).read_text(encoding="utf-8")
    return text.split("\n\n", 2)[2]


def test_agents_md_mirrors_claude_md() -> None:
    assert _body("AGENTS.md") == _body("CLAUDE.md"), (
        "AGENTS.md and CLAUDE.md differ; make the same change to both"
    )
