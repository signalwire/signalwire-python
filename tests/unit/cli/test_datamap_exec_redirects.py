"""
The DataMap simulator follows redirects as the platform does.

It sends every request, redirects included, through the session that refuses
private and internal addresses; it checked only the first URL, so a webhook
that redirected to one reached it. And like the platform, it sends a POST
again, with its body, after a redirect, where it used to send a GET.
"""

import http.client
import ipaddress
import json
import socket
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest

import requests
from requests.adapters import BaseAdapter

from signalwire.cli.execution.datamap_exec import execute_datamap_function
from signalwire.utils.url_validator import _PublicSession

PUBLIC_ADDRESS = "93.184.216.34"


class Scripted(BaseAdapter):
    """Answers each URL from a script, and records what was sent."""

    def __init__(self, routes: dict[str, tuple[int, dict[str, str], str]]) -> None:
        super().__init__()
        self.routes = routes
        self.sent: list[requests.PreparedRequest] = []

    def send(
        self,
        request: requests.PreparedRequest,
        stream: bool = False,
        timeout: float | tuple[float | None, float | None] | None = None,
        verify: bool | str = True,
        cert: str | tuple[str, str] | None = None,
        proxies: dict[str, str] | None = None,
    ) -> requests.Response:
        self.sent.append(request)
        status, headers, body = self.routes[request.url or ""]
        response = requests.Response()
        response.status_code = status
        response.headers.update(headers)
        if "Set-Cookie" in headers:
            # Where Requests reads a response's cookies from
            message = http.client.HTTPMessage()
            message["Set-Cookie"] = headers["Set-Cookie"]
            response.raw = SimpleNamespace(_original_response=SimpleNamespace(msg=message))
        response._content = body.encode()
        response.url = request.url or ""
        response.request = request
        return response

    def close(self) -> None:
        pass


@contextmanager
def _scripted(routes: dict[str, tuple[int, dict[str, str], str]]) -> Iterator[Scripted]:
    """The simulator's session answers from ``routes``; hostnames resolve publicly."""
    adapter = Scripted(routes)
    original_init = _PublicSession.__init__

    def init(self: _PublicSession, allow_private: bool = False) -> None:
        original_init(self, allow_private)
        self.mount("http://", adapter)
        self.mount("https://", adapter)

    def resolve(host: str, *args: Any, **kwargs: Any) -> list[Any]:
        # An address resolves to itself; any name, to a public address
        try:
            address = str(ipaddress.ip_address(host))
        except ValueError:
            address = PUBLIC_ADDRESS
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 0))]

    with patch.object(_PublicSession, "__init__", init), \
         patch("signalwire.utils.url_validator.socket.getaddrinfo", resolve):
        yield adapter


def _function(webhook: dict[str, Any]) -> dict[str, Any]:
    return {
        "function": "lookup",
        "data_map": {"webhooks": [webhook], "output": {"response": "The lookup failed."}},
    }


def test_a_post_is_sent_again_with_its_body_after_a_redirect() -> None:
    routes = {
        "https://api.example.com/w": (302, {"Location": "/final"}, ""),
        "https://api.example.com/final": (200, {}, json.dumps({"answer": "yes"})),
    }
    webhook = {
        "url": "https://api.example.com/w",
        "method": "POST",
        "params": {"q": "${args.q}"},
        "output": {"response": "Answer: ${answer}"},
    }
    with _scripted(routes) as adapter:
        result = execute_datamap_function(_function(webhook), {"q": "hours"})
    assert result == {"response": "Answer: yes"}
    assert [request.method for request in adapter.sent] == ["POST", "POST"]
    body = adapter.sent[1].body
    assert isinstance(body, (str, bytes))
    assert json.loads(body) == {"q": "hours"}


def test_a_redirect_to_a_private_address_is_refused() -> None:
    routes = {
        "https://api.example.com/w": (302, {"Location": "http://127.0.0.1:8000/private"}, ""),
        "http://127.0.0.1:8000/private": (200, {}, json.dumps({"answer": "internal"})),
    }
    webhook = {"url": "https://api.example.com/w", "method": "GET",
               "output": {"response": "Answer: ${answer}"}}
    with _scripted(routes) as adapter:
        result = execute_datamap_function(_function(webhook), {})
    assert result == {"response": "The lookup failed."}
    assert [request.url for request in adapter.sent] == ["https://api.example.com/w"]


def test_credentials_stay_with_their_host() -> None:
    routes = {
        "https://api.example.com/w": (302, {"Location": "https://other.example.com/x"}, ""),
        "https://other.example.com/x": (200, {}, json.dumps({"answer": "moved"})),
    }
    webhook = {"url": "https://api.example.com/w", "method": "GET",
               "headers": {"Authorization": "Bearer secret-key"},
               "output": {"response": "Answer: ${answer}"}}
    with _scripted(routes) as adapter:
        result = execute_datamap_function(_function(webhook), {})
    assert result == {"response": "Answer: moved"}
    assert adapter.sent[0].headers["Authorization"] == "Bearer secret-key"
    assert "Authorization" not in adapter.sent[1].headers


def test_credentials_arent_sent_over_a_redirect_to_plain_http() -> None:
    routes = {
        "https://api.example.com/w": (302, {"Location": "http://api.example.com/final"}, ""),
        "http://api.example.com/final": (200, {}, json.dumps({"answer": "downgraded"})),
    }
    webhook = {"url": "https://user:pass@api.example.com/w", "method": "GET",
               "headers": {"Authorization": "Bearer secret-key", "Cookie": "session=1"},
               "output": {"response": "Answer: ${answer}"}}
    with _scripted(routes) as adapter:
        result = execute_datamap_function(_function(webhook), {})
    assert result == {"response": "Answer: downgraded"}
    assert "Authorization" not in adapter.sent[1].headers
    assert "Cookie" not in adapter.sent[1].headers


def test_the_same_origin_written_differently_keeps_its_credentials() -> None:
    routes = {
        "https://api.example.com/w": (302, {"Location": "https://API.example.com:443/final"}, ""),
        "https://api.example.com:443/final": (200, {}, json.dumps({"answer": "same"})),
        "https://api.example.com/final": (200, {}, json.dumps({"answer": "same"})),
    }
    webhook = {"url": "https://api.example.com/w", "method": "GET",
               "headers": {"Authorization": "Bearer secret-key"},
               "output": {"response": "Answer: ${answer}"}}
    with _scripted(routes) as adapter:
        result = execute_datamap_function(_function(webhook), {})
    assert result == {"response": "Answer: same"}
    assert adapter.sent[1].headers["Authorization"] == "Bearer secret-key"


def test_netrc_and_response_cookies_add_no_credentials(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The platform reads no .netrc and keeps no cookie jar
    netrc = tmp_path / "netrc"
    netrc.write_text("machine api.example.com login user password secret\n")
    netrc.chmod(0o600)
    monkeypatch.setenv("NETRC", str(netrc))
    routes = {
        "https://api.example.com/w": (
            302, {"Location": "http://api.example.com/final", "Set-Cookie": "sid=abc; Path=/"}, ""),
        "http://api.example.com/final": (200, {}, json.dumps({"answer": "plain"})),
    }
    webhook = {"url": "https://api.example.com/w", "method": "GET",
               "output": {"response": "Answer: ${answer}"}}
    with _scripted(routes) as adapter:
        result = execute_datamap_function(_function(webhook), {})
    assert result == {"response": "Answer: plain"}
    for request in adapter.sent:
        assert "Authorization" not in request.headers
        assert "Cookie" not in request.headers
