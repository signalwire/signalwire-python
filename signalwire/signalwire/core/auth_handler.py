"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import secrets
from typing import Any, Protocol, TYPE_CHECKING, runtime_checkable
from collections.abc import Callable
from functools import wraps

if TYPE_CHECKING:
    from fastapi import HTTPException, Depends
    from fastapi.security import (
        HTTPBasic,
        HTTPBasicCredentials,
        HTTPBearer,
        HTTPAuthorizationCredentials,
    )
else:
    # Optional dependency: FastAPI may be absent in non-web installs. These
    # fallbacks let the module import; auth handlers guard on availability at
    # call time.
    try:
        from fastapi import HTTPException, Depends
        from fastapi.security import (
            HTTPBasic,
            HTTPBasicCredentials,
            HTTPBearer,
            HTTPAuthorizationCredentials,
        )
    except ImportError:
        HTTPException = Depends = None
        HTTPBasic = HTTPBasicCredentials = None
        HTTPBearer = HTTPAuthorizationCredentials = None

from signalwire.core.logging_config import get_logger

if TYPE_CHECKING:
    from signalwire.core.security_config import SecurityConfig

logger = get_logger("auth_handler")


# ---------------------------------------------------------------------------
# Credential carriers
# ---------------------------------------------------------------------------
#
# ``verify_basic_auth`` and ``verify_bearer_token`` used to annotate their sole
# parameter with FastAPI's ``HTTPBasicCredentials`` / ``HTTPAuthorizationCredentials``.
# Neither method ever touched anything framework-specific: they read
# ``.username``/``.password`` and ``.credentials`` respectively and compare them with
# ``secrets.compare_digest``. The FIELDS are the contract; which web framework's class
# carries them is idiom — and FastAPI is an OPTIONAL dependency here (see the
# try/except above, which sets these names to ``None`` in a non-web install), so the
# annotation degraded to ``None`` exactly when FastAPI was absent.
#
# So the parameter types are declared structurally, as ``Protocol``s. A Protocol is
# strictly WIDER than the concrete class: a real FastAPI ``HTTPBasicCredentials``
# still satisfies ``BasicCredentials`` with no change at any existing call site, and
# so does any object carrying the same attributes.
#
# The names and field sets match what the rest of the fleet converged on
# independently: 8 of the 9 ports already ship a ``BasicCredentials`` carrier of
# ``username``/``password`` and a ``BearerCredentials`` carrier of
# ``scheme``/``credentials`` (go is the exception — it passes the ``*http.Request``
# or a scalar pair, which is the same contract expressed in its own idiom).
#
# Deliberately NO concrete value class is defined here: any object with the fields
# satisfies these, so adding one would be surface the ports would then have to
# mirror for nothing.


@runtime_checkable
class BasicCredentials(Protocol):
    """HTTP Basic credentials parsed from the ``Authorization`` header.

    Structural: any object exposing ``username`` and ``password`` satisfies this,
    including FastAPI's ``HTTPBasicCredentials``.
    """

    username: str
    password: str


@runtime_checkable
class BearerCredentials(Protocol):
    """HTTP Bearer/authorization credentials parsed from the ``Authorization`` header.

    Structural: any object exposing ``scheme`` and ``credentials`` satisfies this,
    including FastAPI's ``HTTPAuthorizationCredentials``.

    ``scheme`` is the auth-scheme token as the client sent it (``Bearer``) and
    ``credentials`` is the raw token following it. ``verify_bearer_token`` compares
    only ``credentials``; ``scheme`` is carried because it is half of what the header
    conveys and a caller cannot otherwise tell ``Bearer`` from another scheme.
    """

    scheme: str
    credentials: str


class AuthHandler:
    """
    Unified authentication handler supporting multiple auth methods.

    This class provides a clean pattern for handling Basic Auth, Bearer tokens,
    and API keys across all SignalWire services.
    """

    def __init__(self, security_config: "SecurityConfig"):
        """
        Initialize auth handler with security configuration.

        Args:
            security_config: SecurityConfig instance with auth settings
        """
        self.security_config = security_config
        self.basic_auth = HTTPBasic(auto_error=False) if HTTPBasic is not None else None
        self.bearer_auth = (
            HTTPBearer(auto_error=False) if HTTPBearer is not None else None
        )

        # Get auth methods from config
        self._setup_auth_methods()

    def _setup_auth_methods(self) -> None:
        """Setup enabled authentication methods from config"""
        self.auth_methods: dict[str, dict[str, Any]] = {}

        # Basic auth (always available for backward compatibility)
        username, password = self.security_config.get_basic_auth()
        self.auth_methods["basic"] = {
            "enabled": True,
            "username": username,
            "password": password,
        }

        # Bearer token (if configured)
        bearer_token = getattr(self.security_config, "bearer_token", None)
        if bearer_token:
            self.auth_methods["bearer"] = {"enabled": True, "token": bearer_token}

        # API key (if configured)
        api_key = getattr(self.security_config, "api_key", None)
        if api_key:
            self.auth_methods["api_key"] = {
                "enabled": True,
                "key": api_key,
                "header": getattr(self.security_config, "api_key_header", "X-API-Key"),
            }

    def verify_basic_auth(self, credentials: BasicCredentials) -> bool:
        """Verify basic auth credentials"""
        if not self.auth_methods.get("basic", {}).get("enabled"):
            return False

        basic_config = self.auth_methods["basic"]
        username_correct = secrets.compare_digest(
            credentials.username, basic_config["username"]
        )
        password_correct = secrets.compare_digest(
            credentials.password, basic_config["password"]
        )

        return username_correct and password_correct

    def verify_bearer_token(self, credentials: BearerCredentials) -> bool:
        """Verify bearer token"""
        if not self.auth_methods.get("bearer", {}).get("enabled"):
            return False

        bearer_config = self.auth_methods["bearer"]
        return secrets.compare_digest(credentials.credentials, bearer_config["token"])

    def verify_api_key(self, api_key: str) -> bool:
        """Verify API key"""
        if not self.auth_methods.get("api_key", {}).get("enabled"):
            return False

        api_config = self.auth_methods["api_key"]
        return secrets.compare_digest(api_key, api_config["key"])

    def get_fastapi_dependency(
        self, optional: bool = False
    ) -> Callable[..., Any] | None:
        """
        Get FastAPI dependency for authentication.

        Args:
            optional: If True, authentication is optional

        Returns:
            FastAPI dependency function
        """
        if Depends is None:
            return None

        async def auth_dependency(
            basic_credentials: HTTPBasicCredentials | None = Depends(self.basic_auth)  # noqa: B008  # FastAPI DI: Depends() in default is the intended idiom (Depends is lazy-imported so the config-level extend-immutable-calls can't resolve it)
            if self.basic_auth
            else None,
            bearer_credentials: HTTPAuthorizationCredentials | None = Depends(  # noqa: B008  # FastAPI DI: Depends() in default is the intended idiom
                self.bearer_auth
            )
            if self.bearer_auth
            else None,
            api_key: str | None = None,  # Get from header in request
        ) -> dict[str, Any]:
            """
            Authenticate a request from the FastAPI security schemes.

            Bearer is tried first, then Basic; the first scheme that verifies
            wins and no later scheme is consulted. Both comparisons go through
            ``secrets.compare_digest``. The ``api_key`` parameter is accepted
            but NOT consulted here — API-key auth in this dependency is
            unimplemented, so a request bearing only an API key is treated as
            unauthenticated (``AuthHandler.flask_decorator`` does honour the
            API-key header; this FastAPI path does not).

            On failure with ``optional=False`` this raises
            ``HTTPException(401, detail="Invalid authentication credentials")``
            with a ``WWW-Authenticate: Basic`` header — Basic is always
            advertised as the challenge, even when Bearer is the configured
            scheme. With ``optional=True`` no exception is raised and the
            handler runs with ``authenticated=False``.

            Returns:
                ``{"authenticated": bool, "method": "bearer" | "basic" | None}``.
                ``method`` is None whenever ``authenticated`` is False.

            Raises:
                HTTPException: 401 when no scheme verifies and ``optional`` is
                    False.
            """
            # Try each auth method
            authenticated = False
            auth_method = None

            # Try bearer token first (if provided)
            if bearer_credentials and self.verify_bearer_token(bearer_credentials):
                authenticated = True
                auth_method = "bearer"

            # Try basic auth
            elif basic_credentials and self.verify_basic_auth(basic_credentials):
                authenticated = True
                auth_method = "basic"

            # Try API key (would need to be extracted from request headers)
            # This is a simplified version - in practice, you'd get it from request

            if not authenticated and not optional:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Basic"},
                )

            return {"authenticated": authenticated, "method": auth_method}

        return auth_dependency

    def flask_decorator(self, f: Callable[..., Any]) -> Callable[..., Any]:
        """
        Flask decorator for authentication.

        This provides compatibility with Flask-based services like MCP Gateway.
        """

        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            """
            Authenticate the current Flask request, then call the view.

            Schemes are tried in this order, and the first that verifies calls
            through to the wrapped view with the original ``*args``/``**kwargs``:

            1. ``Authorization: Bearer <token>`` — only if a bearer token is
               configured; the token is everything after the 7-character
               ``"Bearer "`` prefix.
            2. The configured API-key header (``X-API-Key`` unless
               ``security_config.api_key_header`` overrides it).
            3. Flask's parsed ``request.authorization`` (HTTP Basic), matching
               both username and password.

            Every comparison uses ``secrets.compare_digest``.

            On failure it logs an ``auth_failed`` event with the client IP,
            method and path, and returns a Flask ``Response`` with body
            ``"Authentication required"``, status **401**, and header
            ``WWW-Authenticate: Basic realm="SignalWire Service"``. Note this
            RETURNS a response rather than raising, and the challenge is always
            Basic regardless of which schemes are enabled.

            Returns:
                The wrapped view's return value on success, else the 401
                ``Response``.
            """
            from flask import request, Response

            # Try Bearer token first
            auth_header = request.headers.get("Authorization", "")

            if auth_header.startswith("Bearer ") and self.auth_methods.get(
                "bearer", {}
            ).get("enabled"):
                token = auth_header[7:]
                if secrets.compare_digest(token, self.auth_methods["bearer"]["token"]):
                    return f(*args, **kwargs)

            # Try API key
            if self.auth_methods.get("api_key", {}).get("enabled"):
                api_config = self.auth_methods["api_key"]
                api_key = request.headers.get(api_config["header"])
                if api_key and secrets.compare_digest(api_key, api_config["key"]):
                    return f(*args, **kwargs)

            # Fall back to Basic auth
            auth = request.authorization
            if auth and self.auth_methods.get("basic", {}).get("enabled"):
                basic_config = self.auth_methods["basic"]
                if secrets.compare_digest(
                    auth.username, basic_config["username"]
                ) and secrets.compare_digest(auth.password, basic_config["password"]):
                    return f(*args, **kwargs)

            # Authentication failed
            logger.warning(
                "auth_failed",
                ip=request.remote_addr,
                method=request.method,
                path=request.path,
            )

            return Response(
                "Authentication required",
                401,
                {"WWW-Authenticate": 'Basic realm="SignalWire Service"'},
            )

        return decorated

    def get_auth_info(self) -> dict[str, Any]:
        """Get information about configured auth methods"""
        info = {}

        if self.auth_methods.get("basic", {}).get("enabled"):
            info["basic"] = {
                "enabled": True,
                "username": self.auth_methods["basic"]["username"],
            }

        if self.auth_methods.get("bearer", {}).get("enabled"):
            info["bearer"] = {
                "enabled": True,
                "hint": "Use Authorization: Bearer <token>",
            }

        if self.auth_methods.get("api_key", {}).get("enabled"):
            api_config = self.auth_methods["api_key"]
            info["api_key"] = {
                "enabled": True,
                "header": api_config["header"],
                "hint": f"Use {api_config['header']}: <key>",
            }

        return info
