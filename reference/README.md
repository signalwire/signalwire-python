# API reference (pilot)

Language-native API reference for the SignalWire Python SDK, generated from
docstrings with **MkDocs Material + mkdocstrings**, wrapped in the SignalWire
**Fern navbar**, and versioned with **mike**. Published to this repo's own
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
pip install -e .
pip install mkdocs-material "mkdocstrings[python]" mike

# Generate API pages + build the static site into reference/_site
bash reference/gen.sh

# Live preview (regenerates pages first, then serves with autoreload)
bash reference/gen.sh --no-build
mkdocs serve --config-file reference/mkdocs.yml
```

`use_directory_urls: false`, so every page is a real `.html` file and the site
works under the `/signalwire-python/` base path.

## Versioning (mike)

`extra.version.provider: mike` in `mkdocs.yml` turns on Material's version
selector; it reads `versions.json` from the site root at runtime. mike commits
each deployed version to a local `gh-pages` branch.

```bash
bash reference/gen.sh --no-build                      # generate pages first

# Deploy a version and (re)point the `latest` alias at it; set it as default.
mike deploy  --config-file reference/mkdocs.yml --update-aliases 3.0.2 latest
mike set-default --config-file reference/mkdocs.yml latest
mike list    --config-file reference/mkdocs.yml       # -> 3.0.2 [latest], 3.0.1

mike serve   --config-file reference/mkdocs.yml       # preview all versions + selector
```

Add `--push` to push the `gh-pages` branch to the remote (CI does this; do not
locally).

## CI

`.github/workflows/reference-docs.yml` (plain `actions/setup-python`, no Docker):

- **Pilot triggers:** `workflow_dispatch` + push to `docs/api-reference-pilot`.
- Installs the SDK editable + `mkdocs-material`, `mkdocstrings[python]`, `mike`,
  runs `gen.sh --no-build`, then `mike deploy --push --update-aliases <version> latest`.
- **Production trigger (later):** `v*` tags (commented in the workflow), so each
  release deploys its version and re-aliases `latest`.

## Manual repo setting required to go live

One-time, in the GitHub UI:

> **Settings → Pages → Build and deployment → Source = "Deploy from a branch" →
> Branch = `gh-pages` / `(root)`.**

mike pushes the built site to `gh-pages`; Pages then serves it at
`https://signalwire.github.io/signalwire-python/`.

## Pilot simplifications

- **Language switcher:** cross-site links with Python marked active; other
  languages point at the POC demo (no per-language hosted site exists yet).
- **Theme toggle:** drives Material's own light/dark color scheme. No
  cross-origin `localStorage` theme sync with signalwire.com/docs (different
  origin — out of scope).
- Out of scope: llms.txt/markdown emission, Docker, other languages, custom domain.
