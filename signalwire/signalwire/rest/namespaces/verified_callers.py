"""Deprecated import path for ``verified_callers`` REST symbols.

These symbols moved out of ``namespaces.verified_callers`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.verified_callers import VerifiedCallersResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.verified_callers`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.verified_callers is deprecated; use client.verified_callers. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import VerifiedCallers  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
VerifiedCallersResource = VerifiedCallers

__all__ = ["VerifiedCallersResource"]
