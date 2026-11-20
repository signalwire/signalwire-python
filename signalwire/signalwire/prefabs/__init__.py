"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Prefab agents with specific functionality that can be used out-of-the-box
"""

from signalwire.prefabs.info_gatherer import InfoGathererAgent
from signalwire.prefabs.faq_bot import FAQBotAgent
from signalwire.prefabs.concierge import ConciergeAgent
from signalwire.prefabs.survey import SurveyAgent
from signalwire.prefabs.receptionist import ReceptionistAgent
from signalwire.prefabs.front_desk import FRONT_DESK_WORDING, Department, FrontDeskAgent

__all__ = [
    "FRONT_DESK_WORDING",
    "ConciergeAgent",
    "Department",
    "FAQBotAgent",
    "FrontDeskAgent",
    "InfoGathererAgent",
    "ReceptionistAgent",
    "SurveyAgent",
]
