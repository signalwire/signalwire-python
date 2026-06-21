"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Typing-only indirection so the mixins can be type-checked as ``AgentBase``
without a runtime import cycle.

``agent_base`` imports every mixin to compose ``AgentBase``; a mixin importing
``agent_base`` back at runtime would cycle. But under ``typing.TYPE_CHECKING``
the import is never executed at runtime — mypy resolves it statically. This
module re-exposes ``AgentBase`` as ``AgentHost`` purely for that static use; at
runtime ``AgentHost`` is ``object``.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from signalwire.core.agent_base import AgentBase as AgentHost  # type: ignore[attr-defined]  # intentional TYPE_CHECKING-only re-export; agent_base imports this module's consumers (the mixins), so the name resolves for them but not in self-check
else:
    AgentHost = object
