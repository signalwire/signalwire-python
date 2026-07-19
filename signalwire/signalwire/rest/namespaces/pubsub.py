"""Deprecated import path for ``pubsub`` REST symbols.

These symbols moved out of ``namespaces.pubsub`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.rest.namespaces.pubsub import PubSubResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.pubsub`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.rest.namespaces.pubsub is deprecated; use client.pubsub. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .pubsub_resources_generated import PubSub  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
PubSubResource = PubSub

__all__ = ["PubSubResource"]
