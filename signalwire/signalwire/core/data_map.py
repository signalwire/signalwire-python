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
    """Build a SWAIG data_map function with a fluent interface.

    A DataMap defines a tool that the SignalWire platform runs itself: it calls
    a REST API, or matches the arguments against patterns, and formats the
    answer, with no webhook endpoint on your server. That cuts latency and
    simplifies deployment. Use a DataMap for a simple API-to-response
    integration. For business logic, database access or multi-step processing,
    use a SWAIG function with a handler instead.

    It works like `FunctionResult`, but builds a data_map structure. Call
    `to_swaig_function()` for the function definition, and register that with
    the agent using `register_swaig_function()`.

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

    Variable substitution patterns:

    - ``${args.param}``: a function argument, in a webhook's url and params.
    - ``${input.args.param}``: a function argument, in a webhook's output,
      expressions and foreach.
    - ``${enc:args.param}``: the argument, URL-encoded (for webhook URLs).
    - ``${lc:args.param}``: the argument, lowercased.
    - ``${fmt_ph:args.phone}``: the argument, formatted as a phone number.
    - ``${field}`` and ``${arr[0]}``: a field or array element of the webhook
      response, in a webhook's output only.
    - ``${global_data.key}``: global session data.
    - ``${meta_data.key}``: the function's metadata, set with
      ``FunctionResult.set_metadata()``; ``${input.meta_data.key}`` in a
      webhook's output.
    - ``${this.field}``: the current item, inside a foreach.

    The prefix helpers ``lc:``, ``enc:`` and ``fmt_ph:`` apply in a fixed
    order, ``fmt_ph``, then ``lc``, then ``enc``, whatever order you write
    them in: ``${lc:enc:args.city}`` lowercases the city and then
    URL-encodes it. There is no ``enc:url:`` prefix.

    Attributes:
        function_name: Name of the SWAIG function this data_map creates.

    Note:
        A DataMap generates the SWML ``data_map`` object inside a SWAIG
        function definition.

    Example:
        ```python
        # A webhook, with a fallback output used when it fails
        weather = (
            DataMap("get_weather")
            .purpose("Get current weather for a city")
            .parameter("city", "string", "City name", required=True)
            .webhook(
                "GET",
                "https://api.weatherapi.com/v1/current.json"
                "?key=YOUR_API_KEY&q=${enc:args.city}",
            )
            .output(
                FunctionResult(
                    "Weather in ${input.args.city}: "
                    "${current.condition.text}, ${current.temp_f} F"
                )
            )
            .error_keys(["error"])
            .fallback_output(
                FunctionResult("Sorry, I couldn't get weather for ${args.city}")
            )
        )
        agent.register_swaig_function(weather.to_swaig_function())

        # Expression-based responses, with no API call
        volume = (
            DataMap("set_volume")
            .purpose("Control audio volume")
            .parameter("level", "string", "Volume level", required=True)
            .expression(
                "${args.level}", r"high|loud|up", FunctionResult("Volume up")
            )
            .expression(
                "${args.level}", r"low|quiet|down", FunctionResult("Volume down")
            )
        )

        # POST with a body and an array from the response
        search = (
            DataMap("search_docs")
            .purpose("Search documentation")
            .parameter("query", "string", "Search query", required=True)
            .webhook(
                "POST",
                "https://api.docs.example.com/search",
                headers={"Authorization": "Bearer TOKEN"},
            )
            .params({"query": "${args.query}", "limit": 3})
            .foreach(
                {
                    "input_key": "results",
                    "output_key": "formatted_results",
                    "max": 3,
                    "append": "- ${this.title}: ${this.summary}\\n",
                }
            )
            .output(FunctionResult("Found:\\n${formatted_results}"))
        )
        ```
    """

    def __init__(self, function_name: str):
        """Initialize a new DataMap builder.

        Args:
            function_name: Name of the SWAIG function this data_map will create.
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
        """Set the function description that the LLM will read.

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
            This DataMap, for chaining.

        Example:
            ```python
            weather = DataMap("get_weather")
            weather.purpose("Get the current weather for a given city")
            ```
        """
        self._purpose = description
        return self

    def description(self, description: str) -> "DataMap":
        """Set the function description (alias for `purpose`).

        See `purpose()` for guidance on writing description text the LLM
        can act on.

        Args:
            description: LLM-facing description of what this function does
                and when to use it.

        Returns:
            This DataMap, for chaining.
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
        """Add a function parameter to the tool definition.

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
            param_type: JSON schema type: "string", "integer", "number",
                "boolean", "array" or "object".
            description: LLM-facing parameter description. See above —
                this should tell the model what value to put here, in
                what format, and where to source it.
            required: Whether the parameter is required. Defaults to False.
            enum: Optional list of allowed values. The model will only
                emit values from this list.

        Returns:
            This DataMap, for chaining.

        Example:
            ```python
            weather = (
                DataMap("get_weather")
                .parameter("city", "string", "City name", required=True)
                .parameter(
                    "units",
                    "string",
                    "Temperature units",
                    enum=["fahrenheit", "celsius"],
                )
            )
            ```
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
        """Add an expression pattern for pattern-based responses.

        An expression answers without an API call.

        The platform expands ``test_value`` against the call data, where an
        argument is ``${args.command}``, and searches it for ``pattern``: a
        regular expression that can match anywhere in the value, without
        regard to case. Write it as ``/pattern/flags`` to set the flags
        yourself (``i`` ignores case, ``s`` lets ``.`` match a newline).
        Expressions run in order, and the first that produces an output ends
        the function. An expression with ``nomatch_output`` always produces
        one, so no expression after it runs.

        Args:
            test_value: Template string to test, such as ``"${args.command}"``.
            pattern: Regex pattern string, or a compiled Pattern object whose
                pattern text is used, to match against the test value.
            output: `FunctionResult` to return when the pattern matches.
            nomatch_output: Optional `FunctionResult` to return when the
                pattern doesn't match.

        Returns:
            This DataMap, for chaining.

        Example:
            ```python
            volume = (
                DataMap("set_volume")
                .purpose("Control audio volume")
                .parameter("level", "string", "Volume level", required=True)
                .expression(
                    "${args.level}", r"high|loud|up", FunctionResult("Volume up")
                )
                .expression(
                    "${args.level}", r"mute|off", FunctionResult("Audio muted")
                )
            )
            ```
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
        """Add a webhook API call.

        The platform sends GET and POST requests only. A webhook is sent as a
        POST when ``method`` is ``"POST"`` or when it has params (see
        ``params()``), and as a GET otherwise, so PUT, PATCH and DELETE are
        sent as GET.

        The platform requests the first webhook whose ``require_args`` are
        met and no other. A later webhook is useful only when the earlier
        ones can be skipped by their ``require_args``; it doesn't run when an
        earlier one fails.

        Args:
            method: HTTP method: "GET" or "POST". The method is upper-cased.
            url: API endpoint URL. Templates in it are expanded against the
                call data, such as ``${enc:args.location}``.
            headers: Optional HTTP headers, sent as written. The platform
                doesn't expand templates in header values.
            form_param: Send the JSON params as one form field with this name.
            input_args_as_params: Merge the function's arguments into params,
                which makes the request a POST. Defaults to False.
            require_args: Skip this webhook, without a request, unless at
                least one of these arguments is present.

        Returns:
            This DataMap, for chaining.

        Example:
            ```python
            weather = (
                DataMap("get_weather")
                .purpose("Get current weather for a city")
                .parameter("city", "string", "City name", required=True)
                .webhook(
                    "GET",
                    "https://api.weatherapi.com/v1/current.json"
                    "?key=YOUR_API_KEY&q=${enc:args.city}",
                    headers={"Accept": "application/json"},
                )
                .output(FunctionResult("Weather: ${current.condition.text}"))
            )
            ```
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
        """Add expressions that run after the most recent webhook completes.

        They give conditional output based on the API response. They run
        after the webhook's foreach, against its response, and the first one
        that produces an output replaces the webhook's own output.
        Their templates read the response's fields from the root, and the
        call data under ``input``, such as ``${input.args.query}``.

        Args:
            expressions: List of expression definitions to check against the
                webhook response. Each is a dict with ``string``, ``pattern``
                and ``output`` keys, and an optional ``nomatch-output``.

        Returns:
            This DataMap, for chaining.

        Raises:
            ValueError: If no webhook has been added yet.

        Example:
            ```python
            status = (
                DataMap("check_status")
                .purpose("Check service status")
                .parameter("service", "string", "Service name", required=True)
                .webhook("GET", "https://api.example.com/status/${enc:args.service}")
                .webhook_expressions(
                    [
                        {
                            "string": "${status}",
                            "pattern": "healthy",
                            "output": {
                                "response": "${input.args.service} is running."
                            },
                        },
                        {
                            "string": "${status}",
                            "pattern": "degraded|down",
                            "output": {
                                "response": "${input.args.service} has issues."
                            },
                        },
                    ]
                )
            )
            ```
        """
        if not self._webhooks:
            raise ValueError("Must add webhook before setting webhook expressions")

        self._webhooks[-1]["expressions"] = expressions
        return self

    def body(self, data: dict[str, Any]) -> "DataMap":
        """Set the JSON request body for the last added webhook (same as `params`).

        The platform reads a webhook's body from its ``params`` field, and
        has no ``body`` field, so this sets ``params``. See `params()`.

        Args:
            data: Request body data. It can include ``${variable}``
                substitutions.

        Returns:
            This DataMap, for chaining.

        Raises:
            ValueError: If no webhook has been added yet.

        Example:
            ```python
            search = (
                DataMap("search_docs")
                .parameter("query", "string", "Search query", required=True)
                .webhook("POST", "https://api.docs.example.com/search")
                .body({"query": "${args.query}", "limit": 3})
            )
            ```
        """
        if not self._webhooks:
            raise ValueError("Must add webhook before setting body")

        self._webhooks[-1]["params"] = data
        return self

    def params(self, data: dict[str, Any]) -> "DataMap":
        """Set the JSON request body for the last added webhook.

        The platform sends ``params`` as the request's JSON body, not as URL
        query parameters, so a webhook with params is sent as a POST whatever
        its method. Put query parameters in the URL instead. Templates in the
        values are expanded against the call data, such as ``${args.query}``.

        Args:
            data: Request params data. It can include ``${variable}``
                substitutions.

        Returns:
            This DataMap, for chaining.

        Raises:
            ValueError: If no webhook has been added yet.

        Example:
            ```python
            search = (
                DataMap("search_docs")
                .parameter("query", "string", "Search query", required=True)
                .webhook("POST", "https://api.docs.example.com/search")
                .params({"q": "${args.query}", "limit": 10})
            )
            ```
        """
        if not self._webhooks:
            raise ValueError("Must add webhook before setting params")

        self._webhooks[-1]["params"] = data
        return self

    def foreach(self, foreach_config: dict[str, Any]) -> "DataMap":
        """Process an array from the webhook response, one item at a time.

        It builds a formatted string from each element.

        The platform runs the foreach before the webhook's expressions and
        output, and stores the text it builds under ``output_key``, so the
        output reads it as ``${formatted_results}``.

        Args:
            foreach_config: Foreach configuration, a dict with these keys:

                - ``input_key``: Path to the array in the API response, such
                  as ``results`` or ``data.items``.
                - ``output_key``: Name for the built string variable.
                - ``max``: Maximum number of items to process (optional).
                - ``append``: Template string to append for each item, where
                  ``${this}`` is the current item and ``${this.title}``
                  its field; the rest of the response stays readable.

        Returns:
            This DataMap, for chaining.

        Raises:
            ValueError: If no webhook has been added yet, if
                ``foreach_config`` isn't a dict, or if it lacks any of
                ``input_key``, ``output_key`` and ``append``.

        Example:
            ```python
            search = (
                DataMap("search_docs")
                .parameter("query", "string", "Search query", required=True)
                .webhook("POST", "https://api.docs.example.com/search")
                .params({"query": "${args.query}", "limit": 3})
                .foreach(
                    {
                        "input_key": "results",
                        "output_key": "formatted_results",
                        "max": 3,
                        "append": "- ${this.title}: ${this.summary}\\n",
                    }
                )
                .output(FunctionResult("Found:\\n${formatted_results}"))
            )
            ```
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
        """Set the output result for the most recent webhook.

        Always set a `fallback_output` too, so the AI has something to say
        when the API is unavailable.

        Its templates read the webhook's JSON response: an object's fields
        from the root, such as ``${current.temp_f}``, or ``${array[0].x}``
        for an array. The call data is under ``input``, so an argument is
        ``${input.args.location}``; ``${args.location}`` is empty here.

        Args:
            result: `FunctionResult` defining the response for this webhook.

        Returns:
            This DataMap, for chaining.

        Raises:
            ValueError: If no webhook has been added yet.

        Example:
            ```python
            weather = (
                DataMap("get_weather")
                .webhook("GET", "https://api.weather.com/v1/current")
                .output(FunctionResult("The weather is ${current.condition.text}."))
            )
            ```
        """
        if not self._webhooks:
            raise ValueError("Must add webhook before setting output")

        self._webhooks[-1]["output"] = result.to_dict()
        return self

    def fallback_output(self, result: FunctionResult) -> "DataMap":
        """Set a fallback output result at the top level.

        The platform uses it when no top-level expression produced an output
        and the webhook stage produced no result: the webhook it requested
        failed, or no webhook was eligible. It doesn't try a later webhook
        first. Its templates read the call data, so an argument is
        ``${args.location}``.

        Args:
            result: `FunctionResult` defining the fallback response.

        Returns:
            This DataMap, for chaining.

        Example:
            ```python
            weather = (
                DataMap("get_weather")
                .webhook("GET", "https://api.weather.com/v1/current?q=${enc:args.city}")
                .output(FunctionResult("Weather: ${current.condition.text}"))
                .fallback_output(FunctionResult("The weather service is down."))
            )
            ```
        """
        self._output = result.to_dict()
        return self

    def error_keys(self, keys: list[str]) -> "DataMap":
        """Set error keys for the most recent webhook, or top-level if none exists.

        If any of these keys appear in the API response, the response is
        treated as an error. To always set keys at the top level, use
        `global_error_keys()`.

        The webhook fails when its JSON response has any of these keys at the
        top level, whatever the value, even ``false`` or ``null``. An HTTP
        status outside 200-299 isn't a failure by itself: the platform adds
        an ``http_code`` key to such a response, so ``"http_code"`` in this
        list fails the webhook on any such status. The platform reads error
        keys only on a webhook; called before any webhook, this sets a
        top-level ``error_keys`` field, which the platform ignores.

        Args:
            keys: List of JSON keys whose presence indicates an error.

        Returns:
            This DataMap, for chaining.

        Example:
            ```python
            api = (
                DataMap("api_call")
                .webhook("GET", "https://api.example.com/data")
                .error_keys(["error", "error_message"])
            )
            ```
        """
        if self._webhooks:
            # Add to most recent webhook
            self._webhooks[-1]["error_keys"] = keys
        else:
            # Store as top-level error keys
            self._error_keys = keys
        return self

    def global_error_keys(self, keys: list[str]) -> "DataMap":
        """Set top-level error keys.

        This sets them at the top-level data_map scope, whatever webhooks
        exist.

        The platform ignores a top-level ``error_keys`` field: it checks only
        each webhook's own. Call ``error_keys()`` after the webhook instead.

        Args:
            keys: List of JSON keys whose presence indicates an error.

        Returns:
            This DataMap, for chaining.
        """
        self._error_keys = keys
        return self

    def gate(self, gate: SemanticGate | dict[str, Any]) -> "DataMap":
        """Add a semantic gate, a precondition checked before the function runs.

        A semantic gate is a yes/no question that a decision model answers
        about the call right before the platform runs this function.

        Every gate must pass for the function to run. When one doesn't, the
        data_map doesn't run, and the model gets that gate's ``on_fail``
        output. Call once per gate, up to 8; gates are checked when the
        function is built, by the platform's rules: `to_swaig_function()`
        raises ``ValueError`` for any gate the platform would refuse. To set
        what the AI says during the check, use `gate_fillers()`.

        Args:
            gate: A `SemanticGate`, or a gate dict in the platform's shape
                (``question``, ``threshold``, ``on_fail``, and optional
                ``id``, ``criteria`` and ``visual_input``).

        Returns:
            This DataMap, for chaining.

        Example:
            ```python
            from signalwire import DataMap, FunctionResult, SemanticGate

            cancel_order = (
                DataMap("cancel_order")
                .purpose("Cancel one of the caller's open orders")
                .parameter("order_id", "string", "The order number", required=True)
                .gate(
                    SemanticGate(
                        "Has the caller asked to cancel the order?",
                        threshold=0.9,
                        on_fail="Not run. Ask which order to cancel.",
                    )
                )
                .webhook("POST", "https://api.example.com/orders/${enc:args.order_id}")
                .output(FunctionResult("The order is cancelled. Tell the caller."))
            )
            ```
        """
        self._gates.append(gate)
        return self

    def gate_fillers(self, fillers: FillerPhrases) -> "DataMap":
        """Set what the AI says while this function's gates are checked.

        Shaped like a function's fillers: phrases keyed by language code,
        "auto" or "default". Without them, the function's own fillers start
        when the model calls it, before the gates decide. Only for a function
        with gates:
        `to_swaig_function()` raises ``ValueError`` when gate fillers are set
        and no `gate()` was added.

        Args:
            fillers: Phrases keyed by language code (``"en-US"``), ``"auto"``
                or ``"default"``. Each entry is a phrase, or a list of
                phrases spoken one at a time while the call waits.

        Returns:
            This DataMap, for chaining.

        Example:
            ```python
            dm.gate_fillers({"en-US": ["Let me check that.", "One moment."]})
            ```
        """
        self._gate_fillers = fillers
        return self

    def to_swaig_function(self) -> dict[str, Any]:
        """Convert this DataMap to a SWAIG function definition.

        Register the result with the agent using `register_swaig_function()`.

        Returns:
            A dict with the function name, description, parameter schema and
            ``data_map`` configuration (instead of a webhook URL).

        Raises:
            ValueError: For gates the platform would refuse, or gate fillers
                without gates.

        Example:
            ```python
            weather = (
                DataMap("get_weather")
                .parameter("city", "string", "City name", required=True)
                .webhook("GET", "https://api.example.com/w?q=${enc:args.city}")
                .output(FunctionResult("Weather: ${current.condition.text}"))
            )
            agent.register_swaig_function(weather.to_swaig_function())
            ```
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
        apply_gate_fields(function, self.function_name, definition=True)
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
    """Create a simple API tool with minimal configuration.

    It builds a `DataMap` for a single-endpoint API call.

    Args:
        name: Function name.
        url: API endpoint URL. Templates read the arguments as ``${args.x}``.
        response_template: Template for formatting the response. It reads the
            response's fields from the root, such as ``${current.temp_f}``, and
            the arguments as ``${input.args.x}``.
        parameters: Optional parameter definitions. Keys are parameter names,
            and values are dicts with ``"type"``, ``"description"`` and an
            optional ``"required"`` key.
        method: HTTP method (default: GET). A webhook with a body is sent as a
            POST.
        headers: Optional HTTP headers, sent as written.
        body: Optional JSON request body, set as the webhook's params.
        error_keys: Optional list of error indicator keys.

    Returns:
        The configured `DataMap`, ready for more chaining or conversion.

    Example:
        ```python
        from signalwire import create_simple_api_tool

        weather = create_simple_api_tool(
            name="get_weather",
            url="https://api.weatherapi.com/v1/current.json?q=${enc:args.city}",
            response_template="Weather in ${input.args.city}: "
            "${current.condition.text}",
            parameters={
                "city": {
                    "type": "string",
                    "description": "City name",
                    "required": True,
                }
            },
            error_keys=["error"],
        )
        agent.register_swaig_function(weather.to_swaig_function())
        ```
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
    """Create an expression-based tool for pattern matching responses.

    It builds a `DataMap` that answers without an API call.

    Args:
        name: Function name.
        patterns: Dict mapping test values to ``(pattern, FunctionResult)``
            tuples.
        parameters: Optional parameter definitions, in the same format as
            `create_simple_api_tool()`.

    Returns:
        The configured `DataMap`.

    Example:
        ```python
        from signalwire import FunctionResult, create_expression_tool

        greeting = create_expression_tool(
            name="greet",
            patterns={
                "${args.language}": (r"spanish|espanol", FunctionResult("Hola!")),
            },
            parameters={
                "language": {"type": "string", "description": "Language"}
            },
        )
        ```
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
