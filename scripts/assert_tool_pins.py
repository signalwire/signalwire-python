#!/usr/bin/env python3
"""TOOL-PINS gate — the linters/typecheckers that decide gate verdicts are the
PINNED versions, and the type stubs they read are exactly the DECLARED ones —
not whatever happened to be installed.

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

TYPE STUBS (added 2026-08-04) — the same defect INVERTED. A version check cannot see
a package that is simply ABSENT on one side, and a type stub's mere presence moves
TYPECHECK's verdict: with the stub mypy resolves real signatures, without it
`ignore_missing_imports` makes those calls `Any`. Because every repo on a dev box
tends to resolve ONE shared venv, a stub declared by a NEIGHBOURING repo silently
lands on this repo's path. Measured: types-PyYAML was declared only in
api-reference-specs' requirements-dev.txt; with it importable mypy reported 3
`redundant-cast` errors, and without it — which is what CI had — mypy reported
"Success: no issues found in 362 source files". Local and CI were type-checking the
same source against different type information, and the local error invited deleting
casts that were load-bearing in CI. So the stub set is now pinned in BOTH directions:
importable-but-undeclared and declared-but-absent are each a failure.

Set SW_ALLOW_TOOL_VERSION_DRIFT=1 to downgrade a mismatch to a warning, for a
deliberate bump-and-fix run only (then update requirements-dev.txt and land the
resulting fixes in the same commit).
"""

from __future__ import annotations

import os
import re
import sys
from importlib.metadata import (
    PackageNotFoundError,
    distributions,
    version as dist_version,
)
from pathlib import Path

# Tools whose version changes a gate verdict. Keyed by the distribution name in
# requirements-dev.txt; the value is the gate(s) it decides, for the error message.
PINNED_TOOLS = {
    "ruff": "FMT / LINT / EXAMPLES-* / REPO-*",
    "mypy": "TYPECHECK",
}

# Distributions whose mere PRESENCE changes TYPECHECK's verdict. A type-stub package
# (PEP 561 `types-*` / `*-stubs`) supplies type information for a third-party import;
# with it, mypy resolves real signatures, and without it `ignore_missing_imports`
# makes those calls `Any`. Same source, two verdicts — and unlike a version skew it is
# invisible to a version check, because the package is simply absent on one side.
#
# This box resolves ONE SHARED venv across every sibling repo, so a stub declared by a
# NEIGHBOURING repo lands on this repo's path. Measured 2026-08-04: types-PyYAML was
# declared only in api-reference-specs' requirements-dev.txt, and its presence made
# mypy report 3 `redundant-cast` errors that CI (which installs only this repo's
# manifest) did not have. Deleting those casts to satisfy the local error would have
# broken CI, where yaml.dump() is Any and the casts were load-bearing.
#
# So: any stub importable by the gate interpreter must be DECLARED here. Declared but
# absent is caught by the same pass — an environment that lacks a stub the manifest
# requires produces CI's verdict for neither side.
STUB_SUFFIX = "-stubs"
STUB_PREFIX = "types-"

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


def _is_stub(name: str) -> bool:
    """True if the distribution name is a PEP 561 type-stub package."""
    low = name.lower()
    return low.startswith(STUB_PREFIX) or low.endswith(STUB_SUFFIX)


def declared_stubs() -> dict[str, str | None]:
    """Stub distributions named in the manifest -> pinned version (None if loose)."""
    found: dict[str, str | None] = {}
    for raw in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0]
        if not line.strip():
            continue
        m = PIN_RE.match(line)
        if m and _is_stub(m.group("name")):
            found[m.group("name").lower()] = m.group("version")
            continue
        m = LOOSE_RE.match(line)
        if m and _is_stub(m.group("name")):
            found[m.group("name").lower()] = None
    return found


def installed_stubs() -> dict[str, str]:
    """Stub distributions importable by THIS interpreter -> installed version."""
    found: dict[str, str] = {}
    for dist in distributions():
        name = dist.metadata["Name"]
        if name and _is_stub(name):
            found[name.lower()] = dist.version
    return found


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

    # 3. Type stubs — presence, not just version, decides TYPECHECK. Both directions
    #    are a local≠CI split, so both fail:
    #      * importable but UNDECLARED — a neighbouring repo's stub leaked onto this
    #        repo's path via the shared venv; local sees types CI does not have.
    #      * declared but ABSENT — this environment types less than CI does.
    want_stubs = declared_stubs()
    have_stubs = installed_stubs()

    for name, ver in sorted(have_stubs.items()):
        if name not in want_stubs:
            problems.append(
                f"{name}=={ver} is importable by {sys.executable} but is NOT declared "
                f"in requirements-dev.txt. A type stub's PRESENCE changes TYPECHECK's "
                f"verdict on unchanged source, so this interpreter and CI (which "
                f"installs only this manifest) are running different type checks. "
                f"Either declare it as {name}=={ver} — and land any resulting source "
                f"changes in the same commit — or uninstall it."
            )

    for name, want in sorted(want_stubs.items()):
        have = have_stubs.get(name)
        if have is None:
            problems.append(
                f"{name} is declared in requirements-dev.txt but is not importable by "
                f"{sys.executable}. TYPECHECK here sees LESS type information than CI "
                f"does, so it can pass on code CI rejects. Install it: "
                f"pip install -r requirements-dev.txt"
            )
        elif want is not None and have != want:
            problems.append(
                f"{name} is {have}, but requirements-dev.txt pins {want}. Typeshed "
                f"revises stubs continuously and an overload change moves TYPECHECK's "
                f"verdict. Fix: pip install {name}=={want}"
            )
        elif want is None:
            problems.append(
                f"{name} is declared without an exact pin. A stub revision changes "
                f"TYPECHECK's verdict on code that never changed — pin it exact "
                f"({name}=={have})."
            )

    if not problems:
        names = ", ".join(f"{t}=={v}" for t, v in sorted(pinned.items()))
        stub_note = (
            f"; stubs: {', '.join(sorted(have_stubs))}" if have_stubs else "; no stubs"
        )
        print(f"[tool-pins] pinned and installed as declared: {names}{stub_note}")
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
