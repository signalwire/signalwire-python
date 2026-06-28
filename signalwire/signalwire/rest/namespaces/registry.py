"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

10DLC Campaign Registry namespace — brands, campaigns, orders, numbers. The resources
are generated from the canonical spec (see ``relay_rest_resources_generated``); this is
the thin namespace that groups them under ``client.registry``.
"""

from typing import Any

from .relay_rest_resources_generated import (
    RegistryBrands,
    RegistryCampaigns,
    RegistryNumbers,
    RegistryOrders,
)

__all__ = [
    "RegistryBrands",
    "RegistryCampaigns",
    "RegistryNamespace",
    "RegistryNumbers",
    "RegistryOrders",
]


class RegistryNamespace:
    """10DLC Campaign Registry namespace."""

    def __init__(self, http: Any) -> None:
        self.brands = RegistryBrands(http)
        self.campaigns = RegistryCampaigns(http)
        self.orders = RegistryOrders(http)
        self.numbers = RegistryNumbers(http)
