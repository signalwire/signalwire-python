"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Project API namespace — API token management. The token resource is generated from the
canonical spec (see ``project_resources_generated``); this is the thin namespace that
exposes it as ``client.project.tokens``.
"""

from typing import Any

from .project_resources_generated import ProjectTokens

__all__ = ["ProjectNamespace", "ProjectTokens"]


class ProjectNamespace:
    """Project API namespace."""

    def __init__(self, http: Any) -> None:
        self.tokens = ProjectTokens(http)
