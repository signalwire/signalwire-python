"""
Tests for ``signalwire.core.security.webhook_middleware``.

These exercise the FastAPI dependency end-to-end against a tiny app — no
mocking of the validator. We synthesize valid signatures with hmac so the
test mirrors what SignalWire's backend would send.
"""

import base64
import hashlib
import hmac
from typing import Optional

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from signalwire.core.security.webhook_middleware import (
    SIGNALWIRE_SIGNATURE_HEADER,
    TWILIO_COMPAT_SIGNATURE_HEADER,
    make_webhook_validation_dependency,
)


SIGNING_KEY = "PSKtest1234567890abcdef"


def _scheme_a_signature(key: str, url: str, raw_body: str) -> str:
    return hmac.new(
        key.encode("utf-8"),
        (url + raw_body).encode("utf-8"),
        hashlib.sha1,
    ).hexdigest()


def _scheme_b_signature(
    key: str, url: str, params: Optional[dict[str, object]] = None
) -> str:
    """Sign url + sortedConcatParams with HMAC-SHA1, base64 encode."""
    params = params or {}
    concat = url
    for k in sorted(params.keys()):
        concat += f"{k}{params[k]}"
    return base64.b64encode(
        hmac.new(key.encode("utf-8"), concat.encode("utf-8"), hashlib.sha1).digest()
    ).decode()


@pytest.fixture
def signed_app() -> FastAPI:
    """Build a tiny FastAPI app with the webhook validator on POST /webhook.

    The handler echoes ``request.state.raw_body`` so we can assert the
    middleware exposed the captured raw bytes downstream.
    """
    app = FastAPI()
    dep = make_webhook_validation_dependency(SIGNING_KEY)

    @app.post("/webhook", dependencies=[Depends(dep)])
    async def webhook(request: Request) -> dict[str, object]:
        # The middleware should have stashed the raw body on request.state.
        raw = request.state.raw_body
        return {"echo_len": len(raw), "echo_decoded": raw.decode("utf-8")}

    return app


# ---------------------------------------------------------------------------
# 403 on invalid / missing
# ---------------------------------------------------------------------------

class TestInvalidSignature:
    def test_invalid_signature_returns_403(self, signed_app: FastAPI) -> None:
        client = TestClient(signed_app)
        body = '{"event":"call.state"}'
        resp = client.post(
            "/webhook",
            content=body,
            headers={
                SIGNALWIRE_SIGNATURE_HEADER: "this-is-not-a-real-signature",
                "content-type": "application/json",
            },
        )
        assert resp.status_code == 403

    def test_missing_signature_header_returns_403(self, signed_app: FastAPI) -> None:
        client = TestClient(signed_app)
        resp = client.post(
            "/webhook",
            content='{"event":"call.state"}',
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 200 on valid + raw body forwarded
# ---------------------------------------------------------------------------

class TestValidSignature:
    def test_valid_scheme_a_signature_passes_through(self, signed_app: FastAPI) -> None:
        client = TestClient(signed_app, base_url="http://testserver")
        body = '{"event":"call.state","params":{"call_id":"abc-123"}}'
        url = "http://testserver/webhook"
        sig = _scheme_a_signature(SIGNING_KEY, url, body)

        resp = client.post(
            "/webhook",
            content=body,
            headers={
                SIGNALWIRE_SIGNATURE_HEADER: sig,
                "content-type": "application/json",
            },
        )
        assert resp.status_code == 200
        # Raw body forwarded to handler — verifies middleware didn't consume it.
        assert resp.json()["echo_decoded"] == body
        assert resp.json()["echo_len"] == len(body.encode("utf-8"))

    def test_twilio_compat_header_alias_accepted(self, signed_app: FastAPI) -> None:
        """X-Twilio-Signature is accepted as an alias for cXML compat."""
        client = TestClient(signed_app, base_url="http://testserver")
        body = ""
        url = "http://testserver/webhook"
        sig = _scheme_a_signature(SIGNING_KEY, url, body)

        resp = client.post(
            "/webhook",
            content=body,
            headers={
                TWILIO_COMPAT_SIGNATURE_HEADER: sig,
                "content-type": "application/json",
            },
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Construction errors
# ---------------------------------------------------------------------------

class TestDependencyFactory:
    def test_empty_signing_key_raises(self) -> None:
        """make_webhook_validation_dependency rejects empty signing_key at build time."""
        with pytest.raises(ValueError):
            make_webhook_validation_dependency("")
        with pytest.raises(ValueError):
            make_webhook_validation_dependency(None)  # type: ignore[arg-type]  # intentional invalid input

    def test_proxy_url_base_env_used(self, signed_app: FastAPI, monkeypatch: pytest.MonkeyPatch) -> None:
        """SWML_PROXY_URL_BASE env wins over request.url for URL reconstruction.

        We sign against the proxy URL and POST to the test app — if the
        middleware honors the env var, validation succeeds.
        """
        proxy_base = "https://public.example.com"
        monkeypatch.setenv("SWML_PROXY_URL_BASE", proxy_base)

        client = TestClient(signed_app, base_url="http://testserver")
        body = '{"x":1}'
        url_signed_against = f"{proxy_base}/webhook"
        sig = _scheme_a_signature(SIGNING_KEY, url_signed_against, body)

        resp = client.post(
            "/webhook",
            content=body,
            headers={
                SIGNALWIRE_SIGNATURE_HEADER: sig,
                "content-type": "application/json",
            },
        )
        assert resp.status_code == 200
