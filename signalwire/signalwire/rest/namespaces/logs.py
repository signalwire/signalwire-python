"""Back-compat shim — DO NOT add to other ports. x-sdk-back-compat-shim

This module path and the *Resource / *Namespace names below were superseded when the
REST layer became spec-generated (classes moved to ``*_resources_generated.py`` and lost
their suffixes). This thin re-export keeps old Python imports
(``from signalwire.signalwire.rest.namespaces.logs import MessageLogs``) working. New code
should import from the generated module / use ``client.logs`` instead. PYTHON-ONLY: the
surface oracle skips this file (the marker above), so no other port implements these.
"""

from .message_resources_generated import MessageLogs
from .voice_resources_generated import VoiceLogs
from .fax_resources_generated import FaxLogs
from .logs_resources_generated import ConferenceLogs
from ._client_tree_generated import LogsNamespace

__all__ = ["ConferenceLogs", "FaxLogs", "LogsNamespace", "MessageLogs", "VoiceLogs"]
