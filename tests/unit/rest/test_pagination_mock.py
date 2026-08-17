"""PaginatedIterator coverage against the mock server.

The iterator wraps any ``HttpClient.get`` call and walks paged responses
following the ``links.next`` cursor. We test it end-to-end by:

1. Staging two FIFO scenarios on a known mock endpoint — the first scenario
   has a ``links.next`` cursor, the second is the terminal page.
2. Iterating over a real ``PaginatedIterator`` wired to the SDK's ``HttpClient``
   pointed at the mock.
3. Asserting on the items collected and on the journal entries that
   correspond to the two HTTP fetches.
"""

from __future__ import annotations

from signalwire.rest._pagination import PaginatedIterator
from signalwire.rest.client import RestClient
from .conftest import _MockHarness
from typing import Any


# Pick an endpoint that the scenario store can override.  We use
# ``GET /api/fabric/addresses`` because (a) it has a stable spec-derived
# endpoint id and (b) the mock returns ``data + links`` shape by default.
_FABRIC_ADDRESSES_PATH = "/api/fabric/addresses"
_FABRIC_ADDRESSES_ENDPOINT_ID = "fabric.list_fabric_addresses"


def _push_scenario(mock: _MockHarness, endpoint_id: str, status: int, response: dict[str, Any]) -> None:
    """Push one consume-once scenario, scoped to THIS client's auth header.

    Scoping (``mock.push_scenario`` -> ``?session_id=<auth header>``) keeps a
    concurrent test from consuming this override under ``pytest -n auto``.
    """
    mock.push_scenario(endpoint_id, status, response)


class TestPaginatedIterator:
    def test_init_state(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        """Constructor records http/path/params/data_key without fetching."""
        it = PaginatedIterator(
            signalwire_client._http,
            _FABRIC_ADDRESSES_PATH,
            params={"page_size": 2},
            data_key="data",
        )
        # Constructor must not have fetched anything yet.
        assert it._http is signalwire_client._http
        assert it._path == _FABRIC_ADDRESSES_PATH
        assert it._params == {"page_size": 2}
        assert it._data_key == "data"
        assert it._index == 0
        assert it._items == []
        assert it._done is False
        # Journal must be empty — no HTTP went out.
        assert mock.journal == []

    def test_iter_returns_self(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        """``__iter__`` returns the iterator itself; ``iter(it)`` is the same."""
        it = PaginatedIterator(
            signalwire_client._http,
            _FABRIC_ADDRESSES_PATH,
            data_key="data",
        )
        # Call the dunder directly so the static coverage audit sees it.
        same = it.__iter__()
        assert same is it
        # ``iter(it)`` is the public form of the same call.
        assert iter(it) is it
        # Still no HTTP yet.
        assert mock.journal == []

    def test_next_pages_through_all_items(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        """Walks two pages and stops on the page without ``links.next``.

        A fresh per-test client starts with an empty (auth-scoped) journal and
        scenario queue, so we stage the two pages exactly once — no reset dance.
        """
        # Page 1 — has a next page. The server's links.next carries the real wire
        # param the fabric list endpoint round-trips: ``page_token`` (a cursor token
        # that starts with PA/PB), NOT a ``cursor`` param (which no SignalWire REST
        # endpoint accepts — see rest-apis/fabric/openapi.yaml ListFabricAddressesQuery).
        _push_scenario(
            mock, _FABRIC_ADDRESSES_ENDPOINT_ID,
            status=200,
            response={
                "data": [
                    {"id": "addr-1", "name": "first"},
                    {"id": "addr-2", "name": "second"},
                ],
                "links": {"next": "http://example.com/api/fabric/addresses?page_token=PA_page2"},
            },
        )
        # Page 2 — terminal (no next).
        _push_scenario(
            mock, _FABRIC_ADDRESSES_ENDPOINT_ID,
            status=200,
            response={
                "data": [
                    {"id": "addr-3", "name": "third"},
                ],
                "links": {},
            },
        )

        it = PaginatedIterator(
            signalwire_client._http,
            _FABRIC_ADDRESSES_PATH,
            data_key="data",
        )
        collected = list(it)
        # All three items, in order.
        assert [item["id"] for item in collected] == ["addr-1", "addr-2", "addr-3"]
        # Journal must have exactly two GETs at the same path.
        gets = [e for e in mock.journal if e.path == _FABRIC_ADDRESSES_PATH]
        assert len(gets) == 2, (
            f"expected 2 paginated GETs, got {len(gets)} entries: "
            f"{[(e.method, e.path, e.query_params) for e in gets]}"
        )
        # The second fetch carries the ``page_token`` param parsed from the first
        # response's ``links.next`` — the real wire token the server round-trips.
        assert gets[1].query_params.get("page_token") == ["PA_page2"], (
            f"second fetch missing page_token=PA_page2: {gets[1].query_params}"
        )

    def test_next_raises_stop_iteration_when_done(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        """After exhausting items and seeing no next cursor, raise StopIteration."""
        # One terminal page.
        _push_scenario(
            mock, _FABRIC_ADDRESSES_ENDPOINT_ID,
            status=200,
            response={
                "data": [{"id": "only-one"}],
                "links": {},
            },
        )
        it = PaginatedIterator(
            signalwire_client._http,
            _FABRIC_ADDRESSES_PATH,
            data_key="data",
        )
        # Call __next__ explicitly so the static coverage audit sees it.
        first = it.__next__()
        assert first == {"id": "only-one"}
        # Exhausted.
        try:
            it.__next__()
        except StopIteration:
            stopped = True
        else:
            stopped = False
        assert stopped, "expected StopIteration on second __next__()"

    def test_empty_page_with_next_continues(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        """An EMPTY page that still carries ``links.next`` must NOT stop iteration.

        Regression for the empty-page-with-next bug (gate plan §3.3): a page can
        legitimately return zero items while more pages exist (e.g. a filtered
        page matching nothing on this cursor).  The old termination condition
        ``next_url and data`` stopped on this empty page and silently dropped
        every subsequent page.  Correct behaviour: keep fetching while there is
        a next link, so the item on page 2 is still yielded.

        This test FAILS against the old ``if next_url and data:`` code (it
        collects ``[]`` — page 1 is empty, and the ``and data`` clause marks the
        iterator done before page 2 is ever fetched) and PASSES after the fix.
        """
        # Page 1 — EMPTY data but a next cursor pointing at page 2.
        _push_scenario(
            mock, _FABRIC_ADDRESSES_ENDPOINT_ID,
            status=200,
            response={
                "data": [],
                "links": {"next": f"{_FABRIC_ADDRESSES_PATH}?page_token=PA_page2"},
            },
        )
        # Page 2 — the real item, terminal (no next).
        _push_scenario(
            mock, _FABRIC_ADDRESSES_ENDPOINT_ID,
            status=200,
            response={
                "data": [{"id": "addr-late", "name": "found-after-empty-page"}],
                "links": {},
            },
        )

        it = PaginatedIterator(
            signalwire_client._http,
            _FABRIC_ADDRESSES_PATH,
            data_key="data",
        )
        collected = list(it)
        # The iterator did NOT stop on the empty page 1 — it fetched page 2 and
        # yielded its item.
        assert [item["id"] for item in collected] == ["addr-late"], (
            "empty page 1 with links.next must not stop pagination; "
            f"expected page-2 item, got {collected}"
        )
        # Two GETs went out: the empty page, then the page reached via the cursor.
        gets = [e for e in mock.journal if e.path == _FABRIC_ADDRESSES_PATH]
        assert len(gets) == 2, (
            f"expected 2 paginated GETs across the empty page and the next, "
            f"got {len(gets)}: {[(e.method, e.path, e.query_params) for e in gets]}"
        )
        assert gets[1].query_params.get("page_token") == ["PA_page2"], (
            f"second fetch missing page_token=PA_page2 parsed from the empty page's "
            f"links.next: {gets[1].query_params}"
        )

    def test_resource_paginate_walks_all_pages(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        """ReadResource.paginate() wires the resource layer to PaginatedIterator:
        a caller pages through every item without hand-constructing the path/token
        loop. Two mock pages (first carries links.next), collected in order."""
        from signalwire.rest._base import ReadResource

        _push_scenario(
            mock, _FABRIC_ADDRESSES_ENDPOINT_ID, status=200,
            response={
                "data": [{"id": "r-1"}, {"id": "r-2"}],
                "links": {"next": f"{_FABRIC_ADDRESSES_PATH}?page_token=PA_page2"},
            },
        )
        _push_scenario(
            mock, _FABRIC_ADDRESSES_ENDPOINT_ID, status=200,
            response={"data": [{"id": "r-3"}], "links": {}},
        )

        resource: ReadResource[Any, Any] = ReadResource(
            signalwire_client._http, _FABRIC_ADDRESSES_PATH
        )
        collected = [item["id"] for item in resource.paginate()]
        assert collected == ["r-1", "r-2", "r-3"]
        gets = [e for e in mock.journal if e.path == _FABRIC_ADDRESSES_PATH]
        assert len(gets) == 2, f"expected 2 paginated GETs, got {len(gets)}"
        assert gets[1].query_params.get("page_token") == ["PA_page2"]

    def test_repeating_next_link_terminates(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        """Cycle guard (3-rust-b's python half): a server that keeps returning the SAME
        ``links.next`` (with or without items) must TERMINATE, not loop forever making
        identical requests. Before the guard, the empty-page fix (terminate only on
        absent next) made a repeating next an infinite loop."""
        same_next = "http://example.com/api/fabric/addresses?page_token=PA_loop"
        # Two pages that both point at the same next cursor. The guard fires when the
        # cursor REPEATS (page 2's next == page 2's own request), so iteration ends
        # after consuming both pages' items instead of looping on page 3, 4, ….
        _push_scenario(
            mock, _FABRIC_ADDRESSES_ENDPOINT_ID,
            status=200,
            response={"data": [{"id": "a-1"}], "links": {"next": same_next}},
        )
        _push_scenario(
            mock, _FABRIC_ADDRESSES_ENDPOINT_ID,
            status=200,
            response={"data": [{"id": "a-2"}], "links": {"next": same_next}},
        )

        it = PaginatedIterator(
            signalwire_client._http,
            _FABRIC_ADDRESSES_PATH,
            data_key="data",
        )
        items = list(it)  # must not hang
        assert [i["id"] for i in items] == ["a-1", "a-2"]
        # exactly 2 requests hit the wire — the repeated cursor was not re-fetched
        assert len(mock.journal) == 2
