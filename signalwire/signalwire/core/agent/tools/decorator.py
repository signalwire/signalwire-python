"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""Tool decorator functionality."""

from functools import wraps
from typing import Callable, Optional, Dict, Any

from signalwire.core.logging_config import get_logger

logger = get_logger(__name__)


class ToolDecorator:
    """Handles tool decoration logic."""
    
    @staticmethod
    def create_instance_decorator(registry):
        """
        Create instance tool decorator.

        Args:
            registry: ToolRegistry instance to register with

        Returns:
            Decorator function
        """
        def decorator(name=None, **kwargs):
            """
            Decorator for defining SWAIG tools in a class.

            A SWAIG tool is exactly the same concept as an OpenAI/Anthropic
            tool: the function's name, description, and parameter schema
            are sent to the model on every turn, and the model decides
            when to call it based on those fields. The `description`
            kwarg (or the function's docstring as a fallback) and the
            per-parameter description strings inside `parameters` are
            ALL read by the LLM — they are prompt engineering, not just
            developer notes.

            Used as:

                @agent.tool(
                    name="lookup_account",
                    description=(
                        "Look up a customer's account by account number. "
                        "Use this BEFORE quoting any account-specific info. "
                        "Don't use it for general product questions."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {
                            "account_number": {
                                "type": "string",
                                "description": (
                                    "The customer's 8-digit account number, "
                                    "no dashes."
                                ),
                            }
                        },
                        "required": ["account_number"],
                    },
                )
                def lookup_account(self, args, raw_data):
                    ...

            If you omit `description`, the function's docstring is used —
            so write the docstring with the model in mind, not just other
            developers. If you omit `parameters` entirely and use type
            hints, the schema is inferred but you should still pass good
            descriptions via Annotated[type, "description"] or similar.

            See AgentBase.define_tool() for the full description-writing
            guidance.
            """
            def inner_decorator(func):
                nonlocal name
                if name is None:
                    name = func.__name__

                parameters = kwargs.pop("parameters", {})
                description = kwargs.pop("description", None)
                secure = kwargs.pop("secure", True)
                fillers = kwargs.pop("fillers", None)
                webhook_url = kwargs.pop("webhook_url", None)
                required = kwargs.pop("required", None)

                handler = func
                is_typed = False

                # If parameters not explicitly provided, try type inference
                if not parameters:
                    from signalwire.core.agent.tools.type_inference import (
                        infer_schema,
                        create_typed_handler_wrapper,
                    )
                    inferred_params, inferred_required, inferred_desc, is_typed, has_raw_data = infer_schema(func)
                    if is_typed:
                        parameters = inferred_params
                        if inferred_required and required is None:
                            required = inferred_required
                        if inferred_desc and description is None:
                            description = inferred_desc
                        handler = create_typed_handler_wrapper(func, has_raw_data)

                # Fall back to docstring or default description
                if description is None:
                    description = func.__doc__ or f"Function {name}"

                registry.define_tool(
                    name=name,
                    description=description,
                    parameters=parameters,
                    handler=handler,
                    secure=secure,
                    fillers=fillers,
                    webhook_url=webhook_url,
                    required=required,
                    is_typed_handler=is_typed,
                    **kwargs  # Pass through any additional swaig_fields
                )
                return func
            return inner_decorator
        return decorator
    
    @classmethod
    def create_class_decorator(cls):
        """
        Create class tool decorator.
        
        Returns:
            Decorator function
        """
        def tool(name=None, **kwargs):
            """
            Class method decorator for defining SWAIG tools.

            See AgentBase.define_tool() for the full guidance on writing
            descriptions. The short version: a SWAIG tool is exactly the
            same concept as an OpenAI tool — the model reads `description`
            (and per-parameter descriptions) on every turn to decide when
            to call this function. Treat those strings as prompt
            engineering, not as developer notes.

            Used as:

                @AgentBase.tool(
                    name="lookup_account",
                    description=(
                        "Look up a customer's account by number. Use BEFORE "
                        "quoting account-specific info."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {
                            "account_number": {
                                "type": "string",
                                "description": "Customer's 8-digit account number",
                            }
                        },
                        "required": ["account_number"],
                    },
                )
                def lookup_account(self, args, raw_data):
                    ...
            """
            def decorator(func):
                # Mark the function as a tool
                func._is_tool = True
                func._tool_name = name if name else func.__name__
                func._tool_params = kwargs
                
                # Return the original function
                return func
            return decorator
        return tool