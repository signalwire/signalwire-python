"""
Tests for ``_PublicSession``, the Requests session that skills use to fetch
user-supplied URLs.

Checking a URL with ``validate_url()`` before fetching it isn't enough on its
own. The server can redirect to an internal address, and the hostname can
resolve differently when the connection is made (DNS rebinding). The session
checks every request it sends, redirects included, and every direct
connection it makes.
"""

import http.server
import threading
from collections.abc import Iterator
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests
from urllib3.connection import HTTPConnection

from signalwire.utils.url_validator import (
    _BlockedAddressError,
    _PublicHTTPConnection,
    _PublicHTTPSConnection,
    _PublicSession,
)

PUBLIC_IP = "93.184.216.34"  # what public_test_dns resolves public.test to
METADATA_URL = "http://169.254.169.254/latest/meta-data/"


@pytest.fixture(autouse=True)
def _no_private_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SWML_ALLOW_PRIVATE_URLS", raising=False)


@pytest.fixture
def loopback_server() -> Iterator[tuple[int, list[str]]]:
    """An HTTP server on 127.0.0.1 standing in for an internal service."""
    hits: list[str] = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            hits.append(self.path)
            body = b"internal-secret"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1], hits
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.usefixtures("public_test_dns")
class TestRedirects:
    def test_redirect_to_metadata_address_is_refused(self, scripted_adapter: type) -> None:
        session = _PublicSession()
        adapter = scripted_adapter(
            {"http://public.test/start": (302, {"Location": METADATA_URL}, b"")}
        )
        session.mount("http://public.test", adapter)
        with pytest.raises(requests.exceptions.InvalidURL):
            session.get("http://public.test/start", timeout=5)
        assert adapter.sent == ["http://public.test/start"]

    def test_redirect_to_public_address_is_followed(self, scripted_adapter: type) -> None:
        session = _PublicSession()
        adapter = scripted_adapter(
            {
                "http://public.test/start": (302, {"Location": "/final"}, b""),
                "http://public.test/final": (200, {}, b"ok"),
            }
        )
        session.mount("http://public.test", adapter)
        response = session.get("http://public.test/start", timeout=5)
        assert response.text == "ok"
        assert adapter.sent == ["http://public.test/start", "http://public.test/final"]

    def test_first_request_is_checked_too(self) -> None:
        with pytest.raises(requests.exceptions.InvalidURL):
            _PublicSession().get(METADATA_URL, timeout=5)

    def test_rejection_message_masks_credentials(self) -> None:
        with pytest.raises(requests.exceptions.InvalidURL) as info:
            _PublicSession().get("http://user:hunter2@10.0.0.5/", timeout=5)
        assert "hunter2" not in str(info.value)


class TestConnectionCheck:
    """A DNS answer that changes after the URL check still can't reach an internal address."""

    def test_connection_to_loopback_is_refused_when_url_check_passed(
        self, loopback_server: tuple[int, list[str]]
    ) -> None:
        port, hits = loopback_server
        session = _PublicSession()
        # The check before the request saw a public address; the connection
        # then reaches 127.0.0.1.
        with patch("signalwire.utils.url_validator.validate_url", return_value=True):
            with pytest.raises(requests.exceptions.ConnectionError) as info:
                session.get(f"http://127.0.0.1:{port}/", timeout=5)
        assert "private or internal address" in str(info.value)
        assert hits == []

    def test_environment_variable_allows_private_connections(
        self, loopback_server: tuple[int, list[str]], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        port, hits = loopback_server
        monkeypatch.setenv("SWML_ALLOW_PRIVATE_URLS", "true")
        response = _PublicSession().get(f"http://127.0.0.1:{port}/", timeout=5)
        assert response.text == "internal-secret"
        assert hits == ["/"]

    def test_allow_private_argument_allows_private_connections(
        self, loopback_server: tuple[int, list[str]]
    ) -> None:
        port, hits = loopback_server
        session = _PublicSession(allow_private=True)
        response = session.get(f"http://127.0.0.1:{port}/", timeout=5)
        assert response.text == "internal-secret"
        assert hits == ["/"]

    @pytest.mark.parametrize("cls", [_PublicHTTPConnection, _PublicHTTPSConnection])
    @pytest.mark.parametrize(
        "peer",
        [("10.0.0.7", 443), ("::ffff:169.254.169.254", 443, 0, 0), ("::", 443, 0, 0)],
    )
    def test_blocked_peer_closes_the_socket(
        self, cls: type[HTTPConnection], peer: tuple[Any, ...]
    ) -> None:
        sock = Mock()
        sock.getpeername.return_value = peer
        with patch.object(HTTPConnection, "_new_conn", return_value=sock):
            with pytest.raises(_BlockedAddressError):
                cls("public.test", 443)._new_conn()
        sock.close.assert_called_once()

    @pytest.mark.parametrize("cls", [_PublicHTTPConnection, _PublicHTTPSConnection])
    def test_public_peer_is_allowed(self, cls: type[HTTPConnection]) -> None:
        sock = Mock()
        sock.getpeername.return_value = (PUBLIC_IP, 443)
        with patch.object(HTTPConnection, "_new_conn", return_value=sock):
            assert cls("public.test", 443)._new_conn() is sock
        sock.close.assert_not_called()
