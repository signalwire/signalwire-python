"""Deprecated import path for ``number_groups`` REST symbols.

These symbols moved out of ``namespaces.number_groups`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.rest.namespaces.number_groups import NumberGroupsResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.number_groups`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.rest.namespaces.number_groups is deprecated; use client.number_groups. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import NumberGroups  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
NumberGroupsResource = NumberGroups

__all__ = ["NumberGroupsResource"]
