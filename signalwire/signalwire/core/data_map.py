"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

DataMap class for building SWAIG data_map configurations

The SDK's installed documentation covers this module: run ``sw-pydocs datamap``, or ``sw-pydocs`` for the index.
"""

from typing import Any
from re import Pattern
from .function_result import FunctionResult
from .semantic_gate import FillerPhrases, SemanticGate, apply_gate_fields


class DataMap:
    """
    Builder class for creating SWAIG data_map configurations.

    This provides a fluent interface for building data_map tools that execute
    on the SignalWire server without requiring webhook endpoints. Works similar
    to FunctionResult but for building data_map structures.

    The platform runs a data_map in this order. The top-level expressions
    come first, and the first one that produces an output ends the function.
    Then the platform requests the first webhook whose ``require_args`` are
    met, and no other: if that webhook fails, it doesn't try later webhooks,
    and the fallback output runs. The fallback output also runs when no
    webhook produced a result. Without one, the AI gets a generic error.

    Templates read two different sets of data. A webhook's url and params,
    the top-level expressions and the fallback output read the call data,
    where an argument is ``${args.location}``. A webhook's foreach,
    expressions and output read its JSON response, whose fields are at the
    root (``${current.temp_f}``, or ``${array[0].x}`` for an array), with
    the call data under ``input``: an argument is ``${input.args.location}``
    there, and ``${args.location}`` is empty. Header values are sent as
    written, without template expansion.

    Example usage:
        # Simple API call - output goes inside webhook
        data_map = (DataMap('get_weather')
            .purpose('Get current weather information')
            .parameter('location', 'string', 'City name', required=True)
            .webhook('GET', 'https://api.weather.com/v1/current?key=API_KEY&q=${enc:args.location}')
            .output(FunctionResult('Weather in ${input.args.location}: ${current.condition.text}, ${current.temp_f}°F'))
        )

        # A webhook with a fallback output, used when the webhook fails
        data_map = (DataMap('search')
            .purpose('Search the catalog')
            .parameter('query', 'string', 'Search query', required=True)
            .webhook('GET', 'https://api.example.com/search?q=${enc:args.query}')
            .output(FunctionResult('Top result: ${title}'))
            .error_keys(['error'])
            .fallback_output(FunctionResult('Sorry, search is unavailable right now'))
        )

        # Expression-based responses (no API calls)
        data_map = (DataMap('file_control')
            .purpose('Control file playback')
            .parameter('command', 'string', 'Playback command')
            .parameter('filename', 'string', 'File to control', required=False)
            .expression('${args.command}', r'start.*', FunctionResult().add_action('start_playback', {'file': '${args.filename}'}))
            .expression('${args.command}', r'stop.*', FunctionResult().add_action('stop_playback', True))
        )

        # API with array processing
        data_map = (DataMap('search_docs')
            .purpose('Search documentation')
            .parameter('query', 'string', 'Search query', required=True)
            .webhook('POST', 'https://api.docs.com/search', headers={'Authorization': 'Bearer TOKEN'})
            .params({'query': '${args.query}', 'limit': 3})
            .foreach({
                'input_key': 'results',
                'output_key': 'formatted_results',
                'max': 3,
                'append': 'Result: ${this.title} - ${this.summary}\n'
            })
            .output(FunctionResult('Found:\n${formatted_results}'))
        )
    """

    def __init__(self, function_name: str):
        """
        Initialize a new DataMap builder

        Args:
            function_name: Name of the SWAIG function this data_map will create
        """
        self.function_name = function_name
        self._purpose = ""
        self._parameters: dict[str, Any] = {}
        self._expressions: list[dict[str, Any]] = []
        self._webhooks: list[dict[str, Any]] = []
        self._output: dict[str, Any] | None = None
        self._error_keys: list[str] = []
        self._gates: list[SemanticGate | dict[str, Any]] = []
        self._gate_fillers: FillerPhrases | None = None

    def purpose(self, description: str) -> "DataMap":
        """
        Set the function description that the LLM will read.

        A DataMap creates a SWAIG function that gets sent to the model in
        OpenAI tool-schema format. This `description` field is what the
        model reads on every turn to decide WHEN to call the tool. It is
        prompt-engineered text, not developer documentation:

          - Bad:  "Search function"
          - Good: "Search the company's knowledge base for help articles
                  matching a user query. Use this when the user asks a
                  product or how-to question that the base prompt does
                  not cover."

        Vague descriptions are the most common cause of "the model has
        the right tool but doesn't call it" failures.

        Args:
            description: LLM-facing description of what this function does
                and when to use it. See above.

        Returns:
            Self for method chaining.
        """
        self._purpose = description
        return self

    def description(self, description: str) -> "DataMap":
        """
        Set the function description (alias for purpose).

        See purpose() for guidance on writing description text the LLM
        can act on.

        Args:
            description: LLM-facing description of what this function does
                and when to use it.

        Returns:
            Self for method chaining.
        """
        return self.purpose(description)

    def parameter(
        self,
        name: str,
        param_type: str,
        description: str,
        required: bool = False,
        enum: list[str] | None = None,
    ) -> "DataMap":
        """
        Add a function parameter.

        Just like the function-level `description`, this parameter
        `description` is sent to the LLM as part of the tool schema and
        is read by the model when deciding HOW to fill in the argument.
        Write it as an instruction to the model:

          - Bad:  "the id"
          - Good: "The customer's 8-digit account number, no dashes or
                  spaces. Ask the user if they don't provide it."

        Args:
            name: Parameter name. Becomes a key in the tool schema's
                `properties` object and is what the model emits.
            param_type: JSON schema type (string, number, boolean, array,
                object).
            description: LLM-facing parameter description. See above —
                this should tell the model what value to put here, in
                what format, and where to source it.
            required: Whether parameter is required.
            enum: Optional list of allowed values. The model will only
                emit values from this list.

        Returns:
            Self for method chaining.
        """
        param_def: dict[str, Any] = {"type": param_type, "description": description}

        if enum:
            param_def["enum"] = enum

        self._parameters[name] = param_def

        if required:
            if "_required" not in self._parameters:
                self._parameters["_required"] = []
            if name not in self._parameters["_required"]:
                self._parameters["_required"].append(name)

        return self

    def expression(
        self,
        test_value: str,
        pattern: str | Pattern[str],
        output: FunctionResult,
        nomatch_output: FunctionResult | None = None,
    ) -> "DataMap":
        """
        Add an expression pattern for pattern-based responses

        The platform expands ``test_value`` against the call data, where an
        argument is ``${args.command}``, and searches it for ``pattern``: a
        regular expression that can match anywhere in the value, without
        regard to case. Write it as ``/pattern/flags`` to set the flags
        yourself (``i`` ignores case, ``s`` lets ``.`` match a newline).
        Expressions run in order, and the first that produces an output ends
        the function. An expression with ``nomatch_output`` always produces
        one, so no expression after it runs.

        Args:
            test_value: Template string to test (e.g., "${args.command}")
            pattern: Regex pattern string or compiled Pattern object to match against
            output: FunctionResult to return when pattern matches
            nomatch_output: Optional FunctionResult to return when pattern doesn't match

        Returns:
            Self for method chaining
        """
        pattern_str = pattern.pattern if isinstance(pattern, Pattern) else str(pattern)

        expr_def = {
            "string": test_value,
            "pattern": pattern_str,
            "output": output.to_dict(),
        }

        if nomatch_output:
            expr_def["nomatch-output"] = nomatch_output.to_dict()

        self._expressions.append(expr_def)
        return self

    def webhook(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        form_param: str | None = None,
        input_args_as_params: bool = False,
        require_args: list[str] | None = None,
    ) -> "DataMap":
        """
        Add a webhook API call

        The platform sends GET and POST requests only. A webhook is sent as a
        POST when ``method`` is ``"POST"`` or when it has params (see
        ``params()``), and as a GET otherwise, so PUT, PATCH and DELETE are
        sent as GET.

        The platform requests the first webhook whose ``require_args`` are
        met and no other. A later webhook is useful only when the earlier
        ones can be skipped by their ``require_args``; it doesn't run when an
        earlier one fails.

        Args:
            method: HTTP method: "GET" or "POST"
            url: API endpoint URL. Templates in it are expanded against the
                call data, such as ``${enc:args.location}``.
            headers: Optional HTTP headers, sent as written. The platform
                doesn't expand templates in header values.
            form_param: Send the JSON params as one form field with this name
            input_args_as_params: Merge the function's arguments into params,
                which makes the request a POST
            require_args: Skip this webhook, without a request, unless at
                least one of these arguments is present

        Returns:
            Self for method chaining
        """
        webhook_def: dict[str, Any] = {"url": url, "method": method.upper()}

        if headers:
            webhook_def["headers"] = headers
        if form_param:
            webhook_def["form_param"] = form_param
        if input_args_as_params:
            webhook_def["input_args_as_params"] = True
        if require_args:
            webhook_def["require_args"] = require_args

        self._webhooks.append(webhook_def)
        return self

    def webhook_expressions(self, expressions: list[dict[str, Any]]) -> "DataMap":
        """
        Add expressions that run after the most recent webhook completes

        They run after the webhook's foreach, against its response, and the
        first one that produces an output replaces the webhook's own output.
        Their templates read the response's fields from the root, and the
        call data under ``input``, such as ``${input.args.query}``.

        Args:
            expressions: List of expression definitions to check post-webhook

        Returns:
            Self for method chaining
        """
        if not self._webhooks:
            raise ValueError("Must add webhook before setting webhook expressions")

        self._webhooks[-1]["expressions"] = expressions
        return self

    def body(self, data: dict[str, Any]) -> "DataMap":
        """
        Set the JSON request body for the last added webhook; the same as params()

        The platform reads a webhook's body from its ``params`` field, and
        has no ``body`` field, so this sets ``params``. See ``params()``.

        Args:
            data: Request body data (can include ${variable} substitutions)

        Returns:
            Self for method chaining
        """
        if not self._webhooks:
            raise ValueError("Must add webhook before setting body")

        self._webhooks[-1]["params"] = data
        return self

    def params(self, data: dict[str, Any]) -> "DataMap":
        """
        Set the JSON request body for the last added webhook

        The platform sends ``params`` as the request's JSON body, not as URL
        query parameters, so a webhook with params is sent as a POST whatever
        its method. Put query parameters in the URL instead. Templates in the
        values are expanded against the call data, such as ``${args.query}``.

        Args:
            data: Request params data (can include ${variable} substitutions)

        Returns:
            Self for method chaining
        """
        if not self._webhooks:
            raise ValueError("Must add webhook before setting params")

        self._webhooks[-1]["params"] = data
        return self

    def foreach(self, foreach_config: dict[str, Any]) -> "DataMap":
        """
        Process an array from the webhook response using foreach mechanism

        The platform runs the foreach before the webhook's expressions and
        output, and stores the text it builds under ``output_key``, so the
        output reads it as ``${formatted_results}``.

        Args:
            foreach_config: Either:
                - Dict: Foreach configuration with keys:
                    - input_key: Path to the array in the API response, such
                      as ``results`` or ``data.items``
                    - output_key: Name for the built string variable
                    - max: Maximum number of items to process (optional)
                    - append: Template string to append for each item, where
                      ``${this}`` is the current item and ``${this.title}``
                      its field; the rest of the response stays readable

        Returns:
            Self for method chaining

        Example:
            .foreach({
                "input_key": "results",
                "output_key": "formatted_results",
                "max": 3,
                "append": "Result: ${this.title} - ${this.summary}\n"
            })
        """
        if not self._webhooks:
            raise ValueError("Must add webhook before setting foreach")

        if isinstance(foreach_config, dict):
            # New format - validate required keys
            required_keys = ["input_key", "output_key", "append"]
            missing_keys = [key for key in required_keys if key not in foreach_config]
            if missing_keys:
                raise ValueError(
                    f"foreach config missing required keys: {missing_keys}"
                )

            foreach_data = foreach_config
        else:
            raise ValueError("foreach_config must be a dictionary")

        self._webhooks[-1]["foreach"] = foreach_data
        return self

    def output(self, result: FunctionResult) -> "DataMap":
        """
        Set the output result for the most recent webhook

        Its templates read the webhook's JSON response: an object's fields
        from the root, such as ``${current.temp_f}``, or ``${array[0].x}``
        for an array. The call data is under ``input``, so an argument is
        ``${input.args.location}``; ``${args.location}`` is empty here.

        Args:
            result: FunctionResult defining the response for this webhook

        Returns:
            Self for method chaining
        """
        if not self._webhooks:
            raise ValueError("Must add webhook before setting output")

        self._webhooks[-1]["output"] = result.to_dict()
        return self

    def fallback_output(self, result: FunctionResult) -> "DataMap":
        """
        Set a fallback output result at the top level

        The platform uses it when no top-level expression produced an output
        and the webhook stage produced no result: the webhook it requested
        failed, or no webhook was eligible. It doesn't try a later webhook
        first. Its templates read the call data, so an argument is
        ``${args.location}``.

        Args:
            result: FunctionResult defining the fallback response

        Returns:
            Self for method chaining
        """
        self._output = result.to_dict()
        return self

    def error_keys(self, keys: list[str]) -> "DataMap":
        """
        Set error keys for the most recent webhook (if webhooks exist) or top-level

        The webhook fails when its JSON response has any of these keys at the
        top level, whatever the value, even ``false`` or ``null``. An HTTP
        status outside 200-299 isn't a failure by itself: the platform adds
        an ``http_code`` key to such a response, so ``"http_code"`` in this
        list fails the webhook on any such status. The platform reads error
        keys only on a webhook; called before any webhook, this sets a
        top-level ``error_keys`` field, which the platform ignores.

        Args:
            keys: List of JSON keys whose presence indicates an error

        Returns:
            Self for method chaining
        """
        if self._webhooks:
            # Add to most recent webhook
            self._webhooks[-1]["error_keys"] = keys
        else:
            # Store as top-level error keys
            self._error_keys = keys
        return self

    def global_error_keys(self, keys: list[str]) -> "DataMap":
        """
        Set top-level error keys

        The platform ignores a top-level ``error_keys`` field: it checks only
        each webhook's own. Call ``error_keys()`` after the webhook instead.

        Args:
            keys: List of JSON keys whose presence indicates an error

        Returns:
            Self for method chaining
        """
        self._error_keys = keys
        return self

    def gate(self, gate: SemanticGate | dict[str, Any]) -> "DataMap":
        """
        Add a semantic gate: a yes/no precondition a decision model checks
        right before the platform runs this function

        Every gate must pass for the function to run. When one doesn't, the
        data_map doesn't run, and the model gets that gate's ``on_fail``
        output. Call once per gate, up to 8; gates are checked when the
        function is built, by the platform's rules.

        Args:
            gate: A SemanticGate, or a gate dict

        Returns:
            Self for method chaining
        """
        self._gates.append(gate)
        return self

    def gate_fillers(self, fillers: FillerPhrases) -> "DataMap":
        """
        Set what the AI says while this function's gates are checked

        Shaped like a function's fillers: phrases keyed by language code,
        "auto" or "default". Without them, the AI says nothing while the
        gates are checked. Only for a function with gates.

        Args:
            fillers: Phrases by language

        Returns:
            Self for method chaining
        """
        self._gate_fillers = fillers
        return self

    def to_swaig_function(self) -> dict[str, Any]:
        """
        Convert this DataMap to a SWAIG function definition

        Returns:
            Dictionary with function definition and data_map instead of url

        Raises:
            ValueError: For gates the platform would refuse, or gate fillers
                without gates
        """
        # Build parameter schema
        if self._parameters:
            # Extract required params without mutating original dict
            required_params = self._parameters.get("_required", [])
            param_properties = {
                k: v for k, v in self._parameters.items() if k != "_required"
            }

            param_schema = {"type": "object", "properties": param_properties}
            if required_params:
                param_schema["required"] = required_params
        else:
            param_schema = {"type": "object", "properties": {}}

        # Build data_map structure
        data_map: dict[str, Any] = {}

        # Add expressions if present
        if self._expressions:
            data_map["expressions"] = self._expressions

        # Add webhooks if present
        if self._webhooks:
            data_map["webhooks"] = self._webhooks

        # Add output if present
        if self._output:
            data_map["output"] = self._output

        # Add error_keys if present
        if self._error_keys:
            data_map["error_keys"] = self._error_keys

        # Build final function definition with correct field names
        function: dict[str, Any] = {
            "function": self.function_name,
            "description": self._purpose or f"Execute {self.function_name}",
            "parameters": param_schema,
            "data_map": data_map,
        }
        if self._gates:
            function["gates"] = self._gates
        if self._gate_fillers is not None:
            function["gate_fillers"] = dict(self._gate_fillers)
        apply_gate_fields(function, self.function_name)
        return function


def create_simple_api_tool(
    name: str,
    url: str,
    response_template: str,
    parameters: dict[str, dict[str, Any]] | None = None,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    error_keys: list[str] | None = None,
) -> DataMap:
    """
    Create a simple API tool with minimal configuration

    Args:
        name: Function name
        url: API endpoint URL. Templates read the arguments as ``${args.x}``.
        response_template: Template for formatting the response. It reads the
            response's fields from the root, such as ``${current.temp_f}``, and
            the arguments as ``${input.args.x}``.
        parameters: Optional parameter definitions
        method: HTTP method (default: GET). A webhook with a body is sent as a
            POST.
        headers: Optional HTTP headers, sent as written
        body: Optional JSON request body, set as the webhook's params
        error_keys: Optional list of error indicator keys

    Returns:
        Configured DataMap object
    """
    data_map = DataMap(name)

    # Add parameters if provided
    if parameters:
        for param_name, param_def in parameters.items():
            required = param_def.get("required", False)
            data_map.parameter(
                param_name,
                param_def.get("type", "string"),
                param_def.get("description", f"{param_name} parameter"),
                required=required,
            )

    # Add webhook
    data_map.webhook(method, url, headers)

    # Add body if provided; the platform sends params as the body
    if body:
        data_map.params(body)

    # Add error keys if provided
    if error_keys:
        data_map.error_keys(error_keys)

    # Set output
    data_map.output(FunctionResult(response_template))

    return data_map


def create_expression_tool(
    name: str,
    patterns: dict[str, tuple[str, FunctionResult]],
    parameters: dict[str, dict[str, Any]] | None = None,
) -> DataMap:
    """
    Create an expression-based tool for pattern matching responses

    Args:
        name: Function name
        patterns: Dictionary mapping test_values to (pattern, FunctionResult) tuples
        parameters: Optional parameter definitions

    Returns:
        Configured DataMap object
    """
    data_map = DataMap(name)

    # Add parameters if provided
    if parameters:
        for param_name, param_def in parameters.items():
            required = param_def.get("required", False)
            data_map.parameter(
                param_name,
                param_def.get("type", "string"),
                param_def.get("description", f"{param_name} parameter"),
                required=required,
            )

    # Add expressions with corrected signature
    for test_value, (pattern, result) in patterns.items():
        data_map.expression(test_value, pattern, result)

    return data_map
