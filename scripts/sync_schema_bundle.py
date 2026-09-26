#!/usr/bin/env python3
"""sync_schema_bundle.py — re-bundle python's runtime ``schema.json`` from porting-sdk.

``SWMLBuilder`` / ``SWMLService`` install their SWML verb methods at runtime from the
bundled ``signalwire/signalwire/schema.json``. That file is a copy of
``porting-sdk/schema.json`` — the same file porting-sdk's generator reads to write the
static verb stub (``swml_verbs_generated.py``) — so the two must move together.

This writes the copy the way porting-sdk's ``scripts/fanout_schema.py`` writes every port
copy: the source bytes verbatim, plus ``schema.json.sha256`` beside it (the record
``fanout_schema.port_hash_record`` produces). The SCHEMA-BUNDLE gate
(``scripts/check_schema_bundle.py``) then fails if either falls behind.

Usage::

    python3 scripts/sync_schema_bundle.py --porting-sdk ../porting-sdk
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = REPO_ROOT / "signalwire" / "signalwire"
BUNDLE = PACKAGE_DIR / "schema.json"
RECORD = PACKAGE_DIR / "schema.json.sha256"


def main(argv: list[str] | None = None) -> int:
    """Copy porting-sdk's schema.json into the package and write its sha256 record."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument(
        "--porting-sdk", type=Path, required=True, help="porting-sdk checkout"
    )
    args = ap.parse_args(argv)
    psdk = args.porting_sdk.resolve()
    source = psdk / "schema.json"
    fanout = psdk / "scripts" / "fanout_schema.py"
    if not source.is_file() or not fanout.is_file():
        print(f"FATAL: {source} or {fanout} not found", file=sys.stderr)
        return 2

    # porting-sdk's fanout_schema.py owns the record format; load it rather than
    # restating it, so the record written here is the one its fan-out writes.
    spec = importlib.util.spec_from_file_location("fanout_schema", fanout)
    if spec is None or spec.loader is None:
        print(f"FATAL: cannot load {fanout}", file=sys.stderr)
        return 2
    module = importlib.util.module_from_spec(spec)
    sys.modules["fanout_schema"] = module
    spec.loader.exec_module(module)
    data = source.read_bytes()
    record = module.port_hash_record(data)
    BUNDLE.write_bytes(data)
    RECORD.write_text(record, encoding="utf-8")
    print(f"bundled {len(data)} B from {source}: {record.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
