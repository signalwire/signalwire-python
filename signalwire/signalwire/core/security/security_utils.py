"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Standalone security hygiene utilities.

These mirror the TypeScript SDK's ``SecurityUtils`` (filterSensitiveHeaders,
redactUrl, isValidHostname) so the same protections — keeping credentials out
of user callbacks and logs, reusable hostname validation — are available in the
Python reference and every port.
"""

import re
from collections.abc import Mapping
from typing import Any, TypeVar

# Header names whose values are credentials/secrets and must never be handed to
# user callbacks or written to logs. Compared case-insensitively.
SENSITIVE_HEADERS = frozenset(
    {
        "authorization",
        "cookie",
        "x-api-key",
        "proxy-authorization",
        "set-cookie",
    }
)

# url credentials: ``://user:secret@host`` -> ``://user:****@host``.
_URL_CREDENTIALS_RE = re.compile(r"://([^:@/]+):([^@/]+)@")

# Hostnames must not contain whitespace, slashes, or control characters.
_HOSTNAME_REJECT_RE = re.compile(r"[\s/\\\x00-\x1f\x7f]")


_V = TypeVar("_V")


def filter_sensitive_headers(headers: Mapping[str, _V]) -> dict[str, _V]:
    """Return a copy of ``headers`` with sensitive (credential-bearing) headers
    removed, so request headers can be safely passed to user callbacks.

    Args:
        headers: Mapping of header name -> value.

    Returns:
        A new dict containing only the non-sensitive headers (keys preserved
        as given; the sensitivity check is case-insensitive).
    """
    if not headers:
        return {}
    return {k: v for k, v in headers.items() if k.lower() not in SENSITIVE_HEADERS}


def redact_url(url: Any) -> Any:
    """Mask the password in a URL's userinfo before logging.

    ``https://user:secret@host/path`` -> ``https://user:****@host/path``.
    A URL with no embedded credentials is returned unchanged.

    Args:
        url: The URL string (or any value; non-strings are returned as-is).

    Returns:
        The URL with any ``:password@`` replaced by ``:****@``.
    """
    if not isinstance(url, str):
        return url
    return _URL_CREDENTIALS_RE.sub(r"://\1:****@", url)


def is_valid_hostname(host: str) -> bool:
    """Standalone hostname sanity check: reject empty hosts and any host
    containing whitespace, slashes, or control characters.

    This is the reusable character-level check, independent of the full
    :func:`signalwire.utils.url_validator.validate_url` (which also does scheme
    checks, DNS resolution, and private-IP blocking). Callers that only need to
    validate a hostname string use this.

    Args:
        host: The hostname string.

    Returns:
        True if the hostname is non-empty and contains no whitespace/slashes/
        control characters; False otherwise.
    """
    if not host:
        return False
    return _HOSTNAME_REJECT_RE.search(host) is None
