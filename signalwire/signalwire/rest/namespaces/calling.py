"""Deprecated import path for ``calling`` REST symbols.

These symbols moved out of ``namespaces.calling`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.rest.namespaces.calling import CallingNamespace``
working but emits a :class:`DeprecationWarning`. Prefer ``client.calling`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.rest.namespaces.calling is deprecated; use client.calling. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .calling_resources_generated import Calling  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
CallingNamespace = Calling

__all__ = ["CallingNamespace"]
