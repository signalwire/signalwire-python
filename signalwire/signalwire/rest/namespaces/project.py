"""Deprecated import path for ``project`` REST symbols.

These symbols moved out of ``namespaces.project`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.rest.namespaces.project import ProjectTokens``
working but emits a :class:`DeprecationWarning`. Prefer ``client.project`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.rest.namespaces.project is deprecated; use client.project. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .project_resources_generated import ProjectTokens  # noqa: E402  (re-export after the deprecation warn — intentional)
from ._client_tree_generated import ProjectNamespace  # noqa: E402  (re-export after the deprecation warn — intentional)

__all__ = ["ProjectNamespace", "ProjectTokens"]
