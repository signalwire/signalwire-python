"""Deprecated import path for ``PhoneCallHandler``.

``PhoneCallHandler`` moved into the generated types module. Prefer
``from signalwire.signalwire.rest import PhoneCallHandler``. This re-export keeps the
old deep path ``...rest.call_handler import PhoneCallHandler`` working but emits a
:class:`DeprecationWarning`.
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.call_handler is deprecated; use "
    "`from signalwire.signalwire.rest import PhoneCallHandler`. This back-compat shim will "
    "be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .namespaces.relay_rest_types_generated import PhoneCallHandler  # noqa: E402  (re-export after the deprecation warn — intentional)

__all__ = ["PhoneCallHandler"]
