# WIRED_MODES.md — load-bearing run-ci mode lines (Part 1.6 merge-coherence guard)

Declared patterns MUST appear in `scripts/run-ci.sh`; `porting-sdk/scripts/
check_wired_modes.py --port python --repo .` fails loud if a merge silently drops one.
If a mode is intentionally retired, update this file in the same change with the reason.

- `export MOCK_SIGNALWIRE_STRICT` — REST mock 400s on any wire violation (D3 strict default)
- `MOCK_RELAY_STRICT=1` — RELAY strict mode on the unit suite (unknown frame field / dup id rejected)
- `assert_no_wire_violations` — STRICT-MOCKS journal-read post-pass after REST coverage
