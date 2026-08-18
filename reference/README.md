# API reference

Language-native API reference for the SignalWire Python SDK, generated from
docstrings with **MkDocs Material + mkdocstrings**, wrapped in the SignalWire
**Fern navbar**, and published as a single unversioned site to this repo's own
GitHub Pages:

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
  _docs/              GENERATED docs tree (one page per signalwire.<subpackage>)  [gitignored]
  _site/              local `mkdocs build` output                                  [gitignored]
  README.md           this file
```

The `signalwire` package is nested (`signalwire/signalwire/`). mkdocstrings
resolves imports from the **editable install**, so `gen.sh` runs `pip install -e .`
first — keep that.

## Build & serve locally

From the repo root, in a virtualenv:

```bash
pip install -r reference/requirements.txt
pip install -e .

# Generate API pages + build the static site into reference/_site
bash reference/gen.sh

# Live preview: regenerates the pages, then serves with autoreload, bound to
# 0.0.0.0 so a forwarded port reaches it. PORT defaults to 3001.
bash reference/dev-server.sh [PORT]
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
`mkdocs build` fails the check on a generator error, an unimportable module, or a
new unresolved cross-reference. Build only: `contents: read`, never deploys.

`.github/workflows/reference-docs.yml` builds and publishes. It installs from
`reference/requirements.txt` plus the SDK editable, runs `gen.sh --no-build
--no-install`, builds with `--strict`, and only then runs `mkdocs gh-deploy --force`.

- **Triggers:** published releases, plus `workflow_dispatch` for manual and
  fork-preview runs.
- **Publishes only when** the run is on `signalwire/signalwire-python` (not a
  fork), the release is not flagged pre-release, the tag is stable semver
  (`vX.Y.Z`), and the tag is greater than or equal to the version recorded in
  `version.txt` at the root of the live site. That last check exists because
  `gh-deploy --force` leaves no prior version on `gh-pages` to roll back to, so
  republishing older docs over newer would be unrecoverable.
- A `workflow_dispatch` run builds a preview and publishes only if you tick the
  `deploy` input.

## Manual repo setting required to go live

One-time, in the GitHub UI:

> **Settings > Pages > Build and deployment > Source = "Deploy from a branch",
> Branch = `gh-pages` / `(root)`.**

`mkdocs gh-deploy` pushes the built site to `gh-pages`; Pages then serves it at
`https://signalwire.github.io/signalwire-python/`.

To create the `gh-pages` branch the first time, run `reference-docs` manually with
the `deploy` input ticked. A dispatch publish writes no `version.txt`, so the next
release finds an empty marker and publishes unconditionally; the monotonicity
check takes effect from the release after that.

## Scope

- **Theme toggle:** drives Material's own light/dark color scheme. There is no
  cross-origin `localStorage` theme sync with signalwire.com/docs, which is a
  different origin.
- **Not included:** versioning (mike), llms.txt/markdown emission, Docker, other
  languages, custom domain.
