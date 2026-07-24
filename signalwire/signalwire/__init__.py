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

# Library-safe logging: importing signalwire installs ONLY a NullHandler on the
# `signalwire` namespace logger (done at logging_config module load). It does NOT
# configure global logging — that would hijack the host application's logging (its
# structlog config, its root/generic-named loggers). The app opts in to SDK log
# OUTPUT by calling configure_logging() explicitly; the server/CLI entry points do.
from .core.logging_config import configure_logging  # noqa: F401  (re-exported)

if TYPE_CHECKING:
    from signalwire.rest.client import RestClient as _RestClient
    from signalwire.core.skill_base import SkillBase
    from signalwire.skills.registry import SkillRegistry

    # §6.2-python: the public symbols are LAZY at runtime (PEP 562, below) so
    # `import signalwire` doesn't drag FastAPI/uvicorn/pydantic at import time; the
    # eager imports here keep type checkers and IDEs fully aware of the real types.
    from signalwire.core.agent_base import AgentBase
    from signalwire.core.contexts import (
        ContextBuilder,
        Context,
        Step,
        GatherInfo,
        GatherQuestion,
        create_simple_context,
    )
    from signalwire.core.data_map import (
        DataMap,
        create_simple_api_tool,
        create_expression_tool,
    )
    from signalwire.agent_server import AgentServer
    from signalwire.core.swml_service import SWMLService
    from signalwire.core.swml_builder import SWMLBuilder
    from signalwire.core.function_result import FunctionResult, SwaigFunctionResult
    from signalwire.core.swaig_function import SWAIGFunction
    from signalwire.agents.bedrock import BedrockAgent
    from signalwire.utils.schema_utils import SchemaValidationError
    from signalwire.web import WebService

__version__ = "3.2.0"

# §6.2-python (owner decision: NO packaging split — one package, all deps required;
# IMPORT-TIME behavior only): the agent/web symbols are lazy-imported via module
# __getattr__ (PEP 562) so `import signalwire` no longer drags FastAPI / uvicorn /
# starlette / pydantic into every process — a REST-only script imports in
# milliseconds. First ATTRIBUTE ACCESS (signalwire.AgentBase,
# `from signalwire import AgentBase`) triggers the real import and caches it on the
# module, so the public surface is byte-identical to the old eager form.
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "AgentBase": ("signalwire.core.agent_base", "AgentBase"),
    "ContextBuilder": ("signalwire.core.contexts", "ContextBuilder"),
    "Context": ("signalwire.core.contexts", "Context"),
    "Step": ("signalwire.core.contexts", "Step"),
    "GatherInfo": ("signalwire.core.contexts", "GatherInfo"),
    "GatherQuestion": ("signalwire.core.contexts", "GatherQuestion"),
    "create_simple_context": ("signalwire.core.contexts", "create_simple_context"),
    "DataMap": ("signalwire.core.data_map", "DataMap"),
    "create_simple_api_tool": ("signalwire.core.data_map", "create_simple_api_tool"),
    "create_expression_tool": ("signalwire.core.data_map", "create_expression_tool"),
    "AgentServer": ("signalwire.agent_server", "AgentServer"),
    "SWMLService": ("signalwire.core.swml_service", "SWMLService"),
    "SWMLBuilder": ("signalwire.core.swml_builder", "SWMLBuilder"),
    "FunctionResult": ("signalwire.core.function_result", "FunctionResult"),
    "SwaigFunctionResult": ("signalwire.core.function_result", "SwaigFunctionResult"),
    "SWAIGFunction": ("signalwire.core.swaig_function", "SWAIGFunction"),
    "BedrockAgent": ("signalwire.agents.bedrock", "BedrockAgent"),
    "SchemaValidationError": ("signalwire.utils.schema_utils", "SchemaValidationError"),
    "WebService": ("signalwire.web", "WebService"),
    # AI Chat client — lazy so its aiohttp dep loads only on first access (mirrors how
    # every other public client here is exposed; RestClient's factory form is the odd
    # one out). Makes `from signalwire import AIChatClient` work like every sibling.
    "AIChatClient": ("signalwire.ai_chat", "AIChatClient"),
}


def __getattr__(name: str) -> Any:
    """PEP 562 lazy attribute resolution for the public agent/web symbols."""
    spec = _LAZY_IMPORTS.get(name)
    if spec is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    value = getattr(importlib.import_module(spec[0]), spec[1])
    globals()[name] = value  # cache — subsequent access skips __getattr__
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_IMPORTS))


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
    "AIChatClient",
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
