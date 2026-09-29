"""
Examples that set things the schema or the skills refuse.

llm_params_demo.py and simple_agent.py passed barge_confidence to
set_prompt_llm_params(). The platform never applies it, and the SWML schema's
prompt object doesn't define it, so their documents failed validation. mcp_gateway_demo.py defaulted to
http://localhost:8080 with placeholder credentials, which the mcp_gateway
skill's URL check refuses, so constructing the agent raised.
"""

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from signalwire import AgentBase
from signalwire.utils.schema_utils import SchemaUtils

REPO = Path(__file__).resolve().parents[2]

_GATEWAY_VARS = (
    "MCP_GATEWAY_URL",
    "MCP_GATEWAY_AUTH_TOKEN",
    "MCP_GATEWAY_AUTH_USER",
    "MCP_GATEWAY_AUTH_PASSWORD",
    "MCP_GATEWAY_SERVICES",
    "SWML_ALLOW_PRIVATE_URLS",
)


def _load(name: str) -> ModuleType:
    path = REPO / "examples" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"example_{name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _ai_prompt(agent: AgentBase) -> dict[str, Any]:
    document = json.loads(agent._render_swml())
    ok, errors = SchemaUtils().validate_document(document)
    assert ok, errors
    prompt: dict[str, Any] = next(
        verb["ai"]["prompt"] for verb in document["sections"]["main"] if "ai" in verb
    )
    return prompt


@pytest.mark.parametrize(
    "class_name", ["PreciseAssistant", "CreativeAssistant", "CustomerServiceAgent"]
)
def test_llm_params_demo_documents_are_valid(class_name: str) -> None:
    agent = getattr(_load("llm_params_demo"), class_name)()
    prompt = _ai_prompt(agent)
    assert "barge_confidence" not in prompt
    assert {"temperature", "top_p", "presence_penalty", "frequency_penalty"} <= set(
        prompt
    )


def test_simple_agent_document_is_valid() -> None:
    agent = _load("simple_agent").SimpleAgent()
    prompt = _ai_prompt(agent)
    assert "barge_confidence" not in prompt
    assert prompt["temperature"] == 0.3


class TestMcpGatewayDemo:
    @pytest.fixture(autouse=True)
    def _clean_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for var in _GATEWAY_VARS:
            monkeypatch.delenv(var, raising=False)

    def test_no_placeholder_url_or_credentials(self) -> None:
        demo = _load("mcp_gateway_demo")
        assert demo.gateway_params() is None
        source = (REPO / "examples" / "mcp_gateway_demo.py").read_text()
        assert "changeme" not in source
        assert "SWML_ALLOW_PRIVATE_URLS" in source

    def test_unconfigured_agent_starts_without_mcp_tools(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        agent = _load("mcp_gateway_demo").MCPGatewayAgent()
        assert not agent.has_skill("mcp_gateway")
        err = capsys.readouterr().err
        assert "MCP gateway not configured" in err
        assert "MCP_GATEWAY_URL" in err

    def test_url_needs_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MCP_GATEWAY_URL", "https://gateway.example.com")
        assert _load("mcp_gateway_demo").gateway_params() is None
        monkeypatch.setenv("MCP_GATEWAY_AUTH_USER", "user")
        assert _load("mcp_gateway_demo").gateway_params() is None

    def test_basic_auth_and_services(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MCP_GATEWAY_URL", "https://gateway.example.com")
        monkeypatch.setenv("MCP_GATEWAY_AUTH_USER", "user")
        monkeypatch.setenv("MCP_GATEWAY_AUTH_PASSWORD", "secret")
        monkeypatch.setenv("MCP_GATEWAY_SERVICES", "todo, calendar")
        assert _load("mcp_gateway_demo").gateway_params() == {
            "gateway_url": "https://gateway.example.com",
            "auth_user": "user",
            "auth_password": "secret",
            "services": [{"name": "todo"}, {"name": "calendar"}],
        }

    def test_token_auth_without_services(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MCP_GATEWAY_URL", "https://gateway.example.com")
        monkeypatch.setenv("MCP_GATEWAY_AUTH_TOKEN", "tok")
        assert _load("mcp_gateway_demo").gateway_params() == {
            "gateway_url": "https://gateway.example.com",
            "auth_token": "tok",
        }

    def test_localhost_gateway_is_refused_with_a_hint(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setenv("MCP_GATEWAY_URL", "http://localhost:8080")
        monkeypatch.setenv("MCP_GATEWAY_AUTH_TOKEN", "tok")
        agent = _load("mcp_gateway_demo").MCPGatewayAgent()
        assert not agent.has_skill("mcp_gateway")
        err = capsys.readouterr().err
        assert "Could not load the mcp_gateway skill" in err
        assert "SWML_ALLOW_PRIVATE_URLS=true" in err
