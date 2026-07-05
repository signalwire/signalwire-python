"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

Deprecated import path. The REST layer is spec-generated; these symbols moved out of
``namespaces.registry`` (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.registry import RegistryBrands`` working
but emits a DeprecationWarning. Prefer ``client.registry`` (no import needed). PYTHON-ONLY: the
surface oracle skips this file, so no other port implements these.
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.registry is deprecated; use client.registry. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import (  # noqa: E402  (re-export after the deprecation warn — intentional)
    RegistryBrands,
    RegistryCampaigns,
    RegistryNumbers,
    RegistryOrders,
)
from ._client_tree_generated import RegistryNamespace  # noqa: E402  (re-export after the deprecation warn — intentional)

__all__ = [
    "RegistryBrands",
    "RegistryCampaigns",
    "RegistryNamespace",
    "RegistryNumbers",
    "RegistryOrders",
]
