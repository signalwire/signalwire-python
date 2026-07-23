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
from typing import Any, Dict, List, Optional

import aiohttp

from signalwire.rest._base import _user_agent

DEFAULT_PATH = "/api/ai/chat"


# ── Errors ───────────────────────────────────────────────────────────

class AIChatError(Exception):
    """Base error for AI Chat service failures."""

    def __init__(self, code: Optional[int], message: str) -> None:
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
    initial_message: Optional[str] = None


@dataclass
class ChatResponse:
    text: str
    conversation_id: str
    user_event: Optional[Dict[str, Any]] = None


@dataclass
class ChatLog:
    messages: List[Dict[str, Any]] = field(default_factory=list)
    call_timeline: List[Dict[str, Any]] = field(default_factory=list)


# ── Client ───────────────────────────────────────────────────────────

class AIChatClient:
    """Async client for the SignalWire AI Chat service."""

    def __init__(
        self,
        project: Optional[str] = None,
        token: Optional[str] = None,
        space: Optional[str] = None,
        url: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
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
    def _resolve_url(url: Optional[str], space: str) -> str:
        if url:
            return url
        dev_url = os.environ.get("RAILS_DEV_MODE", "").strip()
        if dev_url and dev_url.lower() not in ("false", "0", "no", "off", "true", "1", "yes", "on"):
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
                auth=self._auth, headers=self._headers
            )
        return self._session

    async def close(self) -> None:
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    # ── Wire ─────────────────────────────────────────────────────────

    async def _request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
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
            except (aiohttp.ContentTypeError, ValueError):
                raise AIChatError(resp.status, f"non-JSON response (HTTP {resp.status})")
        if "error" in body:
            error = body["error"] or {}
            code = error.get("code")
            raise _ERROR_BY_CODE.get(code, AIChatError)(code, error.get("message", ""))
        return body.get("result") or {}

    # ── API methods ──────────────────────────────────────────────────

    async def create_conversation(
        self,
        conversation_id: str,
        config_url: str,
        user_message: Optional[str] = None,
        timeout: Optional[int] = None,
        user_metadata: Optional[Dict[str, Any]] = None,
        reinit: bool = False,
    ) -> ConversationInfo:
        """Create a conversation (or reinitialize an existing one)."""
        params: Dict[str, Any] = {"id": conversation_id, "config_url": config_url}
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
        config_url: Optional[str] = None,
        user_metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """Send a message and return the AI reply.

        This awaits a full LLM round trip server-side — expect seconds.
        Passing ``config_url`` auto-creates the conversation if it doesn't
        exist yet.
        """
        params: Dict[str, Any] = {
            "id": conversation_id, "message": message, "role": role,
        }
        if config_url:
            params["config_url"] = config_url
        if user_metadata:
            params["user_meta_data"] = user_metadata
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
        summary_prompt: Optional[str] = None,
        **sampling: Any,
    ) -> str:
        """AI summary of the conversation (rate limited server-side)."""
        params: Dict[str, Any] = {"id": conversation_id}
        if summary_prompt:
            params["summary_prompt"] = summary_prompt
        params.update({k: v for k, v in sampling.items() if v is not None})
        result = await self._request("summarize", params)
        return result.get("summary", "")
