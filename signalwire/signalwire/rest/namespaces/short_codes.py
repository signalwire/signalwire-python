"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

Deprecated import path. The REST layer is spec-generated; these symbols moved out of
``namespaces.short_codes`` (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.short_codes import ShortCodesResource`` working
but emits a DeprecationWarning. Prefer ``client.short_codes`` (no import needed). PYTHON-ONLY: the
surface oracle skips this file, so no other port implements these.
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.short_codes is deprecated; use client.short_codes. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import ShortCodes  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
ShortCodesResource = ShortCodes

__all__ = ["ShortCodesResource"]
