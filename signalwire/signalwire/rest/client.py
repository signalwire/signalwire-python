"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

RestClient — top-level REST client with namespaced sub-objects.
"""

import os
from ._base import HttpClient
from .namespaces.fabric import FabricNamespace
from .namespaces.calling import Calling
from .namespaces.phone_numbers import PhoneNumbers
from .namespaces.addresses import Addresses
from .namespaces.queues import Queues
from .namespaces.recordings import Recordings
from .namespaces.number_groups import NumberGroups
from .namespaces.verified_callers import VerifiedCallers
from .namespaces.sip_profile import SipProfile
from .namespaces.lookup import Lookup
from .namespaces.short_codes import ShortCodes
from .namespaces.imported_numbers import ImportedNumbers
from .namespaces.mfa import Mfa
from .namespaces.registry import RegistryNamespace
from .namespaces.datasphere import DatasphereNamespace
from .namespaces.video import VideoNamespace
from .namespaces.logs import LogsNamespace
from .namespaces.project import ProjectNamespace
from .namespaces.pubsub import PubSub
from .namespaces.chat import Chat
from .namespaces.compat import CompatNamespace


class RestClient:
    """REST client for the SignalWire platform APIs.

    Usage:
        client = RestClient(
            project="your-project-id",
            token="your-api-token",
            host="your-space.signalwire.com",
        )

        # Or use environment variables:
        #   SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN, SIGNALWIRE_SPACE
        client = RestClient()

        # Use namespaced resources
        client.fabric.ai_agents.list()
        client.calling.play(call_id, play=[...])
        client.phone_numbers.search(area_code="512")
        client.video.rooms.create(name="standup")
        client.compat.calls.list()
    """

    def __init__(self, project=None, token=None, host=None):
        project = project or os.environ.get("SIGNALWIRE_PROJECT_ID", "")
        token = token or os.environ.get("SIGNALWIRE_API_TOKEN", "")
        host = host or os.environ.get("SIGNALWIRE_SPACE", "")

        if not project or not token or not host:
            raise ValueError(
                "project, token, and host are required. "
                "Provide them as arguments or set SIGNALWIRE_PROJECT_ID, "
                "SIGNALWIRE_API_TOKEN, and SIGNALWIRE_SPACE environment variables."
            )

        self._project = project
        self._http = HttpClient(project, token, host)

        # Fabric API
        self.fabric = FabricNamespace(self._http)

        # Calling API
        self.calling = Calling(self._http)

        # Relay REST resources
        self.phone_numbers = PhoneNumbers(self._http)
        self.addresses = Addresses(self._http)
        self.queues = Queues(self._http)
        self.recordings = Recordings(self._http)
        self.number_groups = NumberGroups(self._http)
        self.verified_callers = VerifiedCallers(self._http)
        self.sip_profile = SipProfile(self._http)
        self.lookup = Lookup(self._http)
        self.short_codes = ShortCodes(self._http)
        self.imported_numbers = ImportedNumbers(self._http)
        self.mfa = Mfa(self._http)
        self.registry = RegistryNamespace(self._http)

        # Datasphere API
        self.datasphere = DatasphereNamespace(self._http)

        # Video API
        self.video = VideoNamespace(self._http)

        # Logs
        self.logs = LogsNamespace(self._http)

        # Project management
        self.project = ProjectNamespace(self._http)

        # PubSub & Chat
        self.pubsub = PubSub(self._http)
        self.chat = Chat(self._http)

        # Compatibility (Twilio-compatible) API
        self.compat = CompatNamespace(self._http, project)
