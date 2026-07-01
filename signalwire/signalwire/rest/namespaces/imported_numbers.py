"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

Deprecated import path. The REST layer is spec-generated; these symbols moved out of
``namespaces.imported_numbers`` (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.imported_numbers import ImportedNumbersResource`` working
but emits a DeprecationWarning. Prefer ``client.imported_numbers`` (no import needed). PYTHON-ONLY: the
surface oracle skips this file, so no other port implements these.
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
