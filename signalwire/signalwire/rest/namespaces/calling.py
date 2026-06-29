"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

This module path and the *Resource / *Namespace names below were superseded when the
REST layer became spec-generated (classes moved to ``*_resources_generated.py`` and lost
their suffixes). This thin re-export keeps old Python imports
(``from signalwire.signalwire.rest.namespaces.calling import CallingNamespace``) working. New code
should import from the generated module / use ``client.calling`` instead. PYTHON-ONLY: the
surface oracle skips this file (the marker above), so no other port implements these.
"""

from .calling_resources_generated import Calling

# Back-compat aliases (old name -> generated bare name):
CallingNamespace = Calling

__all__ = ["CallingNamespace"]
