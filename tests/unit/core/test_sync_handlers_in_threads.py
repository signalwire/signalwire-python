"""
Synchronous user code runs in a worker thread, not on the event loop.

The web endpoints are async and share one event loop. A synchronous tool
handler, per-request configuration callback, routing callback, on_summary or
MCP tool called directly on that loop held up every other request until it
returned. That code now runs in AnyIO's thread pool. An ``async def`` handler
still runs on the loop, and SWML_SYNC_HANDLERS_INLINE restores the old
behavior.

Because the per-request copy of the agent is configured and rendered in a
worker thread, copies for different calls are built at the same time, so each
one must be independent of the agent it was copied from.
"""

import asyncio
import contextlib
import contextvars
import json
import threading
from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import urlparse

import anyio
import anyio.to_thread
import httpx
import pytest
from fastapi import FastAPI

from signalwire import AgentBase, SWMLService
from signalwire.core._sync_handlers import run_sync_handler
from signalwire.core.function_result import FunctionResult

AUTH = ("user", "pass")
WAIT = 5.0  # seconds a blocked callback waits before giving up


class Gate:
    """Something user code blocks on until the test lets it go."""

    def __init__(self) -> None:
        self.entered = threading.Event()
        self.release = threading.Event()
        self.thread: int | None = None

    def block(self) -> bool:
        self.thread = threading.get_ident()
        self.entered.set()
        return self.release.wait(WAIT)

    async def wait_entered(self) -> None:
        # Wait in the default executor, so the event loop stays free.
        assert await asyncio.to_thread(self.entered.wait, WAIT)


@contextlib.asynccontextmanager
async def _thread_pool_full() -> AsyncIterator[None]:
    """Fill AnyIO's thread pool with one blocked worker, for the duration."""
    limiter = anyio.to_thread.current_default_thread_limiter()
    tokens = limiter.total_tokens
    limiter.total_tokens = 1
    entered = threading.Event()
    release = threading.Event()

    def block() -> None:
        entered.set()
        release.wait(60)  # longer than any request below may take

    occupied = asyncio.create_task(anyio.to_thread.run_sync(block))
    try:
        assert await asyncio.to_thread(entered.wait, WAIT)
        yield
        assert not occupied.done(), "the pool stopped being full"
    finally:
        release.set()
        await occupied
        limiter.total_tokens = tokens


def _agent() -> AgentBase:
    return AgentBase(name="threads", route="/agent", basic_auth=AUTH, suppress_logs=True)


def _client(agent: AgentBase) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent.get_app()),
        base_url="http://agent.test",
        auth=AUTH,
    )


def _swaig_body(function: str) -> dict[str, Any]:
    return {"function": function, "argument": {"parsed": [{}]}, "call_id": "call-1"}


def _ai(swml: str) -> dict[str, Any]:
    main = json.loads(swml)["sections"]["main"]
    ai: dict[str, Any] = next(verb["ai"] for verb in main if "ai" in verb)
    return ai


class TestToolHandlers:
    async def test_a_blocked_handler_doesnt_hold_up_other_requests(self) -> None:
        gate = Gate()
        agent = _agent()
        agent.define_tool(
            name="slow", description="slow", parameters={}, secure=False,
            handler=lambda args, raw_data: FunctionResult(f"released={gate.block()}"),
        )
        async with _client(agent) as client:
            call = asyncio.create_task(client.post("/agent/swaig", json=_swaig_body("slow")))
            try:
                await gate.wait_entered()
                # The handler is still blocked, and the SWML still comes back
                swml = await asyncio.wait_for(client.get("/agent"), timeout=WAIT)
                assert swml.status_code == 200
                assert "prompt" in _ai(swml.text)
                assert not call.done()
            finally:
                gate.release.set()
                response = await call
        assert response.json() == {"response": "released=True"}
        assert gate.thread != threading.get_ident()

    async def test_an_async_handler_still_runs_on_the_event_loop(self) -> None:
        threads: list[int] = []

        async def fast(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
            threads.append(threading.get_ident())
            await asyncio.sleep(0)
            return FunctionResult("done")

        agent = _agent()
        agent.define_tool(name="fast", description="fast", parameters={}, handler=fast, secure=False)
        async with _client(agent) as client:
            response = await client.post("/agent/swaig", json=_swaig_body("fast"))
        assert response.json() == {"response": "done"}
        assert threads == [threading.get_ident()]

    async def test_async_handlers_dont_wait_for_a_worker_thread(self) -> None:
        # With the thread pool full, async handlers still run: a plain one, a
        # typed one and an object with an async __call__, because they need
        # no thread.
        agent = _agent()

        async def plain(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
            return FunctionResult("plain")

        class Callable:
            async def __call__(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
                return FunctionResult("callable")

        agent.define_tool(name="plain", description="plain", parameters={}, handler=plain, secure=False)
        agent.define_tool(name="callable", description="c", parameters={}, handler=Callable(), secure=False)

        @agent.tool(name="typed", description="typed", secure=False)
        async def typed(city: str) -> FunctionResult:
            """Look up a city.

            Args:
                city: City name
            """
            return FunctionResult(f"typed {city}")

        typed_body = {"function": "typed", "argument": {"parsed": [{"city": "Paris"}]}, "call_id": "call-1"}
        async with _thread_pool_full(), _client(agent) as client:
            responses = [
                await asyncio.wait_for(client.post("/agent/swaig", json=body), timeout=2)
                for body in (_swaig_body("plain"), _swaig_body("callable"), typed_body)
            ]
        assert [response.json() for response in responses] == [
            {"response": "plain"}, {"response": "callable"}, {"response": "typed Paris"}]

    async def test_a_cancelled_call_lets_the_handler_finish_its_shielded_cleanup(self) -> None:
        # The handler runs inside the request's cancel scope, as a direct
        # await does, so cancellation respects a shield
        started = asyncio.Event()
        cleaned: list[str] = []

        async def slow(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
            started.set()
            try:
                await anyio.sleep(WAIT)
            finally:
                with anyio.CancelScope(shield=True):
                    await anyio.sleep(0.2)
                    cleaned.append("done")
            return FunctionResult("finished")

        agent = _agent()
        agent.set_dynamic_config_callback(lambda query, body, headers, agent: None)
        agent.define_tool(name="slow", description="slow", parameters={}, handler=slow, secure=False)
        scope = anyio.CancelScope()

        async with _client(agent) as client:

            async def call() -> None:
                with scope:
                    await client.post("/agent/swaig", json=_swaig_body("slow"))

            async with anyio.create_task_group() as group:
                group.start_soon(call)
                await asyncio.wait_for(started.wait(), timeout=WAIT)
                scope.cancel()
        assert scope.cancelled_caught
        assert cleaned == ["done"]

    async def test_the_inline_setting_runs_the_handler_on_the_event_loop(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SWML_SYNC_HANDLERS_INLINE", "true")
        threads: list[int] = []

        def handler(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
            threads.append(threading.get_ident())
            return FunctionResult("done")

        agent = _agent()
        agent.define_tool(name="inline", description="inline", parameters={}, handler=handler, secure=False)
        async with _client(agent) as client:
            response = await client.post("/agent/swaig", json=_swaig_body("inline"))
        assert response.json() == {"response": "done"}
        assert threads == [threading.get_ident()]


class TestPerRequestConfiguration:
    async def test_a_blocked_callback_doesnt_hold_up_other_calls(self) -> None:
        gate = Gate()

        def configure(query: dict[str, Any], body: dict[str, Any], headers: dict[str, Any],
                      agent: AgentBase) -> None:
            if query.get("tenant") == "slow":
                gate.block()
            agent.set_global_data({"tenant": query.get("tenant")})

        agent = _agent()
        agent.set_dynamic_config_callback(configure)
        async with _client(agent) as client:
            slow = asyncio.create_task(client.get("/agent", params={"tenant": "slow"}))
            try:
                await gate.wait_entered()
                fast = await asyncio.wait_for(
                    client.get("/agent", params={"tenant": "fast"}), timeout=WAIT)
                assert _ai(fast.text)["global_data"] == {"tenant": "fast"}
                assert not slow.done()
            finally:
                gate.release.set()
                slow_response = await slow
            assert _ai(slow_response.text)["global_data"] == {"tenant": "slow"}
        assert gate.thread != threading.get_ident()

    async def test_overlapping_copies_keep_their_own_configuration(self) -> None:
        # Both callbacks are running at once before either configures its copy
        both_configuring = threading.Barrier(2, timeout=WAIT)
        overlapped: list[str] = []

        def configure(query: dict[str, Any], body: dict[str, Any], headers: dict[str, Any],
                      agent: AgentBase) -> None:
            tenant = query["tenant"]
            both_configuring.wait()  # a timeout raises, and the SDK only logs it
            overlapped.append(tenant)
            agent.set_global_data({"tenant": tenant})
            agent.add_mcp_server(f"https://{tenant}.example.com/mcp")
            agent.prompt_add_section("Tenant", body=f"You answer for {tenant}.")

        agent = _agent()
        agent.set_dynamic_config_callback(configure)
        async with _client(agent) as client:
            first, second = await asyncio.gather(
                client.get("/agent", params={"tenant": "first"}),
                client.get("/agent", params={"tenant": "second"}),
            )
        for response, tenant in ((first, "first"), (second, "second")):
            ai = _ai(response.text)
            assert ai["global_data"] == {"tenant": tenant}
            assert [server["url"] for server in ai["SWAIG"]["mcp_servers"]] == [f"https://{tenant}.example.com/mcp"]
            assert f"You answer for {tenant}." in json.dumps(ai["prompt"])
        assert sorted(overlapped) == ["first", "second"]
        # Nothing the callbacks did reached the agent itself
        assert agent._mcp_servers == []
        assert agent._global_data == {}

    async def test_a_context_variable_the_callback_sets_reaches_the_tool(self) -> None:
        tenant: contextvars.ContextVar[str] = contextvars.ContextVar("tenant", default="MISSING")

        def configure(query: dict[str, Any], body: dict[str, Any], headers: dict[str, Any],
                      agent: AgentBase) -> None:
            tenant.set(query["tenant"])

        def sync_tool(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
            return FunctionResult(f"sync {tenant.get()}")

        async def async_tool(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
            await asyncio.sleep(0)
            return FunctionResult(f"async {tenant.get()}")

        agent = _agent()
        agent.set_dynamic_config_callback(configure)
        agent.define_tool(name="sync_tool", description="s", parameters={}, handler=sync_tool, secure=False)
        agent.define_tool(name="async_tool", description="a", parameters={}, handler=async_tool, secure=False)
        async with _client(agent) as client:
            sync_response = await client.post(
                "/agent/swaig", params={"tenant": "acme"}, json=_swaig_body("sync_tool"))
            async_response = await client.post(
                "/agent/swaig", params={"tenant": "acme"}, json=_swaig_body("async_tool"))
        assert sync_response.json() == {"response": "sync acme"}
        assert async_response.json() == {"response": "async acme"}

    def test_a_verb_added_on_a_copy_stays_on_the_copy(self) -> None:
        agent = _agent()
        copy = agent._create_ephemeral_copy()
        copy.play(url="say:hello")
        assert agent.get_document()["sections"]["main"] == []
        assert copy.get_document()["sections"]["main"] == [{"play": {"url": "say:hello"}}]

    def test_a_sip_username_registered_on_a_copy_stays_on_the_copy(self) -> None:
        agent = _agent()
        agent.register_sip_username("front-desk")
        copy = agent._create_ephemeral_copy()
        copy.register_sip_username("tenant-line")
        assert agent._sip_usernames == {"front-desk"}
        assert copy._sip_usernames == {"front-desk", "tenant-line"}


class TestOtherCallbacks:
    async def test_on_summary_runs_in_a_worker_thread(self) -> None:
        threads: list[int] = []
        agent = _agent()
        agent.set_post_prompt("Summarize the call.")

        def on_summary(summary: Any, raw_data: Any = None) -> None:
            threads.append(threading.get_ident())

        agent.on_summary = on_summary  # type: ignore[method-assign]  # capture the call
        async with _client(agent) as client:
            swml = await client.get("/agent", params={"call_id": "call-1"})
            query = urlparse(_ai(swml.text)["post_prompt_url"]).query
            response = await client.post(
                f"/agent/post_prompt?{query}",
                json={"call_id": "call-1", "summary": "Booked a table."},
            )
        assert response.json() == {"success": True}
        assert len(threads) == 1
        assert threads[0] != threading.get_ident()

    async def test_a_routing_callback_runs_in_a_worker_thread(self) -> None:
        threads: list[int] = []

        def route(body: dict[str, Any], headers: dict[str, Any]) -> str | None:
            threads.append(threading.get_ident())
            return "/elsewhere" if body.get("transfer") else None

        agent = _agent()
        agent.register_routing_callback(route, path="/sip")
        async with _client(agent) as client:
            redirected = await client.post("/agent/sip", json={"transfer": True})
            rendered = await client.post("/agent/sip", json={"call": {"call_id": "call-1"}})
        assert redirected.status_code == 307
        assert redirected.headers["location"] == "/elsewhere"
        assert "prompt" in _ai(rendered.text)
        assert len(threads) == 2
        assert threading.get_ident() not in threads

    async def test_a_swml_service_routing_callback_runs_in_a_worker_thread(self) -> None:
        threads: list[int] = []

        def route(body: dict[str, Any], headers: dict[str, Any]) -> str | None:
            threads.append(threading.get_ident())
            return "/elsewhere" if body.get("transfer") else None

        service = SWMLService(name="plain", route="/svc", basic_auth=AUTH)
        service.add_verb("answer", {})
        service.register_routing_callback(route, path="/sip")
        app = FastAPI()
        app.include_router(service.as_router(), prefix="/svc")
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://svc.test", auth=AUTH) as client:
            redirected = await client.post("/svc/sip", json={"transfer": True})
            rendered = await client.post("/svc/sip", json={"call": {"call_id": "call-1"}})
        assert redirected.status_code == 307
        assert redirected.headers["location"] == "/elsewhere"
        assert json.loads(rendered.text)["sections"]["main"] == [{"answer": {}}]
        assert len(threads) == 2
        assert threading.get_ident() not in threads

    async def test_a_context_variable_the_routing_callback_sets_reaches_on_swml_request(self) -> None:
        tenant: contextvars.ContextVar[str] = contextvars.ContextVar("tenant", default="MISSING")
        seen: list[str] = []

        class Agent(AgentBase):
            def on_swml_request(self, request_data: Any = None, callback_path: Any = None,
                                request: Any = None) -> Any:
                seen.append(tenant.get())
                return super().on_swml_request(request_data, callback_path, request)

        def route(body: dict[str, Any], headers: dict[str, Any]) -> str | None:
            tenant.set("acme")
            return None

        agent = Agent(name="threads", route="/agent", basic_auth=AUTH, suppress_logs=True)
        agent.register_routing_callback(route, path="/sip")
        async with _client(agent) as client:
            response = await client.post("/agent/sip", json={"call": {"call_id": "call-1"}})
        assert response.status_code == 200
        assert seen == ["acme"]

    async def test_a_swml_service_keeps_one_context_and_needs_no_thread_to_render(self) -> None:
        tenant: contextvars.ContextVar[str] = contextvars.ContextVar("tenant", default="MISSING")
        seen: list[str] = []

        class Service(SWMLService):
            def on_request(self, request_data: Any = None, callback_path: Any = None) -> Any:
                seen.append(tenant.get())
                return None

        def route(body: dict[str, Any], headers: dict[str, Any]) -> str | None:
            tenant.set("acme")
            return None

        service = Service(name="plain", route="/svc", basic_auth=AUTH)
        service.add_verb("answer", {})
        service.register_routing_callback(route, path="/sip")
        app = FastAPI()
        app.include_router(service.as_router(), prefix="/svc")
        transport = httpx.ASGITransport(app=app)
        start = contextvars.copy_context()

        def own_task(request: Any) -> Any:
            # A server runs each request in its own task, from its own context
            return start.run(asyncio.ensure_future, request)

        async with httpx.AsyncClient(transport=transport, base_url="http://svc.test", auth=AUTH) as client:
            routed = await own_task(client.post("/svc/sip", json={"call": {"call_id": "call-1"}}))
            # No routing callback applies to a GET, so it needs no thread
            async with _thread_pool_full():
                static = await asyncio.wait_for(own_task(client.get("/svc/")), timeout=2)
        assert routed.status_code == 200
        assert seen == ["acme", "MISSING"]
        assert json.loads(static.text)["sections"]["main"] == [{"answer": {}}]

    async def test_an_mcp_tool_call_runs_in_a_worker_thread(self) -> None:
        threads: list[int] = []

        def lookup(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
            threads.append(threading.get_ident())
            return FunctionResult("found it")

        agent = _agent()
        agent.enable_mcp_server()
        agent.define_tool(name="lookup", description="lookup", parameters={}, handler=lookup)
        async with _client(agent) as client:
            response = await client.post("/agent/mcp", json={
                "jsonrpc": "2.0", "id": 1, "method": "tools/call",
                "params": {"name": "lookup", "arguments": {}},
            })
        assert "found it" in json.dumps(response.json()["result"])
        assert len(threads) == 1
        assert threads[0] != threading.get_ident()


async def test_the_worker_thread_sees_the_callers_context_variables() -> None:
    tenant: contextvars.ContextVar[str] = contextvars.ContextVar("tenant")
    tenant.set("acme")
    seen = await run_sync_handler(lambda: (tenant.get(), threading.get_ident()))
    assert seen[0] == "acme"
    assert seen[1] != threading.get_ident()


async def test_what_the_worker_thread_sets_reaches_the_caller() -> None:
    # As it would had the code run inline, even when it then raises
    region: contextvars.ContextVar[str] = contextvars.ContextVar("region", default="unset")
    unchanged: contextvars.ContextVar[str] = contextvars.ContextVar("unchanged")
    unchanged.set("kept")

    def configure() -> None:
        region.set("us-east")

    def configure_then_fail() -> None:
        region.set("eu-west")
        raise RuntimeError("lookup failed")

    await run_sync_handler(configure)
    assert region.get() == "us-east"
    with pytest.raises(RuntimeError, match="lookup failed"):
        await run_sync_handler(configure_then_fail)
    assert region.get() == "eu-west"
    assert unchanged.get() == "kept"


async def test_a_cancelled_caller_doesnt_get_the_unfinished_workers_changes() -> None:
    region: contextvars.ContextVar[str] = contextvars.ContextVar("region", default="unset")
    gate = Gate()
    seen: list[str] = []

    def configure() -> None:
        region.set("us-east")
        gate.block()

    async def caller() -> None:
        try:
            await run_sync_handler(configure)
        except asyncio.CancelledError:
            seen.append(region.get())
            raise

    task = asyncio.create_task(caller())
    try:
        await gate.wait_entered()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    finally:
        gate.release.set()
    assert seen == ["unset"]


async def test_the_thread_pools_own_settings_stay_in_the_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # AnyIO marks its worker's context (sniffio's library variable) before
    # running the function; only what the function itself sets comes back
    pool_marker: contextvars.ContextVar[str] = contextvars.ContextVar("pool", default="loop")
    region: contextvars.ContextVar[str] = contextvars.ContextVar("region", default="unset")

    async def pool(func: Any) -> Any:
        def worker() -> Any:
            pool_marker.set("worker")
            return func()

        return await asyncio.to_thread(contextvars.copy_context().run, worker)

    monkeypatch.setattr("signalwire.core._sync_handlers.run_in_threadpool", pool)

    def configure() -> str:
        region.set("us-east")
        return pool_marker.get()

    assert await run_sync_handler(configure) == "worker"
    assert region.get() == "us-east"
    assert pool_marker.get() == "loop"
