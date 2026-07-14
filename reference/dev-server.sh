#!/usr/bin/env bash
# Local dev server for the SDK API reference (live-reload, bound to 0.0.0.0 so a
# forwarded port reaches it). Serves at http://<host>:<port>/signalwire-python/.
#
# Prereqs: activate the venv where the doc toolchain is installed, e.g.
#   python3 -m venv .venv && source .venv/bin/activate          # bash/zsh
#   python3 -m venv .venv && source .venv/bin/activate.fish     # fish
#   reference/gen.sh                                            # first run installs deps
#
# Usage:  reference/dev-server.sh [PORT]        # PORT defaults to 3001
#
# Note: mkdocs serve hot-reloads the generated pages and overrides/, but NOT the
# navbar assets (gen.sh copies assets/ into _docs at startup). After editing
# assets/css/*.css or assets/js/*.js, restart this script to pick them up.
set -euo pipefail

PORT="${1:-3001}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .../reference

# Generate the API pages + landing page (skip the HTML build — mkdocs serve builds).
bash "$HERE/gen.sh" --no-build

# Serve with live-reload on all interfaces.
exec python3 -m mkdocs serve --config-file "$HERE/mkdocs.yml" --dev-addr "0.0.0.0:${PORT}"
