#!/usr/bin/env bash
# Generate the SignalWire Python SDK API reference.
#
# Ported from the SDK-docs POC (build/python/gen.sh): install the SDK editable
# so mkdocstrings can import it, walk the `signalwire` package tree with griffe
# (the same static analyser mkdocstrings uses), and write one page per public
# module. The landing page is generated (package index + links to the guides),
# not the SDK README, whose repo-relative links don't resolve in the reference
# site.
#
# Page layout (docs_dir = _docs, use_directory_urls: false, so `x.md` -> `x.html`):
#   api/index.md                    root `signalwire` package: its own functions
#                                   + the lazy top-level exports, cross-referenced
#   api/<package>/index.md          package docstring, `__all__` summary, module list
#   api/<package>/<module>.md       one `::: signalwire.<package>.<module>` page
#   api/<module>.md                 top-level modules (signalwire.agent_server)
# Nested packages nest the same way (api/core/mixins/auth_mixin.md). Module
# names are used verbatim (underscores kept): the URL scheme
# api/<package>/<module>.html is frozen because the Fern-retirement redirects
# target it.
#
# Skipped: signalwire.cli and signalwire.mcp_gateway (entry points, not library
# API), every `_private` module, and back-compat shims that emit a
# DeprecationWarning at import time (rest/namespaces/*.py, rest/call_handler.py).
# signalwire.prefabs modules render their public classes only.
#
# The package is nested (signalwire/signalwire/) and mkdocstrings needs the
# editable install to resolve imports — that is preserved here.
#
# Usage:  reference/gen.sh              # generate pages + strict `mkdocs build`
#         reference/gen.sh --no-build   # generate pages only (the caller builds/deploys)
#         reference/gen.sh --no-install # skip the pip installs (the caller installed already)
#         Both flags are accepted together, in either order.
set -euo pipefail

NO_BUILD=0
NO_INSTALL=0
usage() {
  # Print the header's Usage block: from "# Usage:" to the end of that comment.
  awk '/^# Usage:/{p=1} p&&!/^#/{exit} p{sub(/^# ?/,""); print}' "${BASH_SOURCE[0]}"
}
for arg in "$@"; do
  case "$arg" in
    --no-build)   NO_BUILD=1 ;;
    --no-install) NO_INSTALL=1 ;;
    -h|--help)    usage; exit 0 ;;
    *) echo "gen.sh: unknown option: $arg" >&2; usage >&2; exit 2 ;;
  esac
done

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .../reference
REPO="$(cd "$HERE/.." && pwd)"                          # repo root
DOCS="$HERE/_docs"
CFG="$HERE/mkdocs.yml"

# Install the doc toolchain + the SDK (editable, so mkdocstrings can import it).
# Use `python3 -m pip` so this works whether or not a bare `pip` is on PATH.
# CI installs both itself and passes --no-install, so the pinned environment is
# not re-resolved underneath the build.
if [ "$NO_INSTALL" -eq 0 ]; then
  python3 -m pip install -q -r "$HERE/requirements.txt"
  python3 -m pip install -q -e "$REPO"
fi

# Build the docs tree: generated landing page + one API page per module.
rm -rf "$DOCS"
mkdir -p "$DOCS/api"

# Navbar assets (Fern tokens/CSS/JS/img) live under reference/assets but must be
# copied into the docs tree so Material ships them with the site.
cp -r "$HERE/assets" "$DOCS/assets"

# PYTHONPATH is for the one runtime import below (resolving root exports that
# static analysis cannot see); griffe itself reads the source tree.
PYTHONPATH="$REPO/signalwire" python3 - "$DOCS/api" "$REPO/signalwire" <<'PY'
import ast
import importlib
import os
import re
import sys

import griffe  # dependency of mkdocstrings-python; same analyser the build uses

api_out, src_root = sys.argv[1], sys.argv[2]
docs_root = os.path.dirname(api_out.rstrip("/"))

# Whole packages that are entry points rather than library API. (Note that
# signalwire.skills.mcp_gateway is a skill plugin, not this package.)
SKIP_PACKAGES = ("signalwire.cli", "signalwire.mcp_gateway")
# Packages whose modules render their public classes only (no helpers/constants).
CLASSES_ONLY = ("signalwire.prefabs",)
# Module-docstring paragraphs that are licence boilerplate, not a summary.
BOILERPLATE = ("copyright", "this file is part of", "licensed under", "see license")

pkg = griffe.load("signalwire", search_paths=[src_root], allow_inspection=False)


def walk(mod):
    yield mod
    for name in sorted(mod.modules):
        yield from walk(mod.modules[name])


_TRY_NODES = tuple(t for t in (getattr(ast, "Try", None), getattr(ast, "TryStar", None)) if t)


def warns_deprecated_on_import(filepath):
    """True when the module calls warnings.warn(..., DeprecationWarning) at import
    time: at top level, or inside a module-level if/try (never inside a def)."""
    try:
        with open(filepath, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
    except (OSError, SyntaxError, ValueError) as exc:
        print(f"gen.sh: cannot parse {filepath}: {exc}", file=sys.stderr)
        return False
    todo = list(tree.body)
    while todo:
        node = todo.pop()
        if isinstance(node, ast.If):
            todo += node.body + node.orelse
        elif isinstance(node, _TRY_NODES):
            todo += node.body + node.orelse + node.finalbody
            for handler in node.handlers:
                todo += handler.body
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            fn = call.func
            fn_name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if fn_name == "warn":
                for arg in [*call.args, *(kw.value for kw in call.keywords)]:
                    if isinstance(arg, ast.Name) and arg.id == "DeprecationWarning":
                        return True
    return False


# --- classify every module: page path, or a skip reason ----------------------
pages = {}    # griffe path -> page path relative to api_out
skipped = {}  # griffe path -> reason
for mod in walk(pkg):
    parts = mod.path.split(".")[1:]  # [] for the root package
    if any(p.startswith("_") for p in parts):
        skipped[mod.path] = "private"
    elif any(mod.path == s or mod.path.startswith(s + ".") for s in SKIP_PACKAGES):
        skipped[mod.path] = "not library API"
    elif not mod.is_init_module and warns_deprecated_on_import(mod.filepath):
        skipped[mod.path] = "deprecated shim"
    elif mod.is_init_module:
        pages[mod.path] = "/".join(parts + ["index.md"])
    else:
        pages[mod.path] = "/".join(parts) + ".md"

module_pages = [p for p, rel in pages.items() if not rel.endswith("index.md")]
# Every command after this heredoc still succeeds when nothing was generated, so
# `set -e` would let a gutted site sail through to deploy. (This is NOT an
# install check: griffe reads the source tree, with or without the editable
# install.)
if not module_pages:
    sys.exit(
        "gen.sh: no API pages generated: no public modules found under "
        f"{src_root} (griffe saw: {', '.join(sorted(m.path for m in walk(pkg))) or 'nothing'})"
    )


# --- helpers -------------------------------------------------------------------
def write(rel, text):
    path = os.path.join(api_out, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def link_to(target_rel, from_rel):
    """Relative markdown link from one generated page to another."""
    return os.path.relpath(target_rel, os.path.dirname(from_rel) or ".")


def cell(text):
    return " ".join(str(text).split()).replace("|", "\\|")


def summary(mod):
    """First docstring paragraph that is not licence boilerplate (one line)."""
    doc = mod.docstring.value if mod.docstring else ""
    for para in re.split(r"\n\s*\n", doc.strip()):
        line = para.strip().splitlines()[0].strip() if para.strip() else ""
        if not line or line.lower().startswith(BOILERPLATE):
            continue
        return re.sub(r"\s*[=\-]{3,}\s*$", "", line)
    return ""


def module_options(mod):
    """Per-page `:::` options for a plain module (empty unless classes-only)."""
    if any(mod.path == c or mod.path.startswith(c + ".") for c in CLASSES_ONLY):
        classes = [n for n, o in mod.members.items()
                   if not o.is_alias and o.is_class and not n.startswith("_")]
        return f"      members: [{', '.join(classes)}]" if classes else "      members: false"
    return ""


def resolve_export(mod, name):
    """Where an `__all__` name is defined.

    Returns (kind, defining module path, canonical object path, is_alias), or
    None when neither griffe nor a runtime import can resolve it."""
    obj = mod.members.get(name)
    if obj is not None:
        try:
            target = obj.final_target if obj.is_alias else obj
            return target.kind.value, target.module.path, target.path, obj.is_alias
        except Exception as exc:  # AliasResolutionError, CyclicAliasError
            print(f"gen.sh: {mod.path}.{name}: static resolution failed ({exc})", file=sys.stderr)
            return None
    # Not visible statically (e.g. a PEP 562 lazy export with no TYPE_CHECKING
    # import): ask the live module where the attribute comes from.
    try:
        value = getattr(importlib.import_module(mod.path), name)
        kind = "class" if isinstance(value, type) else "function" if callable(value) else "attribute"
        return kind, value.__module__, f"{value.__module__}.{value.__qualname__}", True
    except Exception as exc:
        print(f"gen.sh: {mod.path}.{name}: could not resolve ({type(exc).__name__}: {exc})",
              file=sys.stderr)
        return None


def package_page(mod, rel):
    """Package index: docstring + members defined in the package __init__ itself
    (and exports whose definition has no page of its own), then an `__all__`
    summary and the list of subpackages/modules, each linking to its page."""
    exports = mod.exports  # None when the package defines no __all__
    if exports is None:
        # No __all__: whatever the __init__ itself defines (not re-imports) is public.
        names = [n for n, o in mod.members.items()
                 if not o.is_alias and not o.is_module and not n.startswith("_")]
    else:
        names = list(exports)

    inline = []  # rendered on this page by mkdocstrings
    rows = []    # (name link, kind, defined-in cell)
    for name in names:
        info = resolve_export(mod, name)
        if info is None:
            rows.append((f"`{name}`", "—", "—"))
            continue
        kind, def_mod, canonical, is_alias = info
        if not is_alias:
            inline.append(name)
            rows.append((f"[`{name}`][{mod.path}.{name}]", kind, "this package"))
        elif def_mod in pages:
            rows.append((f"[`{name}`][{canonical}]", kind,
                         f"[`{def_mod}`]({link_to(pages[def_mod], rel)})"))
        elif name in mod.members:
            # Defined in a private/skipped module: document it here instead.
            inline.append(name)
            rows.append((f"[`{name}`][{mod.path}.{name}]", kind, f"`{def_mod}` (rendered here)"))
        else:
            rows.append((f"`{name}`", kind, f"`{def_mod}`"))

    out = [f"---\ntitle: {mod.path}\n---\n# {mod.path}\n\n::: {mod.path}\n    options:\n"]
    out.append(f"      members: [{', '.join(inline)}]\n\n" if inline else "      members: false\n\n")

    if mod is pkg:
        out.append(
            "## Top-level exports (`__all__`)\n\n"
            "Names not defined in the package `__init__` itself are lazy re-exports "
            "(PEP 562 module `__getattr__`): the module in the *Defined in* column is "
            "imported on first attribute access, so `import signalwire` stays light.\n\n"
        )
    elif exports:
        out.append("## Exports (`__all__`)\n\n")
    if rows and (exports or mod is pkg):
        out.append("| Name | Kind | Defined in |\n|---|---|---|\n")
        out += [f"| {n} | {k} | {d} |\n" for n, k, d in rows]
        out.append("\n")

    children = [(name, mod.modules[name]) for name in sorted(mod.modules) if mod.modules[name].path in pages]
    subpackages = [(n, m) for n, m in children if m.is_init_module]
    modules = [(n, m) for n, m in children if not m.is_init_module]
    if subpackages:
        out.append("## Subpackages\n\n| Package | Summary |\n|---|---|\n")
        out += [f"| [`{m.path}`]({link_to(pages[m.path], rel)}) | {cell(summary(m))} |\n"
                for n, m in subpackages]
        out.append("\n")
    if modules:
        out.append("## Modules\n\n| Module | Summary |\n|---|---|\n")
        out += [f"| [`{n}`]({link_to(pages[m.path], rel)}) | {cell(summary(m))} |\n"
                for n, m in modules]
        out.append("\n")
    return "".join(out)


def module_page(mod):
    opts = module_options(mod)
    block = f"::: {mod.path}\n" + (f"    options:\n{opts}\n" if opts else "")
    return f"---\ntitle: {mod.name}\n---\n# {mod.path}\n\n{block}"


# --- write the pages -----------------------------------------------------------
by_path = {m.path: m for m in walk(pkg)}
for path, rel in pages.items():
    mod = by_path[path]
    write(rel, package_page(mod, rel) if mod.is_init_module else module_page(mod))

# Site landing page. Replaces the SDK README (whose repo-relative links don't
# resolve here): the package list links into the generated API pages, and the
# outbound links point to the guides, source, and package index.
with open(os.path.join(docs_root, "index.md"), "w") as fh:
    fh.write("# SignalWire Python SDK — API Reference\n\n")
    fh.write("Auto-generated technical reference for the SignalWire Python SDK "
             "(`signalwire-sdk`), built from source docstrings.\n\n")
    fh.write("## Packages\n\n")
    fh.write("- [signalwire](api/index.md) — top-level exports\n")
    for name in sorted(pkg.modules):
        child = pkg.modules[name]
        if child.path in pages:
            fh.write(f"- [{child.path}](api/{pages[child.path]})\n")
    fh.write("\n---\n\n")
    fh.write("- **Guides &amp; tutorials** — "
             "[signalwire.com/docs/server-sdks](https://signalwire.com/docs/server-sdks)\n")
    fh.write("- **Source** — "
             "[github.com/signalwire/signalwire-python](https://github.com/signalwire/signalwire-python)\n")
    fh.write("- **Install** — `pip install signalwire-sdk` "
             "([PyPI](https://pypi.org/project/signalwire-sdk/))\n")
    fh.write("- **License** — "
             "[LICENSE](https://github.com/signalwire/signalwire-python/blob/main/LICENSE)\n")

# --- report --------------------------------------------------------------------
print(f"api pages: {len(pages)} ({len(pages) - len(module_pages)} package indexes, "
      f"{len(module_pages)} module pages) under {api_out}")
for reason in ("not library API", "private", "deprecated shim"):
    paths = sorted(p for p, r in skipped.items() if r == reason)
    if paths:
        print(f"skipped ({reason}, {len(paths)}): {', '.join(paths)}")
PY

if [ "$NO_BUILD" -eq 1 ]; then
  echo "pages generated under $DOCS (skipping mkdocs build)"
  exit 0
fi

# --strict so a local run fails on the same warnings CI fails on.
python3 -m mkdocs build --strict --config-file "$CFG"
echo "python -> $HERE/_site ($(find "$HERE/_site" -name '*.html' | wc -l) pages)"
