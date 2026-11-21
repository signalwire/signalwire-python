"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

InfoBot: the read / inform half of an operations agent.

Where ``Operations`` is what an agent can *change* for a caller, ``InfoBotKnowledge``
is what it can *answer* from a corpus. It installs on any ``AgentBase`` and composes
beside ``Operations`` on one agent, in either order: the ``main`` step offers
``search_knowledge`` alongside the operation tools.
"""

from signalwire.operations.infobot.continuity import (
    Continuity,
    build_seed,
    default_switch_note,
    default_switch_turn,
    medium_of,
    pair_tools,
)
from signalwire.operations.infobot.knowledge import (
    CONTACT_FIELDS,
    KNOWLEDGE_WORDING,
    InfoBotKnowledge,
)
from signalwire.operations.infobot.legs import LegStore
from signalwire.operations.infobot.livecall import say_into_call

__all__ = [
    "CONTACT_FIELDS",
    "KNOWLEDGE_WORDING",
    "Continuity",
    "InfoBotKnowledge",
    "LegStore",
    "build_seed",
    "default_switch_note",
    "default_switch_turn",
    "medium_of",
    "pair_tools",
    "say_into_call",
]
