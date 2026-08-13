"""Agent lifecycle surfaces: signing secret, per-call config, call-end, mounting.

Four defects that all failed the same way -- silently, with a symptom pointing
somewhere other than the cause. Each test here reproduces the original failure
so a regression is caught rather than rediscovered in production.
"""

from typing import Any

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from signalwire import AgentBase


def agent(**kwargs: Any) -> AgentBase:
    return AgentBase(name="t", route="/myagent", schema_validation=False, **kwargs)


# ── swaig_secret ─────────────────────────────────────────────────────


class TestSwaigSecret:
    """SessionManager generated a random secret per process, so tokens issued
    before a restart stopped verifying after it -- and the caller saw "the
    security token for this function is invalid or expired", which reads like
    the tool failed rather than like it was never allowed to run.
    """

    def test_without_a_secret_two_instances_cannot_verify_each_other(self) -> None:
        a, b = agent(), agent()
        token = a._session_manager.create_tool_token("search", "call-1")
        assert not b._session_manager.validate_tool_token("search", token, "call-1")

    def test_a_shared_secret_survives_the_restart(self) -> None:
        a = agent(swaig_secret="shared")  # noqa: S106 - test fixture
        b = agent(swaig_secret="shared")  # noqa: S106 - test fixture
        token = a._session_manager.create_tool_token("search", "call-1")
        assert b._session_manager.validate_tool_token("search", token, "call-1")

    def test_env_var_is_honoured(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SIGNALWIRE_SWAIG_SECRET", "from-env")
        a, b = agent(), agent()
        token = a._session_manager.create_tool_token("search", "call-1")
        assert b._session_manager.validate_tool_token("search", token, "call-1")

    def test_explicit_argument_beats_the_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SIGNALWIRE_SWAIG_SECRET", "from-env")
        assert (
            agent(swaig_secret="explicit")._swaig_secret  # noqa: S106 - test fixture
            == "explicit"  # noqa: S105 - test fixture
        )


# ── per-call config ──────────────────────────────────────────────────


class TestPerCallConfig:
    """`set_dynamic_config_callback` holds ONE callback. A second call
    discarded the first with no error: SWML still rendered, every tool still
    worked, and whatever the dropped callback configured was simply absent.
    """

    def test_added_callbacks_all_run_in_registration_order(self) -> None:
        seen: list[str] = []
        a = agent()
        a.add_per_call_config(lambda q, b, h, ag: seen.append("first"))
        a.add_per_call_config(lambda q, b, h, ag: seen.append("second"))
        configure = a._dynamic_config_callback
        assert configure is not None
        configure({}, {}, {}, a)
        assert seen == ["first", "second"]

    def test_set_still_replaces(self) -> None:
        """Documented behaviour of the original method is preserved."""
        seen: list[str] = []
        a = agent()
        a.set_dynamic_config_callback(lambda q, b, h, ag: seen.append("one"))
        a.set_dynamic_config_callback(lambda q, b, h, ag: seen.append("two"))
        configure = a._dynamic_config_callback
        assert configure is not None
        configure({}, {}, {}, a)
        assert seen == ["two"]

    def test_add_composes_with_a_previously_set_callback(self) -> None:
        seen: list[str] = []
        a = agent()
        a.set_dynamic_config_callback(lambda q, b, h, ag: seen.append("set"))
        a.add_per_call_config(lambda q, b, h, ag: seen.append("added"))
        configure = a._dynamic_config_callback
        assert configure is not None
        configure({}, {}, {}, a)
        assert seen == ["set", "added"]

    def test_none_clears_and_reads_falsy(self) -> None:
        """Construction does `self._dynamic_config_callback = None`, and call
        sites branch on truthiness."""
        a = agent()
        a.add_per_call_config(lambda q, b, h, ag: None)
        a._dynamic_config_callback = None
        assert a._dynamic_config_callback is None
        assert not a._dynamic_config_callback

    def test_a_fresh_agent_has_no_callback(self) -> None:
        assert agent()._dynamic_config_callback is None


# ── on_call_end ──────────────────────────────────────────────────────


class TestOnCallEnd:
    """`call_log` is a CONDITIONAL field on a SWAIG request. Without
    `swaig_post_conversation` the hangup hook fires, returns 200, and carries
    no transcript -- indistinguishable from the hook never running.
    """

    @staticmethod
    def _fire(a: AgentBase, payload: dict[str, Any]) -> None:
        hook = a._tool_registry._swaig_functions["hangup_hook"]
        handler = getattr(hook, "handler", None)
        assert handler is not None
        handler({}, payload)

    def test_registering_enables_the_payload_parameter(self) -> None:
        a = agent()
        assert a._params.get("swaig_post_conversation") is None
        a.on_call_end(lambda call_log, raw: None)
        assert a._params["swaig_post_conversation"] is True

    def test_registering_defines_the_reserved_hook(self) -> None:
        a = agent()
        a.on_call_end(lambda call_log, raw: None)
        assert "hangup_hook" in a._tool_registry._swaig_functions

    def test_handlers_receive_the_log_and_run_in_order(self) -> None:
        seen: list[Any] = []
        a = agent()
        a.on_call_end(lambda call_log, raw: seen.append(("one", len(call_log))))
        a.on_call_end(lambda call_log, raw: seen.append(("two", raw.get("call_id"))))
        self._fire(a, {"call_log": [{"role": "user"}], "call_id": "c-1"})
        assert seen == [("one", 1), ("two", "c-1")]

    def test_raw_call_log_is_accepted_too(self) -> None:
        seen: list[int] = []
        a = agent()
        a.on_call_end(lambda call_log, raw: seen.append(len(call_log)))
        self._fire(a, {"raw_call_log": [{"role": "user"}, {"role": "assistant"}]})
        assert seen == [2]

    def test_one_failing_handler_does_not_stop_the_others(self) -> None:
        """A failing teardown handler must not turn into a failed hangup."""
        seen: list[str] = []

        def boom(call_log: Any, raw: Any) -> None:
            raise RuntimeError("boom")

        a = agent()
        a.on_call_end(boom)
        a.on_call_end(lambda call_log, raw: seen.append("still ran"))
        self._fire(a, {"call_log": []})
        assert seen == ["still ran"]

    def test_an_explicit_false_is_not_overridden(self) -> None:
        a = agent()
        a.set_params({"swaig_post_conversation": False})
        a.on_call_end(lambda call_log, raw: None)
        assert a._params["swaig_post_conversation"] is False

    def test_usable_as_a_decorator(self) -> None:
        a = agent()

        @a.on_call_end
        def handler(call_log: Any, raw: Any) -> None:
            return None

        assert callable(handler)
        assert "hangup_hook" in a._tool_registry._swaig_functions


# ── mount ────────────────────────────────────────────────────────────


class TestMount:
    """`get_app()` registers a `/{full_path:path}` catch-all and FastAPI matches
    in registration order, so anything mounted afterwards was unreachable. And
    `get_app()`'s catch-all answers the agent's own bare route with 204 where
    `serve()`'s routes it to the SWML handler -- so mounting anything at all
    silently killed the endpoint the platform actually fetches.
    """

    @staticmethod
    def _router(path: str) -> APIRouter:
        router = APIRouter()

        @router.post(path)
        async def _handler() -> dict[str, bool]:
            return {"ok": True}

        return router

    def test_mounted_route_is_reachable(self) -> None:
        a = agent()
        a.mount(self._router("/handoff"), prefix="/myagent/chat")
        response = TestClient(a.get_app()).post("/myagent/chat/handoff")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

    def test_bare_agent_route_is_not_swallowed(self) -> None:
        """204 here means the SWML endpoint is dead. 401 means it is alive and
        merely demanding auth, which is correct."""
        a = agent()
        a.mount(self._router("/x"), prefix="/myagent/chat")
        assert TestClient(a.get_app()).post("/myagent").status_code != 204

    def test_several_mounts_all_stay_reachable(self) -> None:
        a = agent()
        a.mount(self._router("/one"), prefix="/myagent/a")
        a.mount(self._router("/two"), prefix="/myagent/b")
        client = TestClient(a.get_app())
        assert client.post("/myagent/a/one").status_code == 200
        assert client.post("/myagent/b/two").status_code == 200

    def test_health_endpoints_survive(self) -> None:
        a = agent()
        a.mount(self._router("/x"), prefix="/myagent/chat")
        assert TestClient(a.get_app()).get("/health").status_code == 200

    def test_mount_returns_self_for_chaining(self) -> None:
        a = agent()
        assert a.mount(self._router("/x"), prefix="/myagent/c") is a
