"""Shared fixtures for skill unit tests.

PY-8 (Wave 1) made the SDK library-safe: ``import signalwire`` no longer
configures global logging, so ``get_logger()`` returns a lazy structlog proxy
whose underlying stdlib logger (and thus ``.name``) is only resolved once the
application opts in via ``configure_logging()``. Skill tests that assert a
skill's ``logger.name`` are testing a *configured* logger's identity, so
configure logging once for this test package. This mirrors what a real
deployment does at its serve/run entry point.
"""
from __future__ import annotations

import pytest

from signalwire.core.logging_config import configure_logging


@pytest.fixture(autouse=True)
def _configure_sdk_logging() -> None:
    """Ensure SDK logging is configured so lazy loggers resolve their name."""
    configure_logging()
