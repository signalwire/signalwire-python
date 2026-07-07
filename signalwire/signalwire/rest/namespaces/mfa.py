"""Deprecated import path for ``mfa`` REST symbols.

These symbols moved out of ``namespaces.mfa`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.mfa import MfaResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.mfa`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.mfa is deprecated; use client.mfa. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import Mfa  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
MfaResource = Mfa

__all__ = ["MfaResource"]
