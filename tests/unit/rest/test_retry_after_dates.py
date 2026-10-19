"""Retry-After parsing exercised through real local HTTP responses."""

import uuid
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import ClassVar

import pytest

from signalwire.rest import RequestOptions, RestClient
from signalwire.rest._base import HttpClient


class _RetryHandler(BaseHTTPRequestHandler):
    retry_after: ClassVar[str | None] = None
    attempts: ClassVar[int] = 0
    host: ClassVar[str] = ""

    def do_GET(self) -> None:
        self.rfile.read(int(self.headers.get("Content-Length", "0")))
        type(self).attempts += 1
        self.send_response(503 if self.attempts == 1 else 200)
        if self.attempts == 1 and self.retry_after is not None:
            self.send_header("Retry-After", self.retry_after)
        self.send_header("Content-Type", "application/json")
        payload = (
            b'{"name": "retry-test"}' if self.command == "POST" else b'{"data": []}'
        )
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    do_POST = do_GET

    def log_message(self, format: str, *args: object) -> None:
        pass


@pytest.fixture
def retry_server() -> Iterator[type[_RetryHandler]]:
    class Handler(_RetryHandler):
        pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    Handler.host = f"127.0.0.1:{server.server_port}"
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield Handler
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize(
    ("header", "expected_delay"),
    [
        ("Wed, 21 Oct 2015 07:28:30 GMT", 30.0),
        ("Wed, 21 Oct 2015 07:27:00 GMT", 0.0),
        ("30", 30.0),
        ("0", 0.0),
        ("not-a-date", 0.25),
        (None, 0.25),
        ("inf", 0.25),
        ("nan", 0.25),
        ("-1", 0.25),
    ],
)
def test_retry_after_over_http(
    retry_server: type[_RetryHandler],
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    header: str | None,
    expected_delay: float,
) -> None:
    # 2015-10-21 07:28:00 UTC. Freeze only the clock used by date conversion.
    monkeypatch.setattr("signalwire.rest._base.time.time", lambda: 1445412480.0)
    retry_server.retry_after = header
    delays: list[float] = []
    monkeypatch.setattr(
        HttpClient, "_sleep", lambda self, seconds: delays.append(seconds)
    )
    client = RestClient(project="test", token=uuid.uuid4().hex, host=retry_server.host)
    options = RequestOptions(retries=1, retry_backoff=0.25)
    try:
        # Use public resource operations and the real requests HTTP transport.
        if method == "GET":
            assert client.fabric.addresses.list(request_options=options) == {"data": []}
        else:
            room = client.video.rooms.create(name="retry-test", request_options=options)
            assert room["name"] == "retry-test"
        assert retry_server.attempts == 2
        assert delays == [expected_delay]
    finally:
        client._http._session.close()
