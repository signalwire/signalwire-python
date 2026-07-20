"""Per-call ``request_options`` on the REST RESOURCE verbs (PY-7).

The ``HttpClient`` verbs and the ``RestClient`` ctor already accept
``request_options``; this pins the PUBLIC per-call door on the RESOURCE-layer
verbs — ``list`` / ``get`` / ``create`` and the generated operation methods —
so a caller can override timeout / retry / headers on a SINGLE resource call:

    client.addresses.list(request_options=RequestOptions(retries=1))

The observable is the mock's request journal. ``retries`` is wire-visible: with
``retries=1`` a retryable 503 is retried into the default 200, so the mock sees
TWO attempts. If the resource verb IGNORED ``request_options`` (the pre-PY-7
behaviour — the generated override / base method dropped it), the client would
NOT retry and the mock would see ONE attempt. These tests therefore fail RED
before the template change and pass GREEN after — proving the param reaches the
HTTP layer, not just that it is accepted.

Driven through the real ``requests`` transport into the shared
``mock_signalwire`` (same journal the REST-COVERAGE gate reads), mirroring
``test_request_options.py`` (which pins the same contract one layer lower, on
``client._http``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from signalwire.rest import RequestOptions

if TYPE_CHECKING:
    from signalwire.rest.client import RestClient

    from .conftest import _MockHarness

# retries with zero wall-clock backoff — a retryable 503 folds into the default
# synthesized 200 without a real sleep.
_RETRY_ONCE = RequestOptions(retries=1, retry_backoff=0.0)


def _attempts(mock: _MockHarness, path: str, method: str) -> int:
    return len([e for e in mock.journal if e.path == path and e.method == method])


class TestListVerbHonorsRequestOptions:
    """``ReadResource.list`` threads per-call ``request_options`` to the wire."""

    _PATH = "/api/relay/rest/addresses"

    def test_list_retries_when_request_options_passed(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "relay-rest.list_addresses", 503, {"errors": [{"code": "X"}]}
        )
        signalwire_client.addresses.list(request_options=_RETRY_ONCE)
        # 503 retried into the default 200 => exactly 2 GET attempts. Without the
        # per-call door threaded through, list() would not retry => 1 attempt (RED).
        assert _attempts(mock, self._PATH, "GET") == 2

    def test_list_does_not_retry_without_request_options(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        # Control: the default (no request_options) must NOT retry — proves the 2
        # attempts above come from the passed options, not an always-on retry.
        mock.push_scenario(
            "relay-rest.list_addresses", 503, {"errors": [{"code": "X"}]}
        )
        try:
            signalwire_client.addresses.list()
        except Exception:
            pass
        assert _attempts(mock, self._PATH, "GET") == 1


class TestGetVerbHonorsRequestOptions:
    """``ReadResource.get`` threads per-call ``request_options`` to the wire."""

    _PATH = "/api/relay/rest/addresses/addr-1"

    def test_get_retries_when_request_options_passed(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.get_address", 503, {"errors": [{"code": "X"}]})
        signalwire_client.addresses.get("addr-1", request_options=_RETRY_ONCE)
        assert _attempts(mock, self._PATH, "GET") == 2


class TestCreateVerbHonorsRequestOptions:
    """The generated closed ``create`` threads per-call ``request_options``."""

    _PATH = "/api/relay/rest/addresses"

    def _create(
        self, client: RestClient, request_options: RequestOptions | None = None
    ) -> None:
        client.addresses.create(
            label="home",
            country="US",
            first_name="A",
            last_name="B",
            street_number="1",
            street_name="Main",
            city="X",
            state="CA",
            postal_code="90000",
            request_options=request_options,
        )

    def test_create_retries_when_request_options_passed(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        # 503 is a throttle → retryable even for POST (idempotency asymmetry), so
        # retries=1 yields 2 attempts iff create() forwarded request_options.
        mock.push_scenario("relay-rest.create_address", 503, {"error": "x"})
        self._create(signalwire_client, _RETRY_ONCE)
        assert _attempts(mock, self._PATH, "POST") == 2

    def test_create_does_not_retry_without_request_options(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("relay-rest.create_address", 503, {"error": "x"})
        try:
            self._create(signalwire_client)
        except Exception:
            pass
        assert _attempts(mock, self._PATH, "POST") == 1


class TestGeneratedOperationMethodHonorsRequestOptions:
    """A generated x-sdk-resource operation method (datasphere ``documents.search``)
    threads per-call ``request_options`` to the wire."""

    _PATH = "/api/datasphere/documents/search"

    def test_search_retries_when_request_options_passed(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("datasphere.search_documents", 503, {"error": "x"})
        signalwire_client.datasphere.documents.search(
            query_string="hello", request_options=_RETRY_ONCE
        )
        assert _attempts(mock, self._PATH, "POST") == 2

    def test_search_does_not_retry_without_request_options(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("datasphere.search_documents", 503, {"error": "x"})
        try:
            signalwire_client.datasphere.documents.search(query_string="hello")
        except Exception:
            pass
        assert _attempts(mock, self._PATH, "POST") == 1
