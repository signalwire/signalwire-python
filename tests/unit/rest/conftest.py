"""Mock infrastructure and fixtures for REST client tests.

Two test backends coexist:

1. The legacy ``mock_session`` fixture — patches ``requests.Session`` and is
   used by the transport-contract unit tests (``test_base.py``,
   ``test_calling.py``, ``test_client.py``, ``test_namespaces.py``,
   ``test_phone_numbers.py``, ``test_fabric.py``).  These mirror the frozen
   TypeScript reference's ``HttpClient.test.ts`` / ``calling.test.ts`` /
   ``phoneNumbers.test.ts`` / ``fabric.test.ts``, which keep a ``createMockFetch``
   transport double for the same plumbing-level coverage.  They mock the
   transport on purpose to assert the exact ``(method, url, json, params)`` the
   client builds for arbitrary paths the spec mock would 404.

2. The ``signalwire_client`` / ``mock`` fixtures — back the SDK with a real
   HTTP server provided by the ``mock_signalwire`` package
   (``porting-sdk/test_harness/mock_signalwire``).  The mock loads SignalWire's
   13 OpenAPI specs and synthesises schema-conformant responses.  Tests written
   against this fixture exercise the SDK's actual ``requests`` transport and
   then assert on both the parsed response body and a recorded request journal.

   This is the parity-grade backend and mirrors the frozen TypeScript reference
   harness ``tests/rest/mocktest.ts``: ONE shared mock server (probe-or-spawn,
   adjacency discovery), and a per-test ``MockHarness`` *view* scoped to that
   test's client so the whole REST suite is safe under ``pytest -n auto``.

   Isolation key (REST is pure request/response, no session handshake): each
   ``signalwire_client`` authenticates with a unique random token
   ``test_tok_<12 hex>`` (project stays the constant ``test_proj`` so the LAML
   ``Accounts/test_proj/...`` paths the compat tests assert on stay stable), so
   its ``Authorization: Basic base64(project:token)`` header is unique.  ``mock``
   filters the shared global journal by that header
   (lowercased ``authorization``); ``mock.reset()`` is a no-op for a scoped view
   (a fresh client already sees an empty filtered journal, and a global wipe
   would race a concurrent test); and ``mock.push_scenario(...)`` scopes the
   override to this client (``?session_id=<auth header>``) so a concurrent test
   can't consume it.

   Usage::

       def test_compat_calls_get(signalwire_client, mock):
           res = signalwire_client.compat.calls.get("CA_TEST_SID")
           assert "sid" in res
           j = mock.last_request()
           assert j.method == "GET"
           assert j.path.endswith("/Calls/CA_TEST_SID")

The two backends are independent — a test may use either, but not both at once.
"""

from __future__ import annotations

import atexit
import base64
import os
import socket
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch
from urllib.parse import quote

import pytest
import requests

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
# and return that directory so it can be prepended to ``sys.path`` /
# ``PYTHONPATH``.  This mirrors ``discoverPortingSdkPackage`` in the frozen
# TypeScript reference harness ``tests/rest/mocktest.ts``.  The walk ignores
# ``$PORTING_SDK`` deliberately — the filesystem layout is the source of truth.
# ---------------------------------------------------------------------------


def _discover_mock_package(name: str) -> str | None:
    """Walk up from this file looking for ``../porting-sdk/test_harness/<name>/``.

    Returns the package-root directory (the value to put on ``sys.path`` so
    ``import <name>`` / ``python -m <name>`` resolve), or ``None`` when no
    adjacent ``porting-sdk`` clone is reachable.  Idempotent on ``sys.path``.
    """
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        candidate = parent.parent / "porting-sdk" / "test_harness" / name
        if (candidate / name / "__init__.py").is_file():
            entry = str(candidate)
            if entry not in sys.path:
                sys.path.insert(0, entry)
            return entry
    return None


_MOCK_PKG_DIR = _discover_mock_package("mock_signalwire")
_MOCK_AVAILABLE = _MOCK_PKG_DIR is not None


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
# Shared mock-signalwire server — probe-or-spawn singleton (mirrors mocktest.ts)
#
# The mock's lifetime is per-process: the first time a test needs it we probe
# ``http://127.0.0.1:<port>/__mock__/health`` and either reuse a running server
# or spawn one as a detached subprocess.  Under ``pytest -n auto`` every xdist
# worker is a separate process; the FIRST worker to look spawns the shared
# server, the rest probe and reuse it.  Session isolation (below) is what makes
# that one shared server safe under concurrency — not a per-worker server.
# ---------------------------------------------------------------------------


_STARTUP_TIMEOUT_S = 30.0
_PROBE_TIMEOUT_S = 2.0
# Project stays constant so LAML ``Accounts/test_proj/...`` paths are stable;
# per-test isolation comes from a unique random token (below).
_REST_PROJECT = "test_proj"


def _pick_free_port() -> int:
    """Ask the OS for a free TCP port on the loopback (bind to :0).

    Fails LOUD (raises) rather than falling back to a hardcoded port: a
    silent collision on a fixed port is exactly the self-inflicted hang
    this replaces.  The singleton picks once per session, so the brief
    bind/close race between picking and the mock subprocess re-binding the
    same port is acceptable (loopback, single host, one pick per process).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    finally:
        s.close()
    if not port:
        raise RuntimeError("failed to acquire a free port for mock_signalwire")
    return port


def _resolve_port() -> int:
    """Port for the shared mock server.

    Escape hatch: ``MOCK_SIGNALWIRE_PORT`` (set+valid) wins so the CI gate
    can pin every test to one journal.  When unset, pick a FREE port
    dynamically (never a hardcoded default that can collide with a stale
    listener and hang the suite).
    """
    raw = os.environ.get("MOCK_SIGNALWIRE_PORT")
    if raw:
        try:
            p = int(raw)
            if p > 0:
                return p
        except ValueError:
            pass
    return _pick_free_port()


def _probe_health(base_url: str) -> bool:
    try:
        resp = requests.get(f"{base_url}/__mock__/health", timeout=_PROBE_TIMEOUT_S)
        if resp.status_code != 200:
            return False
        return "specs_loaded" in resp.json()
    except Exception:
        return False


class _SharedServer:
    """Process-wide handle to the one shared mock_signalwire server."""

    def __init__(self) -> None:
        self.url: str | None = None
        self.port: int | None = None
        self._child: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._error: str | None = None

    def ensure(self) -> _SharedServer:
        with self._lock:
            if self.url is not None:
                return self
            if self._error is not None:
                pytest.skip(self._error)

            port = _resolve_port()
            url = f"http://127.0.0.1:{port}"

            if _probe_health(url):
                self.url, self.port = url, port
                return self

            if not _MOCK_AVAILABLE:
                self._error = (
                    "mock_signalwire package not found - clone porting-sdk "
                    "adjacent to this repo so tests can find "
                    "porting-sdk/test_harness/mock_signalwire/"
                )
                pytest.skip(self._error)

            child_env = dict(os.environ)
            if _MOCK_PKG_DIR:
                existing = child_env.get("PYTHONPATH", "")
                child_env["PYTHONPATH"] = (
                    f"{_MOCK_PKG_DIR}{os.pathsep}{existing}" if existing else _MOCK_PKG_DIR
                )
            self._child = subprocess.Popen(
                [
                    sys.executable, "-m", "mock_signalwire",
                    "--host", "127.0.0.1",
                    "--port", str(port),
                    "--log-level", "error",
                ],
                env=child_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            atexit.register(self._terminate)

            deadline = time.time() + _STARTUP_TIMEOUT_S
            while time.time() < deadline:
                if _probe_health(url):
                    self.url, self.port = url, port
                    return self
                # Another worker may have won the spawn race; either way the
                # probe above will succeed once *some* server is up.
                time.sleep(0.1)

            self._terminate()
            self._error = (
                f"mock_signalwire did not become ready within {_STARTUP_TIMEOUT_S}s "
                f"on port {port} (clone porting-sdk next to signalwire-python, or "
                f"set MOCK_SIGNALWIRE_PORT to a pre-running instance)"
            )
            pytest.skip(self._error)

    def _terminate(self) -> None:
        child = self._child
        self._child = None
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except Exception:
                child.kill()


_SHARED = _SharedServer()


@dataclass
class _JournalEntry:
    """Lightweight view of a single request the mock server recorded."""

    method: str
    path: str
    query_params: dict[str, list[str]]
    headers: dict[str, str]
    body: Any
    matched_route: str | None
    response_status: int | None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> _JournalEntry:
        return cls(
            method=str(d.get("method", "")),
            path=str(d.get("path", "")),
            query_params=d.get("query_params") or {},
            headers=d.get("headers") or {},
            body=d.get("body"),
            matched_route=d.get("matched_route"),
            response_status=d.get("response_status"),
        )


class _MockHarness:
    """Per-test view of the shared ``mock_signalwire`` server.

    Scoped to ONE client's ``Authorization`` header so concurrent tests against
    the shared server never see each other's requests.  Mirrors ``MockHarness``
    in the frozen TypeScript reference ``tests/rest/mocktest.ts``.
    """

    def __init__(self, url: str, port: int) -> None:
        self.url = url
        self.port = port
        # The unique random project this view's client authenticates with
        # (``test_proj_<hex>``).  Empty on an unscoped/raw harness.
        self.project = ""
        # ``Authorization: Basic ...`` of this view's client (lowercased match
        # key for the journal filter).  Empty => unscoped (legacy global view).
        self.auth_header = ""

    def _raw_journal(self) -> list[_JournalEntry]:
        resp = requests.get(f"{self.url}/__mock__/journal", timeout=5)
        resp.raise_for_status()
        return [_JournalEntry.from_dict(d) for d in resp.json()]

    @property
    def journal(self) -> list[_JournalEntry]:
        """This client's recorded requests in arrival order.

        Scoped to this harness's ``auth_header`` when set (so a parallel test
        never sees another test's requests); an unscoped harness sees the whole
        journal.
        """
        entries = self._raw_journal()
        if not self.auth_header:
            return entries
        return [e for e in entries if e.headers.get("authorization") == self.auth_header]

    def last_request(self) -> _JournalEntry:
        """Most recent journal entry for THIS client.  Raises if empty."""
        entries = self.journal
        if not entries:
            raise AssertionError(
                "mock journal is empty - no request was recorded for this client"
            )
        return entries[-1]

    def reset(self) -> None:
        """No-op for a scoped view.

        A scoped harness reads only its own entries (by auth header), so there
        is nothing to clear and a global wipe would race a concurrent test.  A
        fresh per-test client already starts with an empty filtered journal.
        Unscoped harnesses do the legacy global reset.
        """
        if self.auth_header:
            return
        requests.post(f"{self.url}/__mock__/journal/reset", timeout=5)
        requests.post(f"{self.url}/__mock__/scenarios/reset", timeout=5)

    def push_scenario(self, endpoint_id: str, status: int, response: Any) -> None:
        """Stage a consume-once response override for ``endpoint_id``.

        Scoped to THIS client's auth header (REST's session key is the
        ``Authorization`` header), so a concurrent test can't consume the
        override and a stale one can't bleed across tests.
        """
        url = f"{self.url}/__mock__/scenarios/{endpoint_id}"
        if self.auth_header:
            url = f"{url}?session_id={quote(self.auth_header, safe='')}"
        resp = requests.post(url, json={"status": status, "response": response}, timeout=5)
        resp.raise_for_status()


@pytest.fixture
def mock():
    """Test-facing harness around the shared mock server (unscoped view).

    Most tests use the scoped view via ``signalwire_client`` instead; this bare
    fixture is the underlying handle (the ``signalwire_client`` fixture scopes
    its returned ``mock`` to the client's auth header).
    """
    shared = _SHARED.ensure()
    return _MockHarness(shared.url, shared.port)


@pytest.fixture
def signalwire_client(mock, monkeypatch):
    """A real ``RestClient`` whose HTTP transport hits the shared mock.

    Each client authenticates with the constant project ``test_proj`` and a
    unique random token (``test_tok_<12 hex>``), so its Basic-Auth header is
    unique while the LAML ``Accounts/test_proj/...`` paths stay stable.  The
    ``mock`` fixture handed to the same test is scoped to that header, so the
    test reads only its own journal entries — making the shared mock safe under
    ``pytest -n auto`` with no SDK change and no mock-server change.  Random
    (not a counter) so concurrent xdist workers can't collide on the same token.

    Patches ``HttpClient.__init__`` to overwrite ``_base_url`` immediately after
    the client is built so the connection hits ``http://127.0.0.1:<port>``
    rather than ``https://<host>`` (the SDK always prepends ``https://``; this
    only rewrites the URL, exactly like the frozen TS reference passes an
    ``http://`` host).  The yield expression is a bare ``RestClient(...)``
    constructor call so the static coverage audit resolves ``signalwire_client``
    to the ``RestClient`` class.
    """
    token = f"test_tok_{uuid.uuid4().hex[:12]}"
    auth_header = "Basic " + base64.b64encode(
        f"{_REST_PROJECT}:{token}".encode()
    ).decode()

    # Scope the harness view to this client's auth header.
    mock.project = _REST_PROJECT
    mock.auth_header = auth_header

    original_init = HttpClient.__init__

    def _patched_init(self, project, token, host):
        original_init(self, project, token, host)
        self._base_url = mock.url

    monkeypatch.setattr(HttpClient, "__init__", _patched_init)

    yield RestClient(
        project=_REST_PROJECT,
        token=token,
        host=f"127.0.0.1:{mock.port}",
    )
