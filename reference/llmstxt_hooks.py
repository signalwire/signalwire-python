"""Finish what the mkdocs-llmstxt plugin publishes. See README.md.

mkdocs.yml loads this file in two roles:

- as the plugin's `preprocess` module: `preprocess()` points every link between
  pages at the page's Markdown copy, so the copies link to each other rather
  than to the HTML pages.
- as an MkDocs hook: `on_post_build()` runs after the plugin has written
  llms.txt. It titles each API link with the full module path, then fails the
  build if llms.txt misses a page or a Markdown copy links to a file that the
  build did not write. `mkdocs build` and `mkdocs gh-deploy` both run it.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import event_priority

# One llms.txt entry: "- [title](url)", optionally followed by ": description".
_ENTRY = re.compile(r"^- \[[^\]\n]*\]\((?P<url>[^)\s]+)\)", re.M)
# A Markdown link target.
_LINK = re.compile(r"\]\((?P<url>[^)\s]+)")


def preprocess(soup: BeautifulSoup, output: str) -> None:
    """Point relative links to `.html` pages at the `.md` copy of the page.

    The plugin then makes these links absolute. Every page has a copy, which
    `on_post_build` checks.
    """
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if not isinstance(href, str) or href.startswith(("/", "#")):
            continue
        parts = urlsplit(href)
        if parts.scheme or parts.netloc or not parts.path.endswith(".html"):
            continue
        anchor["href"] = urlunsplit(
            parts._replace(path=parts.path[: -len(".html")] + ".md")
        )


def _module_path(rel: str) -> str:
    """`api/core/mixins/auth_mixin` -> `signalwire.core.mixins.auth_mixin`.

    gen.sh names API pages after their modules verbatim, so the page path
    gives the module path. A package's page is its `index`.
    """
    parts = rel.split("/")[1:]
    if parts and parts[-1] == "index":
        parts = parts[:-1]
    return ".".join(["signalwire", *parts])


@event_priority(-100)  # after the llmstxt plugin has written llms.txt
def on_post_build(config: MkDocsConfig, **kwargs: Any) -> None:
    site = Path(config.site_dir)
    base = str(config.site_url).rstrip("/") + "/"
    llms = site / "llms.txt"
    errors: list[str] = []
    listed: set[str] = set()  # site paths without the ".md" suffix

    def retitle(entry: re.Match[str]) -> str:
        url = entry["url"]
        if not (url.startswith(base) and url.endswith(".md")):
            errors.append(
                f"llms.txt links to {url}, which is not a page copy on {base}"
            )
            return entry[0]
        rel = url[len(base) : -len(".md")]
        listed.add(rel)
        if rel.split("/")[0] != "api":
            return entry[0]
        return f"- [{_module_path(rel)}]({url})"

    llms.write_text(
        _ENTRY.sub(retitle, llms.read_text(encoding="utf8")), encoding="utf8"
    )

    pages = {
        p.relative_to(site).with_suffix("").as_posix() for p in site.rglob("*.html")
    } - {"404"}  # Material's error page, not a docs page
    errors += [
        f"llms.txt does not list {p}.html (extend the llmstxt sections in mkdocs.yml)"
        for p in sorted(pages - listed)
    ]
    errors += [
        f"llms.txt lists {p}.md, which was not written"
        for p in sorted(listed)
        if not (site / f"{p}.md").is_file()
    ]
    for rel in sorted(listed):
        copy = site / f"{rel}.md"
        if not copy.is_file():
            continue
        for link in _LINK.finditer(copy.read_text(encoding="utf8")):
            url = link["url"].split("#", 1)[0]
            if url.startswith(base) and not (site / url[len(base) :]).is_file():
                errors.append(
                    f"{rel}.md links to {link['url']}, which the build did not write"
                )
    if errors:
        unique = dict.fromkeys(errors)  # a page can repeat the same broken link
        raise PluginError("llms.txt check failed:\n  " + "\n  ".join(unique))
