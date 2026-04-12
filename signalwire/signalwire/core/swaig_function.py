"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
SwaigFunction class for defining and managing SWAIG function interfaces
"""

from typing import Dict, Any, Optional, Callable, List, Type, Union
import inspect
import logging

# Import here to avoid circular imports
from signalwire.core.function_result import FunctionResult

class SWAIGFunction:
    """
    Represents a SWAIG function — i.e., a tool the AI model can call.

    A SWAIG function is exactly the same concept as a "tool" in native
    OpenAI / Anthropic tool calling. Each SWAIGFunction is rendered into
    the OpenAI tool schema format and sent to the model on every turn:

        {"type": "function", "function": {
            "name":        self.name,
            "description": self.description,
            "parameters":  self.parameters,
        }}

    The model parses `description` (and the `description` inside each
    parameter) to decide WHEN to call the tool and HOW to fill in the
    arguments. Both fields are prompt-engineered text — the quality of
    your descriptions directly drives tool-selection accuracy.

    Use AgentBase.define_tool() to create one (it builds the
    SWAIGFunction for you and registers it). Use the @agent.tool()
    decorator for the same thing in class-based agents.
    """
    def __init__(
        self,
        name: str,
        handler: Callable,
        description: str,
        parameters: Dict[str, Dict] = None,
        secure: bool = False,
        fillers: Optional[Dict[str, List[str]]] = None,
        wait_file: Optional[str] = None,
        wait_file_loops: Optional[int] = None,
        webhook_url: Optional[str] = None,
        required: Optional[List[str]] = None,
        is_typed_handler: bool = False,
        **extra_swaig_fields
    ):
        """
        Initialize a new SWAIG function.

        Args:
            name: Function name. Becomes the `name` field in the OpenAI
                tool schema sent to the model — what the model emits when
                it decides to call this tool.
            handler: Python callable invoked when the model calls this tool.
            description: LLM-facing description. The model reads this on
                every turn to decide whether to call the tool. Be specific
                about WHEN to use it and what makes it the right choice
                over sibling tools — vague descriptions are the most
                common cause of "model has the right tool but doesn't
                call it" failures.
            parameters: JSON Schema for the arguments. Per-property
                `description` strings inside the schema are also LLM-facing
                — write them as instructions to the model on how to fill
                in each argument.
            secure: Whether this function requires SWAIG token validation.
            fillers: Optional dictionary of filler phrases by language code
                (deprecated, use wait_file).
            wait_file: Optional URL to audio file to play while function
                executes.
            wait_file_loops: Optional number of times to loop the wait_file.
            webhook_url: Optional external webhook URL to use instead of
                local handling.
            required: Optional list of required parameter names.
            is_typed_handler: Whether the handler uses type-hinted parameters
                (auto-wrapped).
            **extra_swaig_fields: Additional SWAIG-only fields (meta_data_token,
                web_hook_auth_*, etc.) to include in the generated definition.
        """
        self.name = name
        self.handler = handler
        self.description = description
        self.parameters = parameters or {}
        self.secure = secure
        self.fillers = fillers  # Text phrases to say while processing
        self.wait_file = wait_file  # URL to audio/video file to play while waiting
        self.wait_file_loops = wait_file_loops
        self.webhook_url = webhook_url
        self.required = required or []
        self.is_typed_handler = is_typed_handler
        self.extra_swaig_fields = extra_swaig_fields
        
        # Mark as external if webhook_url is provided
        self.is_external = webhook_url is not None
        
    def _ensure_parameter_structure(self) -> Dict:
        """
        Ensure the parameters are correctly structured for SWML
        
        Returns:
            Parameters dict with correct structure
        """
        if not self.parameters:
            return {"type": "object", "properties": {}}
            
        # Check if we already have the correct structure 
        if "type" in self.parameters and "properties" in self.parameters:
            return self.parameters
            
        # Otherwise, wrap the parameters in the expected structure
        result = {
            "type": "object",
            "properties": self.parameters
        }
        
        # Add required fields if specified
        if self.required:
            result["required"] = self.required
            
        return result
        
    def __call__(self, *args, **kwargs):
        """
        Call the underlying handler function
        """
        return self.handler(*args, **kwargs)

    def execute(self, args: Dict[str, Any], raw_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the function with the given arguments
        
        Args:
            args: Parsed arguments for the function
            raw_data: Optional raw request data
            
        Returns:
            Function result as a dictionary (from FunctionResult.to_dict())
        """
        try:
            # Raw data is mandatory, but we'll handle the case where it's null for robustness
            if raw_data is None:
                raw_data = {}  # Provide an empty dict as fallback

            # Call the handler with both args and raw_data
            result = self.handler(args, raw_data)
                
            # Handle different result types - everything must end up as a FunctionResult
            if isinstance(result, FunctionResult):
                # Already a FunctionResult - just convert to dict
                return result.to_dict()
            elif isinstance(result, dict) and "response" in result:
                # Already in the correct format - use as is
                return result
            elif isinstance(result, dict):
                # Dictionary without response - create a FunctionResult
                return FunctionResult("Function completed successfully").to_dict()
            else:
                # String or other type - create a FunctionResult with the string representation
                return FunctionResult(str(result)).to_dict()
                
        except Exception as e:
            # Log the error for debugging but don't expose details to the AI
            logging.error(f"Error executing SWAIG function {self.name}: {str(e)}")
            # Return a generic error message
            return FunctionResult(
                "Sorry, I couldn't complete that action. Please try again or contact support if the issue persists."
            ).to_dict()
        
    def validate_args(self, args: Dict[str, Any]) -> tuple:
        """
        Validate the arguments against the parameter schema.

        Uses jsonschema_rs if available for fast validation, falls back to
        jsonschema if available, otherwise skips validation.

        Args:
            args: Arguments to validate

        Returns:
            Tuple of (is_valid: bool, errors: list[str])
            If no validation library is available, returns (True, [])
        """
        schema = self._ensure_parameter_structure()
        if not schema or not schema.get('properties'):
            return True, []

        # Try jsonschema_rs first (fast Rust-based validator)
        try:
            import jsonschema_rs
            validator = jsonschema_rs.JSONSchema(schema)
            if validator.is_valid(args):
                return True, []
            else:
                errors = []
                for error in validator.iter_errors(args):
                    errors.append(str(error))
                return False, errors
        except ImportError:
            pass
        except Exception as e:
            logging.debug(f"jsonschema_rs validation error for {self.name}: {e}")
            pass

        # Fall back to jsonschema (pure Python)
        try:
            import jsonschema
            validator = jsonschema.Draft7Validator(schema)
            validation_errors = list(validator.iter_errors(args))
            if not validation_errors:
                return True, []
            else:
                errors = [str(e.message) for e in validation_errors]
                return False, errors
        except ImportError:
            pass
        except Exception as e:
            logging.debug(f"jsonschema validation error for {self.name}: {e}")
            pass

        # No validation library available - skip validation
        return True, []
        
    def to_swaig(self, base_url: str, token: Optional[str] = None, call_id: Optional[str] = None, include_auth: bool = True) -> Dict[str, Any]:
        """
        Convert this function to a SWAIG-compatible JSON object for SWML
        
        Args:
            base_url: Base URL for the webhook
            token: Optional auth token to include
            call_id: Optional call ID for session tracking
            include_auth: Whether to include auth credentials in URL
            
        Returns:
            Dictionary representation for the SWAIG array in SWML
        """
        # All functions use a single /swaig endpoint
        url = f"{base_url}/swaig"
        
        # Add token and call_id parameters if provided
        if token and call_id:
            url = f"{url}?token={token}&call_id={call_id}"
        
        # Create properly structured function definition
        function_def = {
            "function": self.name,
            "description": self.description,
            "parameters": self._ensure_parameter_structure(),
        }
        
        # Only add web_hook_url if not using defaults
        # This will be handled by the defaults section in the SWAIG array
        if url:
            function_def["web_hook_url"] = url
            
        # Add fillers if provided
        if self.fillers and len(self.fillers) > 0:
            function_def["fillers"] = self.fillers
        
        # Add any extra SWAIG fields
        function_def.update(self.extra_swaig_fields)
            
        return function_def

