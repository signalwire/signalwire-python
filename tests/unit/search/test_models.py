"""
Tests for the embedding model aliases.

The 'large' alias loads the same model as 'base'. It's deprecated rather than
pointed at a bigger model, because indexes built with it would stop matching
their queries (B11).
"""

import warnings

import pytest

from signalwire.search.models import MODEL_ALIASES, resolve_model_alias


def test_large_warns_and_still_loads_base() -> None:
    with pytest.warns(DeprecationWarning, match="'large' model alias is deprecated"):
        assert resolve_model_alias("large") == MODEL_ALIASES["base"]


@pytest.mark.parametrize(
    "name", ["mini", "base", "sentence-transformers/all-MiniLM-L6-v2"]
)
def test_other_names_do_not_warn(name: str) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        assert resolve_model_alias(name) == MODEL_ALIASES.get(name, name)
