"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The documentation installed with the package, and where to find it.

MANIFEST.in lists every documentation file by name, generated from the files
git tracks, so a local file (a .env, a log, a cache) can't reach a release.
The sdist includes exactly those files, and setup.py copies exactly those into
the wheel under ``signalwire/_docs/``, in the same layout. setup.py loads this
file by path, so it imports only the standard library.

To regenerate MANIFEST.in after adding or removing a doc or example, run this
file from the repository root: ``python signalwire/signalwire/cli/pydocs/_bundle.py``.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path, PurePosixPath

# Repository files and directories installed under signalwire/_docs/
DOC_SOURCES = (
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
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

# Never installed: build and editor leftovers, and files that may hold secrets
_SKIP_DIRS = frozenset(
    {"__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "venv", "node_modules"}
)
_SKIP_NAMES = frozenset({".DS_Store", ".env"})
_SKIP_SUFFIXES = (".pyc", ".pyo", ".pem", ".key", ".log")

_MANIFEST_HEADER = """\
# The documentation that setup.py installs under signalwire/_docs/, one file
# per line, so a local file that git doesn't track can't ship. Generated from
# the tracked files by signalwire/signalwire/cli/pydocs/_bundle.py; run it from
# the repository root after adding or removing a doc or example.
# tests/unit/cli/test_pydocs_bundle.py checks that this list is current.
"""
_MANIFEST_FOOTER = """\
global-exclude __pycache__ *.py[cod] .DS_Store
"""

# A Markdown link into the SDK's source, such as ../signalwire/signalwire/x.py
_SOURCE_LINK = re.compile(r"\]\(((?:\.\./)+)signalwire/signalwire/")


def is_doc_file(rel: str) -> bool:
    """True if ``rel``, a repository-relative POSIX path, may be installed as documentation."""
    parts = PurePosixPath(rel).parts
    if not parts or parts[0] not in DOC_SOURCES or rel in DOC_EXCLUDES:
        return False
    if any(part in _SKIP_DIRS for part in parts[:-1]):
        return False
    name = parts[-1]
    return name not in _SKIP_NAMES and not name.endswith(_SKIP_SUFFIXES)


def manifest_files(root: Path) -> list[str]:
    """The documentation files MANIFEST.in in ``root`` lists."""
    listed = []
    for line in (root / "MANIFEST.in").read_text(encoding="utf-8").splitlines():
        words = line.split()
        if len(words) == 2 and words[0] == "include" and is_doc_file(words[1]):
            listed.append(words[1])
    return sorted(listed)


def iter_doc_files(root: Path) -> Iterator[str]:
    """Yield the documentation files under ``root``, sorted.

    A checkout or an sdist has MANIFEST.in, which says which files they are.
    An installed copy holds only those files.
    """
    if (root / "MANIFEST.in").is_file():
        yield from (rel for rel in manifest_files(root) if (root / rel).is_file())
        return
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        yield path.relative_to(root).as_posix()


def installed_text(rel: str, text: str) -> str:
    """A doc's text as installed: links into the SDK's source point at the package.

    In the repository, a doc links to source as ``../signalwire/signalwire/x.py``.
    Installed, the docs are in ``signalwire/_docs/``, so the package is one
    level further up: ``../../x.py``.
    """
    if not rel.endswith(".md"):
        return text
    return _SOURCE_LINK.sub(lambda m: f"]({m.group(1)}../", text)


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
    if (checkout / "docs").is_dir() and (checkout / "MANIFEST.in").is_file():
        return checkout
    return None


def tracked_doc_files(root: Path) -> list[str]:
    """The documentation files git tracks in the repository at ``root``."""
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git isn't installed")
    listed = subprocess.run(  # noqa: S603  # fixed arguments, in the repository
        [git, "ls-files", "--", *DOC_SOURCES],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    return sorted(rel for rel in listed if is_doc_file(rel))


def render_manifest(root: Path) -> str:
    """MANIFEST.in's contents for the repository at ``root``."""
    lines = [f"include {rel}" for rel in tracked_doc_files(root)]
    return _MANIFEST_HEADER + "\n".join(lines) + "\n" + _MANIFEST_FOOTER


if __name__ == "__main__":
    here = Path.cwd()
    (here / "MANIFEST.in").write_text(render_manifest(here), encoding="utf-8")
    print(f"Wrote {here / 'MANIFEST.in'}")
