"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for AuthHandler class in signalwire/core/auth_handler.py
"""

import asyncio
import secrets
from collections.abc import Coroutine
from typing import Any, TYPE_CHECKING, TypeVar
import pytest
from unittest.mock import Mock, patch, MagicMock

if TYPE_CHECKING:
    from signalwire.core.auth_handler import AuthHandler

_T = TypeVar("_T")


# ---------------------------------------------------------------------------
# Helpers: build a mock SecurityConfig that behaves like the real one
# ---------------------------------------------------------------------------

def _make_security_config(
    username: str = "testuser",
    password: str = "testpass",
    bearer_token: str | None = None,
    api_key: str | None = None,
    api_key_header: str = "X-API-Key",
) -> Mock:
    """
    Return a mock SecurityConfig with the given auth settings.
    """
    cfg = Mock()
    cfg.get_basic_auth.return_value = (username, password)
    cfg.bearer_token = bearer_token
    cfg.api_key = api_key
    cfg.api_key_header = api_key_header
    return cfg


def _run_async(coro: Coroutine[Any, Any, _T]) -> _T:
    """Run an async coroutine synchronously so we don't need pytest-asyncio."""
    return asyncio.run(coro)


# ===========================================================================
# AuthHandler initialisation and _setup_auth_methods
# ===========================================================================

class TestAuthHandlerInit:
    """Test AuthHandler construction and _setup_auth_methods."""

    def test_basic_init_with_basic_auth_only(self) -> None:
        """AuthHandler initializes with basic auth from SecurityConfig."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(username="admin", password="secret")
        handler = AuthHandler(cfg)

        assert handler.security_config is cfg
        assert handler.auth_methods['basic']['enabled'] is True
        assert handler.auth_methods['basic']['username'] == "admin"
        assert handler.auth_methods['basic']['password'] == "secret"
        assert 'bearer' not in handler.auth_methods
        assert 'api_key' not in handler.auth_methods

    def test_init_with_bearer_token(self) -> None:
        """AuthHandler registers bearer method when token is configured."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(bearer_token="my-token-123")
        handler = AuthHandler(cfg)

        assert 'bearer' in handler.auth_methods
        assert handler.auth_methods['bearer']['enabled'] is True
        assert handler.auth_methods['bearer']['token'] == "my-token-123"

    def test_init_with_api_key(self) -> None:
        """AuthHandler registers api_key method when key is configured."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(api_key="ak_abc123")
        handler = AuthHandler(cfg)

        assert 'api_key' in handler.auth_methods
        assert handler.auth_methods['api_key']['enabled'] is True
        assert handler.auth_methods['api_key']['key'] == "ak_abc123"

    def test_init_with_custom_api_key_header(self) -> None:
        """AuthHandler respects a custom api_key_header from SecurityConfig."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(api_key="ak_abc", api_key_header="X-Custom-Key")
        handler = AuthHandler(cfg)

        assert handler.auth_methods['api_key']['header'] == "X-Custom-Key"

    def test_init_with_default_api_key_header(self) -> None:
        """When api_key_header attribute is missing, default to X-API-Key."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = Mock()
        cfg.get_basic_auth.return_value = ("u", "p")
        cfg.bearer_token = None
        cfg.api_key = "somekey"
        # Simulate missing api_key_header attribute -> getattr falls back
        del cfg.api_key_header
        handler = AuthHandler(cfg)

        assert handler.auth_methods['api_key']['header'] == "X-API-Key"

    def test_init_with_all_methods(self) -> None:
        """AuthHandler initializes all three auth methods when all configured."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(
            username="u", password="p",
            bearer_token="tok", api_key="key"
        )
        handler = AuthHandler(cfg)

        assert 'basic' in handler.auth_methods
        assert 'bearer' in handler.auth_methods
        assert 'api_key' in handler.auth_methods

    def test_bearer_not_registered_when_none(self) -> None:
        """Bearer method is not added when bearer_token is None."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(bearer_token=None)
        handler = AuthHandler(cfg)
        assert 'bearer' not in handler.auth_methods

    def test_bearer_not_registered_when_empty_string(self) -> None:
        """Bearer method is not added when bearer_token is empty string (falsy)."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(bearer_token="")
        handler = AuthHandler(cfg)
        assert 'bearer' not in handler.auth_methods

    def test_api_key_not_registered_when_none(self) -> None:
        """api_key method is not added when api_key is None."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(api_key=None)
        handler = AuthHandler(cfg)
        assert 'api_key' not in handler.auth_methods

    def test_auto_error_false_on_http_basic(self) -> None:
        """HTTPBasic is created with auto_error=False so credentials are optional."""
        from signalwire.core.auth_handler import AuthHandler

        with patch("signalwire.core.auth_handler.HTTPBasic") as mock_cls:
            mock_cls.return_value = Mock()
            cfg = _make_security_config()
            handler = AuthHandler(cfg)
            mock_cls.assert_called_once_with(auto_error=False)

    def test_auto_error_false_on_http_bearer(self) -> None:
        """HTTPBearer is created with auto_error=False so credentials are optional."""
        from signalwire.core.auth_handler import AuthHandler

        with patch("signalwire.core.auth_handler.HTTPBearer") as mock_cls:
            mock_cls.return_value = Mock()
            cfg = _make_security_config()
            handler = AuthHandler(cfg)
            mock_cls.assert_called_once_with(auto_error=False)

    def test_basic_auth_always_enabled(self) -> None:
        """Basic auth is always marked as enabled, even when username is empty."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(username="", password="")
        handler = AuthHandler(cfg)
        assert handler.auth_methods['basic']['enabled'] is True


# ===========================================================================
# verify_basic_auth  --  timing-safe comparison
# ===========================================================================

class TestVerifyBasicAuth:
    """Test the verify_basic_auth method, including timing-safe comparison."""

    def _make_handler(self, username: str = "user", password: str = "pass") -> "AuthHandler":
        from signalwire.core.auth_handler import AuthHandler
        cfg = _make_security_config(username=username, password=password)
        return AuthHandler(cfg)

    def _make_creds(self, username: str, password: str) -> Mock:
        creds = Mock()
        creds.username = username
        creds.password = password
        return creds

    def test_correct_credentials(self) -> None:
        """Valid username+password returns True."""
        handler = self._make_handler("admin", "secret")
        creds = self._make_creds("admin", "secret")
        assert handler.verify_basic_auth(creds) is True

    def test_wrong_username(self) -> None:
        """Wrong username returns False."""
        handler = self._make_handler("admin", "secret")
        creds = self._make_creds("wrong", "secret")
        assert handler.verify_basic_auth(creds) is False

    def test_wrong_password(self) -> None:
        """Wrong password returns False."""
        handler = self._make_handler("admin", "secret")
        creds = self._make_creds("admin", "wrong")
        assert handler.verify_basic_auth(creds) is False

    def test_both_wrong(self) -> None:
        """Both wrong returns False."""
        handler = self._make_handler("admin", "secret")
        creds = self._make_creds("wrong", "wrong")
        assert handler.verify_basic_auth(creds) is False

    def test_empty_credentials(self) -> None:
        """Empty strings for credentials are rejected when config values differ."""
        handler = self._make_handler("admin", "secret")
        creds = self._make_creds("", "")
        assert handler.verify_basic_auth(creds) is False

    def test_empty_credentials_match_empty_config(self) -> None:
        """Empty credentials match when config has empty username/password."""
        handler = self._make_handler("", "")
        creds = self._make_creds("", "")
        assert handler.verify_basic_auth(creds) is True

    def test_uses_secrets_compare_digest(self) -> None:
        """Verify that secrets.compare_digest is used (timing-safe comparison)."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(username="admin", password="secret")
        handler = AuthHandler(cfg)
        creds = self._make_creds("admin", "secret")

        with patch("signalwire.core.auth_handler.secrets.compare_digest", wraps=secrets.compare_digest) as mock_cd:
            result = handler.verify_basic_auth(creds)
            assert result is True
            assert mock_cd.call_count == 2
            mock_cd.assert_any_call("admin", "admin")
            mock_cd.assert_any_call("secret", "secret")

    def test_timing_safe_even_on_username_mismatch(self) -> None:
        """Both username and password are checked even when username fails.

        This ensures the comparison doesn't short-circuit in a way that leaks
        timing information about which field was wrong. The implementation
        computes both comparisons before AND-ing them together.
        """
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(username="admin", password="secret")
        handler = AuthHandler(cfg)
        creds = self._make_creds("wrong", "secret")

        with patch("signalwire.core.auth_handler.secrets.compare_digest", wraps=secrets.compare_digest) as mock_cd:
            result = handler.verify_basic_auth(creds)
            assert result is False
            # Both comparisons should still occur (no short-circuit)
            assert mock_cd.call_count == 2

    def test_timing_safe_even_on_password_mismatch(self) -> None:
        """Both fields are compared even when only the password is wrong."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(username="admin", password="secret")
        handler = AuthHandler(cfg)
        creds = self._make_creds("admin", "wrong")

        with patch("signalwire.core.auth_handler.secrets.compare_digest", wraps=secrets.compare_digest) as mock_cd:
            result = handler.verify_basic_auth(creds)
            assert result is False
            assert mock_cd.call_count == 2

    def test_basic_auth_disabled(self) -> None:
        """When basic auth is disabled, verify_basic_auth returns False."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config()
        handler = AuthHandler(cfg)
        # Manually disable basic auth
        handler.auth_methods['basic']['enabled'] = False

        creds = self._make_creds("testuser", "testpass")
        assert handler.verify_basic_auth(creds) is False

    def test_basic_auth_missing_from_methods(self) -> None:
        """When 'basic' key is entirely absent, verify_basic_auth returns False."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config()
        handler = AuthHandler(cfg)
        del handler.auth_methods['basic']

        creds = self._make_creds("testuser", "testpass")
        assert handler.verify_basic_auth(creds) is False

    def test_case_sensitive_username(self) -> None:
        """Username comparison is case-sensitive."""
        handler = self._make_handler("Admin", "secret")
        creds = self._make_creds("admin", "secret")
        assert handler.verify_basic_auth(creds) is False

    def test_case_sensitive_password(self) -> None:
        """Password comparison is case-sensitive."""
        handler = self._make_handler("admin", "Secret")
        creds = self._make_creds("admin", "secret")
        assert handler.verify_basic_auth(creds) is False


# ===========================================================================
# verify_bearer_token  --  timing-safe comparison
# ===========================================================================

class TestVerifyBearerToken:
    """Test the verify_bearer_token method."""

    def _make_handler(self, bearer_token: str = "tok_abc") -> "AuthHandler":
        from signalwire.core.auth_handler import AuthHandler
        cfg = _make_security_config(bearer_token=bearer_token)
        return AuthHandler(cfg)

    def _make_bearer_creds(self, token: str) -> Mock:
        creds = Mock()
        creds.credentials = token
        return creds

    def test_correct_token(self) -> None:
        """Valid bearer token returns True."""
        handler = self._make_handler("my-token")
        creds = self._make_bearer_creds("my-token")
        assert handler.verify_bearer_token(creds) is True

    def test_wrong_token(self) -> None:
        """Invalid bearer token returns False."""
        handler = self._make_handler("my-token")
        creds = self._make_bearer_creds("wrong-token")
        assert handler.verify_bearer_token(creds) is False

    def test_empty_token(self) -> None:
        """Empty token string does not match a non-empty config token."""
        handler = self._make_handler("my-token")
        creds = self._make_bearer_creds("")
        assert handler.verify_bearer_token(creds) is False

    def test_bearer_not_configured(self) -> None:
        """When no bearer token is configured, returns False."""
        from signalwire.core.auth_handler import AuthHandler
        cfg = _make_security_config(bearer_token=None)
        handler = AuthHandler(cfg)

        creds = self._make_bearer_creds("anything")
        assert handler.verify_bearer_token(creds) is False

    def test_bearer_disabled(self) -> None:
        """When bearer is configured but disabled, returns False."""
        handler = self._make_handler("tok")
        handler.auth_methods['bearer']['enabled'] = False

        creds = self._make_bearer_creds("tok")
        assert handler.verify_bearer_token(creds) is False

    def test_uses_secrets_compare_digest(self) -> None:
        """Ensure timing-safe comparison via secrets.compare_digest."""
        handler = self._make_handler("tok_xyz")
        creds = self._make_bearer_creds("tok_xyz")

        with patch("signalwire.core.auth_handler.secrets.compare_digest", wraps=secrets.compare_digest) as mock_cd:
            result = handler.verify_bearer_token(creds)
            assert result is True
            mock_cd.assert_called_once_with("tok_xyz", "tok_xyz")

    def test_bearer_missing_from_methods(self) -> None:
        """When 'bearer' key is absent from auth_methods, returns False."""
        from signalwire.core.auth_handler import AuthHandler
        cfg = _make_security_config(bearer_token="tok")
        handler = AuthHandler(cfg)
        del handler.auth_methods['bearer']

        creds = self._make_bearer_creds("tok")
        assert handler.verify_bearer_token(creds) is False

    def test_token_case_sensitive(self) -> None:
        """Token comparison is case-sensitive."""
        handler = self._make_handler("MyToken")
        creds = self._make_bearer_creds("mytoken")
        assert handler.verify_bearer_token(creds) is False


# ===========================================================================
# verify_api_key  --  timing-safe comparison
# ===========================================================================

class TestVerifyApiKey:
    """Test the verify_api_key method."""

    def _make_handler(self, api_key: str = "ak_secret") -> "AuthHandler":
        from signalwire.core.auth_handler import AuthHandler
        cfg = _make_security_config(api_key=api_key)
        return AuthHandler(cfg)

    def test_correct_api_key(self) -> None:
        """Correct API key returns True."""
        handler = self._make_handler("ak_123")
        assert handler.verify_api_key("ak_123") is True

    def test_wrong_api_key(self) -> None:
        """Wrong API key returns False."""
        handler = self._make_handler("ak_123")
        assert handler.verify_api_key("wrong") is False

    def test_empty_api_key(self) -> None:
        """Empty API key string returns False when configured key is non-empty."""
        handler = self._make_handler("ak_123")
        assert handler.verify_api_key("") is False

    def test_api_key_not_configured(self) -> None:
        """When no API key configured, returns False."""
        from signalwire.core.auth_handler import AuthHandler
        cfg = _make_security_config(api_key=None)
        handler = AuthHandler(cfg)
        assert handler.verify_api_key("anything") is False

    def test_api_key_disabled(self) -> None:
        """When api_key is configured but disabled, returns False."""
        handler = self._make_handler("ak_123")
        handler.auth_methods['api_key']['enabled'] = False
        assert handler.verify_api_key("ak_123") is False

    def test_uses_secrets_compare_digest(self) -> None:
        """Ensure timing-safe comparison via secrets.compare_digest."""
        handler = self._make_handler("ak_xyz")
        with patch("signalwire.core.auth_handler.secrets.compare_digest", wraps=secrets.compare_digest) as mock_cd:
            handler.verify_api_key("ak_xyz")
            mock_cd.assert_called_once_with("ak_xyz", "ak_xyz")

    def test_api_key_missing_from_methods(self) -> None:
        """When 'api_key' key is absent from auth_methods, returns False."""
        from signalwire.core.auth_handler import AuthHandler
        cfg = _make_security_config(api_key="ak")
        handler = AuthHandler(cfg)
        del handler.auth_methods['api_key']
        assert handler.verify_api_key("ak") is False

    def test_api_key_case_sensitive(self) -> None:
        """API key comparison is case-sensitive."""
        handler = self._make_handler("AK_Secret")
        assert handler.verify_api_key("ak_secret") is False


# ===========================================================================
# get_fastapi_dependency  --  auth enforcement
# ===========================================================================

class TestGetFastapiDependency:
    """Test the FastAPI dependency factory."""

    def _make_handler(self, **kwargs: Any) -> "AuthHandler":
        from signalwire.core.auth_handler import AuthHandler
        cfg = _make_security_config(**kwargs)
        return AuthHandler(cfg)

    def test_returns_callable(self) -> None:
        """get_fastapi_dependency returns a callable."""
        handler = self._make_handler()
        dep = handler.get_fastapi_dependency()
        assert callable(dep)

    def test_returns_callable_optional(self) -> None:
        """get_fastapi_dependency(optional=True) also returns a callable."""
        handler = self._make_handler()
        dep = handler.get_fastapi_dependency(optional=True)
        assert callable(dep)

    def test_basic_auth_succeeds(self) -> None:
        """Auth dependency accepts valid basic credentials."""
        handler = self._make_handler(username="u", password="p")
        dep = handler.get_fastapi_dependency()
        assert dep is not None

        basic_creds = Mock()
        basic_creds.username = "u"
        basic_creds.password = "p"

        result = _run_async(dep(basic_credentials=basic_creds, bearer_credentials=None, api_key=None))
        assert result['authenticated'] is True
        assert result['method'] == 'basic'

    def test_basic_auth_fails_raises_401(self) -> None:
        """Auth dependency raises HTTPException(401) on bad basic creds."""
        from signalwire.core.auth_handler import HTTPException  # type: ignore[attr-defined]  # conditionally-defined module attr

        handler = self._make_handler(username="u", password="p")
        dep = handler.get_fastapi_dependency(optional=False)
        assert dep is not None

        bad_creds = Mock()
        bad_creds.username = "bad"
        bad_creds.password = "bad"

        with pytest.raises(HTTPException) as exc_info:
            _run_async(dep(basic_credentials=bad_creds, bearer_credentials=None, api_key=None))
        assert exc_info.value.status_code == 401

    def test_no_credentials_raises_401(self) -> None:
        """Auth dependency raises 401 when no credentials are provided."""
        from signalwire.core.auth_handler import HTTPException  # type: ignore[attr-defined]  # conditionally-defined module attr

        handler = self._make_handler()
        dep = handler.get_fastapi_dependency(optional=False)
        assert dep is not None

        with pytest.raises(HTTPException) as exc_info:
            _run_async(dep(basic_credentials=None, bearer_credentials=None, api_key=None))
        assert exc_info.value.status_code == 401

    def test_no_credentials_optional_returns_unauthenticated(self) -> None:
        """When optional=True, missing credentials returns unauthenticated result."""
        handler = self._make_handler()
        dep = handler.get_fastapi_dependency(optional=True)
        assert dep is not None

        result = _run_async(dep(basic_credentials=None, bearer_credentials=None, api_key=None))
        assert result['authenticated'] is False
        assert result['method'] is None

    def test_bearer_auth_succeeds(self) -> None:
        """Auth dependency accepts valid bearer token."""
        handler = self._make_handler(bearer_token="my_tok")
        dep = handler.get_fastapi_dependency()
        assert dep is not None

        bearer_creds = Mock()
        bearer_creds.credentials = "my_tok"

        result = _run_async(dep(basic_credentials=None, bearer_credentials=bearer_creds, api_key=None))
        assert result['authenticated'] is True
        assert result['method'] == 'bearer'

    def test_bearer_takes_precedence_over_basic(self) -> None:
        """When both bearer and basic credentials are provided, bearer wins."""
        handler = self._make_handler(username="u", password="p", bearer_token="tok")
        dep = handler.get_fastapi_dependency()
        assert dep is not None

        bearer_creds = Mock()
        bearer_creds.credentials = "tok"
        basic_creds = Mock()
        basic_creds.username = "u"
        basic_creds.password = "p"

        result = _run_async(dep(basic_credentials=basic_creds, bearer_credentials=bearer_creds, api_key=None))
        assert result['method'] == 'bearer'

    def test_bad_bearer_falls_back_to_basic(self) -> None:
        """When bearer fails but basic succeeds, result method is 'basic'."""
        handler = self._make_handler(username="u", password="p", bearer_token="tok")
        dep = handler.get_fastapi_dependency()
        assert dep is not None

        bad_bearer = Mock()
        bad_bearer.credentials = "wrong"
        good_basic = Mock()
        good_basic.username = "u"
        good_basic.password = "p"

        result = _run_async(dep(basic_credentials=good_basic, bearer_credentials=bad_bearer, api_key=None))
        assert result['authenticated'] is True
        assert result['method'] == 'basic'

    def test_401_includes_www_authenticate_header(self) -> None:
        """HTTPException includes WWW-Authenticate: Basic header."""
        from signalwire.core.auth_handler import HTTPException  # type: ignore[attr-defined]  # conditionally-defined module attr

        handler = self._make_handler()
        dep = handler.get_fastapi_dependency(optional=False)
        assert dep is not None

        with pytest.raises(HTTPException) as exc_info:
            _run_async(dep(basic_credentials=None, bearer_credentials=None, api_key=None))
        assert exc_info.value.headers == {"WWW-Authenticate": "Basic"}

    def test_401_detail_message(self) -> None:
        """HTTPException 401 includes the expected detail message."""
        from signalwire.core.auth_handler import HTTPException  # type: ignore[attr-defined]  # conditionally-defined module attr

        handler = self._make_handler()
        dep = handler.get_fastapi_dependency(optional=False)
        assert dep is not None

        with pytest.raises(HTTPException) as exc_info:
            _run_async(dep(basic_credentials=None, bearer_credentials=None, api_key=None))
        assert exc_info.value.detail == "Invalid authentication credentials"

    def test_returns_none_when_depends_unavailable(self) -> None:
        """When Depends is None (FastAPI not installed), returns None."""
        from signalwire.core import auth_handler

        original_depends = auth_handler.Depends  # type: ignore[attr-defined]  # conditionally-defined module attr
        try:
            auth_handler.Depends = None  # type: ignore[attr-defined,assignment]  # conditionally-defined module attr
            cfg = _make_security_config()
            handler = auth_handler.AuthHandler(cfg)
            assert handler.get_fastapi_dependency() is None
        finally:
            auth_handler.Depends = original_depends  # type: ignore[attr-defined]  # conditionally-defined module attr

    def test_optional_false_with_valid_basic_does_not_raise(self) -> None:
        """With optional=False and valid basic creds, no exception is raised."""
        handler = self._make_handler(username="admin", password="pass")
        dep = handler.get_fastapi_dependency(optional=False)
        assert dep is not None

        basic_creds = Mock()
        basic_creds.username = "admin"
        basic_creds.password = "pass"

        # Should not raise
        result = _run_async(dep(basic_credentials=basic_creds, bearer_credentials=None, api_key=None))
        assert result['authenticated'] is True


# ===========================================================================
# flask_decorator  --  auth enforcement
# ===========================================================================

class TestFlaskDecorator:
    """Test the Flask decorator for authentication."""

    def _make_handler(self, **kwargs: Any) -> "AuthHandler":
        from signalwire.core.auth_handler import AuthHandler
        cfg = _make_security_config(**kwargs)
        return AuthHandler(cfg)

    def _mock_flask_request(self, auth_header: str | None = None, authorization: Any = None, api_key_header: str | None = None, api_key_value: str | None = None) -> Mock:
        """Build a mock flask request object."""
        request = Mock()
        headers = {}
        if auth_header:
            headers['Authorization'] = auth_header
        if api_key_header and api_key_value:
            headers[api_key_header] = api_key_value
        request.headers = Mock()
        request.headers.get = lambda key, default='': headers.get(key, default)
        request.authorization = authorization
        request.remote_addr = "127.0.0.1"
        request.method = "POST"
        request.path = "/test"
        return request

    def test_bearer_auth_success(self) -> None:
        """Flask decorator accepts valid bearer token."""
        handler = self._make_handler(bearer_token="tok123")

        @handler.flask_decorator
        def my_view() -> str:
            return "OK"

        mock_request = self._mock_flask_request(auth_header="Bearer tok123")
        mock_flask = Mock()
        mock_flask.request = mock_request
        mock_flask.Response = Mock(return_value="401 response")

        with patch.dict("sys.modules", {"flask": mock_flask}):
            result = my_view()
        assert result == "OK"

    def test_api_key_success(self) -> None:
        """Flask decorator accepts valid API key."""
        handler = self._make_handler(api_key="ak_secret", api_key_header="X-API-Key")

        @handler.flask_decorator
        def my_view() -> str:
            return "OK"

        mock_request = self._mock_flask_request(api_key_header="X-API-Key", api_key_value="ak_secret")
        mock_flask = Mock()
        mock_flask.request = mock_request
        mock_flask.Response = Mock(return_value="401 response")

        with patch.dict("sys.modules", {"flask": mock_flask}):
            result = my_view()
        assert result == "OK"

    def test_basic_auth_success(self) -> None:
        """Flask decorator accepts valid basic auth."""
        handler = self._make_handler(username="admin", password="pass")

        @handler.flask_decorator
        def my_view() -> str:
            return "OK"

        mock_auth = Mock()
        mock_auth.username = "admin"
        mock_auth.password = "pass"
        mock_request = self._mock_flask_request(authorization=mock_auth)
        mock_flask = Mock()
        mock_flask.request = mock_request
        mock_flask.Response = Mock(return_value="401 response")

        with patch.dict("sys.modules", {"flask": mock_flask}):
            result = my_view()
        assert result == "OK"

    def test_all_methods_fail_returns_401(self) -> None:
        """Flask decorator returns 401 when all auth methods fail."""
        handler = self._make_handler(
            username="admin", password="pass",
            bearer_token="tok", api_key="ak"
        )

        @handler.flask_decorator
        def my_view() -> str:
            return "OK"

        mock_request = self._mock_flask_request()
        mock_response_instance = Mock()
        mock_flask = Mock()
        mock_flask.request = mock_request
        mock_flask.Response = Mock(return_value=mock_response_instance)

        with patch.dict("sys.modules", {"flask": mock_flask}):
            result = my_view()

        assert result is mock_response_instance
        mock_flask.Response.assert_called_once_with(
            'Authentication required',
            401,
            {'WWW-Authenticate': 'Basic realm="SignalWire Service"'}
        )

    def test_wrong_bearer_wrong_basic_returns_401(self) -> None:
        """Flask decorator returns 401 when bearer and basic both fail."""
        handler = self._make_handler(
            username="admin", password="pass", bearer_token="tok"
        )

        @handler.flask_decorator
        def my_view() -> str:
            return "OK"

        mock_auth = Mock()
        mock_auth.username = "wrong"
        mock_auth.password = "wrong"
        mock_request = self._mock_flask_request(
            auth_header="Bearer wrong_tok",
            authorization=mock_auth,
        )
        mock_response_instance = Mock()
        mock_flask = Mock()
        mock_flask.request = mock_request
        mock_flask.Response = Mock(return_value=mock_response_instance)

        with patch.dict("sys.modules", {"flask": mock_flask}):
            result = my_view()

        assert result is mock_response_instance

    def test_bearer_priority_over_basic(self) -> None:
        """Bearer auth is tried before basic; if bearer succeeds, basic is skipped."""
        handler = self._make_handler(
            username="admin", password="pass", bearer_token="tok"
        )

        @handler.flask_decorator
        def my_view() -> str:
            return "OK"

        mock_request = self._mock_flask_request(auth_header="Bearer tok")
        mock_flask = Mock()
        mock_flask.request = mock_request
        mock_flask.Response = Mock(return_value="401 response")

        with patch.dict("sys.modules", {"flask": mock_flask}):
            result = my_view()
        assert result == "OK"

    def test_preserves_wrapped_function_name(self) -> None:
        """The decorator preserves the original function's name via @wraps."""
        handler = self._make_handler()

        @handler.flask_decorator
        def my_special_view() -> str:
            return "OK"

        assert my_special_view.__name__ == "my_special_view"

    def test_flask_decorator_uses_timing_safe_comparison(self) -> None:
        """Flask decorator uses secrets.compare_digest for token comparison."""
        handler = self._make_handler(bearer_token="tok_safe")

        @handler.flask_decorator
        def my_view() -> str:
            return "OK"

        mock_request = self._mock_flask_request(auth_header="Bearer tok_safe")
        mock_flask = Mock()
        mock_flask.request = mock_request
        mock_flask.Response = Mock(return_value="401 resp")

        with patch.dict("sys.modules", {"flask": mock_flask}):
            with patch("signalwire.core.auth_handler.secrets.compare_digest", wraps=secrets.compare_digest) as mock_cd:
                result = my_view()
                assert result == "OK"
                # Should have been called for the bearer comparison
                mock_cd.assert_any_call("tok_safe", "tok_safe")

    def test_basic_auth_no_authorization_header(self) -> None:
        """When authorization is None, basic auth falls through gracefully."""
        handler = self._make_handler(username="admin", password="pass")

        @handler.flask_decorator
        def my_view() -> str:
            return "OK"

        mock_request = self._mock_flask_request(authorization=None)
        mock_response_instance = Mock()
        mock_flask = Mock()
        mock_flask.request = mock_request
        mock_flask.Response = Mock(return_value=mock_response_instance)

        with patch.dict("sys.modules", {"flask": mock_flask}):
            result = my_view()

        # No bearer, no api_key, no authorization -> 401
        assert result is mock_response_instance

    def test_bearer_not_tried_if_not_configured(self) -> None:
        """When bearer auth is not configured, a Bearer header is ignored."""
        handler = self._make_handler(username="admin", password="pass")
        # bearer is NOT configured

        @handler.flask_decorator
        def my_view() -> str:
            return "OK"

        # Provide a Bearer header, but since bearer is not enabled,
        # should fall through to basic (which will also fail here).
        mock_request = self._mock_flask_request(auth_header="Bearer some_tok")
        mock_response_instance = Mock()
        mock_flask = Mock()
        mock_flask.request = mock_request
        mock_flask.Response = Mock(return_value=mock_response_instance)

        with patch.dict("sys.modules", {"flask": mock_flask}):
            result = my_view()

        # Should fail because no valid basic auth was provided
        assert result is mock_response_instance

    def test_api_key_priority_over_basic(self) -> None:
        """API key auth is checked before basic auth in the Flask decorator."""
        handler = self._make_handler(
            username="admin", password="pass",
            api_key="ak_123", api_key_header="X-API-Key"
        )

        @handler.flask_decorator
        def my_view() -> str:
            return "OK"

        # Provide only API key, no basic auth
        mock_request = self._mock_flask_request(
            api_key_header="X-API-Key",
            api_key_value="ak_123"
        )
        mock_flask = Mock()
        mock_flask.request = mock_request
        mock_flask.Response = Mock(return_value="401 response")

        with patch.dict("sys.modules", {"flask": mock_flask}):
            result = my_view()
        assert result == "OK"


# ===========================================================================
# get_auth_info
# ===========================================================================

class TestGetAuthInfo:
    """Test the get_auth_info method."""

    def _make_handler(self, **kwargs: Any) -> "AuthHandler":
        from signalwire.core.auth_handler import AuthHandler
        cfg = _make_security_config(**kwargs)
        return AuthHandler(cfg)

    def test_basic_only(self) -> None:
        """Only basic auth info returned when that is the only method."""
        handler = self._make_handler(username="admin", password="pass")
        info = handler.get_auth_info()

        assert 'basic' in info
        assert info['basic']['enabled'] is True
        assert info['basic']['username'] == "admin"
        assert 'bearer' not in info
        assert 'api_key' not in info

    def test_bearer_info(self) -> None:
        """Bearer info is included when bearer token is configured."""
        handler = self._make_handler(bearer_token="tok")
        info = handler.get_auth_info()

        assert 'bearer' in info
        assert info['bearer']['enabled'] is True
        assert 'hint' in info['bearer']

    def test_api_key_info(self) -> None:
        """API key info includes header name and hint."""
        handler = self._make_handler(api_key="ak", api_key_header="X-Custom")
        info = handler.get_auth_info()

        assert 'api_key' in info
        assert info['api_key']['enabled'] is True
        assert info['api_key']['header'] == "X-Custom"
        assert "X-Custom" in info['api_key']['hint']

    def test_all_methods_info(self) -> None:
        """All three methods present in info when all configured."""
        handler = self._make_handler(
            username="u", password="p",
            bearer_token="tok", api_key="ak"
        )
        info = handler.get_auth_info()
        assert set(info.keys()) == {'basic', 'bearer', 'api_key'}

    def test_disabled_methods_excluded(self) -> None:
        """Disabled auth methods are excluded from the info dict."""
        handler = self._make_handler(
            username="u", password="p",
            bearer_token="tok", api_key="ak"
        )
        handler.auth_methods['bearer']['enabled'] = False
        handler.auth_methods['api_key']['enabled'] = False

        info = handler.get_auth_info()
        assert 'basic' in info
        assert 'bearer' not in info
        assert 'api_key' not in info

    def test_no_password_leak_in_info(self) -> None:
        """get_auth_info does not leak password or tokens in the returned dict."""
        handler = self._make_handler(
            username="u", password="supersecret",
            bearer_token="hidden_tok", api_key="hidden_ak"
        )
        info = handler.get_auth_info()

        # Password should not be in basic info
        assert 'password' not in info.get('basic', {})
        assert 'supersecret' not in str(info)
        # Token should not be in bearer info
        assert 'token' not in info.get('bearer', {})
        assert 'hidden_tok' not in str(info)
        # API key should not be in api_key info
        assert 'key' not in info.get('api_key', {})
        assert 'hidden_ak' not in str(info)

    def test_empty_info_when_all_disabled(self) -> None:
        """An empty dict is returned when all auth methods are disabled."""
        handler = self._make_handler(
            username="u", password="p",
            bearer_token="tok", api_key="ak"
        )
        handler.auth_methods['basic']['enabled'] = False
        handler.auth_methods['bearer']['enabled'] = False
        handler.auth_methods['api_key']['enabled'] = False

        info = handler.get_auth_info()
        assert info == {}


# ===========================================================================
# Edge cases and credential-related scenarios
# ===========================================================================

class TestEdgeCases:
    """Edge cases around credentials and handler behavior."""

    def test_very_long_credentials(self) -> None:
        """Very long credential strings are handled correctly."""
        from signalwire.core.auth_handler import AuthHandler

        long_user = "u" * 10000
        long_pass = "p" * 10000
        cfg = _make_security_config(username=long_user, password=long_pass)
        handler = AuthHandler(cfg)

        creds = Mock()
        creds.username = long_user
        creds.password = long_pass
        assert handler.verify_basic_auth(creds) is True

    def test_credentials_with_special_characters(self) -> None:
        """Special characters (colons, slashes, etc.) in credentials."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(username="user:with:colons", password="p@ss/w0rd!#$%")
        handler = AuthHandler(cfg)

        creds = Mock()
        creds.username = "user:with:colons"
        creds.password = "p@ss/w0rd!#$%"
        assert handler.verify_basic_auth(creds) is True

    def test_bearer_token_with_jwt_format(self) -> None:
        """Bearer tokens with JWT-like format are handled correctly."""
        from signalwire.core.auth_handler import AuthHandler

        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature"
        cfg = _make_security_config(bearer_token=token)
        handler = AuthHandler(cfg)

        creds = Mock()
        creds.credentials = token
        assert handler.verify_bearer_token(creds) is True

    def test_unicode_credentials_raise_type_error(self) -> None:
        """Non-ASCII strings raise TypeError from secrets.compare_digest.

        secrets.compare_digest only accepts ASCII strings or bytes.
        This test documents the behavior when non-ASCII credentials are used.
        """
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(username="user_\u00e9", password="p\u00e4ss")
        handler = AuthHandler(cfg)

        creds = Mock()
        creds.username = "user_\u00e9"
        creds.password = "p\u00e4ss"

        with pytest.raises(TypeError):
            handler.verify_basic_auth(creds)

    def test_setup_auth_methods_called_on_init(self) -> None:
        """_setup_auth_methods is called during __init__."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(username="u", password="p")
        with patch.object(AuthHandler, '_setup_auth_methods') as mock_setup:
            handler = AuthHandler(cfg)
            mock_setup.assert_called_once()

    def test_handler_stores_security_config(self) -> None:
        """The handler retains a reference to the security config."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config()
        handler = AuthHandler(cfg)
        assert handler.security_config is cfg

    def test_verify_basic_auth_requires_both_fields_correct(self) -> None:
        """Only one matching field (username OR password) is not enough."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(username="admin", password="secret")
        handler = AuthHandler(cfg)

        # Only username correct
        creds = Mock()
        creds.username = "admin"
        creds.password = "not_secret"
        assert handler.verify_basic_auth(creds) is False

        # Only password correct
        creds.username = "not_admin"
        creds.password = "secret"
        assert handler.verify_basic_auth(creds) is False

    def test_multiple_handler_instances_independent(self) -> None:
        """Multiple AuthHandler instances have independent auth_methods."""
        from signalwire.core.auth_handler import AuthHandler

        cfg1 = _make_security_config(username="user1", password="pass1")
        cfg2 = _make_security_config(username="user2", password="pass2", bearer_token="tok")

        handler1 = AuthHandler(cfg1)
        handler2 = AuthHandler(cfg2)

        assert handler1.auth_methods['basic']['username'] == "user1"
        assert handler2.auth_methods['basic']['username'] == "user2"
        assert 'bearer' not in handler1.auth_methods
        assert 'bearer' in handler2.auth_methods

    def test_api_key_header_defaults_when_attr_missing(self) -> None:
        """When security_config has no api_key_header attr, defaults to X-API-Key."""
        from signalwire.core.auth_handler import AuthHandler

        # Use Mock with spec to ensure api_key_header is not an attribute
        cfg = Mock(spec=['get_basic_auth', 'bearer_token', 'api_key'])
        cfg.get_basic_auth.return_value = ("u", "p")
        cfg.bearer_token = None
        cfg.api_key = "thekey"

        handler = AuthHandler(cfg)
        assert handler.auth_methods['api_key']['header'] == "X-API-Key"

    def test_whitespace_credentials_not_stripped(self) -> None:
        """Leading/trailing whitespace in credentials is significant."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(username="admin", password="secret")
        handler = AuthHandler(cfg)

        creds = Mock()
        creds.username = " admin"
        creds.password = "secret "
        assert handler.verify_basic_auth(creds) is False

    def test_null_bearer_token_in_auth_methods(self) -> None:
        """Verifying bearer token when bearer method exists but enabled is False."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config(bearer_token="tok")
        handler = AuthHandler(cfg)
        handler.auth_methods['bearer']['enabled'] = False

        creds = Mock()
        creds.credentials = "tok"
        assert handler.verify_bearer_token(creds) is False

    def test_handler_basic_auth_has_basic_auth_and_bearer_fields(self) -> None:
        """Handler stores both basic_auth and bearer_auth scheme objects."""
        from signalwire.core.auth_handler import AuthHandler

        cfg = _make_security_config()
        handler = AuthHandler(cfg)

        assert hasattr(handler, 'basic_auth')
        assert hasattr(handler, 'bearer_auth')

    def test_handler_with_none_httpbasic(self) -> None:
        """When HTTPBasic is None (not installed), basic_auth attribute is None."""
        from signalwire.core import auth_handler

        original = auth_handler.HTTPBasic  # type: ignore[attr-defined]  # conditionally-defined module attr
        try:
            auth_handler.HTTPBasic = None  # type: ignore[attr-defined,assignment]  # conditionally-defined module attr
            cfg = _make_security_config()
            handler = auth_handler.AuthHandler(cfg)
            assert handler.basic_auth is None
        finally:
            auth_handler.HTTPBasic = original  # type: ignore[attr-defined]  # conditionally-defined module attr

    def test_handler_with_none_httpbearer(self) -> None:
        """When HTTPBearer is None (not installed), bearer_auth attribute is None."""
        from signalwire.core import auth_handler

        original = auth_handler.HTTPBearer  # type: ignore[attr-defined]  # conditionally-defined module attr
        try:
            auth_handler.HTTPBearer = None  # type: ignore[attr-defined,assignment]  # conditionally-defined module attr
            cfg = _make_security_config()
            handler = auth_handler.AuthHandler(cfg)
            assert handler.bearer_auth is None
        finally:
            auth_handler.HTTPBearer = original  # type: ignore[attr-defined]  # conditionally-defined module attr
