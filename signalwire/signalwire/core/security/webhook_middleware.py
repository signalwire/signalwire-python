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

from fastapi import HTTPException, Request, Response, status

from signalwire.core.security.webhook_validator import validate_webhook_signature


SIGNALWIRE_SIGNATURE_HEADER = "x-signalwire-signature"
TWILIO_COMPAT_SIGNATURE_HEADER = "x-twilio-signature"


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

    The ``headers`` map is consulted for the signature header
    (``X-SignalWire-Signature`` or the ``X-Twilio-Signature`` alias); ``method``
    is accepted for signature-shape parity with the cross-port contract but is
    not part of the HMAC. Returns ``(403, {}, "")`` on any failure (missing/bad
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


def _reconstruct_url(request: Request, *, trust_proxy: bool) -> str:
    """Rebuild the public URL SignalWire POSTed to.

    Resolution order (highest priority first):

    1. ``SWML_PROXY_URL_BASE`` env var (joined with the request path + query).
    2. ``X-Forwarded-Proto`` / ``X-Forwarded-Host`` headers, if
       ``trust_proxy=True`` and both headers are present.
    3. ``request.url`` (FastAPI's view of the URL).
    """
    path_and_query = request.url.path
    if request.url.query:
        path_and_query = f"{path_and_query}?{request.url.query}"

    proxy_base = os.environ.get("SWML_PROXY_URL_BASE")
    if proxy_base:
        return f"{proxy_base.rstrip('/')}{path_and_query}"

    if trust_proxy:
        fwd_host = request.headers.get("x-forwarded-host")
        fwd_proto = request.headers.get("x-forwarded-proto", "https")
        if fwd_host:
            return f"{fwd_proto}://{fwd_host}{path_and_query}"

    return str(request.url)


def make_webhook_validation_dependency(
    signing_key: str,
    *,
    trust_proxy: bool = False,
) -> Callable[[Request, Response], Awaitable[Response | None]]:
    """Build a FastAPI dependency that enforces signature validation.

    The returned coroutine:

    1. Reads ``await request.body()`` and stashes the bytes on
       ``request.state.raw_body``.
    2. Pulls the ``X-SignalWire-Signature`` header (or the Twilio alias).
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
    "SIGNALWIRE_SIGNATURE_HEADER",
    "TWILIO_COMPAT_SIGNATURE_HEADER",
    "validate",
    "make_webhook_validation_dependency",
]
