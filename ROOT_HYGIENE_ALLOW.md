# ROOT_HYGIENE_ALLOW.md

Repo-root files excused from the `root_hygiene` gate. Each is a LOAD-BEARING
gate-config / allowlist file that porting-sdk audit scripts (and this port's own
`scripts/run-ci.sh`) read at the repo root by relative path. Moving them under
`eng/` would break the shared audit pipeline, which this port cannot edit.

Format: `- <path> — <reason> (<approver>, <date>)`. Paths match the reported
offender verbatim.

## Gate allowlist / config files (each read by its gate at repo root)

- ROOT_HYGIENE_ALLOW.md — this allowlist itself; the root_hygiene gate reads it at repo root (mike@signalwire.com, 2026-07-15)
- DOC_AUDIT_IGNORE.md — required audit-contract file read by porting-sdk audit_docs.py (DOC-AUDIT) at repo root (mike@signalwire.com, 2026-07-15)
- ACCESSOR_TRUTH_ALLOW.md — allowlist read by porting-sdk accessor_truth.py (ACCESSOR-TRUTH) at repo root (mike@signalwire.com, 2026-07-15)
- DOC_CLI_ALLOW.md — allowlist read by porting-sdk doc_cli.py (DOC-CLI) at repo root (mike@signalwire.com, 2026-07-15)
- EXAMPLES_RUN_ALLOW.md — allowlist read by porting-sdk examples_run.py (EXAMPLES-RUN) at repo root (mike@signalwire.com, 2026-07-15)
- REST_COVERAGE_GAPS.md — required audit-contract file read by porting-sdk rest_coverage (REST-COVERAGE) at repo root (mike@signalwire.com, 2026-07-15)
- ROUTE_COLLISION_ALLOW.md — allowlist read by porting-sdk route_collision.py (ROUTE-COLLISION) at repo root (mike@signalwire.com, 2026-07-15)
- SNIPPET_RUN_ALLOW.md — allowlist read by porting-sdk snippet_run.py (SNIPPET-RUN) at repo root (mike@signalwire.com, 2026-07-15)
