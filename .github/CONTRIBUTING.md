# Contributing

> This is the master copy. The other SignalWire SDK ports carry a
> language-adapted version of the same document.

## The one thing

```bash
bash scripts/run-ci.sh
```

Run it before you push. It runs the same gates CI does, in the same order, and
it is the difference between a review about your change and a review about
formatting.

Most of what follows is just explaining what that command already checks.

## Setup

```bash
pip install -e .
pip install -r requirements-dev.txt
```

`requirements-dev.txt` is not optional, and not only for running the tests.
The type checker's answer depends on which packages are importable — a
`# type: ignore` that is **required** with `sentence-transformers` installed is
an **error** without it, and vice versa. Skip the install and your checker
grades different code than CI's, so a gate can red on lines you never touched.

`ruff` is pinned to an exact version for the same reason: a newer ruff
reformats files that already passed, and the diff lands in your PR.

## What surprises people

These are the gates that fail most often. None of them are obvious from the
code alone.

**Tests are type-checked, and they must be annotated.** `mypy` runs over
`tests/` as well as the package, in strict mode. A new test function without
annotations fails the gate:

```python
async def test_thing(fixture):              # fails
async def test_thing(fixture: Any) -> None: # passes
```

**Tests must assert something real.** A test whose body has no assertion, or
only a nullness check, is rejected — it passes whether or not the code works.
Assert on content:

```python
assert result.status == 403                       # good
assert result is not None                         # rejected: nullness only
gateway.check_origin(origin)                      # rejected: asserts nothing
```

If a test's point is that a call does *not* raise, pair it with the case that
does, so the test can actually fail:

```python
gateway.check_origin("http://localhost:3000")     # allowed
with pytest.raises(GatewayRejection):             # ...and this still isn't
    gateway.check_origin("https://evil.example.com")
```

**Formatting and lint have autofixes.** Run them rather than hand-fixing:

```bash
python3 -m ruff check signalwire --fix
python3 -m ruff format signalwire
```

`__all__` must be sorted (`RUF022`) — append a name to the end and the gate
reds. The autofix handles it.

**Docstrings have a floor.** Public symbols need one, measured against a
committed threshold. Adding public API without docstrings lowers coverage and
fails the gate.

## Before you start

**Check the open PRs.** More than one change here has been written twice
because two people fixed the same thing in the same week.

**Wire shapes come from the engine, not from the docs.** If you are changing
what the SDK puts on the wire — an action shape, an enum value, a parameter
name — say in the PR where you confirmed it. The generated types under
`signalwire/signalwire/**/*_generated.py` are derived from the engine's own
schemas and are the closest authority in this repo. A change that contradicts
them needs a reason.

## Opening the PR

**Say if you change public API.** New or renamed public classes, methods, or
parameters have to be reflected in shared infrastructure that lives in a
private repo, and a maintainer lands that alongside your PR. You do not need
access to it — just flag it in the description so it does not get missed:

> Changes public surface: adds `ChatGateway.router()`.

**If you are contributing from a fork, CI will not run.** Not a mistake on
your part: pull requests from forks do not receive repository secrets, and one
of the setup steps needs one. Every job fails in seconds with
`Input required and not supplied: token`.

Nothing you change will fix that. Run `scripts/run-ci.sh` locally, say in the
PR that you did, and a maintainer will re-run it from a branch in this repo.
Your commits keep your authorship.

## Rules of engagement

The engineering rules this project is held to — parity with the reference
implementation, what may and may not be excused, how tests are written — are
enforced by the gates, so `run-ci.sh` is the practical version of all of them.
Maintainers work from a fuller ruleset; you do not need it to contribute.
