"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, TYPE_CHECKING, cast

from signalwire.core.logging_config import get_logger

if TYPE_CHECKING:
    from signalwire.core.agent_base import AgentBase  # type: ignore[attr-defined]  # cycle: agent_base imports skill_base; name resolves at type-check time
    from signalwire.core.function_result import FunctionResult


class SkillBase(ABC):
    """Abstract base class for all agent skills.

    A skill is a reusable capability that you add to an agent with
    ``agent.add_skill()``. Subclass it, set ``SKILL_NAME`` and
    ``SKILL_DESCRIPTION``, and implement ``setup()`` and ``register_tools()``.
    Override the other hooks to add speech hints, global data or prompt sections.

    Example:
        ```python
        import os
        from signalwire import FunctionResult
        from signalwire.core.skill_base import SkillBase

        class WeatherSkill(SkillBase):
            '''Answer weather questions.'''

            SKILL_NAME = "weather"
            SKILL_DESCRIPTION = "Provides weather information"
            REQUIRED_ENV_VARS = ["WEATHER_API_KEY"]

            def setup(self) -> bool:
                '''Read the API key; skip the skill if it is missing.'''
                if not self.validate_env_vars():
                    return False
                self.api_key = os.getenv("WEATHER_API_KEY")
                return True

            def register_tools(self) -> None:
                '''Register the get_weather tool.'''
                self.define_tool(
                    name="get_weather",
                    description="Get current weather for a location",
                    parameters={
                        "location": {
                            "type": "string",
                            "description": "City name or zip code",
                        }
                    },
                    required=["location"],
                    handler=self._get_weather,
                )

            def _get_weather(self, args, raw_data):
                '''Look up the weather (stubbed here).'''
                return FunctionResult(f"Weather for {args['location']}: sunny")

            def get_hints(self) -> list[str]:
                '''Help speech recognition catch weather words.'''
                return ["weather", "temperature", "forecast"]
        ```
    """

    # Subclasses must define these
    SKILL_NAME: str | None = None  # Required: unique identifier
    SKILL_DESCRIPTION: str | None = None  # Required: human-readable description
    SKILL_VERSION: str = "1.0.0"  # Semantic version
    REQUIRED_PACKAGES: ClassVar[list[str]] = []  # Python packages needed
    REQUIRED_ENV_VARS: ClassVar[list[str]] = []  # Environment variables needed

    # Multiple instance support
    SUPPORTS_MULTIPLE_INSTANCES: bool = False  # Set to True to allow multiple instances

    def __init__(self, agent: "AgentBase", params: dict[str, Any] | None = None):
        """Create the skill and attach it to an agent.

        Pops ``swaig_fields`` out of ``params`` and keeps it in
        ``self.swaig_fields``. ``define_tool()`` merges it into every tool.

        Args:
            agent: The agent that owns this skill.
            params: Configuration for the skill. Defaults to an empty dict.

        Raises:
            ValueError: If the subclass does not define ``SKILL_NAME`` or
                ``SKILL_DESCRIPTION``.
        """
        if self.SKILL_NAME is None:
            raise ValueError(f"{self.__class__.__name__} must define SKILL_NAME")
        if self.SKILL_DESCRIPTION is None:
            raise ValueError(f"{self.__class__.__name__} must define SKILL_DESCRIPTION")

        self.agent = agent
        self.params = params or {}
        self.logger = get_logger(f"signalwire.skills.{self.SKILL_NAME}")

        # Extract swaig_fields from params for merging into tool definitions
        self.swaig_fields = self.params.pop("swaig_fields", {})

    @abstractmethod
    def setup(self) -> bool:
        """Set up the skill: validate env vars and packages, initialize clients.

        Subclasses must implement this. It runs once when the skill is loaded.

        Returns:
            True if setup succeeded, False if the skill should not be loaded.
        """
        pass

    @abstractmethod
    def register_tools(self) -> None:
        """Register the skill's SWAIG tools with the agent.

        Subclasses must implement this. Call ``self.define_tool()`` once for
        each tool. It runs after ``setup()`` succeeds.
        """
        pass

    def define_tool(self, **kwargs: Any) -> None:
        """
        Wrapper method that automatically includes swaig_fields when defining tools.

        This method delegates to self.agent.define_tool() but automatically merges
        any swaig_fields configured for this skill. Skills should use this method
        instead of calling self.agent.define_tool() directly.

        Args:
            **kwargs: All arguments supported by agent.define_tool()
                     (name, description, parameters, handler, etc.)
        """
        # Merge swaig_fields with any explicitly passed fields
        # Explicit fields take precedence over swaig_fields
        merged_kwargs = dict(self.swaig_fields)
        merged_kwargs.update(kwargs)

        # Call the agent's define_tool with merged arguments. agent.define_tool
        # returns the AgentBase (fluent), but this wrapper's contract is -> None
        # and `self.agent` is untyped, so don't propagate the Any return.
        self.agent.define_tool(**merged_kwargs)

    def get_hints(self) -> list[str]:
        """Return speech recognition hints for this skill.

        Override to return words or phrases the agent should recognize better.

        Returns:
            A list of hint strings. The default is an empty list.
        """
        return []

    def get_global_data(self) -> dict[str, Any]:
        """Return data to add to the agent's global data.

        Override to supply session data that SWAIG function handlers can read.

        Returns:
            A dict of key-value pairs. The default is an empty dict.
        """
        return {}

    def get_prompt_sections(self) -> list[dict[str, Any]]:
        """Return prompt sections to add to the agent.

        Subclasses normally override ``_get_prompt_sections()`` instead, so the
        ``skip_prompt`` parameter keeps working.

        Returns:
            A list of section dicts, each with a ``title`` and a ``body`` or
            ``bullets``. The list is empty when ``skip_prompt`` is true in the
            skill's params.
        """
        if self.params.get("skip_prompt", False):
            return []
        return self._get_prompt_sections()

    def _get_prompt_sections(self) -> list[dict[str, Any]]:
        """Return the skill's prompt sections.

        Override this in subclasses to provide prompt sections.

        Returns:
            A list of section dicts. The default is an empty list.
        """
        return []

    def cleanup(self) -> None:  # noqa: B027  # intentional overridable no-op hook, not an abstract method (subclasses override only if they hold resources)
        """Release resources when the skill is removed or the agent shuts down.

        Override to close connections or cancel background work. The default
        does nothing.
        """
        pass

    def validate_env_vars(self) -> bool:
        """Check that every variable in ``REQUIRED_ENV_VARS`` is set.

        Logs an error that lists the missing variables.

        Returns:
            True if all required variables are set, False otherwise.
        """
        import os

        missing = [var for var in self.REQUIRED_ENV_VARS if not os.getenv(var)]
        if missing:
            self.logger.error(f"Missing required environment variables: {missing}")
            return False
        return True

    def validate_packages(self) -> bool:
        """Check that every package in ``REQUIRED_PACKAGES`` can be imported.

        Logs an error that lists the missing packages.

        Returns:
            True if all required packages import, False otherwise.
        """
        import importlib

        missing = []
        for package in self.REQUIRED_PACKAGES:
            try:
                importlib.import_module(package)
            except ImportError:  # noqa: PERF203  # per-iteration error isolation: must check every package to report all missing ones
                missing.append(package)
        if missing:
            self.logger.error(f"Missing required packages: {missing}")
            return False
        return True

    def get_instance_key(self) -> str:
        """
        Get the key used to track this skill instance

        For skills that support multiple instances (SUPPORTS_MULTIPLE_INSTANCES = True),
        this method can be overridden to provide a unique key for each instance.

        Default implementation:
        - If SUPPORTS_MULTIPLE_INSTANCES is False: returns SKILL_NAME
        - If SUPPORTS_MULTIPLE_INSTANCES is True: returns SKILL_NAME + "_" + tool_name
          (where tool_name comes from params['tool_name'] or defaults to the skill name)

        Returns:
            The unique key for this skill instance.
        """
        if not self.SUPPORTS_MULTIPLE_INSTANCES:
            return self.SKILL_NAME or ""

        # For multi-instance skills, create key from skill name + tool name
        tool_name = self.params.get("tool_name", self.SKILL_NAME)
        return f"{self.SKILL_NAME}_{tool_name}"

    def _get_skill_namespace(self) -> str:
        """
        Get the namespaced key for this skill instance's global_data.

        Uses the 'prefix' param if available, otherwise falls back to
        the instance key. This ensures multiple skill instances can
        store state in global_data without collisions.

        Returns:
            A namespace key like "skill:<prefix>" or "skill:<instance_key>".
        """
        prefix = self.params.get("prefix")
        if prefix:
            return f"skill:{prefix}"
        return f"skill:{self.get_instance_key()}"

    def get_skill_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """
        Read this skill instance's namespaced data from raw_data global_data.

        Args:
            raw_data: The raw_data dict passed to SWAIG function handlers,
                     expected to contain a 'global_data' key.

        Returns:
            The skill's namespaced state, or an empty dict if not found.
        """
        namespace = self._get_skill_namespace()
        # raw_data is dict[str, Any], so global_data and the namespaced lookup
        # are Any; the skill's namespaced state is itself a dict.
        global_data = raw_data.get("global_data", {})
        return cast(dict[str, Any], global_data.get(namespace, {}))

    def update_skill_data(
        self, result: "FunctionResult", data: dict[str, Any]
    ) -> "FunctionResult":
        """
        Write this skill instance's namespaced data into a FunctionResult.

        Wraps the data under the skill's namespace key and calls
        result.update_global_data().

        Args:
            result: The FunctionResult to add the global_data update to.
            data: The skill state dict to store under the namespace.

        Returns:
            The same result, for method chaining.
        """
        namespace = self._get_skill_namespace()
        result.update_global_data({namespace: data})
        return result

    @classmethod
    def get_parameter_schema(cls) -> dict[str, dict[str, Any]]:
        """
        Get the parameter schema for this skill

        This method returns metadata about all parameters the skill accepts,
        including their types, descriptions, default values, and whether they
        are required or should be hidden (e.g., API keys).

        The base implementation provides common parameters available to all skills.
        Subclasses should override this method and merge their specific parameters
        with the base schema.

        Returns:
            A parameter schema. Keys are parameter names and values are
            dictionaries containing:
                - type: Parameter type ("string", "integer", "number", "boolean", "object", "array")
                - description: Human-readable description
                - default: Default value if not provided (optional)
                - required: Whether the parameter is required (default: False)
                - hidden: Whether to hide this field in UIs (for secrets/keys)
                - env_var: Environment variable a configuration tool can read this
                  value from (optional). A hint for tools that read the schema; the
                  SDK doesn't read it, so the skill gets the value from its params.
                - enum: List of allowed values (optional)
                - min/max: Minimum/maximum values for numeric types (optional)

        Example:
            {
                "tool_name": {
                    "type": "string",
                    "description": "Name for the tool when using multiple instances",
                    "default": "my_skill",
                    "required": False
                },
                "api_key": {
                    "type": "string",
                    "description": "API key for the service",
                    "required": True,
                    "hidden": True,
                    "env_var": "MY_API_KEY"
                }
            }
        """
        schema = {}

        # Add swaig_fields parameter (available to all skills)
        schema["swaig_fields"] = {
            "type": "object",
            "description": "Additional SWAIG function metadata to merge into tool definitions",
            "default": {},
            "required": False,
        }

        # Add skip_prompt flag (available to all skills)
        schema["skip_prompt"] = {
            "type": "boolean",
            "description": "If true, the skill will not inject its default prompt section into the POM",
            "default": False,
            "required": False,
        }

        # Add tool_name for multi-instance skills. Its default is the skill
        # name; a skill whose tool is named otherwise, or that doesn't use
        # tool_name, redeclares or removes this entry.
        if cls.SUPPORTS_MULTIPLE_INSTANCES:
            schema["tool_name"] = {
                "type": "string",
                "description": "Custom name for this skill instance (for multiple instances)",
                "default": cls.SKILL_NAME,
                "required": False,
            }

        return schema
