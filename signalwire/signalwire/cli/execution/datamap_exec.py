#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

DataMap function execution and template expansion

swaig-test runs a DataMap function locally the way SignalWire's platform
runs it during a call:

1. The top-level ``expressions``, against the call data. The first one that
   produces an output ends the function.
2. The first webhook it requests. Webhooks are skipped, without a request,
   only when none of their ``require_args`` are present or they have neither
   ``output`` nor ``expressions``. Once one is requested, no later webhook
   runs. If it succeeds, its ``foreach``, then its ``expressions``, then its
   ``output`` build the result from the response.
3. The top-level ``output``, when nothing above produced one.
4. Otherwise the platform's generic error.

Templates read one of two sets of data. The top-level ``expressions`` and
``output``, and a webhook's ``url`` and ``params``, read the call data, where
the arguments are ``${args.x}``. A webhook's ``foreach``, ``expressions`` and
``output`` read the response, with ``prompt_vars``, ``global_data`` and
``input``, a copy of the call data, added to it; the arguments are
``${input.args.x}`` there.
"""

import json
import re
import sys
from copy import deepcopy
from typing import Any
from urllib.parse import unquote, urljoin, urlsplit

import requests

# The generic result the platform returns when nothing produced an output
PLATFORM_ERROR_RESPONSE = "There was an error processing this request."

# The platform's request timeouts, in seconds: connecting, then the whole request
_CONNECT_TIMEOUT = 30
_TOTAL_TIMEOUT = 120

# Characters FreeSWITCH's switch_url_encode() percent-encodes, besides control
# characters and bytes outside printable ASCII (SWITCH_URL_UNSAFE)
_URL_UNSAFE = frozenset('\r\n #%&+:;<=>?@[\\]^`{|}"')
_UPPER_HEX = b"0123456789ABCDEF"

# Template paths longer than this, or deeper than this, don't resolve
_MAX_PATH_LENGTH = 1024
_MAX_PATH_DEPTH = 128
_INT_MAX = 2**31 - 1

_ASCII_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")
_STRTOL_INDEX = re.compile(r"[ \t\n\v\f\r]*[+-]?[0-9]+")


class _Missing:
    """Marks a template path that doesn't resolve."""

    def __repr__(self) -> str:
        return "<missing>"


_MISSING = _Missing()

# The stages that read a webhook's response rather than the call data
_RESPONSE_STAGES = frozenset(
    {"webhook foreach", "webhook expressions", "webhook output"}
)


def _ascii_lower(text: str) -> str:
    """Lowercase ASCII letters only, as C's tolower() does."""
    return text.translate(_ASCII_LOWER)


def _object_item(container: Any, name: str) -> Any:
    """A named member of an object, matched without regard to ASCII case.

    Like cJSON_GetObjectItem(), the first match wins, and arrays and scalars
    have no named members.
    """
    if not isinstance(container, dict):
        return _MISSING
    wanted = _ascii_lower(name)
    for key, value in container.items():
        if _ascii_lower(str(key)) == wanted:
            return value
    return _MISSING


def _has_item(container: Any, name: str) -> bool:
    return _object_item(container, name) is not _MISSING


def _add_item(container: dict[str, Any], name: str, value: Any) -> None:
    """Add a member the way cJSON_AddItemToObject() does.

    cJSON appends a second member with the same name, and lookups find the
    first, so an existing member keeps its value.
    """
    if not _has_item(container, name):
        container[name] = value


def _delete_item(container: dict[str, Any], name: str) -> None:
    """Delete the first member matching ``name`` without regard to ASCII case."""
    wanted = _ascii_lower(name)
    for key in list(container):
        if _ascii_lower(str(key)) == wanted:
            del container[key]
            return


def _string_item(container: Any, name: str) -> str | None:
    """A member's value if it's a string, as cJSON_GetObjectCstr() returns it."""
    value = _object_item(container, name)
    return value if isinstance(value, str) else None


def _switch_true(text: str) -> bool:
    """FreeSWITCH's switch_true()."""
    if text.lower() in ("yes", "on", "true", "t", "enabled", "active", "allow"):
        return True
    return (
        bool(re.fullmatch(r"[+-]?[0-9]+(\.[0-9]+)?", text.strip())) and _atoi(text) != 0
    )


def _atoi(text: str) -> int:
    """C's atoi(): the leading integer, or 0."""
    match = re.match(r"[ \t\n\v\f\r]*([+-]?[0-9]+)", text)
    return int(match.group(1)) if match else 0


def _is_true(value: Any) -> bool:
    """mod_openai's cJSON_FSTrue(): JSON true, or a string switch_true() accepts."""
    return value is True or (isinstance(value, str) and _switch_true(value))


def _cjson_string(text: str) -> str:
    """A string as cJSON prints it."""
    escapes = {
        '"': '\\"',
        "\\": "\\\\",
        "\b": "\\b",
        "\f": "\\f",
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
    }
    parts = []
    for char in text:
        if char in escapes:
            parts.append(escapes[char])
        elif ord(char) < 32:
            parts.append(f"\\u{ord(char):04x}")
        else:
            parts.append(char)
    return '"' + "".join(parts) + '"'


def _cjson_print(value: Any, depth: int = 0) -> str:
    """A value as cJSON_Print() formats it.

    Whole numbers print without a decimal point, other numbers with six
    decimal places (72.5 is 72.500000), and objects over several lines, one
    tab per level.
    """
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        number = float(value)
        if number != number or number in (float("inf"), float("-inf")):
            return "null"
        if number.is_integer():
            return str(int(number))
        return f"{number:f}"
    if isinstance(value, str):
        return _cjson_string(value)
    if isinstance(value, list):
        return "[" + ", ".join(_cjson_print(item, depth + 1) for item in value) + "]"
    if isinstance(value, dict):
        inner = depth + 1
        members = [
            "\t" * inner + _cjson_string(str(key)) + ":\t" + _cjson_print(item, inner)
            for key, item in value.items()
        ]
        if not members:
            return "{\n" + "\t" * depth + "}"
        return "{\n" + ",\n".join(members) + "\n" + "\t" * depth + "}"
    return _cjson_string(str(value))


def _cjson_parse(text: str) -> Any:
    """Parse JSON as cJSON_Parse() does, or return _MISSING.

    cJSON skips a byte order mark and leading whitespace, accepts control
    characters inside strings, and ignores anything after the first value.
    """
    text = text.lstrip("\ufeff")
    text = text.lstrip("".join(chr(code) for code in range(33)))
    try:
        value, _ = json.JSONDecoder(strict=False).raw_decode(text)
    except ValueError:
        return _MISSING
    return value


def _url_encode(value: str) -> str:
    """URL-encode as FreeSWITCH's switch_url_encode() does.

    It percent-encodes control characters, bytes outside printable ASCII, and
    ``\\r \\n space # % & + : ; < = > ? @ [ \\ ] ^ ` { | } "``, and leaves the
    rest, including ``/ , $ ! ' ( ) *``. A ``%`` followed by two uppercase hex
    digits is left as it is, so an encoded value isn't encoded twice.
    """
    raw = value.encode("utf-8")
    last = len(raw) - 1
    parts = []
    for index, byte in enumerate(raw):
        if (
            byte == 0x25
            and last - index > 1
            and raw[index + 1] in _UPPER_HEX
            and raw[index + 2] in _UPPER_HEX
        ):
            parts.append("%")
        elif byte < 0x20 or byte > 0x7E or chr(byte) in _URL_UNSAFE:
            parts.append(f"%{byte:02X}")
        else:
            parts.append(chr(byte))
    return "".join(parts)


def _format_phone_national(value: str) -> str:
    """The ``fmt_ph`` helper, for North American numbers.

    The platform formats with libphonenumber in the national format, assuming
    the US for a number without a country code, and gives ``INVALID NUMBER``
    for one it can't validate. The simulation formats a ten-digit North
    American number, with or without its leading 1, as ``(NPA) NXX-XXXX``,
    and leaves anything else as it is.
    """
    digits = re.sub(r"[^0-9]", "", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10 and digits[0] in "23456789" and digits[3] in "23456789":
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return value


def _find_end_brace(text: str, start: int) -> int:
    """The index of the ``}`` matching the ``{`` at ``start``, or -1."""
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return -1


def _lookup(data: Any, path: str) -> Any:
    """The value at a template path, or _MISSING, as get_json_object() finds it.

    Dots separate names, matched without regard to ASCII case. One ``[n]``
    may follow a name, and a negative ``n`` counts from the end. A path
    ending in a dot doesn't resolve, and an empty path is the whole data.
    """
    if len(path.encode("utf-8")) > _MAX_PATH_LENGTH or path.endswith("."):
        return _MISSING
    current = data
    for depth, token in enumerate((part for part in path.split(".") if part), start=1):
        if depth > _MAX_PATH_DEPTH:
            return _MISSING
        if "[" not in token:
            current = _object_item(current, token)
            if current is _MISSING:
                return _MISSING
            continue
        name, rest = token.split("[", 1)
        close = rest.find("]")
        if close < 0:
            return _MISSING
        index_text = rest[:close]
        if rest[close + 1 :] or not _STRTOL_INDEX.fullmatch(index_text):
            return _MISSING
        index = int(index_text)
        if index > _INT_MAX:
            return _MISSING
        current = _object_item(current, name)
        if not isinstance(current, list):
            return _MISSING
        if index < 0:
            index += len(current)
        if not 0 <= index < len(current):
            return _MISSING
        current = current[index]
    return current


def _value_text(value: Any, escape_json: bool) -> str:
    """A resolved value as a template inserts it.

    A string goes in as it is, with ``"`` and ``\\`` backslash-escaped when
    the template is JSON text. Anything else goes in as cJSON prints it,
    without escaping.
    """
    if isinstance(value, str):
        if escape_json:
            return value.replace("\\", "\\\\").replace('"', '\\"')
        return value
    return _cjson_print(value)


def _expand(
    template: str,
    data: Any,
    escape_json: bool = False,
    nested: bool = True,
    unresolved: list[tuple[str, str]] | None = None,
) -> str:
    """Expand ``${...}`` and ``%{...}`` templates as mod_openai's expander does."""
    parts: list[str] = []
    index = 0
    length = len(template)
    while index < length:
        char = template[index]
        if char not in "$%" or index + 1 >= length or template[index + 1] != "{":
            parts.append(char)
            index += 1
            continue
        end = _find_end_brace(template, index + 1)
        if end < 0:
            # No closing brace: the text stays as written
            parts.append(char)
            index += 1
            continue
        if end == index + 2:
            # ${} expands to nothing
            index = end + 1
            continue

        body = template[index + 2 : end]
        lowercase = encode = phone = False
        while True:
            head = _ascii_lower(body[:7])
            if head.startswith("lc:"):
                body, lowercase = body[3:], True
            elif head == "fmt_ph:":
                body, phone = body[7:], True
            elif head.startswith("enc:"):
                body, encode = body[4:], True
            else:
                break

        path = body
        if nested and ("${" in path or "%{" in path):
            path = _expand(path, data, escape_json, nested=False)

        value = _lookup(data, path)
        if value is _MISSING:
            if unresolved is not None:
                unresolved.append((template[index : end + 1], path))
        else:
            text = _value_text(value, escape_json)
            # The helpers apply in this order, whatever order they're written in
            if phone and text:
                text = _format_phone_national(text)
            if lowercase and text:
                text = _ascii_lower(text)
            if encode and text:
                text = _url_encode(text)
            parts.append(text)
        index = end + 1
    return "".join(parts)


def simple_template_expand(
    template: str,
    data: dict[str, Any],
    unresolved: list[tuple[str, str]] | None = None,
) -> str:
    """
    Expand DataMap templates as the platform does, for local testing.

    ``${path}`` and ``%{path}`` read a value from ``data``. A path uses dots
    for names, matched without regard to case, and ``[n]`` for an array
    element, where a negative ``n`` counts from the end. A path that doesn't
    resolve expands to an empty string, and is added to ``unresolved`` when
    it's given, as a (template, path) pair.

    Prefix helpers before the path transform the value: ``lc`` lowercases,
    ``enc`` URL-encodes as FreeSWITCH does, and ``fmt_ph`` formats a phone
    number. They're matched without regard to case, and apply in a fixed
    order, ``fmt_ph``, then ``lc``, then ``enc``, whatever order they're
    written in. There's no ``enc:url``: that reads the path ``url:...``.

    A template nested in a path expands first, one level deep, and its value
    becomes part of the path: ``${meta_data.table.${lc:args.target}}``.
    A value that isn't a string is inserted as JSON. ``@{...}`` functions are
    left as they are.

    Args:
        template: Template string with ${} or %{} variables
        data: Data dictionary for expansion
        unresolved: Optional list to collect templates that didn't resolve

    Returns:
        Expanded string
    """
    if not template:
        return ""
    return _expand(template, data, unresolved=unresolved)


class _Run:
    """One simulated call of a DataMap function."""

    def __init__(self, verbose: bool) -> None:
        self.verbose = verbose
        self.unresolved: list[tuple[str, str, str]] = []

    def log(self, message: str) -> None:
        if self.verbose:
            print(message)

    def expand(
        self, template: str, data: Any, stage: str, escape_json: bool = False
    ) -> str:
        found: list[tuple[str, str]] = []
        text = _expand(template, data, escape_json, unresolved=found)
        self.unresolved.extend((raw, path, stage) for raw, path in found)
        return text

    def expand_json(self, value: Any, data: Any, stage: str) -> Any:
        """Expand an output or expression result as JSON text, then parse it."""
        text = self.expand(_cjson_print(value), data, stage, escape_json=True)
        return _cjson_parse(text)

    def report_unresolved(self) -> None:
        """Say which templates expanded to nothing, with a hint for common mistakes."""
        seen: set[tuple[str, str]] = set()
        for raw, path, stage in self.unresolved:
            if (raw, stage) in seen:
                continue
            seen.add((raw, stage))
            note = f"Note: {raw} in the {stage} expands to an empty string on the platform."
            lowered = _ascii_lower(path)
            if lowered.startswith("response."):
                note += (
                    " The platform reads a webhook's JSON response from the root: "
                    "write ${<field>}, not ${response.<field>}."
                )
            elif stage in _RESPONSE_STAGES and lowered.startswith("args."):
                note += (
                    " In a webhook's foreach, expressions and output, the arguments are "
                    "under input: write ${input." + path + "}."
                )
            elif stage not in _RESPONSE_STAGES and lowered.startswith("input."):
                note += (
                    " input is empty until a webhook responds; read the call data "
                    "directly here, as ${" + path[len("input.") :] + "}."
                )
            print(note, file=sys.stderr)


def _regex_match(target: str, pattern: str) -> bool:
    """FreeSWITCH's switch_regex_match() with a /pattern/flags expression."""
    flags = 0
    if pattern.startswith("/"):
        body = pattern[1:]
        close = body.rfind("/")
        if close < 0:
            return False
        options = body[close + 1 :]
        pattern = body[:close]
        if "i" in options:
            flags |= re.IGNORECASE
        if "s" in options:
            flags |= re.DOTALL
    try:
        return re.search(pattern, target, flags) is not None
    except re.error:
        return False


def _parse_expression(run: _Run, item: Any, data: Any, stage: str) -> Any:
    """One expression's result, or _MISSING when it produces none."""
    string = _string_item(item, "string")
    pattern = _string_item(item, "pattern")
    expr = _string_item(item, "expr")
    if string is None:
        if expr is None:
            # With neither string nor expr, an expression never matches
            return _MISSING
        string = expr
    output = _object_item(item, "output")
    nomatch_output = _object_item(item, "nomatch-output")
    if output is _MISSING:
        return _MISSING

    subject = run.expand(string, data, stage)
    matched = False
    if expr is not None:
        print(
            f"Note: swaig-test doesn't evaluate expr ({expr!r}); treating it as no match.",
            file=sys.stderr,
        )
    if not matched and pattern is not None:
        # A pattern not written as /.../flags is matched without regard to case
        use_pattern = pattern if pattern.startswith("/") else f"/{pattern}/i"
        matched = _regex_match(subject, use_pattern)
        run.log(
            f"Expression {subject!r} against {use_pattern}: {'match' if matched else 'no match'}"
        )

    if matched:
        return run.expand_json(output, data, stage)
    if nomatch_output is not _MISSING:
        return run.expand_json(nomatch_output, data, stage)
    return _MISSING


def _run_expressions(run: _Run, expressions: Any, data: Any, stage: str) -> Any:
    """The first expression result, or _MISSING."""
    if isinstance(expressions, list):
        for item in expressions:
            reply = _parse_expression(run, item, data, stage)
            if reply is not _MISSING:
                return reply
        return _MISSING
    return _parse_expression(run, expressions, data, stage)


def _any_present(keys: Any, container: Any) -> bool:
    """mod_openai's args_present(): whether any of the named keys is present."""
    if keys is None or container is None:
        return False
    if isinstance(keys, list):
        return any(isinstance(key, str) and _has_item(container, key) for key in keys)
    return isinstance(keys, str) and _has_item(container, keys)


def _curl_error_code(error: Exception) -> int:
    """A curl result code standing in for a request exception."""
    if isinstance(error, requests.Timeout):
        return 28
    if isinstance(error, requests.TooManyRedirects):
        return 47
    if isinstance(error, requests.exceptions.SSLError):
        return 35
    if isinstance(error, requests.ConnectionError):
        return 7
    return 1


# The platform follows this many redirects (CURLOPT_MAXREDIRS)
_MAX_REDIRECTS = 15

_DEFAULT_PORTS = {"http": 80, "https": 443}


def _origin(url: str) -> tuple[str, str, int | None]:
    """The URL's scheme, host (lowercased) and port, the default filled in."""
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    return (
        scheme,
        (parts.hostname or "").lower(),
        parts.port or _DEFAULT_PORTS.get(scheme),
    )


def _send(
    run: _Run,
    url: str,
    post: bool,
    body: str | None,
    headers: dict[str, str],
    auth: Any,
) -> requests.Response:
    """Send the webhook's request, following redirects as the platform does.

    The platform follows up to 15 redirects and sends a POST again, with its
    body, after any of them (CURL_REDIR_POST_ALL); it follows none for a
    request it signs, which this doesn't simulate. Every request, redirects
    included, goes through the session that refuses private and internal
    addresses, as the SDK's other fetches of user-supplied URLs do. Like
    curl, it sends credentials only to the origin they were given for (the
    same scheme, host and port), so never over a redirect to plain HTTP.
    """
    from signalwire.utils.url_validator import _PublicSession

    timeout = (_CONNECT_TIMEOUT, _TOTAL_TIMEOUT)
    method = "POST" if post else "GET"
    origin = _origin(url)
    with _PublicSession() as session:
        for _ in range(_MAX_REDIRECTS + 1):
            same_host = _origin(url) == origin
            send_headers = (
                headers
                if same_host
                else {
                    name: value
                    for name, value in headers.items()
                    if name.lower() not in ("authorization", "cookie")
                }
            )
            response = session.request(
                method,
                url,
                data=body if post else None,
                headers=send_headers,
                auth=auth if same_host else None,
                timeout=timeout,
                allow_redirects=False,
            )
            location = response.headers.get("location")
            if not response.is_redirect or not location:
                return response
            url = urljoin(url, location)
            run.log(f"Following redirect ({response.status_code}) to: {url}")
    raise requests.TooManyRedirects(f"More than {_MAX_REDIRECTS} redirects")


def _request(run: _Run, webhook: Any, call_data: dict[str, Any]) -> Any:
    """Send one webhook's request as parse_webhook() does, and return its reply.

    Returns _MISSING when the webhook has no url, so no request is made.
    """
    url = _string_item(webhook, "url")
    if url is None:
        return _MISSING
    method = _string_item(webhook, "method")
    form_param = _string_item(webhook, "form_param")
    params = _object_item(webhook, "params")
    headers = _object_item(webhook, "headers")

    if _is_true(_object_item(webhook, "input_args_as_params")):
        args = _object_item(call_data, "args")
        if args is not _MISSING:
            if isinstance(params, dict) and isinstance(args, dict):
                merged = deepcopy(params)
                for key, value in args.items():
                    _delete_item(merged, key)
                    merged[key] = deepcopy(value)
                params = merged
            elif params is _MISSING:
                params = args

    # Credentials in the url become basic authentication
    auth = None
    credentials = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*://)([^/?#@]*)@", url)
    if credentials:
        user, _, password = credentials.group(2).partition(":")
        auth = (unquote(user), unquote(password))
        url = credentials.group(1) + url[credentials.end() :]
    url = run.expand(url, call_data, "webhook url")

    post = method is not None and method.lower() == "post"
    body = None
    if params is not _MISSING:
        # params are the request body, so a webhook with params is a POST
        post = True
        body = run.expand(
            _cjson_print(params), call_data, "webhook params", escape_json=True
        )
        if form_param is not None:
            body = f"{form_param}={_url_encode(body)}"

    request_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
        if form_param is not None
        else "application/json",
        "User-Agent": "SignalWire-CallFabric/1.0",
    }
    if isinstance(headers, dict):
        # Header values are sent as written; templates in them aren't expanded
        for name, value in headers.items():
            if isinstance(value, str):
                request_headers[str(name)] = value

    run.log(f"Making {'POST' if post else 'GET'} request to: {url}")
    run.log(f"Headers: {json.dumps(request_headers, indent=2)}")
    if body is not None:
        run.log(f"Request body: {body}")

    status = 0
    text = ""
    curl_error: int | None = None
    try:
        response = _send(run, url, post, body, request_headers, auth)
        status = response.status_code
        text = response.text or ""
        run.log(f"Response status: {status}")
    except Exception as error:
        curl_error = _curl_error_code(error)
        run.log(f"Request failed: {error}")

    reply = _cjson_parse(text) if text else _MISSING
    parse_error = reply is _MISSING
    if parse_error or curl_error is not None or not 200 <= status <= 299:
        if reply is _MISSING:
            reply = {}
        if isinstance(reply, dict):
            if parse_error:
                reply["parse_error"] = True
                reply["raw_response"] = text
            if curl_error is not None:
                reply["protocol_error"] = True
                reply["http_req_result"] = curl_error
            reply["http_code"] = status
    run.log(f"Response data: {json.dumps(reply, indent=2)}")
    return reply


def _failure(reply: Any, error_keys: Any) -> str:
    """Why a webhook's reply counts as a failure, or an empty string."""
    for key in ("parse_error", "protocol_error"):
        if _has_item(reply, key):
            return f"the response has {key}"
    if error_keys is _MISSING:
        return ""
    # A listed key fails the webhook when it's present, whatever its value
    keys = error_keys if isinstance(error_keys, list) else [error_keys]
    for key in keys:
        if isinstance(key, str) and _has_item(reply, key):
            return f"the response has the error key {key!r}"
    return ""


def _run_webhooks(
    run: _Run, webhooks: Any, call_data: dict[str, Any]
) -> tuple[Any, Any]:
    """Request the first eligible webhook, as get_input_from_webhooks() does.

    Returns the reply, with an array wrapped as ``{"array": [...]}``, and the
    webhook when its reply counts as a success, or None.
    """
    reply: Any = _MISSING
    match: Any = None

    if isinstance(webhooks, list):
        for number, item in enumerate(webhooks, start=1):
            run.log(f"\n=== Webhook {number}/{len(webhooks)} ===")
            output = _object_item(item, "output")
            expressions = _object_item(item, "expressions")
            require_args = _object_item(item, "require_args")
            eligible = True
            if require_args is not _MISSING:
                # Any one of the listed arguments is enough
                eligible = _any_present(require_args, _object_item(call_data, "args"))
                if not eligible:
                    run.log("Skipped: none of its require_args are present")
            if output is _MISSING and expressions is _MISSING:
                run.log("Skipped: a webhook must have output or expressions")
                eligible = False
            if not eligible:
                continue
            reply = _request(run, item, call_data)
            if reply is _MISSING:
                run.log("Skipped: the webhook has no url")
                continue

            reason = _failure(reply, _object_item(item, "error_keys"))
            if reason:
                run.log(
                    f"Webhook {number} failed: {reason}. The platform doesn't try later "
                    "webhooks; the top-level output runs instead."
                )
            else:
                run.log(f"Webhook {number} succeeded")
                match = item
            break
    elif isinstance(webhooks, dict):
        # A single webhook object is never checked for errors
        if _has_item(webhooks, "output") or _has_item(webhooks, "expressions"):
            reply = _request(run, webhooks, call_data)
            if reply is not _MISSING:
                match = webhooks
        else:
            run.log("Skipped: a webhook must have output or expressions")

    if isinstance(reply, list):
        reply = {"array": reply}
    return reply, match


def _process_foreach(run: _Run, foreach: Any, data: dict[str, Any]) -> None:
    """Build a foreach's text into its output_key, as process_foreach() does."""
    input_key = _string_item(foreach, "input_key")
    output_key = _string_item(foreach, "output_key")
    append = _string_item(foreach, "append")
    if input_key is None or output_key is None or append is None:
        run.log("foreach needs input_key, output_key and append; skipping it")
        return
    items = _lookup(data, input_key)
    if not isinstance(items, list):
        run.log(f"foreach: {input_key} isn't an array in the response; skipping it")
        return

    count = len(items)
    limit = _object_item(foreach, "max")
    if limit is not _MISSING:
        if isinstance(limit, str):
            maximum = _atoi(limit)
        elif isinstance(limit, (int, float)):
            maximum = int(limit)
        else:
            maximum = 0
        if maximum > 0:
            count = min(count, maximum)

    parts = []
    for item in items[:count]:
        # this is the current element, and everything else stays readable
        _delete_item(data, "this")
        data["this"] = deepcopy(item)
        parts.append(run.expand(append, data, "webhook foreach"))
        _delete_item(data, "this")
    _add_item(data, output_key, "".join(parts))
    run.log(f"Foreach built {output_key} from {count} items")


def _call_data(
    datamap_config: dict[str, Any],
    args: dict[str, Any],
    call_data: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], Any]:
    """The call data templates read before a webhook responds.

    Returns the call data, the prompt variables, and the global data (or
    _MISSING). As on the platform, the prompt variables are merged into the
    root of the call data, and ``input`` is empty.
    """
    extra = deepcopy(call_data) if call_data else {}
    prompt_vars = extra.pop("prompt_vars", {})
    if not isinstance(prompt_vars, dict):
        prompt_vars = {}
    data: dict[str, Any] = {}
    function_name = datamap_config.get("function")
    if isinstance(function_name, str):
        data["function"] = function_name
    meta_data = datamap_config.get("meta_data", {})
    data["meta_data"] = deepcopy(meta_data) if isinstance(meta_data, dict) else {}
    for key, value in extra.items():
        _delete_item(data, key)
        data[key] = value
    for key, value in prompt_vars.items():
        _delete_item(data, key)
        data[key] = deepcopy(value)
    _add_item(data, "args", deepcopy(args))
    _add_item(data, "input", {})
    return data, prompt_vars, _object_item(data, "global_data")


def execute_datamap_function(
    datamap_config: dict[str, Any],
    args: dict[str, Any],
    verbose: bool = False,
    call_data: dict[str, Any] | None = None,
) -> Any:
    """
    Execute a DataMap function as SignalWire's platform does.

    See the module docstring for the order. The platform's HTTP request is
    made for real; everything else is simulated.

    Args:
        datamap_config: DataMap configuration dictionary
        args: Function arguments
        verbose: Enable verbose output
        call_data: Optional call data the platform would add, merged into the
            root of the template data, such as ``global_data``, ``call_id`` or
            ``caller_id_num``. Its ``prompt_vars``, if any, are merged into the
            root too, and are also ``${prompt_vars.x}`` in a webhook's output.

    Returns:
        The function's result, normally a dict with a ``response`` key
    """
    run = _Run(verbose)
    try:
        return _execute(run, datamap_config, args, call_data)
    finally:
        run.report_unresolved()


def _execute(
    run: _Run,
    datamap_config: dict[str, Any],
    args: dict[str, Any],
    call_data: dict[str, Any] | None,
) -> Any:
    run.log("=== DataMap Function Execution ===")
    run.log(f"Args: {json.dumps(args, indent=2)}")

    # DataMap configs have the structure: {"function": "...", "data_map": {...}}
    data_map = datamap_config.get("data_map", datamap_config)
    data, prompt_vars, global_data = _call_data(datamap_config, args, call_data)
    run.log(f"Call data: {json.dumps(data, indent=2)}")

    expressions = _object_item(data_map, "expressions")
    if expressions is not _MISSING:
        run.log("\n--- Processing Expressions ---")
        reply = _run_expressions(run, expressions, data, "top-level expressions")
        if reply is not _MISSING:
            run.log(f"Expression result: {json.dumps(reply, indent=2)}")
            return reply

    webhooks = _object_item(data_map, "webhooks")
    if webhooks is not _MISSING:
        run.log("\n--- Processing Webhooks ---")
        reply, match = _run_webhooks(run, webhooks, data)
        if match is not None:
            # The response is the root of the template data; the call data is under input
            rdata: dict[str, Any] = reply if isinstance(reply, dict) else {}
            _add_item(rdata, "prompt_vars", deepcopy(prompt_vars))
            if global_data is not _MISSING:
                _add_item(rdata, "global_data", deepcopy(global_data))
            _add_item(rdata, "input", deepcopy(data))

            foreach = _object_item(match, "foreach")
            if foreach is not _MISSING:
                run.log("\n--- Processing Webhook Foreach ---")
                _process_foreach(run, foreach, rdata)

            response: Any = _MISSING
            processed = False
            webhook_expressions = _object_item(match, "expressions")
            if webhook_expressions is not _MISSING:
                run.log("\n--- Processing Webhook Expressions ---")
                result = _run_expressions(
                    run, webhook_expressions, rdata, "webhook expressions"
                )
                if result is not _MISSING:
                    # The platform expands a matched result a second time
                    response = run.expand_json(result, rdata, "webhook expressions")
                    processed = True
                else:
                    run.log("No webhook expression matched")

            output = _object_item(match, "output")
            if response is _MISSING and output is not _MISSING:
                run.log("\n--- Processing Webhook Output ---")
                response = run.expand_json(output, rdata, "webhook output")
                processed = True

            if processed:
                return _finish(run, response)

    output = _object_item(data_map, "output")
    if output is not _MISSING:
        run.log("\n--- Using the Top-Level Output ---")
        _add_item(data, "prompt_vars", deepcopy(prompt_vars))
        return _finish(run, run.expand_json(output, data, "top-level output"))

    run.log("\nNothing produced an output; the platform returns its generic error")
    return {"response": PLATFORM_ERROR_RESPONSE}


def _finish(run: _Run, response: Any) -> Any:
    if response is _MISSING:
        run.log("The expanded output isn't valid JSON")
        return {
            "error": "The expanded output isn't valid JSON, so the platform gets no result "
            "from this function. A template that inserts an object or array into a "
            "string causes this."
        }
    run.log(f"Result: {json.dumps(response, indent=2)}")
    return response
