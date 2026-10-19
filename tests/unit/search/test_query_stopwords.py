"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

# Corpus-wide query terms.
#
# In a corpus about one product, the product's name carries no information and
# only rewards the chunks that spell it out: "SignalWire call pricing" ranked
# the phone-number rate cards ("can be ported into SignalWire") over the
# per-minute rates. An index declares such terms; search drops them from the
# query unless the query is about the name itself.

import asyncio
import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from signalwire.search.index_builder import IndexBuilder
from signalwire.search.query_processor import drop_corpus_terms
from signalwire.search.search_engine import SearchEngine


class TestDropCorpusTerms:
    @pytest.mark.parametrize(
        "query,expected",
        [
            ("SignalWire call pricing", "call pricing"),
            ("how much does SignalWire charge for an outbound call", "how much does charge for an outbound call"),
            ("signalwire AI agent", "AI agent"),
            ("SignalWire's outbound call rates", "outbound call rates"),
        ],
    )
    def test_drops_the_term(self, query: str, expected: str) -> None:
        assert drop_corpus_terms(query, ["SignalWire"]) == expected

    @pytest.mark.parametrize(
        "query",
        ["SignalWire", "what is SignalWire", "what does SignalWire do", "SignalWire architecture", "  SignalWire's  "],
    )
    def test_keeps_it_when_the_query_is_about_it(self, query: str) -> None:
        # Fewer than two content words would remain, so the query IS about the name.
        assert drop_corpus_terms(query, ["SignalWire"]) == query

    def test_phrases_and_several_terms(self) -> None:
        assert drop_corpus_terms("Acme Cloud pricing for voice calls", ["acme cloud"]) == "pricing for voice calls"
        assert drop_corpus_terms("Acme and Beta voice pricing", ["Acme", "Beta"]) == "and voice pricing"

    def test_word_boundaries(self) -> None:
        assert drop_corpus_terms("signalwired call pricing tips", ["SignalWire"]) == "signalwired call pricing tips"

    @pytest.mark.parametrize("terms", [[], [""], ["  "], None, "SignalWire", MagicMock()])
    def test_no_usable_terms_leaves_the_query_alone(self, terms: Any) -> None:
        assert drop_corpus_terms("SignalWire call pricing", terms) == "SignalWire call pricing"

    def test_no_match_returns_the_query_untouched(self) -> None:
        assert drop_corpus_terms("  call   pricing ", ["SignalWire"]) == "  call   pricing "


class TestQueryStopwordsFromIndexConfig:
    def _engine(self, config: Any) -> SearchEngine:
        engine = SearchEngine.__new__(SearchEngine)
        engine.config = config
        return engine

    def test_sqlite_config_stores_a_json_string(self) -> None:
        assert self._engine({"query_stopwords": '["SignalWire"]'}).query_stopwords == ["SignalWire"]

    def test_pgvector_config_keeps_it_in_metadata(self) -> None:
        assert self._engine({"metadata": {"query_stopwords": ["SignalWire", "Acme"]}}).query_stopwords == ["SignalWire", "Acme"]

    @pytest.mark.parametrize(
        "config",
        [{}, None, {"query_stopwords": "not json"}, {"query_stopwords": '{"a": 1}'}, {"metadata": {"query_stopwords": 5}}, {"metadata": None}],
    )
    def test_missing_or_malformed_means_none(self, config: Any) -> None:
        assert self._engine(config).query_stopwords == []

    def test_sqlite_index_records_the_terms(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            out = str(Path(d) / "t.swsearch")
            IndexBuilder(query_stopwords=[" SignalWire ", ""])._create_database(
                out, [{"content": "x", "filename": "a.md", "embedding": b"data"}], ["en"], ["a.md"], ["md"]
            )
            conn = sqlite3.connect(out)
            try:
                row = conn.execute("SELECT value FROM config WHERE key='query_stopwords'").fetchone()
            finally:
                conn.close()
        assert json.loads(row[0]) == ["SignalWire"]


class TestSearchServiceAppliesThem:
    def test_query_is_stripped_before_preprocessing(self) -> None:
        from signalwire.search.search_service import SearchService

        svc = SearchService()
        engine = MagicMock()
        engine.config = {}
        engine.query_stopwords = ["SignalWire"]
        engine.search.return_value = []
        svc.search_engines["default"] = engine

        request = Mock()
        request.query = "SignalWire call pricing"
        request.index_name = "default"
        request.count = 3
        request.similarity_threshold = 0.0
        request.tags = None
        request.language = None

        with patch("signalwire.search.search_service.preprocess_query") as pp:
            pp.return_value = {"enhanced_text": "call pricing", "vector": [0.1], "language": "en"}
            loop = asyncio.new_event_loop()
            try:
                response = loop.run_until_complete(svc._handle_search(request))
            finally:
                loop.close()

        assert pp.call_args.args[0] == "call pricing"
        # The caller's own words are still what the response reports.
        assert response.query_analysis is not None
        assert response.query_analysis["original_query"] == "SignalWire call pricing"
