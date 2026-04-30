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

import requests

from signalwire.rest._pagination import PaginatedIterator


# Pick an endpoint that the scenario store can override.  We use
# ``GET /api/fabric/addresses`` because (a) it has a stable spec-derived
# endpoint id and (b) the mock returns ``data + links`` shape by default.
_FABRIC_ADDRESSES_PATH = "/api/fabric/addresses"
_FABRIC_ADDRESSES_ENDPOINT_ID = "fabric.list_fabric_addresses"


def _push_scenario(mock, endpoint_id: str, status: int, response: dict) -> None:
    """Push one consume-once scenario via the mock control plane."""
    r = requests.post(
        f"{mock.url}/__mock__/scenarios/{endpoint_id}",
        json={"status": status, "response": response},
    )
    r.raise_for_status()


class TestPaginatedIterator:
    def test_init_state(self, signalwire_client, mock):
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

    def test_iter_returns_self(self, signalwire_client, mock):
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

    def test_next_pages_through_all_items(self, signalwire_client, mock):
        """Walks two pages and stops on the page without ``links.next``."""
        # Page 1 — has a next cursor.
        _push_scenario(
            mock, _FABRIC_ADDRESSES_ENDPOINT_ID,
            status=200,
            response={
                "data": [
                    {"id": "addr-1", "name": "first"},
                    {"id": "addr-2", "name": "second"},
                ],
                "links": {"next": "http://example.com/api/fabric/addresses?cursor=page2"},
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

        # Reset journal so only our paginated fetches are recorded.
        mock.reset()
        # Re-stage scenarios after reset (reset() clears scenarios too).
        _push_scenario(
            mock, _FABRIC_ADDRESSES_ENDPOINT_ID,
            status=200,
            response={
                "data": [
                    {"id": "addr-1", "name": "first"},
                    {"id": "addr-2", "name": "second"},
                ],
                "links": {"next": "http://example.com/api/fabric/addresses?cursor=page2"},
            },
        )
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
        # The second fetch carries the ``cursor=page2`` param parsed from
        # the first response's ``links.next``.
        assert gets[1].query_params.get("cursor") == ["page2"], (
            f"second fetch missing cursor=page2: {gets[1].query_params}"
        )

    def test_next_raises_stop_iteration_when_done(self, signalwire_client, mock):
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
