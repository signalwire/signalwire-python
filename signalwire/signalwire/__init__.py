"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

SignalWire SDK
=======================

A package for building AI agents using SignalWire's AI and SWML capabilities.
"""

from typing import TYPE_CHECKING, Any

# Configure logging before any other imports to ensure early initialization
from .core.logging_config import configure_logging

if TYPE_CHECKING:
    from signalwire.rest.client import RestClient as _RestClient
    from signalwire.core.skill_base import SkillBase
    from signalwire.skills.registry import SkillRegistry

configure_logging()

__version__ = "3.1.0"

# Import core classes for easier access.
# These imports are intentionally placed after configure_logging() so the SDK's
# logging is initialized before any submodule is imported (E402 expected).
from .core.agent_base import AgentBase  # noqa: E402
from .core.contexts import (  # noqa: E402
    ContextBuilder,
    Context,
    Step,
    GatherInfo,
    GatherQuestion,
    create_simple_context,
)
from .core.data_map import (  # noqa: E402
    DataMap,
    create_simple_api_tool,
    create_expression_tool,
)
from signalwire.agent_server import AgentServer  # noqa: E402
from signalwire.core.swml_service import SWMLService  # noqa: E402
from signalwire.core.swml_builder import SWMLBuilder  # noqa: E402
from signalwire.core.function_result import (  # noqa: E402
    FunctionResult,
    SwaigFunctionResult,
)
from signalwire.core.swaig_function import SWAIGFunction  # noqa: E402
from signalwire.agents.bedrock import BedrockAgent  # noqa: E402
from signalwire.utils.schema_utils import SchemaValidationError  # noqa: E402

# Import WebService for static file serving
from signalwire.web import WebService  # noqa: E402


# Lazy import skills to avoid slow startup for CLI tools
# Skills are now loaded on-demand when requested
def _get_skill_registry() -> "SkillRegistry":
    """Lazy import and return skill registry"""
    import signalwire.skills

    return signalwire.skills.skill_registry


def list_skills() -> list[dict[str, Any]]:
    """List all available skills with metadata.

    Returns one dict per skill (name, description, version, required packages /
    env vars, multi-instance support). Delegates to the skill registry — the
    same source as ``list_skills_with_params()``, but the lighter summary."""
    from signalwire.skills.registry import skill_registry

    return skill_registry.list_skills()


def list_skills_with_params() -> dict[str, dict[str, Any]]:
    """
    Get complete schema for all available skills including parameter metadata

    This function returns a comprehensive schema for all available skills,
    including their metadata and parameter definitions. This is useful for
    GUI configuration tools, API documentation, or programmatic skill discovery.

    Returns:
        Dict[str, Dict[str, Any]]: Complete skill schema where keys are skill names

    Example:
        >>> schema = list_skills_with_params()
        >>> print(schema['web_search']['parameters']['api_key'])
        {
            'type': 'string',
            'description': 'Google Custom Search API key',
            'required': True,
            'hidden': True,
            'env_var': 'GOOGLE_SEARCH_API_KEY'
        }
    """
    from signalwire.skills.registry import skill_registry

    return skill_registry.get_all_skills_schema()


def register_skill(skill_class: "type[SkillBase]") -> None:
    """
    Register a custom skill class

    This allows third-party code to register skill classes directly without
    requiring them to be in a specific directory structure.

    Args:
        skill_class: A class that inherits from SkillBase

    Example:
        >>> from my_custom_skills import MyWeatherSkill
        >>> register_skill(MyWeatherSkill)
        >>> # Now you can use it in agents:
        >>> agent.add_skill('my_weather')
    """
    from signalwire.skills.registry import skill_registry

    return skill_registry.register_skill(skill_class)


def add_skill_directory(path: str) -> None:
    """
    Add a directory to search for skills

    This allows third-party skill collections to be registered by path.
    Skills in these directories should follow the same structure as built-in skills.

    Args:
        path: Path to directory containing skill subdirectories

    Example:
        >>> add_skill_directory('/opt/custom_skills')
        >>> # Now agent.add_skill('my_custom_skill') will search in this directory
    """
    from signalwire.skills.registry import skill_registry

    return skill_registry.add_skill_directory(path)


def RestClient(*args: Any, **kwargs: Any) -> "_RestClient":
    """Create a SignalWire REST API client (lazy import)"""
    from signalwire.rest import RestClient as _RestClient

    return _RestClient(*args, **kwargs)


__all__ = [
    "AgentBase",
    "AgentServer",
    "BedrockAgent",
    "Context",
    "ContextBuilder",
    "DataMap",
    "FunctionResult",
    "GatherInfo",
    "GatherQuestion",
    "RestClient",
    "SWAIGFunction",
    "SWMLBuilder",
    "SWMLService",
    "SchemaValidationError",
    "Step",
    "SwaigFunctionResult",
    "WebService",
    "add_skill_directory",
    "create_expression_tool",
    "create_simple_api_tool",
    "create_simple_context",
    "list_skills",
    "list_skills_with_params",
    "register_skill",
]
