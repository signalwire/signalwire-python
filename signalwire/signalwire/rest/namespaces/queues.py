"""Deprecated import path for ``queues`` REST symbols.

These symbols moved out of ``namespaces.queues`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.rest.namespaces.queues import QueuesResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.queues`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.rest.namespaces.queues is deprecated; use client.queues. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import Queues  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
QueuesResource = Queues

__all__ = ["QueuesResource"]
