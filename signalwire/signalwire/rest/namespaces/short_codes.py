"""Deprecated import path for ``short_codes`` REST symbols.

These symbols moved out of ``namespaces.short_codes`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.rest.namespaces.short_codes import ShortCodesResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.short_codes`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.rest.namespaces.short_codes is deprecated; use client.short_codes. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import ShortCodes  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
ShortCodesResource = ShortCodes

__all__ = ["ShortCodesResource"]
