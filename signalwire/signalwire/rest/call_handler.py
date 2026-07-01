"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

Deprecated import path. ``PhoneCallHandler`` moved into the spec-generated types module.
``from signalwire.signalwire.rest import PhoneCallHandler`` is the supported import; this
re-export keeps the old DEEP path ``...rest.call_handler import PhoneCallHandler`` working but
emits a DeprecationWarning. PYTHON-ONLY: the surface oracle skips this file.
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
