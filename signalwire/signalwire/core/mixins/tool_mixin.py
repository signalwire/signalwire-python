"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from typing import TYPE_CHECKING, Any
from collections.abc import Awaitable, Callable, Sequence
import inspect
import json
import logging

from signalwire.core.swaig_function import SWAIGFunction, _resolve_awaitable
from signalwire.core.function_result import (
    FunctionResult,
    ToolRefusal,
    settle_result,
    tool_error_result,
)
from signalwire.core.semantic_gate import FillerPhrases, SemanticGate
from signalwire.core.tool_middleware import ResendDedupe, ToolMiddleware, run_chain
from signalwire.core.agent.tools.decorator import ToolDecorator
from signalwire.core.mixins._mixin_host import _HostTyped

if TYPE_CHECKING:
    from signalwire.core.agent_base import AgentBase  # type: ignore[attr-defined]  # cycle: agent_base imports the mixins; the name resolves at type-check time but mypy flags the back-reference

_tool_mixin_logger = logging.getLogger(__name__)

#: The web_hook_url that has the platform run its own implementation of a
#: function, by name
NATIVE_WEBHOOK_URL = "native"


async def _complete_async_call(name: str, pending: Awaitable[Any]) -> Any:
    """Await an async handler, and shape its outcome like a synchronous call's."""
    try:
        return settle_result(name, await pending)
    except ToolRefusal as declined:
        return declined.result()
    except Exception:
        _tool_mixin_logger.exception(f"SWAIG function '{name}' raised")
        return tool_error_result(name)


class ToolMixin(_HostTyped):  # type: ignore[misc]  # _HostTyped is object at runtime; AgentBase under TYPE_CHECKING — intentional split
    """
    Mixin class containing all tool/function-related methods for AgentBase
    """

    def define_tool(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable[..., Any],
        secure: bool = True,
        fillers: dict[str, list[str]] | None = None,
        webhook_url: str | None = None,
        required: list[str] | None = None,
        is_typed_handler: bool = False,
        gates: Sequence[SemanticGate | dict[str, Any]] | None = None,
        gate_fillers: FillerPhrases | None = None,
        vouched: bool = False,
        nullable_optional: bool | None = None,
        middleware: Sequence[ToolMiddleware] | None = None,
        needs_conversation: bool = False,
        **swaig_fields: Any,
    ) -> "AgentBase":
        """
        Define a SWAIG function the AI can call.

        How this becomes a tool the model sees
        --------------------------------------
        SWAIG functions are NOT a separate concept from "LLM tools" — they
        ARE the tools, exposed to the model in exactly the same shape as
        native OpenAI / Anthropic tool calling. Under the hood, the SDK
        renders each SWAIG function into an OpenAI-format tool schema:

            {"type": "function", "function": {
                "name":        "<your name>",
                "description": "<your description>",
                "parameters":  {<your JSON schema>}
            }}

        That schema is sent to the model on every turn. The model reads
        the `description` field and the per-parameter `description`
        strings inside `parameters` to decide WHEN to call this tool and
        HOW to fill in the arguments.

        Treat description text as prompt engineering, not as developer
        documentation:

          - Bad:  "Lookup function"
          - Bad:  "Internal helper for account fetching"
          - Good: "Look up a customer's account details by their account
                  number. Use this BEFORE quoting any account-specific
                  information (balance, plan, status, billing date)."

          - Bad parameter:  "the id"
          - Good parameter: "The customer's account number, exactly 8
                           digits, no dashes or spaces. Ask the user if
                           they don't provide it."

        Vague descriptions are the #1 cause of "the model has the right
        tool but doesn't call it" failures. Be specific about WHEN to
        use the tool, what makes it the right choice over alternatives,
        and any preconditions on the arguments.

        Tool count matters too: LLM tool selection accuracy degrades past
        ~7-8 simultaneously-active tools per call. If you have many tools,
        partition them across steps using Step.set_functions() so only
        the relevant subset is active at any moment.

        Args:
            name: Function name. Must be unique across all SWAIG functions
                on this agent. Becomes the `name` field in the OpenAI tool
                schema and is what the model emits when it picks this tool.
                Use snake_case; the model picks up naming conventions from
                this field too.
            description: The function description as the LLM will read it.
                See above — this is prompt-engineered text, not internal
                docs. Explain what the tool does, when to use it, and what
                NOT to use it for if there are sibling tools the model
                might confuse it with.
            parameters: JSON Schema for the function's arguments. The
                per-property `description` fields inside the schema are
                also LLM-facing — give every parameter a description that
                tells the model how to fill it in (format, source,
                constraints).
            handler: Python callable invoked when the model calls this
                tool. Receives parsed args and the raw request data.
                Should return a FunctionResult or dict; anything else
                logs a warning and is stringified.
            secure: Whether to require SWAIG token validation on the
                webhook callback.
            fillers: Optional phrases the AI says while the function runs,
                keyed by language code, "auto" (translated into the call's
                language on first use) or "default". An entry may be a list
                of phrases, a wait script, spoken one at a time while the call
                waits; the annotation predates wait scripts, so a type
                checker needs a cast for one. Format: {"en-US": ["one moment...", "checking..."]}
            webhook_url: Optional external webhook URL. If set, the SDK
                does not handle the call locally — the model's tool call
                is forwarded to this URL.
            required: Optional list of required parameter names. May also
                be set inside `parameters["required"]`.
            is_typed_handler: Whether the handler uses type-hinted
                parameters (auto-wrapped from inferred schema).
            gates: Optional semantic gates, 1 to 8 SemanticGate objects or
                gate dicts: yes/no preconditions a decision model checks
                right before the platform dispatches the function. When one
                fails, the function doesn't run and the model gets that
                gate's on_fail output. The fillers and wait_file start only
                once the gates pass.
            gate_fillers: Optional phrases the AI says while the gates are
                checked, shaped like ``fillers``. Only with ``gates``.
            vouched: True for a tool whose arguments must come from the
                user, not from the model's guesses. The tool gets a required
                boolean argument, ``data_supplied_by_user``, in which the
                model says they did. Unless it's true, the handler doesn't
                run, and the model gets "<name> was not run." with the tool
                prompt "Get the answer from the user before using this
                tool." The handler never sees the argument.
            nullable_optional: True to let the model send null for an
                optional argument, as providers with strict schemas require:
                each argument that isn't required takes null as well as its
                type, and a null reaches the handler as an argument not
                given. None (default) follows
                ``set_nullable_optional_parameters()``.
            middleware: Middleware that runs around this tool's calls only,
                inside the agent's (``add_tool_middleware``).
            needs_conversation: True when the handler reads the
                conversation, as ``caller_turns(raw_data)`` does. It turns
                on the agent's ``swaig_post_conversation`` when the SWML is
                rendered, so every tool request carries the call log, unless
                it was set to False.
            **swaig_fields: Additional SWAIG-only fields (e.g.
                meta_data_token, web_hook_auth_user) included in the
                generated function definition.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: For gates the platform would refuse, or gate_fillers
                without gates.

        Example:
            agent.define_tool(
                name="lookup_account",
                description=(
                    "Look up a customer's account details by their account "
                    "number. Use this BEFORE quoting any account-specific "
                    "information. Do not call it for general questions about "
                    "the product."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "account_number": {
                            "type": "string",
                            "description": (
                                "The customer's 8-digit account number, "
                                "no dashes. Ask the user if not provided."
                            ),
                        }
                    },
                    "required": ["account_number"],
                },
                handler=self.handle_lookup_account,
            )
        """
        if gates is not None:
            swaig_fields["gates"] = gates
        if gate_fillers is not None:
            swaig_fields["gate_fillers"] = gate_fillers
        if vouched:
            swaig_fields["vouched"] = True
        if nullable_optional is not None:
            swaig_fields["nullable_optional"] = nullable_optional
        if middleware:
            swaig_fields["middleware"] = middleware
        if needs_conversation:
            swaig_fields["needs_conversation"] = True
        self._tool_registry.define_tool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
            secure=secure,
            fillers=fillers,
            webhook_url=webhook_url,
            required=required,
            is_typed_handler=is_typed_handler,
            **swaig_fields,
        )
        return self

    def define_native_tool(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any] | None = None,
        **swaig_fields: Any,
    ) -> "AgentBase":
        """
        Define a function the platform implements itself, under your own
        description and parameters.

        The platform runs its own implementation of a function whose
        ``web_hook_url`` is "native", by name, and never calls a webhook.
        A tool defined with ``define_tool`` gets the agent's webhook URL, so
        it can't be one. Use this to describe a function the platform
        implements, such as ``end_call``, in your own words, or to put it
        in a step's function list.

        Args:
            name: The function's name, one the platform implements.
            description: The description the model reads.
            parameters: The JSON schema of its arguments, as the platform's
                implementation reads them. Default: none.
            **swaig_fields: Other SWAIG fields, such as fillers.

        Returns:
            Self for method chaining
        """
        definition: dict[str, Any] = {
            "function": name,
            "description": description,
            "parameters": parameters or {"type": "object", "properties": {}},
            **swaig_fields,
            "web_hook_url": NATIVE_WEBHOOK_URL,
        }
        return self.register_swaig_function(definition)

    def set_nullable_optional_parameters(self, enabled: bool = True) -> "AgentBase":
        """
        Let the model send null for any tool's optional arguments.

        Some providers' strict schemas make every argument required and
        refuse a call that leaves one out, so an optional argument has to
        take null instead. With this on, each optional argument of every
        tool defined with ``define_tool`` takes null as well as its type, and
        a null reaches the handler as an argument not given. A tool's own
        ``nullable_optional`` overrides it. It applies when the SWML is
        rendered, so it covers tools defined before or after it.

        Args:
            enabled: True to turn it on, False to turn it off.

        Returns:
            Self for method chaining
        """
        self._nullable_optional_parameters = enabled
        return self

    def _nullable_optional_default(self) -> bool:
        return bool(getattr(self, "_nullable_optional_parameters", False))

    def register_swaig_function(self, function_dict: dict[str, Any]) -> "AgentBase":
        """
        Register a raw SWAIG function dictionary (e.g., from DataMap.to_swaig_function())

        Args:
            function_dict: Complete SWAIG function definition dictionary

        Returns:
            Self for method chaining
        """
        self._tool_registry.register_swaig_function(function_dict)
        return self

    def _tool_decorator(
        self, name: str | None = None, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator for defining SWAIG tools in a class

        Used as:

        @agent.tool(name="example_function", parameters={...})
        def example_function(self, param1):
            # ...
        """
        # ToolDecorator.create_instance_decorator is untyped (cross-file:
        # core/agent/tools/decorator.py); the call returns Any.
        return ToolDecorator.create_instance_decorator(self._tool_registry)(
            name, **kwargs
        )

    @classmethod
    def tool(
        cls, name: str | None = None, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Class method decorator for defining SWAIG tools

        Used as:

        @AgentBase.tool(name="example_function", parameters={...})
        def example_function(self, param1):
            # ...
        """
        # ToolDecorator.create_class_decorator is untyped (cross-file:
        # core/agent/tools/decorator.py); the call returns Any.
        return ToolDecorator.create_class_decorator()(name, **kwargs)

    def define_tools(self) -> list[SWAIGFunction | dict[str, Any]]:
        """
        Define the tools this agent can use

        Returns:
            List of SWAIGFunction objects or raw dictionaries (for data_map tools)

        This method can be overridden by subclasses.
        """
        tools: list[SWAIGFunction | dict[str, Any]] = []
        for func in self._tool_registry._swaig_functions.values():
            if isinstance(func, dict):
                # Raw dictionary from register_swaig_function (e.g., DataMap)
                tools.append(func)
            else:
                # SWAIGFunction object from define_tool
                tools.append(func)
        return tools

    def on_function_call(
        self, name: str, args: dict[str, Any], raw_data: dict[str, Any] | None = None
    ) -> Any:
        """
        Called when a SWAIG function is invoked

        Args:
            name: Function name
            args: Function arguments
            raw_data: Raw request data

        Returns:
            Function result
        """
        # Check if the function is registered
        if name not in self._tool_registry._swaig_functions:
            # If the function is not found, return an error
            return {"response": f"Function '{name}' not found"}

        # Get the function
        func = self._tool_registry._swaig_functions[name]

        # Check if this is a data_map function (raw dictionary)
        if isinstance(func, dict):
            # Data_map functions execute on SignalWire's server, not here
            # This should never be called, but if it is, return an error
            return {
                "response": f"Data map function '{name}' should be executed by SignalWire server, not locally"
            }

        # Check if this is an external webhook function
        if hasattr(func, "webhook_url") and func.webhook_url:
            # External webhook functions should be called directly by SignalWire, not locally
            return {
                "response": f"External webhook function '{name}' should be executed by SignalWire at {func.webhook_url}, not locally"
            }

        # Validate arguments against the parameter schema (soft validation - warn but proceed)
        if hasattr(func, "validate_args") and args:
            try:
                is_valid, errors = func.validate_args(
                    args, self._nullable_optional_default()
                )
                if not is_valid:
                    _tool_mixin_logger.warning(
                        f"Argument validation failed for function '{name}': {'; '.join(errors)}"
                    )
            except Exception as e:
                _tool_mixin_logger.debug(
                    f"Argument validation error for function '{name}': {e}"
                )

        nullable_default = self._nullable_optional_default()

        def dispatch(args: dict[str, Any], raw_data: dict[str, Any]) -> Any:
            # A vouched tool runs only when the model vouches for its arguments
            refusal = func._vouched_refusal(args)
            if refusal is not None:
                return refusal

            # Call the handler for regular SWAIG functions
            try:
                result = func.handler(
                    func._handler_args(args, nullable_default), raw_data
                )
                if inspect.isawaitable(result):
                    # An async def handler. Return an awaitable, so the caller can
                    # run it on its own event loop: the /swaig endpoint awaits it,
                    # and synchronous callers pass it to _resolve_awaitable().
                    return _complete_async_call(name, result)
                return settle_result(name, result)
            except ToolRefusal as declined:
                return declined.result()
            except Exception:
                # Logged, not sent: the text can hold internals, and the model
                # would read it as the outcome
                _tool_mixin_logger.exception(f"SWAIG function '{name}' raised")
                return tool_error_result(name)

        middleware = self._tool_middleware_for(func)
        if not middleware:
            return dispatch(args, raw_data or {})
        try:
            outcome = run_chain(middleware, name, args, raw_data or {}, dispatch)
        except ToolRefusal as declined:
            return declined.result()
        except Exception:
            _tool_mixin_logger.exception(f"Tool middleware for '{name}' raised")
            return tool_error_result(name)
        if inspect.isawaitable(outcome):
            return _complete_async_call(name, outcome)
        return settle_result(name, outcome)

    def _tool_middleware_for(self, func: SWAIGFunction) -> list[Any]:
        """The middleware around a call of ``func``, outermost first: the
        resend dedupe, the agent's, then the tool's own."""
        chain: list[Any] = []
        dedupe = getattr(self, "_tool_resend_dedupe", None)
        if dedupe is not None:
            chain.append(dedupe)
        chain.extend(getattr(self, "_tool_middleware", ()))
        chain.extend(getattr(func, "middleware", ()))
        return chain

    def add_tool_middleware(self, middleware: ToolMiddleware) -> "AgentBase":
        """
        Run ``middleware`` around every tool call, after any added before it.

        A middleware is ``fn(name, args, raw_data, call_next)``. It runs before
        the handler and calls ``call_next(args, raw_data)`` for the rest of the
        chain and the handler, possibly with changed arguments. What it
        returns is the call's result: the handler's, a changed one, or its own
        without calling ``call_next``, as a ``FunctionResult`` or a dict. For
        an ``async def`` handler ``call_next`` returns an awaitable; an
        ``async def`` middleware can ``await resolve(call_next(...))``
        (``signalwire.core.tool_middleware.resolve``) to take either. One that
        raises ``ToolRefusal`` declines the call, and any other exception
        gives the model the unknown-outcome result.

        It covers tools defined with ``define_tool``, not DataMap or native
        tools, which run on the platform. Synchronous handlers for different
        calls run at once in worker threads, so guard shared state.

        Args:
            middleware: The middleware.

        Returns:
            Self for method chaining

        Example:
            def log_calls(name, args, raw_data, call_next):
                started = time.monotonic()
                result = call_next(args, raw_data)
                log.info("tool", name=name, ms=(time.monotonic() - started) * 1000)
                return result

            agent.add_tool_middleware(log_calls)
        """
        self._tool_middleware.append(middleware)
        return self

    def set_tool_resend_dedupe(self, enabled: bool = True) -> "AgentBase":
        """
        Turn the dedupe of transport retries on or off. It's on by default.

        SignalWire sends a tool request again, with the same body, after a
        timeout, a failed connection or a 5xx, so a slow tool can run twice.
        The dedupe answers a retry with the first attempt's result: one that
        arrives while the first is still running waits for it. A retry is a
        call with the same ``call_id``, ``tool_call_id`` and function name; a
        call the model makes again has a new ``tool_call_id`` and runs, and a
        call without one always runs. The record is kept in this process, so
        with several processes or replicas a retry that reaches another one
        runs the tool again.

        Args:
            enabled: False to run every request, retries included.

        Returns:
            Self for method chaining
        """
        if not enabled:
            self._tool_resend_dedupe = None
        elif getattr(self, "_tool_resend_dedupe", None) is None:
            self._tool_resend_dedupe = ResendDedupe()
        return self

    def _execute_swaig_function(
        self,
        function_name: str,
        args: dict[str, Any] | None = None,
        call_id: str | None = None,
        raw_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a SWAIG function in serverless context

        Args:
            function_name: Name of the function to execute
            args: Function arguments dictionary
            call_id: Optional call ID
            raw_data: Optional raw request data

        Returns:
            Function execution result
        """
        # Use the existing logger
        req_log = self.log.bind(endpoint="serverless_swaig", function=function_name)

        if call_id:
            req_log = req_log.bind(call_id=call_id)

        req_log.debug("serverless_function_call_received")

        try:
            # Validate function exists
            if function_name not in self._tool_registry._swaig_functions:
                req_log.warning(
                    "function_not_found",
                    available_functions=list(
                        self._tool_registry._swaig_functions.keys()
                    ),
                )
                return {"error": f"Function '{function_name}' not found"}

            # Use empty args if not provided
            if args is None:
                args = {}

            # Use empty raw_data if not provided, but include function call structure
            if raw_data is None:
                raw_data = {
                    "function": function_name,
                    "argument": {
                        "parsed": [args] if args else [],
                        "raw": json.dumps(args) if args else "{}",
                    },
                }
                if call_id:
                    raw_data["call_id"] = call_id

            req_log.debug("executing_function", args=json.dumps(args))

            # Call the function using the existing on_function_call method,
            # running an async handler to completion
            result = _resolve_awaitable(
                self.on_function_call(function_name, args, raw_data)
            )

            # Convert result to dict if needed (same logic as in _handle_swaig_request)
            if isinstance(result, FunctionResult):
                result_dict = result.to_dict()
            elif isinstance(result, dict):
                result_dict = result
            else:
                req_log.warning(
                    "unexpected_function_result_type",
                    function=function_name,
                    result_type=type(result).__name__,
                    hint=(
                        "SWAIG function returned a value that is neither "
                        "FunctionResult nor dict; falling back to str(result). "
                        "The AI will see the stringified value as its tool "
                        "response. Wrap your return in FunctionResult(...) or "
                        "return a dict with at least a 'response' key."
                    ),
                )
                result_dict = {"response": str(result)}

            req_log.info("serverless_function_executed_successfully")
            req_log.debug("function_result", result=json.dumps(result_dict))
            return result_dict

        except Exception as e:
            req_log.error("serverless_function_execution_error", error=str(e))
            return {"error": str(e), "function": function_name}
