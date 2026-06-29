"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

Deprecated import path. The REST layer is spec-generated; these symbols moved out of
``namespaces.datasphere`` (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.datasphere import DatasphereDocuments`` working
but emits a DeprecationWarning. Prefer ``client.datasphere`` (no import needed). PYTHON-ONLY: the
surface oracle skips this file, so no other port implements these.
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
