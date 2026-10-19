"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import warnings
from collections.abc import Mapping
from typing import Any

# Embedding model configuration
MODEL_ALIASES = {
    "mini": "sentence-transformers/all-MiniLM-L6-v2",  # 384 dims, ~5x faster
    "base": "sentence-transformers/all-mpnet-base-v2",  # 768 dims, balanced
    # Deprecated: the same model as base. It can't point at a different
    # model, because indexes built with it would stop matching their queries.
    "large": "sentence-transformers/all-mpnet-base-v2",
}

LARGE_ALIAS_DEPRECATION = (
    "The 'large' model alias is deprecated: it loads the same model as 'base' "
    "(sentence-transformers/all-mpnet-base-v2). Use 'base' instead."
)

# Default model for new indexes
DEFAULT_MODEL = MODEL_ALIASES["mini"]


def resolve_model_alias(model_name: str) -> str:
    """
    Resolve model alias to full model name

    Args:
        model_name: Model name or alias (mini or base; large is deprecated)

    Returns:
        Full model name
    """
    if model_name == "large":
        warnings.warn(LARGE_ALIAS_DEPRECATION, DeprecationWarning, stacklevel=2)
    return MODEL_ALIASES.get(model_name, model_name)


# Metadata keys naming the document a chunk came from, most specific first.
# `document` lets an index state it outright. Without it, a page URL or a
# repo:path source is the next-best identity, and the file the chunk was read
# from is the last resort -- which is right for one-document-per-file indexes
# and wrong for JSON collections, where one file holds many documents.
DOCUMENT_KEYS = ("document", "url", "source", "filename")


def document_key(metadata: Mapping[str, Any] | None) -> str | None:
    """Identify the document a chunk belongs to, or None if nothing says.

    Used wherever "the same document" matters: resetting heading context
    between documents in a JSON file, and penalising several chunks of one
    document in a result list. One definition, so the two cannot disagree.
    """
    if not metadata:
        return None
    for key in DOCUMENT_KEYS:
        value = metadata.get(key)
        if value:
            return str(value)
    return None
