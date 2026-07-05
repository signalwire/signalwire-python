"""Cross-port host-app router type.

``HostAppRouter`` is the named return type of ``as_router()`` — the "embed this
agent/service's routes into your own host web app" capability (used as
``app.include_router(agent.as_router())``).

It is a thin subclass of FastAPI's ``APIRouter`` — so at runtime it IS an
``APIRouter`` and every existing consumer (``app.include_router(...)``,
``isinstance(x, APIRouter)``, route introspection) works unchanged; the subclass
adds no behavior. Its purpose is to give the capability a **stable, named
cross-port type** in the signature oracle: every port implements ``as_router()``
returning its own framework's mount handle (Go ``http.Handler``, .NET
``IEndpointRouteBuilder``/``RequestDelegate``, Ruby a Rack app, Perl a PSGI
coderef, Java an ``HttpHandler``/Spring ``RouterFunction``, Rust an
``axum::Router``, TS a Hono sub-app, C++ an httplib handler), and each port maps
that native type to this canonical ``HostAppRouter`` in its type-alias table. The
capability is thereby enforced cross-port; the framework-specific realization is
idiom.
"""

from __future__ import annotations

try:
    from fastapi import APIRouter
except ImportError:  # pragma: no cover - fastapi is a hard dependency of the web layer
    raise ImportError(
        "fastapi is required for the web/host-app layer. Install it with: pip install fastapi"
    ) from None


class HostAppRouter(APIRouter):
    """A FastAPI ``APIRouter`` returned by ``as_router()``.

    Behaviourally identical to ``APIRouter`` (no added state or methods) — it
    exists to name the "embed my routes in a host app" return type as a stable
    cross-port symbol. See the module docstring.
    """
