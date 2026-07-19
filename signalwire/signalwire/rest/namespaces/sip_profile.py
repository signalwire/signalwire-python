"""Deprecated import path for ``sip_profile`` REST symbols.

These symbols moved out of ``namespaces.sip_profile`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.rest.namespaces.sip_profile import SipProfileResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.sip_profile`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.rest.namespaces.sip_profile is deprecated; use client.sip_profile. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import SipProfile  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
SipProfileResource = SipProfile

__all__ = ["SipProfileResource"]
