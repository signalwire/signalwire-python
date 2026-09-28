#!/usr/bin/env python3
"""check_swml_verbs_agree.py — the SWML-VERBS-AGREE gate.

python's SWML verb set exists twice, and the two copies are produced by different
machinery:

* **static** — ``signalwire/signalwire/core/swml_verbs_generated.py``'s ``_SwmlVerbs``
  Protocol, which ``SWMLBuilder`` inherits under ``TYPE_CHECKING``. porting-sdk's
  ``generate_python_rest_types.py`` writes it from ``porting-sdk/schema.json``, and the
  GEN-FRESH gate keeps it current with that file.
* **runtime** — the methods ``SWMLBuilder`` installs on each instance from the BUNDLED
  ``signalwire/signalwire/schema.json`` (``SchemaUtils.get_all_verb_names``).

The bundle once fell eight verbs behind the stub (echo, execute_rpc, ring, set_meta,
stream, stop_stream, transcribe, transcribe_stop), so a type checker accepted
``builder.echo()`` and the call raised ``AttributeError``.

The bundle's FRESHNESS (bundled bytes == porting-sdk's schema.json == ARS output, plus the
``schema.json.sha256`` record) is the fleet-shared SCHEMA-BUNDLE gate,
``porting-sdk/scripts/port_schema_bundle.py check`` (contract:
``porting-sdk/docs/SCHEMA_ROUND_TRIP.md``). This gate is the python-specific half:
**AGREE** — the verb methods the runtime installs equal the verb methods the stub declares,
compared in both directions.

``--selftest`` proves AGREE can fail: a bundle with a verb removed must fail (runtime short
of the stub), and a bundle with an extra verb must fail (runtime ahead of the stub).
Scratch copies go under ``<repo>/.sw-tmp/``, which is gitignored.

The verdict is the ``==> SWML-VERBS-AGREE PASS|FAIL`` line; the exit code matches it.

Usage::

    python3 scripts/check_swml_verbs_agree.py [--selftest]
"""

from __future__ import annotations

import argparse
import copy
import json
import keyword
import shutil
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = REPO_ROOT / "signalwire" / "signalwire"
BUNDLE = PACKAGE_DIR / "schema.json"
SCRATCH = REPO_ROOT / ".sw-tmp" / "swml-verbs-agree-selftest"

_TAG = "[swml-verbs-agree]"


def stub_verb_methods() -> set[str]:
    """The verb methods the static ``_SwmlVerbs`` Protocol declares."""
    from signalwire.core import swml_verbs_generated as gen

    return {
        name
        for name, value in vars(gen._SwmlVerbs).items()
        if isinstance(value, types.FunctionType) and not name.startswith("__")
    }


def reachable_verb_methods(builder: object, candidates: set[str]) -> set[str]:
    """The names among ``candidates`` a caller can write as ``builder.<name>(...)`` and
    reach a schema-installed verb method.

    A name counts when it is a plain identifier (``builder.return`` is a syntax error,
    so the keyword spelling never counts), is not a class attribute (the hand-written
    answer/hangup/ai/play/say methods are, and the stub leaves them out by design), and
    resolves on the instance to a callable. Resolution is measured, through the real
    ``__getattr__`` the installer relies on, not derived from the schema.
    """
    found: set[str] = set()
    for name in candidates:
        if not name.isidentifier() or keyword.iskeyword(name) or name.startswith("_"):
            continue
        if hasattr(type(builder), name):
            continue
        try:
            value = getattr(builder, name)
        except AttributeError:
            continue
        if callable(value):
            found.add(name)
    return found


def runtime_verb_methods(schema_path: Path) -> set[str]:
    """The verb methods ``SWMLBuilder`` reaches at runtime when built over ``schema_path``.

    Candidates are every stub name plus every verb the runtime itself lists (raw and
    keyword-escaped), so a verb present on only one side is still probed.
    """
    from signalwire.core.swml_builder import SWMLBuilder
    from signalwire.core.swml_service import SWMLService

    service = SWMLService(
        name="schema-bundle", route="/schema-bundle", schema_path=str(schema_path)
    )
    builder = SWMLBuilder(service)
    if service.schema_utils is None:
        msg = f"SWMLService loaded no schema from {schema_path}"
        raise RuntimeError(msg)
    listed = set(service.schema_utils.get_all_verb_names())
    candidates = stub_verb_methods() | listed | {f"{v}_" for v in listed}
    return reachable_verb_methods(builder, candidates)


def check_agree(schema_path: Path) -> list[str]:
    """Problems with runtime-vs-static agreement; empty when the sets are equal."""
    runtime = runtime_verb_methods(schema_path)
    stub = stub_verb_methods()
    problems: list[str] = []
    if not stub:
        problems.append("stub declares no verb methods — nothing was compared")
    if stub - runtime:
        problems.append(
            f"declared by the stub but not installed at runtime (AttributeError): "
            f"{sorted(stub - runtime)}"
        )
    if runtime - stub:
        problems.append(
            f"installed at runtime but not declared by the stub (invisible to a type "
            f"checker): {sorted(runtime - stub)}"
        )
    return problems


def run() -> list[str]:
    """AGREE against the committed tree."""
    agree = [f"AGREE: {p}" for p in check_agree(BUNDLE)]
    if not agree:
        print(
            f"{_TAG} AGREE ok: runtime == stub ({len(stub_verb_methods())} verb methods)"
        )
    return agree


def selftest() -> list[str]:
    """Negative controls: each broken input must make AGREE fail."""
    failures: list[str] = []
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    try:
        data = BUNDLE.read_bytes()
        schema = json.loads(data)
        methods = schema["$defs"]["SWMLMethod"]["anyOf"]

        # 2. A bundle missing a verb must fail AGREE (stub ahead of runtime).
        missing = copy.deepcopy(schema)
        missing["$defs"]["SWMLMethod"]["anyOf"] = [
            m for m in methods if m.get("$ref") != "#/$defs/Echo"
        ]
        if len(missing["$defs"]["SWMLMethod"]["anyOf"]) != len(methods) - 1:
            failures.append(
                "control missing-verb: Echo is not in SWMLMethod — control not built"
            )
        else:
            path = SCRATCH / "missing.json"
            path.write_text(json.dumps(missing), encoding="utf-8")
            got = check_agree(path)
            print(
                f"{_TAG} control missing-verb(echo) -> {'FAIL (expected)' if got else 'PASS'}"
            )
            if not any("echo" in p for p in got):
                failures.append(
                    "control missing-verb: AGREE did not report echo absent at runtime"
                )

        # 3. A bundle with an extra verb must fail AGREE (runtime ahead of stub).
        extra = copy.deepcopy(schema)
        extra["$defs"]["SelftestVerb"] = {
            "type": "object",
            "properties": {"selftest_verb": {"type": "object", "properties": {}}},
            "required": ["selftest_verb"],
        }
        extra["$defs"]["SWMLMethod"]["anyOf"].append({"$ref": "#/$defs/SelftestVerb"})
        path = SCRATCH / "extra.json"
        path.write_text(json.dumps(extra), encoding="utf-8")
        got = check_agree(path)
        print(
            f"{_TAG} control extra-verb(selftest_verb) -> {'FAIL (expected)' if got else 'PASS'}"
        )
        if not any("selftest_verb" in p for p in got):
            failures.append(
                "control extra-verb: AGREE did not report selftest_verb missing from the stub"
            )
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    return failures


def main(argv: list[str] | None = None) -> int:
    """CLI entry point; prints the verdict line and returns its exit code."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument(
        "--selftest", action="store_true", help="also run the negative controls"
    )
    args = ap.parse_args(argv)

    sys.path.insert(0, str(REPO_ROOT / "signalwire"))
    problems = run()
    if args.selftest:
        problems += [f"SELFTEST: {p}" for p in selftest()]
    for p in problems:
        print(f"{_TAG} {p}")
    if problems:
        print("==> SWML-VERBS-AGREE FAIL")
        return 1
    print("==> SWML-VERBS-AGREE PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
