#!/usr/bin/env python3
"""
Prove the tutorial's code blocks are the real code.

A lesson quotes code by putting a marker on the line before the fence:

    <!-- source: handlers.py#finish -->     one ``# region: finish`` of a file
    <!-- source: penny.py -->               the whole file

This script checks every marked block is identical to what it claims to quote
(ignoring the indentation the lesson removes), and that every region marker in
the source files is paired. Run it directly, or through test_penny.py.

``--write`` rewrites every marked block from the code it quotes, and expands
``{{source:penny.py#finish}}`` placeholder lines into marked blocks. Change the
code, run ``python check_docs.py --write``, and the lessons follow.

A quoted Python block is an excerpt, so it can't run on its own. ``--write``
also marks it ``no-run`` for the repository's snippet checks, which run the
code blocks in every document; test_penny.py runs the real files instead.

Copyright (c) 2025 SignalWire. Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from __future__ import annotations

import re
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = re.compile(r"<!--\s*source:\s*(?P<file>[\w./-]+?)(?:#(?P<region>[\w-]+))?\s*-->")
FENCE = re.compile(r"^\s*```")
REGION_LINE = re.compile(r"^\s*#\s*(?P<kind>region|endregion):\s*(?P<name>[\w-]+)\s*$")
PLACEHOLDER = re.compile(r"^\{\{source:(?P<file>[\w./-]+?)(?:#(?P<region>[\w-]+))?\}\}\s*$")


def _clean(lines: list[str]) -> str:
    """Drop region markers and surrounding blank lines, then remove common indentation."""
    kept = [line.rstrip() for line in lines if not REGION_LINE.match(line)]
    while kept and not kept[0]:
        kept.pop(0)
    while kept and not kept[-1]:
        kept.pop()
    return textwrap.dedent("\n".join(kept))


def quoted(file: Path, region: str | None) -> str:
    lines = file.read_text().splitlines()
    if region is None:
        return _clean(lines)
    starts = [i for i, line in enumerate(lines)
              if (m := REGION_LINE.match(line)) and m["kind"] == "region" and m["name"] == region]
    ends = [i for i, line in enumerate(lines)
            if (m := REGION_LINE.match(line)) and m["kind"] == "endregion" and m["name"] == region]
    if len(starts) != 1 or len(ends) != 1 or ends[0] < starts[0]:
        raise LookupError(f"{file.name} has no single '# region: {region}'")
    return _clean(lines[starts[0] + 1:ends[0]])


def unpaired_regions(file: Path) -> list[str]:
    opened: dict[str, int] = {}
    problems = []
    for number, line in enumerate(file.read_text().splitlines(), 1):
        m = REGION_LINE.match(line)
        if not m:
            continue
        if m["kind"] == "region":
            if m["name"] in opened:
                problems.append(f"{file.name}:{number}: region '{m['name']}' opened twice")
            opened[m["name"]] = number
        elif opened.pop(m["name"], None) is None:
            problems.append(f"{file.name}:{number}: endregion '{m['name']}' without a region")
    problems += [f"{file.name}:{n}: region '{name}' is never closed" for name, n in opened.items()]
    return problems


def check_docs(root: Path = HERE) -> list[str]:
    problems: list[str] = []
    for source in sorted(root.glob("*.py")):
        problems += unpaired_regions(source)
    for md in sorted((root / "tutorial").glob("*.md")):
        lines = md.read_text().splitlines()
        for number, line in enumerate(lines, 1):
            m = MARKER.search(line)
            if not m:
                continue
            where = f"{md.name}:{number}"
            if number >= len(lines) or not FENCE.match(lines[number]):
                problems.append(f"{where}: a source marker must sit directly above a code fence")
                continue
            end = next((j for j in range(number + 1, len(lines)) if FENCE.match(lines[j])), None)
            if end is None:
                problems.append(f"{where}: the code fence is never closed")
                continue
            source = root / m["file"]
            if not source.is_file():
                problems.append(f"{where}: {m['file']} does not exist")
                continue
            try:
                expected = quoted(source, m["region"])
            except LookupError as missing:
                problems.append(f"{where}: {missing}")
                continue
            if _clean(lines[number + 1:end]) != expected:
                label = m["file"] + (f"#{m['region']}" if m["region"] else "")
                problems.append(f"{where}: the block no longer matches {label}")
    return problems


def _fence_language(name: str) -> str:
    if name == "Dockerfile":
        return "dockerfile"
    return {".py": "python", ".sh": "bash"}.get(Path(name).suffix, "")


def _marker_line(name: str, region: str | None) -> str:
    line = f"<!-- source: {name}{'#' + region if region else ''} -->"
    if _fence_language(name) == "python":
        line += f" <!-- snippet: no-run an excerpt of {name}, checked against the file by test_penny.py -->"
    return line


def sync_docs(root: Path = HERE) -> int:
    """Rewrite every quoted block from the code it quotes. Returns the files changed."""
    changed = 0
    for md in sorted((root / "tutorial").glob("*.md")):
        lines = md.read_text().splitlines()
        out: list[str] = []
        i = 0
        while i < len(lines):
            placeholder = PLACEHOLDER.match(lines[i])
            marker = MARKER.search(lines[i])
            quoting = marker and i + 1 < len(lines) and FENCE.match(lines[i + 1])
            found = placeholder or (marker if quoting else None)
            if found is None:
                out.append(lines[i])
                i += 1
                continue
            name, region = found["file"], found["region"]
            out.append(_marker_line(name, region))
            out += [f"```{_fence_language(name)}", *quoted(root / name, region).splitlines(), "```"]
            if placeholder:
                i += 1
            else:  # skip the old block through its closing fence
                i = next(j for j in range(i + 2, len(lines)) if FENCE.match(lines[j])) + 1
        text = "\n".join(out) + "\n"
        if text != md.read_text():
            md.write_text(text)
            changed += 1
    return changed


if __name__ == "__main__":
    if "--write" in sys.argv[1:]:
        print(f"Rewrote {sync_docs()} lesson file(s).")
    found = check_docs()
    for problem in found:
        print(problem)
    print(f"{len(found)} problem(s)" if found else "Every quoted block matches the code.")
    sys.exit(1 if found else 0)
