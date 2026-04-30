"""
Tests for ToolRegistry — the public API for managing SWAIG functions
on an agent. Methods exercised here are part of the cross-language SDK
contract: every port must support `has_function`, `get_function`,
`get_all_functions`, `remove_function`, `define_tool`, and
`register_swaig_function`.

Python parity baseline for: dotnet/go/typescript/java/php/rust/ruby/perl/cpp.
"""

import pytest
from unittest.mock import MagicMock

from signalwire.core.agent.tools.registry import ToolRegistry


@pytest.fixture
def registry():
    agent = MagicMock()
    return ToolRegistry(agent)


class TestToolRegistryDefineAndQuery:
    def test_register_swaig_function_via_dict(self, registry):
        registry.register_swaig_function({"function": "lookup", "description": "Look up a value"})
        assert registry.has_function("lookup")

    def test_has_function_false_when_unregistered(self, registry):
        assert registry.has_function("nope") is False

    def test_get_function_returns_registered(self, registry):
        registry.register_swaig_function({"function": "lookup", "description": "x"})
        fn = registry.get_function("lookup")
        assert fn is not None
        assert fn["function"] == "lookup"

    def test_get_function_none_when_unregistered(self, registry):
        assert registry.get_function("nope") is None

    def test_get_all_functions_starts_empty(self, registry):
        assert registry.get_all_functions() == {}

    def test_get_all_functions_returns_registered(self, registry):
        registry.register_swaig_function({"function": "a", "description": "x"})
        registry.register_swaig_function({"function": "b", "description": "y"})
        all_fns = registry.get_all_functions()
        assert set(all_fns.keys()) == {"a", "b"}

    def test_get_all_functions_returns_copy(self, registry):
        registry.register_swaig_function({"function": "a", "description": "x"})
        snapshot = registry.get_all_functions()
        registry.register_swaig_function({"function": "b", "description": "y"})
        # Original snapshot unaffected by later registration
        assert "b" not in snapshot

    def test_remove_function_when_present(self, registry):
        registry.register_swaig_function({"function": "doomed", "description": "x"})
        assert registry.remove_function("doomed") is True
        assert registry.has_function("doomed") is False

    def test_remove_function_when_absent_returns_false(self, registry):
        assert registry.remove_function("never_existed") is False

    def test_define_tool_registers_with_handler(self, registry):
        def my_handler(args, raw_data=None):
            return {"result": "ok"}
        registry.define_tool(
            name="echo",
            description="Echo back",
            parameters={"type": "object", "properties": {}},
            handler=my_handler,
        )
        assert registry.has_function("echo")
        fn = registry.get_function("echo")
        assert fn is not None
