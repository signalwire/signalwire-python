<!--
Thanks for the patch. The checklist is short on purpose — the first box
catches almost everything. See CONTRIBUTING.md.
-->

## What this changes



## Checklist

- [ ] `bash scripts/run-ci.sh` passes locally
- [ ] New tests assert on content (not just "does not raise" / "is not None")
- [ ] New test functions are type-annotated (`mypy` covers `tests/`)

## Does this change public API?

- [ ] No
- [ ] Yes — naming it here so a maintainer can land the matching
      infrastructure change:

<!--
  e.g. "adds ChatGateway.router()", "renames tap(direction=) values".
  You do not need access to that repo. Just say what changed.
-->

## Changing something that goes on the wire?

If this alters an emitted shape, an enum value, or a parameter name, say where
you confirmed it — the generated types under `signalwire/**/*_generated.py` are
derived from the engine's schemas and are the authority here.

<!--
  Contributing from a fork? CI will fail in seconds on
  "Input required and not supplied: token" — fork PRs do not get repository
  secrets. That is expected and not something you can fix. Run
  scripts/run-ci.sh locally, say so above, and a maintainer will re-run it.
-->
