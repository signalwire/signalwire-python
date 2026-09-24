"""
FastAPI middleware / dependency for SignalWire webhook signature validation.

Copyright (c) 2025 SignalWire. Licensed under the MIT License.
See LICENSE file in the project root for full license information.

This module ships a small, framework-aware adapter around
:func:`signalwire.core.security.webhook_validator.validate_webhook_signature`.

Why a custom dependency rather than a vanilla ``Depends`` on ``request.body()``?

- We MUST capture the raw bytes BEFORE FastAPI's JSON parser consumes the
  stream — re-serialization changes whitespace and key order, which breaks
  the Scheme A digest. The dependency stashes the raw body on
  ``request.state.raw_body`` so the downstream handler can re-parse without
  re-reading the stream.
- Reverse-proxy / ngrok deployments need the URL the platform POSTed to,
  which differs from the URL the SDK sees. The dependency honors
  ``X-Forwarded-Proto`` / ``X-Forwarded-Host`` when ``trust_proxy=True``,
  plus the ``SWML_PROXY_URL_BASE`` env var, with ``request.url`` as last
  resort.
- The legacy cXML/Compatibility scheme used the ``X-Twilio-Signature``
  header. We accept it as an alias of ``X-SignalWire-Signature`` so users
  migrating from the legacy SDK can keep their callers unchanged.

Usage::

    from signalwire.core.security.webhook_middleware import (
        make_webhook_validation_dependency,
    )

    dep = make_webhook_validation_dependency(signing_key="PSK...")

    @app.post("/webhook", dependencies=[Depends(dep)])
    async def webhook(request: Request):
        body = request.state.raw_body  # bytes; re-parse if you need JSON
"""

from __future__ import annotations

import os
from typing import NoReturn
from collections.abc import Awaitable, Callable, Mapping
from urllib.parse import urlsplit

from fastapi import HTTPException, Request, Response, status

from signalwire.core.security.webhook_validator import (
    validate_webhook_signature,
    validate_webhook_signature_sha256,
)


SIGNALWIRE_SIGNATURE_HEADER = "x-signalwire-signature"
SIGNALWIRE_SHA256_SIGNATURE_HEADER = "x-signalwire-sha256-signature"
TWILIO_COMPAT_SIGNATURE_HEADER = "x-twilio-signature"

# The agent endpoints SignalWire POSTs to, relative to the agent's route and
# without slashes: the SWML fetch, SWAIG dispatch and the post-prompt summary.
# With a signing_key set, a POST to any of them needs a valid signature,
# however the agent is served.
_SIGNED_POST_PATHS = frozenset({"", "swaig", "post_prompt"})


def validate(
    method: str,
    url: str,
    headers: Mapping[str, str],
    body: str,
    *,
    signing_key: str,
) -> tuple[int, dict[str, str], str] | None:
    """Framework-free webhook-validation decision.

    This is the **cross-port** validation core: it takes a request decomposed
    into language-neutral primitives and returns either a 403-shaped response
    triple to short-circuit with, or ``None`` to let the handler run. Every
    port implements this same shape (dotnet ``WebhookValidationMiddleware.
    Validate``, Rack/PSGI middleware, a Hono handler, …); the framework-specific
    wrapper (:func:`make_webhook_validation_dependency` here) is the only idiom
    on top of it.

    The ``headers`` map is consulted for the signature header: the stronger
    ``X-SignalWire-Sha256-Signature`` is preferred when present, falling back to
    ``X-SignalWire-Signature`` (or the ``X-Twilio-Signature`` alias); ``method``
    is accepted to keep a stable signature but is not part of the HMAC. Returns
    ``(403, {}, "")`` on any failure (missing/bad
    signature, non-UTF-8 body, validator error) — no body detail, to avoid
    leaking which branch tripped.

    Args:
        method: HTTP method (part of the cross-port contract; not HMAC'd).
        url: The public URL SignalWire POSTed to (already reconstructed).
        headers: Case-insensitively-looked-up request headers.
        body: The raw request body as a UTF-8 string.
        signing_key: The customer's Signing Key. Required, non-empty.

    Returns:
        ``None`` if the signature is valid; ``(403, {}, "")`` otherwise.

    Raises:
        ValueError: if ``signing_key`` is empty.
    """
    if not signing_key:
        raise ValueError("signing_key is required")

    # Prefer the stronger SHA-256 signature when the platform sends it
    # (X-SignalWire-Sha256-Signature): same Scheme A message, SHA-256 hash. Fall
    # back to the SHA-1 header below so deployments on older platform builds --
    # and the cXML/form Scheme B path -- keep validating.
    sha256_signature = headers.get(SIGNALWIRE_SHA256_SIGNATURE_HEADER)
    if sha256_signature:
        try:
            if validate_webhook_signature_sha256(
                signing_key, sha256_signature, url, body
            ):
                return None
        except (TypeError, ValueError):
            pass  # fall back to the SHA-1 header path below

    signature = headers.get(SIGNALWIRE_SIGNATURE_HEADER)
    if signature is None:
        signature = headers.get(TWILIO_COMPAT_SIGNATURE_HEADER)
    if not signature:
        return (status.HTTP_403_FORBIDDEN, {}, "")

    try:
        ok = validate_webhook_signature(signing_key, signature, url, body)
    except (TypeError, ValueError):
        return (status.HTTP_403_FORBIDDEN, {}, "")

    if not ok:
        return (status.HTTP_403_FORBIDDEN, {}, "")
    return None


def _public_url(
    url: str,
    headers: Mapping[str, str],
    *,
    trust_proxy: bool,
    path_and_query: str | None = None,
) -> str:
    """Rebuild the public URL SignalWire POSTed to, from the URL the server saw.

    Framework-free, so the web server and the serverless adapters share it.
    Resolution order (highest priority first):

    1. ``SWML_PROXY_URL_BASE`` env var, joined with the path and query.
    2. ``X-Forwarded-Proto`` / ``X-Forwarded-Host`` headers, if
       ``trust_proxy=True`` and the host header is present.
    3. ``url`` as the server saw it.

    Args:
        url: The full URL the server received the request on.
        headers: Request headers, looked up by lower-case name.
        trust_proxy: Whether to honor the forwarded headers.
        path_and_query: The path and query to join to a proxy base.
            Defaults to those of ``url``; a serverless platform passes the
            path below the app's root instead. A forwarded host always keeps
            the path of ``url``.

    Returns:
        The URL the signature was computed over.
    """
    parts = urlsplit(url)
    url_path_and_query = parts.path + (f"?{parts.query}" if parts.query else "")

    proxy_base = os.environ.get("SWML_PROXY_URL_BASE")
    if proxy_base:
        joined = url_path_and_query if path_and_query is None else path_and_query
        return f"{proxy_base.rstrip('/')}{joined}"

    if trust_proxy:
        # A forwarded host replaces only the host: the path is the one the
        # platform saw, prefixes such as a CGI script or an Azure app included
        fwd_host = headers.get("x-forwarded-host")
        fwd_proto = headers.get("x-forwarded-proto", "https")
        if fwd_host:
            return f"{fwd_proto}://{fwd_host}{url_path_and_query}"

    return url


def _reconstruct_url(request: Request, *, trust_proxy: bool) -> str:
    """Rebuild the public URL SignalWire POSTed to. See :func:`_public_url`."""
    return _public_url(str(request.url), request.headers, trust_proxy=trust_proxy)


def make_webhook_validation_dependency(
    signing_key: str,
    *,
    trust_proxy: bool = False,
) -> Callable[[Request, Response], Awaitable[Response | None]]:
    """Build a FastAPI dependency that enforces signature validation.

    The returned coroutine:

    1. Reads ``await request.body()`` and stashes the bytes on
       ``request.state.raw_body``.
    2. Pulls the signature header (``X-SignalWire-Sha256-Signature`` preferred,
       then ``X-SignalWire-Signature`` or the Twilio alias).
    3. Reconstructs the public URL (proxy headers / env / fallback).
    4. Calls :func:`validate_webhook_signature`.
    5. On invalid signature: raises ``HTTPException(403)`` to short-circuit
       the handler. FastAPI's ``dependencies=[Depends(...)]`` only honors
       short-circuiting via raised exceptions — returning a Response from a
       dependency does not stop the endpoint.
    6. On valid: returns ``None`` so the handler runs as normal.

    Args:
        signing_key: The customer's Signing Key. Required, non-empty.
        trust_proxy: If True, honor ``X-Forwarded-Proto`` / ``X-Forwarded-Host``
            when reconstructing the URL. Default False — proxy headers are
            spoofable, so opt in only when you control the proxy.

    Returns:
        Async callable suitable for ``Depends(...)``.

    Raises:
        ValueError: at construction time if ``signing_key`` is empty.
    """
    if not signing_key:
        raise ValueError("signing_key is required")

    def _forbidden() -> NoReturn:
        # Single canonical 403 short-circuit. No body detail (would leak
        # which branch failed); validators MUST NOT log scheme details.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    async def dependency(request: Request, response: Response) -> None:
        # Capture raw body BEFORE any other consumer reads the stream.
        # request.body() caches internally so subsequent calls are safe.
        raw_bytes = await request.body()
        request.state.raw_body = raw_bytes
        try:
            raw_body_str = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            # Non-UTF-8 body cannot match an HMAC over UTF-8 input.
            _forbidden()

        # Decompose the FastAPI Request into primitives and hand off to the
        # framework-free cross-port core. The FastAPI-specific parts (raw-body
        # capture above, proxy-aware URL reconstruction) stay here as idiom.
        url = _reconstruct_url(request, trust_proxy=trust_proxy)
        rejection = validate(
            request.method,
            url,
            request.headers,
            raw_body_str,
            signing_key=signing_key,
        )
        if rejection is not None:
            _forbidden()
        # Valid — fall through and let the handler run.

    return dependency


__all__ = [
    "SIGNALWIRE_SHA256_SIGNATURE_HEADER",
    "SIGNALWIRE_SIGNATURE_HEADER",
    "TWILIO_COMPAT_SIGNATURE_HEADER",
    "make_webhook_validation_dependency",
    "validate",
]
