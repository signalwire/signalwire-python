"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The NLTK data search uses, and fetching it.

Search never downloads anything while it runs: a process that answers calls
shouldn't reach the internet for data mid-request. Fetch the data once, when
you set up a machine or build an image, with ``sw-search download-nltk`` or
:func:`download_nltk_data`. Without it, search still works, with simpler
sentence splitting and query processing, and logs once which data is missing.
"""

from __future__ import annotations

import threading

from signalwire.core.logging_config import get_logger

logger = get_logger(__name__)

NLTK_DATA = {
    "punkt_tab": "tokenizers/punkt_tab",
    "averaged_perceptron_tagger_eng": "taggers/averaged_perceptron_tagger_eng",
    "wordnet": "corpora/wordnet",
    "stopwords": "corpora/stopwords",
}
"""The NLTK data search uses, by name, with where NLTK keeps each one."""

_noted: set[str] = set()
_noted_lock = threading.Lock()


def missing_nltk_data() -> list[str]:
    """The names of the NLTK data search uses that aren't installed.

    Returns all of them when NLTK itself isn't installed.
    """
    try:
        import nltk
    except ImportError:
        return list(NLTK_DATA)
    missing = []
    for name, path in NLTK_DATA.items():
        try:
            nltk.data.find(path)
        except LookupError:  # noqa: PERF203  # each resource is looked up on its own
            missing.append(name)
    return missing


def download_nltk_data(quiet: bool = True) -> list[str]:
    """Download the NLTK data search uses that isn't installed yet, into
    NLTK's data path (the ``NLTK_DATA`` environment variable, if set).

    Run it once, when you set up a machine or build an image; search itself
    never downloads.

    Args:
        quiet: Whether to leave out NLTK's own progress output.

    Returns:
        The names that are still missing afterwards; empty when it's all there.

    Raises:
        ImportError: When NLTK isn't installed.
    """
    import nltk

    for name in missing_nltk_data():
        try:
            nltk.download(name, quiet=quiet)
        except Exception as e:  # noqa: PERF203  # each resource is fetched on its own
            logger.warning(f"Couldn't download NLTK data '{name}': {e}")
    return missing_nltk_data()


def note_missing(name: str) -> None:
    """Log, once per process, that a piece of NLTK data is missing and what
    search does without it."""
    with _noted_lock:
        if name in _noted:
            return
        _noted.add(name)
    logger.warning(
        f"NLTK data '{name}' isn't installed, so search uses a simpler fallback. "
        "Run 'sw-search download-nltk' once to install it."
    )


__all__ = ["NLTK_DATA", "download_nltk_data", "missing_nltk_data"]
