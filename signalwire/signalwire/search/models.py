"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import warnings

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
