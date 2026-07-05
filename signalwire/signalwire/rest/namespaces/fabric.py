"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

Deprecated import path. The REST layer is spec-generated; these symbols moved out of
``namespaces.fabric`` (the ``*Resource``/``*Namespace`` suffixes were dropped). This thin
re-export keeps ``from signalwire.signalwire.rest.namespaces.fabric import FabricResource`` working
but emits a DeprecationWarning. Prefer ``client.fabric`` (no import needed). PYTHON-ONLY: the
surface oracle skips this file, so no other port implements these.
"""

import warnings

warnings.warn(
    "signalwire.signalwire.rest.namespaces.fabric is deprecated; use client.fabric. "
    "This back-compat shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .._base import FabricResource, FabricResourcePUT  # noqa: E402  (re-export after the deprecation warn — intentional)
from .fabric_resources_generated import (  # noqa: E402  (re-export after the deprecation warn — intentional)
    CallFlows,
    ConferenceRooms,
    CxmlApplications,
    CxmlWebhooks,
    FabricAddresses,
    FabricTokens,
    GenericResources,
    Subscribers,
    SwmlWebhooks,
)
from ._client_tree_generated import FabricNamespace  # noqa: E402  (re-export after the deprecation warn — intentional)

# Back-compat aliases (old name -> generated bare name):
SwmlWebhooksResource = SwmlWebhooks
CxmlWebhooksResource = CxmlWebhooks
CallFlowsResource = CallFlows
ConferenceRoomsResource = ConferenceRooms
SubscribersResource = Subscribers
CxmlApplicationsResource = CxmlApplications

__all__ = [
    "CallFlowsResource",
    "ConferenceRoomsResource",
    "CxmlApplicationsResource",
    "CxmlWebhooksResource",
    "FabricAddresses",
    "FabricNamespace",
    "FabricResource",
    "FabricResourcePUT",
    "FabricTokens",
    "GenericResources",
    "SubscribersResource",
    "SwmlWebhooksResource",
]
