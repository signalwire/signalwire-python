"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

``PhoneCallHandler`` moved into the spec-generated types module. The public import
``from signalwire.signalwire.rest import PhoneCallHandler`` was never broken; this re-export
keeps the old DEEP path ``...rest.call_handler import PhoneCallHandler`` working too.
PYTHON-ONLY: the surface oracle skips this file.
"""

from .namespaces.relay_rest_types_generated import PhoneCallHandler

__all__ = ["PhoneCallHandler"]
