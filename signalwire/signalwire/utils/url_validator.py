"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

URL validation utility to prevent SSRF attacks
"""

import ipaddress
import os
import socket
import logging
from typing import Any
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPConnection, HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool

logger = logging.getLogger("signalwire.url_validator")

# Private/reserved IP ranges that should be blocked
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local / cloud metadata
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),  # IPv6 private
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
]


def validate_url(url: str, allow_private: bool = False) -> bool:
    """
    Validate that a URL is safe to fetch (not pointing to private/internal resources).

    Args:
        url: The URL to validate
        allow_private: If True, allow private IP ranges (default: False)

    Returns:
        True if the URL is safe to fetch, False otherwise
    """
    try:
        parsed = urlparse(url)

        # Require http or https scheme
        if parsed.scheme not in ("http", "https"):
            logger.warning("URL rejected: invalid scheme %s", parsed.scheme)
            return False

        # Must have a hostname
        hostname = parsed.hostname
        if not hostname:
            logger.warning("URL rejected: no hostname")
            return False

        if _private_urls_allowed(allow_private):
            return True

        # Resolve hostname to IP addresses
        try:
            addr_infos = socket.getaddrinfo(hostname, None)
        except socket.gaierror:
            logger.warning("URL rejected: could not resolve hostname %s", hostname)
            return False

        # Check all resolved IPs against blocked ranges
        for addr_info in addr_infos:
            ip_str = str(addr_info[4][0])
            if _address_is_blocked(ip_str):
                logger.warning(
                    "URL rejected: %s resolves to blocked IP %s", hostname, ip_str
                )
                return False

        return True

    except Exception as e:
        logger.warning("URL validation error: %s", e)
        return False


def _private_urls_allowed(allow_private: bool) -> bool:
    """True when the caller or ``SWML_ALLOW_PRIVATE_URLS`` permits private addresses."""
    return allow_private or os.getenv("SWML_ALLOW_PRIVATE_URLS", "").lower() in (
        "1",
        "true",
        "yes",
    )


def _proxy_allowed() -> bool:
    """True when ``SWML_URL_FETCH_USE_PROXY`` lets these fetches use a proxy.

    A proxy connects on the session's behalf, so the connection check can't
    see the address it reaches, and the proxy resolves the hostname itself.
    Only a proxy that restricts destinations on its own keeps the protection.
    """
    return os.getenv("SWML_URL_FETCH_USE_PROXY", "").lower() in ("1", "true", "yes")


def _address_is_blocked(ip_str: str) -> bool:
    """True if ``ip_str`` is an address that a user-supplied URL must not reach."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    # An IPv4-mapped IPv6 address (::ffff:a.b.c.d) reaches the IPv4 host, so
    # check the IPv4 address it carries.
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    # The unspecified address (0.0.0.0 or ::) connects to the local host.
    if ip.is_unspecified:
        return True
    return any(ip in network for network in _BLOCKED_NETWORKS)


class _BlockedAddressError(OSError):
    """A connection would have reached a private or internal address."""


class _BlockedURLError(requests.exceptions.InvalidURL):
    """A request, or one of its redirects, targets a private or internal URL."""


def _refuse_blocked_peer(sock: socket.socket, host: str) -> None:
    """Close ``sock`` and raise if it connected to a blocked address.

    ``validate_url()`` resolves the hostname before the request, and the
    connection resolves it again. A DNS answer that changes in between (DNS
    rebinding) would pass the first check, so check the address actually
    connected to.
    """
    peer = str(sock.getpeername()[0])
    if not _private_urls_allowed(False) and _address_is_blocked(peer):
        sock.close()
        raise _BlockedAddressError(
            f"Refused to connect to {host}: {peer} is a private or internal address"
        )


class _PublicHTTPConnection(HTTPConnection):
    """An HTTP connection that refuses private or internal peer addresses."""

    def _new_conn(self) -> socket.socket:
        """Connect, then refuse a peer at a private or internal address."""
        sock = super()._new_conn()
        _refuse_blocked_peer(sock, self.host)
        return sock


class _PublicHTTPSConnection(HTTPSConnection):
    """An HTTPS connection that refuses private or internal peer addresses."""

    def _new_conn(self) -> socket.socket:
        """Connect, then refuse a peer at a private or internal address."""
        sock = super()._new_conn()
        _refuse_blocked_peer(sock, self.host)
        return sock


class _PublicHTTPConnectionPool(HTTPConnectionPool):
    """An HTTP connection pool whose connections refuse private or internal peers."""

    ConnectionCls = _PublicHTTPConnection


class _PublicHTTPSConnectionPool(HTTPSConnectionPool):
    """An HTTPS connection pool whose connections refuse private or internal peers."""

    ConnectionCls = _PublicHTTPSConnection


class _PublicAdapter(HTTPAdapter):
    """Refuses direct connections to private and internal addresses.

    Requests sent through a proxy use Requests' own proxy managers, so this
    check doesn't apply to them. ``_PublicSession`` sends directly unless
    ``SWML_URL_FETCH_USE_PROXY`` is set.
    """

    def init_poolmanager(self, *args: Any, **kwargs: Any) -> None:
        """Set up the pool manager to use the address-checking connection pools."""
        super().init_poolmanager(*args, **kwargs)
        self.poolmanager.pool_classes_by_scheme = {
            "http": _PublicHTTPConnectionPool,
            "https": _PublicHTTPSConnectionPool,
        }


class _PublicSession(requests.Session):
    """A Requests session for fetching user-supplied URLs.

    Checking a URL with ``validate_url()`` before fetching it isn't enough on
    its own: the server can redirect to an internal address, and the hostname
    can resolve differently when the connection is made. This session checks
    the URL of every request it sends, redirects included, and refuses a
    direct connection to a blocked address. ``SWML_ALLOW_PRIVATE_URLS`` turns
    both checks off, as it does for ``validate_url()``.

    It ignores HTTP_PROXY and HTTPS_PROXY, because through a proxy the
    connection check can't apply. Set ``SWML_URL_FETCH_USE_PROXY`` to use
    them, with a proxy that restricts destinations itself.
    """

    def __init__(self, allow_private: bool = False) -> None:
        """Create the session; unless ``allow_private``, refuse private peers."""
        super().__init__()
        self._allow_private = allow_private
        if not allow_private:
            adapter = _PublicAdapter()
            self.mount("http://", adapter)
            self.mount("https://", adapter)

    def send(
        self, request: requests.PreparedRequest, **kwargs: Any
    ) -> requests.Response:
        """Check the URL, then send the request; redirects are checked too.

        Raises an error for a private, internal or invalid URL. Unless a proxy is in
        use, the request connects directly so the peer address check applies.
        """
        # resolve_redirects() sends each redirect through this method, so
        # every hop is checked before it's requested.
        url = request.url or ""
        if not validate_url(url, allow_private=self._allow_private):
            from signalwire.core.security.security_utils import redact_url

            raise _BlockedURLError(
                f"URL rejected: {redact_url(url)} is private, internal or invalid"
            )
        if self._direct_only():
            # Connect directly, so the peer address check applies
            kwargs["proxies"] = {}
        return super().send(request, **kwargs)

    def rebuild_proxies(
        self,
        prepared_request: requests.PreparedRequest,
        proxies: dict[str, str] | None,
    ) -> dict[str, str]:
        """Return a redirect's proxies; drop proxy credentials when direct."""
        # Requests calls this for each redirect. For a plain-HTTP target it
        # would add the environment proxy's credentials as a header, which a
        # direct request would then send to the target itself.
        if self._direct_only():
            prepared_request.headers.pop("Proxy-Authorization", None)
            return {}
        return super().rebuild_proxies(prepared_request, proxies)

    def _direct_only(self) -> bool:
        """True when requests must bypass proxies, so the peer check applies."""
        return not (_private_urls_allowed(self._allow_private) or _proxy_allowed())
