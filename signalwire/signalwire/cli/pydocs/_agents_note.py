"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The note that points a project's coding agents at sw-pydocs, for AGENTS.md
(which most coding agents read) and an Agent Skills SKILL.md. ``sw-pydocs
init`` and ``sw-agent-init`` both write it.
"""

from __future__ import annotations

from pathlib import Path

NOTE_BEGIN = "<!-- signalwire-sdk: begin -->"
NOTE_END = "<!-- signalwire-sdk: end -->"

_GUIDANCE = """\
This project uses the SignalWire SDK for Python (`signalwire-sdk`, imported as
`signalwire`). Its documentation is installed with it and matches the installed
version:

- Run `sw-pydocs` for a map of the SDK, and `sw-pydocs <topic>` for an area:
  `agents`, `tools`, `contexts`, `skills`, `relay`, `rest`, `search`, `deploy`
  and more.
- Check SDK names and signatures with `sw-pydocs api <name>` instead of
  recalling them. `sw-pydocs examples` and `sw-pydocs grep <regex>` find
  examples and docs.
- Before building an agent that takes real actions, read `sw-pydocs pgi`.
- Test tools and SWML without a call: `swaig-test <file> --list-tools`,
  `--dump-swml`, `--exec <tool>`.
"""

_SKILL = f"""\
---
name: signalwire-sdk
description: Use when writing, changing or reviewing code that uses the SignalWire SDK for Python (signalwire-sdk, import signalwire), such as AI voice agents, SWML, SWAIG tools, RELAY call control, the REST client or search. Gets accurate, version-matched documentation from the installed package with sw-pydocs.
---

# SignalWire SDK for Python

{_GUIDANCE}"""


def note() -> str:
    """The AGENTS.md section, between markers so ``init`` can update it."""
    return f"{NOTE_BEGIN}\n## SignalWire SDK\n\n{_GUIDANCE}{NOTE_END}\n"


def _with_note(text: str) -> str:
    """``text`` with the note added, or updated if it's already there."""
    start = text.find(NOTE_BEGIN)
    end = text.find(NOTE_END)
    if start != -1 and end > start:
        return text[:start] + note() + text[end + len(NOTE_END) :].lstrip("\n")
    if text.strip():
        return text.rstrip("\n") + "\n\n" + note()
    return "# Notes for coding agents\n\n" + note()


def init(project: Path, skill: bool = False) -> list[tuple[Path, str]]:
    """Add or update the note in ``project``; return each file changed and how.

    AGENTS.md gets the note. So does CLAUDE.md if it exists and doesn't
    import AGENTS.md, since an agent that reads CLAUDE.md skips AGENTS.md when
    both are present. ``skill`` also writes an Agent Skills SKILL.md under
    .agents/skills/ and .claude/skills/, where agents look for skills.
    """
    changes: list[tuple[Path, str]] = []

    def write(path: Path, content: str) -> None:
        old = path.read_text(encoding="utf-8") if path.is_file() else None
        if old == content:
            changes.append((path, "unchanged"))
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        changes.append((path, "created" if old is None else "updated"))

    agents = project / "AGENTS.md"
    current = agents.read_text(encoding="utf-8") if agents.is_file() else ""
    write(agents, _with_note(current))

    claude = project / "CLAUDE.md"
    if claude.is_file():
        text = claude.read_text(encoding="utf-8")
        if "@AGENTS.md" not in text:
            write(claude, _with_note(text))

    if skill:
        for base in (".agents", ".claude"):
            write(project / base / "skills" / "signalwire-sdk" / "SKILL.md", _SKILL)
    return changes
