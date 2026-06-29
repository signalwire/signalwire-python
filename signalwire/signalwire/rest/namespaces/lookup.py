"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

This module path and the *Resource / *Namespace names below were superseded when the
REST layer became spec-generated (classes moved to ``*_resources_generated.py`` and lost
their suffixes). This thin re-export keeps old Python imports
(``from signalwire.signalwire.rest.namespaces.lookup import LookupResource``) working. New code
should import from the generated module / use ``client.lookup`` instead. PYTHON-ONLY: the
surface oracle skips this file (the marker above), so no other port implements these.
"""

from .relay_rest_resources_generated import Lookup

# Back-compat aliases (old name -> generated bare name):
LookupResource = Lookup

__all__ = ["LookupResource"]
