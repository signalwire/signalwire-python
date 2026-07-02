# API reference (pilot)

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
  gen.sh              installs the SDK editable, generates the API pages, builds
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

# Live preview (regenerates pages first, then serves with autoreload)
bash reference/gen.sh --no-build
mkdocs serve --config-file reference/mkdocs.yml
```

`use_directory_urls: false`, so every page is a real `.html` file and the site
works under the `/signalwire-python/` base path.

## Deploy

A single, unversioned "latest" site is published to the `gh-pages` branch via
`mkdocs gh-deploy` (CI does this — see below). Versioning (a per-release version
selector via `mike`) was intentionally left out of the pilot and can be added
later without touching the markup.

## CI

`.github/workflows/reference-docs.yml` (plain `actions/setup-python`, no Docker):

- **Triggers:** `v*` release tags (each release rebuilds + republishes) plus
  `workflow_dispatch` for manual / fork-preview runs.
- Installs from `reference/requirements.txt` + the SDK editable, runs
  `gen.sh --no-build`, then `mkdocs gh-deploy --force` to the `gh-pages` branch.

## Manual repo setting required to go live

One-time, in the GitHub UI:

> **Settings → Pages → Build and deployment → Source = "Deploy from a branch" →
> Branch = `gh-pages` / `(root)`.**

`mkdocs gh-deploy` pushes the built site to `gh-pages`; Pages then serves it at
`https://signalwire.github.io/signalwire-python/`.

## Pilot simplifications

- **Theme toggle:** drives Material's own light/dark color scheme. No
  cross-origin `localStorage` theme sync with signalwire.com/docs (different
  origin — out of scope).
- Out of scope: versioning (mike), llms.txt/markdown emission, Docker, other
  languages, custom domain.
