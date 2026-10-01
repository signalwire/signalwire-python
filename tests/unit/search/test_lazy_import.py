"""
Tests for the search package's lazy imports.

The package used to import sentence-transformers, NLTK, numpy and
scikit-learn as soon as anything imported it, even a light submodule such
as models. That made `sw-search --help` and every chunk-only sw-search run
take about 15 seconds. Now the package probes for those dependencies with
importlib.util.find_spec and imports a component only when it's first used.
"""

import subprocess
import sys
from importlib.util import find_spec

import pytest

HEAVY = ("sentence_transformers", "nltk", "sklearn", "torch")


def _run(code: str) -> list[str]:
    completed = subprocess.run(  # noqa: S603  # fixed arguments: this interpreter and a test-literal script
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=180
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip().splitlines()


def test_importing_sw_search_does_not_load_the_model_stack() -> None:
    out = _run(
        "import sys, signalwire.cli.build_search\n"
        f"print(sorted(m for m in {HEAVY!r} if m in sys.modules))"
    )
    assert out[-1] == "[]"


def test_components_resolve_on_first_use() -> None:
    import signalwire.search as search

    assert search.SearchEngine.__name__ == "SearchEngine"
    assert search.IndexBuilder.__module__ == "signalwire.search.index_builder"
    assert search.resolve_model_alias("mini") == search.MODEL_ALIASES["mini"]
    for name in search.__all__:
        assert getattr(search, name) is not None
    with pytest.raises(AttributeError):
        search.NoSuchThing  # noqa: B018  # attribute access is the test


@pytest.mark.skipif(
    any(
        find_spec(m) is None
        for m in ("numpy", "sklearn", "sentence_transformers", "nltk")
    ),
    reason="needs the search extras installed",
)
def test_available_when_the_dependencies_are_installed() -> None:
    import signalwire.search as search

    assert search._SEARCH_AVAILABLE is True
    assert search._MISSING_DEPS == []


def test_missing_dependency_gives_stubs_with_the_install_hint() -> None:
    out = _run(
        "import importlib.util\n"
        "real = importlib.util.find_spec\n"
        "importlib.util.find_spec = lambda name, *a, **k: "
        "None if name == 'sentence_transformers' else real(name, *a, **k)\n"
        "import signalwire.search as s\n"
        "print(s._SEARCH_AVAILABLE, s._MISSING_DEPS)\n"
        "try:\n"
        "    s.SearchEngine()\n"
        "except ImportError as e:\n"
        "    print('hint' if 'pip install signalwire-sdk[search]' in str(e) else 'no hint')\n"
        "from signalwire.search import preprocess_query, DocumentProcessor\n"
        "print('stubs importable')\n"
    )
    assert out == ["False ['sentence-transformers']", "hint", "stubs importable"]
