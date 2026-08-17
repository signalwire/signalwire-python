"""Deprecated import path for ``recordings`` REST symbols.

These symbols moved out of ``namespaces.recordings`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.rest.namespaces.recordings import RecordingsResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.recordings`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.rest.namespaces.recordings is deprecated; use client.recordings. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import Recordings  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
RecordingsResource = Recordings

__all__ = ["RecordingsResource"]
