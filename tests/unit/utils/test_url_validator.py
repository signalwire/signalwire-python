"""
Tests for ``signalwire.utils.url_validator.validate_url`` — the
SSRF-prevention helper that ports must mirror.

Cross-language SDK contract: every port that fetches user-supplied URLs
must reject (a) non-http(s) schemes, (b) URLs without a hostname,
(c) URLs that resolve to private / loopback / link-local IPs, unless
``allow_private=True`` is passed or ``SWML_ALLOW_PRIVATE_URLS`` is set.
"""

import os
from unittest.mock import patch

import pytest

from signalwire.utils.url_validator import validate_url


class TestValidateUrlScheme:
    def test_http_scheme_allowed(self):
        with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("1.2.3.4", 0))]):
            assert validate_url("http://example.com") is True

    def test_https_scheme_allowed(self):
        with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("1.2.3.4", 0))]):
            assert validate_url("https://example.com") is True

    def test_ftp_scheme_rejected(self):
        assert validate_url("ftp://example.com") is False

    def test_file_scheme_rejected(self):
        assert validate_url("file:///etc/passwd") is False

    def test_javascript_scheme_rejected(self):
        assert validate_url("javascript:alert(1)") is False


class TestValidateUrlHostname:
    def test_no_hostname_rejected(self):
        # Path-only URLs without a hostname are rejected
        assert validate_url("http://") is False

    def test_hostname_unresolvable_rejected(self):
        import socket as _socket
        with patch("socket.getaddrinfo", side_effect=_socket.gaierror):
            assert validate_url("http://nonexistent.invalid") is False


class TestValidateUrlBlockedRanges:
    def test_loopback_ipv4_rejected(self):
        with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("127.0.0.1", 0))]):
            assert validate_url("http://localhost") is False

    def test_rfc1918_10_rejected(self):
        with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("10.0.0.5", 0))]):
            assert validate_url("http://internal") is False

    def test_rfc1918_192_rejected(self):
        with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("192.168.1.1", 0))]):
            assert validate_url("http://router") is False

    def test_link_local_metadata_rejected(self):
        # 169.254.169.254 is the AWS/GCP metadata endpoint
        with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("169.254.169.254", 0))]):
            assert validate_url("http://metadata") is False

    def test_ipv6_loopback_rejected(self):
        with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("::1", 0))]):
            assert validate_url("http://[::1]") is False

    def test_public_ip_allowed(self):
        with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("8.8.8.8", 0))]):
            assert validate_url("http://dns.google") is True


class TestValidateUrlAllowPrivate:
    def test_allow_private_param_bypasses_check(self):
        # No DNS call needed — allow_private short-circuits.
        assert validate_url("http://10.0.0.5", allow_private=True) is True

    def test_env_var_bypasses_check(self):
        with patch.dict(os.environ, {"SWML_ALLOW_PRIVATE_URLS": "true"}):
            assert validate_url("http://10.0.0.5") is True

    def test_env_var_false_does_not_bypass(self):
        with patch.dict(os.environ, {"SWML_ALLOW_PRIVATE_URLS": "false"}, clear=False):
            with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("10.0.0.5", 0))]):
                assert validate_url("http://internal") is False
