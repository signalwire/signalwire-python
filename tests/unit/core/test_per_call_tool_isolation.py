"""
A per-request copy's tools are its own.

The per-request copy of an agent shared its tool objects with the agent, so a
configuration callback that changed a tool (turned off `secure`, edited its
parameters, or set a DataMap webhook's header) changed it for every later
call. Each copy now gets its own copy of every tool's configuration.
"""

import json
from typing import Any

import httpx

from signalwire import AgentBase
from signalwire.core.data_map import DataMap
from signalwire.core.function_result import FunctionResult

AUTH = ("user", "pass")


def _lookup(args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    return FunctionResult("found")


def _weather() -> dict[str, Any]:
    return (
        DataMap("get_weather")
        .description("Get the weather")
        .parameter("city", "string", "City name", required=True)
        .webhook("GET", "https://api.example.com/weather?q=${enc:args.city}")
        .output(FunctionResult("It's ${current.temp} degrees."))
        .to_swaig_function()
    )


def _tenant_agent() -> AgentBase:
    def configure(query: dict[str, Any], body: dict[str, Any], headers: dict[str, Any],
                  agent: AgentBase) -> None:
        tenant = query.get("tenant")
        if tenant != "trusted":
            return
        for tool in agent.define_tools():
            if isinstance(tool, dict):
                webhook = tool["data_map"]["webhooks"][0]
                webhook.setdefault("headers", {})["Authorization"] = "Bearer trusted-key"
            else:
                tool.secure = False
                tool.parameters["note"] = {"type": "string", "description": "Trusted only"}

    agent = AgentBase(name="tenants", route="/agent", basic_auth=AUTH, suppress_logs=True)
    agent.define_tool(name="lookup", description="Look up", parameters={}, handler=_lookup)
    agent.register_swaig_function(_weather())
    agent.set_dynamic_config_callback(configure)
    return agent


def _functions(swml: str) -> dict[str, dict[str, Any]]:
    main = json.loads(swml)["sections"]["main"]
    ai = next(verb["ai"] for verb in main if "ai" in verb)
    return {function["function"]: function for function in ai["SWAIG"]["functions"]}


async def test_a_callbacks_tool_changes_stay_with_its_request() -> None:
    agent = _tenant_agent()
    transport = httpx.ASGITransport(app=agent.get_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://agent.test", auth=AUTH) as client:
        trusted = _functions((await client.get("/agent", params={"tenant": "trusted"})).text)
        other = _functions((await client.get("/agent", params={"tenant": "other"})).text)

    # The trusted request saw its own changes
    assert "note" in trusted["lookup"]["parameters"]["properties"]
    assert trusted["get_weather"]["data_map"]["webhooks"][0]["headers"] == {
        "Authorization": "Bearer trusted-key"}
    # A later request for another tenant didn't
    assert "note" not in other["lookup"]["parameters"].get("properties", {})
    assert "headers" not in other["get_weather"]["data_map"]["webhooks"][0]
    # secure=False applied to the trusted request's tool only
    assert "__token=" not in trusted["lookup"].get("web_hook_url", "")
    assert "__token=" in other["lookup"]["web_hook_url"]


def test_the_agents_own_tools_are_unchanged() -> None:
    agent = _tenant_agent()
    agent._per_call_agent({"tenant": "trusted"}, {}, {})
    lookup = agent._tool_registry._swaig_functions["lookup"]
    weather = agent._tool_registry._swaig_functions["get_weather"]
    assert lookup.secure is True  # type: ignore[union-attr]  # a SWAIGFunction
    assert "note" not in lookup.parameters  # type: ignore[union-attr]  # a SWAIGFunction
    assert "headers" not in weather["data_map"]["webhooks"][0]  # type: ignore[index]  # a DataMap dict
    # A secure tool still needs its token on the agent itself
    assert agent._tool_token_rejection("lookup", None, "call-1") is not None
