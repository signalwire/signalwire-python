#!/usr/bin/env bash
# run-ci.sh — canonical local-and-CI gate runner for signalwire-python.
#
# Same script invoked locally (`bash scripts/run-ci.sh`) AND by the
# GitHub Actions workflow. No drift between local and CI behavior.
#
# Python is the reference SDK. Per-port "drift gate" doesn't apply — python IS the
# spec. Instead we regenerate the python_signatures.json oracle (in porting-sdk/)
# from the live Python source and verify the regenerated file matches what's checked
# in, so a Python-side surface change can't silently invalidate every other port's audit.
#
# GATE SCHEDULING (porting-sdk/scripts/gate_scheduler.sh — CI_PERF S1 + S2):
#   Gates run CONCURRENTLY up to a cap (SW_CI_JOBS, default nproc), scheduled by
#   their DATA dependencies:
#     * S2 concurrent wave: the pure-Python side-effect-free gates (NO-CHEAT,
#       SPEC-PARITY, LINT, TYPECHECK, GEN-FRESH) overlap — they share no mutable state.
#     * S1 fail-fast: heavy gates (TEST, REST-COVERAGE, FMT) are deferred behind the
#       cheap wave, so a trivial cheap-gate failure surfaces in seconds; --fail-fast
#       aborts the run before TEST starts.
#   HARD ordering is data-dependency ONLY:
#     * SIGNATURES regenerates python_signatures.json in porting-sdk; DRIFT git-diffs
#       that file → deps=SIGNATURES (never diff before the regen writes).
#   Per-gate PASS/FAIL + the FAILED_GATES tally preserved exactly; each gate's output
#   captured + replayed atomically.
#
# Flags:
#   --fail-fast   stop launching new gates at the first failure (local dev loop).

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

# shellcheck source=/dev/null
source "$PORTING_SDK_DIR/scripts/gate_scheduler.sh"

pick_free_port() {
    python3 - <<'PY'
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
}

cd "$PORT_ROOT"

# Gate-enforcement plan (Part D): python's red list is burned, so its widened
# (wave-A) gate findings BLOCK rather than report-only. Default OFF here; a
# caller may still set SW_WAVE_A_REPORT_ONLY=1 to inspect the report-only view.
export SW_WAVE_A_REPORT_ONLY="${SW_WAVE_A_REPORT_ONLY:-0}"

echo "==> running CI gates for $PORT_NAME (porting-sdk at $PORTING_SDK_DIR)"
echo "==> wave-A gate findings are ${SW_WAVE_A_REPORT_ONLY:+BLOCKING (SW_WAVE_A_REPORT_ONLY=$SW_WAVE_A_REPORT_ONLY)}"

# Record the resolved web-stack versions up front (CI-only web-layer failures have
# been impossible to diagnose without the runner's actual resolution).
echo "==> environment: $(python3 --version 2>&1)"
python3 -m pip freeze 2>/dev/null \
    | grep -iE '^(fastapi|starlette|pydantic|pydantic-core|anyio|uvicorn|httpx|requests)==' \
    | sed 's/^/    /' || true

# FMT — ruff format. LOCAL applies; CI --check.
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

# REST-COVERAGE — every implemented REST route covered success+error. Self-
# contained: spins its own mock on an ephemeral port, runs the rest/ suite serially,
# then checks the journal.
rest_coverage_gate() {
    local port
    port="$(pick_free_port)" || {
        echo "FATAL: could not acquire a free port for mock_signalwire" >&2
        return 1
    }
    local mock_pkg_parent="$PORTING_SDK_DIR/test_harness/mock_signalwire"
    export PYTHONPATH="$mock_pkg_parent${PYTHONPATH:+:$PYTHONPATH}"
    python3 -m mock_signalwire --host 127.0.0.1 --port "$port" --log-level error \
        >/tmp/rest_cov_mock.$$.log 2>&1 &
    local mock_pid=$!
    # shellcheck disable=SC2064
    trap "kill $mock_pid 2>/dev/null" RETURN
    local i healthy=0
    for i in $(seq 1 30); do
        if ! kill -0 "$mock_pid" 2>/dev/null; then
            echo "FATAL: mock_signalwire (pid $mock_pid) exited before becoming healthy" >&2
            sed 's/^/    mock: /' "/tmp/rest_cov_mock.$$.log" >&2 || true
            return 1
        fi
        if python3 -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:$port/__mock__/health',timeout=1)" 2>/dev/null; then
            healthy=1
            break
        fi
        sleep 0.5
    done
    if [ "$healthy" -ne 1 ]; then
        echo "FATAL: mock_signalwire never became healthy on port $port within ~15s" >&2
        sed 's/^/    mock: /' "/tmp/rest_cov_mock.$$.log" >&2 || true
        return 1
    fi
    python3 -c "import urllib.request; urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:$port/__mock__/journal/reset',method='POST'),timeout=5).read()"
    # Drive every generated wire test (the `*_generated_test.py` suite, `*Wire`
    # classes) against the mock to populate the coverage journal. These replaced the
    # old hand `*_full_mock` tests (bb2c6cf); the previous `-k full_mock` selector
    # matched nothing after that, so the journal stayed empty and coverage failed.
    MOCK_SIGNALWIRE_PORT="$port" python3 -m pytest \
        "$PORT_ROOT/tests/unit/rest/" -k Wire -p no:xdist -q -o addopts="" || return 1
    python3 -m mock_signalwire.rest_coverage \
        --mock-url "http://127.0.0.1:$port" \
        --spec-root "$PORTING_SDK_DIR/rest-apis" \
        --allowlist "$PORTING_SDK_DIR/REST_COVERAGE_BASELINE.md" \
        --allowlist "$PORT_ROOT/REST_COVERAGE_GAPS.md" \
        --gap-baseline "$PORTING_SDK_DIR/REST_COVERAGE_GAP_BASELINE.md"
}

# ---- register gates ----------------------------------------------------------
sched_init "$@"

sched_gate TEST defer=1 desc="python -m pytest tests/unit/" \
    -- python -m pytest tests/unit/

# SIGNATURES regenerates the porting-sdk oracle → DRIFT git-diffs it. deps=SIGNATURES.
sched_gate SIGNATURES desc="regenerate python_signatures.json (reference oracle)" \
    -- python3 "$PORTING_SDK_DIR/scripts/enumerate_python_signatures.py" \
        --signalwire-python "$PORT_ROOT/signalwire" \
        --out "$PORTING_SDK_DIR/python_signatures.json"

sched_gate DRIFT deps=SIGNATURES desc="python_signatures.json unchanged after regen" \
    -- bash -c "cd '$PORTING_SDK_DIR' && git diff --quiet -- python_signatures.json"

sched_gate SEMVER-DIFF deps=SIGNATURES desc="version bump matches surface change vs python_signatures.baseline.json (the reference is not exempt)" \
    -- python3 "$PORTING_SDK_DIR/scripts/semver_diff.py" --port python --repo "$PORT_ROOT"

sched_gate NO-CHEAT desc="audit_no_cheat_tests" \
    -- python3 "$PORTING_SDK_DIR/scripts/audit_no_cheat_tests.py" --root "$PORT_ROOT"

sched_gate REST-COVERAGE defer=1 desc="every implemented REST route covered success+error (parity + allowlist)" \
    --fn rest_coverage_gate

sched_gate SPEC-PARITY defer=1 desc="implemented routes == canonical spec (modulo SPEC_IMPLEMENTATION_GAPS.md)" \
    -- python3 "$PORTING_SDK_DIR/scripts/diff_spec_implementation.py" \
        --sdk "$PORT_ROOT/signalwire/signalwire" \
        --gaps "$PORTING_SDK_DIR/SPEC_IMPLEMENTATION_GAPS.md"

sched_gate FMT defer=1 desc="ruff format (local: apply; CI: --check)" \
    --fn fmt_gate

sched_gate LINT desc="ruff check zero findings" \
    -- python3 -m ruff check "$PORT_ROOT/signalwire"

sched_gate TYPECHECK desc="mypy zero findings" \
    -- python3 -m mypy --config-file "$PORT_ROOT/pyproject.toml"

sched_gate GEN-FRESH desc="generated REST/RELAY types reproduce from specs" \
    -- python3 "$PORTING_SDK_DIR/scripts/generate_python_rest_types.py" \
        --signalwire-python "$PORT_ROOT/signalwire" --check

# ---- expansion gates (GATE_EXPANSION_PLAN) — enforcing ----------------------
# python is the reference: GEN-TYPE-DEGENERACY + GEN-IDIOM self-skip clean;
# PUBLIC-JARGON + RELEASE-FRESH enforce; ROUTE-COLLISION enforces (modulo the
# user-approved ROUTE_COLLISION_ALLOW.md list_addresses singular-path entries).
sched_gate GEN-TYPE-DEGENERACY desc="no degenerate/over-broad generated param types" \
    -- python3 "$PORTING_SDK_DIR/scripts/gen_type_degeneracy.py" --port python --repo "$PORT_ROOT"

sched_gate PUBLIC-JARGON desc="no internal jargon in public identifiers/docstrings" \
    -- python3 "$PORTING_SDK_DIR/scripts/public_jargon.py" --port python --repo "$PORT_ROOT"

sched_gate ROUTE-COLLISION desc="no split routes / duplicate CRUD bases (modulo allowlist)" \
    -- python3 "$PORTING_SDK_DIR/scripts/route_collision.py" --port python --repo "$PORT_ROOT"

sched_gate GEN-IDIOM desc="generated surface follows the port's idiom" \
    -- python3 "$PORTING_SDK_DIR/scripts/gen_idiom.py" --port python --repo "$PORT_ROOT"

sched_gate RELEASE-FRESH desc="publish path runs the gates before releasing" \
    -- python3 "$PORTING_SDK_DIR/scripts/release_fresh.py" --port python --repo "$PORT_ROOT"

sched_gate README-INCLUDE desc="doc code blocks are byte-identical to their gate-compiled fixture regions" \
    -- python3 "$PORTING_SDK_DIR/scripts/readme_include.py" --port python --repo .

# ---- §C1 doc/example execution gates -----------------------------------------
# SNIPPET-COMPILE (~18s, compile-only) + DOC-CLI (parallelized probe pool, ~25s)
# are cheap → cheap wave, blocking. SNIPPET-RUN + EXAMPLES-RUN execute code
# (mock-backed) and are minutes-long even when green → defer=1 heavy wave.
sched_gate SNIPPET-COMPILE tier=nightly desc="documented code snippets compile" \
    -- python3 "$PORTING_SDK_DIR/scripts/snippet_compile.py" --port python --repo "$PORT_ROOT"

sched_gate DOC-CLI desc="documented swaig-test invocations parse against the real CLI" \
    -- python3 "$PORTING_SDK_DIR/scripts/doc_cli.py" --port python --repo "$PORT_ROOT"

# Wave-3 doc/API-truth gates — deterministic source/doc analysis (no build, no
# mock, ~1.3s for all six). Per-PR tier: cheap enough to catch doc/API drift at
# PR time rather than a day later in nightly.
sched_gate ERROR-ENVELOPE desc="REST error carries the full (status,body,url,method) envelope + raised on >=400" \
    -- python3 "$PORTING_SDK_DIR/scripts/error_envelope.py" --port python --repo "$PORT_ROOT"
sched_gate DEAD-PUBLIC-ERROR desc="exported error types are raised/caught/user-signalled (no dead error surface)" \
    -- python3 "$PORTING_SDK_DIR/scripts/dead_public_error.py" --port python --repo "$PORT_ROOT"
sched_gate PAGINATION-WIRED desc="shipped iterator-protocol paginator is wired into list()" \
    -- python3 "$PORTING_SDK_DIR/scripts/pagination_wired.py" --port python --repo "$PORT_ROOT"
sched_gate DOC-ENV desc="documented SIGNALWIRE_*/SWML_* env vars <=> code-read vars agree" \
    -- python3 "$PORTING_SDK_DIR/scripts/doc_env.py" --port python --repo "$PORT_ROOT"
sched_gate COUNT-CLAIM desc="numeric doc claims (skills/namespaces) match reality" \
    -- python3 "$PORTING_SDK_DIR/scripts/count_claim.py" --port python --repo "$PORT_ROOT"
sched_gate ACCESSOR-TRUTH desc="documented backtick method() refs exist in source" \
    -- python3 "$PORTING_SDK_DIR/scripts/accessor_truth.py" --port python --repo "$PORT_ROOT"

# DOC-AUDIT — every method/class referenced in docs/examples resolves to a real
# symbol in the python surface oracle (python_surface.json, in porting-sdk). The
# DOC_AUDIT_IGNORE.md ledger excuses stdlib/third-party/user-tutorial-helper refs.
sched_gate DOC-AUDIT desc="audit_docs vs python_surface.json (the reference oracle)" \
    -- python3 "$PORTING_SDK_DIR/scripts/audit_docs.py" \
        --root "$PORT_ROOT" \
        --surface "$PORTING_SDK_DIR/python_surface.json" \
        --ignore "$PORT_ROOT/DOC_AUDIT_IGNORE.md"

# DOC-WIRE (§A1) — the documented REST fixtures are wire-clean against the spec
# (strict-flag mock journals wire_violations; runner replays the doc calls). Cheap.
sched_gate DOC-WIRE desc="documented REST doc fixtures put the spec wire shape on the wire (areacode/params:{text})" \
    -- python3 "$PORTING_SDK_DIR/scripts/doc_wire.py" --port python --repo "$PORT_ROOT" \
        --runner "python3 $PORT_ROOT/scripts/doc_wire_runner.py"

# STATUS-CLAIM (§C2) — no false capability/status claims in docs (e.g. "not
# implemented" / "transport pending" for surface that exists).
sched_gate STATUS-CLAIM desc="doc status/capability claims match the shipped surface" \
    -- python3 "$PORTING_SDK_DIR/scripts/status_claim.py" --port python --repo "$PORT_ROOT" \
        --surface "$PORTING_SDK_DIR/python_surface.json"

# GATE-INVENTORY (§1.11b) — porting-sdk's generated GATE_INVENTORY.md stays fresh
# vs the reference run-ci; any repo that adds a gate fails until the inventory regens.
sched_gate GATE-INVENTORY desc="porting-sdk GATE_INVENTORY.md is fresh (gen_gate_inventory --check)" \
    -- python3 "$PORTING_SDK_DIR/scripts/gen_gate_inventory.py" --check

# SNIPPET-RUN is BLOCKING: the fragment backlog is burned to zero. Residual
# non-runnable snippets carry `<!-- snippet: no-run <reason> -->` markers (blocking
# servers, live REST/network calls, optional-dep imports, prose-context fragments,
# before/after excerpts); real API-mismatch doc bugs were fixed. ~130s parallelized.
sched_gate SNIPPET-RUN tier=nightly defer=1 desc="dynamic-port doc snippets run to a zero exit against the mock (STRICT-MOCKS: MOCK_RELAY_STRICT=1)" \
    -- env MOCK_RELAY_STRICT=1 python3 "$PORTING_SDK_DIR/scripts/snippet_run.py" --port python --repo "$PORT_ROOT"

sched_gate EXAMPLES-RUN tier=nightly defer=1 desc="shipped examples load/start against the mock (modulo EXAMPLES_RUN_ALLOW.md; STRICT-MOCKS: MOCK_RELAY_STRICT=1)" \
    -- env MOCK_RELAY_STRICT=1 python3 "$PORTING_SDK_DIR/scripts/examples_run.py" --port python --repo "$PORT_ROOT"

# WAIT-LIVENESS (§2.4) — the wait_liveness corpus runs against the python
# reference and produces the golden LIVENESS classification (play/record wait()
# blocks until the completing event, then returns — never busy-hangs or early-
# returns). For python (the oracle) proving the corpus runs IS the gate; the
# ports diff their classification against this golden. Nightly (spawns dump
# programs). Report-only is NOT used — python is the oracle floor.
sched_gate WAIT-LIVENESS tier=nightly defer=1 desc="wait() liveness corpus runs on the reference + yields the golden classification" \
    -- python3 "$PORTING_SDK_DIR/scripts/diff_port_wait_liveness.py" --show-oracle --python-sdk "$PORT_ROOT"

# ---- Day-one deterministic doc/tree-hygiene gates ---------------------------
sched_gate DOC-LINKS desc="every relative markdown link resolves to a tracked file" \
    -- python3 "$PORTING_SDK_DIR/scripts/doc_links.py" --port python --repo "$PORT_ROOT"

sched_gate ROOT-HYGIENE desc="no audit/scratch clutter tracked at repo root (allowlist ROOT_HYGIENE_ALLOW.md)" \
    -- python3 "$PORTING_SDK_DIR/scripts/root_hygiene.py" --port python --repo "$PORT_ROOT"

sched_run
rc=$?
if [ "$rc" -eq 0 ]; then
    echo "==> CI PASS"
else
    echo "==> CI FAIL (gates:$FAILED_GATES )"
fi
exit "$rc"
