"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Run synchronous user code off the event loop.

The web server's endpoints are async and share one event loop. Synchronous
user code called directly on that loop, such as a tool handler that makes an
HTTP request, blocks every other request, on every call, until it returns.
The endpoints call that code through ``run_sync_handler``, which runs it in a
worker thread from AnyIO's thread pool, the pool FastAPI uses for ``def``
routes. That pool runs 40 threads at a time by default.

The code runs in the worker's copy of the request's context, as for a
``def`` route, and the context variables it sets are applied to the request's
context when it returns. So a variable one step sets reaches the request's
later steps, such as the per-request configuration callback's to the tool
handler, as it did when every step ran inline.

An ``async def`` handler runs on the event loop, awaited directly, and needs
no worker thread. When an endpoint can't tell a handler is async, calling it
in the thread only creates its coroutine, which the endpoint then awaits.

Setting ``SWML_SYNC_HANDLERS_INLINE`` to ``1``, ``true`` or ``yes`` calls the
code on the event loop instead, as earlier releases did.
"""

import contextvars
import functools
import inspect
import os
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from starlette.concurrency import run_in_threadpool

_P = ParamSpec("_P")
_T = TypeVar("_T")
_UNSET = object()


def sync_handlers_inline() -> bool:
    """True when ``SWML_SYNC_HANDLERS_INLINE`` asks for the event loop."""
    return os.getenv("SWML_SYNC_HANDLERS_INLINE", "").lower() in ("1", "true", "yes")


def is_async_callable(obj: object) -> bool:
    """True for an ``async def`` function or method, a partial of one, or an
    object whose ``__call__`` is ``async def``: calling it only creates a
    coroutine."""
    while isinstance(obj, functools.partial):
        obj = obj.func
    if inspect.iscoroutinefunction(obj):
        return True
    # An instance of a class whose __call__ is async def
    return callable(obj) and inspect.iscoroutinefunction(type(obj).__call__)


async def run_sync_handler(
    func: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs
) -> _T:
    """Call ``func`` in a worker thread, or inline when so configured.

    ``func`` sees the caller's context variables, such as the per-request
    proxy URL and structlog's bound context. The ones it sets, even if it
    then raises, are set in the caller's context once it finishes, as they
    would have been had it run inline. If the caller is cancelled first, they
    aren't.
    """
    if sync_handlers_inline():
        return func(*args, **kwargs)
    changes = _Changes()
    try:
        return await run_in_threadpool(
            functools.partial(_recording_changes, changes, func, *args, **kwargs)
        )
    finally:
        if changes.complete:
            for var, value in changes.values:
                var.set(value)


class _Changes:
    """The context variables a function set in its worker thread."""

    def __init__(self) -> None:
        """Start with no recorded changes, not yet complete."""
        self.values: list[tuple[contextvars.ContextVar[Any], Any]] = []
        # Set last, once values is final
        self.complete = False


def _recording_changes(
    changes: _Changes, func: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs
) -> _T:
    """Call ``func``, and record in ``changes`` the context variables it sets.

    It runs in the worker's context, where the thread pool has already made
    its own settings, so only what ``func`` itself changes is recorded.
    """
    before = contextvars.copy_context()
    try:
        return func(*args, **kwargs)
    finally:
        changes.values = [
            (var, value)
            for var, value in contextvars.copy_context().items()
            if before.get(var, _UNSET) is not value
        ]
        changes.complete = True
