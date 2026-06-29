"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

This module path and the *Resource / *Namespace names below were superseded when the
REST layer became spec-generated (classes moved to ``*_resources_generated.py`` and lost
their suffixes). This thin re-export keeps old Python imports
(``from signalwire.signalwire.rest.namespaces.fabric import FabricResource``) working. New code
should import from the generated module / use ``client.fabric`` instead. PYTHON-ONLY: the
surface oracle skips this file (the marker above), so no other port implements these.
"""

from .._base import FabricResource, FabricResourcePUT
from .fabric_resources_generated import CallFlows, ConferenceRooms, CxmlApplications, CxmlWebhooks, FabricAddresses, FabricTokens, GenericResources, Subscribers, SwmlWebhooks
from ._client_tree_generated import FabricNamespace

# Back-compat aliases (old name -> generated bare name):
SwmlWebhooksResource = SwmlWebhooks
CxmlWebhooksResource = CxmlWebhooks
CallFlowsResource = CallFlows
ConferenceRoomsResource = ConferenceRooms
SubscribersResource = Subscribers
CxmlApplicationsResource = CxmlApplications

__all__ = ["CallFlowsResource", "ConferenceRoomsResource", "CxmlApplicationsResource", "CxmlWebhooksResource", "FabricAddresses", "FabricNamespace", "FabricResource", "FabricResourcePUT", "FabricTokens", "GenericResources", "SubscribersResource", "SwmlWebhooksResource"]
