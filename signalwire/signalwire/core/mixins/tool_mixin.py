"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from typing import Dict, Any, List, Optional, Callable
import json
import logging

from signalwire.core.swaig_function import SWAIGFunction
from signalwire.core.function_result import FunctionResult
from signalwire.core.agent.tools.decorator import ToolDecorator

_tool_mixin_logger = logging.getLogger(__name__)


class ToolMixin:
    """
    Mixin class containing all tool/function-related methods for AgentBase
    """
    
    def define_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable,
        secure: bool = True,
        fillers: Optional[Dict[str, List[str]]] = None,
        webhook_url: Optional[str] = None,
        required: Optional[List[str]] = None,
        is_typed_handler: bool = False,
        **swaig_fields
    ) -> 'AgentBase':
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
            fillers: Optional dict mapping language codes to arrays of
                filler phrases the AI speaks while the function executes.
                Format: {"en-US": ["one moment...", "checking..."]}
            webhook_url: Optional external webhook URL. If set, the SDK
                does not handle the call locally — the model's tool call
                is forwarded to this URL.
            required: Optional list of required parameter names. May also
                be set inside `parameters["required"]`.
            is_typed_handler: Whether the handler uses type-hinted
                parameters (auto-wrapped from inferred schema).
            **swaig_fields: Additional SWAIG-only fields (e.g.
                meta_data_token, web_hook_auth_user) included in the
                generated function definition.

        Returns:
            Self for method chaining.

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
            **swaig_fields
        )
        return self
    
    def register_swaig_function(self, function_dict: Dict[str, Any]) -> 'AgentBase':
        """
        Register a raw SWAIG function dictionary (e.g., from DataMap.to_swaig_function())
        
        Args:
            function_dict: Complete SWAIG function definition dictionary
            
        Returns:
            Self for method chaining
        """
        self._tool_registry.register_swaig_function(function_dict)
        return self
    
    def _tool_decorator(self, name=None, **kwargs):
        """
        Decorator for defining SWAIG tools in a class
        
        Used as:
        
        @agent.tool(name="example_function", parameters={...})
        def example_function(self, param1):
            # ...
        """
        return ToolDecorator.create_instance_decorator(self._tool_registry)(name, **kwargs)
    
    @classmethod
    def tool(cls, name=None, **kwargs):
        """
        Class method decorator for defining SWAIG tools
        
        Used as:
        
        @AgentBase.tool(name="example_function", parameters={...})
        def example_function(self, param1):
            # ...
        """
        return ToolDecorator.create_class_decorator()(name, **kwargs)
    
    def define_tools(self) -> List[SWAIGFunction]:
        """
        Define the tools this agent can use
        
        Returns:
            List of SWAIGFunction objects or raw dictionaries (for data_map tools)
            
        This method can be overridden by subclasses.
        """
        tools = []
        for func in self._tool_registry._swaig_functions.values():
            if isinstance(func, dict):
                # Raw dictionary from register_swaig_function (e.g., DataMap)
                tools.append(func)
            else:
                # SWAIGFunction object from define_tool
                tools.append(func)
        return tools
    
    def on_function_call(self, name: str, args: Dict[str, Any], raw_data: Optional[Dict[str, Any]] = None) -> Any:
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
            return {"response": f"Data map function '{name}' should be executed by SignalWire server, not locally"}
        
        # Check if this is an external webhook function
        if hasattr(func, 'webhook_url') and func.webhook_url:
            # External webhook functions should be called directly by SignalWire, not locally
            return {"response": f"External webhook function '{name}' should be executed by SignalWire at {func.webhook_url}, not locally"}

        # Validate arguments against the parameter schema (soft validation - warn but proceed)
        if hasattr(func, 'validate_args') and args:
            try:
                is_valid, errors = func.validate_args(args)
                if not is_valid:
                    _tool_mixin_logger.warning(
                        f"Argument validation failed for function '{name}': {'; '.join(errors)}"
                    )
            except Exception as e:
                _tool_mixin_logger.debug(f"Argument validation error for function '{name}': {e}")

        # Call the handler for regular SWAIG functions
        try:
            result = func.handler(args, raw_data)
            if result is None:
                # If the handler returns None, create a default response
                result = FunctionResult("Function executed successfully")
            return result
        except Exception as e:
            # If the handler raises an exception, return an error response
            return {"response": f"Error executing function '{name}': {str(e)}"}
    
    
    def _execute_swaig_function(self, function_name: str, args: Optional[Dict[str, Any]] = None, call_id: Optional[str] = None, raw_data: Optional[Dict[str, Any]] = None):
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
        req_log = self.log.bind(
            endpoint="serverless_swaig",
            function=function_name
        )
        
        if call_id:
            req_log = req_log.bind(call_id=call_id)
            
        req_log.debug("serverless_function_call_received")
        
        try:
            # Validate function exists
            if function_name not in self._tool_registry._swaig_functions:
                req_log.warning("function_not_found", available_functions=list(self._tool_registry._swaig_functions.keys()))
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
                        "raw": json.dumps(args) if args else "{}"
                    }
                }
                if call_id:
                    raw_data["call_id"] = call_id
            
            req_log.debug("executing_function", args=json.dumps(args))
            
            # Call the function using the existing on_function_call method
            result = self.on_function_call(function_name, args, raw_data)

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