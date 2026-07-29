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

import importlib
import importlib.util
from typing import TYPE_CHECKING, Any

# The search stack (sentence-transformers, NLTK, numpy, scikit-learn) takes
# many seconds to import. This package imports it only when a component that
# needs it is first used, so importing a light submodule such as models, or
# running sw-search --help, doesn't pay for it.

# Optional dependencies: module name -> the package that provides it
_SEARCH_DEPENDENCIES = {
    "numpy": "numpy",
    "sklearn": "scikit-learn",
    "sentence_transformers": "sentence-transformers",
    "nltk": "nltk",
}

# Probe for them without importing them
_MISSING_DEPS: list[str] = [
    package
    for module, package in _SEARCH_DEPENDENCIES.items()
    if importlib.util.find_spec(module) is None
]
_SEARCH_AVAILABLE = not _MISSING_DEPS


def _check_search_dependencies() -> None:
    """Check if search dependencies are available and provide helpful error message"""
    if not _SEARCH_AVAILABLE:
        missing = ", ".join(_MISSING_DEPS)
        raise ImportError(
            f"Search functionality requires additional dependencies: {missing}\n"
            f"Install with: pip install signalwire-sdk[search]\n"
            f"For full features: pip install signalwire-sdk[search-all]"
        )


# Each public name, and the submodule that defines it. __getattr__ imports the
# submodule the first time the name is used.
_LAZY_EXPORTS = {
    "preprocess_query": "query_processor",
    "preprocess_document_content": "query_processor",
    "DocumentProcessor": "document_processor",
    "IndexBuilder": "index_builder",
    "SearchEngine": "search_engine",
    "SearchService": "search_service",
    "SearchIndexMigrator": "migration",
    "MODEL_ALIASES": "models",
    "DEFAULT_MODEL": "models",
    "resolve_model_alias": "models",
}

if TYPE_CHECKING:
    from .document_processor import DocumentProcessor
    from .index_builder import IndexBuilder
    from .migration import SearchIndexMigrator
    from .models import DEFAULT_MODEL, MODEL_ALIASES, resolve_model_alias
    from .query_processor import preprocess_document_content, preprocess_query
    from .search_engine import SearchEngine
    from .search_service import SearchService

if _SEARCH_AVAILABLE:
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
else:
    # Provide stub functions that give helpful error messages.
    # These conditional fallbacks intentionally shadow the real imports above
    # when optional deps are absent; mypy can't model that mutual exclusion.
    def preprocess_query(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        """Unavailable-dependency stub for :func:`.query_processor.preprocess_query`.

        Bound under this name only when one of numpy, scikit-learn,
        sentence-transformers or nltk is missing, so ``from signalwire.search
        import preprocess_query`` still succeeds without the extras installed.
        Accepts and ignores any arguments; it never preprocesses a query.

        Raises:
            ImportError: Always, naming the missing packages and the
                ``pip install signalwire-sdk[search]`` command that supplies them.
        """
        _check_search_dependencies()

    def preprocess_document_content(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        """Unavailable-dependency stub for
        :func:`.query_processor.preprocess_document_content`.

        Bound under this name only when the search extras are missing, so the
        import resolves and the failure is deferred to the call site with an
        actionable message rather than raised at import time.

        Raises:
            ImportError: Always, listing the missing search dependencies.
        """
        _check_search_dependencies()

    class DocumentProcessor:  # type: ignore[no-redef]
        """Unavailable-dependency stub for
        :class:`.document_processor.DocumentProcessor`.

        Substituted for the real chunker when the search extras are absent so
        that importing the name works; every attempt to construct one fails.
        """

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Reject construction because the search extras are not installed.

            Raises:
                ImportError: Always, listing the missing search dependencies.
            """
            _check_search_dependencies()

    class IndexBuilder:  # type: ignore[no-redef]
        """Unavailable-dependency stub for :class:`.index_builder.IndexBuilder`.

        Substituted for the real index builder when the search extras are
        absent; construction always fails rather than silently building nothing.
        """

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Reject construction because the search extras are not installed.

            Raises:
                ImportError: Always, listing the missing search dependencies.
            """
            _check_search_dependencies()

    class SearchEngine:  # type: ignore[no-redef]
        """Unavailable-dependency stub for :class:`.search_engine.SearchEngine`.

        Substituted for the real query engine when the search extras are absent.
        Note this stub is bound even for query-only workloads: embedding a query
        needs sentence-transformers, so no search can run without the extras.
        """

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Reject construction because the search extras are not installed.

            Raises:
                ImportError: Always, listing the missing search dependencies.
            """
            _check_search_dependencies()

    class SearchService:  # type: ignore[no-redef]
        """Unavailable-dependency stub for
        :class:`.search_service.SearchService`.

        Substituted for the real HTTP search service when the search extras are
        absent. Unlike the real class — which degrades to direct search when
        only FastAPI is missing — this stub cannot serve or search at all.
        """

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Reject construction because the search extras are not installed.

            Raises:
                ImportError: Always, listing the missing search dependencies.
            """
            _check_search_dependencies()

    __all__ = [
        "DocumentProcessor",
        "IndexBuilder",
        "SearchEngine",
        "SearchService",
        "preprocess_document_content",
        "preprocess_query",
    ]


def __getattr__(name: str) -> Any:
    """Import a search component the first time it's used (PEP 562)."""
    if not _SEARCH_AVAILABLE or name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        module = importlib.import_module(f".{_LAZY_EXPORTS[name]}", __name__)
    except ImportError as e:
        raise ImportError(
            f"{name} failed to import: {e}\n"
            f"For full search functionality, install: pip install signalwire-sdk[search-all]"
        ) from e
    value = getattr(module, name)
    globals()[name] = value
    return value
