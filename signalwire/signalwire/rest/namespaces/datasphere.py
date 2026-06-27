"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Datasphere API namespace — document management and semantic search.

The document resource is generated from the canonical spec (see
``datasphere_resources_generated``).
"""

from .datasphere_resources_generated import DatasphereDocumentsResource

# Back-compat alias: the resource was historically named ``DatasphereDocuments``.
DatasphereDocuments = DatasphereDocumentsResource

__all__ = ["DatasphereDocuments", "DatasphereDocumentsResource", "DatasphereNamespace"]


class DatasphereNamespace:
    """Datasphere API namespace."""

    def __init__(self, http):
        self.documents = DatasphereDocumentsResource(http)
