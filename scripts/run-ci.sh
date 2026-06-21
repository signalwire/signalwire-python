#!/usr/bin/env bash
# run-ci.sh — canonical local-and-CI gate runner for signalwire-python.
#
# Same script invoked locally (`bash scripts/run-ci.sh`) AND by the
# GitHub Actions workflow. No drift between local and CI behavior.
#
# Python is the reference SDK. Per-port "drift gate" doesn't apply —
# python IS the spec. Instead we regenerate the python_signatures.json
# oracle (in porting-sdk/) from the live Python source and verify the
# regenerated file matches what's checked in. That way a Python-side
# surface change can't silently invalidate every other port's audit.
#
# Gates (in order, fail-fast):
#   1. python -m pytest tests/unit/       — language test runner
#   2. signature regen                    — porting-sdk's enumerate_python_signatures.py
#   3. drift gate                         — git-diff python_signatures.json (must be unchanged)
#   4. no-cheat gate                      — porting-sdk audit_no_cheat_tests.py
#   4b. rest-coverage gate                — porting-sdk rest_coverage.py over a REST-suite
#                                           journal: every implemented route hit success+error
#                                           (parity), accepted gaps allowlisted
#   5. fmt gate                           — ruff format (local: apply; CI: --check)
#   6. lint gate                          — ruff check, zero findings
#   7. typecheck gate                     — mypy, zero findings

set -u
set -o pipefail

PORT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT_NAME="signalwire-python"

resolve_porting_sdk() {
    if [ -n "${PORTING_SDK:-}" ] && [ -d "$PORTING_SDK/scripts" ]; then
        echo "$PORTING_SDK"
        return 0
    fi
    if [ -d "$PORT_ROOT/../porting-sdk/scripts" ]; then
        (cd "$PORT_ROOT/../porting-sdk" && pwd)
        return 0
    fi
    return 1
}

PORTING_SDK_DIR="$(resolve_porting_sdk)" || {
    echo "FATAL: porting-sdk not found, clone it adjacent to this repo" >&2
    echo "       (expected $PORT_ROOT/../porting-sdk or \$PORTING_SDK env var)" >&2
    exit 2
}

FAILED_GATES=""

run_gate() {
    local name="$1"; shift
    local description="$1"; shift
    local logfile
    logfile="$(mktemp)"
    "$@" >"$logfile" 2>&1
    local rc=$?
    if [ "$rc" -eq 0 ]; then
        echo "[$name] $description ... PASS"
        rm -f "$logfile"
        return 0
    fi
    echo "[$name] $description ... FAIL: exit $rc"
    # On failure show the LAST 400 lines (was 40) so pytest's per-test
    # tracebacks — which print before the short-summary — actually reach the CI
    # log. A blind `tail -40` on a multi-thousand-test run captured only the
    # FAILED summary lines and discarded every traceback, making CI-only
    # failures undiagnosable. 400 lines covers a realistic handful of failing
    # tests; a fully green run prints nothing here regardless.
    sed 's/^/    /' "$logfile" | tail -400
    rm -f "$logfile"
    FAILED_GATES="$FAILED_GATES $name"
    return $rc
}

cd "$PORT_ROOT"

echo "==> running CI gates for $PORT_NAME (porting-sdk at $PORTING_SDK_DIR)"

# Record the resolved web-stack versions up front. CI-only test failures in the
# web layer have been impossible to diagnose because the runner's fresh
# dependency resolution differs from local envs; logging it makes that visible.
echo "==> environment: $(python3 --version 2>&1)"
python3 -m pip freeze 2>/dev/null \
    | grep -iE '^(fastapi|starlette|pydantic|pydantic-core|anyio|uvicorn|httpx|requests)==' \
    | sed 's/^/    /' || true

# Gate 1: pytest unit suite
run_gate "TEST" "python -m pytest tests/unit/" \
    python -m pytest tests/unit/

# Gate 2: regenerate the python reference oracle into porting-sdk
run_gate "SIGNATURES" "regenerate python_signatures.json (reference oracle)" \
    python3 "$PORTING_SDK_DIR/scripts/enumerate_python_signatures.py" \
        --signalwire-python "$PORT_ROOT/signalwire" \
        --out "$PORTING_SDK_DIR/python_signatures.json"

# Gate 3: oracle-drift gate — the regenerated file must match what's
# committed in porting-sdk. Drift here means a Python-side surface
# change wasn't propagated to the audit oracle, which would silently
# invalidate every port's drift report.
run_gate "DRIFT" "python_signatures.json unchanged after regen" \
    bash -c "cd '$PORTING_SDK_DIR' && git diff --quiet -- python_signatures.json"

# Gate 4: no-cheat
run_gate "NO-CHEAT" "audit_no_cheat_tests" \
    python3 "$PORTING_SDK_DIR/scripts/audit_no_cheat_tests.py" --root "$PORT_ROOT"

# Gate 4b: REST-COVERAGE — every canonical REST route the SDK implements must be
# exercised with BOTH a success (2xx) AND an error (4xx/5xx) response, on the
# correct on-the-wire path (parity). Measured by replaying the mock journal of a
# REST-suite run through porting-sdk's rest_coverage checker. Accepted gaps —
# routes with no SDK method, malformed canonical routes, mock-router collisions —
# are allowlisted: the shared baseline (porting-sdk/REST_COVERAGE_BASELINE.md) for
# universal gaps + this port's REST_COVERAGE_GAPS.md for its own sdk-gaps. A
# stale allowlist entry (a route now actually covered) fails the gate.
#
# Self-contained: spins up its own mock on an ephemeral port, runs the rest/ suite
# serially against it (MOCK_SIGNALWIRE_PORT so all traffic lands in one journal),
# then checks that journal. Same shape on every port.
rest_coverage_gate() {
    local port=8951
    python3 -m mock_signalwire.cli --port "$port" >/tmp/rest_cov_mock.$$.log 2>&1 &
    local mock_pid=$!
    # shellcheck disable=SC2064
    trap "kill $mock_pid 2>/dev/null" RETURN
    # wait for the control plane to answer
    local i
    for i in $(seq 1 30); do
        if python3 -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:$port/__mock__/health',timeout=1)" 2>/dev/null; then
            break
        fi
        sleep 0.5
    done
    python3 -c "import urllib.request; urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:$port/__mock__/journal/reset',method='POST'),timeout=5).read()"
    MOCK_SIGNALWIRE_PORT="$port" python3 -m pytest "$PORT_ROOT/tests/unit/rest/" -k full_mock -p no:xdist -q -o addopts="" || return 1
    python3 -m mock_signalwire.rest_coverage \
        --mock-url "http://127.0.0.1:$port" \
        --spec-root "$PORTING_SDK_DIR/rest-apis" \
        --allowlist "$PORTING_SDK_DIR/REST_COVERAGE_BASELINE.md" \
        --allowlist "$PORT_ROOT/REST_COVERAGE_GAPS.md"
}
run_gate "REST-COVERAGE" "every implemented REST route covered success+error (parity + allowlist)" \
    rest_coverage_gate

# Gate 5: FMT — ruff format. Config in pyproject.toml [tool.ruff]. Source-style
# only (no public-API change → the SIGNATURES/DRIFT oracle is unaffected).
#   * LOCAL ($CI unset)  → `ruff format` reformats the tree in place.
#   * CI ($CI=true)      → `ruff format --check` (read-only): fails on unformatted.
fmt_gate() {
    if [ -n "${CI:-}" ]; then
        python3 -m ruff format --check "$PORT_ROOT/signalwire"
    else
        python3 -m ruff format "$PORT_ROOT/signalwire" >/dev/null
        if ! (cd "$PORT_ROOT" && git diff --quiet 2>/dev/null); then
            echo "    (FMT auto-applied formatting to your working tree — review & stage)"
        fi
        python3 -m ruff format --check "$PORT_ROOT/signalwire"
    fi
}
run_gate "FMT" "ruff format (local: apply; CI: --check)" fmt_gate

# Gate 6: LINT — ruff check, zero findings. Burned to zero (the DISABLE list is
# none; the few intentional lazy-import / re-export sites carry per-line # noqa
# with a rationale). Mirrors the go golangci / ruby rubocop blocking-lint gate.
run_gate "LINT" "ruff check zero findings" \
    python3 -m ruff check "$PORT_ROOT/signalwire"

# Gate 7: TYPECHECK — mypy, zero findings. Config in pyproject.toml [tool.mypy]
# (files=signalwire/signalwire, ignore_missing_imports, check_untyped_defs). Burned
# to zero across all 176 source files. `# type: ignore` is reserved for genuine
# third-party-stub gaps / optional-dependency import shims, each with an error code
# and rationale (warn_unused_ignores keeps them honest). Source-type only — mypy is
# dev-time and adds no runtime validation, so wire payloads stay forward-compatible.
run_gate "TYPECHECK" "mypy zero findings" \
    python3 -m mypy --config-file "$PORT_ROOT/pyproject.toml"

if [ -z "$FAILED_GATES" ]; then
    echo "==> CI PASS"
    exit 0
else
    echo "==> CI FAIL (gates:$FAILED_GATES )"
    exit 1
fi
