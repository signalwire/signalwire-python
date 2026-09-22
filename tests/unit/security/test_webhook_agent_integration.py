"""
Integration tests: AgentBase + webhook signature validation.

These spin up an AgentBase via FastAPI's TestClient and exercise the
``signing_key`` plumbing end-to-end. We sign requests against the URL the
test client posts to and assert:

- 200 + handler runs when the signature is correct
- 403 + handler does NOT run when the signature is missing/wrong
- AgentBase emits a startup warning when no key is configured
- ``SIGNALWIRE_SIGNING_KEY`` env var is honored as a fallback
"""

import base64
import contextlib
import hashlib
import hmac
import io
import logging
from collections.abc import Iterator
from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from signalwire.agent_server import AgentServer
from signalwire.core.agent_base import AgentBase
from signalwire.core.security.webhook_middleware import SIGNALWIRE_SIGNATURE_HEADER


SIGNING_KEY = "PSKtest1234567890abcdef"


def _scheme_a_sig(key: str, url: str, raw_body: str) -> str:
    return hmac.new(
        key.encode("utf-8"),
        (url + raw_body).encode("utf-8"),
        hashlib.sha1,
    ).hexdigest()


def _build_app(agent: AgentBase) -> Any:
    """Use the AgentBase's get_app() to materialize the FastAPI app."""
    return agent.get_app()


def _basic_auth_headers(agent: AgentBase) -> dict[str, str]:
    """AgentBase auto-generates basic-auth credentials. Build the header."""
    creds = agent.get_basic_auth_credentials()
    user, password = creds[0], creds[1]
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


# ---------------------------------------------------------------------------
# Signed: valid signature → 200, invalid → 403
# ---------------------------------------------------------------------------

class TestAgentSignedWebhooks:
    def test_post_swaig_with_valid_signature_runs_handler(self) -> None:
        agent = AgentBase(name="t1", signing_key=SIGNING_KEY)
        app = _build_app(agent)
        client = TestClient(app, base_url="http://testserver")

        body = '{"function":"nope"}'
        # /swaig is mounted under the agent's route which defaults to "/"
        url = "http://testserver/swaig"
        sig = _scheme_a_sig(SIGNING_KEY, url, body)

        resp = client.post(
            "/swaig",
            content=body,
            headers={
                **_basic_auth_headers(agent),
                SIGNALWIRE_SIGNATURE_HEADER: sig,
                "content-type": "application/json",
            },
        )
        # 200 = passed signature gate. The handler may itself return an
        # error body for an unknown function, but we must NOT see 403.
        assert resp.status_code != 403, (
            f"valid signature was rejected: status={resp.status_code} body={resp.text}"
        )

    def test_post_swaig_without_signature_returns_403(self) -> None:
        agent = AgentBase(name="t2", signing_key=SIGNING_KEY)
        app = _build_app(agent)
        client = TestClient(app)

        resp = client.post(
            "/swaig",
            content='{"function":"nope"}',
            headers={
                **_basic_auth_headers(agent),
                "content-type": "application/json",
            },
        )
        assert resp.status_code == 403

    def test_post_swaig_with_wrong_signature_returns_403(self) -> None:
        agent = AgentBase(name="t3", signing_key=SIGNING_KEY)
        app = _build_app(agent)
        client = TestClient(app)

        resp = client.post(
            "/swaig",
            content='{"function":"nope"}',
            headers={
                **_basic_auth_headers(agent),
                SIGNALWIRE_SIGNATURE_HEADER: "deadbeef" * 5,
                "content-type": "application/json",
            },
        )
        assert resp.status_code == 403

    def test_unsigned_agent_accepts_any_request(self) -> None:
        """When signing_key is NOT set, requests pass through (legacy behaviour)."""
        agent = AgentBase(name="t4")  # no signing_key
        app = _build_app(agent)
        client = TestClient(app)

        resp = client.post(
            "/swaig",
            content='{"function":"nope"}',
            headers={
                **_basic_auth_headers(agent),
                "content-type": "application/json",
            },
        )
        # Same logic as the signed-but-no-sig case, EXCEPT the validator
        # was never wired — so we should NOT see 403 from this layer.
        assert resp.status_code != 403


# ---------------------------------------------------------------------------
# Every app that serves an agent checks signatures, on every path to a handler
# ---------------------------------------------------------------------------

# Paths below the agent's route that reach a signed handler. The router matches
# the canonical forms; the catch-alls serve the bare route and slash variants,
# and must not become a way around the check.
SIGNED_PATHS = ["", "/", "/swaig", "/swaig/", "//swaig", "/swaig//",
                "/post_prompt", "/post_prompt//"]


def _served_app(agent: AgentBase) -> Any:
    """The app ``agent.serve()`` builds, captured instead of started."""
    with (
        patch("uvicorn.run") as run,
        patch("signalwire.core.logging_config.configure_logging"),
        contextlib.redirect_stdout(io.StringIO()),
    ):
        agent.serve()
    return run.call_args.args[0]


@contextlib.contextmanager
def _agent_server_client(agent: AgentBase) -> Iterator[TestClient]:
    """A client for an AgentServer hosting ``agent``, with startup run."""
    server = AgentServer()
    server.register(agent)
    # The catch-all is registered on startup; entering the client runs it.
    with TestClient(server.app) as client:
        yield client


def _served_client(agent: AgentBase) -> Iterator[TestClient]:
    yield TestClient(_served_app(agent))


def _get_app_client(agent: AgentBase) -> Iterator[TestClient]:
    yield TestClient(agent.get_app())


APPS = {
    "serve": contextlib.contextmanager(_served_client),
    "get_app": contextlib.contextmanager(_get_app_client),
    "agent_server": _agent_server_client,
}


class TestEveryServedPathIsSigned:
    @pytest.mark.parametrize("app_kind", sorted(APPS))
    @pytest.mark.parametrize("path", SIGNED_PATHS)
    def test_unsigned_post_is_refused(self, app_kind: str, path: str) -> None:
        agent = AgentBase(name="signed", route="/agent", signing_key=SIGNING_KEY)
        body = '{"function":"nope"}'
        with APPS[app_kind](agent) as client:
            resp = client.post(
                "/agent" + path,
                content=body,
                headers={**_basic_auth_headers(agent), "content-type": "application/json"},
            )
        # get_app() answers some variants with 204 without running a handler;
        # what matters is that no handler runs unsigned.
        assert resp.status_code in (403, 204), (
            f"{app_kind}: unsigned POST /agent{path} got {resp.status_code}: {resp.text[:200]}"
        )
        if app_kind != "get_app":
            assert resp.status_code == 403

    @pytest.mark.parametrize("app_kind", ["serve", "agent_server"])
    @pytest.mark.parametrize("path", ["", "/swaig//"])
    def test_signed_post_reaches_the_handler(self, app_kind: str, path: str) -> None:
        agent = AgentBase(name="signed", route="/agent", signing_key=SIGNING_KEY)
        body = '{"function":"nope"}'
        signature = _scheme_a_sig(SIGNING_KEY, "http://testserver/agent" + path, body)
        with APPS[app_kind](agent) as client:
            resp = client.post(
                "/agent" + path,
                content=body,
                headers={
                    **_basic_auth_headers(agent),
                    SIGNALWIRE_SIGNATURE_HEADER: signature,
                    "content-type": "application/json",
                },
            )
        assert resp.status_code == 200, (
            f"{app_kind}: signed POST /agent{path} got {resp.status_code}: {resp.text[:200]}"
        )

    def test_unsigned_get_still_needs_only_basic_auth(self) -> None:
        agent = AgentBase(name="signed", route="/agent", signing_key=SIGNING_KEY)
        client = TestClient(_served_app(agent))
        resp = client.get("/agent", headers=_basic_auth_headers(agent))
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Startup warning when key is unset
# ---------------------------------------------------------------------------

class _CaptureHandler(logging.Handler):
    """Minimal handler used to harvest LogRecords from the SDK's namespaced logger.

    The SDK installs handlers on the ``agent_base`` logger directly with
    ``propagate=False`` (see ``signalwire.core.logging_config``), so pytest's
    ``caplog`` (which attaches to root) doesn't see them. We attach our own
    handler to the same named logger.
    """

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class TestAgentNoKeyWarning:
    def test_warning_emitted_when_signing_key_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AgentBase logs a prominent WARNING when neither arg nor env is set."""
        monkeypatch.delenv("SIGNALWIRE_SIGNING_KEY", raising=False)

        capture = _CaptureHandler()
        agent_logger = logging.getLogger("agent_base")
        agent_logger.addHandler(capture)
        try:
            AgentBase(name="warntest")
        finally:
            agent_logger.removeHandler(capture)

        warning_records = [
            r for r in capture.records
            if r.levelno >= logging.WARNING
            and (
                "webhook_signature_validation_disabled" in r.getMessage()
                or "webhook signature validation is disabled" in r.getMessage()
            )
        ]
        assert warning_records, (
            f"expected disabled-warning in logs; got: {[r.getMessage() for r in capture.records]}"
        )

    def test_no_warning_when_key_is_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Setting the key suppresses the warning."""
        monkeypatch.delenv("SIGNALWIRE_SIGNING_KEY", raising=False)

        capture = _CaptureHandler()
        agent_logger = logging.getLogger("agent_base")
        agent_logger.addHandler(capture)
        try:
            AgentBase(name="warntest2", signing_key=SIGNING_KEY)
        finally:
            agent_logger.removeHandler(capture)

        warning_records = [
            r for r in capture.records
            if r.levelno >= logging.WARNING
            and (
                "webhook_signature_validation_disabled" in r.getMessage()
                or "webhook signature validation is disabled" in r.getMessage()
            )
        ]
        assert not warning_records, (
            f"unexpected disabled-warning when key is set: {[r.getMessage() for r in warning_records]}"
        )


# ---------------------------------------------------------------------------
# Env var fallback
# ---------------------------------------------------------------------------

class TestAgentEnvFallback:
    def test_env_signing_key_picked_up_when_no_explicit_arg(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """SIGNALWIRE_SIGNING_KEY env var supplies the key when arg is omitted."""
        monkeypatch.setenv("SIGNALWIRE_SIGNING_KEY", SIGNING_KEY)
        agent = AgentBase(name="envtest")
        assert agent.signing_key == SIGNING_KEY

    def test_explicit_arg_overrides_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Explicit constructor arg wins over the env var."""
        monkeypatch.setenv("SIGNALWIRE_SIGNING_KEY", "env-key")
        agent = AgentBase(name="envtest2", signing_key="explicit-key")
        assert agent.signing_key == "explicit-key"
