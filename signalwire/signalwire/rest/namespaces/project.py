"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

Deprecated import path. The REST layer is spec-generated; these symbols moved out of
``namespaces.project`` (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.project import ProjectTokens`` working
but emits a DeprecationWarning. Prefer ``client.project`` (no import needed). PYTHON-ONLY: the
surface oracle skips this file, so no other port implements these.
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.project is deprecated; use client.project. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .project_resources_generated import ProjectTokens  # noqa: E402  (re-export after the deprecation warn — intentional)
from ._client_tree_generated import ProjectNamespace  # noqa: E402  (re-export after the deprecation warn — intentional)

__all__ = ["ProjectNamespace", "ProjectTokens"]
