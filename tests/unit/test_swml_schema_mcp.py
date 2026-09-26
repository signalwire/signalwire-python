"""
The SWML schema search MCP server (mcp/swml-schema-search) finds the SDK's
schema.json without SWML_SCHEMA_PATH.

Its default path pointed at <repo>/signalwire/schema.json, one directory
short of the real <repo>/signalwire/signalwire/schema.json, so the server
exited on start unless the variable was set (B16).
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "mcp"
    / "swml-schema-search"
    / "swml_schema_mcp.py"
)


@pytest.fixture
def server(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    monkeypatch.delenv("SWML_SCHEMA_PATH", raising=False)
    spec = importlib.util.spec_from_file_location("swml_schema_mcp_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_path_is_the_packaged_schema(server: ModuleType) -> None:
    path = Path(server.default_schema_path())
    assert path.is_file()
    assert path.name == "schema.json"
    assert path.parent.name == "signalwire"


def test_loads_the_schema_without_the_environment_variable(server: ModuleType) -> None:
    server.load_schema()
    assert len(server.METHODS) > 10
    assert "ai" in server.METHODS


def test_environment_variable_still_wins(
    server: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    schema = tmp_path / "custom.json"
    schema.write_text('{"$defs": {"SWMLMethod": {"anyOf": []}}}')
    monkeypatch.setenv("SWML_SCHEMA_PATH", str(schema))
    server.load_schema()
    assert server.SCHEMA == {"$defs": {"SWMLMethod": {"anyOf": []}}}
