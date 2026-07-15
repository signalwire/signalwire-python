# AUTO-GENERATED from porting-sdk/rest-apis/*/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# The SDK client object tree: one namespace container per x-sdk-namespace group
# plus the flat resources, wired from each resource's spec placement.
from __future__ import annotations

from typing import Any

from .calling_resources_generated import (
    Calling,
)
from .chat_resources_generated import (
    Chat,
)
from .datasphere_resources_generated import (
    DatasphereDocuments,
)
from .fabric_resources_generated import (
    AiAgents,
    CallFlows,
    ConferenceRooms,
    CxmlApplications,
    CxmlScripts,
    CxmlWebhooks,
    FabricAddresses,
    FabricTokens,
    FreeswitchConnectors,
    GenericResources,
    RelayApplications,
    SipEndpoints,
    SipGateways,
    Subscribers,
    SwmlScripts,
    SwmlWebhooks,
)
from .fax_resources_generated import (
    FaxLogs,
)
from .logs_resources_generated import (
    ConferenceLogs,
)
from .message_resources_generated import (
    MessageLogs,
)
from .messages_resources_generated import (
    Messages,
)
from .project_resources_generated import (
    ProjectTokens,
)
from .projects_resources_generated import (
    Projects,
)
from .pubsub_resources_generated import (
    PubSub,
)
from .relay_rest_resources_generated import (
    Addresses,
    ImportedNumbers,
    Lookup,
    Mfa,
    NumberGroups,
    PhoneNumbers,
    Queues,
    Recordings,
    RegistryBrands,
    RegistryCampaigns,
    RegistryNumbers,
    RegistryOrders,
    ShortCodes,
    SipProfile,
    VerifiedCallers,
)
from .video_resources_generated import (
    VideoConferenceTokens,
    VideoConferences,
    VideoRoomRecordings,
    VideoRoomSessions,
    VideoRoomTokens,
    VideoRooms,
    VideoStreams,
)
from .voice_resources_generated import (
    VoiceLogs,
)


class DatasphereNamespace:
    """Generated ``client.datasphere`` namespace."""

    def __init__(self, http: Any) -> None:
        self.documents = DatasphereDocuments(http)


class FabricNamespace:
    """Generated ``client.fabric`` namespace."""

    def __init__(self, http: Any) -> None:
        self.addresses = FabricAddresses(http)
        self.ai_agents = AiAgents(http)
        self.call_flows = CallFlows(http)
        self.conference_rooms = ConferenceRooms(http)
        self.cxml_applications = CxmlApplications(http)
        self.cxml_scripts = CxmlScripts(http)
        self.cxml_webhooks = CxmlWebhooks(http)
        self.freeswitch_connectors = FreeswitchConnectors(http)
        self.relay_applications = RelayApplications(http)
        self.resources = GenericResources(http)
        self.sip_endpoints = SipEndpoints(http)
        self.sip_gateways = SipGateways(http)
        self.subscribers = Subscribers(http)
        self.swml_scripts = SwmlScripts(http)
        self.swml_webhooks = SwmlWebhooks(http)
        self.tokens = FabricTokens(http)


class LogsNamespace:
    """Generated ``client.logs`` namespace."""

    def __init__(self, http: Any) -> None:
        self.conferences = ConferenceLogs(http)
        self.fax = FaxLogs(http)
        self.messages = MessageLogs(http)
        self.voice = VoiceLogs(http)


class ProjectNamespace:
    """Generated ``client.project`` namespace."""

    def __init__(self, http: Any) -> None:
        self.tokens = ProjectTokens(http)


class RegistryNamespace:
    """Generated ``client.registry`` namespace."""

    def __init__(self, http: Any) -> None:
        self.brands = RegistryBrands(http)
        self.campaigns = RegistryCampaigns(http)
        self.numbers = RegistryNumbers(http)
        self.orders = RegistryOrders(http)


class VideoNamespace:
    """Generated ``client.video`` namespace."""

    def __init__(self, http: Any) -> None:
        self.conference_tokens = VideoConferenceTokens(http)
        self.conferences = VideoConferences(http)
        self.room_recordings = VideoRoomRecordings(http)
        self.room_sessions = VideoRoomSessions(http)
        self.room_tokens = VideoRoomTokens(http)
        self.rooms = VideoRooms(http)
        self.streams = VideoStreams(http)


class _GeneratedResourceTree:
    """Generated resource wiring for ``RestClient`` (flat resources + namespaces)."""

    def _wire_resources(self, http: Any) -> None:
        self.addresses = Addresses(http)
        self.calling = Calling(http)
        self.chat = Chat(http)
        self.imported_numbers = ImportedNumbers(http)
        self.lookup = Lookup(http)
        self.messages = Messages(http)
        self.mfa = Mfa(http)
        self.number_groups = NumberGroups(http)
        self.phone_numbers = PhoneNumbers(http)
        self.projects = Projects(http)
        self.pubsub = PubSub(http)
        self.queues = Queues(http)
        self.recordings = Recordings(http)
        self.short_codes = ShortCodes(http)
        self.sip_profile = SipProfile(http)
        self.verified_callers = VerifiedCallers(http)
        self.datasphere = DatasphereNamespace(http)
        self.fabric = FabricNamespace(http)
        self.logs = LogsNamespace(http)
        self.project = ProjectNamespace(http)
        self.registry = RegistryNamespace(http)
        self.video = VideoNamespace(http)
