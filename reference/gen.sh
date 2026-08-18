#!/usr/bin/env bash
# Generate the SignalWire Python SDK API reference.
#
# Ported from the SDK-docs POC (build/python/gen.sh): install the SDK editable
# so mkdocstrings can import it, discover each importable top-level subpackage of
# `signalwire`, and write one `::: signalwire.<name>` page per subpackage. The
# landing page is generated (package index + links to the guides), not the SDK
# README, whose repo-relative links don't resolve in the reference site.
#
# The package is nested (signalwire/signalwire/) and mkdocstrings needs the
# editable install to resolve imports — that is preserved here.
#
# Usage:  reference/gen.sh              # generate pages + strict `mkdocs build`
#         reference/gen.sh --no-build   # generate pages only (the caller builds/deploys)
#         reference/gen.sh --no-install # skip the pip installs (the caller installed already)
#         Both flags are accepted together, in either order.
set -euo pipefail

NO_BUILD=0
NO_INSTALL=0
for arg in "$@"; do
  case "$arg" in
    --no-build)   NO_BUILD=1 ;;
    --no-install) NO_INSTALL=1 ;;
    *) echo "gen.sh: unknown option: $arg" >&2; exit 2 ;;
  esac
done

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .../reference
REPO="$(cd "$HERE/.." && pwd)"                          # repo root
DOCS="$HERE/_docs"
CFG="$HERE/mkdocs.yml"

# Install the doc toolchain + the SDK (editable, so mkdocstrings can import it).
# Use `python3 -m pip` so this works whether or not a bare `pip` is on PATH.
# CI installs both itself and passes --no-install, so the pinned environment is
# not re-resolved underneath the build.
if [ "$NO_INSTALL" -eq 0 ]; then
  python3 -m pip install -q -r "$HERE/requirements.txt"
  python3 -m pip install -q -e "$REPO"
fi

# Build the docs tree: generated landing page + one API page per subpackage.
rm -rf "$DOCS"
mkdir -p "$DOCS/api"

# Navbar assets (Fern tokens/CSS/JS/img) live under reference/assets but must be
# copied into the docs tree so Material ships them with the site.
cp -r "$HERE/assets" "$DOCS/assets"

PYTHONPATH="$REPO/signalwire" python3 - "$DOCS/api" <<'PY'
import sys, os, pkgutil, importlib
api_out = sys.argv[1]
docs_root = os.path.dirname(api_out.rstrip("/"))
pkg = importlib.import_module("signalwire")
names = sorted(m.name for m in pkgutil.iter_modules(pkg.__path__))
written = []
for name in names:
    if name.startswith("_"):
        continue
    slug = name.replace("_", "-")
    with open(os.path.join(api_out, f"{slug}.md"), "w") as fh:
        fh.write(f"# signalwire.{name}\n\n::: signalwire.{name}\n")
    written.append(name)

# An unresolvable install yields zero modules, and every command below still
# succeeds, so `set -e` would let a gutted site sail through to deploy. Fail loud.
if not written:
    sys.exit("gen.sh: no API pages generated (is the signalwire package importable?)")

# API-section landing entry.
with open(os.path.join(api_out, "index.md"), "w") as fh:
    fh.write("# API reference\n\n")
    fh.write("Auto-generated reference for each top-level package of the "
             "SignalWire Python SDK.\n\n")
    for n in written:
        fh.write(f"- [signalwire.{n}]({n.replace('_','-')}.md)\n")

# Site landing page. Replaces the SDK README (whose repo-relative links don't
# resolve here): the package list links into the generated API pages, and the
# outbound links point to the guides, source, and package index.
with open(os.path.join(docs_root, "index.md"), "w") as fh:
    fh.write("# SignalWire Python SDK — API Reference\n\n")
    fh.write("Auto-generated technical reference for the SignalWire Python SDK "
             "(`signalwire-sdk`), built from source docstrings.\n\n")
    fh.write("## Packages\n\n")
    for n in written:
        fh.write(f"- [signalwire.{n}](api/{n.replace('_','-')}.md)\n")
    fh.write("\n---\n\n")
    fh.write("- **Guides &amp; tutorials** — "
             "[signalwire.com/docs/server-sdks](https://signalwire.com/docs/server-sdks)\n")
    fh.write("- **Source** — "
             "[github.com/signalwire/signalwire-python](https://github.com/signalwire/signalwire-python)\n")
    fh.write("- **Install** — `pip install signalwire-sdk` "
             "([PyPI](https://pypi.org/project/signalwire-sdk/))\n")
    fh.write("- **License** — "
             "[LICENSE](https://github.com/signalwire/signalwire-python/blob/main/LICENSE)\n")
print("api pages:", ", ".join(written))
PY

if [ "$NO_BUILD" -eq 1 ]; then
  echo "pages generated under $DOCS (skipping mkdocs build)"
  exit 0
fi

# --strict so a local run fails on the same warnings CI fails on.
python3 -m mkdocs build --strict --config-file "$CFG"
echo "python -> $HERE/_site ($(find "$HERE/_site" -name '*.html' | wc -l) pages)"
