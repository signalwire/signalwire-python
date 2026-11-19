"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

InfoBot: the read / inform half of an operations agent.

Where ``Operations`` is what an agent can *change* for a caller, ``InfoBotKnowledge``
is what it can *answer* from a corpus. It installs on any ``AgentBase`` and composes
beside ``Operations`` on one agent: install the knowledge layer, then ``Operations``,
and the generated ``main`` step gains ``search_knowledge`` alongside the operation
tools, with each layer's record line kept in its own ``global_data`` namespace.
"""

from signalwire.operations.infobot.continuity import (
    Continuity,
    build_seed,
    medium_of,
    pair_tools,
)
from signalwire.operations.infobot.knowledge import InfoBotKnowledge
from signalwire.operations.infobot.legs import LegStore

__all__ = [
    "Continuity",
    "InfoBotKnowledge",
    "LegStore",
    "build_seed",
    "medium_of",
    "pair_tools",
]
