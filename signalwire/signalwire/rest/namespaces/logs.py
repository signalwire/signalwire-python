"""Deprecated import path for ``logs`` REST symbols.

These symbols moved out of ``namespaces.logs`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.logs import MessageLogs``
working but emits a :class:`DeprecationWarning`. Prefer ``client.logs`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.logs is deprecated; use client.logs. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .message_resources_generated import MessageLogs  # noqa: E402  (re-export after the deprecation warn — intentional)
from .voice_resources_generated import VoiceLogs  # noqa: E402  (re-export after the deprecation warn — intentional)
from .fax_resources_generated import FaxLogs  # noqa: E402  (re-export after the deprecation warn — intentional)
from .logs_resources_generated import ConferenceLogs  # noqa: E402  (re-export after the deprecation warn — intentional)
from ._client_tree_generated import LogsNamespace  # noqa: E402  (re-export after the deprecation warn — intentional)

__all__ = ["ConferenceLogs", "FaxLogs", "LogsNamespace", "MessageLogs", "VoiceLogs"]
