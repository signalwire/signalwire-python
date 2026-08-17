# SNIPPET_RUN_ALLOW.md

Snippets that cannot run to a zero exit under the mock and cannot carry a
`<!-- snippet: no-run … -->` marker (a README include-site must have its
`<!-- include: … -->` comment immediately above the fence, leaving no room for a
second marker line). Each entry is `- <path>:<line> — <reason> (approver, date)`.

The remaining entry is the README quickstart_rest include (synced from
`examples/quickstart_rest.py`, whose hardcoded placeholder creds + real host make it a
display quickstart, not a runnable program). The agent/relay quickstart entries
(README.md:44/:116) were RETIRED 2026-07-19: snippet_run's structural blocking-server
auto-classify covers a server-starting quickstart (verified — the gate is clean without
them), so those lines were redundant (double-allowlist purge, plan 3-python-f).

- README.md:152 — quickstart_rest include: hardcoded placeholder creds + real host — a display quickstart, not runnable against the mock (burn-py, 2026-07-09; reason updated 2026-07-19; anchor refreshed 2026-07-23 after the quickstart_agent/relay blocks above gained ruff-format blank lines)
