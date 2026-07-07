"""Deprecated import path for ``imported_numbers`` REST symbols.

These symbols moved out of ``namespaces.imported_numbers`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.imported_numbers import ImportedNumbersResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.imported_numbers`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.imported_numbers is deprecated; use client.imported_numbers. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import ImportedNumbers  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
ImportedNumbersResource = ImportedNumbers

__all__ = ["ImportedNumbersResource"]
