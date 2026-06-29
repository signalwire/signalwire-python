"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

This module path and the *Resource / *Namespace names below were superseded when the
REST layer became spec-generated (classes moved to ``*_resources_generated.py`` and lost
their suffixes). This thin re-export keeps old Python imports
(``from signalwire.signalwire.rest.namespaces.addresses import AddressesResource``) working. New code
should import from the generated module / use ``client.addresses`` instead. PYTHON-ONLY: the
surface oracle skips this file (the marker above), so no other port implements these.
"""

from .relay_rest_resources_generated import Addresses

# Back-compat aliases (old name -> generated bare name):
AddressesResource = Addresses

__all__ = ["AddressesResource"]
