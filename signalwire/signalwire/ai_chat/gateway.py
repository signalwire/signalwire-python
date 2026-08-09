"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

A browser-facing gateway for the SignalWire AI Chat service.

The problem it solves: a chat widget running in a page cannot hold a
SignalWire API token. The token carries the whole project, so putting it in
JavaScript hands every visitor the ability to run up turns — and every turn
bills. Yet the widget has to reach the chat service somehow.

So it doesn't. The widget talks to a gateway you mount in your own app, which
holds the credential server-side and forwards on the widget's behalf::

    browser ──(publishable key)──▶ your app ──(project:token)──▶ chat service

The browser learns exactly two things: the gateway's URL and a publishable
key. Not the project, not the space, not the token, and not which agent
config runs — the gateway injects ``config_url`` itself, so a key can only
ever reach the one script it was issued for.

Mount it on an existing FastAPI app (an ``AgentBase`` already serves one, so
this costs you no new infrastructure)::

    from signalwire.ai_chat import ChatGateway

    gateway = ChatGateway(
        config_url="https://my-agent.example.com/swml",
        key="pk_live_...",                       # what the widget carries
        allowed_origins=["https://shop.example.com"],
    )
    agent.get_app().include_router(gateway.router(), prefix="/chat")

## What a stolen key gets you

Nothing to read: ``chat_log`` is not exposed, and a conversation handle is
signed by the gateway, so ids cannot be guessed or enumerated. What it gets
you is the ability to *talk*, which costs the project money. That makes the
caps the primary control rather than a nicety — see ``max_new_conversations``
and ``max_turns``, which bound the bill from both directions: how many
conversations can exist, and how long each can run.

The origin allowlist is a second layer, and an honest description of it is:
it stops a key pasted into someone else's page, because a browser will send
their origin and we refuse it. It does not stop anyone using curl. Treat it
as leak containment, not access control.
"""

import base64
import hashlib
import hmac
import os
import secrets
import time
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from .client import AIChatClient

if TYPE_CHECKING:  # pragma: no cover - typing only
    from fastapi import APIRouter

# A handle outlives a page refresh but not a session left open overnight.
DEFAULT_HANDLE_TTL = 24 * 60 * 60

# Caps chosen to be invisible to a real conversation and ruinous to a script.
DEFAULT_MAX_NEW_CONVERSATIONS = 60      # per window, per gateway
DEFAULT_MAX_TURNS = 200                 # per conversation, ever
DEFAULT_WINDOW_SECONDS = 60

# Hosts that never need listing, so `pip install` → run → it works.
_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1", "[::1]"})

ALLOWED_METHODS = frozenset({"start", "chat", "log", "end"})

# Roles a browser may see. `chat_log` returns the WHOLE conversation as the
# service holds it — the substituted system prompt, tool calls, tool results.
# The system prompt is the developer's own content and the tool traffic is
# nobody's business, so the transcript is filtered down to what the visitor
# already watched go past.
VISIBLE_ROLES = frozenset({"user", "assistant"})


class GatewayRejection(Exception):
    """A request the gateway refused, with the status the browser should see.

    Deliberately coarse: the browser is told *that* it was refused and, at
    most, which of a handful of buckets it fell into. Anything finer would
    let a caller map out the caps and the allowlist by probing.
    """

    def __init__(self, status: int, reason: str) -> None:
        self.status = status
        self.reason = reason
        super().__init__(f"{status}: {reason}")


class ChatGateway:
    """Server-side proxy that lets a browser chat without holding a token.

    Args:
        config_url: The agent this key may talk to. Injected on every call —
            never accepted from the request, or whoever holds a key would
            choose which agent runs.
        key: The publishable key the widget carries. Generated for you if
            omitted, which is only useful for a process that also serves the
            page and can embed it.
        allowed_origins: Origins permitted to use this key. Localhost is
            always allowed so local development works unconfigured; anything
            else must be listed, so nothing ships open by accident.
        client: An ``AIChatClient``. Built from the environment if omitted.
        secret: HMAC key for signing handles. Random per process if omitted —
            which invalidates outstanding handles on restart, so set it
            explicitly if you run more than one replica or restart often.
        handle_ttl: Seconds a handle stays valid.
        max_new_conversations: New conversations per ``window_seconds``. The
            cap that matters: a leaked key does not need to hammer one
            conversation, it mints thousands of one-turn ones, and every one
            of those bills its opening turn.
        max_turns: Turns a single conversation may run.
        window_seconds: Window for ``max_new_conversations``.

    Counters live in this process. Behind several replicas each holds its own,
    so the effective cap multiplies by replica count — set them with that in
    mind, or put a shared limiter in front.
    """

    def __init__(
        self,
        *,
        config_url: str,
        key: str | None = None,
        allowed_origins: list[str] | tuple[str, ...] = (),
        client: AIChatClient | None = None,
        secret: bytes | str | None = None,
        handle_ttl: int = DEFAULT_HANDLE_TTL,
        max_new_conversations: int = DEFAULT_MAX_NEW_CONVERSATIONS,
        max_turns: int = DEFAULT_MAX_TURNS,
        window_seconds: int = DEFAULT_WINDOW_SECONDS,
    ) -> None:
        if not config_url:
            raise ValueError("config_url is required — it is what a key is scoped to.")

        self.config_url = config_url
        self.key = key or os.environ.get("SIGNALWIRE_CHAT_GATEWAY_KEY") or (
            "pk_" + secrets.token_urlsafe(24)
        )
        self.allowed_origins = {o.rstrip("/") for o in allowed_origins}
        self.handle_ttl = handle_ttl
        self.max_new_conversations = max_new_conversations
        self.max_turns = max_turns
        self.window_seconds = window_seconds

        self._client = client or AIChatClient()
        self._owns_client = client is None

        if secret is None:
            secret = os.environ.get("SIGNALWIRE_CHAT_GATEWAY_SECRET") or secrets.token_bytes(32)
        self._secret = secret.encode() if isinstance(secret, str) else secret

        self._mints: list[float] = []
        self._turns: dict[str, tuple[int, float]] = {}

    async def close(self) -> None:
        if self._owns_client:
            await self._client.close()

    # ── Handles ──────────────────────────────────────────────────────

    def mint_handle(self, conversation_id: str | None = None) -> str:
        """Issue a signed handle for a new conversation.

        The browser never names a conversation. If it did, a publishable key
        plus a guessed id would be enough to continue someone else's chat;
        signing means a caller can only present handles this gateway issued.
        """
        conversation_id = conversation_id or f"chat-{secrets.token_urlsafe(18)}"
        expires = int(time.time()) + self.handle_ttl
        payload = f"{conversation_id}:{expires}".encode()
        sig = hmac.new(self._secret, payload, hashlib.sha256).digest()
        return f"{_b64(payload)}.{_b64(sig)}"

    def read_handle(self, handle: str) -> str:
        """Return the conversation id inside a handle, or raise.

        Signature first, expiry second, both before the id is trusted for
        anything.
        """
        try:
            raw, sig = handle.split(".", 1)
            payload = _unb64(raw)
            given = _unb64(sig)
        except Exception as err:
            raise GatewayRejection(400, "malformed handle") from err

        expected = hmac.new(self._secret, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(given, expected):
            raise GatewayRejection(403, "invalid handle")

        try:
            conversation_id, expires = payload.decode().rsplit(":", 1)
            if time.time() > int(expires):
                raise GatewayRejection(403, "expired handle")
        except GatewayRejection:
            raise
        except Exception as err:
            raise GatewayRejection(400, "malformed handle") from err
        return conversation_id

    # ── Guards ───────────────────────────────────────────────────────

    def check_origin(self, origin: str | None) -> None:
        """Localhost always; anything else must be listed.

        A missing ``Origin`` is allowed: browsers always send one for the
        cross-origin POSTs this serves, so absence means a non-browser caller
        — and refusing those would break server-side use without stopping an
        attacker, who simply omits the header.
        """
        if origin is None:
            return
        host = urlparse(origin).hostname or ""
        if host in _LOCAL_HOSTS or host.endswith(".localhost"):
            return
        if origin.rstrip("/") in self.allowed_origins:
            return
        raise GatewayRejection(403, "origin not allowed")

    def check_key(self, presented: str | None) -> None:
        if not presented or not hmac.compare_digest(presented, self.key):
            raise GatewayRejection(401, "bad key")

    @staticmethod
    def visible_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
        """The transcript a browser may redraw, and nothing else.

        `chat_log` hands back the conversation as the service holds it: the
        substituted system prompt first, then tool calls and their results
        alongside the dialogue. Relaying that verbatim would publish the
        developer's prompt to anyone holding a handle. Only user and assistant
        turns with actual text survive, reduced to role and content — no
        timestamps, no tool_calls, no ids.
        """
        out = []
        for msg in messages or []:
            if not isinstance(msg, dict):
                continue
            role = msg.get("role")
            content = msg.get("content")
            if role in VISIBLE_ROLES and isinstance(content, str) and content.strip():
                out.append({"role": role, "content": content})
        return out

    def _charge_mint(self) -> None:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        self._mints = [t for t in self._mints if t > cutoff]
        if len(self._mints) >= self.max_new_conversations:
            raise GatewayRejection(429, "too many new conversations")
        self._mints.append(now)

    def _charge_turn(self, conversation_id: str) -> None:
        now = time.monotonic()
        # Sweep here rather than on a timer: a handle cannot outlive its TTL,
        # so anything older can never be charged against again.
        cutoff = now - self.handle_ttl
        self._turns = {k: v for k, v in self._turns.items() if v[1] > cutoff}
        count, _ = self._turns.get(conversation_id, (0, now))
        if count >= self.max_turns:
            raise GatewayRejection(429, "conversation turn limit reached")
        self._turns[conversation_id] = (count + 1, now)

    # ── The proxied call ─────────────────────────────────────────────

    def prepare(self, body: dict[str, Any], *, origin: str | None,
                key: str | None) -> tuple[str, dict[str, Any], str | None]:
        """Validate a browser request and build the upstream JSON-RPC call.

        Returns ``(method, params, minted_handle)`` — ``minted_handle`` is set
        only on the call that created the conversation, so the caller can
        hand it back.

        Everything the browser could use to widen its own access is either
        rejected or overwritten here: the method must be one of two, the
        conversation comes from a signed handle, and ``config_url`` is ours.
        """
        self.check_key(key)
        self.check_origin(origin)

        method = body.get("method", "chat")
        if method not in ALLOWED_METHODS:
            raise GatewayRejection(400, "method not allowed")

        handle = body.get("handle")
        minted = None
        if handle:
            conversation_id = self.read_handle(handle)
        elif method in ("end", "log"):
            raise GatewayRejection(400, f"{method} requires a handle")
        else:
            self._charge_mint()
            minted = self.mint_handle()
            conversation_id = self.read_handle(minted)

        if method == "end":
            return "end_conversation", {"id": conversation_id}, None

        if method == "log":
            # Scoped to the conversation named INSIDE the signed handle, never
            # to anything the caller sent, so a handle reads one conversation
            # and only for as long as it is valid.
            return "chat_log", {"id": conversation_id}, None

        if method == "start":
            # Opens the conversation with no user message, so the agent speaks
            # first. Separate from `chat` because the auto-create path needs a
            # message to ride on, and a widget wants the greeting before the
            # visitor has typed anything.
            return "create_conversation", {
                "id": conversation_id,
                "config_url": self.config_url,
            }, minted

        message = body.get("message")
        if not isinstance(message, str) or not message.strip():
            raise GatewayRejection(400, "message is required")

        self._charge_turn(conversation_id)
        # config_url on every chat so the service auto-creates on the first
        # one and ignores it after — no separate create method on the wire,
        # and nothing for the browser to point somewhere else.
        return "chat", {
            "id": conversation_id,
            "message": message,
            "config_url": self.config_url,
        }, minted

    # ── FastAPI surface ──────────────────────────────────────────────

    def router(self) -> "APIRouter":
        """An ``APIRouter`` exposing this gateway.

        ``POST /`` takes ``{"method": "chat"|"end", "handle"?, "message"?}``
        with the key in ``Authorization: Bearer``. A chat streams the
        service's JSON-RPC response body through **unbuffered** — the service
        pads slow turns with keepalive whitespace so proxies do not sever the
        connection, and collecting the body here would swallow that padding
        and recreate the timeout inside your own stack. A newly minted handle
        rides back in the ``X-Chat-Handle`` header, which is why it can be
        sent before the body has been produced.
        """
        from fastapi import APIRouter, Request
        from fastapi.responses import JSONResponse, Response, StreamingResponse

        router = APIRouter()

        def _cors(origin: str | None) -> dict[str, str]:
            if origin is None:
                return {}
            try:
                self.check_origin(origin)
            except GatewayRejection:
                return {}
            return {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Expose-Headers": "X-Chat-Handle",
                "Vary": "Origin",
            }

        @router.options("/")
        async def preflight(request: Request) -> Response:
            origin = request.headers.get("origin")
            headers = _cors(origin)
            if headers:
                headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
                headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
                headers["Access-Control-Max-Age"] = "600"
            return Response(status_code=204, headers=headers)

        @router.post("/")
        async def proxy(request: Request) -> Response:
            origin = request.headers.get("origin")
            auth = request.headers.get("authorization", "")
            key = auth[7:] if auth.lower().startswith("bearer ") else None
            cors = _cors(origin)

            try:
                body = await request.json()
                if not isinstance(body, dict):
                    raise GatewayRejection(400, "body must be an object")
                method, params, minted = self.prepare(body, origin=origin, key=key)
            except GatewayRejection as rej:
                return JSONResponse(
                    {"error": rej.reason}, status_code=rej.status, headers=cors
                )
            except Exception:
                return JSONResponse(
                    {"error": "bad request"}, status_code=400, headers=cors
                )

            if method == "end_conversation":
                await self._client.end(params["id"])
                return JSONResponse({"status": "ended"}, headers=cors)

            if method == "create_conversation":
                info = await self._client.create_conversation(
                    params["id"], config_url=params["config_url"]
                )
                if minted:
                    cors["X-Chat-Handle"] = minted
                return JSONResponse(
                    {"greeting": info.initial_message, "status": info.status},
                    headers=cors,
                )

            if method == "chat_log":
                log = await self._client.log(params["id"])
                return JSONResponse(
                    {"messages": self.visible_messages(log.messages)}, headers=cors
                )

            headers = dict(cors)
            if minted:
                headers["X-Chat-Handle"] = minted

            async def stream() -> Any:
                async with self._client.raw_post(method, params) as resp:
                    async for chunk in resp.content.iter_any():
                        yield chunk

            return StreamingResponse(
                stream(), media_type="application/json", headers=headers
            )

        return router


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
