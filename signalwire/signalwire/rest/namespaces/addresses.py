"""Deprecated import path for ``addresses`` REST symbols.

These symbols moved out of ``namespaces.addresses`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.rest.namespaces.addresses import AddressesResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.addresses`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.rest.namespaces.addresses is deprecated; use client.addresses. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import Addresses  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
AddressesResource = Addresses

__all__ = ["AddressesResource"]
