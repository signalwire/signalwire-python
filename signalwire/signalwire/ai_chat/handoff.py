#!/usr/bin/env python3
"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Moving one conversation between voice and text.

:class:`~signalwire.ai_chat.gateway.ChatGateway` lets a browser hold a text
conversation. This module is the other half of what a browser client needs: the
three routes it calls to move that conversation to a phone call and back, and
to type into a live call.

Why this is in the SDK rather than in each application: the browser side is
already shipped. The SignalWire address widget hardcodes ``{gateway-url}/handoff``,
``{gateway-url}/escalate`` and ``{gateway-url}/say`` against the same URL that
points at a ``ChatGateway``, and sends ``handoff_nonce`` and ``chat_handle`` as
user variables. Without these routes a gateway answers the widget's JSON-RPC
and 404s everything else -- so the SDK would be shipping a gateway its own
widget considers incomplete, with the missing half specified nowhere.

MECHANISM VS POLICY
-------------------
This class owns the wire contract only: the routes, the nonce, the ordering
guarantee, and the spend guards. It owns nothing about what a conversation
*is*. Where a leg's transcript gets written, what a resumed greeting says, how
much history to carry -- all of that is the application's, injected as
callbacks.

THE NONCE
---------
A browser cannot be trusted to name a call. ``ai_message`` takes a ``call_id``,
and a page-supplied one would let anyone who learned or guessed an id inject
speech into a stranger's live call. So the browser proves which call it is on
instead: the application puts a random ``handoff_nonce`` in the user variables
of one dial, registers it here against that call's ids, and the browser
presents it later. The nonce appears nowhere else, so knowing it is proof of
having placed the call.

Redemption for a handle is single use. Typing is not -- it is repeatable for
the life of the call, bounded by ``max_messages_per_call``.

An unknown nonce is answered exactly like an expired one, so this cannot be
used to probe whether a given call is live.

THE ORDERING GUARANTEE
----------------------
A medium never starts until the one it replaces has finished and its record is
durable. ``/handoff`` ends the call and waits for the application to confirm
capture before minting a handle; ``/escalate`` ends the chat leg and waits
before returning. Skipping the wait means the new medium's config fetch races a
record that is still seconds away, and it opens knowing nothing -- which is
what polling and retries elsewhere end up papering over.

The wait is event-driven. An earlier polling implementation deadlocked: a
synchronous sleep inside an async route blocked the event loop, and therefore
blocked the very webhook it was waiting for, which then arrived milliseconds
after the wait timed out -- every time.

DEPLOYMENT
----------
The nonce registry lives in this process, like ``ChatGateway``'s rate-limit
counters. A redemption must reach the replica that served the dial. Run one
replica, use sticky routing, or supply a shared ``registry``.
"""

# NOTE: deliberately no `from __future__ import annotations` -- FastAPI resolves
# route annotations against module globals, and `Request` is imported inside
# router() below. Stringified annotations would make it unresolvable, and
# FastAPI would silently treat `request` as a query parameter (422 on every
# call). gateway.py avoids the future import for the same reason.
import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from signalwire.core.logging_config import get_logger

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import APIRouter

    from signalwire.ai_chat.gateway import ChatGateway

logger = get_logger("ai_chat.handoff")

__all__ = ["HandoffRouter", "NonceEntry"]

DEFAULT_NONCE_TTL = 3600
DEFAULT_MAX_MESSAGES_PER_CALL = 200
DEFAULT_CAPTURE_TIMEOUT = 8.0


@dataclass
class NonceEntry:
    """What a nonce is a capability for."""

    conversation_id: str
    call_id: str | None = None
    issued_at: float = field(default_factory=time.monotonic)
    messages: int = 0


# Application-supplied policy.
#
# capture_leg(conversation_id, medium) -> awaitable/bool
#     End the leg and write its record. Return True once the record is durable.
#     Called before the replacement medium is allowed to exist.
# end_call(call_id) -> awaitable/None
#     Hang the call up server-side so its teardown hooks fire immediately.
# send_message(call_id, text) -> awaitable/bool
#     Inject typed text into the live call as if the caller had spoken it.
CaptureLeg = Callable[[str, str], "Awaitable[bool] | bool"]
EndCall = Callable[[str], "Awaitable[None] | None"]
SendMessage = Callable[[str, str], "Awaitable[bool] | bool"]


async def _maybe_await(value: Any) -> Any:
    """Allow every injected callback to be sync or async."""
    if asyncio.iscoroutine(value) or isinstance(value, asyncio.Future):
        return await value
    return value


class HandoffRouter:
    """The three routes a browser client needs beside a :class:`ChatGateway`.

    Args:
        gateway: The gateway that owns the conversations. Used to mint handles
            and to check origins, so both halves of the URL enforce the same
            origin policy.
        capture_leg: Called as ``capture_leg(conversation_id, medium)`` to end
            a leg and write its record. Must return truthy only once that
            record is durable. May be sync or async. When omitted, no wait
            happens and the ordering guarantee is not provided.
        end_call: Called as ``end_call(call_id)`` to hang up server-side.
        send_message: Called as ``send_message(call_id, text)`` for ``/say``.
            Omit to leave typing disabled (the route then answers 404).
        next_conversation_id: Called as ``next_conversation_id(conversation_id)``
            to produce the id for the NEW leg. Defaults to appending ``.N``.
            A fresh id is required because an ended conversation cannot be
            reopened; the separator must be ``.`` -- see
            ``_warn_if_id_will_be_altered`` in ``ai_chat.client``.
        nonce_ttl: Seconds a nonce stays redeemable.
        max_messages_per_call: Ceiling on typed messages for one call. Each is
            a billable turn, so this is a spend guard as much as an abuse one.
        capture_timeout: Seconds to wait for ``capture_leg``. A ceiling, not a
            budget -- capture is normally sub-second.
        registry: Optional shared mapping for the nonce table. Supply one
            backed by shared storage to run more than one replica.
    """

    def __init__(
        self,
        *,
        gateway: "ChatGateway",
        capture_leg: CaptureLeg | None = None,
        end_call: EndCall | None = None,
        send_message: SendMessage | None = None,
        next_conversation_id: Callable[[str], str] | None = None,
        nonce_ttl: int = DEFAULT_NONCE_TTL,
        max_messages_per_call: int = DEFAULT_MAX_MESSAGES_PER_CALL,
        capture_timeout: float = DEFAULT_CAPTURE_TIMEOUT,
        registry: dict[str, NonceEntry] | None = None,
    ) -> None:
        self.gateway = gateway
        self.capture_leg = capture_leg
        self.end_call = end_call
        self.send_message = send_message
        self.next_conversation_id = next_conversation_id or self._default_next_id
        self.nonce_ttl = nonce_ttl
        self.max_messages_per_call = max_messages_per_call
        self.capture_timeout = capture_timeout
        self._nonces: dict[str, NonceEntry] = registry if registry is not None else {}

    # -- nonce lifecycle ---------------------------------------------------

    @staticmethod
    def _default_next_id(conversation_id: str) -> str:
        """``root`` -> ``root.1``; ``root.2`` -> ``root.3``.

        ``.`` specifically: the chat service strips ``~`` silently, ``_`` and
        ``-`` already occur inside generated ids so a suffix built from either
        cannot be distinguished from the id it was appended to, and ``:`` is
        the gateway's handle delimiter.
        """
        root, _, tail = conversation_id.rpartition(".")
        if root and tail.isdigit():
            return f"{root}.{int(tail) + 1}"
        return f"{conversation_id}.1"

    def register(
        self, nonce: str, *, conversation_id: str, call_id: str | None = None
    ) -> None:
        """Record what a nonce is a capability for.

        Call this from the dynamic-config callback of the dial that carried the
        nonce, reading ``call_id`` from the request the platform sent -- never
        from anything the browser supplied.
        """
        if not nonce or not isinstance(nonce, str):
            return
        self._prune()
        self._nonces[nonce] = NonceEntry(
            conversation_id=conversation_id, call_id=call_id
        )
        logger.info(
            "handoff_nonce_registered",
            conversation_id=conversation_id,
            call_id=call_id,
        )

    def _prune(self) -> None:
        cutoff = time.monotonic() - self.nonce_ttl
        for nonce in [n for n, e in self._nonces.items() if e.issued_at < cutoff]:
            self._nonces.pop(nonce, None)

    def _lookup(self, nonce: Any) -> NonceEntry | None:
        if not nonce or not isinstance(nonce, str):
            return None
        self._prune()
        return self._nonces.get(nonce)

    # -- operations --------------------------------------------------------

    async def _capture(self, conversation_id: str, medium: str) -> bool:
        """Await the application's capture, bounded. Never raises."""
        if self.capture_leg is None:
            return False
        try:
            return bool(
                await asyncio.wait_for(
                    _maybe_await(self.capture_leg(conversation_id, medium)),
                    timeout=self.capture_timeout,
                )
            )
        except TimeoutError:
            logger.warning(
                "handoff_capture_timeout",
                conversation_id=conversation_id,
                medium=medium,
                note="starting the next medium without this leg's record",
            )
        except Exception as exc:
            logger.error(
                "handoff_capture_failed",
                conversation_id=conversation_id,
                error=str(exc),
            )
        return False

    async def redeem(self, nonce: str) -> str | None:
        """Exchange a nonce for a chat handle. Single use.

        Ends the call, waits for its record, and only then mints a handle for a
        new leg of the same conversation.

        Returns:
            The signed handle, or None for an unknown, expired or already
            redeemed nonce -- deliberately indistinguishable from each other.
        """
        entry = self._lookup(nonce)
        if entry is None:
            return None
        # Consumed even if what follows fails: a nonce is one attempt.
        self._nonces.pop(nonce, None)

        if entry.call_id and self.end_call is not None:
            try:
                await _maybe_await(self.end_call(entry.call_id))
            except Exception as exc:
                logger.warning("handoff_end_call_failed", error=str(exc))

        await self._capture(entry.conversation_id, "voice")

        try:
            handle: str = self.gateway.mint_handle(
                self.next_conversation_id(entry.conversation_id)
            )
        except Exception as exc:
            logger.error("handoff_mint_failed", error=str(exc))
            return None

        logger.info("handoff_redeemed", conversation_id=entry.conversation_id)
        return handle

    async def escalate(self, handle: str) -> bool:
        """End a chat leg and wait for its record, before a call is placed.

        The browser calls this and waits, so a voice leg started immediately
        afterwards is guaranteed to find the text leg already recorded.
        """
        try:
            conversation_id = self.gateway.read_handle(handle)
        except Exception:
            return False
        await self._capture(conversation_id, "chat")
        logger.info("handoff_escalated", conversation_id=conversation_id)
        return True

    async def say(self, nonce: str, text: str) -> bool:
        """Deliver typed text into the live call the nonce names.

        Does NOT consume the nonce -- typing is repeatable for the life of the
        call. Addressed by nonce rather than by any browser-supplied call id,
        and no other request field is forwarded: ``global_data`` in particular
        is trusted agent state that step logic branches on, and letting a page
        write it would be a far larger hole than injecting text.
        """
        if self.send_message is None:
            return False
        cleaned = (text or "").strip()
        if not cleaned:
            return False
        entry = self._lookup(nonce)
        if entry is None or not entry.call_id:
            return False
        if entry.messages >= self.max_messages_per_call:
            logger.warning("handoff_say_cap_reached", call_id=entry.call_id)
            return False
        try:
            await _maybe_await(self.send_message(entry.call_id, cleaned))
        except Exception as exc:
            logger.error("handoff_say_failed", error=str(exc))
            return False
        entry.messages += 1
        return True

    # -- transport ---------------------------------------------------------

    def router(self) -> "APIRouter":
        """Build the router. Mount at the SAME prefix as the gateway's.

        The browser derives all three paths from one configured URL, so they
        must be siblings of the gateway's JSON-RPC endpoint::

            agent.mount(gateway.router(), prefix="/chat")
            agent.mount(handoff.router(), prefix="/chat")
        """
        from fastapi import APIRouter, Request
        from fastapi.responses import JSONResponse

        router = APIRouter()

        def _forbidden_origin(request: Request) -> JSONResponse | None:
            try:
                self.gateway.check_origin(request.headers.get("origin"))
            except Exception:
                return JSONResponse({"error": "origin not allowed"}, status_code=403)
            return None

        async def _body(request: Request) -> dict[str, Any]:
            try:
                data = await request.json()
            except Exception:
                return {}
            return data if isinstance(data, dict) else {}

        @router.post("/handoff")
        async def _handoff(request: Request) -> JSONResponse:
            denied = _forbidden_origin(request)
            if denied:
                return denied
            nonce = (await _body(request)).get("nonce")
            if not isinstance(nonce, str):
                return JSONResponse({"error": "not found"}, status_code=404)
            handle = await self.redeem(nonce)
            if not handle:
                # Same answer for unknown, expired and already-redeemed.
                return JSONResponse({"error": "not found"}, status_code=404)
            return JSONResponse({"handle": handle})

        @router.post("/escalate")
        async def _escalate(request: Request) -> JSONResponse:
            denied = _forbidden_origin(request)
            if denied:
                return denied
            handle = (await _body(request)).get("handle")
            if not handle or not isinstance(handle, str):
                return JSONResponse({"error": "bad request"}, status_code=400)
            if not await self.escalate(handle):
                return JSONResponse({"error": "not found"}, status_code=404)
            return JSONResponse({"ok": True})

        @router.post("/say")
        async def _say(request: Request) -> JSONResponse:
            denied = _forbidden_origin(request)
            if denied:
                return denied
            data = await _body(request)
            nonce = data.get("nonce")
            text = data.get("text", "")
            if not isinstance(nonce, str) or not isinstance(text, str):
                return JSONResponse({"error": "not found"}, status_code=404)
            if not await self.say(nonce, text):
                return JSONResponse({"error": "not found"}, status_code=404)
            return JSONResponse({"ok": True})

        return router
