"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

SignalWire Agents CLI Tools

This package contains command-line tools for working with SignalWire AI Agents.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .test_swaig import main as test_swaig_main

__all__ = ["test_swaig_main"]


def __getattr__(name: str) -> Any:
    """Import ``test_swaig_main`` on first access, so other commands start fast."""
    # Imported on first use: swaig-test's loader costs about a second, which
    # every other command in this package would otherwise pay at startup
    if name == "test_swaig_main":
        from .test_swaig import main

        return main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
