"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for search index builder module
"""

import pytest
import tempfile
import os
import sqlite3
import json
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path

from signalwire.search.index_builder import IndexBuilder


class TestIndexBuilderInit:
    """Test IndexBuilder initialization"""
    
    def test_default_initialization(self):
        """Test default initialization"""
        builder = IndexBuilder()
        
        assert builder.model_name == 'sentence-transformers/all-mpnet-base-v2'
        assert builder.chunking_strategy == 'sentence'
        assert builder.max_sentences_per_chunk == 5
        assert builder.chunk_size == 50
        assert builder.chunk_overlap == 10
        assert builder.split_newlines is None
        assert builder.verbose is False
        assert builder.model is None
        assert builder.doc_processor is not None
        assert builder.semantic_threshold == 0.5
        assert builder.topic_threshold == 0.3
    
    def test_custom_initialization(self):
        """Test initialization with custom parameters"""
        builder = IndexBuilder(
            model_name='custom-model',
            chunking_strategy='sliding',
            max_sentences_per_chunk=25,
            chunk_size=100,
            chunk_overlap=20,
            split_newlines=3,
            verbose=True
        )
        
        assert builder.model_name == 'custom-model'
        assert builder.chunking_strategy == 'sliding'
        assert builder.max_sentences_per_chunk == 25
        assert builder.chunk_size == 100
        assert builder.chunk_overlap == 20
        assert builder.split_newlines == 3
        assert builder.verbose is True


class TestIndexBuilderModelLoading:
    """Test model loading functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.builder = IndexBuilder()
    
    @patch('signalwire.search.index_builder.SentenceTransformer', None)
    def test_load_model_no_library(self):
        """Test model loading without sentence-transformers"""
        with pytest.raises(ImportError, match="sentence-transformers is required"):
            self.builder._load_model()
    
    @patch('signalwire.search.index_builder.SentenceTransformer')
    def test_load_model_success(self, mock_transformer):
        """Test successful model loading"""
        mock_model = Mock()
        mock_transformer.return_value = mock_model
        
        self.builder._load_model()
        
        mock_transformer.assert_called_once_with('sentence-transformers/all-mpnet-base-v2')
        assert self.builder.model == mock_model
    
    @patch('signalwire.search.index_builder.SentenceTransformer')
    def test_load_model_error(self, mock_transformer):
        """Test model loading with error"""
        mock_transformer.side_effect = Exception("Model loading failed")
        
        with pytest.raises(Exception, match="Model loading failed"):
            self.builder._load_model()
    
    @patch('signalwire.search.index_builder.SentenceTransformer')
    def test_load_model_lazy_loading(self, mock_transformer):
        """Test that model is only loaded once"""
        mock_model = Mock()
        mock_transformer.return_value = mock_model
        
        # First call should load model
        self.builder._load_model()
        assert mock_transformer.call_count == 1
        
        # Second call should not load again
        self.builder._load_model()
        assert mock_transformer.call_count == 1


class TestIndexBuilderFileDiscovery:
    """Test file discovery functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.builder = IndexBuilder()
    
    def test_is_file_excluded_no_patterns(self):
        """Test file exclusion with no patterns"""
        file_path = Path("test.txt")
        
        result = self.builder._is_file_excluded(file_path, None)
        
        assert result is False
    
    def test_is_file_excluded_with_patterns(self):
        """Test file exclusion with patterns"""
        file_path = Path("temp/test.txt")
        exclude_patterns = ["temp/*", "*.log"]
        
        result = self.builder._is_file_excluded(file_path, exclude_patterns)
        
        assert result is True
    
    def test_is_file_excluded_not_matching(self):
        """Test file exclusion with non-matching patterns"""
        file_path = Path("docs/test.txt")
        exclude_patterns = ["temp/*", "*.log"]
        
        result = self.builder._is_file_excluded(file_path, exclude_patterns)
        
        assert result is False
    
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    def test_discover_files_from_directory(self, mock_exists, mock_rglob, mock_is_dir):
        """Test file discovery from directory"""
        mock_is_dir.return_value = True
        mock_exists.return_value = True
        mock_files = [Path("test1.txt"), Path("test2.py"), Path("test3.txt")]
        mock_rglob.return_value = mock_files
        
        sources = [Path("test_dir")]
        file_types = ["txt", "py"]
        
        with patch.object(self.builder, '_discover_files', return_value=mock_files):
            result = self.builder._discover_files_from_sources(sources, file_types)
        
        assert len(result) == 3
        assert all(f in result for f in mock_files)
    
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.is_file')
    def test_discover_files_from_individual_files(self, mock_is_file, mock_is_dir):
        """Test file discovery from individual files"""
        mock_is_dir.return_value = False
        mock_is_file.return_value = True
        
        # Create mock Path objects with proper suffix
        mock_path1 = Mock(spec=Path)
        mock_path1.suffix = ".txt"
        mock_path1.__str__ = Mock(return_value="test1.txt")
        
        mock_path2 = Mock(spec=Path)
        mock_path2.suffix = ".py"
        mock_path2.__str__ = Mock(return_value="test2.py")
        
        sources = [mock_path1, mock_path2]
        file_types = ["txt", "py"]
        
        with patch.object(self.builder, '_is_file_excluded', return_value=False):
            result = self.builder._discover_files_from_sources(sources, file_types)
        
        assert len(result) == 2
        assert mock_path1 in result
        assert mock_path2 in result
    
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.is_file')
    def test_discover_files_with_exclusions(self, mock_is_file, mock_is_dir):
        """Test file discovery with exclusions"""
        mock_is_dir.return_value = False
        mock_is_file.return_value = True
        
        # Create mock Path objects
        mock_path1 = Mock(spec=Path)
        mock_path1.suffix = ".txt"
        mock_path1.__str__ = Mock(return_value="test1.txt")
        
        mock_path2 = Mock(spec=Path)
        mock_path2.suffix = ".txt"
        mock_path2.__str__ = Mock(return_value="temp/test2.txt")
        
        sources = [mock_path1, mock_path2]
        file_types = ["txt"]
        exclude_patterns = ["temp/*"]
        
        result = self.builder._discover_files_from_sources(sources, file_types, exclude_patterns)
        
        assert len(result) == 1
        assert mock_path1 in result
        assert mock_path2 not in result


class TestIndexBuilderFileProcessing:
    """Test file processing functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.builder = IndexBuilder()
    
    def test_get_base_directory_for_individual_file(self):
        """Test base directory calculation for individual files"""
        file_path = Path("/home/user/docs/test.txt")
        sources = [file_path]
        
        result = self.builder._get_base_directory_for_file(file_path, sources)
        
        assert result == str(file_path.parent)
    
    def test_get_base_directory_for_directory_file(self):
        """Test base directory calculation for files from directories"""
        # Create mock Path objects
        mock_file_path = Mock(spec=Path)
        mock_source_path = Mock(spec=Path)
        mock_source_path.is_dir.return_value = True
        
        # Mock relative_to to succeed (not raise ValueError)
        mock_file_path.relative_to.return_value = Path("subdir/test.txt")
        
        sources = [mock_source_path]
        
        result = self.builder._get_base_directory_for_file(mock_file_path, sources)
        
        assert result == str(mock_source_path)
    
    @patch('pathlib.Path.read_text')
    def test_process_file_success(self, mock_read_text):
        """Test successful file processing"""
        mock_read_text.return_value = "Test content for processing"
        
        # Create mock Path object
        mock_file_path = Mock(spec=Path)
        mock_file_path.read_text.return_value = "Test content for processing"
        mock_file_path.relative_to.return_value = Path("test.txt")
        mock_file_path.suffix = ".txt"
        
        source_dir = "/home/user"
        
        mock_chunks = [
            {"content": "Test content", "filename": "test.txt"},
            {"content": "for processing", "filename": "test.txt"}
        ]
        
        with patch.object(self.builder.doc_processor, 'create_chunks', return_value=mock_chunks):
            result = self.builder._process_file(mock_file_path, source_dir)
        
        assert len(result) == 2
        assert result[0]["content"] == "Test content"
        assert result[1]["content"] == "for processing"
    
    @patch('pathlib.Path.read_text')
    def test_process_file_with_tags(self, mock_read_text):
        """Test file processing with global tags"""
        mock_read_text.return_value = "Test content"
        
        # Create mock Path object
        mock_file_path = Mock(spec=Path)
        mock_file_path.read_text.return_value = "Test content"
        mock_file_path.relative_to.return_value = Path("test.txt")
        mock_file_path.suffix = ".txt"
        
        source_dir = "/home/user"
        global_tags = ["tag1", "tag2"]
        
        mock_chunks = [{"content": "Test content", "filename": "test.txt", "tags": ["existing"]}]
        
        with patch.object(self.builder.doc_processor, 'create_chunks', return_value=mock_chunks):
            result = self.builder._process_file(mock_file_path, source_dir, global_tags)
        
        assert result[0]["tags"] == ["existing", "tag1", "tag2"]
    
    @patch('pathlib.Path.read_text')
    def test_process_file_unicode_error(self, mock_read_text):
        """Test file processing with unicode error"""
        mock_read_text.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")
        file_path = Path("test.bin")
        source_dir = "/home/user"
        
        result = self.builder._process_file(file_path, source_dir)
        
        assert result == []
    
    @patch('pathlib.Path.read_text')
    def test_process_file_general_error(self, mock_read_text):
        """Test file processing with general error"""
        mock_read_text.side_effect = Exception("File error")
        file_path = Path("test.txt")
        source_dir = "/home/user"
        
        result = self.builder._process_file(file_path, source_dir)
        
        assert result == []

    def test_process_file_with_string_tags(self):
        """Test file processing with string tags instead of list"""
        builder = IndexBuilder()
        
        mock_chunks = [{"content": "Test", "filename": "test.txt", "tags": "single_tag"}]
        
        # Create mock Path object
        mock_file_path = Mock(spec=Path)
        mock_file_path.read_text.return_value = "content"
        mock_file_path.relative_to.return_value = Path("test.txt")
        mock_file_path.suffix = ".txt"
        
        with patch.object(builder.doc_processor, 'create_chunks', return_value=mock_chunks):
            result = builder._process_file(mock_file_path, "/home", ["global_tag"])
            
            # Should convert string tag to list and add global tags
            assert result[0]["tags"] == ["single_tag", "global_tag"]


class TestIndexBuilderDatabaseCreation:
    """Test database creation functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.builder = IndexBuilder()
        self.temp_db = None
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if self.temp_db and os.path.exists(self.temp_db):
            os.remove(self.temp_db)
    
    def test_create_database_basic(self):
        """Test basic database creation"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            self.temp_db = f.name
        
        chunks = [
            {
                "content": "Test content",
                "processed_content": "test content",
                "keywords": ["test", "content"],
                "language": "en",
                "embedding": b"fake_embedding_data",
                "filename": "test.txt",
                "section": "Section 1",
                "start_line": 1,
                "end_line": 5,
                "tags": ["tag1"],
                "metadata": {"key": "value"}
            }
        ]
        
        languages = ["en"]
        sources_info = ["/home/user/docs"]
        file_types = ["txt"]
        
        self.builder._create_database(self.temp_db, chunks, languages, sources_info, file_types)
        
        # Verify database was created
        assert os.path.exists(self.temp_db)
        
        # Verify schema
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['chunks', 'chunks_fts', 'synonyms', 'config']
        assert all(table in tables for table in expected_tables)
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM chunks")
        assert cursor.fetchone()[0] == 1
        
        cursor.execute("SELECT content, filename FROM chunks")
        row = cursor.fetchone()
        assert row[0] == "Test content"
        assert row[1] == "test.txt"
        
        conn.close()
    
    def test_create_database_with_existing_file(self):
        """Test database creation with existing file"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            self.temp_db = f.name
            f.write(b"existing content")
        
        chunks = [{"content": "Test", "filename": "test.txt", "embedding": b"data"}]
        
        self.builder._create_database(self.temp_db, chunks, ["en"], ["/home"], ["txt"])
        
        # File should be recreated
        assert os.path.exists(self.temp_db)
        
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chunks")
        assert cursor.fetchone()[0] == 1
        conn.close()
    
    @patch('signalwire.search.index_builder.np')
    def test_create_database_with_numpy_embedding_dimensions(self, mock_np):
        """Test database creation with numpy embedding dimension detection"""
        mock_array = Mock()
        mock_array.__len__ = Mock(return_value=512)
        mock_np.frombuffer.return_value = mock_array
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            self.temp_db = f.name
        
        chunks = [{"content": "Test", "filename": "test.txt", "embedding": b"fake_data"}]
        
        self.builder._create_database(self.temp_db, chunks, ["en"], ["/home"], ["txt"])
        
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key='embedding_dimensions'")
        dimensions = cursor.fetchone()[0]
        assert dimensions == "512"
        conn.close()


class TestIndexBuilderIndexValidation:
    """Test index validation functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.builder = IndexBuilder()
        self.temp_db = None
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if self.temp_db and os.path.exists(self.temp_db):
            os.remove(self.temp_db)
    
    def test_validate_index_nonexistent_file(self):
        """Test validation of non-existent index file"""
        result = self.builder.validate_index("nonexistent.db")
        
        assert result["valid"] is False
        assert "does not exist" in result["error"]
    
    def test_validate_index_valid_file(self):
        """Test validation of valid index file"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            self.temp_db = f.name
        
        # Create a valid database
        chunks = [
            {"content": "Test", "filename": "test1.txt", "embedding": b"data"},
            {"content": "Test2", "filename": "test2.txt", "embedding": b"data"},
            {"content": "Test3", "filename": "test1.txt", "embedding": b"data"}
        ]
        self.builder._create_database(self.temp_db, chunks, ["en"], ["/home"], ["txt"])
        
        result = self.builder.validate_index(self.temp_db)
        
        assert result["valid"] is True
        assert result["chunk_count"] == 3
        assert result["file_count"] == 2  # 2 unique filenames
        assert "config" in result
    
    def test_validate_index_missing_tables(self):
        """Test validation of index with missing tables"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            self.temp_db = f.name
        
        # Create incomplete database
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE chunks (id INTEGER)")
        conn.commit()
        conn.close()
        
        result = self.builder.validate_index(self.temp_db)
        
        assert result["valid"] is False
        assert "Missing tables" in result["error"]
    
    def test_validate_index_database_error(self):
        """Test validation with database error"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            self.temp_db = f.name
            f.write(b"invalid sqlite data")
        
        result = self.builder.validate_index(self.temp_db)
        
        assert result["valid"] is False
        assert "error" in result


class TestIndexBuilderBuildMethods:
    """Test index building methods"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.builder = IndexBuilder(verbose=True)
        self.temp_db = None
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if self.temp_db and os.path.exists(self.temp_db):
            os.remove(self.temp_db)
    
    @patch('signalwire.search.index_builder.preprocess_document_content')
    def test_build_index_from_sources_success(self, mock_preprocess):
        """Test successful index building from sources"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            self.temp_db = f.name
        
        # Mock preprocessing
        mock_preprocess.return_value = {
            "enhanced_text": "enhanced content",
            "keywords": ["test", "content"]
        }
        
        # Mock file discovery
        mock_files = [Path("test1.txt"), Path("test2.txt")]
        
        # Mock file processing
        mock_chunks = [
            {"content": "Test content 1", "filename": "test1.txt"},
            {"content": "Test content 2", "filename": "test2.txt"}
        ]
        
        # Mock model
        mock_model = Mock()
        mock_embedding = Mock()
        mock_embedding.tobytes.return_value = b"fake_embedding"
        mock_model.encode.return_value = mock_embedding
        
        with patch.object(self.builder, '_discover_files_from_sources', return_value=mock_files), \
             patch.object(self.builder, '_process_file', side_effect=[mock_chunks[:1], mock_chunks[1:]]), \
             patch.object(self.builder, '_load_model'), \
             patch.object(self.builder, '_create_database') as mock_create_db:
            
            self.builder.model = mock_model
            
            sources = [Path("/home/user/docs")]
            file_types = ["txt"]
            
            self.builder.build_index_from_sources(sources, self.temp_db, file_types)
            
            # Verify methods were called
            mock_create_db.assert_called_once()
            assert mock_model.encode.call_count == 2
    
    def test_build_index_from_sources_no_files(self):
        """Test index building with no files found"""
        # Don't create temp file since method should return early
        temp_db = "/tmp/nonexistent.db"
        
        with patch.object(self.builder, '_discover_files_from_sources', return_value=[]):
            sources = [Path("/empty/dir")]
            file_types = ["txt"]
            
            # Should return early without creating database
            self.builder.build_index_from_sources(sources, temp_db, file_types)
            
            # Database should not be created
            assert not os.path.exists(temp_db)
    
    def test_build_index_from_sources_no_chunks(self):
        """Test index building with no chunks created"""
        # Don't create temp file since method should return early
        temp_db = "/tmp/nonexistent2.db"
        
        mock_files = [Path("test.txt")]
        
        with patch.object(self.builder, '_discover_files_from_sources', return_value=mock_files), \
             patch.object(self.builder, '_process_file', return_value=[]):
            
            sources = [Path("/home/user/docs")]
            file_types = ["txt"]
            
            # Should return early without creating database
            self.builder.build_index_from_sources(sources, temp_db, file_types)
            
            # Database should not be created
            assert not os.path.exists(temp_db)
    
    @patch('signalwire.search.index_builder.np')
    def test_build_index_from_sources_embedding_error(self, mock_np):
        """Test index building with embedding generation error"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            self.temp_db = f.name
        
        # Mock numpy for fallback embedding
        mock_zeros = Mock()
        mock_zeros.tobytes.return_value = b"zero_embedding"
        mock_np.zeros.return_value = mock_zeros
        
        mock_files = [Path("test.txt")]
        mock_chunks = [{"content": "Test content", "filename": "test.txt"}]
        
        # Mock model that raises error
        mock_model = Mock()
        mock_model.encode.side_effect = Exception("Embedding error")
        
        with patch.object(self.builder, '_discover_files_from_sources', return_value=mock_files), \
             patch.object(self.builder, '_process_file', return_value=mock_chunks), \
             patch.object(self.builder, '_load_model'), \
             patch.object(self.builder, '_create_database') as mock_create_db, \
             patch('signalwire.search.index_builder.preprocess_document_content') as mock_preprocess:
            
            mock_preprocess.return_value = {"enhanced_text": "enhanced", "keywords": []}
            self.builder.model = mock_model
            
            sources = [Path("/home/user/docs")]
            file_types = ["txt"]
            
            # Should handle error gracefully
            self.builder.build_index_from_sources(sources, self.temp_db, file_types)
            
            # Database should still be created with fallback embedding
            mock_create_db.assert_called_once()
    
    def test_build_index_legacy_method(self):
        """Test legacy build_index method"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            self.temp_db = f.name
        
        with patch.object(self.builder, 'build_index_from_sources') as mock_build:
            source_dir = "/home/user/docs"
            file_types = ["txt"]
            
            self.builder.build_index(source_dir, self.temp_db, file_types)
            
            # Should call new method with converted parameters
            mock_build.assert_called_once_with([Path(source_dir)], self.temp_db, file_types, None, None, None)


class TestIndexBuilderEdgeCases:
    """Test edge cases and error handling"""
    
    def test_create_database_embedding_dimension_error(self):
        """Test database creation with embedding dimension detection error"""
        builder = IndexBuilder()
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_db = f.name
        
        try:
            chunks = [{"content": "Test", "filename": "test.txt", "embedding": b"invalid_data"}]
            
            with patch('signalwire.search.index_builder.np') as mock_np:
                mock_np.frombuffer.side_effect = Exception("Invalid buffer")
                
                # Should handle error gracefully and use default dimensions
                builder._create_database(temp_db, chunks, ["en"], ["/home"], ["txt"])
                
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM config WHERE key='embedding_dimensions'")
                dimensions = cursor.fetchone()[0]
                assert dimensions == "768"  # Default
                conn.close()
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db) 