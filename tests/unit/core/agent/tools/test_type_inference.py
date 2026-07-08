"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Comprehensive tests for type-hint-based tool schema inference.
"""

from typing import Any, Optional, List, Dict, Literal

from signalwire.core.agent.tools.type_inference import (
    infer_schema,
    create_typed_handler_wrapper,
    _resolve_type,
    _parse_docstring_args,
)
from signalwire.core.agent_base import AgentBase
from signalwire.core.function_result import FunctionResult
from signalwire.core.swaig_function import SWAIGFunction


# ===========================================================================
# Tests for _resolve_type
# ===========================================================================

class TestResolveType:
    """Tests for the _resolve_type helper."""

    def test_str(self) -> None:
        schema, optional = _resolve_type(str)
        assert schema == {"type": "string"}
        assert optional is False

    def test_int(self) -> None:
        schema, optional = _resolve_type(int)
        assert schema == {"type": "integer"}
        assert optional is False

    def test_float(self) -> None:
        schema, optional = _resolve_type(float)
        assert schema == {"type": "number"}
        assert optional is False

    def test_bool(self) -> None:
        schema, optional = _resolve_type(bool)
        assert schema == {"type": "boolean"}
        assert optional is False

    def test_list(self) -> None:
        schema, optional = _resolve_type(list)
        assert schema == {"type": "array"}
        assert optional is False

    def test_dict(self) -> None:
        schema, optional = _resolve_type(dict)
        assert schema == {"type": "object"}
        assert optional is False

    def test_optional_str(self) -> None:
        schema, optional = _resolve_type(Optional[str])
        assert schema == {"type": "string"}
        assert optional is True

    def test_optional_int(self) -> None:
        schema, optional = _resolve_type(Optional[int])
        assert schema == {"type": "integer"}
        assert optional is True

    def test_literal_strings(self) -> None:
        schema, optional = _resolve_type(Literal["a", "b", "c"])
        assert schema == {"type": "string", "enum": ["a", "b", "c"]}
        assert optional is False

    def test_literal_ints(self) -> None:
        schema, optional = _resolve_type(Literal[1, 2, 3])
        assert schema == {"type": "integer", "enum": [1, 2, 3]}
        assert optional is False

    def test_list_of_str(self) -> None:
        schema, optional = _resolve_type(List[str])
        assert schema == {"type": "array", "items": {"type": "string"}}
        assert optional is False

    def test_list_of_int(self) -> None:
        schema, optional = _resolve_type(List[int])
        assert schema == {"type": "array", "items": {"type": "integer"}}
        assert optional is False

    def test_dict_str_any(self) -> None:
        schema, optional = _resolve_type(Dict[str, int])
        assert schema == {"type": "object"}
        assert optional is False

    def test_unknown_type_falls_back_to_string(self) -> None:
        class CustomType:
            pass
        schema, optional = _resolve_type(CustomType)
        assert schema == {"type": "string"}
        assert optional is False


# ===========================================================================
# Tests for _parse_docstring_args
# ===========================================================================

class TestParseDocstringArgs:
    """Tests for docstring parsing."""

    def test_empty_docstring(self) -> None:
        summary, params = _parse_docstring_args("")
        assert summary == ""
        assert params == {}

    def test_none_docstring(self) -> None:
        summary, params = _parse_docstring_args(None)  # type: ignore[arg-type]  # intentional invalid input
        assert summary == ""
        assert params == {}

    def test_summary_only(self) -> None:
        summary, params = _parse_docstring_args("Get the weather forecast.")
        assert summary == "Get the weather forecast."
        assert params == {}

    def test_args_block(self) -> None:
        doc = """Get the weather forecast.

        Args:
            city: Name of the city
            units: Temperature units (celsius or fahrenheit)
        """
        summary, params = _parse_docstring_args(doc)
        assert summary == "Get the weather forecast."
        assert params["city"] == "Name of the city"
        assert params["units"] == "Temperature units (celsius or fahrenheit)"

    def test_args_block_with_type_annotations(self) -> None:
        doc = """Look up a user.

        Args:
            name (str): The user's name
            age (int): The user's age
        """
        summary, params = _parse_docstring_args(doc)
        assert summary == "Look up a user."
        assert params["name"] == "The user's name"
        assert params["age"] == "The user's age"

    def test_args_block_with_returns_section(self) -> None:
        doc = """Do something.

        Args:
            x: First param
            y: Second param

        Returns:
            Some result
        """
        summary, params = _parse_docstring_args(doc)
        assert params["x"] == "First param"
        assert params["y"] == "Second param"

    def test_multiline_param_description(self) -> None:
        doc = """Search function.

        Args:
            query: The search query to execute
                against the database
            limit: Maximum results
        """
        summary, params = _parse_docstring_args(doc)
        assert "search query to execute" in params["query"]
        assert "against the database" in params["query"]
        assert params["limit"] == "Maximum results"


# ===========================================================================
# Tests for infer_schema - detection heuristic
# ===========================================================================

class TestInferSchemaDetection:
    """Tests for when infer_schema should and should not activate."""

    def test_old_style_args_raw_data(self) -> None:
        """Old-style (args, raw_data) should not be treated as typed."""
        def handler(args: dict[str, Any], raw_data: dict[str, Any]) -> None:
            pass
        params, required, desc, is_typed, has_raw_data = infer_schema(handler)
        assert is_typed is False

    def test_old_style_args_only(self) -> None:
        """Old-style (args,) should not be treated as typed."""
        def handler(args: dict[str, Any]) -> None:
            pass
        params, required, desc, is_typed, has_raw_data = infer_schema(handler)
        assert is_typed is False

    def test_varargs_fallback(self) -> None:
        """Functions with *args should fall back to old style."""
        def handler(*args: Any) -> None:
            pass
        params, required, desc, is_typed, has_raw_data = infer_schema(handler)
        assert is_typed is False

    def test_kwargs_fallback(self) -> None:
        """Functions with **kwargs should fall back to old style."""
        def handler(**kwargs: Any) -> None:
            pass
        params, required, desc, is_typed, has_raw_data = infer_schema(handler)
        assert is_typed is False

    def test_typed_params_detected(self) -> None:
        """Typed parameters should be detected as new style."""
        def handler(city: str, units: str = "celsius") -> None:
            pass
        params, required, desc, is_typed, has_raw_data = infer_schema(handler)
        assert is_typed is True

    def test_zero_param_tool(self) -> None:
        """Function with no params (after self filtering) is a valid zero-param typed tool."""
        def handler() -> None:
            """Get the current time."""
            pass
        params, required, desc, is_typed, has_raw_data = infer_schema(handler)
        assert is_typed is True
        assert params == {}
        assert required == []
        assert desc == "Get the current time."

    def test_self_filtered_out(self) -> None:
        """self parameter should be filtered out."""
        def handler(self: Any, city: str) -> None:
            pass
        params, required, desc, is_typed, has_raw_data = infer_schema(handler)
        assert is_typed is True
        assert "self" not in params
        assert "city" in params

    def test_no_annotations_fallback(self) -> None:
        """No type hints on non-standard param names should fall back."""
        def handler(city, units) -> None:  # type: ignore[no-untyped-def]  # intentional: exercises the no-annotations fallback path
            pass
        params, required, desc, is_typed, has_raw_data = infer_schema(handler)
        assert is_typed is False


# ===========================================================================
# Tests for infer_schema - type mapping
# ===========================================================================

class TestInferSchemaTypes:
    """Tests for correct type mapping in inferred schemas."""

    def test_string_param(self) -> None:
        def handler(name: str) -> None:
            pass
        params, *_ = infer_schema(handler)
        assert params["name"]["type"] == "string"

    def test_int_param(self) -> None:
        def handler(count: int) -> None:
            pass
        params, *_ = infer_schema(handler)
        assert params["count"]["type"] == "integer"

    def test_float_param(self) -> None:
        def handler(price: float) -> None:
            pass
        params, *_ = infer_schema(handler)
        assert params["price"]["type"] == "number"

    def test_bool_param(self) -> None:
        def handler(enabled: bool) -> None:
            pass
        params, *_ = infer_schema(handler)
        assert params["enabled"]["type"] == "boolean"

    def test_list_param(self) -> None:
        def handler(items: list[Any]) -> None:
            pass
        params, *_ = infer_schema(handler)
        assert params["items"]["type"] == "array"

    def test_dict_param(self) -> None:
        def handler(data: dict[str, Any]) -> None:
            pass
        params, *_ = infer_schema(handler)
        assert params["data"]["type"] == "object"

    def test_optional_param(self) -> None:
        def handler(name: str, nickname: Optional[str] = None) -> None:
            pass
        params, required, *_ = infer_schema(handler)
        assert params["name"]["type"] == "string"
        assert params["nickname"]["type"] == "string"
        assert "name" in required
        assert "nickname" not in required

    def test_literal_param(self) -> None:
        def handler(color: Literal["red", "green", "blue"]) -> None:
            pass
        params, *_ = infer_schema(handler)
        assert params["color"]["type"] == "string"
        assert params["color"]["enum"] == ["red", "green", "blue"]

    def test_list_of_str_param(self) -> None:
        def handler(tags: List[str]) -> None:
            pass
        params, *_ = infer_schema(handler)
        assert params["tags"]["type"] == "array"
        assert params["tags"]["items"] == {"type": "string"}


# ===========================================================================
# Tests for infer_schema - required/optional
# ===========================================================================

class TestInferSchemaRequired:
    """Tests for required vs optional parameter detection."""

    def test_no_default_is_required(self) -> None:
        def handler(city: str) -> None:
            pass
        _, required, *_ = infer_schema(handler)
        assert "city" in required

    def test_with_default_is_optional(self) -> None:
        def handler(city: str = "London") -> None:
            pass
        _, required, *_ = infer_schema(handler)
        assert "city" not in required

    def test_optional_type_is_not_required(self) -> None:
        def handler(city: Optional[str]) -> None:
            pass
        _, required, *_ = infer_schema(handler)
        assert "city" not in required

    def test_mixed_required_optional(self) -> None:
        def handler(city: str, units: str = "celsius", country: Optional[str] = None) -> None:
            pass
        _, required, *_ = infer_schema(handler)
        assert "city" in required
        assert "units" not in required
        assert "country" not in required


# ===========================================================================
# Tests for infer_schema - docstring integration
# ===========================================================================

class TestInferSchemaDocstring:
    """Tests for docstring-driven description and parameter docs."""

    def test_description_from_docstring(self) -> None:
        def handler(city: str) -> None:
            """Get the weather forecast."""
            pass
        _, _, desc, *_ = infer_schema(handler)
        assert desc == "Get the weather forecast."

    def test_no_docstring(self) -> None:
        def handler(city: str) -> None:
            pass
        _, _, desc, *_ = infer_schema(handler)
        assert desc is None

    def test_param_descriptions_from_docstring(self) -> None:
        def handler(city: str, units: str = "celsius") -> None:
            """Get the weather.

            Args:
                city: Name of the city
                units: Temperature units
            """
            pass
        params, *_ = infer_schema(handler)
        assert params["city"]["description"] == "Name of the city"
        assert params["units"]["description"] == "Temperature units"


# ===========================================================================
# Tests for infer_schema - raw_data handling
# ===========================================================================

class TestInferSchemaRawData:
    """Tests for raw_data parameter detection and exclusion."""

    def test_raw_data_detected(self) -> None:
        def handler(city: str, raw_data: Optional[dict[str, Any]] = None) -> None:
            pass
        _, _, _, is_typed, has_raw_data = infer_schema(handler)
        assert is_typed is True
        assert has_raw_data is True

    def test_raw_data_excluded_from_schema(self) -> None:
        def handler(city: str, raw_data: Optional[dict[str, Any]] = None) -> None:
            pass
        params, *_ = infer_schema(handler)
        assert "raw_data" not in params
        assert "city" in params

    def test_no_raw_data(self) -> None:
        def handler(city: str) -> None:
            pass
        _, _, _, is_typed, has_raw_data = infer_schema(handler)
        assert is_typed is True
        assert has_raw_data is False

    def test_only_raw_data(self) -> None:
        """Function with only raw_data param is a zero-param typed tool with raw_data."""
        def handler(raw_data: dict[str, Any]) -> None:
            pass
        params, required, _, is_typed, has_raw_data = infer_schema(handler)
        assert is_typed is True
        assert has_raw_data is True
        assert params == {}
        assert required == []


# ===========================================================================
# Tests for create_typed_handler_wrapper
# ===========================================================================

class TestCreateTypedHandlerWrapper:
    """Tests for the handler wrapper function."""

    def test_wrapper_unpacks_args(self) -> None:
        def handler(city: str, units: str = "celsius") -> FunctionResult:
            return FunctionResult(f"Weather in {city} ({units})")

        wrapper = create_typed_handler_wrapper(handler, has_raw_data=False)
        result = wrapper({"city": "London", "units": "fahrenheit"}, {})
        assert isinstance(result, FunctionResult)
        assert "London" in result.response
        assert "fahrenheit" in result.response

    def test_wrapper_passes_raw_data(self) -> None:
        def handler(city: str, raw_data: Optional[dict[str, Any]] = None) -> FunctionResult:
            call_id = raw_data.get("call_id", "none") if raw_data else "none"
            return FunctionResult(f"Weather in {city}, call={call_id}")

        wrapper = create_typed_handler_wrapper(handler, has_raw_data=True)
        result = wrapper({"city": "Paris"}, {"call_id": "abc123"})
        assert isinstance(result, FunctionResult)
        assert "Paris" in result.response
        assert "abc123" in result.response

    def test_wrapper_without_raw_data(self) -> None:
        def handler(name: str) -> FunctionResult:
            return FunctionResult(f"Hello, {name}")

        wrapper = create_typed_handler_wrapper(handler, has_raw_data=False)
        result = wrapper({"name": "Alice"}, {"call_id": "ignored"})
        assert isinstance(result, FunctionResult)
        assert "Alice" in result.response

    def test_wrapper_preserves_name(self) -> None:
        def my_tool(x: str) -> None:
            pass

        wrapper = create_typed_handler_wrapper(my_tool, has_raw_data=False)
        assert wrapper.__name__ == "my_tool"

    def test_wrapper_preserves_doc(self) -> None:
        def my_tool(x: str) -> None:
            """My tool docstring."""
            pass

        wrapper = create_typed_handler_wrapper(my_tool, has_raw_data=False)
        assert wrapper.__doc__ == "My tool docstring."

    def test_wrapper_has_wrapped_attr(self) -> None:
        def my_tool(x: str) -> None:
            pass

        wrapper = create_typed_handler_wrapper(my_tool, has_raw_data=False)
        assert wrapper.__wrapped__ is my_tool  # type: ignore[attr-defined]  # __wrapped__ set by functools.wraps

    def test_wrapper_with_empty_args(self) -> None:
        def handler() -> FunctionResult:
            return FunctionResult("done")

        wrapper = create_typed_handler_wrapper(handler, has_raw_data=False)
        result = wrapper({}, {})
        assert isinstance(result, FunctionResult)
        assert result.response == "done"

    def test_wrapper_with_default_values(self) -> None:
        def handler(city: str, units: str = "celsius") -> FunctionResult:
            return FunctionResult(f"{city}:{units}")

        wrapper = create_typed_handler_wrapper(handler, has_raw_data=False)
        # Only pass required arg, default should fill in
        result = wrapper({"city": "Tokyo"}, {})
        assert "Tokyo" in result.response
        assert "celsius" in result.response


# ===========================================================================
# Tests for end-to-end integration with AgentBase
# ===========================================================================

class TestEndToEndIntegration:
    """Tests that type inference works end-to-end through the decorator and registry."""

    def test_class_decorator_with_typed_handler(self) -> None:
        """Test that @AgentBase.tool() with typed params infers schema correctly."""

        class TestAgent(AgentBase):
            def __init__(self) -> None:
                super().__init__("Test Agent", route="/test")

            @AgentBase.tool(name="get_weather")
            def get_weather(self, city: str, units: str = "celsius") -> FunctionResult:
                """Get the weather forecast.

                Args:
                    city: Name of the city
                    units: Temperature units
                """
                return FunctionResult(f"Weather in {city}")

        agent = TestAgent()
        func = agent._tool_registry.get_function("get_weather")
        assert isinstance(func, SWAIGFunction)
        assert func.is_typed_handler is True
        assert "city" in func.parameters
        assert func.parameters["city"]["type"] == "string"
        assert func.parameters["city"]["description"] == "Name of the city"
        assert "units" in func.parameters
        assert func.parameters["units"]["type"] == "string"
        assert "city" in func.required
        assert "units" not in func.required
        assert func.description == "Get the weather forecast."

    def test_class_decorator_with_explicit_params_not_overridden(self) -> None:
        """Explicit parameters= should always win over inference."""

        explicit_params = {
            "location": {"type": "string", "description": "Location name"}
        }

        class TestAgent(AgentBase):
            def __init__(self) -> None:
                super().__init__("Test Agent", route="/test2")

            @AgentBase.tool(name="get_weather2", parameters=explicit_params, description="Explicit desc")
            def get_weather(self, city: str, units: str = "celsius") -> FunctionResult:
                """Get the weather forecast."""
                return FunctionResult(f"Weather in {city}")

        agent = TestAgent()
        func = agent._tool_registry.get_function("get_weather2")
        assert isinstance(func, SWAIGFunction)
        assert func.is_typed_handler is False
        assert "location" in func.parameters
        assert "city" not in func.parameters
        assert func.description == "Explicit desc"

    def test_class_decorator_old_style_still_works(self) -> None:
        """Old-style (self, args, raw_data) should work as before."""

        class TestAgent(AgentBase):
            def __init__(self) -> None:
                super().__init__("Test Agent", route="/test3")

            @AgentBase.tool(
                name="old_tool",
                description="Old style tool",
                parameters={"x": {"type": "string", "description": "Input"}},
            )
            def old_tool(self, args, raw_data) -> FunctionResult:  # type: ignore[no-untyped-def]  # intentional: exercises the old-style (untyped args, raw_data) path
                return FunctionResult("done")

        agent = TestAgent()
        func = agent._tool_registry.get_function("old_tool")
        assert isinstance(func, SWAIGFunction)
        assert func.is_typed_handler is False
        assert func.parameters == {"x": {"type": "string", "description": "Input"}}

    def test_typed_handler_execution_through_on_function_call(self) -> None:
        """Typed handler should execute correctly through the standard dispatch."""

        class TestAgent(AgentBase):
            def __init__(self) -> None:
                super().__init__("Test Agent", route="/test4")

            @AgentBase.tool(name="greet")
            def greet(self, name: str, greeting: str = "Hello") -> FunctionResult:
                """Greet someone.

                Args:
                    name: Person's name
                    greeting: Greeting word
                """
                return FunctionResult(f"{greeting}, {name}!")

        agent = TestAgent()
        result = agent.on_function_call("greet", {"name": "Alice", "greeting": "Hi"}, {})
        assert isinstance(result, FunctionResult)
        assert "Hi" in result.response
        assert "Alice" in result.response

    def test_typed_handler_with_defaults(self) -> None:
        """Typed handler should use defaults for missing args."""

        class TestAgent(AgentBase):
            def __init__(self) -> None:
                super().__init__("Test Agent", route="/test5")

            @AgentBase.tool(name="greet2")
            def greet(self, name: str, greeting: str = "Hello") -> FunctionResult:
                """Greet someone."""
                return FunctionResult(f"{greeting}, {name}!")

        agent = TestAgent()
        result = agent.on_function_call("greet2", {"name": "Bob"}, {})
        assert isinstance(result, FunctionResult)
        assert "Hello" in result.response
        assert "Bob" in result.response

    def test_typed_handler_with_raw_data(self) -> None:
        """Typed handler with raw_data should receive it."""

        class TestAgent(AgentBase):
            def __init__(self) -> None:
                super().__init__("Test Agent", route="/test6")

            @AgentBase.tool(name="check_call")
            def check_call(self, query: str, raw_data: Optional[dict[str, Any]] = None) -> FunctionResult:
                """Check the call.

                Args:
                    query: Search query
                """
                call_id = raw_data.get("call_id", "unknown") if raw_data else "unknown"
                return FunctionResult(f"query={query}, call={call_id}")

        agent = TestAgent()
        result = agent.on_function_call("check_call", {"query": "test"}, {"call_id": "c42"})
        assert isinstance(result, FunctionResult)
        assert "test" in result.response
        assert "c42" in result.response

    def test_literal_enum_in_swml(self) -> None:
        """Literal types should produce enum in SWML output."""

        class TestAgent(AgentBase):
            def __init__(self) -> None:
                super().__init__("Test Agent", route="/test7")

            @AgentBase.tool(name="set_mode")
            def set_mode(self, mode: Literal["auto", "manual", "off"]) -> FunctionResult:
                """Set the operating mode.

                Args:
                    mode: The mode to set
                """
                return FunctionResult(f"Mode set to {mode}")

        agent = TestAgent()
        func = agent._tool_registry.get_function("set_mode")
        assert isinstance(func, SWAIGFunction)
        assert func.parameters["mode"]["type"] == "string"
        assert func.parameters["mode"]["enum"] == ["auto", "manual", "off"]

    def test_instance_decorator_with_typed_handler(self) -> None:
        """Test the instance-level @agent.tool() decorator with typed params."""

        agent = AgentBase("Test Agent", route="/test8")

        @agent._tool_decorator(name="lookup")
        def lookup(user_id: int, include_details: bool = False) -> FunctionResult:
            """Look up a user.

            Args:
                user_id: The user's ID
                include_details: Whether to include extra details
            """
            return FunctionResult(f"User {user_id}")

        func = agent._tool_registry.get_function("lookup")
        assert isinstance(func, SWAIGFunction)
        assert func.is_typed_handler is True
        assert func.parameters["user_id"]["type"] == "integer"
        assert func.parameters["include_details"]["type"] == "boolean"
        assert "user_id" in func.required
        assert "include_details" not in func.required
        assert func.description == "Look up a user."

    def test_swml_output_includes_inferred_schema(self) -> None:
        """The generated SWML should include the inferred parameter schema."""

        class TestAgent(AgentBase):
            def __init__(self) -> None:
                super().__init__("Test Agent", route="/test9")

            @AgentBase.tool(name="search")
            def search(self, query: str, limit: int = 10) -> FunctionResult:
                """Search for items.

                Args:
                    query: Search query string
                    limit: Max results to return
                """
                return FunctionResult("results")

        agent = TestAgent()
        func = agent._tool_registry.get_function("search")
        assert isinstance(func, SWAIGFunction)
        swaig = func.to_swaig("https://example.com")

        assert swaig["function"] == "search"
        assert swaig["description"] == "Search for items."
        params = swaig["parameters"]
        assert params["type"] == "object"
        assert "query" in params["properties"]
        assert params["properties"]["query"]["type"] == "string"
        assert "limit" in params["properties"]
        assert params["properties"]["limit"]["type"] == "integer"
        assert "query" in params.get("required", [])
        assert "limit" not in params.get("required", [])
