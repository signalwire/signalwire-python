"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Tests for which repository files install with the package as documentation.

MANIFEST.in lists each file, generated from the files git tracks. The sdist
includes exactly those, and setup.py copies exactly those into the wheel, so a
local file that isn't tracked (a .env, a log, a cache) can't ship.
"""

import os
import re
import shutil
from pathlib import Path, PurePosixPath

import pytest

from signalwire.cli.pydocs._bundle import (
    installed_text,
    is_doc_file,
    iter_doc_files,
    manifest_files,
    render_manifest,
    tracked_doc_files,
)

REPO = Path(__file__).resolve().parents[3]
HAS_GIT = shutil.which("git") is not None and (REPO / ".git").exists()


@pytest.mark.parametrize(
    ("rel", "shipped"),
    [
        ("docs/agent_guide.md", True),
        ("examples/simple_agent.py", True),
        ("tutorial/multi_agents/sales_knowledge.swsearch", True),
        ("README.md", True),
        ("LICENSE", True),
        ("docs/pipecat_comparison.md", False),
        ("docs/livekit_comparison.md", False),
        ("examples/__pycache__/simple_agent.cpython-312.pyc", False),
        ("tutorial/fred/.env", False),
        ("tutorial/fred/.env.example", True),
        ("examples/certs/server.pem", False),
        ("examples/debug.log", False),
        ("tests/unit/test_x.py", False),
        ("signalwire/signalwire/__init__.py", False),
    ],
)
def test_is_doc_file(rel: str, shipped: bool) -> None:
    assert is_doc_file(rel) is shipped


@pytest.mark.skipif(not HAS_GIT, reason="needs a git checkout")
def test_manifest_lists_exactly_the_tracked_docs() -> None:
    assert manifest_files(REPO) == tracked_doc_files(REPO), (
        "MANIFEST.in is out of date; from the repository root, run "
        "python signalwire/signalwire/cli/pydocs/_bundle.py"
    )


@pytest.mark.skipif(not HAS_GIT, reason="needs a git checkout")
def test_manifest_is_as_generated() -> None:
    assert (REPO / "MANIFEST.in").read_text(encoding="utf-8") == render_manifest(REPO)


def test_manifest_has_no_patterns() -> None:
    # A graft or wildcard would take whatever is on disk, tracked or not
    for line in (REPO / "MANIFEST.in").read_text(encoding="utf-8").splitlines():
        words = line.split()
        if not words or words[0].startswith("#"):
            continue
        assert words[0] in ("include", "global-exclude"), line
        if words[0] == "include":
            assert len(words) == 2 and not any(c in words[1] for c in "*?["), line


def test_files_not_listed_never_ship(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "examples").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    # Local files a developer might have: none of them is in MANIFEST.in
    for junk in (
        "examples/.env.production",
        "examples/debug.log",
        "docs/notes.md",
        "examples/config.json",
    ):
        (tmp_path / junk).write_text("secret\n", encoding="utf-8")
    (tmp_path / "MANIFEST.in").write_text("include docs/guide.md\n", encoding="utf-8")
    assert list(iter_doc_files(tmp_path)) == ["docs/guide.md"]


def test_an_installed_copy_is_walked(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Readme\n", encoding="utf-8")
    assert list(iter_doc_files(tmp_path)) == ["README.md", "docs/guide.md"]


def test_installed_text_points_source_links_at_the_package() -> None:
    text = "See [the code](../signalwire/signalwire/core/contexts.py#L10) and [a doc](other.md)."
    assert installed_text("docs/x.md", text) == (
        "See [the code](../../core/contexts.py#L10) and [a doc](other.md)."
    )
    assert installed_text("examples/x.py", text) == text


_LINK = re.compile(r"\]\(([^)\s]+)\)")
_FENCE = re.compile(r"^\s*(```|~~~).*?^\s*\1", re.DOTALL | re.MULTILINE)


def test_links_resolve_once_installed() -> None:
    # Installed, the docs are in <package>/_docs/ and the package is one level
    # up; every relative link must reach a shipped doc or the package's source
    shipped = set(manifest_files(REPO))
    broken = []
    for rel in sorted(shipped):
        if not rel.endswith(".md"):
            continue
        text = installed_text(rel, (REPO / rel).read_text(encoding="utf-8"))
        for target in _LINK.findall(_FENCE.sub("", text)):
            path = target.split("#", 1)[0]
            if not path or re.match(r"^[a-z][a-z0-9+.-]*:", path):
                continue
            where = PurePosixPath(
                os.path.normpath(PurePosixPath("pkg/_docs") / rel).rsplit("/", 1)[0]
            )
            resolved = PurePosixPath(os.path.normpath(where / path)).as_posix()
            if resolved.startswith("pkg/_docs/"):
                if (
                    resolved[len("pkg/_docs/") :] in shipped
                    or (REPO / resolved[len("pkg/_docs/") :]).is_dir()
                ):
                    continue
            elif (
                resolved.startswith("pkg/")
                and (REPO / "signalwire/signalwire" / resolved[4:]).exists()
            ):
                continue
            broken.append(f"{rel}: {target}")
    assert broken == []
