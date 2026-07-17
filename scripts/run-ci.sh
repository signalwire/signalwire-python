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

# ---- register gates ----------------------------------------------------------
sched_init "$@"

sched_gate TEST defer=1 desc="python -m pytest tests/unit/" \
    -- python -m pytest tests/unit/

# ---- Part 5 gate SUITES ------------------------------------------------------
# The former per-gate SIGNATURES/DRIFT/SEMVER-DIFF/GEN-TYPE-DEGENERACY/ROUTE-
# COLLISION/GEN-IDIOM/GEN-FRESH/ERROR-ENVELOPE/PAGINATION-WIRED/DOC-WIRE/
# REST-COVERAGE/SPEC-PARITY/WAIT-LIVENESS/RELEASE-FRESH gates now run under the
# shared Part-5 SUITE engines. Each suite emits every original gate NAME as a
# `[SUITE:RULE] ... PASS/FAIL` rule ID (failure identity + allowlists + finding
# output unchanged); a suite exits nonzero iff any of its rules fails. Byte-
# identity vs the old per-gate path is proven by porting-sdk tests/test_suite_
# parity*.py.
#
# PYTHON IS THE ORACLE, so it schedules FAR FEWER suite members than the ports:
# it wires NONE of the diff-vs-oracle rules (SURFACE-FRESH/SURFACE-DIFF/
# BEHAVIORAL-*/EMISSION/SKILL-CONTRACT/SWAIG-*/DOC-LANG-PURITY) — there is no
# oracle for python to diff AGAINST. Each suite's build_rules() already returns
# python's smaller (oracle) rule set, so a python suite line runs exactly its
# scheduled members. Two suites are DELIBERATELY NOT wired for python:
#   * DOC-TRUTH — its rule table always emits DOC-LANG-PURITY ("no python-
#     verbatim docs in a NON-python port"), which python has never scheduled and
#     which self-skips as a no-op; with no --rules filter on that suite, wiring it
#     would inject a gate python's baseline lacks. So DOC-AUDIT/DOC-LINKS/DOC-ENV/
#     COUNT-CLAIM/ACCESSOR-TRUTH/STATUS-CLAIM/README-INCLUDE stay STANDALONE below.
#   * LEDGER — emits only SUPPRESSION-LEDGER/IGNORE-LEDGER-VERIFY, neither of which
#     python schedules; wiring it would invent two gates. Not wired.
#
# The former single-gate scheduler features are preserved INSIDE the suites:
#   * SIGNATURES→DRIFT→SEMVER-DIFF ordering (python's SIGNATURES regenerates the
#     porting-sdk oracle python_signatures.json; DRIFT git-diffs it; SEMVER-DIFF
#     reads the regenerated file) lives in the SURFACE suite, which regenerates,
#     consumes in order, then git-restores the oracle — leaving both trees clean.
#   * BEHAVIORAL's mixed tiers are split with --rules: a per-PR line (5 rules) and
#     a nightly line (WAIT-LIVENESS).

# SURFACE (parity spine): SIGNATURES→DRIFT→SEMVER-DIFF ordered + GEN-TYPE-
# DEGENERACY/ROUTE-COLLISION/GEN-IDIOM. python is the oracle so there is no
# SURFACE-FRESH/SURFACE-DIFF. The suite regenerates the oracle in porting-sdk and
# restores it after DRIFT/SEMVER consume it. Cheap wave (parity spine).
sched_gate SURFACE desc="surface parity suite (SIGNATURES/DRIFT/SEMVER-DIFF/GEN-TYPE-DEGENERACY/ROUTE-COLLISION/GEN-IDIOM)" \
    -- python3 "$PORTING_SDK_DIR/scripts/suites/surface.py" --port python --repo "$PORT_ROOT"

# GEN (regen-from-specs family): python schedules only GEN-FRESH.
sched_gate GEN desc="generated-code freshness suite (GEN-FRESH)" \
    -- python3 "$PORTING_SDK_DIR/scripts/suites/gen.py" --port python --repo "$PORT_ROOT"

# BEHAVIORAL, per-PR rules: python's oracle set is ERROR-ENVELOPE/PAGINATION-
# WIRED/DOC-WIRE/REST-COVERAGE/SPEC-PARITY (no BEHAVIORAL-*/EMISSION/SKILL-
# CONTRACT/SWAIG-* — those diff a port against python). REST-COVERAGE/SPEC-PARITY
# are heavy (spin the mock) → defer=1. WAIT-LIVENESS is the nightly line below.
sched_gate BEHAVIORAL defer=1 desc="behavioral suite, per-PR rules (ERROR-ENVELOPE/PAGINATION-WIRED/DOC-WIRE/REST-COVERAGE/SPEC-PARITY)" \
    -- python3 "$PORTING_SDK_DIR/scripts/suites/behavioral.py" --port python --repo "$PORT_ROOT" \
        --rules ERROR-ENVELOPE,PAGINATION-WIRED,DOC-WIRE,REST-COVERAGE,SPEC-PARITY

sched_gate BEHAVIORAL-NIGHTLY tier=nightly defer=1 desc="behavioral suite, nightly rules (WAIT-LIVENESS)" \
    -- python3 "$PORTING_SDK_DIR/scripts/suites/behavioral.py" --port python --repo "$PORT_ROOT" \
        --rules WAIT-LIVENESS

# PACKAGE: python schedules only RELEASE-FRESH (no ARTIFACT-DENY/PACKAGE-SMOKE/
# META-CONSISTENT).
sched_gate PACKAGE desc="package suite, per-PR rules (RELEASE-FRESH)" \
    -- python3 "$PORTING_SDK_DIR/scripts/suites/package.py" --port python --repo "$PORT_ROOT" \
        --rules RELEASE-FRESH

# ---- gates that stay standalone ----------------------------------------------
sched_gate NO-CHEAT desc="audit_no_cheat_tests" \
    -- python3 "$PORTING_SDK_DIR/scripts/audit_no_cheat_tests.py" --root "$PORT_ROOT"

sched_gate FMT defer=1 desc="ruff format (local: apply; CI: --check)" \
    --fn fmt_gate

sched_gate LINT desc="ruff check zero findings" \
    -- python3 -m ruff check "$PORT_ROOT/signalwire"

sched_gate TYPECHECK desc="mypy zero findings" \
    -- python3 -m mypy --config-file "$PORT_ROOT/pyproject.toml"

# GEN-FRESH runs under the GEN suite (above).

# ---- expansion gates (GATE_EXPANSION_PLAN) — enforcing ----------------------
# GEN-TYPE-DEGENERACY / ROUTE-COLLISION / GEN-IDIOM now run under the SURFACE
# suite; RELEASE-FRESH under the PACKAGE suite. PUBLIC-JARGON stays standalone
# (public-API source analysis, not a suite family). README-INCLUDE stays
# standalone: it is a DOC-TRUTH member, but DOC-TRUTH is not wired for python (it
# would inject DOC-LANG-PURITY — see the SUITES note above).
sched_gate PUBLIC-JARGON desc="no internal jargon in public identifiers/docstrings" \
    -- python3 "$PORTING_SDK_DIR/scripts/public_jargon.py" --port python --repo "$PORT_ROOT"

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
# ERROR-ENVELOPE + PAGINATION-WIRED run under the BEHAVIORAL suite (above).
# DEAD-PUBLIC-ERROR stays standalone (source analysis of exported error types).
sched_gate DEAD-PUBLIC-ERROR desc="exported error types are raised/caught/user-signalled (no dead error surface)" \
    -- python3 "$PORTING_SDK_DIR/scripts/dead_public_error.py" --port python --repo "$PORT_ROOT"
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

# DOC-WIRE (§A1) runs under the BEHAVIORAL suite (above).

# STATUS-CLAIM (§C2) — no false capability/status claims in docs (e.g. "not
# implemented" / "transport pending" for surface that exists).
sched_gate STATUS-CLAIM desc="doc status/capability claims match the shipped surface" \
    -- python3 "$PORTING_SDK_DIR/scripts/status_claim.py" --port python --repo "$PORT_ROOT" \
        --surface "$PORTING_SDK_DIR/python_surface.json"

# NOTE: §1.11b (GATE-INVENTORY freshness) is NOT wired here. gen_gate_inventory.py
# resolves its reference port as a sibling checkout (DEFAULT_REFERENCE=signalwire-
# typescript), which does not exist in a port's CI layout (porting-sdk is a subdir
# of the port workspace, so ../signalwire-typescript is absent → exit 2). The check
# is inherently porting-sdk-side and already runs in porting-sdk's own CI
# (.github/workflows/test.yml, with --reference ./signalwire-typescript). Wiring it
# per-port would require each port to also check out the TS reference — not worth it.

# SNIPPET-RUN is BLOCKING: the fragment backlog is burned to zero. Residual
# non-runnable snippets carry `<!-- snippet: no-run <reason> -->` markers (blocking
# servers, live REST/network calls, optional-dep imports, prose-context fragments,
# before/after excerpts); real API-mismatch doc bugs were fixed. ~130s parallelized.
sched_gate SNIPPET-RUN tier=nightly defer=1 desc="dynamic-port doc snippets run to a zero exit against the mock (STRICT-MOCKS: MOCK_RELAY_STRICT=1)" \
    -- env MOCK_RELAY_STRICT=1 python3 "$PORTING_SDK_DIR/scripts/snippet_run.py" --port python --repo "$PORT_ROOT"

sched_gate EXAMPLES-RUN tier=nightly defer=1 desc="shipped examples load/start against the mock (modulo EXAMPLES_RUN_ALLOW.md; STRICT-MOCKS: MOCK_RELAY_STRICT=1)" \
    -- env MOCK_RELAY_STRICT=1 python3 "$PORTING_SDK_DIR/scripts/examples_run.py" --port python --repo "$PORT_ROOT"

# WAIT-LIVENESS (§2.4) runs under the BEHAVIORAL-NIGHTLY suite line (above).

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
