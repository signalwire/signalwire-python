"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Search never downloads NLTK data while it runs: fetching it is an explicit
step, and without it search degrades.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

pytest.importorskip("nltk")

from signalwire.search import nltk_data  # noqa: E402
from signalwire.search.nltk_data import NLTK_DATA, download_nltk_data, missing_nltk_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]


def test_without_any_data_search_runs_and_downloads_nothing(tmp_path: Path) -> None:
    script = textwrap.dedent(
        f"""
        import nltk
        nltk.data.path[:] = [{str(tmp_path)!r}]

        def no_download(*args, **kwargs):
            raise AssertionError("search downloaded NLTK data")

        nltk.download = no_download

        from signalwire.search import missing_nltk_data
        from signalwire.search.document_processor import DocumentProcessor
        from signalwire.search.query_processor import preprocess_query

        assert sorted(missing_nltk_data()) == sorted({sorted(NLTK_DATA)!r})
        chunks = DocumentProcessor(max_sentences_per_chunk=1).create_chunks(
            "First one. Second one! Third?", "t.txt", "txt"
        )
        assert [c["content"] for c in chunks] == ["First one.", "Second one!", "Third?"], chunks
        result = preprocess_query("how do I reset my password", vector=False)
        assert "reset" in result["input"], result
        print("ok")
        """
    )
    run = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "signalwire"), "PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        timeout=240,
    )
    assert run.returncode == 0, run.stderr[-2000:]
    assert run.stdout.strip().endswith("ok")


def test_missing_nltk_data_names_what_isnt_installed(tmp_path: Path) -> None:
    import nltk

    with patch.object(nltk.data, "path", [str(tmp_path)]):
        assert sorted(missing_nltk_data()) == sorted(NLTK_DATA)


def test_download_nltk_data_fetches_only_whats_missing() -> None:
    calls: list[Any] = []
    with patch("signalwire.search.nltk_data.missing_nltk_data", side_effect=[["wordnet", "stopwords"], []]), \
         patch("nltk.download", side_effect=lambda name, quiet: calls.append(name)):
        assert download_nltk_data() == []
    assert calls == ["wordnet", "stopwords"]


def test_a_missing_piece_is_noted_once(caplog: pytest.LogCaptureFixture) -> None:
    nltk_data._noted.discard("punkt_tab")
    with patch.object(nltk_data.logger, "warning") as warning:
        nltk_data.note_missing("punkt_tab")
        nltk_data.note_missing("punkt_tab")
    warning.assert_called_once()
    assert "sw-search download-nltk" in warning.call_args.args[0]


def test_only_the_current_formats_are_used() -> None:
    assert set(NLTK_DATA) == {"punkt_tab", "averaged_perceptron_tagger_eng", "wordnet", "stopwords"}


def test_sw_search_download_nltk(capsys: pytest.CaptureFixture[str]) -> None:
    from signalwire.cli import build_search

    with patch("sys.argv", ["sw-search download-nltk"]), \
         patch("signalwire.search.nltk_data.missing_nltk_data", return_value=["wordnet"]), \
         patch("signalwire.search.nltk_data.download_nltk_data", return_value=[]) as download:
        build_search.download_nltk_command()
    download.assert_called_once_with(quiet=False)
    assert "NLTK data installed" in capsys.readouterr().out
