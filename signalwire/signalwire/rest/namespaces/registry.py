"""Deprecated import path for ``registry`` REST symbols.

These symbols moved out of ``namespaces.registry`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.rest.namespaces.registry import RegistryBrands``
working but emits a :class:`DeprecationWarning`. Prefer ``client.registry`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.rest.namespaces.registry is deprecated; use client.registry. "
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
