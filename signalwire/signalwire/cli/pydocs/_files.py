"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Finding, showing and searching the installed documentation files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ._bundle import iter_doc_files

# Suffixes worth searching and showing; everything else (such as .swsearch
# index files) is binary or not documentation
_TEXT_SUFFIXES = (".md", ".py", ".txt", ".yaml", ".yml", ".json", ".sh", ".example")
_TEXT_PREFIXES = ("Dockerfile",)

_HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")


def is_text(rel: str) -> bool:
    """True if a documentation file is text worth showing or searching."""
    name = rel.rsplit("/", 1)[-1]
    return name.endswith(_TEXT_SUFFIXES) or name.startswith(_TEXT_PREFIXES)


def package_dir() -> Path:
    """The installed ``signalwire`` package directory."""
    return Path(__file__).resolve().parents[2]


def all_doc_files(root: Path | None) -> dict[str, Path]:
    """Every documentation file, by the path sw-pydocs shows for it.

    Files from the docs root keep their repository paths. The skill READMEs,
    which live inside the package, appear as ``signalwire/skills/...``.
    """
    files: dict[str, Path] = {}
    if root is not None:
        for rel in iter_doc_files(root):
            files[rel] = root / rel
    skills = package_dir() / "skills"
    for readme in sorted(skills.glob("**/README.md")):
        files["signalwire/" + readme.relative_to(package_dir()).as_posix()] = readme
    return files


def resolve(name: str, files: dict[str, Path]) -> list[str]:
    """The documentation files ``name`` could mean, best matches first.

    Accepts a path as shown by sw-pydocs, the same without ``.md``, a file
    name such as ``agent_guide.md``, or a stem such as ``agent_guide``.
    """
    wanted = name.strip().strip("/")
    if wanted in files:
        return [wanted]
    if wanted + ".md" in files:
        return [wanted + ".md"]
    matches = [
        rel
        for rel in files
        if rel.endswith("/" + wanted) or rel.endswith("/" + wanted + ".md")
    ]
    if matches:
        return sorted(matches, key=len)
    lowered = wanted.lower()
    return sorted((rel for rel in files if lowered in rel.lower()), key=len)


@dataclass(frozen=True)
class Heading:
    """A Markdown heading and where it is."""

    level: int
    text: str
    line: int  # 1-based


def headings(text: str) -> list[Heading]:
    """The Markdown headings in ``text``, skipping lines inside code fences."""
    found: list[Heading] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = _HEADING.match(line)
        if match:
            found.append(Heading(len(match.group(1)), match.group(2), number))
    return found


def section(text: str, wanted: str) -> tuple[Heading, str] | None:
    """The first section whose heading contains ``wanted``, ignoring case.

    The section runs to the next heading at the same level or higher.
    """
    lines = text.splitlines()
    marks = headings(text)
    lowered = wanted.lower()
    for index, heading in enumerate(marks):
        if lowered not in heading.text.lower():
            continue
        end = len(lines)
        for later in marks[index + 1 :]:
            if later.level <= heading.level:
                end = later.line - 1
                break
        return heading, "\n".join(lines[heading.line - 1 : end]).rstrip() + "\n"
    return None


@dataclass(frozen=True)
class Match:
    """One line that matched a search."""

    rel: str
    line: int
    text: str


def grep(
    pattern: re.Pattern[str], files: dict[str, Path], limit: int
) -> tuple[list[Match], int]:
    """Lines matching ``pattern`` in the text files, and the total number of matches."""
    found: list[Match] = []
    total = 0
    for rel, path in files.items():
        if not is_text(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                total += 1
                if len(found) < limit:
                    found.append(Match(rel, number, line.strip()))
    return found, total
