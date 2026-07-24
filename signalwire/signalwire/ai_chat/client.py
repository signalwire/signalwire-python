"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Async client for the SignalWire AI Chat service.

The client speaks the standard SignalWire front-door protocol: HTTP Basic
``project:api_token`` with the space in the hostname —
``POST https://{space}.signalwire.com/api/ai/chat`` — carrying a JSON-RPC 2.0
body whose params are pure payload (identity never appears in the body).

Async-first by design: a ``chat()`` call waits on a full LLM round trip
(seconds, not milliseconds), and the typical consumers — bots, MCP servers —
run on asyncio event loops where a blocking HTTP call would stall every other
conversation. Use it as an async context manager::

    from signalwire.ai_chat import AIChatClient

    async with AIChatClient(space="myspace") as client:  # env supplies creds
        await client.create_conversation("conv-1", config_url=CONFIG_URL)
        reply = await client.chat("conv-1", "hello")
        print(reply.text)

URL resolution, in order:

1. ``url=`` constructor argument — used verbatim.
2. ``RAILS_DEV_MODE`` environment variable — a full URL used verbatim
   (point it at a dev chat service, e.g. ``http://localhost:8080/``).
3. ``https://{space}.signalwire.com/api/ai/chat`` built from ``space``
   (argument or ``SIGNALWIRE_SPACE``).

Credentials come from the constructor or the standard environment variables
``SIGNALWIRE_PROJECT_ID`` / ``SIGNALWIRE_API_TOKEN``.
"""

import os
from dataclasses import dataclass, field
from typing import Any

import aiohttp

from signalwire.rest._base import _user_agent

DEFAULT_PATH = "/api/ai/chat"

# The service streams keepalive whitespace ahead of slow responses (every
# ~10s), so liveness is byte-driven, not wall-clock: no total cap (turn
# length is the server's business), ``sock_read`` as the dead-connection
# detector (60s of true byte silence means the request is dead — the proxy
# itself severs after 30s of upstream silence), and a bounded connect.
# The leading whitespace is valid JSON, so ``resp.json()`` is unaffected.
# Pass your own ``session=`` to override.
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=None, connect=10, sock_read=60)


# ── Errors ───────────────────────────────────────────────────────────


class AIChatError(Exception):
    """Base error for AI Chat service failures."""

    def __init__(self, code: int | None, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class AuthenticationError(AIChatError):
    """Missing/rejected identity (HTTP 401 / JSON-RPC -32009)."""


class ConversationNotFoundError(AIChatError):
    """The conversation does not exist in this project (-32001)."""


class RateLimitError(AIChatError):
    """Project or conversation rate limit hit (-32005 / -32006)."""


class ChatInProgressError(AIChatError):
    """Another message is being processed for this conversation (-32007)."""


class SummaryError(AIChatError):
    """Summary generation failed. ``summarize`` returns EXACTLY ONE of
    ``{summary}`` (success) or ``{error}`` (generation failed), and the failure
    rides the JSON-RPC *success* envelope — not an ``error`` object — so it never
    reaches the ``_ERROR_BY_CODE`` mapping. Surfaced here so a failed summary
    can't masquerade as an empty string. ``code`` is None (no JSON-RPC code)."""


_ERROR_BY_CODE = {
    -32001: ConversationNotFoundError,
    -32005: RateLimitError,
    -32006: RateLimitError,
    -32007: ChatInProgressError,
    -32009: AuthenticationError,
}


# ── Response models ──────────────────────────────────────────────────


@dataclass
class ConversationInfo:
    id: str
    status: str
    initial_message: str | None = None


@dataclass
class ChatResponse:
    text: str
    conversation_id: str
    user_event: dict[str, Any] | None = None


@dataclass
class ChatLog:
    messages: list[dict[str, Any]] = field(default_factory=list)
    call_timeline: list[dict[str, Any]] = field(default_factory=list)


# ── Client ───────────────────────────────────────────────────────────


class AIChatClient:
    """Async client for the SignalWire AI Chat service."""

    def __init__(
        self,
        project: str | None = None,
        token: str | None = None,
        space: str | None = None,
        url: str | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._project = project or os.environ.get("SIGNALWIRE_PROJECT_ID", "")
        self._token = token or os.environ.get("SIGNALWIRE_API_TOKEN", "")
        space = space or os.environ.get("SIGNALWIRE_SPACE", "")

        if not self._project:
            raise ValueError(
                "project is required. Provide it as an argument or set the "
                "SIGNALWIRE_PROJECT_ID environment variable."
            )

        self.url = self._resolve_url(url, space)
        self._auth = aiohttp.BasicAuth(self._project, self._token)
        self._headers = {"User-Agent": _user_agent()}
        self._session = session
        self._owns_session = session is None
        self._request_counter = 0

    @staticmethod
    def _resolve_url(url: str | None, space: str) -> str:
        if url:
            return url
        dev_url = os.environ.get("RAILS_DEV_MODE", "").strip()
        if dev_url and dev_url.lower() not in (
            "false",
            "0",
            "no",
            "off",
            "true",
            "1",
            "yes",
            "on",
        ):
            # RAILS_DEV_MODE doubles as the service's persona switch, so
            # plain booleans mean "on" without carrying a URL — only a real
            # URL-looking value overrides the target here.
            return dev_url
        if space:
            return f"https://{space}.signalwire.com{DEFAULT_PATH}"
        raise ValueError(
            "No service URL: provide url=, set RAILS_DEV_MODE to a full URL, "
            "or provide space= / SIGNALWIRE_SPACE."
        )

    # ── Session lifecycle ────────────────────────────────────────────

    async def __aenter__(self) -> "AIChatClient":
        await self._ensure_session()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                auth=self._auth, headers=self._headers, timeout=DEFAULT_TIMEOUT
            )
        return self._session

    async def close(self) -> None:
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    # ── Wire ─────────────────────────────────────────────────────────

    async def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        session = await self._ensure_session()
        self._request_counter += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": f"req-{self._request_counter}",
        }
        async with session.post(self.url, json=payload) as resp:
            try:
                body = await resp.json()
            except (aiohttp.ContentTypeError, ValueError) as err:
                raise AIChatError(
                    resp.status, f"non-JSON response (HTTP {resp.status})"
                ) from err
        # Success/failure is decided by the JSON-RPC body, NOT the HTTP status:
        # the service's keepalive heartbeat commits ``200`` before the turn's
        # outcome is known (heartbeat.py), so a slow error arrives as
        # ``200 + {"error": …}``. Never gate on ``resp.status`` here.
        if "error" in body:
            error = body["error"] or {}
            code = error.get("code")
            exc_type = (
                _ERROR_BY_CODE.get(code, AIChatError)
                if code is not None
                else AIChatError
            )
            raise exc_type(code, error.get("message", ""))
        result = body.get("result")
        return result if isinstance(result, dict) else {}

    # ── API methods ──────────────────────────────────────────────────

    async def create_conversation(
        self,
        conversation_id: str,
        config_url: str,
        user_message: str | None = None,
        timeout: int | None = None,
        user_metadata: dict[str, Any] | None = None,
        reinit: bool = False,
    ) -> ConversationInfo:
        """Create a conversation (or reinitialize an existing one)."""
        params: dict[str, Any] = {"id": conversation_id, "config_url": config_url}
        if user_message:
            params["user_message"] = user_message
        if timeout:
            params["conversation_timeout"] = timeout
        if user_metadata:
            params["user_meta_data"] = user_metadata
        if reinit:
            params["reinit"] = True
        result = await self._request("create_conversation", params)
        return ConversationInfo(
            id=conversation_id,
            status=result.get("status", "created"),
            initial_message=result.get("initial_message"),
        )

    async def chat(
        self,
        conversation_id: str,
        message: str,
        role: str = "user",
        config_url: str | None = None,
        user_metadata: dict[str, Any] | None = None,
        timeout: int | None = None,
        reinit: bool = False,
    ) -> ChatResponse:
        """Send a message and return the AI reply.

        This awaits a full LLM round trip server-side — expect seconds.
        Passing ``config_url`` auto-creates the conversation if it doesn't
        exist yet; ``timeout`` and ``reinit`` apply to that auto-create,
        with the same meaning as on :meth:`create_conversation`.
        """
        params: dict[str, Any] = {
            "id": conversation_id,
            "message": message,
            "role": role,
        }
        if config_url:
            params["config_url"] = config_url
        if user_metadata:
            params["user_meta_data"] = user_metadata
        if timeout:
            params["conversation_timeout"] = timeout
        if reinit:
            params["reinit"] = True
        result = await self._request("chat", params)
        return ChatResponse(
            text=result.get("response", ""),
            conversation_id=conversation_id,
            user_event=result.get("user_event"),
        )

    async def end(self, conversation_id: str) -> bool:
        """End a conversation (triggers server-side post-processing)."""
        result = await self._request("end_conversation", {"id": conversation_id})
        return result.get("status") == "ended"

    async def delete(self, conversation_id: str) -> bool:
        """Permanently delete a conversation and its data."""
        result = await self._request("delete", {"id": conversation_id})
        return result.get("status") == "deleted"

    async def log(self, conversation_id: str) -> ChatLog:
        """Full message history plus the call timeline."""
        result = await self._request("chat_log", {"id": conversation_id})
        return ChatLog(
            messages=result.get("chat_log", []),
            call_timeline=result.get("call_timeline", []),
        )

    async def summarize(
        self,
        conversation_id: str,
        summary_prompt: str | None = None,
        **sampling: Any,
    ) -> str:
        """AI summary of the conversation (rate limited server-side).

        Raises :class:`SummaryError` when the server reports that summary
        generation failed — the service returns EXACTLY ONE of ``{summary}`` or
        ``{error}`` (both on the success envelope), so a failure must surface as
        an error, never as an empty string.
        """
        params: dict[str, Any] = {"id": conversation_id}
        if summary_prompt:
            params["summary_prompt"] = summary_prompt
        params.update({k: v for k, v in sampling.items() if v is not None})
        result = await self._request("summarize", params)
        if "error" in result and "summary" not in result:
            raise SummaryError(None, str(result["error"]))
        summary = result.get("summary", "")
        return summary if isinstance(summary, str) else str(summary)
