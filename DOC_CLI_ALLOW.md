# DOC_CLI_ALLOW.md — CLI-invocation doc lines excused from DOC-CLI

Each entry: a substring of the documented invocation the gate should skip,
followed by a reason. Only for lines that are intentionally non-runnable
(syntax templates, shell-loop variables) — never to hide a real fictional flag.

- swaig-test <file> [--cli-flags] --exec <function> [--function-args] — grammar/syntax template with literal <placeholder> tokens, not a runnable command (docs/cli_guide.md, 2026-07-08)
- $func '{"test":"data"}' — inside a bash `for func in ...` loop; $func is a shell variable, not a real function name (docs/cli_guide.md, 2026-07-08)
