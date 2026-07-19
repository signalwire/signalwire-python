"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Core components for SignalWire AI Agents
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from signalwire.core.agent_base import AgentBase
    from signalwire.core.function_result import FunctionResult
    from signalwire.core.swaig_function import SWAIGFunction
    from signalwire.core.swml_service import SWMLService
    from signalwire.core.swml_handler import SWMLVerbHandler, VerbHandlerRegistry
    from signalwire.core.swml_builder import SWMLBuilder

# §6.2-python: lazy (PEP 562) so importing any signalwire.core.* leaf (e.g.
# logging_config from the package root) doesn't drag AgentBase → FastAPI into every
# process. First attribute access resolves + caches; public surface unchanged.
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "AgentBase": ("signalwire.core.agent_base", "AgentBase"),
    "FunctionResult": ("signalwire.core.function_result", "FunctionResult"),
    "SWAIGFunction": ("signalwire.core.swaig_function", "SWAIGFunction"),
    "SWMLService": ("signalwire.core.swml_service", "SWMLService"),
    "SWMLVerbHandler": ("signalwire.core.swml_handler", "SWMLVerbHandler"),
    "VerbHandlerRegistry": ("signalwire.core.swml_handler", "VerbHandlerRegistry"),
    "SWMLBuilder": ("signalwire.core.swml_builder", "SWMLBuilder"),
}


def __getattr__(name: str) -> Any:
    spec = _LAZY_IMPORTS.get(name)
    if spec is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    value = getattr(importlib.import_module(spec[0]), spec[1])
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_IMPORTS))


__all__ = [
    "AgentBase",
    "FunctionResult",
    "SWAIGFunction",
    "SWMLBuilder",
    "SWMLService",
    "SWMLVerbHandler",
    "VerbHandlerRegistry",
]
