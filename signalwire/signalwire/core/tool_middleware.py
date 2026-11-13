"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Tool middleware: code that runs around every tool call.

A middleware is ``fn(name, args, raw_data, call_next)``. It runs before the
handler, and calls ``call_next(args, raw_data)`` to run the rest of the chain
and the handler, possibly with changed arguments. What it returns is the
call's result, so it can return the handler's, change it, or answer without
calling ``call_next`` at all. ``call_next`` returns the handler's result, or
an awaitable of it for an ``async def`` handler; an ``async def`` middleware
can await either with ``await resolve(call_next(args, raw_data))``.

The SDK puts one middleware first in every chain, unless it's turned off
(``set_tool_resend_dedupe(False)``): ``ResendDedupe``, which keeps a transport
retry from running a tool twice. SignalWire sends a tool request again, with
the same body, after a timeout, a failed connection or a 5xx, so a slow tool
can run twice. The retry carries the same ``tool_call_id``; a call the model
makes again gets a new one.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import threading
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from typing import Any

#: The rest of the chain, as a middleware calls it
CallNext = Callable[[dict[str, Any], dict[str, Any]], Any]
#: A tool middleware
ToolMiddleware = Callable[[str, dict[str, Any], dict[str, Any], CallNext], Any]


async def resolve(value: Any) -> Any:
    """``value``, awaited when it's awaitable: for an ``async def``
    middleware, which can get either from ``call_next``."""
    if inspect.isawaitable(value):
        return await value
    return value


def run_chain(
    middleware: list[ToolMiddleware],
    name: str,
    args: dict[str, Any],
    raw_data: dict[str, Any],
    dispatch: CallNext,
) -> Any:
    """Run ``middleware`` in order around ``dispatch``."""
    call: CallNext = dispatch
    for layer in reversed(middleware):
        call = _layer(layer, name, call)
    return call(args, raw_data)


def _layer(layer: ToolMiddleware, name: str, call_next: CallNext) -> CallNext:
    def call(args: dict[str, Any], raw_data: dict[str, Any]) -> Any:
        return layer(name, args, raw_data, call_next)

    return call


class ResendDedupe:
    """
    The middleware that answers a transport retry of a tool call with the
    first attempt's result, instead of running the tool again.

    A call is the same when its ``call_id``, ``tool_call_id`` and function
    name are. A retry that arrives while the first attempt is still running,
    as after a timeout, waits for it; one that arrives after it finished
    gets its result. A call without a ``tool_call_id`` always runs. Results
    are kept for ``ttl`` seconds, at most ``max_entries`` of them.
    """

    def __init__(self, ttl: float = 600.0, max_entries: int = 1024) -> None:
        self.ttl = ttl
        self.max_entries = max_entries
        self._lock = threading.Lock()
        # key -> (when it started, the future of its result)
        self._calls: OrderedDict[
            tuple[str, str, str], tuple[float, concurrent.futures.Future[Any]]
        ] = OrderedDict()

    def __call__(
        self,
        name: str,
        args: dict[str, Any],
        raw_data: dict[str, Any],
        call_next: CallNext,
    ) -> Any:
        key = _key(name, raw_data)
        if key is None:
            return call_next(args, raw_data)
        with self._lock:
            self._expire()
            known = self._calls.get(key)
            if known is None:
                future: concurrent.futures.Future[Any] = concurrent.futures.Future()
                self._calls[key] = (time.monotonic(), future)
        if known is not None:
            return _await_first(known[1])
        try:
            result = call_next(args, raw_data)
        except BaseException as e:
            self._forget(key, future, e)
            raise
        if inspect.isawaitable(result):
            return self._settle_async(key, future, result)
        future.set_result(result)
        return result

    async def _settle_async(
        self,
        key: tuple[str, str, str],
        future: concurrent.futures.Future[Any],
        pending: Awaitable[Any],
    ) -> Any:
        try:
            result = await pending
        except BaseException as e:
            self._forget(key, future, e)
            raise
        future.set_result(result)
        return result

    def _forget(
        self,
        key: tuple[str, str, str],
        future: concurrent.futures.Future[Any],
        error: BaseException,
    ) -> None:
        """A first attempt that raised isn't kept: a retry runs the tool."""
        with self._lock:
            if self._calls.get(key, (0.0, None))[1] is future:
                del self._calls[key]
        future.set_exception(error)

    def _expire(self) -> None:
        cutoff = time.monotonic() - self.ttl
        while self._calls:
            key, (started, future) = next(iter(self._calls.items()))
            if started >= cutoff and len(self._calls) <= self.max_entries:
                break
            if not future.done() and len(self._calls) <= self.max_entries:
                break
            del self._calls[key]


def _key(name: str, raw_data: dict[str, Any] | None) -> tuple[str, str, str] | None:
    if not isinstance(raw_data, dict):
        return None
    tool_call_id = raw_data.get("tool_call_id")
    call_id = raw_data.get("call_id")
    if not isinstance(tool_call_id, str) or not tool_call_id:
        return None
    return (str(call_id or ""), tool_call_id, name)


def _await_first(future: concurrent.futures.Future[Any]) -> Any:
    """The first attempt's result, for a retry: waited for on this thread,
    or awaited when an event loop runs here."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return future.result()
    return asyncio.wrap_future(future)
