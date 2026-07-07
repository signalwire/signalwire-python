"""Deprecated import path for ``phone_numbers`` REST symbols.

These symbols moved out of ``namespaces.phone_numbers`` when the REST layer was
regenerated (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.phone_numbers import PhoneNumbersResource``
working but emits a :class:`DeprecationWarning`. Prefer ``client.phone_numbers`` instead
(no import needed).
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.phone_numbers is deprecated; use client.phone_numbers. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .relay_rest_resources_generated import PhoneNumbers  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
PhoneNumbersResource = PhoneNumbers

__all__ = ["PhoneNumbersResource"]
