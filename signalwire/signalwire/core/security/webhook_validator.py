"""
Webhook signature validation for SignalWire-signed HTTP requests.

Copyright (c) 2025 SignalWire. Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Implements both schemes from porting-sdk/webhooks.md:

- Scheme A (RELAY/SWML/JSON): hex(HMAC-SHA1(key, url + raw_body))
- Scheme B (Compat/cXML form): base64(HMAC-SHA1(key, url + sortedFormParams))
  with optional bodySHA256 query-param fallback for JSON-on-compat-surface.

Public API:
    validate_webhook_signature(signing_key, signature, url, raw_body) -> bool
    validate_request(signing_key, signature, url, params_or_raw_body) -> bool

All comparisons use ``hmac.compare_digest`` (constant-time) so the secret
is not leaked over repeated requests.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Any, Dict, List, Mapping, Tuple, Union
from urllib.parse import parse_qsl, urlparse, urlunparse


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _hex_hmac_sha1(key: str, message: str) -> str:
    """Scheme-A digest: lowercase hex of HMAC-SHA1."""
    return hmac.new(
        key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha1,
    ).hexdigest()


def _b64_hmac_sha1(key: str, message: str) -> str:
    """Scheme-B digest: standard base64 of HMAC-SHA1."""
    return base64.b64encode(
        hmac.new(
            key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha1,
        ).digest()
    ).decode("ascii")


def _safe_eq(a: str, b: str) -> bool:
    """Constant-time string compare. Both inputs coerced to str.

    Uses ``hmac.compare_digest`` to prevent timing-attack leakage of the
    expected signature. Returns False on any TypeError / ValueError so
    malformed inputs never raise.
    """
    try:
        return hmac.compare_digest(str(a), str(b))
    except (TypeError, ValueError):
        return False


def _sorted_concat_params(
    params: Union[Mapping[str, Any], List[Tuple[str, Any]], None],
) -> str:
    """Concatenate form params per Scheme B rules.

    - Sort by key, ASCII ascending.
    - For repeated keys: keep original submission order, emit ``key+value``
      once per occurrence.
    - Non-string values are stringified via ``str()`` (matches the
      JS reference's ``Buffer.from(... + value)`` coercion).
    """
    if not params:
        return ""

    # Normalize to a list of (key, value) tuples preserving original order.
    if isinstance(params, Mapping):
        items: List[Tuple[str, Any]] = []
        for k, v in params.items():
            if isinstance(v, (list, tuple)):
                for vi in v:
                    items.append((k, vi))
            else:
                items.append((k, v))
    else:
        items = [(k, v) for (k, v) in params]

    # Stable sort by key — preserves original order within repeated keys.
    items.sort(key=lambda kv: kv[0])

    return "".join(f"{k}{'' if v is None else v}" for k, v in items)


def _parse_form_body(raw_body: str) -> List[Tuple[str, str]]:
    """Best-effort parse of an x-www-form-urlencoded body.

    Returns an empty list if the body doesn't decode as form data; the
    caller will then sign against ``url + ""``.
    """
    if not raw_body:
        return []
    try:
        return parse_qsl(raw_body, keep_blank_values=True, strict_parsing=False)
    except Exception:
        return []


def _split_url(url: str) -> Tuple[str, str, str, str, str, str, Dict[str, str]]:
    """Split URL into scheme, host (no port), port (or ''), path, query, fragment, query_params.

    Empty strings if the field is absent.
    """
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = "" if parsed.port is None else str(parsed.port)
    qparams = dict(parse_qsl(parsed.query, keep_blank_values=True))
    return (
        parsed.scheme or "",
        host,
        port,
        parsed.path or "",
        parsed.query or "",
        parsed.fragment or "",
        qparams,
    )


def _build_url(
    scheme: str,
    host: str,
    port: str,
    path: str,
    query: str,
    fragment: str,
) -> str:
    """Reassemble a URL with explicit (or empty) port. IPv6 hosts wrapped in [ ]."""
    if host and ":" in host and not host.startswith("["):
        netloc_host = f"[{host}]"
    else:
        netloc_host = host
    netloc = f"{netloc_host}:{port}" if port else netloc_host
    return urlunparse((scheme, netloc, path, "", query, fragment))


def _candidate_urls(url: str) -> List[str]:
    """Return the URL variants to try for Scheme B port normalization.

    - If the URL already has a non-standard port: just the input URL.
    - If https + no port: input URL AND url with ":443".
    - If http + no port: input URL AND url with ":80".
    - If https + ":443" / http + ":80": input URL AND url with port stripped.
    - Otherwise (any explicit non-standard port): just the input URL.
    """
    scheme, host, port, path, query, fragment, _ = _split_url(url)
    if not host:
        return [url]

    standard = {"http": "80", "https": "443"}.get(scheme.lower())
    candidates: List[str] = [url]

    if not port and standard is not None:
        # Input has no port; also try with-standard-port.
        with_port = _build_url(scheme, host, standard, path, query, fragment)
        if with_port != url:
            candidates.append(with_port)
    elif port and standard == port:
        # Input has the standard port; also try without-port.
        without_port = _build_url(scheme, host, "", path, query, fragment)
        if without_port != url:
            candidates.append(without_port)
    # else: non-standard explicit port — only try as-is.
    return candidates


def _check_body_sha256(url: str, raw_body: str) -> bool:
    """If URL has ``?bodySHA256=<hex>``, verify ``sha256_hex(raw_body)`` matches.

    Returns True if the param is absent (no constraint), or present and matches.
    Returns False only when the param is present and mismatches.
    """
    _, _, _, _, _, _, qparams = _split_url(url)
    expected = qparams.get("bodySHA256")
    if expected is None:
        return True
    actual = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()
    return _safe_eq(actual, expected)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_webhook_signature(
    signing_key: str,
    signature: str,
    url: str,
    raw_body: str,
) -> bool:
    """Validate a SignalWire webhook signature against both schemes.

    Args:
        signing_key: Customer's Signing Key from the Dashboard. UTF-8 string,
            secret. ``None`` / empty raises ``ValueError`` — that's a programming
            error, not a validation failure.
        signature: The ``X-SignalWire-Signature`` header value (or
            ``X-Twilio-Signature`` for cXML compat). Missing / empty returns
            False without raising.
        url: The full URL SignalWire POSTed to (scheme, host, optional port,
            path, query). Must match what the platform saw — see the
            ``URL reconstruction`` section of porting-sdk/webhooks.md.
        raw_body: The raw request body bytes as a UTF-8 string, BEFORE any
            JSON / form parsing. Must be a ``str`` — passing a parsed dict
            raises ``TypeError``.

    Returns:
        True if the signature matches either Scheme A (hex JSON) or Scheme B
        (base64 form, with port-normalization variants and optional
        bodySHA256 fallback). False otherwise.

    Raises:
        ValueError: when ``signing_key`` is missing.
        TypeError: when ``raw_body`` is not a string.
    """
    if not signing_key:
        raise ValueError("signing_key is required")
    if not isinstance(raw_body, str):
        raise TypeError("raw_body must be a str — did you pass parsed JSON by mistake?")
    if signature is None or signature == "":
        return False

    # ------------------------------------------------------------------
    # Scheme A — RELAY/SWML/JSON: hex(HMAC-SHA1(key, url + raw_body))
    # ------------------------------------------------------------------
    expected_a = _hex_hmac_sha1(signing_key, url + raw_body)
    if _safe_eq(expected_a, signature):
        return True

    # ------------------------------------------------------------------
    # Scheme B — Compat/cXML form: base64(HMAC-SHA1(key, url + sorted_concat_params))
    # Try with parsed form params; fall back to empty params for JSON-on-compat.
    # Try both with-port and without-port URL variants.
    # ------------------------------------------------------------------
    parsed_params = _parse_form_body(raw_body)

    # Two param-shape attempts: parsed (form bodies) and empty (JSON-on-compat).
    param_shapes = [parsed_params, []]

    for candidate_url in _candidate_urls(url):
        for shape in param_shapes:
            concat = _sorted_concat_params(shape)
            expected_b = _b64_hmac_sha1(signing_key, candidate_url + concat)
            if _safe_eq(expected_b, signature):
                # If the URL carries bodySHA256, the body hash must match too.
                if _check_body_sha256(candidate_url, raw_body):
                    return True
                # bodySHA256 mismatched — keep trying other shapes/urls.

    return False


def validate_request(
    signing_key: str,
    signature: str,
    url: str,
    params_or_raw_body: Union[str, Mapping[str, Any], List[Tuple[str, Any]], None],
) -> bool:
    """Legacy ``@signalwire/compatibility-api`` drop-in entry point.

    If ``params_or_raw_body`` is a string, delegates to
    :func:`validate_webhook_signature` (Scheme A then Scheme B with parsed form).

    If it's a mapping or a list of (key, value) tuples, treats it as
    pre-parsed form params and runs Scheme B directly (with URL port
    normalization and optional bodySHA256 fallback).

    Args:
        signing_key: Customer's Signing Key. Missing raises ``ValueError``.
        signature: Header value. Missing / empty returns False.
        url: Full URL SignalWire POSTed to.
        params_or_raw_body: ``str`` raw body OR pre-parsed form params.

    Returns:
        True on match, False otherwise.

    Raises:
        ValueError: when ``signing_key`` is missing.
        TypeError: when ``params_or_raw_body`` is neither a string nor a
            mapping/list (e.g. a parsed JSON dict-like that's been rejected).
    """
    if not signing_key:
        raise ValueError("signing_key is required")
    if signature is None or signature == "":
        return False

    if isinstance(params_or_raw_body, str):
        return validate_webhook_signature(
            signing_key, signature, url, params_or_raw_body
        )

    if params_or_raw_body is None:
        params_or_raw_body = []

    if not isinstance(params_or_raw_body, (Mapping, list, tuple)):
        raise TypeError(
            "params_or_raw_body must be a str (raw body) or a dict/list of form params"
        )

    # Pre-parsed form params → Scheme B only.
    concat = _sorted_concat_params(params_or_raw_body)
    for candidate_url in _candidate_urls(url):
        expected_b = _b64_hmac_sha1(signing_key, candidate_url + concat)
        if _safe_eq(expected_b, signature):
            # bodySHA256 has no raw body to verify here — skip that check.
            return True
    return False


__all__ = [
    "validate_webhook_signature",
    "validate_request",
]
