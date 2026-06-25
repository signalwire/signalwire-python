#!/usr/bin/env bash
# Generate the SignalWire Python SDK API reference.
#
# Ported from the SDK-docs POC (build/python/gen.sh): install the SDK editable
# so mkdocstrings can import it, discover each importable top-level subpackage of
# `signalwire`, and write one `::: signalwire.<name>` page per subpackage. The
# landing page is the SDK README.
#
# The package is nested (signalwire/signalwire/) and mkdocstrings needs the
# editable install to resolve imports — that is preserved here.
#
# Usage:  reference/gen.sh            # generate pages + `mkdocs build`
#         reference/gen.sh --no-build # generate pages only (mike runs the build)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .../reference
REPO="$(cd "$HERE/.." && pwd)"                          # repo root
DOCS="$HERE/_docs"
CFG="$HERE/mkdocs.yml"

# Install the SDK + deps so mkdocstrings can import it (idempotent).
pip install -q -e "$REPO"

# Build the docs tree: README landing page + one API page per subpackage.
rm -rf "$DOCS"
mkdir -p "$DOCS/api"
cp "$REPO/README.md" "$DOCS/index.md"

# Navbar assets (Fern tokens/CSS/JS/img) live under reference/assets but must be
# copied into the docs tree so Material ships them with the site.
cp -r "$HERE/assets" "$DOCS/assets"

PYTHONPATH="$REPO/signalwire" python - "$DOCS/api" <<'PY'
import sys, os, pkgutil, importlib
out = sys.argv[1]
pkg = importlib.import_module("signalwire")
names = sorted(m.name for m in pkgutil.iter_modules(pkg.__path__))
written = []
for name in names:
    if name.startswith("_"):
        continue
    slug = name.replace("_", "-")
    with open(os.path.join(out, f"{slug}.md"), "w") as fh:
        fh.write(f"# signalwire.{name}\n\n::: signalwire.{name}\n")
    written.append(name)
# A small nav index page so the API section has a landing entry.
with open(os.path.join(out, "index.md"), "w") as fh:
    fh.write("# API reference\n\n")
    fh.write("Auto-generated reference for each top-level package of the "
             "SignalWire Python SDK.\n\n")
    for n in written:
        fh.write(f"- [signalwire.{n}]({n.replace('_','-')}.md)\n")
print("api pages:", ", ".join(written))
PY

if [ "${1:-}" = "--no-build" ]; then
  echo "pages generated under $DOCS (skipping mkdocs build)"
  exit 0
fi

mkdocs build --config-file "$CFG"
echo "python -> $HERE/_site ($(find "$HERE/_site" -name '*.html' | wc -l) pages)"
