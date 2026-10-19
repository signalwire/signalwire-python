"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

# Ranking by document, and the rank_weight prior.
#
# Diversity used to key on the file a chunk was read from. A JSON collection
# holds many documents in one file, so their chunks decayed each other: 50 rate
# cards in one pricing file, and the per-minute card for "outbound call pricing"
# fell from 9th by relevance to below the top 20.

from typing import Any

import pytest

from signalwire.search.models import document_key
from signalwire.search.search_engine import SearchEngine


def _engine() -> SearchEngine:
    # The stages under test use no index state.
    return SearchEngine.__new__(SearchEngine)


def _result(score: float, **metadata: Any) -> dict[str, Any]:
    return {"content": f"chunk {score} {sorted(metadata.items())}", "final_score": score, "metadata": metadata}


class TestDocumentKey:
    def test_precedence(self) -> None:
        md = {"document": "d", "url": "u", "source": "s", "filename": "f"}
        assert document_key(md) == "d"
        del md["document"]
        assert document_key(md) == "u"
        del md["url"]
        assert document_key(md) == "s"
        del md["source"]
        assert document_key(md) == "f"

    def test_empty_values_fall_through(self) -> None:
        assert document_key({"document": "", "url": None, "source": "repo:a.md"}) == "repo:a.md"

    def test_nothing_identifies_it(self) -> None:
        assert document_key(None) is None
        assert document_key({}) is None
        assert document_key({"title": "x"}) is None


class TestDiversityByDocument:
    def test_distinct_documents_in_one_file_are_not_penalised(self) -> None:
        results = [_result(0.9 - i / 100, filename="pricing.json", document=f"card{i}") for i in range(5)]
        out = _engine()._apply_diversity_penalties(results, 10)
        assert [r["diversity_penalty"] for r in out] == [1.0] * 5
        assert [r["metadata"]["document"] for r in out] == [f"card{i}" for i in range(5)]

    def test_chunks_of_one_document_still_decay(self) -> None:
        results = [_result(0.9 - i / 100, filename="docs.json", url="https://x/page") for i in range(3)]
        out = _engine()._apply_diversity_penalties(results, 10)
        assert [r["diversity_penalty"] for r in out] == [1.0, 0.85, 0.7]

    def test_filename_is_the_fallback(self) -> None:
        results = [_result(0.9 - i / 100, filename="guide.md") for i in range(2)]
        out = _engine()._apply_diversity_penalties(results, 10)
        assert [r["diversity_penalty"] for r in out] == [1.0, 0.85]

    def test_reselection_tolerates_results_without_metadata(self) -> None:
        # Enough same-document results to trigger the reselection pass, which
        # used to index metadata["filename"] directly and raise KeyError.
        results = [_result(0.9 - i / 100, url="https://x/one") for i in range(6)]
        results.append({"content": "no metadata", "final_score": 0.6, "metadata": {}})
        out = _engine()._apply_diversity_penalties(results, 3)
        assert len(out) == 7


class TestRankWeight:
    @pytest.mark.parametrize(
        "value,expected",
        [(0.85, 0.85), (1, 1.0), (0.5, 0.5), (0, 1.0), (-0.2, 1.0), (1.5, 1.0), (True, 1.0), ("0.5", 1.0), (None, 1.0)],
    )
    def test_only_numbers_in_range_count(self, value: Any, expected: float) -> None:
        assert SearchEngine._rank_weight({"rank_weight": value}) == expected

    def test_missing_metadata(self) -> None:
        assert SearchEngine._rank_weight(None) == 1.0
        assert SearchEngine._rank_weight({}) == 1.0

    def _ranked(self, candidates: list[dict[str, Any]]) -> list[str]:
        out = _engine()._process_candidates(candidates, count=10)
        return [r["metadata"]["document"] for r in out]

    def test_weight_lets_reference_outrank_matching_commentary(self) -> None:
        candidates = [
            {"content": "commentary quoting a price", "vector_score": 0.70, "metadata": {"document": "commentary", "rank_weight": 0.85}},
            {"content": "the rate card", "vector_score": 0.65, "metadata": {"document": "rate-card"}},
        ]
        assert self._ranked(candidates) == ["rate-card", "commentary"]

    def test_weight_cannot_promote(self) -> None:
        candidates = [
            {"content": "weak match claiming weight 2", "vector_score": 0.60, "metadata": {"document": "weak", "rank_weight": 2.0}},
            {"content": "better match", "vector_score": 0.65, "metadata": {"document": "better"}},
        ]
        assert self._ranked(candidates) == ["better", "weak"]

    def test_unweighted_order_is_unchanged(self) -> None:
        candidates = [
            {"content": "second", "vector_score": 0.60, "metadata": {"document": "b"}},
            {"content": "first", "vector_score": 0.70, "metadata": {"document": "a"}},
        ]
        assert self._ranked(candidates) == ["a", "b"]
