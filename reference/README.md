# API reference

Language-native API reference for the SignalWire Python SDK,
generated from docstrings with **MkDocs Material + mkdocstrings**,
wrapped in the SignalWire **Fern navbar**,
and published as a single unversioned site to this repo's own GitHub Pages:

> https://signalwire.github.io/signalwire-python/

This is self-contained under `reference/` and does **not** touch the repo's
existing top-level `docs/` directory (owned by `doc-audit.yml`).

## Layout

```
reference/
  mkdocs.yml          MkDocs Material + mkdocstrings config (docs_dir = _docs)
  requirements.txt    pinned doc toolchain (MkDocs Material, mkdocstrings)
  gen.sh              installs the SDK editable, generates the API pages, builds
  dev-server.sh       generates the pages, then serves them with live reload
  overrides/main.html extends Material's base.html; injects the Fern navbar
  assets/             Fern tokens/CSS/JS + logo/favicon (committed; no shared host yet)
  _docs/              GENERATED docs tree (one page per public module, see below) [gitignored]
  _site/              local `mkdocs build` output                                  [gitignored]
  README.md           this file
```

The `signalwire` package is nested (`signalwire/signalwire/`). mkdocstrings
resolves imports from the **editable install**, so `gen.sh` runs `pip install -e .`
first — keep that.

## Page layout

`gen.sh` walks the `signalwire` package tree with griffe (the static analyser
mkdocstrings itself uses) and writes one page per public module. With
`use_directory_urls: false`, `x.md` renders to `x.html`:

| Page | Renders |
|---|---|
| `api/index.md` | the root `signalwire` package: the functions its `__init__` defines, then a table of the top-level `__all__` exports (the lazy, PEP 562 ones included) cross-referenced to the module that defines each. This is the "root `signalwire` page"; it doubles as the API section's index, so there is no separate `api/signalwire.html`. |
| `api/<package>/index.md` | the package docstring, an `__all__` summary table linking each export to its page, and the list of subpackages and modules. Whatever the package `__init__` defines itself is rendered here (`signalwire.livewire` defines most of its API there), and so is an export whose definition lives in a `_private` module (`signalwire.rest.SignalWireRestError`), since that module has no page of its own. |
| `api/<package>/<module>.md` | `::: signalwire.<package>.<module>` — everything public in the module. |
| `api/<module>.md` | top-level modules (`signalwire.agent_server`). |

Nested packages nest the same way (`api/core/mixins/auth_mixin.html`). Module
names are used verbatim, underscores included: the `api/<package>/<module>.html`
URL scheme is frozen because the Fern-retirement redirects target it.

Skipped:

- `signalwire.cli` and `signalwire.mcp_gateway`: entry points, not library API.
  (`signalwire.skills.mcp_gateway` is a skill plugin and is kept.)
- any module with a `_private` component in its dotted path.
- deprecated back-compat shims: modules that call
  `warnings.warn(..., DeprecationWarning)` at import time (top level, or inside a
  module-level `if`/`try`). Detected from the AST, so nothing is imported. Today
  that is every `rest/namespaces/<name>.py` re-export shim and `rest/call_handler.py`.

`signalwire.prefabs` modules render their public classes only. `gen.sh` prints
what it wrote and what it skipped, and the "no API pages generated" guard aborts
the run when the walk yields no module pages.

The nav is MkDocs' automatic one, built from the docs tree: page titles come from
front matter (module pages use the short module name, index pages the dotted
package path), section labels from directory names.

## Build & serve locally

From the repo root, in a virtualenv:

```bash
pip install -r reference/requirements.txt
pip install -e .

# Generate API pages + build the static site into reference/_site
bash reference/gen.sh

# Live preview: regenerates the pages, then serves with autoreload, bound to
# 0.0.0.0 so a forwarded port reaches it. PORT defaults to 3001.
bash reference/dev-server.sh        # or: bash reference/dev-server.sh 3005
```

`gen.sh` also takes `--no-build` (generate the pages only) and `--no-install`
(skip the pip installs). Both CI workflows pass `--no-install`, since they install
the pinned toolchain themselves; the publishing one adds `--no-build`, since it
builds in a separate step.

`use_directory_urls: false`, so every page is a real `.html` file and the site
works under the `/signalwire-python/` base path.

## Deploy

The site is unversioned: `mkdocs gh-deploy` publishes it to the `gh-pages` branch,
where the current release's docs sit at the site root. There is no per-version
path and no `latest` alias to navigate to. A version selector (via `mike`) can be
added later without touching the markup. CI does the publishing, see below.

## CI

Two workflows, both plain `actions/setup-python`, no Docker.

`.github/workflows/reference-check.yml` builds on every PR touching `signalwire/`,
`reference/`, or `pyproject.toml`. It runs `gen.sh --no-install`, whose strict
`mkdocs build` fails the check on a generator error or a new unresolved
cross-reference. It does **not** catch a
submodule with a missing runtime dependency: mkdocstrings analyses statically
through griffe, so that module still renders a clean page. Build only:
`contents: read`, never deploys.

`.github/workflows/reference-docs.yml` builds and publishes. It installs from
`reference/requirements.txt` plus the SDK editable, runs `gen.sh --no-build
--no-install`, builds with `--strict`, and only then runs `mkdocs gh-deploy --force`.

- **Triggers:** a reusable `workflow_call` from `publish-release.yml`, which
  invokes it after the CI gates and the PyPI upload have succeeded, plus
  `workflow_dispatch` for manual and fork-preview runs. There is deliberately no
  `release: published` trigger: that release is created with `GITHUB_TOKEN`, and
  GitHub raises no workflow-triggering events for that token, so the trigger
  would look right and never fire on the normal tag path.
- **Publishes only when** the run is on `signalwire/signalwire-python` (not a
  fork), the tag is stable semver (`vX.Y.Z`) so an rc tag cannot overwrite the
  stable site, and the tag is at least as new as the version recorded in
  `version.txt` at the root of the live site. Anything the gate cannot positively
  determine, such as an unreadable `gh-pages` or a site with no marker, fails
  closed rather than publishing, and fails the job so the run goes red. The PyPI
  upload is already done by then and is not affected; "Re-run failed jobs"
  republishes once the cause is repaired.
- A `workflow_dispatch` run builds a preview, and publishes only if you tick the
  `deploy` input **and** dispatch from the default branch. Without that second
  condition any branch in the dropdown could publish itself as the official
  public reference, running its own code under a `contents: write` token.
- **On rollback:** `gh-deploy` force-pushes but does not discard history. mkdocs
  passes `no_history=False`, so ghp-import parents each deploy onto the previous
  one and `--force` forces only the push. A bad publish is recoverable by hand
  with `git push --force origin gh-pages~1:gh-pages`. The gate exists because
  that recovery depends on somebody noticing, not because rollback is impossible.
  This is also why `fetch-depth: 0` must stay: it is what fetches
  `origin/gh-pages`, and without it the force-push lands a parentless orphan and
  the history really is gone.

## Going live

Two one-time steps, in this order. The Pages dropdown cannot offer `gh-pages`
until the branch exists, so the dispatch has to come first.

1. Run `reference-docs` manually from the default branch with the `deploy` input
   ticked. That creates `gh-pages` and stamps `version.txt` with the `v0.0.0`
   bootstrap floor.
2. In the GitHub UI: **Settings > Pages > Build and deployment >
   Source = "Deploy from a branch", Branch = `gh-pages` / `(root)`.**

Pages then serves the site at `https://signalwire.github.io/signalwire-python/`.

### The version marker

`version.txt` at the site root records the version currently published, and the
monotonicity check reads it. **Every** publish stamps it, dispatches included:
`gh-deploy` replaces the whole site tree, so a dispatch that did not re-stamp
would erase the marker and silently disarm the guard for the next release. A
dispatch preserves whatever is already there.

A site with no readable marker is therefore an anomaly, and the gate refuses to
publish over it on both paths: a release fails, and a dispatch fails unless the
`version_marker` input is set. The `v0.0.0` floor applies only when `gh-pages`
does not exist yet. If the marker ever needs repairing, for instance after a typo
tag like `v31.0.0` sorts newest and starts blocking real releases, dispatch a
publish with the `version_marker` input set to the correct `vX.Y.Z`.

## Scope

- **Theme toggle:** drives Material's own light/dark color scheme. There is no
  cross-origin `localStorage` theme sync with signalwire.com/docs, which is a
  different origin.
- **Not included:** versioning (mike), llms.txt/markdown emission, Docker, other
  languages, custom domain.
