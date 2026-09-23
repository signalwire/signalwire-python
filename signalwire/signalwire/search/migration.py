"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import sqlite3
import json
from typing import Any, TYPE_CHECKING

from signalwire.core.logging_config import get_logger
from pathlib import Path

if TYPE_CHECKING:
    import numpy as np
else:
    try:
        import numpy as np
    except ImportError:
        np = None

logger = get_logger(__name__)


class SearchIndexMigrator:
    """Migrate search indexes between different backends"""

    def __init__(self, verbose: bool = False):
        """
        Initialize the migrator

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose

    def migrate_sqlite_to_pgvector(
        self,
        sqlite_path: str,
        connection_string: str,
        collection_name: str,
        overwrite: bool = False,
        batch_size: int = 100,
    ) -> dict[str, Any]:
        """
        Migrate a .swsearch SQLite index to pgvector

        Args:
            sqlite_path: Path to .swsearch file
            connection_string: PostgreSQL connection string
            collection_name: Name for the pgvector collection
            overwrite: Whether to overwrite existing collection
            batch_size: Number of chunks to insert at once

        Returns:
            Migration statistics
        """
        if not Path(sqlite_path).exists():
            raise FileNotFoundError(f"SQLite index not found: {sqlite_path}")

        # Import pgvector backend
        from .pgvector_backend import PgVectorBackend

        stats: dict[str, Any] = {
            "source": sqlite_path,
            "target": collection_name,
            "chunks_migrated": 0,
            "errors": 0,
            "config": {},
        }

        sqlite_conn = None
        try:
            # Connect to SQLite
            if self.verbose:
                print(f"Opening SQLite index: {sqlite_path}")

            sqlite_conn = sqlite3.connect(sqlite_path)
            cursor = sqlite_conn.cursor()

            # Load configuration
            cursor.execute("SELECT key, value FROM config")
            config_rows = cursor.fetchall()
            config = dict(config_rows)
            stats["config"] = config

            # Get important config values
            model_name = config.get(
                "embedding_model", "sentence-transformers/all-mpnet-base-v2"
            )
            embedding_dim = int(config.get("embedding_dimensions", 768))

            if self.verbose:
                print("Source configuration:")
                print(f"  Model: {model_name}")
                print(f"  Dimensions: {embedding_dim}")
                print(f"  Created: {config.get('created_at', 'Unknown')}")

            # Initialize pgvector backend
            pgvector = PgVectorBackend(connection_string)

            try:
                # Handle existing collection
                if overwrite:
                    if self.verbose:
                        print(f"Dropping existing collection: {collection_name}")
                    pgvector.delete_collection(collection_name)

                # Create schema
                if self.verbose:
                    print(f"Creating pgvector collection: {collection_name}")

                pgvector.create_schema(collection_name, embedding_dim)

                # Prepare collection config
                collection_config = {
                    "model_name": model_name,
                    "embedding_dimensions": embedding_dim,
                    "chunking_strategy": config.get("chunking_strategy", "sentence"),
                    "languages": json.loads(config.get("languages", '["en"]')),
                    "metadata": {
                        "migrated_from": sqlite_path,
                        "original_created": config.get("created_at"),
                        "source_dir": config.get("source_dir"),
                        "file_types": json.loads(config.get("file_types", "[]")),
                    },
                }

                # Count total chunks
                cursor.execute("SELECT COUNT(*) FROM chunks")
                total_chunks = cursor.fetchone()[0]

                if self.verbose:
                    print(f"Migrating {total_chunks} chunks...")

                # Check if metadata_text column exists (do this once)
                cursor.execute("PRAGMA table_info(chunks)")
                columns = [col[1] for col in cursor.fetchall()]
                has_metadata_text = "metadata_text" in columns

                # Migrate chunks in batches
                offset = 0
                while offset < total_chunks:
                    # Fetch batch of chunks

                    if has_metadata_text:
                        cursor.execute(
                            """
                            SELECT id, content, processed_content, keywords, language, 
                                   embedding, filename, section, start_line, end_line, 
                                   tags, metadata, metadata_text, chunk_hash
                            FROM chunks
                            ORDER BY id
                            LIMIT ? OFFSET ?
                        """,
                            (batch_size, offset),
                        )
                    else:
                        cursor.execute(
                            """
                            SELECT id, content, processed_content, keywords, language, 
                                   embedding, filename, section, start_line, end_line, 
                                   tags, metadata, chunk_hash
                            FROM chunks
                            ORDER BY id
                            LIMIT ? OFFSET ?
                        """,
                            (batch_size, offset),
                        )

                    chunks_batch = []
                    for row in cursor.fetchall():
                        # Handle both old and new schema (with or without metadata_text)
                        if len(row) == 14:  # New schema with metadata_text
                            (
                                _chunk_id,
                                content,
                                processed_content,
                                keywords_json,
                                language,
                                embedding_blob,
                                filename,
                                section,
                                start_line,
                                end_line,
                                tags_json,
                                metadata_json,
                                metadata_text,
                                chunk_hash,
                            ) = row
                        else:  # Old schema without metadata_text
                            (
                                _chunk_id,
                                content,
                                processed_content,
                                keywords_json,
                                language,
                                embedding_blob,
                                filename,
                                section,
                                start_line,
                                end_line,
                                tags_json,
                                metadata_json,
                                chunk_hash,
                            ) = row
                            metadata_text = None

                        # Convert embedding blob to numpy array if available
                        if embedding_blob and np:
                            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                        else:
                            embedding = embedding_blob

                        # Parse JSON fields
                        keywords = json.loads(keywords_json) if keywords_json else []
                        tags = json.loads(tags_json) if tags_json else []
                        metadata = json.loads(metadata_json) if metadata_json else {}

                        chunk = {
                            "content": content,
                            "processed_content": processed_content,
                            "keywords": keywords,
                            "language": language,
                            "embedding": embedding,
                            "filename": filename,
                            "section": section,
                            "start_line": start_line,
                            "end_line": end_line,
                            "tags": tags,
                            "metadata": metadata,
                            "metadata_text": metadata_text,  # Will be regenerated if None
                            "chunk_hash": chunk_hash,
                        }

                        chunks_batch.append(chunk)

                    # Store batch in pgvector
                    if chunks_batch:
                        try:
                            pgvector.store_chunks(
                                chunks_batch, collection_name, collection_config
                            )
                            stats["chunks_migrated"] += len(chunks_batch)

                            if self.verbose:
                                progress = (
                                    (offset + len(chunks_batch)) / total_chunks * 100
                                )
                                print(
                                    f"  Progress: {stats['chunks_migrated']}/{total_chunks} ({progress:.1f}%)"
                                )
                        except Exception as e:
                            logger.error(f"Error storing batch at offset {offset}: {e}")
                            stats["errors"] += len(chunks_batch)

                    offset += batch_size

                # Success
                if self.verbose:
                    print("\nMigration completed successfully!")
                    print(f"  Chunks migrated: {stats['chunks_migrated']}")
                    print(f"  Errors: {stats['errors']}")

            finally:
                pgvector.close()

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
        finally:
            # Guarded because sqlite3.connect itself can raise -- a missing
            # file, a permissions problem, a corrupt database. The name is then
            # unbound and this finally raised UnboundLocalError ON TOP of the
            # real failure, so the caller was told "cannot access local
            # variable" instead of "unable to open database file". A cleanup
            # handler must not be able to destroy the diagnosis.
            if sqlite_conn is not None:
                sqlite_conn.close()

        return stats

    def migrate_pgvector_to_sqlite(
        self,
        connection_string: str,
        collection_name: str,
        output_path: str,
        batch_size: int = 100,
    ) -> dict[str, Any]:
        """
        Migrate a pgvector collection to SQLite .swsearch format (not implemented)

        The pgvector backend can't export chunks yet, so this method raises
        before it connects to the database or touches ``output_path``. An
        index that already exists at that path is left as it is.

        Args:
            connection_string: PostgreSQL connection string
            collection_name: Name of the pgvector collection
            output_path: Output .swsearch file path
            batch_size: Number of chunks to fetch at once

        Raises:
            NotImplementedError: always
        """
        raise NotImplementedError(
            "Migrating a pgvector collection to SQLite isn't implemented yet. "
            f"Nothing was read from {collection_name!r}, and {output_path!r} "
            "wasn't changed."
        )

    def get_index_info(self, index_path: str) -> dict[str, Any]:
        """
        Get information about a search index

        Args:
            index_path: Path to index file or pgvector collection identifier

        Returns:
            Index information including type, config, and statistics
        """
        info: dict[str, Any] = {}

        if index_path.endswith(".swsearch") and Path(index_path).exists():
            # SQLite index
            info["type"] = "sqlite"
            info["path"] = index_path

            # try/finally rather than a trailing close(): a corrupt or
            # partially written index makes any of these statements raise, and
            # the handle would otherwise be held until GC -- which on Windows
            # keeps the file locked against the very repair the caller is
            # probably attempting.
            conn = sqlite3.connect(index_path)
            try:
                cursor = conn.cursor()

                # Get config
                cursor.execute("SELECT key, value FROM config")
                info["config"] = dict(cursor.fetchall())

                # Get stats
                cursor.execute("SELECT COUNT(*) FROM chunks")
                info["total_chunks"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(DISTINCT filename) FROM chunks")
                info["total_files"] = cursor.fetchone()[0]
            finally:
                conn.close()

        else:
            info["type"] = "unknown"
            info["path"] = index_path

        return info
