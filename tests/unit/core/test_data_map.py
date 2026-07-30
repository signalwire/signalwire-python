"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for DataMap class
"""

import pytest
import json
import re

from signalwire.core.data_map import (
    DataMap,
    create_simple_api_tool,
    create_expression_tool,
)
from signalwire.core.function_result import FunctionResult


class TestDataMapBasic:
    """Test basic DataMap functionality"""

    def test_basic_creation(self) -> None:
        """Test creating a basic DataMap"""
        data_map = DataMap("test_function")

        assert data_map.function_name == "test_function"
        assert data_map._purpose == ""
        assert data_map._parameters == {}
        assert data_map._expressions == []
        assert data_map._webhooks == []

    def test_creation_with_purpose(self) -> None:
        """Test creating DataMap with purpose"""
        data_map = DataMap("test_function")
        data_map.purpose("Test function description")

        assert data_map.function_name == "test_function"
        assert data_map._purpose == "Test function description"

    def test_creation_with_description_alias(self) -> None:
        """Test using description as alias for purpose"""
        data_map = DataMap("test_function")
        data_map.description("Test function description")

        assert data_map._purpose == "Test function description"

    def test_parameter_addition(self) -> None:
        """Test adding parameters"""
        data_map = DataMap("test_function")
        data_map.parameter("location", "string", "City name", required=True)

        assert "location" in data_map._parameters
        param = data_map._parameters["location"]
        assert param["type"] == "string"
        assert param["description"] == "City name"
        assert "_required" in data_map._parameters
        assert "location" in data_map._parameters["_required"]


class TestDataMapExpressions:
    """Test expression functionality"""

    def test_add_expression_with_string_pattern(self) -> None:
        """Test adding expression with string pattern"""
        data_map = DataMap("test_function")
        output = FunctionResult("Pattern matched")

        data_map.expression("${args.command}", r"start.*", output)

        assert len(data_map._expressions) == 1
        expr = data_map._expressions[0]
        assert expr["string"] == "${args.command}"
        assert expr["pattern"] == r"start.*"
        assert expr["output"] == output.to_dict()

    def test_add_expression_with_compiled_pattern(self) -> None:
        """Test adding expression with compiled regex pattern"""
        data_map = DataMap("test_function")
        output = FunctionResult("Pattern matched")
        pattern = re.compile(r"stop.*")

        data_map.expression("${args.command}", pattern, output)

        expr = data_map._expressions[0]
        assert expr["pattern"] == r"stop.*"

    def test_add_expression_with_nomatch_output(self) -> None:
        """Test adding expression with nomatch output"""
        data_map = DataMap("test_function")
        match_output = FunctionResult("Matched")
        nomatch_output = FunctionResult("No match")

        data_map.expression("${args.command}", r"test.*", match_output, nomatch_output)

        expr = data_map._expressions[0]
        assert "nomatch-output" in expr
        assert expr["nomatch-output"] == nomatch_output.to_dict()


class TestDataMapWebhooks:
    """Test webhook functionality"""

    def test_add_basic_webhook(self) -> None:
        """Test adding basic webhook"""
        data_map = DataMap("test_function")

        data_map.webhook("GET", "https://api.example.com/data")

        assert len(data_map._webhooks) == 1
        webhook = data_map._webhooks[0]
        assert webhook["method"] == "GET"
        assert webhook["url"] == "https://api.example.com/data"

    def test_add_webhook_with_headers(self) -> None:
        """Test adding webhook with headers"""
        data_map = DataMap("test_function")
        headers = {"Authorization": "Bearer token", "Content-Type": "application/json"}

        data_map.webhook("POST", "https://api.example.com/data", headers=headers)

        webhook = data_map._webhooks[0]
        assert webhook["headers"] == headers

    def test_add_webhook_with_options(self) -> None:
        """Test adding webhook with various options"""
        data_map = DataMap("test_function")

        data_map.webhook(
            "POST",
            "https://api.example.com/data",
            form_param="data",
            input_args_as_params=True,
            require_args=["location"],
        )

        webhook = data_map._webhooks[0]
        assert webhook["form_param"] == "data"
        assert webhook["input_args_as_params"] is True
        assert webhook["require_args"] == ["location"]

    def test_webhook_params(self) -> None:
        """params() writes the ``params`` webhook key — the one in the contract.

        Was ``test_webhook_body_and_params``, which called body() AND params() and
        then asserted only ``len(_webhooks) == 1`` — it never checked either key, so
        it passed for any shape. It now asserts the emitted key.
        """
        data_map = DataMap("test_function")

        data_map.webhook("POST", "https://api.example.com/data")
        data_map.params({"api_key": "12345", "query": "${location}"})

        assert len(data_map._webhooks) == 1
        wh = data_map._webhooks[0]
        assert wh["params"] == {"api_key": "12345", "query": "${location}"}
        assert "body" not in wh


class TestDataMapOutput:
    """Test output functionality"""

    def test_set_output(self) -> None:
        """Test setting output"""
        data_map = DataMap("test_function")
        output = FunctionResult("API call successful: ${response.data}")

        # Must add webhook first
        data_map.webhook("GET", "https://api.example.com/data")
        data_map.output(output)

        # Output should be stored in the webhook
        assert data_map._webhooks[0]["output"] == output.to_dict()

    def test_set_fallback_output(self) -> None:
        """Test setting fallback output"""
        data_map = DataMap("test_function")
        fallback = FunctionResult("API unavailable")

        data_map.fallback_output(fallback)

        # Should be stored in the data map structure
        assert data_map._output == fallback.to_dict()


class TestDataMapSerialization:
    """Test serialization functionality"""

    def test_to_swaig_function_basic(self) -> None:
        """Test basic to_swaig_function conversion"""
        data_map = DataMap("test_function")
        data_map.purpose("Test function")
        data_map.parameter("location", "string", "City name", required=True)

        swaig_func = data_map.to_swaig_function()

        assert swaig_func["function"] == "test_function"
        assert swaig_func["description"] == "Test function"
        assert "parameters" in swaig_func
        assert "properties" in swaig_func["parameters"]
        assert "location" in swaig_func["parameters"]["properties"]

    def test_to_swaig_function_with_expressions(self) -> None:
        """Test to_swaig_function with expressions"""
        data_map = DataMap("test_function")
        data_map.purpose("Test function")
        output = FunctionResult("Expression result")
        data_map.expression("${args.command}", r"test.*", output)

        swaig_func = data_map.to_swaig_function()

        assert "data_map" in swaig_func
        assert "expressions" in swaig_func["data_map"]
        assert len(swaig_func["data_map"]["expressions"]) == 1

    def test_to_swaig_function_with_webhooks(self) -> None:
        """Test to_swaig_function with webhooks"""
        data_map = DataMap("test_function")
        data_map.purpose("Test function")
        data_map.webhook("GET", "https://api.example.com/data")
        output = FunctionResult("Webhook result: ${response.data}")
        data_map.output(output)

        swaig_func = data_map.to_swaig_function()

        assert "data_map" in swaig_func
        assert "webhooks" in swaig_func["data_map"]
        assert len(swaig_func["data_map"]["webhooks"]) == 1


class TestDataMapChaining:
    """Test method chaining functionality"""

    def test_method_chaining(self) -> None:
        """Test that methods return self for chaining"""
        output = FunctionResult("Chained result")

        data_map = (
            DataMap("test_function")
            .purpose("Test chaining")
            .parameter("param1", "string", "Parameter 1")
            .webhook("GET", "https://api.example.com/data")
            .output(output)
        )

        assert data_map.function_name == "test_function"
        assert data_map._purpose == "Test chaining"
        assert "param1" in data_map._parameters
        assert len(data_map._webhooks) == 1

    def test_complex_chaining(self) -> None:
        """Test complex method chaining"""
        result = FunctionResult()
        result.say("Complex result")

        data_map = (
            DataMap("complex_function")
            .purpose("Complex test")
            .parameter("input", "string", "Input data", required=True)
            .webhook("POST", "https://api.example.com/process")
            .params({"data": "${input}"})
            .output(result)
        )

        assert data_map._purpose == "Complex test"
        assert "input" in data_map._parameters


class TestDataMapFactoryFunctions:
    """Test factory functions"""

    def test_create_simple_api_tool(self) -> None:
        """Test create_simple_api_tool factory"""
        data_map = create_simple_api_tool(
            name="weather_tool",
            url="https://api.weather.com/current?location=${location}",
            response_template="Weather: ${response.condition}, ${response.temp}°F",
        )

        assert isinstance(data_map, DataMap)
        assert data_map.function_name == "weather_tool"

    def test_create_simple_api_tool_with_parameters(self) -> None:
        """Test create_simple_api_tool with parameters"""
        parameters = {"location": {"type": "string", "description": "City name"}}

        data_map = create_simple_api_tool(
            name="weather_tool",
            url="https://api.weather.com/current",
            response_template="Weather data",
            parameters=parameters,
        )

        assert isinstance(data_map, DataMap)

    def test_create_simple_api_tool_rejects_body(self) -> None:
        """`create_simple_api_tool` has no `body` parameter.

        `body` is not a valid webhook key: porting-sdk/schema.json `$defs/Webhook`
        declares exactly ten properties (error_keys, expressions, foreach, headers,
        input_args_as_params, method, output, params, require_args, url) under
        `unevaluatedProperties: {"not": {}}`, and neither engine reader
        (mod_openai/actions.c parse_webhook, mod_openai/bedrock.c
        bedrock_parse_webhook) looks up "body". Accepting the argument and
        discarding it into an unread key silently lost the caller's data.
        """
        with pytest.raises(TypeError):
            create_simple_api_tool(  # type: ignore[call-arg]
                name="poster",
                url="https://api.example.com/search",
                response_template="Found: ${response.title}",
                method="POST",
                body={"query": "${args.q}"},
            )

    def test_create_simple_api_tool_emits_no_body_key(self) -> None:
        """The EMITTED webhook payload carries no `body` key."""
        data_map = create_simple_api_tool(
            name="poster",
            url="https://api.example.com/search",
            response_template="Found: ${response.title}",
            parameters={"q": {"type": "string", "description": "Query"}},
            method="POST",
            headers={"Authorization": "Bearer TOKEN"},
            error_keys=["error"],
        )

        emitted = data_map.to_swaig_function()
        webhooks = emitted["data_map"]["webhooks"]
        assert len(webhooks) == 1
        assert "body" not in webhooks[0], f"webhook carries a body key: {webhooks[0]!r}"

        allowed = {
            "error_keys",
            "expressions",
            "foreach",
            "headers",
            "input_args_as_params",
            "method",
            "output",
            "params",
            "require_args",
            "url",
        }
        assert set(webhooks[0]) <= allowed, (
            f"webhook has keys outside schema.json $defs/Webhook: "
            f"{sorted(set(webhooks[0]) - allowed)}"
        )

    def test_create_expression_tool(self) -> None:
        """Test create_expression_tool factory"""
        # NOTE: create_expression_tool takes dict[test_value -> (pattern, result)],
        # so the test_value is the KEY -- two patterns cannot share one test_value
        # (this literal previously repeated "${args.command}" twice and the second
        # entry silently clobbered the first, so only "stop" was ever exercised).
        patterns = {
            "${args.command}": ("start", FunctionResult().add_action("start", True)),
            "${args.mode}": ("stop", FunctionResult().add_action("stop", True)),
        }

        data_map = create_expression_tool("control_tool", patterns)

        assert isinstance(data_map, DataMap)
        assert data_map.function_name == "control_tool"
        # Both entries must survive -- one expression per pattern, in order.
        expressions = data_map.to_swaig_function()["data_map"]["expressions"]
        assert [(e["string"], e["pattern"]) for e in expressions] == [
            ("${args.command}", "start"),
            ("${args.mode}", "stop"),
        ]

    def test_create_expression_tool_with_parameters(self) -> None:
        """Test create_expression_tool with parameters"""
        patterns = {"${args.input}": ("test", FunctionResult("Test result"))}
        parameters = {"input": {"type": "string", "description": "Input text"}}

        data_map = create_expression_tool("test_tool", patterns, parameters)

        assert isinstance(data_map, DataMap)


class TestDataMapErrorHandling:
    """Test error handling and edge cases"""

    def test_empty_function_name(self) -> None:
        """Test creating DataMap with empty function name"""
        # Should not raise error, just store empty string
        data_map = DataMap("")
        assert data_map.function_name == ""

    def test_none_function_name(self) -> None:
        """Test creating DataMap with None function name"""
        # Should not raise error, just store None
        data_map = DataMap(None)  # type: ignore[arg-type]  # intentional invalid input for validation test
        assert data_map.function_name is None

    def test_invalid_parameter_type(self) -> None:
        """Test adding parameter with invalid type"""
        data_map = DataMap("test_function")

        # Should not validate type, just store it
        data_map.parameter("test_param", "invalid_type", "Test parameter")

        param = data_map._parameters["test_param"]
        assert param["type"] == "invalid_type"

    def test_duplicate_parameter_names(self) -> None:
        """Test adding parameters with duplicate names"""
        data_map = DataMap("test_function")

        data_map.parameter("param1", "string", "First description")
        data_map.parameter("param1", "number", "Second description")

        # Should overwrite the first parameter
        param = data_map._parameters["param1"]
        assert param["type"] == "number"
        assert param["description"] == "Second description"

    def test_output_without_webhook(self) -> None:
        """Test setting output without webhook raises error"""
        data_map = DataMap("test_function")
        output = FunctionResult("Test output")

        with pytest.raises(ValueError, match="Must add webhook before setting output"):
            data_map.output(output)


class TestDataMapTemplateVariables:
    """Test template variable handling"""

    def test_env_variables_in_webhooks(self) -> None:
        """Test environment variables in webhook URLs"""
        data_map = DataMap("test_function")

        data_map.webhook("GET", "https://api.example.com/data?key=${ENV.API_KEY}")

        webhook = data_map._webhooks[0]
        assert "${ENV.API_KEY}" in webhook["url"]

    def test_args_variables_in_body(self) -> None:
        """Test argument variables in request body"""
        data_map = DataMap("test_function")

        data_map.webhook("POST", "https://api.example.com/data")
        data_map.params({"query": "${args.search_term}", "limit": 10})

        # Body should be stored for processing
        assert len(data_map._webhooks) == 1

    def test_response_variables_in_output(self) -> None:
        """Test response variables in output templates"""
        data_map = DataMap("test_function")
        output = FunctionResult("Result: ${response.data.title}")

        data_map.webhook("GET", "https://api.example.com/data")
        data_map.output(output)

        assert data_map._webhooks[0]["output"] == output.to_dict()


class TestDataMapIntegration:
    """Test integration with other components"""

    def test_agent_integration(self) -> None:
        """Test DataMap integration with agent"""
        data_map = DataMap("test_tool")
        data_map.purpose("Test integration")
        data_map.parameter("input", "string", "Input data")

        swaig_func = data_map.to_swaig_function()

        # Should be compatible with agent.define_tool
        assert "function" in swaig_func
        assert "description" in swaig_func
        assert "parameters" in swaig_func

    def test_swaig_function_compatibility(self) -> None:
        """Test compatibility with FunctionResult"""
        data_map = DataMap("test_function")
        result = FunctionResult("Test response")
        result.add_action("test_action", {"key": "value"})

        data_map.webhook("GET", "https://api.example.com/data")
        data_map.output(result)

        # Should store the result properly
        assert data_map._webhooks[0]["output"] == result.to_dict()

    def test_json_serialization(self) -> None:
        """Test JSON serialization of complete DataMap"""

        data_map = DataMap("serialization_test")
        data_map.purpose("Test serialization")
        data_map.parameter("input", "string", "Test input")
        result = FunctionResult("Serialized result")
        data_map.webhook("GET", "https://api.example.com/data")
        data_map.output(result)

        swaig_func = data_map.to_swaig_function()

        # Should be JSON serializable
        json_str = json.dumps(swaig_func)
        assert isinstance(json_str, str)

        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed["function"] == "serialization_test"


class TestBodyBuilderRemoved:
    """``DataMap.body()`` is GONE — the key it wrote is invalid, not merely ignored.

    Owner-ruled 2026-07-29, extending the f171ce3 ruling ("if the server doesn't
    read them, remove them") from the ``create_simple_api_tool`` PARAMETER to the
    public BUILDER METHOD. The same three sources condemn both:

    * ``porting-sdk/schema.json`` ``$defs/Webhook`` declares exactly ten properties
      under ``unevaluatedProperties: {"not": {}}`` — ``body`` is not among them, so
      emitting it is a SCHEMA VIOLATION.
    * ``mod_openai/actions.c:735-739`` and ``bedrock.c:4920-4926`` read url, method,
      form_param, ``params`` and ``headers`` and nothing else; ``grep -n '"body"'``
      across both returns ZERO matches.
    * So the method's only possible effect was producing an invalid document while
      silently discarding the caller's payload.

    ``params()`` is the correct method for POST/PUT request data — it writes the
    ``params`` key, which IS in the contract and IS read.
    """

    def test_body_method_is_gone(self) -> None:
        from signalwire.core.data_map import DataMap

        assert not hasattr(DataMap, "body"), (
            "DataMap.body() must be removed — it writes a schema-forbidden key "
            "that no engine reader consumes; use params() instead"
        )

    def test_params_still_writes_the_contract_key(self) -> None:
        """The replacement must keep working — this is the positive control."""
        from signalwire.core.data_map import DataMap

        dm = DataMap("t").webhook("POST", "https://x.test").params({"q": "${query}"})
        wh = dm.to_swaig_function()["data_map"]["webhooks"][0]
        assert wh["params"] == {"q": "${query}"}
        assert "body" not in wh
