"""RequestOptions envelope — behavioral contract over the real mock (plan 4.2).

These drive a real ``RestClient`` through the real ``requests`` transport into
the shared ``mock_signalwire`` and assert on the recorded journal — the same
journal the REST-COVERAGE gate reads. Retry / timeout are wire-observable: the
mock sees N attempts and honors the backoff ordering, so the contract is proven
over the real mock, NOT mock.patch.

Contract pinned here (the oracle):
- ``retries``: a retryable failure is retried up to ``retries`` extra times; the
  mock sees ``retries + 1`` attempts; the final success is returned.
- idempotency asymmetry: GET/PUT/DELETE retry on the full ``retry_on_status``
  set; POST/PATCH retry only on 429/503 (throttles), never 500/502/504.
- ``timeout``: a server-side delay exceeding the timeout raises the transport
  error family.
- ``abort_signal``: set before a request raises the transport error family.
- per-request options shallow-override the client default.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import pytest

from signalwire.rest import RequestOptions
from signalwire.rest._base import SignalWireRestError, SignalWireRestTransportError

if TYPE_CHECKING:
    from signalwire.rest.client import RestClient

    from .conftest import _MockHarness

# A spec-derived endpoint the mock synthesizes a 200 for by default, and whose
# scenario store we can override. Same one the pagination tests use.
_ADDRESSES_ENDPOINT_ID = "fabric.list_fabric_addresses"


def _addresses(client: RestClient, request_options: RequestOptions | None = None):
    """Drive one GET /api/fabric/addresses through the real transport."""
    return client._http.get("/api/fabric/addresses", request_options=request_options)


class TestRetryContract:
    """A retryable failure is retried; the mock sees every attempt."""

    def test_get_retries_503_then_succeeds(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        # Arm a single 503; the default synthesized 200 follows it. With
        # retries=1 the client retries the 503 into the 200 → 2 attempts.
        mock.push_scenario(_ADDRESSES_ENDPOINT_ID, 503, {"errors": [{"code": "X"}]})
        result = _addresses(
            signalwire_client,
            RequestOptions(retries=1, retry_backoff=0.0),  # no wall-clock delay
        )
        assert result is not None
        gets = [
            e
            for e in mock.journal
            if e.path == "/api/fabric/addresses" and e.method == "GET"
        ]
        assert len(gets) == 2, f"expected 2 attempts (503 then 200), got {len(gets)}"

    def test_no_retries_by_default_raises_on_first_failure(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        # Default retries=0: the first non-2xx raises immediately (the original
        # no-retry contract remains the default; retries are opt-in).
        mock.push_scenario(_ADDRESSES_ENDPOINT_ID, 503, {"errors": [{"code": "X"}]})
        with pytest.raises(SignalWireRestError) as exc:
            _addresses(signalwire_client)
        assert exc.value.status_code == 503
        gets = [
            e
            for e in mock.journal
            if e.path == "/api/fabric/addresses" and e.method == "GET"
        ]
        assert len(gets) == 1, "default must not retry"

    def test_retries_exhausted_raises_last_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        # Two 503s + retries=1 => attempts = 2, both 503 => raise the 503.
        mock.push_scenario(_ADDRESSES_ENDPOINT_ID, 503, {"errors": [{"code": "X"}]})
        mock.push_scenario(_ADDRESSES_ENDPOINT_ID, 503, {"errors": [{"code": "X"}]})
        with pytest.raises(SignalWireRestError) as exc:
            _addresses(signalwire_client, RequestOptions(retries=1, retry_backoff=0.0))
        assert exc.value.status_code == 503
        gets = [
            e
            for e in mock.journal
            if e.path == "/api/fabric/addresses" and e.method == "GET"
        ]
        assert len(gets) == 2, "retries=1 => exactly 2 attempts"


class TestIdempotencyAsymmetry:
    """POST/PATCH do not blindly retry 500/502/504; GET/PUT/DELETE do."""

    _CREATE_ADDRESS_PATH = "/api/relay/rest/addresses"

    def test_post_does_not_retry_500(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        # A real POST route; 500 is NOT retryable for a non-idempotent method
        # even with retries armed → exactly one attempt, raise the 500.
        mock.push_scenario("relay-rest.create_address", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client._http.post(
                self._CREATE_ADDRESS_PATH,
                body={"label": "x"},
                request_options=RequestOptions(retries=2, retry_backoff=0.0),
            )
        assert exc.value.status_code == 500
        posts = [
            e
            for e in mock.journal
            if e.path == self._CREATE_ADDRESS_PATH and e.method == "POST"
        ]
        assert len(posts) == 1, "POST must not retry a 500 (side-effect safety)"

    def test_post_does_retry_503(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        # 503 (throttle, carries Retry-After semantics) IS retryable even for a
        # non-idempotent method → the 503 retries into the default 200.
        mock.push_scenario("relay-rest.create_address", 503, {"error": "x"})
        signalwire_client._http.post(
            self._CREATE_ADDRESS_PATH,
            body={"label": "x"},
            request_options=RequestOptions(retries=1, retry_backoff=0.0),
        )
        posts = [
            e
            for e in mock.journal
            if e.path == self._CREATE_ADDRESS_PATH and e.method == "POST"
        ]
        assert len(posts) == 2, "POST retries a 503 throttle (safe): 503 then 200"


class TestTimeout:
    """A server-side delay exceeding the timeout raises the transport error."""

    def test_slow_response_times_out(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        # Arm a 200 delayed 400ms; a 100ms timeout must fire → transport error.
        mock.push_scenario(
            _ADDRESSES_ENDPOINT_ID, 200, {"data": [], "links": {}}, delay_ms=400
        )
        with pytest.raises(SignalWireRestTransportError):
            _addresses(signalwire_client, RequestOptions(timeout=0.1))


class TestAbortSignal:
    """A set abort_signal raises before the request goes out."""

    def test_preset_abort_raises_transport_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        ev = threading.Event()
        ev.set()
        with pytest.raises(SignalWireRestTransportError):
            _addresses(signalwire_client, RequestOptions(abort_signal=ev))
        # Nothing reached the mock — cancelled before the send.
        gets = [
            e
            for e in mock.journal
            if e.path == "/api/fabric/addresses" and e.method == "GET"
        ]
        assert gets == [], "aborted request must not reach the server"


class TestPerRequestOverride:
    """Per-request options shallow-override the client default."""

    def test_per_request_retries_override_client_default(
        self, mock: _MockHarness
    ) -> None:
        from signalwire.rest.client import RestClient

        # Client default = no retries; per-request opts in to 1 retry.
        client = RestClient(
            project="p" * 34,
            token="t" * 34,
            host="127.0.0.1",
            request_options=RequestOptions(retries=0),
        )
        # Point it at the mock.
        client._http._base_url = mock.url
        # Auth-scope the scenario to this client.
        mock_scoped = mock  # unscoped harness; use shared bucket
        mock_scoped.push_scenario(
            _ADDRESSES_ENDPOINT_ID, 503, {"errors": [{"code": "X"}]}
        )
        result = client._http.get(
            "/api/fabric/addresses",
            request_options=RequestOptions(retries=1, retry_backoff=0.0),
        )
        assert result is not None
