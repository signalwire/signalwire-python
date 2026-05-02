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
    sed 's/^/    /' "$logfile" | tail -40
    rm -f "$logfile"
    FAILED_GATES="$FAILED_GATES $name"
    return $rc
}

cd "$PORT_ROOT"

echo "==> running CI gates for $PORT_NAME (porting-sdk at $PORTING_SDK_DIR)"

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

if [ -z "$FAILED_GATES" ]; then
    echo "==> CI PASS"
    exit 0
else
    echo "==> CI FAIL (gates:$FAILED_GATES )"
    exit 1
fi
