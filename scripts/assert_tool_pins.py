#!/usr/bin/env python3
"""TOOL-PINS gate — the linters/typecheckers that decide gate verdicts are the
PINNED versions, not whatever happened to be installed.

WHY THIS GATE EXISTS
--------------------
ruff and mypy both change their findings between releases: ruff adds rules and
adjusts format heuristics, mypy adds checks and narrows inference. If the version
that runs is not the version the repo declares, the gate's verdict becomes a
function of WHEN the environment was provisioned rather than of the source — the
classic green-locally/red-in-CI split, where CI installs fresh (newest allowed) and
a contributor runs whatever they installed months ago. No local run reproduces the
CI failure, because the difference is not in the code.

requirements-dev.txt pins both EXACT. Pinning the manifest is necessary but NOT
sufficient: an environment provisioned before a pin was tightened keeps its old
version indefinitely (pip does not re-resolve an already-satisfied requirement),
so the pin can be right in the file and violated in the interpreter that actually
runs the gates. This gate compares what is IMPORTABLE against what is DECLARED,
reading the expected versions out of requirements-dev.txt so there is exactly one
source of truth and the two cannot drift apart.

Measured when this gate was added: requirements-dev.txt said `mypy>=1.8` (an open
floor), and the interpreter running the gates had mypy 1.18.2 — a full major
version behind what a fresh CI install would resolve. TYPECHECK's verdict here and
in CI were being produced by different type checkers.

Set SW_ALLOW_TOOL_VERSION_DRIFT=1 to downgrade a mismatch to a warning, for a
deliberate bump-and-fix run only (then update requirements-dev.txt and land the
resulting fixes in the same commit).
"""

from __future__ import annotations

import os
import re
import sys
from importlib.metadata import PackageNotFoundError, version as dist_version
from pathlib import Path

# Tools whose version changes a gate verdict. Keyed by the distribution name in
# requirements-dev.txt; the value is the gate(s) it decides, for the error message.
PINNED_TOOLS = {
    "ruff": "FMT / LINT / EXAMPLES-* / REPO-*",
    "mypy": "TYPECHECK",
}

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = REPO_ROOT / "requirements-dev.txt"

# `name==1.2.3` with optional surrounding whitespace, ignoring trailing comments.
PIN_RE = re.compile(r"^\s*(?P<name>[A-Za-z0-9._-]+)\s*==\s*(?P<version>[^\s#;]+)")
# Any non-`==` constraint on a tool we require to be pinned exact.
LOOSE_RE = re.compile(r"^\s*(?P<name>[A-Za-z0-9._-]+)\s*(?P<op>[><~!]=?|===)\s*")


def declared_pins() -> tuple[dict[str, str], dict[str, str]]:
    """Return ({tool: pinned_version}, {tool: offending_line}) from the manifest."""
    pinned: dict[str, str] = {}
    loose: dict[str, str] = {}
    for raw in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0]
        if not line.strip():
            continue
        m = PIN_RE.match(line)
        if m and m.group("name").lower() in PINNED_TOOLS:
            pinned[m.group("name").lower()] = m.group("version")
            continue
        m = LOOSE_RE.match(line)
        if m and m.group("name").lower() in PINNED_TOOLS:
            loose[m.group("name").lower()] = raw.strip()
    return pinned, loose


def installed_version(tool: str) -> str | None:
    """The tool's version as installed for THIS interpreter.

    Read from the installed distribution metadata rather than by shelling out to
    `python3 -m <tool> --version`. Same answer (run-ci invokes the tools through
    this interpreter, so its site-packages is what decides), but no subprocess —
    which keeps the gate itself clean under the repo's own ruff ruleset (S603
    flags subprocess calls). Removing the rule's premise beats suppressing it.
    """
    try:
        return dist_version(tool)
    except PackageNotFoundError:
        return None


def main() -> int:
    allow_drift = os.environ.get("SW_ALLOW_TOOL_VERSION_DRIFT") == "1"
    pinned, loose = declared_pins()
    problems: list[str] = []

    # 1. Every version-sensitive tool must be pinned EXACT in the manifest. An open
    #    floor is the defect itself, whatever happens to be installed today.
    for tool, gates in PINNED_TOOLS.items():
        if tool in pinned:
            continue
        if tool in loose:
            problems.append(
                f"{tool} is NOT pinned exact in requirements-dev.txt "
                f'(found "{loose[tool]}"). It decides {gates}, so an open '
                f"constraint lets CI run a different version than local. "
                f"Use {tool}=={{version}}."
            )
        else:
            problems.append(
                f"{tool} is missing from requirements-dev.txt but decides {gates}; "
                f"declare it as {tool}=={{version}}."
            )

    # 2. The interpreter running the gates must actually HAVE the pinned version.
    for tool, want in pinned.items():
        have = installed_version(tool)
        if have is None:
            problems.append(
                f"{tool} is pinned to {want} but is not importable by "
                f"{sys.executable} — the gate it decides ({PINNED_TOOLS[tool]}) "
                f"cannot run. Install it: pip install {tool}=={want}"
            )
        elif have != want:
            problems.append(
                f"{tool} is {have}, but requirements-dev.txt pins {want}. "
                f"{PINNED_TOOLS[tool]} would be decided by a different version "
                f"than CI uses. Fix: pip install {tool}=={want}"
            )

    if not problems:
        names = ", ".join(f"{t}=={v}" for t, v in sorted(pinned.items()))
        print(f"[tool-pins] pinned and installed as declared: {names}")
        return 0

    label = "WARNING" if allow_drift else "FAIL"
    for p in problems:
        print(f"[tool-pins] {label}: {p}", file=sys.stderr)
    if allow_drift:
        print(
            "[tool-pins] SW_ALLOW_TOOL_VERSION_DRIFT=1 — not failing.", file=sys.stderr
        )
        return 0
    print(
        "[tool-pins] A linter/typechecker version that differs between local and CI "
        "makes a gate red on code that never changed. Set "
        "SW_ALLOW_TOOL_VERSION_DRIFT=1 only for a deliberate bump run.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
