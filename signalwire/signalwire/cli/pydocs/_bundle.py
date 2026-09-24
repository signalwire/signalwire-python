"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The documentation installed with the package, and where to find it.

setup.py copies these repository files into the wheel under
``signalwire/_docs/``, in the same layout, so relative links between them
still work. setup.py loads this file by path, so it imports only the standard
library.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path, PurePosixPath

# Repository files and directories installed under signalwire/_docs/
DOC_SOURCES = (
    "README.md",
    "CHANGELOG.md",
    "docs",
    "examples",
    "tutorial",
    "relay",
    "rest",
    "livewire",
    "mcp",
    "mcp_gateway",
)

# Comparisons with other frameworks: not documentation of the SDK
DOC_EXCLUDES = frozenset({"docs/pipecat_comparison.md", "docs/livekit_comparison.md"})

# Never installed, even when present in a source tree: build and editor
# leftovers, and files that may hold local secrets
_SKIP_DIRS = frozenset(
    {"__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "venv", "node_modules"}
)
_SKIP_NAMES = frozenset({".DS_Store", ".env"})
_SKIP_SUFFIXES = (".pyc", ".pyo", ".pem", ".key")


def is_doc_file(rel: str) -> bool:
    """True if ``rel``, a repository-relative POSIX path, is installed as documentation."""
    parts = PurePosixPath(rel).parts
    if not parts or parts[0] not in DOC_SOURCES or rel in DOC_EXCLUDES:
        return False
    if any(part in _SKIP_DIRS for part in parts[:-1]):
        return False
    name = parts[-1]
    return name not in _SKIP_NAMES and not name.endswith(_SKIP_SUFFIXES)


def iter_doc_files(root: Path) -> Iterator[str]:
    """Yield the documentation files under a source tree or an installed bundle, sorted."""
    for source in DOC_SOURCES:
        path = root / source
        if path.is_file():
            candidates: list[Path] = [path]
        elif path.is_dir():
            candidates = sorted(p for p in path.rglob("*") if p.is_file())
        else:
            continue
        for candidate in candidates:
            rel = candidate.relative_to(root).as_posix()
            if is_doc_file(rel):
                yield rel


def docs_root() -> Path | None:
    """The directory holding the installed documentation, or None if it's missing.

    An installed wheel has it at ``signalwire/_docs``. An editable install or
    a source checkout has no copy, so the repository root serves instead.
    """
    package = Path(__file__).resolve().parents[2]
    bundled = package / "_docs"
    if (bundled / "docs").is_dir():
        return bundled
    checkout = package.parents[1]
    if (checkout / "docs").is_dir() and (checkout / "pyproject.toml").is_file():
        return checkout
    return None
