"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

SwaigFunction class for defining and managing SWAIG function interfaces
"""

from typing import TYPE_CHECKING, Any
from collections.abc import Callable
import asyncio
import concurrent.futures
import inspect
import logging

# Import here to avoid circular imports
from signalwire.core.function_result import (
    FunctionResult,
    ToolRefusal,
    settle_result,
    tool_error_result,
)
from signalwire.core.semantic_gate import apply_gate_fields

#: The argument a vouched tool adds, which the model sets to say every other
#: argument came from the user
VOUCHED_PARAMETER = "data_supplied_by_user"
#: Its description, as the model reads it
VOUCHED_DESCRIPTION = (
    "True only when every other argument is what the user said in this call, "
    "not a guess, an example or something assumed. False when any value did "
    "not come from the user."
)
#: The tool prompt the model gets when it calls a vouched tool without
#: vouching for its arguments
VOUCHED_PROMPT = "Get the answer from the user before using this tool."

if TYPE_CHECKING:
    # The inbound SWAIG function-webhook payload, typed from the spec (a plain dict at
    # runtime; TYPE_CHECKING-only so there's no import cost / cycle). Generated from
    # porting-sdk/swaig-specs/swaig-request.yaml (vendored from mod_openai).
    from signalwire.core.swaig_request_generated import SwaigRequest


def _nullable_spec(spec: Any) -> Any:
    """A property's schema that also takes null."""
    if not isinstance(spec, dict) or "type" not in spec:
        return spec
    types = spec["type"] if isinstance(spec["type"], list) else [spec["type"]]
    widened: dict[str, Any] = {**spec, "type": [*types, "null"] if "null" not in types else types}
    if isinstance(spec.get("enum"), list) and None not in spec["enum"]:
        widened["enum"] = [*spec["enum"], None]
    return widened


def _resolve_awaitable(result: Any) -> Any:
    """Return ``result``, first running it to completion if it's awaitable.

    For synchronous callers of an ``async def`` tool handler, such as the
    serverless entry points and ``swaig-test``. It uses ``asyncio.run()`` when
    no event loop is running in this thread. Inside a running loop, where
    ``asyncio.run()`` isn't allowed, it runs the awaitable on a separate
    thread's loop and waits for it. Asynchronous callers, such as the
    ``/swaig`` endpoint, await the result on their own loop instead.
    """
    if not inspect.isawaitable(result):
        return result

    async def _await() -> Any:
        return await result

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_await())
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, _await()).result()


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
        handler: Callable[..., Any],
        description: str,
        parameters: dict[str, dict[str, Any]] | None = None,
        secure: bool = False,
        fillers: dict[str, list[str]] | None = None,
        wait_file: str | None = None,
        wait_file_loops: int | None = None,
        webhook_url: str | None = None,
        required: list[str] | None = None,
        is_typed_handler: bool = False,
        vouched: bool = False,
        nullable_optional: bool | None = None,
        **extra_swaig_fields: Any,
    ) -> None:
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
            fillers: Optional phrases the AI says while the function runs,
                keyed by language code, "auto" (translated into the call's
                language on first use) or "default". An entry may be a list of
                phrases, a wait script, spoken one at a time while the call
                waits; the annotation predates wait scripts, so a type
                checker needs a cast for one.
            wait_file: Optional URL to audio file to play while function
                executes.
            wait_file_loops: Optional number of times to loop the wait_file.
            webhook_url: Optional external webhook URL to use instead of
                local handling.
            required: Optional list of required parameter names.
            is_typed_handler: Whether the handler uses type-hinted parameters
                (auto-wrapped).
            vouched: True to add a required boolean argument,
                ``data_supplied_by_user`` (VOUCHED_PARAMETER), in which the
                model says every other argument came from the user. Unless
                it's true, the handler doesn't run and the model is told to
                get the answer from the user (VOUCHED_PROMPT). The handler
                never sees the argument.
            nullable_optional: True to let the model send null for an
                optional argument: each argument that isn't required takes
                null as well as its type, as providers with strict schemas
                require, and a null reaches the handler as an argument not
                given. None (default) follows the agent's
                ``set_nullable_optional_parameters()``.
            **extra_swaig_fields: Additional SWAIG-only fields (meta_data_token,
                web_hook_auth_*, etc.) to include in the generated definition.
                ``gates`` (SemanticGate objects or gate dicts) and
                ``gate_fillers`` are checked by the platform's rules.

        Raises:
            ValueError: For gates the platform would refuse, or gate_fillers
                without gates.
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
        self.vouched = vouched
        self.nullable_optional = nullable_optional
        apply_gate_fields(extra_swaig_fields, name)
        self.extra_swaig_fields = extra_swaig_fields

        # Mark as external if webhook_url is provided
        self.is_external = webhook_url is not None

    def _ensure_parameter_structure(
        self, nullable_optional: bool | None = None
    ) -> dict[str, Any]:
        """
        Ensure the parameters are correctly structured for SWML

        Args:
            nullable_optional: The agent's default for whether optional
                arguments take null, used when this function doesn't set
                its own.

        Returns:
            Parameters dict with correct structure
        """
        if not self.parameters:
            result: dict[str, Any] = {"type": "object", "properties": {}}
        elif "type" in self.parameters and "properties" in self.parameters:
            # Already the correct structure
            result = self.parameters
        else:
            # Otherwise, wrap the parameters in the expected structure
            result = {"type": "object", "properties": self.parameters}

            # Add required fields if specified
            if self.required:
                result["required"] = self.required

        if self._nullable(nullable_optional):
            required = set(result.get("required", []))
            result = {
                **result,
                "properties": {
                    key: spec if key in required else _nullable_spec(spec)
                    for key, spec in result.get("properties", {}).items()
                },
            }

        if self.vouched:
            result = {
                **result,
                "properties": {
                    **result.get("properties", {}),
                    VOUCHED_PARAMETER: {
                        "type": "boolean",
                        "description": VOUCHED_DESCRIPTION,
                    },
                },
                "required": [
                    *(r for r in result.get("required", []) if r != VOUCHED_PARAMETER),
                    VOUCHED_PARAMETER,
                ],
            }
        return result

    def _vouched_refusal(self, args: dict[str, Any]) -> FunctionResult | None:
        """What the model gets for a vouched call it didn't vouch for, or None."""
        if not self.vouched or (args or {}).get(VOUCHED_PARAMETER) is True:
            return None
        return FunctionResult(
            tool_result=f"{self.name} was not run.", tool_prompt=VOUCHED_PROMPT
        )

    def _nullable(self, default: bool | None) -> bool:
        """Whether optional arguments take null: this function's own setting,
        else the agent's default."""
        own = self.nullable_optional
        return bool(default) if own is None else own

    def _handler_args(
        self, args: dict[str, Any], nullable_optional: bool | None = None
    ) -> dict[str, Any]:
        """The arguments the handler gets: a vouched tool's own is removed,
        and a null for an optional argument that takes null is an argument
        not given."""
        if not args:
            return args
        drop: set[str] = set()
        if self.vouched and VOUCHED_PARAMETER in args:
            drop.add(VOUCHED_PARAMETER)
        if self._nullable(nullable_optional):
            required = set(self._ensure_parameter_structure(False).get("required", []))
            drop.update(k for k, v in args.items() if v is None and k not in required)
        if not drop:
            return args
        return {k: v for k, v in args.items() if k not in drop}

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Call the underlying handler function
        """
        return self.handler(*args, **kwargs)

    def execute(
        self, args: dict[str, Any], raw_data: "SwaigRequest | None" = None
    ) -> dict[str, Any]:
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

            refusal = self._vouched_refusal(args)
            if refusal is not None:
                return refusal.to_dict()

            # Call the handler with both args and raw_data. An async handler
            # returns an awaitable, which runs to completion here.
            result = settle_result(
                self.name,
                _resolve_awaitable(self.handler(self._handler_args(args), raw_data)),
            )

            # Handle different result types - everything must end up as a FunctionResult
            if isinstance(result, FunctionResult):
                return result.to_dict()
            if isinstance(result, dict):
                # A SWAIG result already (settle_result made sure)
                return result
            # String or other type - create a FunctionResult with the string representation
            return FunctionResult(str(result)).to_dict()

        except ToolRefusal as declined:
            return declined.result().to_dict()
        except Exception as e:
            # Logged, not sent: the text can hold internals, and the model
            # would read it as the outcome
            logging.error(f"Error executing SWAIG function {self.name}: {e!s}")
            return tool_error_result(self.name).to_dict()

    def validate_args(
        self, args: dict[str, Any], nullable_optional: bool | None = None
    ) -> tuple[Any, ...]:
        """
        Validate the arguments against the parameter schema.

        Uses jsonschema_rs if available for fast validation, falls back to
        jsonschema if available, otherwise skips validation.

        Args:
            args: Arguments to validate
            nullable_optional: The agent's default for whether optional
                arguments take null, used when this function doesn't set
                its own.

        Returns:
            Tuple of (is_valid: bool, errors: list[str])
            If no validation library is available, returns (True, [])
        """
        schema = self._ensure_parameter_structure(nullable_optional)
        if not schema or not schema.get("properties"):
            return True, []

        # Try jsonschema_rs first (fast Rust-based validator)
        try:
            import jsonschema_rs

            validator = jsonschema_rs.JSONSchema(schema)  # type: ignore[attr-defined]  # jsonschema_rs ships no type stubs
            if validator.is_valid(args):
                return True, []
            errors = [str(error) for error in validator.iter_errors(args)]
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
            errors = [str(e.message) for e in validation_errors]
            return False, errors
        except ImportError:
            pass
        except Exception as e:
            logging.debug(f"jsonschema validation error for {self.name}: {e}")
            pass

        # No validation library available - skip validation
        return True, []

    def to_swaig(
        self,
        base_url: str,
        token: str | None = None,
        call_id: str | None = None,
        include_auth: bool = True,
    ) -> dict[str, Any]:
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
