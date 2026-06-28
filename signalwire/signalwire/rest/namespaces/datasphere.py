"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Datasphere API namespace — document management and semantic search.

The document resource is generated from the canonical spec (see
``datasphere_resources_generated``).
"""

from typing import Any

from .datasphere_resources_generated import DatasphereDocuments

__all__ = ["DatasphereDocuments", "DatasphereNamespace"]


class DatasphereNamespace:
    """Datasphere API namespace."""

    def __init__(self, http: Any) -> None:
        self.documents = DatasphereDocuments(http)
