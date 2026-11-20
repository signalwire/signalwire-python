"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The deprecated prefabs still work, and say what to use instead.
"""

from __future__ import annotations

import pytest

from signalwire.prefabs import ConciergeAgent, FAQBotAgent, ReceptionistAgent


def test_each_warns_and_names_its_replacement() -> None:
    with pytest.warns(DeprecationWarning, match="Use FrontDeskAgent"):
        ConciergeAgent(venue_name="Inn", services=["spa"], amenities={}, suppress_logs=True)
    with pytest.warns(DeprecationWarning, match="use FrontDeskAgent"):
        ReceptionistAgent(departments=[{"name": "sales", "description": "buying", "number": "+15550100001"}],
                          suppress_logs=True)
    with pytest.warns(DeprecationWarning, match="use InfoBotKnowledge"):
        FAQBotAgent(faqs=[{"question": "Hours?", "answer": "9 to 5."}], suppress_logs=True)
