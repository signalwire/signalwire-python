"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

SignalWire Agents Local Search Module

This module provides local search capabilities for the SignalWire Agents SDK.
It requires additional dependencies that can be installed with:

    pip install signalwire-sdk[search]           # Basic search
    pip install signalwire-sdk[search-full]      # + Document processing
    pip install signalwire-sdk[search-nlp]       # + Advanced NLP
    pip install signalwire-sdk[search-all]       # All features
"""

import warnings
from typing import Any

# Check for core search dependencies
_SEARCH_AVAILABLE = True
_MISSING_DEPS: list[str] = []

# These bare imports probe for optional-dependency availability; the import
# itself is the test, so the bound name is intentionally unused (F401).
try:
    import numpy  # noqa: F401
except ImportError:
    _SEARCH_AVAILABLE = False
    _MISSING_DEPS.append("numpy")

try:
    import sklearn  # noqa: F401
except ImportError:
    _SEARCH_AVAILABLE = False
    _MISSING_DEPS.append("scikit-learn")

try:
    import sentence_transformers  # noqa: F401
except ImportError:
    _SEARCH_AVAILABLE = False
    _MISSING_DEPS.append("sentence-transformers")

try:
    import nltk  # noqa: F401
except ImportError:
    _SEARCH_AVAILABLE = False
    _MISSING_DEPS.append("nltk")


def _check_search_dependencies() -> None:
    """Check if search dependencies are available and provide helpful error message"""
    if not _SEARCH_AVAILABLE:
        missing = ", ".join(_MISSING_DEPS)
        raise ImportError(
            f"Search functionality requires additional dependencies: {missing}\n"
            f"Install with: pip install signalwire-sdk[search]\n"
            f"For full features: pip install signalwire-sdk[search-all]"
        )


# Conditional imports based on available dependencies
__all__ = []

if _SEARCH_AVAILABLE:
    try:
        from .query_processor import preprocess_query, preprocess_document_content
        from .document_processor import DocumentProcessor
        from .index_builder import IndexBuilder
        from .search_engine import SearchEngine
        from .search_service import SearchService
        from .models import MODEL_ALIASES, DEFAULT_MODEL, resolve_model_alias
        from .migration import SearchIndexMigrator

        __all__ = [
            "DEFAULT_MODEL",
            "MODEL_ALIASES",
            "DocumentProcessor",
            "IndexBuilder",
            "SearchEngine",
            "SearchIndexMigrator",
            "SearchService",
            "preprocess_document_content",
            "preprocess_query",
            "resolve_model_alias",
        ]
    except ImportError as e:
        # Some search components failed to import
        warnings.warn(
            f"Some search components failed to import: {e}\n"
            f"For full search functionality, install: pip install signalwire-sdk[search-all]",
            ImportWarning,
            stacklevel=2,
        )

        # Try to import what we can
        try:
            from .query_processor import preprocess_query, preprocess_document_content

            __all__.extend(["preprocess_document_content", "preprocess_query"])
        except ImportError:
            pass

        try:
            from .document_processor import DocumentProcessor

            __all__.append("DocumentProcessor")
        except ImportError:
            pass
else:
    # Provide stub functions that give helpful error messages.
    # These conditional fallbacks intentionally shadow the real imports above
    # when optional deps are absent; mypy can't model that mutual exclusion.
    def preprocess_query(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        _check_search_dependencies()

    def preprocess_document_content(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        _check_search_dependencies()

    class DocumentProcessor:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _check_search_dependencies()

    class IndexBuilder:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _check_search_dependencies()

    class SearchEngine:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _check_search_dependencies()

    class SearchService:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _check_search_dependencies()

    __all__ = [
        "DocumentProcessor",
        "IndexBuilder",
        "SearchEngine",
        "SearchService",
        "preprocess_document_content",
        "preprocess_query",
    ]
