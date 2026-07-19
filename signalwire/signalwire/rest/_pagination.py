"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Pagination support for list endpoints that return paged results.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Type-only import: _base imports this module (ReadResource.paginate), so a
    # runtime `from ._base import HttpClient` would be a circular import. HttpClient
    # is used here purely as an annotation, so guard it under TYPE_CHECKING.
    from ._base import HttpClient


class PaginatedIterator:
    """Iterates items across paginated API responses.

    Usage:
        for item in PaginatedIterator(http, "/api/path", params={}, data_key="data"):
            print(item)
    """

    def __init__(
        self,
        http: "HttpClient",
        path: str,
        params: dict[str, Any] | None = None,
        data_key: str = "data",
    ) -> None:
        self._http = http
        self._path = path
        self._params: dict[str, Any] = dict(params or {})
        self._data_key = data_key
        self._current_page: Any = None
        self._items: list[Any] = []
        self._index = 0
        self._done = False
        # Cycle guard: next-link cursors already followed. A server that keeps
        # returning the SAME ``links.next`` would otherwise loop forever (the
        # empty-page fix terminates only on an ABSENT next link, so a repeating
        # next became an infinite loop). Seeing a repeat terminates iteration.
        self._seen_next: set[str] = set()

    def __iter__(self) -> "PaginatedIterator":
        return self

    def __next__(self) -> Any:
        while self._index >= len(self._items):
            if self._done:
                raise StopIteration
            self._fetch_next()

        item = self._items[self._index]
        self._index += 1
        return item

    def _fetch_next(self) -> None:
        resp = self._http.get(self._path, params=self._params or None)
        data = resp.get(self._data_key, [])
        self._items.extend(data)

        links = resp.get("links", {})
        next_url = links.get("next")
        # Termination is driven ONLY by the absence of a next link, NOT by an
        # empty ``data`` array on this page.  A page can legitimately carry a
        # ``links.next`` (more pages exist) while returning zero items on THIS
        # page — e.g. a filtered page that happens to match nothing here.  The
        # old ``next_url and data`` condition stopped on such a page and
        # silently dropped every subsequent page; iterate while a next link
        # exists, empty page or not.
        if next_url:
            # Cycle guard: a ``links.next`` we have already followed means the
            # server is looping (a repeating cursor) — terminate instead of
            # re-fetching the same page forever.
            if next_url in self._seen_next:
                self._done = True
                return
            self._seen_next.add(next_url)
            # Parse cursor/page token from next URL if present
            # Most SignalWire APIs use page_token or cursor param
            from urllib.parse import urlparse, parse_qs

            parsed = urlparse(next_url)
            query = parse_qs(parsed.query)
            # Flatten single-value lists
            self._params = {k: v[0] if len(v) == 1 else v for k, v in query.items()}
        else:
            self._done = True
