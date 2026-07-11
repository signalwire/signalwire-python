# SNIPPET_RUN_ALLOW.md

Snippets that cannot run to a zero exit under the mock and cannot carry a
`<!-- snippet: no-run … -->` marker (a README include-site must have its
`<!-- include: … -->` comment immediately above the fence, leaving no room for a
second marker line). Each entry is `- <path>:<line> — <reason> (approver, date)`.

These three README blocks are include-synced from `examples/quickstart_*.py` and are
exercised by the EXAMPLES-RUN gate; the agent/relay quickstarts start a blocking
server/WebSocket client and the REST quickstart makes a live authenticated REST call,
none of which run standalone to a zero exit against the mock.

- README.md:44 — quickstart_agent include: starts a blocking agent server (covered by EXAMPLES-RUN) (burn-py, 2026-07-09)
- README.md:116 — quickstart_relay include: opens a blocking RELAY WebSocket connection (covered by EXAMPLES-RUN) (burn-py, 2026-07-09)
- README.md:145 — quickstart_rest include: makes a live authenticated REST call to a real host (burn-py, 2026-07-09)
