"""Mock infrastructure and fixtures for REST client tests.

Two test backends coexist:

1. The legacy ``mock_session`` fixture — patches ``requests.Session`` and is
   used by the older REST tests (``test_namespaces.py``, ``test_calling.py``,
   etc.).  Each test there pre-stages the response on ``mock_session.request``.

2. The newer ``signalwire_client`` / ``mock`` fixtures — back the SDK with a
   real HTTP server provided by the ``mock_signalwire`` package
   (``porting-sdk/test_harness/mock_signalwire``).  The mock loads SignalWire's
   13 OpenAPI specs and synthesises schema-conformant responses.  Tests written
   against this fixture exercise the SDK's actual ``requests`` transport and
   then assert on both the parsed response body and a recorded request journal.

   Usage::

       def test_compat_calls_get(signalwire_client, mock):
           res = signalwire_client.compat.calls.get("CA_TEST_SID")
           assert "sid" in res
           j = mock.last_request()
           assert j.method == "GET"
           assert j.path.endswith("/Calls/CA_TEST_SID")

The two fixtures are independent — a test may use either, but not both at
once (no one ever needs both).
"""

from __future__ import annotations

import socket
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from signalwire.rest._base import HttpClient
from signalwire.rest.client import RestClient


# ---------------------------------------------------------------------------
# Adjacency-based discovery for porting-sdk mock packages.
#
# Contract: ``~/src/porting-sdk/`` must sit next to ``~/src/signalwire-python/``.
# That single layout is all the tests need to find the mock harness — no pip
# install of ``mock_signalwire`` / ``mock_relay`` is required.
#
# We walk this file's parents looking for ``../porting-sdk/test_harness/<name>/``
# and prepend it to ``sys.path`` so ``import mock_signalwire`` resolves. If the
# discovery fails we fall back to whatever is on ``sys.path`` (e.g. a prior
# editable install) and ultimately to the per-fixture skip.
# ---------------------------------------------------------------------------


def _discover_mock_package(name: str) -> bool:
    """Walk up from this file looking for ``../porting-sdk/test_harness/<name>/``.

    Returns True when a sibling ``porting-sdk`` clone is found and the package
    root has been prepended to ``sys.path``. Idempotent — multiple calls don't
    duplicate ``sys.path`` entries.
    """
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        candidate = parent.parent / "porting-sdk" / "test_harness" / name
        if (candidate / name / "__init__.py").is_file():
            entry = str(candidate)
            if entry not in sys.path:
                sys.path.insert(0, entry)
            return True
    return False


# Try the relative-path discovery first; this works in fresh adjacent clones
# without any prior pip install.
_MOCK_AVAILABLE = _discover_mock_package("mock_signalwire")
_RELAY_MOCK_AVAILABLE = _discover_mock_package("mock_relay")

try:
    from mock_signalwire import MockServer  # type: ignore
    _MOCK_AVAILABLE = True
except ImportError:  # pragma: no cover - env without porting-sdk available
    MockServer = None  # type: ignore
    _MOCK_AVAILABLE = False


class MockResponse:
    """Simulates a requests.Response — used by the legacy ``mock_session`` fixture."""

    def __init__(self, status_code=200, json_data=None, content=b"ok"):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.content = content
        self.ok = 200 <= status_code < 300
        self.text = str(json_data)

    def json(self):
        return self._json


@pytest.fixture
def mock_session():
    """Patches requests.Session and returns the mock session instance."""
    with patch("signalwire.rest._base.requests.Session") as MockSession:
        session = MagicMock()
        MockSession.return_value = session
        # Default: return 200 with empty dict
        session.request.return_value = MockResponse(200, {})
        yield session


@pytest.fixture
def http(mock_session):
    """An HttpClient backed by a mock session."""
    return HttpClient("test-project-id", "test-token", "test.signalwire.com")


@pytest.fixture
def client(mock_session):
    """A RestClient backed by a mock session."""
    return RestClient(
        project="test-project-id",
        token="test-token",
        host="test.signalwire.com",
    )


# ---------------------------------------------------------------------------
# Real mock-server fixtures (mock_signalwire package)
# ---------------------------------------------------------------------------


def _free_port() -> int:
    """Pick an unused localhost TCP port for the mock server."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@dataclass
class _JournalEntry:
    """Lightweight view of a single request the mock server recorded.

    Mirrors the dataclass in mock_signalwire.journal but is decoupled from
    the upstream type so this conftest doesn't import internal modules.
    """

    method: str
    path: str
    query_params: dict[str, list[str]]
    headers: dict[str, str]
    body: Any
    matched_route: str | None
    response_status: int | None


class _MockHarness:
    """Convenience wrapper around the running ``MockServer`` for tests.

    Keeps the journal/scenario plumbing reachable without leaking the
    underlying Starlette/uvicorn types.
    """

    def __init__(self, server: "MockServer") -> None:  # type: ignore[name-defined]
        self._server = server

    @property
    def url(self) -> str:
        return self._server.url

    @property
    def port(self) -> int:
        return self._server.port

    @property
    def journal(self) -> list[_JournalEntry]:
        """Return all recorded entries in arrival order."""
        raw = self._server.app.state.mock_state.journal.all()
        return [
            _JournalEntry(
                method=e.method,
                path=e.path,
                query_params=e.query_params,
                headers=e.headers,
                body=e.body,
                matched_route=e.matched_route,
                response_status=e.response_status,
            )
            for e in raw
        ]

    def last_request(self) -> _JournalEntry:
        """Return the most recent journal entry. Raises if empty."""
        entries = self.journal
        if not entries:
            raise AssertionError("mock journal is empty - no request was recorded")
        return entries[-1]

    def reset(self) -> None:
        """Clear journal + scenarios. Called automatically between tests."""
        self._server.app.state.mock_state.journal.reset()
        self._server.app.state.mock_state.scenarios.reset()


@pytest.fixture(scope="session")
def _mock_server_instance():
    """Boot one real mock server for the whole test session."""
    if not _MOCK_AVAILABLE:
        pytest.skip(
            "mock_signalwire package not found - clone porting-sdk adjacent "
            "to this repo so tests can find porting-sdk/test_harness/mock_signalwire/"
        )
    server = MockServer(host="127.0.0.1", port=_free_port(), log_level="error").start()
    try:
        yield server
    finally:
        server.stop()


@pytest.fixture
def mock(_mock_server_instance):
    """Test-facing harness around the mock server.

    Starts empty (journal + scenarios) before every test.
    """
    harness = _MockHarness(_mock_server_instance)
    harness.reset()
    yield harness


@pytest.fixture
def signalwire_client(mock, monkeypatch):
    """A real ``RestClient`` whose HTTP transport hits the local mock.

    Patches ``HttpClient.__init__`` to overwrite the ``_base_url`` field
    immediately after the client is built so the connection hits
    ``http://127.0.0.1:<port>`` rather than ``https://<host>``.  The yield
    expression is a bare ``RestClient(...)`` constructor call so the static
    coverage audit (porting-sdk/scripts/audit_python_test_coverage.py)
    resolves ``signalwire_client`` to the ``RestClient`` class.
    """
    original_init = HttpClient.__init__

    def _patched_init(self, project, token, host):
        original_init(self, project, token, host)
        self._base_url = mock.url

    monkeypatch.setattr(HttpClient, "__init__", _patched_init)

    yield RestClient(
        project="test_proj",
        token="test_tok",
        host=f"127.0.0.1:{mock.port}",
    )
