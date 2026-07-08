"""Deprecated import path for ``lookup`` REST symbols.

These symbols moved out of ``namespaces.lookup`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.lookup import LookupResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.lookup`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.lookup is deprecated; use client.lookup. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import Lookup  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
LookupResource = Lookup

__all__ = ["LookupResource"]
