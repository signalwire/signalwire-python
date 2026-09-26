"""
A tool handler that's a method of the agent runs on the per-request copy.

With a per-request configuration callback, a request is handled by a copy of
the agent that the callback configured. on_summary already ran on that copy,
but a tool method stayed bound to the original agent, so its ``self`` didn't
see what the callback set. The copy now binds such handlers to itself: plain
methods, typed methods (sync and async) and methods passed to define_tool().
"""

import functools
from typing import Any
from unittest.mock import patch

import httpx
import pytest

from signalwire import AgentBase
from signalwire.core.function_result import FunctionResult

AUTH = ("user", "pass")


class TenantAgent(AgentBase):
    def __init__(self) -> None:
        super().__init__(
            name="tenant", route="/agent", basic_auth=AUTH, suppress_logs=True
        )
        self.tenant = "none"
        self.set_dynamic_config_callback(self.configure)
        self.define_tool(
            name="registered",
            description="Registered method",
            parameters={},
            handler=self.registered,
            secure=False,
        )

    def configure(
        self,
        query: dict[str, Any],
        body: dict[str, Any],
        headers: dict[str, Any],
        agent: AgentBase,
    ) -> None:
        agent.tenant = query.get("tenant", "none")  # set on the copy

    @AgentBase.tool(
        name="plain", description="Plain method", parameters={}, secure=False
    )
    def plain(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        return FunctionResult(f"plain {self.tenant}")

    @AgentBase.tool(name="typed", secure=False)
    def typed(self, city: str) -> FunctionResult:
        """Typed method.

        Args:
            city: City name
        """
        return FunctionResult(f"typed {self.tenant} {city}")

    @AgentBase.tool(name="typed_async", secure=False)
    async def typed_async(self, city: str) -> FunctionResult:
        """Async typed method.

        Args:
            city: City name
        """
        return FunctionResult(f"async {self.tenant} {city}")

    def registered(
        self, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        return FunctionResult(f"registered {self.tenant}")

    def labelled(
        self, label: str, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        return FunctionResult(f"{label} {self.tenant}")


def _body(function: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "function": function,
        "argument": {"parsed": [args or {}]},
        "call_id": "call-1",
    }


@pytest.mark.parametrize(
    ("function", "args", "expected"),
    [
        ("plain", None, "plain acme"),
        ("typed", {"city": "Paris"}, "typed acme Paris"),
        ("typed_async", {"city": "Paris"}, "async acme Paris"),
        ("registered", None, "registered acme"),
    ],
)
async def test_a_tool_method_sees_the_per_request_configuration(
    function: str, args: dict[str, Any] | None, expected: str
) -> None:
    agent = TenantAgent()
    transport = httpx.ASGITransport(app=agent.get_app())
    async with httpx.AsyncClient(
        transport=transport, base_url="http://agent.test", auth=AUTH
    ) as client:
        response = await client.post(
            "/agent/swaig", params={"tenant": "acme"}, json=_body(function, args)
        )
    assert response.json() == {"response": expected}
    assert agent.tenant == "none"  # the original agent is untouched


def test_the_copy_rebinds_only_handlers_bound_to_the_agent() -> None:
    agent = TenantAgent()
    captured = agent

    def closure(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        return FunctionResult(captured.tenant)

    agent.define_tool(
        name="closure",
        description="Closure",
        parameters={},
        handler=closure,
        secure=False,
    )
    copy = agent._create_ephemeral_copy()
    functions = agent._tool_registry._swaig_functions
    copied = copy._tool_registry._swaig_functions
    for name in ("plain", "typed", "typed_async", "registered"):
        assert copied[name] is not functions[name]
        assert copied[name].handler is not functions[name].handler  # type: ignore[union-attr]  # SWAIGFunction entries
    # A closure can't be rebound, so the copy shares it
    assert copied["closure"] is functions["closure"]
    # The original's entries still run on the original
    assert functions["plain"].handler.__self__ is agent  # type: ignore[union-attr]  # a bound method


async def test_a_partial_of_a_method_sees_the_per_request_configuration() -> None:
    agent = TenantAgent()
    agent.define_tool(
        name="partial",
        description="Partial",
        parameters={},
        secure=False,
        handler=functools.partial(agent.labelled, "food"),
    )
    transport = httpx.ASGITransport(app=agent.get_app())
    async with httpx.AsyncClient(
        transport=transport, base_url="http://agent.test", auth=AUTH
    ) as client:
        response = await client.post(
            "/agent/swaig", params={"tenant": "acme"}, json=_body("partial")
        )
    assert response.json() == {"response": "food acme"}


class SlottedAgent(AgentBase):
    __slots__ = ("client",)

    def __init__(self) -> None:
        super().__init__(
            name="slotted", route="/agent", basic_auth=AUTH, suppress_logs=True
        )
        self.client = "api-client"
        self.set_dynamic_config_callback(lambda query, body, headers, agent: None)

    @AgentBase.tool(
        name="which_client", description="Client", parameters={}, secure=False
    )
    def which_client(
        self, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        return FunctionResult(self.client)


async def test_a_copy_keeps_attributes_a_subclass_holds_in_slots() -> None:
    agent = SlottedAgent()
    transport = httpx.ASGITransport(app=agent.get_app())
    async with httpx.AsyncClient(
        transport=transport, base_url="http://agent.test", auth=AUTH
    ) as client:
        response = await client.post("/agent/swaig", json=_body("which_client"))
    assert response.json() == {"response": "api-client"}


class TestSkillsOnTheCopy:
    """The copy shares the agent's loaded skills instead of loading them again."""

    def _agent(self, configure: Any = None) -> AgentBase:
        agent = AgentBase(
            name="skills", route="/agent", basic_auth=AUTH, suppress_logs=True
        )
        agent.add_skill("datetime")
        agent.set_dynamic_config_callback(
            configure or (lambda query, body, headers, agent: None)
        )
        return agent

    def test_the_copy_lists_the_agents_skills_without_setting_them_up_again(
        self,
    ) -> None:
        from signalwire.skills.datetime.skill import DateTimeSkill

        agent = self._agent()
        with patch.object(
            DateTimeSkill, "setup", autospec=True, return_value=True
        ) as setup:
            copy = agent._create_ephemeral_copy()
        assert copy.list_skills() == agent.list_skills() == ["datetime"]
        setup.assert_not_called()

    def test_the_callback_can_add_a_skill_the_agent_already_has(self) -> None:
        agent = self._agent(
            lambda query, body, headers, agent: agent.add_skill("datetime")
        )
        copy = agent._per_call_agent({}, {}, {})
        assert copy is not agent
        assert copy.list_skills() == ["datetime"]

    def test_removing_a_shared_skill_on_the_copy_leaves_the_agents_instance_alone(
        self,
    ) -> None:
        agent = self._agent()
        shared = agent.skill_manager.get_skill("datetime")
        copy = agent._create_ephemeral_copy()
        with patch.object(type(shared), "cleanup") as cleanup:
            copy.remove_skill("datetime")
        cleanup.assert_not_called()
        assert copy.list_skills() == []
        assert agent.list_skills() == ["datetime"]
