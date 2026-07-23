"""AIChatClient wire contract.

The client always speaks the rails front-door protocol: HTTP Basic
``project:api_token``, JSON-RPC envelope, pure-payload params (identity never
in the body). These tests pin that contract against an in-process stub server
— no live service needed.
"""

import base64
from collections.abc import AsyncIterator
from typing import Any

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from signalwire.ai_chat import (
    AIChatClient,
    AIChatError,
    AuthenticationError,
    ChatInProgressError,
    ConversationNotFoundError,
    RateLimitError,
)

PROJECT = "proj-1"
TOKEN = "tok-1"  # noqa: S105  test placeholder credential, not a real secret


class StubService:
    """Records every request; replies with a canned result or error."""

    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []
        self.result: dict[str, Any] = {
            "status": "created",
            "response": "hi",
            "initial_message": "hello",
        }
        self.error: tuple[int, str] | None = None  # (code, message) -> JSON-RPC error
        self.http_status = 200
        self.url = ""

    def app(self) -> web.Application:
        async def handle(request: web.Request) -> web.Response:
            self.requests.append(
                {
                    "path": request.path,
                    "auth": request.headers.get("Authorization", ""),
                    "user_agent": request.headers.get("User-Agent", ""),
                    "body": await request.json(),
                }
            )
            if self.error:
                code, message = self.error
                return web.json_response(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": code, "message": message},
                        "id": "x",
                    },
                    status=self.http_status,
                )
            return web.json_response(
                {"jsonrpc": "2.0", "result": self.result, "id": "x"}
            )

        app = web.Application()
        app.router.add_post("/api/ai/chat", handle)
        app.router.add_post("/", handle)
        return app


@pytest.fixture
async def stub() -> AsyncIterator[StubService]:
    service = StubService()
    server = TestServer(service.app())
    await server.start_server()
    service.url = str(server.make_url("/api/ai/chat"))
    yield service
    await server.close()


def decode_basic(header: str) -> str:
    assert header.startswith("Basic ")
    return base64.b64decode(header[6:]).decode()


# ── Wire shape ───────────────────────────────────────────────────────


async def test_basic_auth_and_envelope(stub: StubService) -> None:
    async with AIChatClient(PROJECT, TOKEN, url=stub.url) as client:
        await client.chat("conv-1", "hello")
    req = stub.requests[0]
    # Identity rides in Basic auth — project as username
    assert decode_basic(req["auth"]) == f"{PROJECT}:{TOKEN}"
    # SDK-standard User-Agent
    assert req["user_agent"].startswith("signalwire-python/")
    # JSON-RPC envelope with pure-payload params
    body = req["body"]
    assert body["jsonrpc"] == "2.0" and body["method"] == "chat"
    assert body["params"] == {"id": "conv-1", "message": "hello", "role": "user"}


async def test_params_never_carry_identity(stub: StubService) -> None:
    async with AIChatClient(PROJECT, TOKEN, url=stub.url) as client:
        await client.create_conversation(
            "conv-1",
            config_url="http://cfg",
            user_message="hi",
            timeout=600,
            user_metadata={"k": "v"},
            reinit=True,
        )
    params = stub.requests[0]["body"]["params"]
    assert params == {
        "id": "conv-1",
        "config_url": "http://cfg",
        "user_message": "hi",
        "conversation_timeout": 600,
        "user_meta_data": {"k": "v"},
        "reinit": True,
    }
    for forbidden in ("project_id", "token", "space_id"):
        assert forbidden not in params


async def test_all_methods_map_to_jsonrpc(stub: StubService) -> None:
    async with AIChatClient(PROJECT, TOKEN, url=stub.url) as client:
        await client.create_conversation("c", config_url="http://cfg")
        await client.chat("c", "m")
        stub.result = {"status": "ended"}
        await client.end("c")
        stub.result = {"status": "deleted"}
        await client.delete("c")
        stub.result = {"chat_log": [], "call_timeline": []}
        await client.log("c")
        stub.result = {"summary": "s"}
        await client.summarize("c", summary_prompt="sum it")
    methods = [r["body"]["method"] for r in stub.requests]
    assert methods == [
        "create_conversation",
        "chat",
        "end_conversation",
        "delete",
        "chat_log",
        "summarize",
    ]


async def test_response_models(stub: StubService) -> None:
    stub.result = {"status": "created", "initial_message": "welcome"}
    async with AIChatClient(PROJECT, TOKEN, url=stub.url) as client:
        info = await client.create_conversation("c", config_url="http://cfg")
        assert info.status == "created" and info.initial_message == "welcome"

        stub.result = {
            "response": "answer",
            "user_event": {"event_type": "order", "n": 1},
        }
        reply = await client.chat("c", "m")
        assert reply.text == "answer"
        assert reply.user_event == {"event_type": "order", "n": 1}

        stub.result = {
            "chat_log": [{"role": "user", "content": "m"}],
            "call_timeline": [{"t": 1}],
        }
        log = await client.log("c")
        assert log.messages[0]["content"] == "m"
        assert log.call_timeline == [{"t": 1}]


# ── URL resolution ───────────────────────────────────────────────────


def test_url_from_space() -> None:
    client = AIChatClient(PROJECT, TOKEN, space="myspace")
    assert client.url == "https://myspace.signalwire.com/api/ai/chat"


def test_url_arg_wins_over_space_and_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAILS_DEV_MODE", "http://dev:1/")
    client = AIChatClient(PROJECT, TOKEN, space="myspace", url="http://arg:2/")
    assert client.url == "http://arg:2/"


def test_rails_dev_mode_env_overrides_space(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAILS_DEV_MODE", "http://localhost:8080/")
    client = AIChatClient(PROJECT, TOKEN, space="myspace")
    assert client.url == "http://localhost:8080/"


def test_boolean_rails_dev_mode_is_not_a_url(monkeypatch: pytest.MonkeyPatch) -> None:
    # The same env var is the service's persona switch; a bare boolean
    # carries no URL and must not clobber the space-derived target
    monkeypatch.setenv("RAILS_DEV_MODE", "true")
    client = AIChatClient(PROJECT, TOKEN, space="myspace")
    assert client.url == "https://myspace.signalwire.com/api/ai/chat"


def test_env_fallbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SIGNALWIRE_PROJECT_ID", "env-proj")
    monkeypatch.setenv("SIGNALWIRE_API_TOKEN", "env-tok")
    monkeypatch.setenv("SIGNALWIRE_SPACE", "env-space")
    client = AIChatClient()
    assert client._project == "env-proj"
    assert client.url == "https://env-space.signalwire.com/api/ai/chat"


def test_missing_project_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SIGNALWIRE_PROJECT_ID", raising=False)
    with pytest.raises(ValueError, match="project"):
        AIChatClient(space="s")


def test_missing_url_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SIGNALWIRE_SPACE", raising=False)
    monkeypatch.delenv("RAILS_DEV_MODE", raising=False)
    with pytest.raises(ValueError, match="URL"):
        AIChatClient(PROJECT, TOKEN)


# ── Error mapping ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "code,exc",
    [
        (-32001, ConversationNotFoundError),
        (-32005, RateLimitError),
        (-32006, RateLimitError),
        (-32007, ChatInProgressError),
        (-32009, AuthenticationError),
        (-32602, AIChatError),  # unmapped codes fall to the base
    ],
)
async def test_jsonrpc_errors_map_to_exceptions(
    stub: StubService, code: int, exc: type[AIChatError]
) -> None:
    stub.error = (code, "nope")
    stub.http_status = 401 if code == -32009 else 200
    async with AIChatClient(PROJECT, TOKEN, url=stub.url) as client:
        with pytest.raises(exc) as info:
            await client.chat("c", "m")
    assert info.value.code == code


async def test_non_json_response_is_wrapped(
    stub: StubService, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Point at a path the stub doesn't serve JSON-RPC from
    async with AIChatClient(
        PROJECT, TOKEN, url=stub.url.replace("/api/ai/chat", "/missing")
    ) as client:
        with pytest.raises(AIChatError) as info:
            await client.chat("c", "m")
    assert info.value.code == 404
