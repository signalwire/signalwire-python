#!/usr/bin/env bash
# coordinated-ref.sh — resolve the coordinated-pass refs from BRANCH-LOCAL pin files.
#
# CANONICAL COPY: porting-sdk/.github/coordinated-ref.sh. Every repo that checks out a
# coordinated-set repo in CI carries a byte-identical copy at .github/coordinated-ref.sh;
# the COORDINATED-REFS gate (porting-sdk/scripts/check_coordinated_refs.py) enforces the
# identity. Edit it HERE, then copy it to every repo.
#
# Why a file on the branch and not a repo variable: a repo/org variable is read by EVERY
# branch's CI — main and everyone else's PRs included — so pinning a coordinated pass that
# way silently points the whole repo at an in-progress branch. A pin file is committed
# only on the coordinated branch, so only that branch's CI sees it. (Owner, 2026-09-29.)
#
# Usage: a workflow step with `id: coord`, placed AFTER the repo's own checkout:
#     - name: Resolve coordinated refs (branch-local .github/porting-sdk-ref pin; no pin = main)
#       id: coord
#       shell: bash
#       run: bash <self-path>/.github/coordinated-ref.sh <self-path>
# then every foreign coordinated-set checkout uses
#     ref: ${{ steps.coord.outputs.ref }}          # signalwire/porting-sdk
#     ref: ${{ steps.coord.outputs.ref_python }}   # signalwire/signalwire-python
#     ref: ${{ steps.coord.outputs.ref_<port> }}   # signalwire/signalwire-<port>
#
# Pin files (under .github/, so the repo root stays clean; committed ONLY on a coordinated
# branch and DELETED in the PR that merges the coordinated set — see
# porting-sdk/COORDINATED_PASS.md):
#   .github/porting-sdk-ref         one line: the coordinated ref. porting-sdk's branch, and
#                                   the default for every other coordinated repo.
#   .github/signalwire-<name>-ref   optional per-repo override, for a pass where that repo's
#                                   branch is named differently
#                                   (e.g. .github/signalwire-typescript-ref).
# No pin file -> main. A pin at the retired repo-root location (.porting-sdk-ref,
# .signalwire-<name>-ref) fails the job rather than being silently ignored.
#
# Content is validated (one branch name; characters A-Z a-z 0-9 . _ / - only); anything
# else fails the job instead of reaching a `ref:` or $GITHUB_OUTPUT.
#
# Outputs ($GITHUB_OUTPUT; stdout when run outside Actions):
#   ref          porting-sdk ref
#   ref_<name>   signalwire-<name> ref, for every <name> in NAMES
set -euo pipefail

root="${1:-.}"
NAMES="python typescript go java dotnet ruby php perl rust cpp"
out="${GITHUB_OUTPUT:-/dev/stdout}"

# $1 = pin file, $2 = default. Sets PIN. Invalid content exits 1.
read_pin() {
  PIN="$2"
  [ -f "$1" ] || return 0
  PIN=$(tr -d ' \t\r' < "$1")
  if [[ ! "$PIN" =~ ^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$ || "$PIN" == *..* || "$PIN" == */ || "$PIN" == *.lock ]]; then
    echo "::error::.github/${1##*/} must hold exactly one git branch name (characters A-Z a-z 0-9 . _ / - only)"
    exit 1
  fi
}

for legacy in "$root/.porting-sdk-ref" "$root"/.signalwire-*-ref; do
  if [ -f "$legacy" ]; then
    echo "::error::${legacy##*/} at the repo root is the retired pin location; move it to .github/${legacy##*/.}"
    exit 1
  fi
done

read_pin "$root/.github/porting-sdk-ref" main
ref="$PIN"
echo "ref=$ref" >> "$out"
summary="porting-sdk=$ref"
for n in $NAMES; do
  read_pin "$root/.github/signalwire-$n-ref" "$ref"
  echo "ref_$n=$PIN" >> "$out"
  summary="$summary signalwire-$n=$PIN"
done
echo "coordinated refs: $summary" >&2
