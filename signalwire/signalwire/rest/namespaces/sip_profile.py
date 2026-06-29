"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

This module path and the *Resource / *Namespace names below were superseded when the
REST layer became spec-generated (classes moved to ``*_resources_generated.py`` and lost
their suffixes). This thin re-export keeps old Python imports
(``from signalwire.signalwire.rest.namespaces.sip_profile import SipProfileResource``) working. New code
should import from the generated module / use ``client.sip_profile`` instead. PYTHON-ONLY: the
surface oracle skips this file (the marker above), so no other port implements these.
"""

from .relay_rest_resources_generated import SipProfile

# Back-compat aliases (old name -> generated bare name):
SipProfileResource = SipProfile

__all__ = ["SipProfileResource"]
