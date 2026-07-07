"""Deprecated import path for ``chat`` REST symbols.

These symbols moved out of ``namespaces.chat`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.chat import ChatResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.chat`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.chat is deprecated; use client.chat. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .chat_resources_generated import Chat  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
ChatResource = Chat

__all__ = ["ChatResource"]
