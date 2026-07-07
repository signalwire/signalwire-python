"""Deprecated import path for ``datasphere`` REST symbols.

These symbols moved out of ``namespaces.datasphere`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.datasphere import DatasphereDocuments``
working but emits a :class:`DeprecationWarning`. Prefer ``client.datasphere`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.datasphere is deprecated; use client.datasphere. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .datasphere_resources_generated import DatasphereDocuments  # noqa: E402  (re-export after the deprecation warn — intentional)
from ._client_tree_generated import DatasphereNamespace  # noqa: E402  (re-export after the deprecation warn — intentional)

__all__ = ["DatasphereDocuments", "DatasphereNamespace"]
