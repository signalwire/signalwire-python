"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import base64
import json
import os
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlsplit

from signalwire.core.logging_config import get_execution_mode
from signalwire.core.function_result import FunctionResult
from signalwire.core.mixins._mixin_host import _HostTyped
from signalwire.core.swaig_function import _resolve_awaitable
from signalwire.core.security.webhook_middleware import (
    _public_url,
    validate,
)

# Maximum allowed CGI request body size (10MB)
MAX_CGI_BODY_SIZE = 10 * 1024 * 1024


@dataclass(frozen=True)
class _ServerlessRequest:
    """One serverless HTTP request, reduced to what the agent needs.

    Each platform adapter (CGI, Lambda, Cloud Functions, Azure Functions, and
    AgentServer's serverless modes) builds one, so routing, the signature and
    token checks, and dispatch work the same way on every platform, and the
    same way as the web server.

    Attributes:
        method: The HTTP method.
        path: The request path below the app's root, e.g. "/agent/swaig/".
        query_string: The raw query string, without the "?".
        url: The full URL the platform received the request on.
        headers: Request headers, with lower-case names.
        body: The raw request body.
        signature_queries: Other raw encodings of the query string to try when
            checking a signature, for platforms that decode the query.
    """

    method: str = "GET"
    path: str = "/"
    query_string: str = ""
    url: str = ""
    headers: Mapping[str, str] = field(default_factory=dict)
    body: str = ""
    signature_queries: tuple[str, ...] = ()

    @property
    def query(self) -> dict[str, str]:
        """The decoded query parameters."""
        return dict(parse_qsl(self.query_string, keep_blank_values=True))


class _RequestTooLarge(ValueError):
    """The request body is larger than MAX_CGI_BODY_SIZE."""


@dataclass(frozen=True)
class _RequestView:
    """What per-call configuration reads from a request: its query and headers."""

    query_params: Mapping[str, str]
    headers: Mapping[str, str]


def _lower_headers(headers: Any) -> dict[str, str]:
    """A platform's headers as a plain dict with lower-case names."""
    try:
        items = list(headers.items())
    except (AttributeError, TypeError):
        return {}
    return {str(name).lower(): str(value) for name, value in items}


def _json_object(body: str) -> dict[str, Any]:
    """The body parsed as a JSON object, or {} if it isn't one."""
    if not body:
        return {}
    try:
        data = json.loads(body)
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def _call_id(data: dict[str, Any]) -> str | None:
    """The call a request belongs to: ``call_id``, or ``call.call_id`` in a SWML fetch."""
    call_id = data.get("call_id")
    if not call_id and isinstance(data.get("call"), dict):
        call_id = data["call"].get("call_id")
    return call_id if isinstance(call_id, str) and call_id else None


def _function_args(data: dict[str, Any]) -> dict[str, Any]:
    """A SWAIG request's arguments, from ``argument.parsed[0]`` or ``argument.raw``."""
    argument = data.get("argument")
    if not isinstance(argument, dict):
        return {}
    args: Any = {}
    parsed = argument.get("parsed")
    if isinstance(parsed, list) and parsed:
        args = parsed[0]
    elif argument.get("raw"):
        try:
            args = json.loads(argument["raw"])
        except (TypeError, ValueError):
            args = {}
    return args if isinstance(args, dict) else {}


def _cgi_response(status: int, body: str) -> str:
    """A complete CGI response: status, headers, a blank line, then the body."""
    return (
        f"Status: {status} {HTTPStatus(status).phrase}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body.encode('utf-8'))}\r\n"
        "\r\n"
        f"{body}"
    )


def _lambda_request(event: Any) -> _ServerlessRequest:
    """Reduce an AWS Lambda event: a function URL, or API Gateway v1 or v2."""
    event = event if isinstance(event, dict) else {}
    context = event.get("requestContext") or {}
    method = (
        (context.get("http") or {}).get("method")
        or event.get("httpMethod")
        or ("POST" if event.get("body") else "GET")
    )

    path = event.get("rawPath") or ""
    if not path and event.get("pathParameters"):
        path = "/" + str((event.get("pathParameters") or {}).get("proxy") or "")
    if not path:
        path = event.get("path") or "/"

    signature_queries: tuple[str, ...] = ()
    if "rawQueryString" in event:
        query_string = str(event.get("rawQueryString") or "")
    else:
        # REST (v1) events carry decoded parameters, so the original encoding
        # is lost: build the "+" form and keep the "%20" form for signatures
        multi = event.get("multiValueQueryStringParameters") or {}
        single = event.get("queryStringParameters") or {}
        pairs = [(k, v) for k, values in multi.items() for v in values] or list(
            single.items()
        )
        query_string = urlencode(pairs)
        signature_queries = (urlencode(pairs, quote_via=quote),)

    body: Any = event.get("body") or ""
    if isinstance(body, str) and event.get("isBase64Encoded"):
        try:
            body = base64.b64decode(body).decode("utf-8")
        except ValueError:
            body = ""
    elif not isinstance(body, str):
        body = json.dumps(body)

    # The URL the platform was called on, for signature checks. REST (v1)
    # events keep the stage in requestContext.path.
    url = ""
    if context.get("domainName"):
        called = (
            event.get("rawPath") or context.get("path") or event.get("path") or path
        )
        url = f"https://{context['domainName']}{called}"
        if query_string:
            url += f"?{query_string}"

    return _ServerlessRequest(
        method=str(method).upper(),
        path=str(path),
        query_string=query_string,
        url=url,
        headers=_lower_headers(event.get("headers")),
        body=body,
        signature_queries=signature_queries,
    )


def _cgi_request() -> _ServerlessRequest:
    """Reduce a CGI request, from the environment and stdin.

    Raises:
        _RequestTooLarge: if CONTENT_LENGTH is over MAX_CGI_BODY_SIZE
    """
    body = ""
    content_length = os.environ.get("CONTENT_LENGTH", "")
    if content_length.isdigit() and int(content_length) > 0:
        size = int(content_length)
        if size > MAX_CGI_BODY_SIZE:
            raise _RequestTooLarge(f"{size} bytes")
        stream: Any = getattr(sys.stdin, "buffer", sys.stdin)
        raw = stream.read(size)
        body = (
            raw.decode("utf-8", errors="replace")
            if isinstance(raw, bytes)
            else str(raw)
        )

    path = os.environ.get("PATH_INFO") or "/"
    query_string = os.environ.get("QUERY_STRING", "")
    scheme = "https" if os.environ.get("HTTPS", "").lower() in ("on", "1") else "http"
    host = os.environ.get("HTTP_HOST") or os.environ.get("SERVER_NAME") or "localhost"
    request_uri = os.environ.get("REQUEST_URI") or (
        os.environ.get("SCRIPT_NAME", "")
        + path
        + (f"?{query_string}" if query_string else "")
    )
    headers = {
        name[len("HTTP_") :].replace("_", "-").lower(): value
        for name, value in os.environ.items()
        if name.startswith("HTTP_")
    }
    if os.environ.get("CONTENT_TYPE"):
        headers["content-type"] = os.environ["CONTENT_TYPE"]

    return _ServerlessRequest(
        method=(
            os.environ.get("REQUEST_METHOD") or ("POST" if body else "GET")
        ).upper(),
        path=path,
        query_string=query_string,
        url=f"{scheme}://{host}{request_uri}",
        headers=headers,
        body=body,
    )


class ServerlessMixin(_HostTyped):  # type: ignore[misc]  # _HostTyped is object at runtime; AgentBase under TYPE_CHECKING — intentional split
    """
    Mixin class containing all serverless/cloud platform methods for AgentBase
    """

    def handle_serverless_request(
        self,
        event: Any = None,
        context: Any = None,
        mode: str | None = None,
    ) -> Any:
        """
        Handle serverless environment requests (CGI, Lambda, Cloud Functions)

        Args:
            event: Serverless event object (Lambda, Cloud Functions)
            context: Serverless context object (Lambda, Cloud Functions)
            mode: Override execution mode (from force_mode in run())

        Returns:
            Response appropriate for the serverless platform: a complete CGI
            response, a Lambda response dict, or the Flask or Azure response
        """
        if mode is None:
            mode = get_execution_mode()

        try:
            if mode == "cgi":
                # Check authentication in CGI mode
                if not self._check_cgi_auth():
                    return self._send_cgi_auth_challenge()
                try:
                    request = _cgi_request()
                except _RequestTooLarge:
                    return _cgi_response(
                        413,
                        json.dumps(
                            {
                                "error": "Request body too large",
                                "max_size": MAX_CGI_BODY_SIZE,
                            }
                        ),
                    )
                return _cgi_response(*self._serverless_response(request))

            if mode == "lambda":
                # Check authentication in Lambda mode
                if not self._check_lambda_auth(event):
                    return self._send_lambda_auth_challenge()
                status, body = self._serverless_response(_lambda_request(event))
                return {
                    "statusCode": status,
                    "headers": {"Content-Type": "application/json"},
                    "body": body,
                }

            if mode == "google_cloud_function":
                # Check authentication in Google Cloud Functions mode
                if not self._check_google_cloud_function_auth(event):
                    return self._send_google_cloud_function_auth_challenge()

                return self._handle_google_cloud_function_request(event)

            if mode == "azure_function":
                # Check authentication in Azure Functions mode
                if not self._check_azure_function_auth(event):
                    return self._send_azure_function_auth_challenge()

                return self._handle_azure_function_request(event)

        except Exception as e:
            import logging
            import traceback

            logging.error(f"Error in serverless request handler: {e}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            if mode == "lambda":
                return {
                    "statusCode": 500,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": str(e)}),
                }
            raise

    def _serverless_response(
        self, request: _ServerlessRequest, relative_path: str | None = None
    ) -> tuple[int, str]:
        """Handle one authenticated serverless request.

        Every serverless platform, and AgentServer's serverless modes, come
        through here, so they follow the web server's rules. The request is
        first resolved to what it asks for: the SWML document, a function, or
        a post-prompt summary. Running a function or delivering a summary
        takes a POST, and every POST needs a valid signature when a
        signing_key is set, whatever its path. A secure function needs its
        token, and so does a summary. Per-call configuration applies to all
        three, with the request's query, headers and body, and the SWML is
        rendered for the call the request names, so the tokens it hands out
        validate later in that call.

        Args:
            request: The platform's request
            relative_path: The path below the agent's route, when the caller
                has already matched the route (AgentServer does). Otherwise it
                is worked out from ``request.path`` and the agent's route.

        Returns:
            The HTTP status and the JSON body
        """
        if relative_path is None:
            relative_path = self._path_below_route(request.path)
        relative_path = relative_path.strip("/")
        method = request.method

        # What the request asks for: /swaig names a function in the body,
        # /swaig/<name> and /<name> in the path
        if relative_path == "post_prompt":
            operation = "summary" if method == "POST" else "swml"
        elif relative_path == "swaig":
            operation = "function" if method == "POST" else "swml"
        elif relative_path:
            operation = "function"
        else:
            operation = "swml"

        if method not in ("GET", "POST") or (operation != "swml" and method != "POST"):
            return 405, json.dumps({"error": "Method not allowed"})
        if method == "POST" and self._serverless_signature_rejected(request):
            return 403, json.dumps({"error": "Forbidden"})

        data = _json_object(request.body)
        query = request.query
        headers = dict(request.headers)
        token = query.get("__token") or query.get("token")

        if operation == "summary":
            status, payload = self._post_prompt_response(
                data,
                query.get("call_id"),
                token,
                query,
                headers,
                self.log.bind(endpoint="post_prompt"),
            )
            return status, json.dumps(payload)

        if operation == "swml":
            # The SWML fetch names its call in the body, or a GET in the query
            call_id = _call_id(data) or query.get("call_id") or None
            # on_swml_request's contract is a FastAPI request or None, so an
            # override gets None here, as it always has on serverless. The
            # per-call config it asks for still sees the query and headers.
            modifications = self.on_swml_request(data or None, None, None)
            if (
                isinstance(modifications, dict)
                and modifications.get("__use_ephemeral_agent")
                and modifications.get("__request") is None
            ):
                modifications = {
                    **modifications,
                    "__request": _RequestView(query, headers),
                }
            swml = self._render_swml(call_id=call_id, modifications=modifications)
            return 200, swml if isinstance(swml, str) else json.dumps(swml)

        if relative_path == "swaig":
            function_name = data.get("function")
            if not isinstance(function_name, str) or not function_name:
                return 400, json.dumps({"error": "Missing function name"})
        elif relative_path.startswith("swaig/"):
            function_name = relative_path[len("swaig/") :]
        else:
            function_name = relative_path

        # As on the web server, a function call names its call in the body,
        # and the token is checked against the agent that will run it
        call_id = _call_id(data)
        target = self._per_call_agent(query, data, headers)
        rejection = target._tool_token_rejection(function_name, token, call_id)
        if rejection is not None:
            return 200, json.dumps(rejection)

        result = target._execute_swaig_function(
            function_name, _function_args(data), call_id, data or None
        )
        return 200, json.dumps(result) if isinstance(result, dict) else str(result)

    def _path_below_route(self, path: str) -> str:
        """The request path below the agent's route, without slashes."""
        relative = path.strip("/")
        route = str(getattr(self, "route", "") or "").strip("/")
        if route and (relative == route or relative.startswith(route + "/")):
            relative = relative[len(route) :].strip("/")
        return relative

    def _serverless_signature_rejected(self, request: _ServerlessRequest) -> bool:
        """True when a signing_key is set and the request isn't validly signed.

        The URL is rebuilt by the web server's rules: SWML_PROXY_URL_BASE
        joined with the path below the app's root, then forwarded headers when
        trust_proxy_for_signature is set, then the URL the platform reports.
        """
        signing_key = getattr(self, "signing_key", None)
        if not signing_key:
            return False
        # A platform that hands over decoded query parameters (API Gateway
        # REST) loses the original encoding, so each plausible one is tried.
        for query in dict.fromkeys((request.query_string, *request.signature_queries)):
            platform_url = (
                urlsplit(request.url)._replace(query=query).geturl()
                if request.url
                else ""
            )
            path_and_query = request.path + (f"?{query}" if query else "")
            url = _public_url(
                platform_url,
                request.headers,
                trust_proxy=getattr(self, "_trust_proxy_for_signature", False),
                path_and_query=path_and_query,
            )
            if (
                validate(
                    request.method,
                    url,
                    request.headers,
                    request.body,
                    signing_key=signing_key,
                )
                is None
            ):
                return False
        return True

    def _execute_swaig_function(
        self,
        function_name: str,
        args: dict[str, Any] | None = None,
        call_id: str | None = None,
        raw_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a SWAIG function in serverless context

        Args:
            function_name: Name of the function to execute
            args: Function arguments dictionary
            call_id: Optional call ID
            raw_data: Optional raw request data

        Returns:
            Function execution result
        """
        # Validate function name format before dispatch
        if function_name and not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", function_name):
            return {"error": f"Invalid function name format: '{function_name}'"}

        # Use the existing logger
        req_log = self.log.bind(endpoint="serverless_swaig", function=function_name)

        if call_id:
            req_log = req_log.bind(call_id=call_id)

        req_log.debug("serverless_function_call_received")

        try:
            # Validate function exists
            if function_name not in self._tool_registry._swaig_functions:
                req_log.warning(
                    "function_not_found",
                    available_functions=list(
                        self._tool_registry._swaig_functions.keys()
                    ),
                )
                return {"error": f"Function '{function_name}' not found"}

            # Use empty args if not provided
            if args is None:
                args = {}

            # Use empty raw_data if not provided, but include function call structure
            if raw_data is None:
                raw_data = {
                    "function": function_name,
                    "argument": {
                        "parsed": [args] if args else [],
                        "raw": json.dumps(args) if args else "{}",
                    },
                }
                if call_id:
                    raw_data["call_id"] = call_id

            req_log.debug("executing_function", args=json.dumps(args))

            # Call the function using the existing on_function_call method,
            # running an async handler to completion
            result = _resolve_awaitable(
                self.on_function_call(function_name, args, raw_data)
            )

            # Convert result to dict if needed (same logic as in _handle_swaig_request)
            if isinstance(result, FunctionResult):
                result_dict = result.to_dict()
            elif isinstance(result, dict):
                result_dict = result
            else:
                req_log.warning(
                    "unexpected_function_result_type",
                    function=function_name,
                    result_type=type(result).__name__,
                    hint=(
                        "SWAIG function returned a value that is neither "
                        "FunctionResult nor dict; falling back to str(result). "
                        "The AI will see the stringified value as its tool "
                        "response. Wrap your return in FunctionResult(...) or "
                        "return a dict with at least a 'response' key."
                    ),
                )
                result_dict = {"response": str(result)}

            req_log.info("serverless_function_executed_successfully")
            req_log.debug("function_result", result=json.dumps(result_dict))
            return result_dict

        except Exception as e:
            req_log.error("serverless_function_execution_error", error=str(e))
            return {"error": str(e), "function": function_name}

    def _handle_google_cloud_function_request(self, request: Any) -> Any:
        """
        Handle Google Cloud Functions specific requests

        Args:
            request: Flask request object from Google Cloud Functions

        Returns:
            Flask response object
        """
        try:
            from flask import Response

            # Detect the base URL from the request, so the SWML's webhook URLs
            # point back here
            base_url = None
            if hasattr(request, "url") and request.url:
                parsed = urlparse(request.url)
                base_url = f"{parsed.scheme}://{parsed.netloc}"
            if base_url and not getattr(self, "_proxy_url_base_from_env", False):
                self._proxy_url_base = base_url

            raw = request.get_data(as_text=True) if request.method == "POST" else ""
            query_string = getattr(request, "query_string", b"")
            status, body = self._serverless_response(
                _ServerlessRequest(
                    method=str(request.method).upper(),
                    path=str(request.path or "/"),
                    query_string=(
                        query_string.decode("utf-8", errors="replace")
                        if isinstance(query_string, bytes)
                        else query_string
                        if isinstance(query_string, str)
                        else ""
                    ),
                    url=request.url if isinstance(request.url, str) else "",
                    headers=_lower_headers(getattr(request, "headers", None)),
                    body=(
                        raw.decode("utf-8", errors="replace")
                        if isinstance(raw, bytes)
                        else str(raw or "")
                    ),
                )
            )
            return Response(
                response=body,
                status=status,
                headers={"Content-Type": "application/json"},
            )

        except Exception as e:
            import logging

            logging.error(f"Error in Google Cloud Function request handler: {e}")
            from flask import Response

            return Response(
                response=json.dumps({"error": str(e)}),
                status=500,
                headers={"Content-Type": "application/json"},
            )

    def _handle_azure_function_request(self, req: Any) -> Any:
        """
        Handle Azure Functions specific requests

        Args:
            req: Azure Functions HttpRequest object

        Returns:
            Azure Functions HttpResponse object
        """
        try:
            import azure.functions as func

            # Azure Functions URLs look like: https://app.azurewebsites.net/api/function_name/path
            # The path is read from the parsed URL, without its query string.
            path = ""
            base_url = None
            url = req.url if isinstance(req.url, str) else ""
            if url:
                parsed = urlparse(url)
                api_path = parsed.path.split("/api/", 1)
                if len(api_path) > 1:
                    # Split into the function app name and the path below it
                    function_app_name, _, path = api_path[1].strip("/").partition("/")

                    # Base URL includes the function app name for webhook URLs
                    # e.g., https://app.azurewebsites.net/api/function_app
                    base_url = (
                        f"{parsed.scheme}://{parsed.netloc}/api/{function_app_name}"
                    )
                else:
                    base_url = f"{parsed.scheme}://{parsed.netloc}/api"

            # Set the proxy URL base so SWML renders correct webhook URLs
            if base_url and not getattr(self, "_proxy_url_base_from_env", False):
                self._proxy_url_base = base_url

            raw = req.get_body() if req.method == "POST" else b""
            status, body = self._serverless_response(
                _ServerlessRequest(
                    method=str(req.method).upper(),
                    path="/" + path,
                    query_string=urlsplit(url).query,
                    url=url,
                    headers=_lower_headers(getattr(req, "headers", None)),
                    body=(
                        raw.decode("utf-8", errors="replace")
                        if isinstance(raw, bytes)
                        else str(raw or "")
                    ),
                )
            )
            return func.HttpResponse(
                body=body,
                status_code=status,
                headers={"Content-Type": "application/json"},
            )

        except Exception as e:
            import logging

            logging.error(f"Error in Azure Function request handler: {e}")
            import azure.functions as func

            return func.HttpResponse(
                body=json.dumps({"error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"},
            )
