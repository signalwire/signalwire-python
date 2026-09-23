"""
Tests for SearchIndexMigrator.migrate_pgvector_to_sqlite, which isn't
implemented yet.

It used to delete any index at its output path, write an empty one, and
report success with zero errors. It must now raise before it connects to the
database or touches the output path.
"""

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from signalwire.search.migration import SearchIndexMigrator


def _index_with_rows(path: Path, rows: int) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.execute("CREATE TABLE chunks (id INTEGER PRIMARY KEY, content TEXT)")
        conn.executemany(
            "INSERT INTO chunks (content) VALUES (?)",
            [(f"row {i}",) for i in range(rows)],
        )
        conn.commit()
    finally:
        conn.close()


class TestMigratePgvectorToSqlite:
    def test_leaves_an_existing_index_unchanged(self, tmp_path: Path) -> None:
        output = tmp_path / "existing.swsearch"
        _index_with_rows(output, 250)
        before = output.read_bytes()

        with patch("signalwire.search.pgvector_backend.PgVectorBackend") as backend:
            with pytest.raises(NotImplementedError):
                SearchIndexMigrator().migrate_pgvector_to_sqlite(
                    "postgresql://localhost/db", "docs", str(output)
                )

        backend.assert_not_called()
        assert output.read_bytes() == before

    def test_creates_no_output_file(self, tmp_path: Path) -> None:
        output = tmp_path / "new.swsearch"

        with patch("signalwire.search.pgvector_backend.PgVectorBackend") as backend:
            with pytest.raises(NotImplementedError):
                SearchIndexMigrator().migrate_pgvector_to_sqlite(
                    "postgresql://localhost/db", "docs", str(output)
                )

        backend.assert_not_called()
        assert not output.exists()
