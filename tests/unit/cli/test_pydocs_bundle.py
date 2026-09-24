"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Tests for which repository files install with the package as documentation.

setup.py copies them into the wheel from the list in
signalwire/cli/pydocs/_bundle.py, and MANIFEST.in puts them in the source
distribution that the wheel is built from. The two must agree.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

from signalwire.cli.pydocs._bundle import DOC_EXCLUDES, DOC_SOURCES, is_doc_file, iter_doc_files

REPO = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    ("rel", "shipped"),
    [
        ("docs/agent_guide.md", True),
        ("examples/simple_agent.py", True),
        ("tutorial/multi_agents/sales_knowledge.swsearch", True),
        ("README.md", True),
        ("docs/pipecat_comparison.md", False),
        ("docs/livekit_comparison.md", False),
        ("examples/__pycache__/simple_agent.cpython-312.pyc", False),
        ("tutorial/fred/.env", False),
        ("tutorial/fred/.env.example", True),
        ("examples/certs/server.pem", False),
        ("tests/unit/test_x.py", False),
        ("signalwire/signalwire/__init__.py", False),
    ],
)
def test_is_doc_file(rel: str, shipped: bool) -> None:
    assert is_doc_file(rel) is shipped


GIT = shutil.which("git")


@pytest.mark.skipif(GIT is None or not (REPO / ".git").exists(), reason="needs a git checkout")
def test_ships_exactly_the_tracked_files() -> None:
    assert GIT is not None
    tracked = subprocess.run(  # noqa: S603  # fixed arguments, in the repository
        [GIT, "ls-files", "--", *DOC_SOURCES],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    expected = sorted(rel for rel in tracked if rel not in DOC_EXCLUDES)
    assert sorted(iter_doc_files(REPO)) == expected


def test_manifest_matches_the_list() -> None:
    lines = [
        line.split()
        for line in (REPO / "MANIFEST.in").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    grafted = {words[1] for words in lines if words[0] == "graft"}
    included = {word for words in lines if words[0] == "include" for word in words[1:]}
    excluded = {word for words in lines if words[0] == "exclude" for word in words[1:]}
    directories = {source for source in DOC_SOURCES if (REPO / source).is_dir()}
    assert grafted == directories
    assert included == set(DOC_SOURCES) - directories
    assert excluded == set(DOC_EXCLUDES)
