"""Host-app router type.

``HostAppRouter`` is the named return type of ``as_router()`` — the "embed this
agent/service's routes into your own host web app" capability (used as
``app.include_router(agent.as_router())``).

It is a thin subclass of FastAPI's ``APIRouter`` — so at runtime it IS an
``APIRouter`` and every existing consumer (``app.include_router(...)``,
``isinstance(x, APIRouter)``, route introspection) works unchanged; the subclass
adds no behavior. It exists to give the capability a stable, named type you can
reference when mounting an agent's routes into an existing FastAPI application.
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
