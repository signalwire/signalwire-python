"""ChatGateway: what a browser holding a publishable key can and cannot do.

The gateway exists so a widget never holds a SignalWire API token. These
tests pin the boundary that makes that safe — what the browser may name, what
the gateway overwrites, and what the caps bound — against an in-process stub
chat service.
"""

import json
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from signalwire.ai_chat import AIChatClient, ChatGateway, GatewayRejection

CONFIG_URL = "https://agent.example.com/swml"
KEY = "pk_test_key"

# What `ChatGateway.prepare` hands back: (service method, params, minted handle).
Prepared = tuple[str, dict[str, Any], str | None]


# ── Stub service ─────────────────────────────────────────────────────


@pytest.fixture
async def service() -> AsyncIterator[Any]:
    """Records what the gateway forwarded upstream."""
    seen: list[dict[str, Any]] = []

    async def handler(request: web.Request) -> web.Response:
        body = await request.json()
        seen.append(body)
        method = body["method"]
        result = {
            "chat": {"response": "hi there"},
            "create_conversation": {
                "status": "created",
                "initial_message": "Hi, I am Sigmond.",
            },
            "chat_log": {
                "chat_log": [
                    {"role": "system", "content": "secret prompt"},
                    {"role": "user", "content": "hi"},
                    {"role": "assistant", "content": "hi there"},
                ]
            },
        }.get(method, {"status": "ended"})
        return web.json_response({"jsonrpc": "2.0", "result": result, "id": body["id"]})

    app = web.Application()
    app.router.add_post("/", handler)
    server = TestServer(app)
    await server.start_server()
    yield type("Svc", (), {"seen": seen, "url": str(server.make_url("/"))})
    await server.close()


@pytest.fixture
async def gateway(service: Any) -> AsyncIterator[ChatGateway]:
    client = AIChatClient(project="p", token="t", url=service.url)
    gw = ChatGateway(
        config_url=CONFIG_URL,
        key=KEY,
        allowed_origins=["https://shop.example.com"],
        client=client,
        secret=b"test-secret",
    )
    yield gw
    await client.close()


def make_gateway(service: Any, **kw: Any) -> ChatGateway:
    """A gateway wired to the stub service. Construction is deliberately
    fail-fast on credentials, so every gateway gets a client."""
    kw.setdefault("secret", b"s")
    return ChatGateway(
        config_url=CONFIG_URL,
        key=KEY,
        client=AIChatClient(project="p", token="t", url=service.url),
        **kw,
    )


# ── Handles ──────────────────────────────────────────────────────────


def test_a_handle_round_trips(gateway: ChatGateway) -> None:
    handle = gateway.mint_handle()
    assert gateway.read_handle(handle).startswith("chat-")


def test_the_browser_cannot_forge_a_conversation(gateway: ChatGateway) -> None:
    """The whole reason the gateway mints: with a publishable key, a guessable
    id would be enough to continue somebody else's chat."""
    forged = gateway.mint_handle()
    tampered = forged.split(".")[0] + ".AAAA"
    with pytest.raises(GatewayRejection) as err:
        gateway.read_handle(tampered)
    assert err.value.status == 403


def test_a_handle_from_another_gateway_is_refused(
    gateway: ChatGateway, service: Any
) -> None:
    other = make_gateway(service, secret=b"different")
    with pytest.raises(GatewayRejection):
        gateway.read_handle(other.mint_handle())


def test_an_expired_handle_is_refused(service: Any) -> None:
    gw = make_gateway(service, handle_ttl=-1)
    with pytest.raises(GatewayRejection) as err:
        gw.read_handle(gw.mint_handle())
    assert err.value.status == 403


def test_garbage_is_refused_without_leaking_why(gateway: ChatGateway) -> None:
    for bad in ("", "not-a-handle", "a.b.c", "!!!.!!!"):
        with pytest.raises(GatewayRejection):
            gateway.read_handle(bad)


# ── Origin ───────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "origin",
    ["http://localhost:3000", "http://127.0.0.1:8080", "http://app.localhost"],
)
def test_localhost_never_needs_listing(gateway: ChatGateway, origin: str) -> None:
    """`pip install` → run → it works, without shipping open by default."""
    # Allowed even though it was never listed...
    gateway.check_origin(origin)
    # ...and the exemption is localhost-specific, not open-by-default. Without
    # this contrast the test would still pass against a gateway that allowed
    # every origin.
    with pytest.raises(GatewayRejection):
        gateway.check_origin("https://evil.example.com")


def test_a_listed_origin_is_allowed(gateway: ChatGateway) -> None:
    gateway.check_origin("https://shop.example.com")
    # A near-miss must not pass: the check is a full-origin match, not a
    # substring/prefix one (which would let evil host a lookalike domain).
    with pytest.raises(GatewayRejection):
        gateway.check_origin("https://shop.example.com.evil.test")


def test_an_unlisted_origin_is_refused(gateway: ChatGateway) -> None:
    """The case this actually defends: a key pasted into someone else's page."""
    with pytest.raises(GatewayRejection) as err:
        gateway.check_origin("https://evil.example.com")
    assert err.value.status == 403


def test_a_missing_origin_is_allowed(gateway: ChatGateway) -> None:
    """Browsers always send one on these POSTs, so absence means a non-browser
    caller. Refusing it would break server-side use and stop no attacker, who
    just omits the header."""
    gateway.check_origin(None)
    # Absent is not the same as unrecognised — a present-but-unlisted origin is
    # still refused, so this is a deliberate exemption rather than a hole.
    with pytest.raises(GatewayRejection):
        gateway.check_origin("https://evil.example.com")


# ── Key ──────────────────────────────────────────────────────────────


def test_the_key_is_required(gateway: ChatGateway) -> None:
    for bad in (None, "", "pk_wrong"):
        with pytest.raises(GatewayRejection) as err:
            gateway.check_key(bad)
        assert err.value.status == 401


# ── What the browser may ask for ─────────────────────────────────────


def prep(
    gw: ChatGateway,
    body: dict[str, Any],
    origin: str | None = "https://shop.example.com",
) -> Prepared:
    return gw.prepare(body, origin=origin, key=KEY)


def test_config_url_is_ours_not_theirs(gateway: ChatGateway) -> None:
    """If the browser could name it, whoever holds a key picks which agent
    runs — and which project pays for it."""
    _, params, _ = prep(gateway, {"message": "hi", "config_url": "https://evil/swml"})
    assert params["config_url"] == CONFIG_URL


def test_the_browser_cannot_name_the_conversation(gateway: ChatGateway) -> None:
    _, params, minted = prep(gateway, {"message": "hi", "id": "someone-elses-chat"})
    assert params["id"] != "someone-elses-chat"
    assert minted is not None
    assert gateway.read_handle(minted) == params["id"]


def test_only_chat_and_end_pass(gateway: ChatGateway) -> None:
    for method in ("chat_log", "summarize", "delete", "create_conversation"):
        with pytest.raises(GatewayRejection) as err:
            prep(gateway, {"method": method, "message": "hi"})
        assert err.value.status == 400


def test_chat_log_is_not_reachable(gateway: ChatGateway) -> None:
    """Keeping it off the wire is what makes a stolen key a bill, not a
    breach."""
    with pytest.raises(GatewayRejection):
        prep(gateway, {"method": "chat_log"})


def test_the_first_chat_mints_and_later_ones_reuse(gateway: ChatGateway) -> None:
    _, first, minted = prep(gateway, {"message": "one"})
    assert minted
    _, second, again = prep(gateway, {"message": "two", "handle": minted})
    assert again is None
    assert second["id"] == first["id"]


def test_end_needs_a_handle(gateway: ChatGateway) -> None:
    with pytest.raises(GatewayRejection):
        prep(gateway, {"method": "end"})


def test_end_maps_to_the_service_method(gateway: ChatGateway) -> None:
    minted = gateway.mint_handle()
    method, params, _ = prep(gateway, {"method": "end", "handle": minted})
    assert method == "end_conversation"
    assert params == {"id": gateway.read_handle(minted)}


def test_an_empty_message_is_refused(gateway: ChatGateway) -> None:
    for bad in (None, "", "   ", 5):
        with pytest.raises(GatewayRejection):
            prep(gateway, {"message": bad})


# ── The caps, which are the real control ─────────────────────────────


def test_minting_is_capped(service: Any) -> None:
    """A leaked key does not hammer one conversation — it mints thousands of
    one-turn ones, and each bills its opening turn."""
    gw = make_gateway(service, max_new_conversations=3)
    for _ in range(3):
        gw.prepare({"message": "hi"}, origin=None, key=KEY)
    with pytest.raises(GatewayRejection) as err:
        gw.prepare({"message": "hi"}, origin=None, key=KEY)
    assert err.value.status == 429


def test_turns_are_capped_per_conversation(service: Any) -> None:
    gw = make_gateway(service, max_turns=2)
    handle = gw.mint_handle()
    for _ in range(2):
        gw.prepare({"message": "hi", "handle": handle}, origin=None, key=KEY)
    with pytest.raises(GatewayRejection) as err:
        gw.prepare({"message": "hi", "handle": handle}, origin=None, key=KEY)
    assert err.value.status == 429


def test_one_conversation_hitting_its_cap_does_not_stop_another(service: Any) -> None:
    gw = make_gateway(service, max_turns=1)
    a, b = gw.mint_handle(), gw.mint_handle()
    gw.prepare({"message": "hi", "handle": a}, origin=None, key=KEY)
    gw.prepare({"message": "hi", "handle": b}, origin=None, key=KEY)
    with pytest.raises(GatewayRejection):
        gw.prepare({"message": "again", "handle": a}, origin=None, key=KEY)


# ── End to end through the router ────────────────────────────────────
#
# Driven through ASGI in this event loop, not starlette's sync TestClient:
# that runs the app on a loop of its own, while the gateway's aiohttp session
# belongs to this one, and the cross-loop call simply hangs.


def asgi(gateway: ChatGateway) -> Any:
    httpx = pytest.importorskip("httpx")
    fastapi = pytest.importorskip("fastapi")
    app = fastapi.FastAPI()
    app.include_router(gateway.router(), prefix="/chat")
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://gw"
    )


HEADERS = {"Authorization": f"Bearer {KEY}", "Origin": "https://shop.example.com"}


async def test_a_full_exchange_over_http(gateway: ChatGateway, service: Any) -> None:
    async with asgi(gateway) as http:
        r = await http.post("/chat/", json={"message": "hello"}, headers=HEADERS)
        assert r.status_code == 200
        handle = r.headers["x-chat-handle"]
        assert json.loads(r.text)["result"]["response"] == "hi there"

        # What actually went upstream: our config_url, our conversation id,
        # and a Basic credential the browser never saw.
        sent = service.seen[-1]["params"]
        assert sent["config_url"] == CONFIG_URL
        assert sent["id"] == gateway.read_handle(handle)
        assert "token" not in json.dumps(sent)

        r2 = await http.post(
            "/chat/", json={"method": "end", "handle": handle}, headers=HEADERS
        )
        assert r2.status_code == 200 and r2.json() == {"status": "ended"}
        assert service.seen[-1]["method"] == "end_conversation"


async def test_a_second_turn_reuses_the_handle(
    gateway: ChatGateway, service: Any
) -> None:
    async with asgi(gateway) as http:
        first = await http.post("/chat/", json={"message": "one"}, headers=HEADERS)
        handle = first.headers["x-chat-handle"]

        second = await http.post(
            "/chat/", json={"message": "two", "handle": handle}, headers=HEADERS
        )
        assert "x-chat-handle" not in second.headers  # nothing new minted
        assert service.seen[-1]["params"]["id"] == gateway.read_handle(handle)


async def test_http_refuses_a_bad_key(gateway: ChatGateway) -> None:
    async with asgi(gateway) as http:
        r = await http.post(
            "/chat/",
            json={"message": "hi"},
            headers={"Authorization": "Bearer nope"},
        )
        assert r.status_code == 401


async def test_http_refuses_an_unlisted_origin(gateway: ChatGateway) -> None:
    async with asgi(gateway) as http:
        r = await http.post(
            "/chat/",
            json={"message": "hi"},
            headers={"Authorization": f"Bearer {KEY}", "Origin": "https://evil.test"},
        )
        assert r.status_code == 403
        assert "access-control-allow-origin" not in r.headers


async def test_preflight_answers_a_listed_origin(gateway: ChatGateway) -> None:
    async with asgi(gateway) as http:
        r = await http.options("/chat/", headers={"Origin": "https://shop.example.com"})
        assert r.status_code == 204
        assert r.headers["access-control-allow-origin"] == "https://shop.example.com"
        assert "X-Chat-Handle" in r.headers["access-control-expose-headers"]


# ── Streaming passthrough ────────────────────────────────────────────


@pytest.fixture
async def slow_service() -> AsyncIterator[Any]:
    """Pads the response the way the real service does on a slow turn.

    heartbeat.py trickles whitespace so intermediaries do not sever a
    connection mid-turn. It is valid JSON leader, so a relay can forward it
    untouched — but only if the relay forwards bytes instead of decoding.
    """
    import asyncio

    async def handler(request: web.Request) -> web.StreamResponse:
        body = await request.json()
        resp = web.StreamResponse(
            status=200, headers={"Content-Type": "application/json"}
        )
        await resp.prepare(request)
        for _ in range(3):
            await resp.write(b" " * 16)
            await asyncio.sleep(0.01)
        await resp.write(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "result": {"response": "slow reply"},
                    "id": body["id"],
                }
            ).encode()
        )
        await resp.write_eof()
        return resp

    app = web.Application()
    app.router.add_post("/", handler)
    server = TestServer(app)
    await server.start_server()
    yield type("Svc", (), {"url": str(server.make_url("/"))})
    await server.close()


@pytest.fixture
async def slow_gateway(slow_service: Any) -> AsyncIterator[ChatGateway]:
    client = AIChatClient(project="p", token="t", url=slow_service.url)
    yield ChatGateway(config_url=CONFIG_URL, key=KEY, client=client, secret=b"s")
    await client.close()


async def test_the_keepalive_padding_is_relayed_not_swallowed(
    slow_gateway: ChatGateway,
) -> None:
    """The regression guard: a gateway that awaits the whole body would strip
    this padding and recreate, inside the customer's own stack, the very proxy
    timeout the service pads to survive.
    """
    async with asgi(slow_gateway) as http:
        r = await http.post(
            "/chat/",
            json={"message": "hi"},
            headers={"Authorization": f"Bearer {KEY}"},
        )
        assert r.status_code == 200
        assert r.text.startswith(" "), "padding was consumed instead of forwarded"
        assert json.loads(r.text)["result"]["response"] == "slow reply"


async def test_the_relay_streams_rather_than_collects(
    slow_gateway: ChatGateway, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Chunks leave the upstream socket one at a time, and the route hands
    back a streaming response rather than a completed body.

    Asserted at these two seams rather than end-to-end because httpx's
    ASGITransport drains the app before returning, so no in-process client can
    observe incremental delivery. What matters is that nothing between the
    socket and the response awaits the whole body.
    """
    from fastapi.responses import StreamingResponse

    client = slow_gateway._client
    chunks = []
    async with client.raw_post("chat", {"id": "c", "message": "hi"}) as resp:
        async for chunk in resp.content.iter_any():
            chunks.append(chunk)
    assert len(chunks) > 1, f"upstream body arrived in one piece: {chunks!r}"
    assert chunks[0].strip() == b"", "first chunk should be keepalive padding"

    # And the route returns a stream, not a materialised body.
    route = next(
        r for r in slow_gateway.router().routes if "POST" in getattr(r, "methods", ())
    )
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/",
        "headers": [],
        "query_string": b"",
    }
    from starlette.requests import Request

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": json.dumps({"message": "hi"}).encode()}

    request = Request(scope, receive)
    # Reaching past the public surface on purpose: this asserts the route's
    # internal contract (streams rather than materialises), which no public
    # client can observe — see the docstring.
    request._headers = {"authorization": f"Bearer {KEY}"}  # type: ignore[assignment]
    response = await route.endpoint(request)  # type: ignore[attr-defined]
    assert isinstance(response, StreamingResponse)


# ── start / log ──────────────────────────────────────────────────────


def test_start_mints_and_opens_with_no_message(gateway: ChatGateway) -> None:
    """A widget wants the agent to speak first, before anyone has typed."""
    method, params, minted = prep(gateway, {"method": "start"})
    assert method == "create_conversation"
    assert minted is not None
    assert params == {"id": gateway.read_handle(minted), "config_url": CONFIG_URL}


def test_log_is_scoped_to_the_handle_not_the_body(gateway: ChatGateway) -> None:
    """The conversation comes from inside the signed handle, so a caller
    cannot read somebody else's by naming it."""
    handle = gateway.mint_handle()
    method, params, _ = prep(
        gateway, {"method": "log", "handle": handle, "id": "someone-elses-chat"}
    )
    assert method == "chat_log"
    assert params == {"id": gateway.read_handle(handle)}


def test_log_needs_a_handle(gateway: ChatGateway) -> None:
    with pytest.raises(GatewayRejection):
        prep(gateway, {"method": "log"})


def test_the_transcript_hides_everything_but_the_dialogue(
    gateway: ChatGateway,
) -> None:
    """chat_log returns the substituted SYSTEM PROMPT and the tool traffic.
    Relaying that would publish the developer's prompt to anyone with a
    handle."""
    raw: list[dict[str, Any]] = [
        {"role": "system", "content": "You are Sigmond. Secret instructions."},
        {"role": "user", "content": "hi", "timestamp": 123},
        {"role": "assistant", "content": None, "tool_calls": [{"id": "call_1"}]},
        {"role": "tool", "content": '{"internal": "result"}'},
        {"role": "assistant", "content": "Hello!", "timestamp": 124},
        {"role": "assistant", "content": "   "},
    ]
    out = gateway.visible_messages(raw)

    # Role, text, and when it was said — the timestamp rides along because a
    # client redrawing a restored transcript would otherwise have to date it
    # "now", making an hour-old conversation look like it just happened. It is
    # the turn's own time, already visible to whoever holds the handle.
    assert out == [
        {"role": "user", "content": "hi", "timestamp": 123 / 1_000_000},
        {"role": "assistant", "content": "Hello!", "timestamp": 124 / 1_000_000},
    ]
    blob = json.dumps(out)
    assert "Secret instructions" not in blob
    assert "tool_calls" not in blob and "internal" not in blob


def test_the_transcript_reports_seconds_not_microseconds(
    gateway: ChatGateway,
) -> None:
    """A 1000000x unit slip here is SILENT: a browser bootstrapping its idle
    clock from a microsecond value reads the conversation as fresh forever and
    never warns that the next message starts a new one."""
    ts_us = 1_786_258_737_756_596  # microseconds, as the service stores
    out = gateway.visible_messages(
        [{"role": "user", "content": "hi", "timestamp": ts_us}]
    )
    assert out[0]["timestamp"] == pytest.approx(1_786_258_737.756596)

    assert gateway.last_activity(
        [{"role": "user", "content": "hi", "timestamp": ts_us}]
    ) == pytest.approx(1_786_258_737.756596)


def test_last_activity_takes_the_newest_message_of_any_role(
    gateway: ChatGateway,
) -> None:
    """The service's idle clock runs off updated_at, which ANY write moves.
    Counting only the visible roles would report an older time than the
    service is measuring and warn early for no reason."""
    assert (
        gateway.last_activity(
            [
                {"role": "user", "content": "first", "timestamp": 1_000_000},
                {"role": "assistant", "content": "second", "timestamp": 3_000_000},
                {"role": "tool", "content": "internal", "timestamp": 5_000_000},
            ]
        )
        == 5.0
    )


def test_last_activity_is_none_when_nothing_is_dated(gateway: ChatGateway) -> None:
    """None, not 0 — a zero would read as 1970 and expire every conversation
    the instant it was restored."""
    assert gateway.last_activity([{"role": "user", "content": "hi"}]) is None
    assert gateway.last_activity([]) is None
    assert gateway.last_activity(None) is None
    undated: list[Any] = [{"role": "user", "timestamp": "not a number"}]
    assert gateway.last_activity(undated) is None


def test_effective_timeout_is_always_a_number(gateway: ChatGateway) -> None:
    """A browser cannot warn about a deadline it was told nothing about, so an
    unset timeout still reports the service default rather than null."""
    assert gateway.effective_timeout == 3600


def test_the_transcript_survives_junk(gateway: ChatGateway) -> None:
    # Deliberately malformed input: the service is upstream of us, so a
    # transcript that is not a list of dicts must degrade to empty rather than
    # raise inside somebody's page. `list[Any]` because that is exactly the
    # contract being probed.
    junk: list[Any] = ["not a dict", {"role": "user"}]
    assert gateway.visible_messages([]) == []
    assert gateway.visible_messages(None) == []
    assert gateway.visible_messages(junk) == []


async def test_start_then_reload_replays_the_same_conversation(
    gateway: ChatGateway, service: Any
) -> None:
    """The reload path end to end: start, keep the handle, read it back."""
    async with asgi(gateway) as http:
        started = await http.post("/chat/", json={"method": "start"}, headers=HEADERS)
        assert started.status_code == 200
        handle = started.headers["x-chat-handle"]
        assert started.json()["greeting"]

        replay = await http.post(
            "/chat/", json={"method": "log", "handle": handle}, headers=HEADERS
        )
        assert replay.status_code == 200
        assert "messages" in replay.json()
        # and it asked the service for the conversation the handle names
        assert service.seen[-1]["params"]["id"] == gateway.read_handle(handle)


async def test_start_forwards_the_configured_timeout_upstream(service):
    """prepare() puts conversation_timeout in the start params, but the HTTP
    dispatch used to rebuild the create_conversation call and drop it — the
    browser was told 900 while the service kept its 3600 default. The number
    the page schedules its idle warning around must be the number the service
    actually enforces."""
    gw = make_gateway(
        service,
        allowed_origins=["https://shop.example.com"],
        conversation_timeout=900,
    )
    try:
        async with asgi(gw) as http:
            started = await http.post(
                "/chat/", json={"method": "start"}, headers=HEADERS
            )
            assert started.status_code == 200
            assert started.json()["timeout"] == 900
            sent = service.seen[-1]
            assert sent["method"] == "create_conversation"
            assert sent["params"]["conversation_timeout"] == 900

            # The chat path auto-creates too, and takes the same timeout.
            handle = started.headers["x-chat-handle"]
            chatted = await http.post(
                "/chat/",
                json={"message": "hi", "handle": handle},
                headers=HEADERS,
            )
            assert chatted.status_code == 200
            sent = service.seen[-1]
            assert sent["method"] == "chat"
            assert sent["params"]["conversation_timeout"] == 900
    finally:
        await gw._client.close()
