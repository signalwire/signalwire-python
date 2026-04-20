"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import json
import re
from typing import List, Dict, Any, Optional

from signalwire.core.logging_config import get_logger
from datetime import datetime


def _sanitize_collection_name(collection_name: str) -> str:
    """Sanitize a collection name to prevent SQL injection"""
    return re.sub(r'[^a-zA-Z0-9_]', '_', collection_name)

try:
    import psycopg2
    from psycopg2 import sql as psycopg2_sql
    from psycopg2.extras import execute_values
    from pgvector.psycopg2 import register_vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    psycopg2 = None
    psycopg2_sql = None
    register_vector = None

try:
    import numpy as np
except ImportError:
    np = None

logger = get_logger(__name__)


class PgVectorBackend:
    """PostgreSQL pgvector backend for search indexing and retrieval"""
    
    def __init__(self, connection_string: str):
        """
        Initialize pgvector backend
        
        Args:
            connection_string: PostgreSQL connection string
        """
        if not PGVECTOR_AVAILABLE:
            raise ImportError(
                "pgvector dependencies not available. Install with: "
                "pip install psycopg2-binary pgvector"
            )
        
        self.connection_string = connection_string
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            register_vector(self.conn)
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            error_msg = str(e)
            if "vector type not found" in error_msg:
                logger.error(
                    "pgvector extension not installed in database. "
                    "Run: CREATE EXTENSION IF NOT EXISTS vector;"
                )
            else:
                logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _ensure_connection(self):
        """Ensure database connection is active"""
        if self.conn is None or self.conn.closed:
            self._connect()
    
    def create_schema(self, collection_name: str, embedding_dim: int = 768):
        """
        Create database schema for a collection
        
        Args:
            collection_name: Name of the collection
            embedding_dim: Dimension of embeddings
        """
        self._ensure_connection()
        
        with self.conn.cursor() as cursor:
            # Create extensions
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
            
            # Create table - sanitize collection name to prevent SQL injection
            import re
            sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '_', collection_name)
            table_name = f"chunks_{sanitized_name}"
            tbl = psycopg2_sql.Identifier(table_name)
            idx_embedding = psycopg2_sql.Identifier(f"idx_{table_name}_embedding")
            idx_content = psycopg2_sql.Identifier(f"idx_{table_name}_content")
            idx_tags = psycopg2_sql.Identifier(f"idx_{table_name}_tags")
            idx_metadata = psycopg2_sql.Identifier(f"idx_{table_name}_metadata")
            idx_metadata_text = psycopg2_sql.Identifier(f"idx_{table_name}_metadata_text")

            cursor.execute(psycopg2_sql.SQL("""
                CREATE TABLE IF NOT EXISTS {tbl} (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    processed_content TEXT,
                    embedding vector(%s),
                    filename TEXT,
                    section TEXT,
                    tags JSONB DEFAULT '[]'::jsonb,
                    metadata JSONB DEFAULT '{{}}'::jsonb,
                    metadata_text TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """).format(tbl=tbl), (embedding_dim,))

            # Create indexes
            cursor.execute(psycopg2_sql.SQL("""
                CREATE INDEX IF NOT EXISTS {idx}
                ON {tbl} USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """).format(idx=idx_embedding, tbl=tbl))

            cursor.execute(psycopg2_sql.SQL("""
                CREATE INDEX IF NOT EXISTS {idx}
                ON {tbl} USING gin (content gin_trgm_ops)
            """).format(idx=idx_content, tbl=tbl))

            cursor.execute(psycopg2_sql.SQL("""
                CREATE INDEX IF NOT EXISTS {idx}
                ON {tbl} USING gin (tags)
            """).format(idx=idx_tags, tbl=tbl))

            cursor.execute(psycopg2_sql.SQL("""
                CREATE INDEX IF NOT EXISTS {idx}
                ON {tbl} USING gin (metadata)
            """).format(idx=idx_metadata, tbl=tbl))

            cursor.execute(psycopg2_sql.SQL("""
                CREATE INDEX IF NOT EXISTS {idx}
                ON {tbl} USING gin (metadata_text gin_trgm_ops)
            """).format(idx=idx_metadata_text, tbl=tbl))
            
            # Create config table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collection_config (
                    collection_name TEXT PRIMARY KEY,
                    model_name TEXT,
                    embedding_dimensions INTEGER,
                    chunking_strategy TEXT,
                    languages JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            """)
            
            self.conn.commit()
            logger.info(f"Created schema for collection '{collection_name}'")
    
    def _extract_metadata_from_json_content(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from JSON content if present
        
        Returns:
            metadata_dict
        """
        metadata_dict = {}
        
        # Try to extract metadata from JSON structure in content
        if '"metadata":' in content:
            try:
                import re
                # Find all metadata objects
                pattern = r'"metadata"\s*:\s*(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    try:
                        json_metadata = json.loads(match.group(1))
                        # Merge all found metadata
                        if isinstance(json_metadata, dict):
                            metadata_dict.update(json_metadata)
                    except:
                        pass
            except Exception as e:
                logger.debug(f"Error extracting JSON metadata: {e}")
        
        return metadata_dict

    def store_chunks(self, chunks: List[Dict[str, Any]], collection_name: str,
                    config: Dict[str, Any]):
        """
        Store document chunks in the database

        Args:
            chunks: List of processed chunks with embeddings
            collection_name: Name of the collection
            config: Configuration metadata
        """
        self._ensure_connection()

        collection_name = _sanitize_collection_name(collection_name)
        table_name = f"chunks_{collection_name}"
        
        # Prepare data for batch insert
        data = []
        for chunk in chunks:
            embedding = chunk.get('embedding')
            if embedding is not None:
                # Convert to list if it's a numpy array
                if hasattr(embedding, 'tolist'):
                    embedding = embedding.tolist()
            
            metadata = chunk.get('metadata', {})
            
            # Extract fields - they might be at top level or in metadata
            filename = chunk.get('filename') or metadata.get('filename', '')
            section = chunk.get('section') or metadata.get('section', '')
            tags = chunk.get('tags', []) or metadata.get('tags', [])
            
            # Extract metadata from JSON content and merge with chunk metadata
            json_metadata = self._extract_metadata_from_json_content(chunk['content'])
            
            # Build metadata from all fields except the ones we store separately
            chunk_metadata = {}
            for key, value in chunk.items():
                if key not in ['content', 'processed_content', 'embedding', 'filename', 'section', 'tags']:
                    chunk_metadata[key] = value
            # Also include any extra metadata
            for key, value in metadata.items():
                if key not in ['filename', 'section', 'tags']:
                    chunk_metadata[key] = value
            
            # Merge metadata: chunk metadata takes precedence over JSON metadata
            merged_metadata = {**json_metadata, **chunk_metadata}
            
            # Create searchable metadata text
            metadata_text_parts = []
            
            # Add all metadata keys and values
            for key, value in merged_metadata.items():
                metadata_text_parts.append(str(key).lower())
                if isinstance(value, list):
                    metadata_text_parts.extend(str(v).lower() for v in value)
                else:
                    metadata_text_parts.append(str(value).lower())
            
            # Add tags
            if tags:
                metadata_text_parts.extend(str(tag).lower() for tag in tags)
            
            # Add section if present
            if section:
                metadata_text_parts.append(section.lower())
            
            metadata_text = ' '.join(metadata_text_parts)
            
            data.append((
                chunk['content'],
                chunk.get('processed_content', chunk['content']),
                embedding,
                filename,
                section,
                json.dumps(tags),
                json.dumps(merged_metadata),
                metadata_text
            ))
        
        # Batch insert chunks
        with self.conn.cursor() as cursor:
            tbl = psycopg2_sql.Identifier(table_name)
            insert_query = psycopg2_sql.SQL("""
                INSERT INTO {tbl}
                (content, processed_content, embedding, filename, section, tags, metadata, metadata_text)
                VALUES %s
            """).format(tbl=tbl)
            execute_values(
                cursor,
                insert_query.as_string(self.conn),
                data,
                template="(%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s)"
            )
            
            # Update or insert config
            cursor.execute("""
                INSERT INTO collection_config 
                (collection_name, model_name, embedding_dimensions, chunking_strategy, 
                 languages, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (collection_name) 
                DO UPDATE SET 
                    model_name = EXCLUDED.model_name,
                    embedding_dimensions = EXCLUDED.embedding_dimensions,
                    chunking_strategy = EXCLUDED.chunking_strategy,
                    languages = EXCLUDED.languages,
                    metadata = EXCLUDED.metadata
            """, (
                collection_name,
                config.get('model_name'),
                config.get('embedding_dimensions'),
                config.get('chunking_strategy'),
                json.dumps(config.get('languages', [])),
                json.dumps(config.get('metadata', {}))
            ))
            
            self.conn.commit()
            logger.info(f"Stored {len(chunks)} chunks in collection '{collection_name}'")
    
    def get_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        self._ensure_connection()

        collection_name = _sanitize_collection_name(collection_name)
        table_name = f"chunks_{collection_name}"
        
        with self.conn.cursor() as cursor:
            tbl = psycopg2_sql.Identifier(table_name)
            # Get chunk count
            cursor.execute(psycopg2_sql.SQL("SELECT COUNT(*) FROM {tbl}").format(tbl=tbl))
            total_chunks = cursor.fetchone()[0]

            # Get unique files
            cursor.execute(psycopg2_sql.SQL("SELECT COUNT(DISTINCT filename) FROM {tbl}").format(tbl=tbl))
            total_files = cursor.fetchone()[0]
            
            # Get config
            cursor.execute(
                "SELECT * FROM collection_config WHERE collection_name = %s",
                (collection_name,)
            )
            config_row = cursor.fetchone()
            
            if config_row:
                config = {
                    'model_name': config_row[1],
                    'embedding_dimensions': config_row[2],
                    'chunking_strategy': config_row[3],
                    'languages': config_row[4],
                    'created_at': config_row[5].isoformat() if config_row[5] else None,
                    'metadata': config_row[6]
                }
            else:
                config = {}
            
            return {
                'total_chunks': total_chunks,
                'total_files': total_files,
                'config': config
            }
    
    def list_collections(self) -> List[str]:
        """List all collections in the database"""
        self._ensure_connection()
        
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT collection_name FROM collection_config ORDER BY collection_name")
            return [row[0] for row in cursor.fetchall()]
    
    def delete_collection(self, collection_name: str):
        """Delete a collection and its data"""
        self._ensure_connection()
        
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', collection_name)
        table_name = f"chunks_{sanitized}"

        with self.conn.cursor() as cursor:
            tbl = psycopg2_sql.Identifier(table_name)
            cursor.execute(psycopg2_sql.SQL("DROP TABLE IF EXISTS {tbl}").format(tbl=tbl))
            cursor.execute(
                "DELETE FROM collection_config WHERE collection_name = %s",
                (collection_name,)
            )
            self.conn.commit()
            logger.info(f"Deleted collection '{collection_name}'")
    
    def close(self):
        """Close database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Closed database connection")


class PgVectorSearchBackend:
    """PostgreSQL pgvector backend for search operations"""
    
    def __init__(self, connection_string: str, collection_name: str):
        """
        Initialize search backend

        Args:
            connection_string: PostgreSQL connection string
            collection_name: Name of the collection to search
        """
        if not PGVECTOR_AVAILABLE:
            raise ImportError(
                "pgvector dependencies not available. Install with: "
                "pip install psycopg2-binary pgvector"
            )

        self.connection_string = connection_string
        self.collection_name = _sanitize_collection_name(collection_name)
        self.table_name = f"chunks_{self.collection_name}"
        self.conn = None
        self._connect()
        self.config = self._load_config()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            register_vector(self.conn)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _ensure_connection(self):
        """Ensure database connection is active"""
        if self.conn is None or self.conn.closed:
            self._connect()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load collection configuration"""
        self._ensure_connection()
        
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM collection_config WHERE collection_name = %s",
                (self.collection_name,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'model_name': row[1],
                    'embedding_dimensions': row[2],
                    'chunking_strategy': row[3],
                    'languages': row[4],
                    'metadata': row[6]
                }
            return {}
    
    def search(self, query_vector: List[float], enhanced_text: str,
              count: int = 5, similarity_threshold: float = 0.0,
              tags: Optional[List[str]] = None,
              keyword_weight: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (vector + keyword + metadata).

        NOTE: As of the unified-pipeline refactor, production traffic flows
        through SearchEngine.search() which calls fetch_candidates() here
        and then runs all post-processing (scoring, dedup, diversity) in
        SearchEngine. This method remains as a self-contained search path
        for direct backend use and test coverage, but does NOT receive the
        SearchEngine's exact-match boost, filename diversity, or match-type
        diversity logic. For consistent behavior, call SearchEngine.search().

        Args:
            query_vector: Embedding vector for the query
            enhanced_text: Processed query text for keyword search
            count: Number of results to return
            similarity_threshold: Minimum similarity score
            tags: Filter by tags
            keyword_weight: Manual keyword weight (0.0-1.0). If None, uses default weighting

        Returns:
            List of search results with scores and metadata
        """
        self._ensure_connection()

        # Extract query terms for metadata search
        query_terms = enhanced_text.lower().split()

        # Vector search
        vector_results = self._vector_search(query_vector, count * 2, tags)

        # Keyword search
        keyword_results = self._keyword_search(enhanced_text, count * 2, tags)

        # Metadata search
        metadata_results = self._metadata_search(query_terms, count * 2, tags)

        # Merge all results
        merged_results = self._merge_all_results(vector_results, keyword_results, metadata_results, keyword_weight)

        # Ensure 'score' field exists for CLI compatibility
        for r in merged_results:
            if 'score' not in r:
                r['score'] = r.get('final_score', 0.0)

        # Apply similarity threshold to FINAL merged scores
        # This filters on the score the consumer actually sees, not just the vector component
        if similarity_threshold > 0:
            merged_results = [r for r in merged_results if r['score'] >= similarity_threshold]

        # Collapse content duplicates. Index quality varies: some source docs have
        # repeated boilerplate (footers, disclaimers) chunked into many near-identical
        # entries. Without this, those repeated chunks flood the top-N for any query
        # whose surface words overlap. Normalize (lowercase + whitespace collapse +
        # trim formatting punctuation) before hashing to catch formatting variation.
        # Results must be sorted best-first so the kept copy wins.
        merged_results.sort(key=lambda r: r.get('score', 0.0), reverse=True)
        merged_results = self._dedupe_by_content(merged_results)

        return merged_results[:count]

    def _dedupe_by_content(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Drop duplicate-content chunks, keeping the first (highest-scoring) occurrence."""
        import hashlib
        import re
        if not results:
            return results
        seen = set()
        out = []
        for r in results:
            content = r.get('content') or ''
            normalized = re.sub(r'\s+', ' ', content.strip().lower()).strip('*_`#>- \t\n')
            if not normalized:
                out.append(r)
                continue
            h = hashlib.sha1(normalized.encode('utf-8')).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            out.append(r)
        return out
    
    def _vector_search(self, query_vector: List[float], count: int,
                      tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        with self.conn.cursor() as cursor:
            # Set probes for IVFFlat index to ensure we get enough results
            cursor.execute("SET LOCAL ivfflat.probes = %s", (max(count, 10),))
            # Build query parts
            tbl = psycopg2_sql.Identifier(self.table_name)
            parts = [psycopg2_sql.SQL("""
                SELECT id, content, filename, section, tags, metadata,
                       1 - (embedding <=> %s::vector) as similarity
                FROM {tbl}
                WHERE embedding IS NOT NULL
            """).format(tbl=tbl)]

            params = [query_vector]

            # Add tag filter if specified
            if tags:
                parts.append(psycopg2_sql.SQL(" AND tags ?| %s"))
                params.append(tags)

            parts.append(psycopg2_sql.SQL(" ORDER BY embedding <=> %s::vector LIMIT %s"))
            params.extend([query_vector, count])

            query = psycopg2_sql.SQL("").join(parts)
            cursor.execute(query, params)

            results = []
            for row in cursor.fetchall():
                chunk_id, content, filename, section, tags_json, metadata_json, similarity = row
                
                results.append({
                    'id': chunk_id,
                    'content': content,
                    'score': float(similarity),
                    'metadata': {
                        'filename': filename,
                        'section': section,
                        'tags': tags_json if isinstance(tags_json, list) else [],
                        **metadata_json
                    },
                    'search_type': 'vector'
                })
            
            return results
    
    def _keyword_search(self, enhanced_text: str, count: int,
                       tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Perform full-text search"""
        with self.conn.cursor() as cursor:
            # Use PostgreSQL text search
            tbl = psycopg2_sql.Identifier(self.table_name)
            parts = [psycopg2_sql.SQL("""
                SELECT id, content, filename, section, tags, metadata,
                       ts_rank(to_tsvector('english', content),
                              plainto_tsquery('english', %s)) as rank
                FROM {tbl}
                WHERE to_tsvector('english', content) @@ plainto_tsquery('english', %s)
            """).format(tbl=tbl)]

            params = [enhanced_text, enhanced_text]

            # Add tag filter if specified
            if tags:
                parts.append(psycopg2_sql.SQL(" AND tags ?| %s"))
                params.append(tags)

            parts.append(psycopg2_sql.SQL(" ORDER BY rank DESC LIMIT %s"))
            params.append(count)

            query = psycopg2_sql.SQL("").join(parts)
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                chunk_id, content, filename, section, tags_json, metadata_json, rank = row
                
                # Normalize rank to 0-1 score
                score = min(1.0, rank / 10.0)
                
                results.append({
                    'id': chunk_id,
                    'content': content,
                    'score': float(score),
                    'metadata': {
                        'filename': filename,
                        'section': section,
                        'tags': tags_json if isinstance(tags_json, list) else [],
                        **metadata_json
                    },
                    'search_type': 'keyword'
                })
            
            return results
    
    def _metadata_search(self, query_terms: List[str], count: int,
                        tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Perform metadata search using JSONB operators and metadata_text
        """
        with self.conn.cursor() as cursor:
            # Build WHERE conditions
            where_conditions = []
            params = []

            # Use metadata_text for trigram search
            if query_terms:
                # Create AND conditions for all terms
                for term in query_terms:
                    where_conditions.append(psycopg2_sql.SQL("metadata_text ILIKE %s"))
                    params.append(f'%{term}%')

            # Add tag filter if specified
            if tags:
                where_conditions.append(psycopg2_sql.SQL("tags ?| %s"))
                params.append(tags)

            # Build query
            tbl = psycopg2_sql.Identifier(self.table_name)
            if where_conditions:
                where_clause = psycopg2_sql.SQL(" AND ").join(where_conditions)
            else:
                where_clause = psycopg2_sql.SQL("1=1")

            query = psycopg2_sql.SQL("""
                SELECT id, content, filename, section, tags, metadata,
                       metadata_text
                FROM {tbl}
                WHERE {where_clause}
                LIMIT %s
            """).format(tbl=tbl, where_clause=where_clause)
            
            params.append(count)
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                chunk_id, content, filename, section, tags_json, metadata_json, metadata_text = row
                
                # Calculate score based on proportion of terms matched
                text_matches = 0
                json_matches = 0
                total_terms = len(query_terms) if query_terms else 1

                if metadata_text:
                    metadata_lower = metadata_text.lower()
                    for term in query_terms:
                        if term.lower() in metadata_lower:
                            text_matches += 1

                if metadata_json:
                    json_str = json.dumps(metadata_json).lower()
                    for term in query_terms:
                        if term.lower() in json_str:
                            json_matches += 1

                # Score based on what fraction of terms matched, scaled to a reasonable range
                # Max possible: 0.4 (text) + 0.2 (json) = 0.6 for a perfect metadata match
                text_score = (text_matches / total_terms) * 0.4
                json_score = (json_matches / total_terms) * 0.2
                score = text_score + json_score
                
                results.append({
                    'id': chunk_id,
                    'content': content,
                    'score': float(score),
                    'metadata': {
                        'filename': filename,
                        'section': section,
                        'tags': tags_json if isinstance(tags_json, list) else [],
                        **metadata_json
                    },
                    'search_type': 'metadata'
                })
            
            # Sort by score
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:count]

    def _filename_search(self, query: str, count: int,
                        tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for query in filenames with term coverage scoring.

        Phase 1: exact phrase match on filename (highest score).
        Phase 2: any-term match (scored by coverage = matched_terms / total_terms).
        Mirrors the sqlite path so downstream scoring treats signals uniformly.
        """
        query_lower = (query or '').lower().strip()
        if not query_lower:
            return []

        terms = query_lower.split()

        with self.conn.cursor() as cursor:
            tbl = psycopg2_sql.Identifier(self.table_name)
            results = []
            seen_ids = set()

            # Phase 1 — exact phrase match on filename
            parts = [psycopg2_sql.SQL("""
                SELECT DISTINCT id, content, filename, section, tags, metadata
                FROM {tbl}
                WHERE LOWER(filename) LIKE %s
            """).format(tbl=tbl)]
            params = [f'%{query_lower}%']
            if tags:
                parts.append(psycopg2_sql.SQL(" AND tags ?| %s"))
                params.append(tags)
            parts.append(psycopg2_sql.SQL(" LIMIT %s"))
            params.append(count)

            try:
                cursor.execute(psycopg2_sql.SQL("").join(parts), params)
                for row in cursor.fetchall():
                    chunk_id, content, filename, section, tags_json, metadata_json = row
                    seen_ids.add(chunk_id)
                    filename_lower = (filename or '').lower()
                    basename = filename_lower.rsplit('/', 1)[-1]
                    # Exact phrase in basename scores higher than elsewhere in path.
                    # Normalize to 0-1 so downstream scoring treats this like vector scores.
                    score = 1.0 if query_lower in basename else 0.67
                    results.append({
                        'id': chunk_id,
                        'content': content,
                        'score': float(score),
                        'metadata': {
                            'filename': filename,
                            'section': section,
                            'tags': tags_json if isinstance(tags_json, list) else [],
                            **(metadata_json or {})
                        },
                        'search_type': 'filename',
                        'match_coverage': 1.0,
                    })
            except Exception as e:
                logger.debug(f"Filename phase-1 search error: {e}")

            # Phase 2 — any-term match with coverage scoring, excluding already-seen
            if terms and len(results) < count:
                remaining = count - len(results)
                parts = [psycopg2_sql.SQL("""
                    SELECT DISTINCT id, content, filename, section, tags, metadata
                    FROM {tbl}
                    WHERE (
                """).format(tbl=tbl)]
                ors = []
                params = []
                for t in terms:
                    ors.append(psycopg2_sql.SQL("LOWER(filename) LIKE %s"))
                    params.append(f'%{t}%')
                parts.append(psycopg2_sql.SQL(" OR ").join(ors))
                parts.append(psycopg2_sql.SQL(")"))
                if seen_ids:
                    parts.append(psycopg2_sql.SQL(" AND id NOT IN %s"))
                    params.append(tuple(seen_ids))
                if tags:
                    parts.append(psycopg2_sql.SQL(" AND tags ?| %s"))
                    params.append(tags)
                parts.append(psycopg2_sql.SQL(" LIMIT %s"))
                params.append(remaining * 2)

                try:
                    cursor.execute(psycopg2_sql.SQL("").join(parts), params)
                    for row in cursor.fetchall():
                        chunk_id, content, filename, section, tags_json, metadata_json = row
                        filename_lower = (filename or '').lower()
                        matched = sum(1 for t in terms if t in filename_lower)
                        coverage = matched / len(terms) if terms else 0.0
                        # Term-coverage-only matches cap at 0.5 so phrase matches always outrank them.
                        score = min(0.5, coverage * 0.5)
                        results.append({
                            'id': chunk_id,
                            'content': content,
                            'score': float(score),
                            'metadata': {
                                'filename': filename,
                                'section': section,
                                'tags': tags_json if isinstance(tags_json, list) else [],
                                **(metadata_json or {})
                            },
                            'search_type': 'filename',
                            'match_coverage': coverage,
                        })
                except Exception as e:
                    logger.debug(f"Filename phase-2 search error: {e}")

            results.sort(key=lambda r: r['score'], reverse=True)
            return results[:count]

    def fetch_candidates(self, query_vector: List[float], enhanced_text: str,
                        count: int, similarity_threshold: float = 0.0,
                        tags: Optional[List[str]] = None,
                        original_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch raw candidates with per-source signal scores.

        Runs vector/keyword/metadata/filename searches, applies similarity
        threshold to raw vector scores pre-merge (keeps threshold intuitive),
        and merges into a candidate list keyed by chunk id. Does NOT compute
        final scores, boost exact matches, dedupe, or apply diversity -
        those run uniformly in SearchEngine for every backend.

        Result shape per candidate (matches sqlite path):
            {
                'id', 'content', 'metadata': {filename, section, tags, **custom},
                'search_type', 'vector_score' (if vector matched),
                'vector_distance' (if vector matched),
                'sources': {source_type: True, ...},
                'source_scores': {source_type: raw_score, ...},
            }
        """
        self._ensure_connection()
        query_terms = enhanced_text.lower().split()

        # Vector + apply threshold to raw scores before merging
        vector_results = self._vector_search(query_vector, count, tags)
        if similarity_threshold > 0:
            vector_results = [r for r in vector_results if r['score'] >= similarity_threshold]

        keyword_results = self._keyword_search(enhanced_text, count, tags)
        metadata_results = self._metadata_search(query_terms, count, tags)
        filename_results = self._filename_search(original_query or enhanced_text, count, tags)

        logger.debug(
            f"pgvector fetch_candidates: vector={len(vector_results)}, "
            f"filename={len(filename_results)}, metadata={len(metadata_results)}, "
            f"keyword={len(keyword_results)}"
        )

        candidates: Dict[Any, Dict[str, Any]] = {}

        # Vector first (primary signal)
        for r in vector_results:
            cid = r['id']
            candidates[cid] = r
            candidates[cid]['vector_score'] = r['score']
            candidates[cid]['vector_distance'] = 1 - r['score']
            candidates[cid]['sources'] = {'vector': True}
            candidates[cid]['source_scores'] = {'vector': r['score']}

        # Other signals: fill in or add as backfill
        for result_set, source_type in [
            (filename_results, 'filename'),
            (metadata_results, 'metadata'),
            (keyword_results, 'keyword'),
        ]:
            for r in result_set:
                cid = r['id']
                if cid not in candidates:
                    candidates[cid] = r
                    candidates[cid]['sources'] = {source_type: True}
                    candidates[cid]['source_scores'] = {source_type: r['score']}
                else:
                    candidates[cid]['sources'][source_type] = True
                    candidates[cid]['source_scores'][source_type] = r['score']

        return list(candidates.values())

    def _merge_results(self, vector_results: List[Dict[str, Any]],
                      keyword_results: List[Dict[str, Any]],
                      keyword_weight: Optional[float] = None) -> List[Dict[str, Any]]:
        """Merge and rank results from vector and keyword search.

        Uses max-signal-wins scoring: the strongest signal (vector or keyword)
        becomes the base score, and agreement from the other source boosts it.
        This keeps scores in an intuitive 0-1 range where 0.5 means 'decent match'.
        """
        agreement_boost = 0.1  # Boost when multiple sources agree

        # Collect per-source scores for each result
        results_map = {}
        all_sources = {}

        for result in vector_results:
            chunk_id = result['id']
            results_map[chunk_id] = result.copy()
            all_sources.setdefault(chunk_id, {})['vector'] = result['score']

        for result in keyword_results:
            chunk_id = result['id']
            if chunk_id not in results_map:
                results_map[chunk_id] = result.copy()
            all_sources.setdefault(chunk_id, {})['keyword'] = result['score']

        # Score: max signal wins, boost for agreement
        for chunk_id, result in results_map.items():
            sources = all_sources[chunk_id]
            scores = list(sources.values())
            base = max(scores)
            boost = agreement_boost * (len(scores) - 1)
            result['score'] = min(1.0, base + boost)

        merged = list(results_map.values())
        merged.sort(key=lambda x: x['score'], reverse=True)

        return merged
    
    def _merge_all_results(self, vector_results: List[Dict[str, Any]],
                          keyword_results: List[Dict[str, Any]],
                          metadata_results: List[Dict[str, Any]],
                          keyword_weight: Optional[float] = None) -> List[Dict[str, Any]]:
        """Merge and rank results from vector, keyword, and metadata search.

        Uses max-signal-wins scoring: the strongest signal (vector, keyword,
        or metadata) becomes the base score, and agreement from additional
        sources boosts it. This keeps scores in an intuitive 0-1 range where
        0.5 means 'decent match' regardless of which source found it.
        """
        agreement_boost = 0.1  # Boost per additional agreeing source

        # Collect per-source scores for each result
        results_map = {}
        all_sources = {}

        for result in vector_results:
            chunk_id = result['id']
            results_map[chunk_id] = result.copy()
            all_sources.setdefault(chunk_id, {})['vector'] = result['score']

        for result in keyword_results:
            chunk_id = result['id']
            if chunk_id not in results_map:
                results_map[chunk_id] = result.copy()
            all_sources.setdefault(chunk_id, {})['keyword'] = result['score']

        for result in metadata_results:
            chunk_id = result['id']
            if chunk_id not in results_map:
                results_map[chunk_id] = result.copy()
            all_sources.setdefault(chunk_id, {})['metadata'] = result['score']

        # Score: max signal wins, boost for each additional agreeing source
        for chunk_id, result in results_map.items():
            sources = all_sources[chunk_id]
            scores = list(sources.values())
            base = max(scores)
            boost = agreement_boost * (len(scores) - 1)
            result['score'] = min(1.0, base + boost)
            result['sources'] = sources
            result['final_score'] = result['score']

        merged = list(results_map.values())
        merged.sort(key=lambda x: x['score'], reverse=True)

        return merged
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for the collection"""
        backend = PgVectorBackend(self.connection_string)
        stats = backend.get_stats(self.collection_name)
        backend.close()
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()