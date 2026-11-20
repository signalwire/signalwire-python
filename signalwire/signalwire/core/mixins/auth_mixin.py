"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import os
import hmac
import json
import base64
from typing import Any

from fastapi import Request


from signalwire.core.mixins._mixin_host import _HostTyped


class AuthMixin(_HostTyped):  # type: ignore[misc]  # _HostTyped is object at runtime; AgentBase under TYPE_CHECKING — intentional split
    """
    Mixin class containing all authentication-related methods for AgentBase.
    """

    def validate_basic_auth(self, username: str, password: str) -> bool:
        """Validate a username and password against the agent's Basic Auth credentials.

        The comparison is constant-time (`hmac.compare_digest`), which guards
        against timing attacks.

        Note:
            This method is an override point. A subclass can replace it with
            custom authentication logic, such as a database lookup or an external
            identity provider. The rest of the auth pipeline keeps calling it.

        Args:
            username: Username from the request's `Authorization` header.
            password: Password from the request's `Authorization` header.

        Returns:
            True if the credentials are valid, False otherwise. Returns False
            when the agent has no credentials configured.

        Example:
            ```python
            is_valid = agent.validate_basic_auth("admin", "secret123")
            ```

        Example:
            ```python
            class SecureAgent(AgentBase):
                def validate_basic_auth(self, username: str, password: str) -> bool:
                    # Look up credentials in an external user store.
                    return username == "admin" and password == "secret123"
            ```
        """
        exp_user, exp_pass = self._basic_auth
        if exp_user is None or exp_pass is None:
            return False
        return hmac.compare_digest(username, exp_user) and hmac.compare_digest(
            password, exp_pass
        )

    def get_basic_auth_credentials(
        self, include_source: bool = False
    ) -> tuple[str, str] | tuple[str, str, str]:
        """Get the username and password used for HTTP Basic Auth on this agent.

        Credentials are auto-generated unless the `SWML_BASIC_AUTH_USER` and
        `SWML_BASIC_AUTH_PASSWORD` environment variables are set.

        Args:
            include_source: When True, the returned tuple has a third element
                naming where the credentials came from: `"provided"` (set
                explicitly), `"environment"` (the `SWML_BASIC_AUTH_USER` and
                `SWML_BASIC_AUTH_PASSWORD` variables), `"config file"`, or
                `"generated"` (auto-generated at startup). Defaults to False.

        Returns:
            `(username, password)` when `include_source` is False, or
            `(username, password, source)` when it is True.

        Example:
            ```python
            user, password = agent.get_basic_auth_credentials()
            ```

        Example:
            ```python
            user, password, source = agent.get_basic_auth_credentials(
                include_source=True
            )
            if source == "generated":
                print(f"Auto-generated credentials: {user}:{password}")
            ```
        """
        username, password = self._basic_auth

        if not include_source:
            return (username, password)

        # Recorded when the credentials were resolved, in SWMLService.__init__
        source = getattr(self, "_basic_auth_source", "provided")
        return (username, password, source)

    def _check_basic_auth(self, request: Request) -> bool:
        """
        Check basic auth from a request

        Args:
            request: FastAPI request object

        Returns:
            True if auth is valid, False otherwise
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return False

        try:
            # Decode the base64 credentials
            credentials = base64.b64decode(auth_header[6:]).decode("utf-8")
            username, password = credentials.split(":", 1)
            return self.validate_basic_auth(username, password)
        except Exception:
            return False

    def _check_cgi_auth(self) -> bool:
        """
        Check basic auth in CGI mode using environment variables

        Returns:
            True if auth is valid, False otherwise
        """
        # Check for HTTP_AUTHORIZATION environment variable
        auth_header = os.getenv("HTTP_AUTHORIZATION")
        if not auth_header:
            # Only trust REMOTE_USER if explicitly configured
            remote_user = os.getenv("REMOTE_USER")
            return bool(
                remote_user
                and os.getenv("SWML_TRUST_REMOTE_USER", "").lower()
                in ("1", "true", "yes")
            )

        if not auth_header.startswith("Basic "):
            return False

        try:
            # Decode the base64 credentials
            credentials = base64.b64decode(auth_header[6:]).decode("utf-8")
            username, password = credentials.split(":", 1)
            return self.validate_basic_auth(username, password)
        except Exception:
            return False

    def _send_cgi_auth_challenge(self) -> str:
        """
        Send authentication challenge in CGI mode

        Returns:
            HTTP response with 401 status and WWW-Authenticate header
        """
        # In CGI, we need to output the complete HTTP response
        response = "Status: 401 Unauthorized\r\n"
        response += 'WWW-Authenticate: Basic realm="SignalWire Agent"\r\n'
        response += "Content-Type: application/json\r\n"
        response += "\r\n"
        response += json.dumps({"error": "Unauthorized"})
        return response

    def _check_lambda_auth(self, event: dict[str, Any] | None) -> bool:
        """
        Check basic auth in Lambda mode using event headers

        Args:
            event: Lambda event object containing headers

        Returns:
            True if auth is valid, False otherwise
        """
        if not event or "headers" not in event:
            return False

        headers = event["headers"]

        # Check for authorization header (case-insensitive)
        auth_header = None
        for key, value in headers.items():
            if key.lower() == "authorization":
                auth_header = value
                break

        if not auth_header or not auth_header.startswith("Basic "):
            return False

        try:
            # Decode the base64 credentials
            credentials = base64.b64decode(auth_header[6:]).decode("utf-8")
            username, password = credentials.split(":", 1)
            return self.validate_basic_auth(username, password)
        except Exception:
            return False

    def _send_lambda_auth_challenge(self) -> dict[str, Any]:
        """
        Send authentication challenge in Lambda mode

        Returns:
            Lambda response with 401 status and WWW-Authenticate header
        """
        return {
            "statusCode": 401,
            "headers": {
                "WWW-Authenticate": 'Basic realm="SignalWire Agent"',
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": "Unauthorized"}),
        }

    def _check_google_cloud_function_auth(self, request: Any) -> bool:
        """
        Check basic auth in Google Cloud Functions mode using request headers

        Args:
            request: Flask request object or similar containing headers

        Returns:
            True if auth is valid, False otherwise
        """
        if not hasattr(request, "headers"):
            return False

        # Check for authorization header (case-insensitive)
        # Flask headers can be accessed directly with .get() which is case-insensitive
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Basic "):
            return False

        try:
            import base64

            encoded_credentials = auth_header[6:]  # Remove 'Basic '
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            provided_username, provided_password = decoded_credentials.split(":", 1)

            return self.validate_basic_auth(provided_username, provided_password)
        except Exception:
            return False

    def _send_google_cloud_function_auth_challenge(self) -> Any:
        """
        Send authentication challenge in Google Cloud Functions mode

        Returns:
            Flask-compatible response with 401 status and WWW-Authenticate header
        """
        from flask import Response

        return Response(
            response=json.dumps({"error": "Unauthorized"}),
            status=401,
            headers={
                "WWW-Authenticate": 'Basic realm="SignalWire Agent"',
                "Content-Type": "application/json",
            },
        )

    def _check_azure_function_auth(self, req: Any) -> bool:
        """
        Check basic auth in Azure Functions mode using request object

        Args:
            req: Azure Functions request object containing headers

        Returns:
            True if auth is valid, False otherwise
        """
        if not hasattr(req, "headers"):
            return False

        # Check for authorization header - use .get() which works with both dict and Flask headers
        auth_header = req.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Basic "):
            return False

        try:
            import base64

            encoded_credentials = auth_header[6:]  # Remove 'Basic '
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            provided_username, provided_password = decoded_credentials.split(":", 1)

            return self.validate_basic_auth(provided_username, provided_password)
        except Exception:
            return False

    def _send_azure_function_auth_challenge(self) -> Any:
        """
        Send authentication challenge in Azure Functions mode

        Returns:
            Azure Functions response with 401 status and WWW-Authenticate header
        """
        import azure.functions as func

        return func.HttpResponse(
            body=json.dumps({"error": "Unauthorized"}),
            status_code=401,
            headers={
                "WWW-Authenticate": 'Basic realm="SignalWire Agent"',
                "Content-Type": "application/json",
            },
        )
