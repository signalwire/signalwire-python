#!/usr/bin/env python3
"""Emit ``port_surface_native.json`` — the doc-audit resolvable-name sidecar.

WHY THE REFERENCE NEEDS ONE. ``porting-sdk/scripts/enumerate_python.py`` excludes
``signalwire.livewire.*`` from the surface oracle BY DESIGN (user-approved
2026-07-24): livewire is the LiveKit-agents integration shipped only by python and
typescript, so putting it in the cross-port oracle would force ~44 omissions x 8
non-shipping ports. The 2 ports that ship it record it as a port-specific ADDITION.

But ``livewire/`` DOCS are inside the doc-audit perimeter, and doc-audit resolves doc
references against that same oracle. So every livewire API reference was unresolvable
BY CONSTRUCTION — 7 findings for 5 methods that are all genuinely implemented in
``signalwire/livewire/__init__.py`` (generate_reply, interrupt, rtc_session, run_app,
wait_for_participant). Two correct decisions colliding, not a doc error.

An ignore-ledger entry would have been the wrong fix: these are REAL shipped members,
so excusing them by name is a permanent blind spot that would also silence a future
genuine typo in those same names.

audit_docs.py already has the right seam — ``--native-names`` unions a sidecar into
the resolvable ``known`` set ("the enumerator carrying the port's idiom, not a
doc-audit omission"). This script fills it for the reference: the surface oracle's
own walker, run over exactly the modules the oracle EXCLUDES but the port really
ships. Names come from the source, never a hand-maintained list, so a renamed or
deleted livewire method stops resolving instead of silently staying excused.

Emits the NESTED sidecar shape (``{"names": "python-native", "modules": {...}}``),
matching java/dotnet.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The oracle-excluded module prefixes this port DOES ship and DOES document. Keep in
# step with _EXCLUDE_MODULES in porting-sdk/scripts/enumerate_python.py: an entry here
# is only legitimate when the module is excluded from the oracle AND really shipped.
NATIVE_ONLY_PREFIXES = ("signalwire.livewire",)


def _resolve_porting_sdk() -> Path:
    for cand in (REPO.parent / "porting-sdk", REPO / "porting-sdk"):
        if (cand / "scripts" / "enumerate_python.py").is_file():
            return cand
    raise SystemExit(
        "emit_surface_native.py: porting-sdk not found next to this repo "
        "(expected ../porting-sdk/scripts/enumerate_python.py)"
    )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=REPO / "port_surface_native.json")
    args = ap.parse_args(argv)

    psdk = _resolve_porting_sdk()
    sys.path.insert(0, str(psdk / "scripts"))
    import enumerate_python as ep  # noqa: E402  (path set above)

    # ``enumerate_module`` short-circuits on ``_module_excluded`` and returns an empty
    # entry — which is the whole point of the oracle exclusion and exactly what we need
    # to step past HERE, since a native-only module is excluded BY DEFINITION. Suppress
    # the check for our declared prefixes ONLY; every other rule (public-name filter,
    # _EXCLUDE_CLASSES, member selection) still applies unchanged, so the sidecar
    # records precisely what the oracle would have recorded had the module not been
    # excluded — rather than a second, drifting notion of "public".
    _orig_excluded = ep._module_excluded

    def _excluded_except_native_only(module_name: str) -> bool:
        if module_name.startswith(NATIVE_ONLY_PREFIXES):
            return False
        return _orig_excluded(module_name)

    ep._module_excluded = _excluded_except_native_only
    # Fail loud if the exclusion we are stepping past ever stops existing: a
    # native-only prefix that the oracle no longer excludes belongs in the ORACLE, and
    # this sidecar would then be double-counting real cross-port surface.
    for prefix in NATIVE_ONLY_PREFIXES:
        if not _orig_excluded(prefix):
            raise SystemExit(
                f"emit_surface_native.py: {prefix!r} is NO LONGER excluded from the "
                "surface oracle. Drop it from NATIVE_ONLY_PREFIXES — the oracle now "
                "covers it, and keeping it here would resolve doc refs twice."
            )

    pkg_root = REPO / "signalwire" / "signalwire"
    if not (pkg_root / "__init__.py").is_file():
        raise SystemExit(f"emit_surface_native.py: no package at {pkg_root}")

    modules: dict[str, dict] = {}
    for path in sorted(pkg_root.rglob("*.py")):
        rel = path.relative_to(pkg_root).with_suffix("")
        parts = [p for p in rel.parts if p != "__init__"]
        name = ".".join(["signalwire", *parts])
        if not name.startswith(NATIVE_ONLY_PREFIXES):
            continue
        # enumerate_module applies the oracle's OWN public/exclude rules, so the
        # sidecar records exactly what the oracle would have recorded had the module
        # not been excluded — no second, drifting notion of "public".
        entry = ep.enumerate_module(path, name)
        if entry["classes"] or entry["functions"]:
            modules[name] = entry

    if not modules:
        raise SystemExit(
            "emit_surface_native.py: no native-only modules found — refusing to write "
            "an empty sidecar (an empty sidecar silently resolves NOTHING, which reads "
            f"as 'no findings'). Checked prefixes: {NATIVE_ONLY_PREFIXES}"
        )

    doc = {"names": "python-native", "modules": modules}
    args.out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    members = sum(
        len(m) for e in modules.values() for m in (e.get("classes") or {}).values()
    ) + sum(len(e.get("functions") or []) for e in modules.values())
    print(
        f"emit_surface_native: wrote {args.out} "
        f"({len(modules)} module(s), {members} native member(s))"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
