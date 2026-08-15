"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

HTTP client infrastructure and base resource classes for the REST client.
"""

import os
import time
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Generic, TypeVar, cast

import requests
from signalwire.core.logging_config import get_logger
from signalwire.rest._pagination import PaginatedIterator
from signalwire.rest._request_options import (
    RequestOptions,
    resolve,
    status_is_retryable,
)

logger = get_logger("rest_client")


def _user_agent() -> str:
    """Build the REST client User-Agent from the installed package version.

    The version segment is derived at runtime from ``signalwire-sdk`` (the dist
    name in ``pyproject.toml``) so it can never drift from a hardcoded literal
    (SDK_BUG_LEDGER P1: the old ``signalwire-agents-python-rest/1.0`` was both the
    wrong product token and a stale ``/1.0`` while the package was at 3.x). The
    product token stays stable at ``signalwire-python``.
    """
    try:
        pkg_version = version("signalwire-sdk")
    except PackageNotFoundError:  # pragma: no cover - only when running uninstalled
        pkg_version = "unknown"
    return f"signalwire-python/{pkg_version}"


def _is_loopback_host(host: str) -> bool:
    """True if ``host`` (bare host or host:port) is a local loopback address — a
    local mock/dev server that speaks plain HTTP. Used to pick http:// vs https://
    so a shipped example runs verbatim against the local mock. A real SignalWire
    space (``<name>.signalwire.com``) is never loopback, so production is unaffected."""
    hostname = host.rsplit(":", 1)[0] if ":" in host else host
    return hostname in ("127.0.0.1", "localhost", "::1", "[::1]")


# CRUD response/request type parameters. Each concrete resource binds these to its
# spec-generated TypedDicts (e.g. CrudResource[ListRoomsResponse, RoomResponse,
# CreateRoomRequest, UpdateRoomRequest]); the signature oracle resolves the
# binding so every resource publishes its real per-operation shapes. Mirrors the
# TS port's CrudResource<TList, TItem, TCreate, TUpdate>.
TList = TypeVar("TList")
TItem = TypeVar("TItem")
TCreate = TypeVar("TCreate")
TUpdate = TypeVar("TUpdate")


class SignalWireRestError(Exception):
    """Raised when the SignalWire REST API returns a non-2xx response.

    ``status_code`` is the HTTP status; for a TRANSPORT failure (the request never
    reached a response — connection refused, DNS failure, connection reset) it is
    ``None`` and the raised type is :class:`SignalWireRestTransportError`. Callers
    catch this one family for every REST failure, HTTP or transport.

    §6.6 error-observability: ``headers`` is the response header map (or ``None`` for a
    transport error that produced no response) and ``request_id`` is the platform request
    id pulled from those headers — client-side observability with NO wire-contract change,
    so a caller can log/correlate a failure against SignalWire's own request id.
    """

    def __init__(
        self,
        status_code: int | None,
        body: Any,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.url = url
        self.method = method
        self.headers: dict[str, str] | None = headers
        self.request_id: str | None = _extract_request_id(headers)
        if status_code is None:
            message = f"{method} {url} failed to reach the server: {body}"
        else:
            message = f"{method} {url} returned {status_code}: {body}"
        if self.request_id:
            message += f" (request-id: {self.request_id})"
        super().__init__(message)


# Header names SignalWire (and common proxies) use for the platform request id, in
# preference order. Matched case-insensitively.
_REQUEST_ID_HEADERS = (
    "x-request-id",
    "x-signalwire-request-id",
    "request-id",
    "x-amzn-requestid",
)


def _extract_request_id(headers: dict[str, str] | None) -> str | None:
    if not headers:
        return None
    lowered = {k.lower(): v for k, v in headers.items()}
    for name in _REQUEST_ID_HEADERS:
        if name in lowered:
            return lowered[name]
    return None


class SignalWireRestTransportError(SignalWireRestError):
    """Raised when a REST request never reached a response — a transport-level
    failure (connection refused, DNS failure, connection reset, TLS error).

    A member of the :class:`SignalWireRestError` family (``status_code`` is ``None``,
    ``body`` is the underlying transport error message) so a caller catching
    ``SignalWireRestError`` handles both HTTP-error and transport-error responses with
    one ``except``, instead of the bare ``requests.ConnectionError`` leaking through.
    ``headers``/``request_id`` are ``None`` (no response was produced).
    """

    def __init__(self, body: Any, url: str, method: str = "GET") -> None:
        super().__init__(None, body, url, method, headers=None)


class HttpClient:
    """Thin wrapper around requests.Session with Basic Auth and JSON handling."""

    def __init__(
        self,
        project: str,
        token: str,
        host: str,
        request_options: RequestOptions | None = None,
    ) -> None:
        # A loopback host (127.0.0.1[:port] / localhost[:port]) is a local mock/dev
        # server that speaks plain HTTP — use http:// for it. Every other host is the
        # real platform over https://. This lets a shipped example run verbatim against
        # the local mock (SIGNALWIRE_SPACE=127.0.0.1:<port>) without a code change or a
        # separate URL knob; production is unaffected (a real space is never loopback).
        scheme = "http" if _is_loopback_host(host) else "https"
        self._base_url = f"{scheme}://{host}"
        self._request_options = request_options
        self._session = requests.Session()
        self._session.auth = (project, token)
        # A5 (fleet CA-var contract, hard-cut no aliases): a custom CA bundle for
        # the REST transport is supplied via SIGNALWIRE_REST_CA_FILE. When set, it
        # becomes the session's verify bundle (requests uses it for TLS
        # verification of the platform cert). Unset → requests' default trust
        # store. This is the REST half of the fleet-standard pair
        # (SIGNALWIRE_RELAY_CA_FILE is the RELAY half).
        _rest_ca_file = os.environ.get("SIGNALWIRE_REST_CA_FILE")
        if _rest_ca_file:
            self._session.verify = _rest_ca_file
        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": _user_agent(),
            }
        )
        logger.debug("HttpClient initialized", host=host, project=project[:8] + "...")

    def _sleep(self, seconds: float) -> None:
        """Backoff sleep between retries. A seam so tests can drive the retry
        loop without wall-clock delay (the mock proves attempt ORDERING, not
        real time)."""
        if seconds > 0:
            time.sleep(seconds)

    def _retry_after_seconds(self, resp: requests.Response) -> float | None:
        """Parse a ``Retry-After`` header (delta-seconds form) if present."""
        value = resp.headers.get("Retry-After")
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None  # HTTP-date form: fall back to computed backoff

    def _request(
        self,
        method: str,
        path: str,
        body: Any = None,
        params: dict[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> Any:
        url = self._base_url + path
        # D1 (owner-approved 2026-07-18): error.url is the FULL URL WITH the query
        # string preserved — the reference decision the fleet never actually took (the
        # ports stored the bare path behind a `url`-named field). Build the full URL
        # including the query so an error message / .url attribute is copy-pasteable and
        # carries the query context. (urlencode with doseq=True mirrors requests' own
        # list-param expansion.)
        full_url = url
        if params:
            from urllib.parse import urlencode

            qs = urlencode(
                {k: v for k, v in params.items() if v is not None}, doseq=True
            )
            if qs:
                full_url = f"{url}?{qs}"
        opts = resolve(self._request_options, request_options)
        logger.debug("REST request", method=method, path=path)

        # total attempts = retries + 1; retry on a retryable status (idempotency-
        # aware) or a transport error, honoring Retry-After then exponential
        # backoff. abort_signal is checked cooperatively before every attempt.
        attempt = 0
        while True:
            attempt += 1
            if opts.abort_signal is not None and opts.abort_signal.is_set():
                # Cancelled before this attempt — surface as the transport-error
                # family (no response was produced), not a bare exception.
                raise SignalWireRestTransportError(
                    "request cancelled by abort_signal", full_url, method
                )

            try:
                resp = self._session.request(
                    method, url, json=body, params=params, timeout=opts.timeout
                )
            except requests.RequestException as exc:
                # Transport failure (connection refused / DNS / reset / TLS /
                # timeout): the request never produced a response. Retry if
                # attempts remain, else wrap in the typed error family so a caller
                # catching SignalWireRestError handles it too.
                if attempt <= opts.retries:
                    self._sleep(opts.retry_backoff * 2 ** (attempt - 1))
                    continue
                raise SignalWireRestTransportError(str(exc), full_url, method) from exc

            if not resp.ok:
                if attempt <= opts.retries and status_is_retryable(
                    method, resp.status_code, opts
                ):
                    delay = self._retry_after_seconds(resp)
                    if delay is None:
                        delay = opts.retry_backoff * 2 ** (attempt - 1)
                    self._sleep(delay)
                    continue
                try:
                    err_body: Any = resp.json()
                except Exception:
                    err_body = resp.text
                raise SignalWireRestError(
                    resp.status_code,
                    err_body,
                    full_url,
                    method,
                    headers=dict(resp.headers),
                )

            if resp.status_code == 204 or not resp.content:
                return {}
            try:
                return resp.json()
            except ValueError as exc:
                # A 2xx with an undecodable body (truncated / HTML error page / non-JSON)
                # must surface as the typed error family, NOT a bare
                # requests.JSONDecodeError leaking to the caller (who catches
                # SignalWireRestError for every REST failure). status_code is the real
                # 2xx; body is the raw text so the caller can see what arrived.
                raise SignalWireRestError(
                    resp.status_code,
                    resp.text,
                    full_url,
                    method,
                    headers=dict(resp.headers),
                ) from exc

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> Any:
        """Issue a ``GET`` to ``path`` and return the decoded JSON body.

        Args:
            path: Absolute API path (e.g. ``/api/fabric/resources``), appended to
                the client's ``scheme://host`` base URL.
            params: Query-string parameters. ``None`` values are dropped from the
                URL recorded on an error; list values expand repeated-key style.
            request_options: Per-call transport overrides (timeout / retries /
                backoff / abort signal) shallow-merged over the client default.

        Returns:
            The parsed JSON body, or ``{}`` for a ``204`` or an empty body.

        Raises:
            SignalWireRestError: On a non-2xx response, or on a 2xx whose body is
                not decodable JSON.
            SignalWireRestTransportError: If no response was ever received
                (connection refused, DNS failure, TLS error, timeout) or the
                ``abort_signal`` was set before an attempt.
        """
        return self._request(
            "GET", path, params=params, request_options=request_options
        )

    def post(
        self,
        path: str,
        body: Any = None,
        params: dict[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> Any:
        """Issue a ``POST`` to ``path`` with ``body`` JSON-encoded, returning the
        decoded JSON response.

        Unlike :meth:`get`, this is a non-idempotent method: on a retryable
        failure it retries only for a transport error or a ``429``/``503``
        throttle, never blindly on ``500``/``502``/``504``.

        Args:
            path: Absolute API path.
            body: Value serialised as the JSON request body. ``None`` sends no body.
            params: Query-string parameters (some create endpoints take both).
            request_options: Per-call transport overrides.

        Returns:
            The parsed JSON body, or ``{}`` for a ``204`` or an empty body.

        Raises:
            SignalWireRestError: On a non-2xx response, or an undecodable 2xx body.
            SignalWireRestTransportError: If no response was received or the request
                was cancelled via ``abort_signal``.
        """
        return self._request(
            "POST", path, body=body, params=params, request_options=request_options
        )

    def put(
        self,
        path: str,
        body: Any = None,
        request_options: RequestOptions | None = None,
    ) -> Any:
        """Issue a ``PUT`` to ``path`` with ``body`` JSON-encoded (full replace).

        Takes no query parameters, unlike :meth:`get`/:meth:`post`. ``PUT`` is
        treated as idempotent, so it retries on the full ``retry_on_status`` set.

        Args:
            path: Absolute API path, usually a specific item (``<collection>/<id>``).
            body: Value serialised as the JSON request body.
            request_options: Per-call transport overrides.

        Returns:
            The parsed JSON body, or ``{}`` for a ``204`` or an empty body.

        Raises:
            SignalWireRestError: On a non-2xx response, or an undecodable 2xx body.
            SignalWireRestTransportError: If no response was received or the request
                was cancelled via ``abort_signal``.
        """
        return self._request("PUT", path, body=body, request_options=request_options)

    def patch(
        self,
        path: str,
        body: Any = None,
        request_options: RequestOptions | None = None,
    ) -> Any:
        """Issue a ``PATCH`` to ``path`` with ``body`` JSON-encoded (partial update).

        Takes no query parameters. Like :meth:`post`, ``PATCH`` is non-idempotent,
        so it retries only on a transport error or a ``429``/``503`` throttle.

        Args:
            path: Absolute API path, usually a specific item (``<collection>/<id>``).
            body: Value serialised as the JSON request body — only the fields to change.
            request_options: Per-call transport overrides.

        Returns:
            The parsed JSON body, or ``{}`` for a ``204`` or an empty body.

        Raises:
            SignalWireRestError: On a non-2xx response, or an undecodable 2xx body.
            SignalWireRestTransportError: If no response was received or the request
                was cancelled via ``abort_signal``.
        """
        return self._request("PATCH", path, body=body, request_options=request_options)

    def delete(self, path: str, request_options: RequestOptions | None = None) -> Any:
        """Issue a ``DELETE`` to ``path``, returning the decoded JSON response.

        Sends neither a body nor query parameters. ``DELETE`` is treated as
        idempotent, so it retries on the full ``retry_on_status`` set. SignalWire
        delete endpoints typically answer ``204``, which surfaces here as ``{}``.

        Args:
            path: Absolute API path of the item to delete.
            request_options: Per-call transport overrides.

        Returns:
            The parsed JSON body, or ``{}`` for a ``204`` or an empty body.

        Raises:
            SignalWireRestError: On a non-2xx response, or an undecodable 2xx body.
            SignalWireRestTransportError: If no response was received or the request
                was cancelled via ``abort_signal``.
        """
        return self._request("DELETE", path, request_options=request_options)


class BaseResource:
    """Base for all namespace/resource classes."""

    def __init__(self, http: HttpClient, base_path: str) -> None:
        self._http = http
        self._base_path = base_path

    def _path(self, *parts: Any) -> str:
        return "/".join([self._base_path] + [str(p) for p in parts])


class ReadResource(BaseResource, Generic[TList, TItem]):
    """Read-only resource with list + get (no create/update/delete).

    The shared base for read-only surfaces (e.g. the per-product log resources).
    ``CrudResource`` extends this with the write operations, so list/get are
    defined once here.
    """

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> TList:
        """Fetch ONE raw page from this resource's collection endpoint.

        ``GET``s the resource's ``base_path`` verbatim (no id segment appended)
        and returns the server's response as-is — the envelope, not the items.
        This does NOT follow pagination links: use :meth:`paginate` to iterate
        every item across all pages.

        Args:
            request_options: Per-call transport overrides (timeout / retries /
                backoff / abort signal).
            **params: Arbitrary filter/paging query parameters, sent as the query
                string. Passing none sends no query string at all.

        Returns:
            The decoded list envelope, statically typed as this resource's
            ``TList`` binding. At runtime it is the raw JSON dict from the server;
            the type parameter is static only.

        Raises:
            SignalWireRestError: On a non-2xx response, or an undecodable 2xx body.
            SignalWireRestTransportError: If no response was received.
        """
        return cast(
            TList,
            self._http.get(
                self._base_path,
                params=params or None,
                request_options=request_options,
            ),
        )

    def paginate(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> PaginatedIterator:
        """Iterate every item across all pages of this resource's list endpoint.

        ``list()`` returns a single raw page (the server's first response). For
        endpoints that paginate on the wire (a ``links.next`` / ``page_token`` in
        the response), ``paginate()`` follows those links and yields each item:

            for address in client.fabric.addresses.paginate():
                ...

        Wires the resource layer to the tested ``PaginatedIterator`` (which walks
        ``resp["data"]`` and follows ``resp["links"]["next"]``), so callers no
        longer hand-construct the path + token loop. ``request_options`` (a per-call
        timeout / retry / header override) is applied to EVERY page fetch.
        """
        return PaginatedIterator(
            self._http,
            self._base_path,
            params=params or None,
            data_key="data",
            request_options=request_options,
        )

    def get(
        self, resource_id: str, *, request_options: RequestOptions | None = None
    ) -> TItem:
        """Fetch a single item of this resource by id.

        ``GET``s ``<base_path>/<resource_id>``. Distinct from
        :meth:`HttpClient.get`, which takes a caller-built absolute path and no id:
        here the path is composed from the resource's own ``base_path``, and no
        query parameters are sent.

        Args:
            resource_id: Identifier appended as the final path segment. Stringified
                as-is, so it must already be URL-safe.
            request_options: Per-call transport overrides.

        Returns:
            The decoded item, statically typed as this resource's ``TItem``
            binding; a raw JSON dict at runtime.

        Raises:
            SignalWireRestError: On a non-2xx response — notably ``404`` for an
                unknown id — or an undecodable 2xx body.
            SignalWireRestTransportError: If no response was received.
        """
        return cast(
            TItem,
            self._http.get(self._path(resource_id), request_options=request_options),
        )


class CrudResource(ReadResource[TList, TItem], Generic[TList, TItem, TCreate, TUpdate]):
    """Standard CRUD resource with list/create/get/update/delete.

    Extends ``ReadResource`` (list + get) with create/update/delete. Generic over
    the spec-generated response/request types so each concrete resource publishes
    its real per-operation shapes (the type checker resolves each subclass's
    binding). At runtime every method still returns the raw server JSON dict — the
    type params are static only.
    """

    _update_method = "PATCH"

    def create(
        self, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> TItem:
        """Create a new item in this collection.

        ``POST``s ``base_path`` with the keyword arguments serialised **as the JSON
        request body** — not as a query string, which is how they differ from
        :meth:`list`'s ``**params``.

        Concrete generated resources override this with a closed, spec-typed
        signature; this base accepts arbitrary wire fields.

        Args:
            request_options: Per-call transport overrides.
            **kwargs: Fields of the create request, sent verbatim as the JSON body.

        Returns:
            The created item as returned by the server, statically typed as
            ``TItem``; a raw JSON dict at runtime.

        Raises:
            SignalWireRestError: On a non-2xx response — notably ``422`` for an
                invalid body — or an undecodable 2xx body.
            SignalWireRestTransportError: If no response was received.
        """
        # Honest fallback: the body accepts arbitrary wire fields and at runtime
        # is a plain dict. Concrete resources override this with a generated
        # CLOSED typed signature (explicit spec fields + an ``extras`` door); the
        # class-level ``CrudResource[...]`` binding is what publishes the real
        # TCreate shape to the signature oracle, NOT this base method body. (A
        # bare ``**kwargs: TCreate`` here is wrong — it would type each kwarg
        # VALUE as a whole TCreate — and is what the generated overrides replace.)
        return cast(
            TItem,
            self._http.post(
                self._base_path, body=kwargs, request_options=request_options
            ),
        )

    def update(
        self,
        resource_id: str,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> TItem:
        """Update an existing item by id, sending only the given fields.

        Dispatches on the class attribute ``_update_method``: ``PATCH`` by default
        (partial update), or ``PUT`` for resources that bind
        :class:`FabricResourcePUT`. The keyword arguments become the JSON request
        body, sent to ``<base_path>/<resource_id>``.

        Concrete generated resources override this with a closed, spec-typed
        signature; this base accepts arbitrary wire fields.

        Args:
            resource_id: Identifier of the item to update, appended as the final
                path segment. Positional-only, so a subclass may rename it.
            request_options: Per-call transport overrides.
            **kwargs: Fields to change, sent verbatim as the JSON body.

        Returns:
            The updated item as returned by the server, statically typed as
            ``TItem``; a raw JSON dict at runtime.

        Raises:
            SignalWireRestError: On a non-2xx response — notably ``404`` for an
                unknown id or ``422`` for an invalid body — or an undecodable 2xx body.
            SignalWireRestTransportError: If no response was received.
        """
        # resource_id is positional-only so a subclass may rename it without an LSP
        # override conflict. Same contract as ``create``: honest ``**kwargs: Any``
        # fallback; the concrete generated override carries the closed typed shape, the
        # binding carries TUpdate for the oracle.
        method = getattr(self._http, self._update_method.lower())
        return cast(
            TItem,
            method(
                self._path(resource_id),
                body=kwargs,
                request_options=request_options,
            ),
        )

    def delete(
        self, resource_id: str, *, request_options: RequestOptions | None = None
    ) -> TItem:
        """Delete a single item of this resource by id.

        ``DELETE``s ``<base_path>/<resource_id>``. Distinct from
        :meth:`HttpClient.delete`, which takes a caller-built absolute path: here
        the path is composed from the resource's own ``base_path``.

        Args:
            resource_id: Identifier of the item to delete, appended as the final
                path segment.
            request_options: Per-call transport overrides.

        Returns:
            Statically typed as ``TItem``, but SignalWire delete endpoints
            typically answer ``204`` with no body, which arrives here as ``{}``.
            Do not rely on the deleted item being echoed back.

        Raises:
            SignalWireRestError: On a non-2xx response — notably ``404`` for an
                unknown id.
            SignalWireRestTransportError: If no response was received.
        """
        return cast(
            TItem,
            self._http.delete(self._path(resource_id), request_options=request_options),
        )


class CrudWithAddresses(CrudResource[TList, TItem, TCreate, TUpdate]):
    """CRUD resource that also supports listing addresses."""

    def list_addresses(
        self,
        resource_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> Any:
        """List the addresses belonging to one item of this resource.

        ``GET``s the sibling sub-collection ``<base_path>/<resource_id>/addresses``.
        Unlike :meth:`list`, which pages the resource's OWN collection, this lists a
        different collection nested under a single item, so it requires an id.

        Args:
            resource_id: Identifier of the owning item.
            request_options: Per-call transport overrides.
            **params: Filter/paging query parameters for the addresses collection.
                Passing none sends no query string.

        Returns:
            The decoded addresses list envelope. Untyped (``Any``) — this method
            carries no ``TList``-style type parameter, so it is the raw server JSON
            both statically and at runtime.

        Raises:
            SignalWireRestError: On a non-2xx response — notably ``404`` for an
                unknown ``resource_id``.
            SignalWireRestTransportError: If no response was received.
        """
        return self._http.get(
            self._path(resource_id, "addresses"),
            params=params or None,
            request_options=request_options,
        )


class FabricResource(CrudWithAddresses[TList, TItem, TCreate, TUpdate]):
    """Standard fabric resource with CRUD + addresses.

    Intermediate generic base — concrete leaf resources bind the four type
    parameters. Lives here (not in the fabric namespace) so the generated
    ``fabric_resources_generated`` subclasses can inherit it without a cycle.
    """

    pass


class FabricResourcePUT(CrudWithAddresses[TList, TItem, TCreate, TUpdate]):
    """Fabric resource that uses PUT for updates.

    Intermediate generic base (see :class:`FabricResource`).
    """

    _update_method = "PUT"
