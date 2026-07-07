"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

HTTP client infrastructure and base resource classes for the REST client.
"""

from importlib.metadata import PackageNotFoundError, version
from typing import Any, Generic, TypeVar, cast

import requests
from signalwire.core.logging_config import get_logger

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
    """Raised when the SignalWire REST API returns a non-2xx response."""

    def __init__(
        self, status_code: int, body: Any, url: str, method: str = "GET"
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.url = url
        self.method = method
        message = f"{method} {url} returned {status_code}: {body}"
        super().__init__(message)


class HttpClient:
    """Thin wrapper around requests.Session with Basic Auth and JSON handling."""

    def __init__(self, project: str, token: str, host: str) -> None:
        self._base_url = f"https://{host}"
        self._session = requests.Session()
        self._session.auth = (project, token)
        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": _user_agent(),
            }
        )
        logger.debug("HttpClient initialized", host=host, project=project[:8] + "...")

    def _request(
        self,
        method: str,
        path: str,
        body: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = self._base_url + path
        logger.debug("REST request", method=method, path=path)
        resp = self._session.request(method, url, json=body, params=params)
        if not resp.ok:
            try:
                err_body: Any = resp.json()
            except Exception:
                err_body = resp.text
            raise SignalWireRestError(resp.status_code, err_body, path, method)
        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(
        self, path: str, body: Any = None, params: dict[str, Any] | None = None
    ) -> Any:
        return self._request("POST", path, body=body, params=params)

    def put(self, path: str, body: Any = None) -> Any:
        return self._request("PUT", path, body=body)

    def patch(self, path: str, body: Any = None) -> Any:
        return self._request("PATCH", path, body=body)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)


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

    def list(self, **params: Any) -> TList:
        return cast(TList, self._http.get(self._base_path, params=params or None))

    def get(self, resource_id: str) -> TItem:
        return cast(TItem, self._http.get(self._path(resource_id)))


class CrudResource(ReadResource[TList, TItem], Generic[TList, TItem, TCreate, TUpdate]):
    """Standard CRUD resource with list/create/get/update/delete.

    Extends ``ReadResource`` (list + get) with create/update/delete. Generic over
    the spec-generated response/request types so each concrete resource publishes
    its real per-operation shapes (the signature oracle resolves the subclass's
    binding). At runtime every method still returns the raw server JSON dict — the
    type params are static only.
    """

    _update_method = "PATCH"

    def create(self, **kwargs: Any) -> TItem:
        # Honest fallback: the body accepts arbitrary wire fields and at runtime
        # is a plain dict. Concrete resources override this with a generated
        # CLOSED typed signature (explicit spec fields + an ``extras`` door); the
        # class-level ``CrudResource[...]`` binding is what publishes the real
        # TCreate shape to the signature oracle, NOT this base method body. (A
        # bare ``**kwargs: TCreate`` here is wrong — it would type each kwarg
        # VALUE as a whole TCreate — and is what the generated overrides replace.)
        return cast(TItem, self._http.post(self._base_path, body=kwargs))

    def update(self, resource_id: str, /, **kwargs: Any) -> TItem:
        # resource_id is positional-only so a subclass may rename it without an LSP
        # override conflict. Same contract as ``create``: honest ``**kwargs: Any``
        # fallback; the concrete generated override carries the closed typed shape, the
        # binding carries TUpdate for the oracle.
        method = getattr(self._http, self._update_method.lower())
        return cast(TItem, method(self._path(resource_id), body=kwargs))

    def delete(self, resource_id: str) -> TItem:
        return cast(TItem, self._http.delete(self._path(resource_id)))


class CrudWithAddresses(CrudResource[TList, TItem, TCreate, TUpdate]):
    """CRUD resource that also supports listing addresses."""

    def list_addresses(self, resource_id: str, **params: Any) -> Any:
        return self._http.get(
            self._path(resource_id, "addresses"), params=params or None
        )


class FabricResource(CrudWithAddresses[TList, TItem, TCreate, TUpdate]):
    """Standard fabric resource with CRUD + addresses.

    Intermediate generic base — concrete leaf resources bind the four type
    parameters. Mirrors the TS port's ``FabricResource<TList, TItem, TCreate,
    TUpdate>``. Lives here (not in the fabric namespace) so the generated
    ``fabric_resources_generated`` subclasses can inherit it without a cycle.
    """

    pass


class FabricResourcePUT(CrudWithAddresses[TList, TItem, TCreate, TUpdate]):
    """Fabric resource that uses PUT for updates.

    Intermediate generic base (see :class:`FabricResource`).
    """

    _update_method = "PUT"
