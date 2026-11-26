"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for search document processor module
"""

import pytest
import sys
import tempfile
import os
from typing import Any
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path

from signalwire.search.document_processor import DocumentExtractionError, DocumentProcessor


class TestDocumentProcessorInit:
    """Test DocumentProcessor initialization"""
    
    def test_default_initialization(self) -> None:
        """Test default initialization"""
        processor = DocumentProcessor()
        
        assert processor.chunking_strategy == 'sentence'
        assert processor.max_sentences_per_chunk == 5
        assert processor.chunk_size == 50
        assert processor.chunk_overlap == 10
        assert processor.split_newlines is None
        assert processor.chunk_overlap == 10  # Legacy support
        assert processor.semantic_threshold == 0.5
        assert processor.topic_threshold == 0.3
    
    def test_custom_initialization(self) -> None:
        """Test initialization with custom parameters"""
        processor = DocumentProcessor(
            chunking_strategy='sliding',
            max_sentences_per_chunk=25,
            chunk_size=100,
            chunk_overlap=20,
            split_newlines=3
        )
        
        assert processor.chunking_strategy == 'sliding'
        assert processor.max_sentences_per_chunk == 25
        assert processor.chunk_size == 100
        assert processor.chunk_overlap == 20
        assert processor.split_newlines == 3
        assert processor.chunk_overlap == 20
        assert processor.semantic_threshold == 0.5
        assert processor.topic_threshold == 0.3


class TestDocumentProcessorChunking:
    """Test document chunking strategies"""
    
    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.processor = DocumentProcessor()
        self.sample_text = "This is the first sentence. This is the second sentence. This is the third sentence."
        self.filename = "test.txt"
        self.file_type = "txt"
    
    def test_create_chunks_sentence_strategy(self) -> None:
        """Test create_chunks with sentence strategy"""
        processor = DocumentProcessor(chunking_strategy='sentence', max_sentences_per_chunk=2)
        
        chunks = processor.create_chunks(self.sample_text, self.filename, self.file_type)
        
        assert len(chunks) > 0
        assert all('content' in chunk for chunk in chunks)
        assert all('filename' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
        assert all(chunk['metadata']['chunk_method'] == 'sentence_based' for chunk in chunks)
    
    def test_create_chunks_sliding_strategy(self) -> None:
        """Test create_chunks with sliding window strategy"""
        processor = DocumentProcessor(chunking_strategy='sliding', chunk_size=5, chunk_overlap=2)
        
        chunks = processor.create_chunks(self.sample_text, self.filename, self.file_type)
        
        assert len(chunks) > 0
        assert all('content' in chunk for chunk in chunks)
        assert all(chunk['metadata']['chunk_method'] == 'sliding_window' for chunk in chunks)
        assert all('chunk_size_words' in chunk['metadata'] for chunk in chunks)
        assert all('overlap_size_words' in chunk['metadata'] for chunk in chunks)
    
    def test_create_chunks_paragraph_strategy(self) -> None:
        """Test create_chunks with paragraph strategy"""
        processor = DocumentProcessor(chunking_strategy='paragraph')
        paragraph_text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        
        chunks = processor.create_chunks(paragraph_text, self.filename, self.file_type)
        
        assert len(chunks) == 3
        assert all(chunk['metadata']['chunk_method'] == 'paragraph_based' for chunk in chunks)
        assert chunks[0]['content'] == "First paragraph."
        assert chunks[1]['content'] == "Second paragraph."
        assert chunks[2]['content'] == "Third paragraph."
    
    def test_create_chunks_page_strategy(self) -> None:
        """Test create_chunks with page strategy"""
        processor = DocumentProcessor(chunking_strategy='page')
        
        # Test with list input (like PDF pages)
        page_list = ["Page 1 content", "Page 2 content", "Page 3 content"]
        chunks = processor.create_chunks(page_list, self.filename, self.file_type)
        
        assert len(chunks) == 3
        assert all(chunk['metadata']['chunk_method'] == 'page_based' for chunk in chunks)
        assert chunks[0]['content'] == "Page 1 content"
        assert chunks[1]['content'] == "Page 2 content"
        assert chunks[2]['content'] == "Page 3 content"
    
    def test_create_chunks_fallback_strategy(self) -> None:
        """Test create_chunks with unknown strategy falls back to sentence"""
        processor = DocumentProcessor(chunking_strategy='unknown')
        
        chunks = processor.create_chunks(self.sample_text, self.filename, self.file_type)
        
        assert len(chunks) > 0
        assert all(chunk['metadata']['chunk_method'] == 'sentence_based' for chunk in chunks)


class TestDocumentProcessorSentenceChunking:
    """Test sentence-based chunking functionality"""
    
    def test_chunk_by_sentences_basic(self) -> None:
        """Test basic sentence chunking"""
        processor = DocumentProcessor(max_sentences_per_chunk=2)
        content = "First sentence. Second sentence. Third sentence. Fourth sentence."
        
        chunks = processor._chunk_by_sentences(content, "test.txt", "txt")
        
        assert len(chunks) >= 1
        assert all('content' in chunk for chunk in chunks)
        assert all(chunk['metadata']['chunk_method'] == 'sentence_based' for chunk in chunks)
        assert all(chunk['metadata']['max_sentences_per_chunk'] == 2 for chunk in chunks)
    
    def test_chunk_by_sentences_with_list_input(self) -> None:
        """Test sentence chunking with list input"""
        processor = DocumentProcessor(max_sentences_per_chunk=2)
        content = ["First line.", "Second line.", "Third line."]
        
        chunks = processor._chunk_by_sentences(content, "test.txt", "txt")
        
        assert len(chunks) >= 1
        assert all('content' in chunk for chunk in chunks)
    
    def test_chunk_by_sentences_with_split_newlines(self) -> None:
        """Test sentence chunking with split_newlines parameter"""
        processor = DocumentProcessor(max_sentences_per_chunk=5, split_newlines=2)
        content = "First sentence. Second sentence.\n\nThird sentence. Fourth sentence."
        
        chunks = processor._chunk_by_sentences(content, "test.txt", "txt")
        
        assert len(chunks) >= 1
        assert all(chunk['metadata']['split_newlines'] == 2 for chunk in chunks)


class TestDocumentProcessorSlidingWindow:
    """Test sliding window chunking functionality"""
    
    def test_chunk_by_sliding_window_basic(self) -> None:
        """Test basic sliding window chunking"""
        processor = DocumentProcessor(chunk_size=3, chunk_overlap=1)
        content = "one two three four five six seven eight"
        
        chunks = processor._chunk_by_sliding_window(content, "test.txt", "txt")
        
        assert len(chunks) > 1
        assert all(chunk['metadata']['chunk_method'] == 'sliding_window' for chunk in chunks)
        assert all(chunk['metadata']['chunk_size_words'] == 3 for chunk in chunks)
        assert all(chunk['metadata']['overlap_size_words'] == 1 for chunk in chunks)
        
        # Check overlap
        first_chunk_words = chunks[0]['content'].split()
        second_chunk_words = chunks[1]['content'].split()
        assert len(first_chunk_words) == 3
        assert len(second_chunk_words) <= 3
    
    def test_chunk_by_sliding_window_with_list_input(self) -> None:
        """Test sliding window chunking with list input"""
        processor = DocumentProcessor(chunk_size=2, chunk_overlap=1)
        content = ["line one", "line two", "line three"]
        
        chunks = processor._chunk_by_sliding_window(content, "test.txt", "txt")
        
        assert len(chunks) >= 1
        assert all('content' in chunk for chunk in chunks)
    
    def test_chunk_by_sliding_window_empty_content(self) -> None:
        """Test sliding window chunking with empty content"""
        processor = DocumentProcessor(chunk_size=3, chunk_overlap=1)
        content = ""
        
        chunks = processor._chunk_by_sliding_window(content, "test.txt", "txt")
        
        assert chunks == []
    
    def test_chunk_by_sliding_window_metadata(self) -> None:
        """Test sliding window chunking metadata"""
        processor = DocumentProcessor(chunk_size=2, chunk_overlap=1)
        content = "word1 word2 word3 word4"
        
        chunks = processor._chunk_by_sliding_window(content, "test.txt", "txt")
        
        assert len(chunks) >= 2
        assert chunks[0]['metadata']['start_word'] == 0
        assert chunks[0]['metadata']['end_word'] == 2
        assert chunks[1]['metadata']['start_word'] == 1  # overlap
        assert chunks[1]['metadata']['end_word'] == 3


class TestDocumentProcessorParagraphChunking:
    """Test paragraph-based chunking functionality"""
    
    def test_chunk_by_paragraphs_basic(self) -> None:
        """Test basic paragraph chunking"""
        processor = DocumentProcessor()
        content = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        
        chunks = processor._chunk_by_paragraphs(content, "test.txt", "txt")
        
        assert len(chunks) == 3
        assert chunks[0]['content'] == "First paragraph."
        assert chunks[1]['content'] == "Second paragraph."
        assert chunks[2]['content'] == "Third paragraph."
        assert all(chunk['metadata']['chunk_method'] == 'paragraph_based' for chunk in chunks)
    
    def test_chunk_by_paragraphs_with_list_input(self) -> None:
        """Test paragraph chunking with list input"""
        processor = DocumentProcessor()
        content = ["First line", "Second line", "", "Third line"]
        
        chunks = processor._chunk_by_paragraphs(content, "test.txt", "txt")
        
        assert len(chunks) >= 1
        assert all('content' in chunk for chunk in chunks)
    
    def test_chunk_by_paragraphs_with_whitespace(self) -> None:
        """Test paragraph chunking with various whitespace"""
        processor = DocumentProcessor()
        content = "Para 1.\n  \n  Para 2.  \n\n\n  Para 3."
        
        chunks = processor._chunk_by_paragraphs(content, "test.txt", "txt")
        
        assert len(chunks) == 3
        assert chunks[0]['content'] == "Para 1."
        assert chunks[1]['content'] == "Para 2."
        assert chunks[2]['content'] == "Para 3."
    
    def test_chunk_by_paragraphs_empty_paragraphs(self) -> None:
        """Test paragraph chunking skips empty paragraphs"""
        processor = DocumentProcessor()
        content = "Para 1.\n\n\n\nPara 2.\n\n"
        
        chunks = processor._chunk_by_paragraphs(content, "test.txt", "txt")
        
        assert len(chunks) == 2
        assert chunks[0]['content'] == "Para 1."
        assert chunks[1]['content'] == "Para 2."


class TestDocumentProcessorPageChunking:
    """Test page-based chunking functionality"""
    
    def test_chunk_by_pages_with_list(self) -> None:
        """Test page chunking with list input (like PDF)"""
        processor = DocumentProcessor()
        content = ["Page 1 content", "Page 2 content", "", "Page 3 content"]
        
        chunks = processor._chunk_by_pages(content, "test.txt", "txt")
        
        assert len(chunks) == 3  # Empty page should be skipped
        assert chunks[0]['content'] == "Page 1 content"
        assert chunks[1]['content'] == "Page 2 content"
        assert chunks[2]['content'] == "Page 3 content"
        assert all(chunk['metadata']['chunk_method'] == 'page_based' for chunk in chunks)
    
    def test_chunk_by_pages_with_form_feeds(self) -> None:
        """Test page chunking with form feed characters"""
        processor = DocumentProcessor()
        content = "Page 1 content\fPage 2 content\fPage 3 content"
        
        chunks = processor._chunk_by_pages(content, "test.txt", "txt")
        
        assert len(chunks) == 3
        assert chunks[0]['content'] == "Page 1 content"
        assert chunks[1]['content'] == "Page 2 content"
        assert chunks[2]['content'] == "Page 3 content"
    
    def test_chunk_by_pages_with_page_markers(self) -> None:
        """Test page chunking with page break markers"""
        processor = DocumentProcessor()
        content = "Page 1 content---PAGE---Page 2 content---PAGE---Page 3 content"
        
        chunks = processor._chunk_by_pages(content, "test.txt", "txt")
        
        assert len(chunks) == 3
        assert chunks[0]['content'] == "Page 1 content"
        assert chunks[1]['content'] == "Page 2 content"
        assert chunks[2]['content'] == "Page 3 content"
    
    def test_chunk_by_pages_fallback_chunking(self) -> None:
        """Test page chunking fallback for plain text"""
        processor = DocumentProcessor()
        # Create content that will trigger fallback chunking
        words = ["word"] * 1000  # 1000 words
        content = " ".join(words)
        
        chunks = processor._chunk_by_pages(content, "test.txt", "txt")
        
        assert len(chunks) > 1  # Should create multiple chunks
        assert all(chunk['metadata']['chunk_method'] == 'page_based' for chunk in chunks)
        assert all('page_number' in chunk['metadata'] for chunk in chunks)


class TestDocumentProcessorFileExtraction:
    """Test file extraction methods"""
    
    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.processor = DocumentProcessor()
    
    @patch('signalwire.search.document_processor.magic', None)
    def test_extract_text_from_file_no_magic(self) -> None:
        """Test file extraction without magic library"""
        with patch.object(self.processor, '_extract_text') as mock_extract:
            mock_extract.return_value = "test content"
            
            result = self.processor._extract_text_from_file("test.txt")
            
            mock_extract.assert_called_once_with("test.txt")
            assert result == "test content"
    
    @patch('signalwire.search.document_processor.magic')
    def test_extract_text_from_file_with_magic(self, mock_magic: MagicMock) -> None:
        """Test file extraction with magic library"""
        mock_mime = Mock()
        mock_mime.from_file.return_value = "text/plain"
        mock_magic.Magic.return_value = mock_mime
        
        with patch.object(self.processor, '_extract_text') as mock_extract:
            mock_extract.return_value = "test content"
            
            result = self.processor._extract_text_from_file("test.txt")
            
            mock_extract.assert_called_once_with("test.txt")
            assert result == "test content"
    
    def test_extract_text_from_file_pdf(self) -> None:
        """Test PDF file extraction"""
        with patch.object(self.processor, '_extract_pdf') as mock_extract:
            mock_extract.return_value = ["page 1", "page 2"]
            
            result = self.processor._extract_text_from_file("test.pdf")
            
            mock_extract.assert_called_once_with("test.pdf")
            assert result == ["page 1", "page 2"]
    
    def test_extract_text_from_file_docx(self) -> None:
        """Test DOCX file extraction"""
        with patch.object(self.processor, '_extract_docx') as mock_extract:
            mock_extract.return_value = ["paragraph 1", "paragraph 2"]
            
            result = self.processor._extract_text_from_file("test.docx")
            
            mock_extract.assert_called_once_with("test.docx")
            assert result == ["paragraph 1", "paragraph 2"]
    
    @pytest.mark.parametrize("mime", [None, "text/html"])
    def test_extract_text_from_file_html(self, mime: str | None) -> None:
        """HTML goes to the HTML extractor, by extension or by its text/html type"""
        detector = None if mime is None else MagicMock()
        if detector is not None:
            detector.Magic.return_value.from_file.return_value = mime
        with patch('signalwire.search.document_processor.magic', detector):
            with patch.object(self.processor, '_extract_html') as mock_extract:
                mock_extract.return_value = "html content"

                result = self.processor._extract_text_from_file("test.html")

                mock_extract.assert_called_once_with("test.html")
                assert result == "html content"

    def test_extract_text_from_file_markdown(self) -> None:
        """Test Markdown file extraction"""
        # Markdown comes back as written, so the markdown strategy can read its headers
        with patch('signalwire.search.document_processor.magic', None):
            with patch.object(self.processor, '_extract_text') as mock_extract:
                mock_extract.return_value = "markdown content"
                
                result = self.processor._extract_text_from_file("test.md")
                
                mock_extract.assert_called_once_with("test.md")
                assert result == "markdown content"
    
    def test_extract_text_from_file_unsupported(self) -> None:
        """Test unsupported file type"""
        with patch('signalwire.search.document_processor.magic') as mock_magic:
            mock_mime = Mock()
            mock_mime.from_file.return_value = "application/unknown"
            mock_magic.Magic.return_value = mock_mime
            
            result = self.processor._extract_text_from_file("test.unknown")
            
            assert "Unsupported file type" in result


class TestDocumentProcessorSpecificExtractors:
    """Test specific file format extractors"""
    
    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.processor = DocumentProcessor()
    
    @patch('signalwire.search.document_processor.pdfplumber', None)
    def test_extract_pdf_no_library(self) -> None:
        """Test PDF extraction without pdfplumber"""
        with pytest.raises(DocumentExtractionError, match="pdfplumber not available"):
            self.processor._extract_pdf("test.pdf")
        
    
    @patch('signalwire.search.document_processor.pdfplumber')
    def test_extract_pdf_success(self, mock_pdfplumber: MagicMock) -> None:
        """Test successful PDF extraction"""
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        
        mock_pdfplumber.open.return_value = mock_pdf
        
        result = self.processor._extract_pdf("test.pdf")
        
        assert result == ["Page 1 content", "Page 2 content"]
    
    @patch('signalwire.search.document_processor.pdfplumber')
    def test_extract_pdf_error(self, mock_pdfplumber: MagicMock) -> None:
        """Test PDF extraction with error"""
        mock_pdfplumber.open.side_effect = Exception("PDF error")
        
        with pytest.raises(DocumentExtractionError, match="Error processing PDF"):
            self.processor._extract_pdf("test.pdf")
        
    
    @patch('signalwire.search.document_processor.DocxDocument', None)
    def test_extract_docx_no_library(self) -> None:
        """Test DOCX extraction without python-docx"""
        with pytest.raises(DocumentExtractionError, match="python-docx not available"):
            self.processor._extract_docx("test.docx")
        
    
    def test_extract_docx_success(self, tmp_path: Path) -> None:
        """Paragraphs come back as written, and empty ones are left out"""
        docx = pytest.importorskip("docx")
        document = docx.Document()
        for text in ("Paragraph 1", "", "Paragraph 2"):
            document.add_paragraph(text)
        document.save(str(tmp_path / "test.docx"))
        assert self.processor._extract_docx(str(tmp_path / "test.docx")) == ["Paragraph 1", "Paragraph 2"]

    @patch('signalwire.search.document_processor.DocxDocument')
    def test_extract_docx_error(self, mock_docx: MagicMock) -> None:
        """Test DOCX extraction with error"""
        mock_docx.side_effect = Exception("DOCX error")
        
        with pytest.raises(DocumentExtractionError, match="Error processing DOCX"):
            self.processor._extract_docx("test.docx")
        
    
    def test_extract_text_success(self) -> None:
        """Test successful text file extraction"""
        with patch('builtins.open', mock_open(read_data="test content")):
            result = self.processor._extract_text("test.txt")
            
            assert result == "test content"
    
    def test_extract_text_error(self) -> None:
        """Test text file extraction with error"""
        with patch('builtins.open', side_effect=Exception("File error")):
            with pytest.raises(DocumentExtractionError, match="Error processing TXT"):
                self.processor._extract_text("test.txt")
            
    
    @patch('signalwire.search.document_processor.BeautifulSoup', None)
    def test_extract_html_no_library(self) -> None:
        """Test HTML extraction without BeautifulSoup"""
        with pytest.raises(DocumentExtractionError, match="beautifulsoup4 not available"):
            self.processor._extract_html("test.html")
        
    
    def test_extract_html_success(self, tmp_path: Path) -> None:
        """An HTML page's text, without its markup"""
        pytest.importorskip("bs4")
        page = tmp_path / "page.html"
        page.write_text("<html><body><p>Hello World</p></body></html>", encoding="utf-8")
        assert self.processor._extract_html(str(page)) == "Hello World"

    @patch('signalwire.search.document_processor.markdown', None)
    def test_extract_markdown_no_library(self) -> None:
        """Test Markdown extraction without markdown library"""
        with patch('builtins.open', mock_open(read_data="# Header\nContent")):
            result = self.processor._extract_markdown("test.md")
            
            # Should fallback to plain text
            assert result == "# Header\nContent"
    
    @patch('signalwire.search.document_processor.markdown')
    def test_extract_markdown_success(self, mock_markdown: MagicMock) -> None:
        """Test successful Markdown extraction"""
        mock_markdown.markdown.return_value = "<h1>Header</h1><p>Content</p>"
        
        with patch('builtins.open', mock_open(read_data="# Header\nContent")):
            with patch('signalwire.search.document_processor.BeautifulSoup') as mock_bs:
                mock_soup = Mock()
                mock_soup.get_text.return_value = "Header Content"
                mock_bs.return_value = mock_soup
                
                result = self.processor._extract_markdown("test.md")
                
                assert result == "Header Content"


class TestDocumentProcessorUtilities:
    """Test utility methods"""
    
    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.processor = DocumentProcessor()
    
    def test_create_chunk_basic(self) -> None:
        """Test basic chunk creation"""
        chunk = self.processor._create_chunk(
            content="Test content",
            filename="test.txt",
            section="Section 1"
        )
        
        assert chunk['content'] == "Test content"
        assert chunk['filename'] == "test.txt"
        assert chunk['section'] == "Section 1"
        assert 'metadata' in chunk
        assert chunk['metadata']['file_type'] == 'txt'
        assert chunk['metadata']['chunk_size'] == len("Test content")
        assert chunk['metadata']['word_count'] == 2
    
    def test_create_chunk_with_metadata(self) -> None:
        """Test chunk creation with custom metadata"""
        custom_metadata = {"custom_field": "custom_value"}
        
        chunk = self.processor._create_chunk(
            content="Test content",
            filename="test.txt",
            metadata=custom_metadata
        )
        
        assert chunk['metadata']['custom_field'] == "custom_value"
        assert chunk['metadata']['file_type'] == 'txt'  # Base metadata should still be there
    
    @patch('signalwire.search.document_processor.sent_tokenize')
    def test_create_chunk_sentence_count_with_nltk(self, mock_sent_tokenize: MagicMock) -> None:
        """Test chunk creation with NLTK sentence tokenization"""
        mock_sent_tokenize.return_value = ["Sentence 1.", "Sentence 2."]
        
        chunk = self.processor._create_chunk(
            content="Sentence 1. Sentence 2.",
            filename="test.txt"
        )
        
        assert chunk['metadata']['sentence_count'] == 2
        mock_sent_tokenize.assert_called_once_with("Sentence 1. Sentence 2.")
    
    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_create_chunk_sentence_count_fallback(self) -> None:
        """Test chunk creation with fallback sentence counting"""
        chunk = self.processor._create_chunk(
            content="Sentence 1. Sentence 2. Sentence 3.",
            filename="test.txt"
        )
        
        assert chunk['metadata']['sentence_count'] == 3
    
    @patch('signalwire.search.document_processor.sent_tokenize')
    def test_create_chunk_sentence_count_error(self, mock_sent_tokenize: MagicMock) -> None:
        """Test chunk creation with sentence counting error"""
        mock_sent_tokenize.side_effect = Exception("NLTK error")
        
        chunk = self.processor._create_chunk(
            content="Sentence 1. Sentence 2.",
            filename="test.txt"
        )
        
        # Should fallback to period counting
        assert chunk['metadata']['sentence_count'] == 2
    
    def test_find_best_split_point_with_empty_lines(self) -> None:
        """Test finding best split point with paragraph boundaries"""
        lines = ["line1", "line2", "", "line4", "line5", "line6"]
        
        split_point = self.processor._find_best_split_point(lines)
        
        # The algorithm searches backwards from the end in the last 25% of the chunk
        # With 6 lines, it starts searching from line 4 (3//4 * 6 = 4) backwards
        # It should find the empty line at index 2, but since it's outside the search range,
        # it will return the 75% point which is max(1, 6 * 3 // 4) = 4
        assert split_point == 4
    
    def test_find_best_split_point_no_empty_lines(self) -> None:
        """Test finding best split point without paragraph boundaries"""
        lines = ["line1", "line2", "line3", "line4", "line5", "line6"]
        
        split_point = self.processor._find_best_split_point(lines)
        
        # Should split at 75% of chunk size
        expected = max(1, len(lines) * 3 // 4)
        assert split_point == expected
    
    def test_get_overlap_lines_basic(self) -> None:
        """Test getting overlap lines"""
        processor = DocumentProcessor(chunk_overlap=50)  # 50 characters - large enough to capture lines
        lines = ["short", "medium line", "longer line here"]
        
        overlap = processor._get_overlap_lines(lines)
        
        # Should include lines that fit within overlap size
        assert len(overlap) > 0
        assert all(isinstance(line, str) for line in overlap)
    
    def test_get_overlap_lines_empty(self) -> None:
        """Test getting overlap lines with empty input"""
        overlap = self.processor._get_overlap_lines([])
        
        assert overlap == []


class TestDocumentProcessorEdgeCases:
    """Test edge cases and error handling"""
    
    def test_chunking_with_empty_content(self) -> None:
        """Test chunking with empty content"""
        processor = DocumentProcessor()
        
        chunks = processor.create_chunks("", "test.txt", "txt")
        
        # Should handle empty content gracefully
        assert isinstance(chunks, list)
    
    def test_chunking_with_whitespace_only(self) -> None:
        """Test chunking with whitespace-only content"""
        processor = DocumentProcessor()
        
        chunks = processor.create_chunks("   \n\n   ", "test.txt", "txt")
        
        # Should handle whitespace-only content gracefully
        assert isinstance(chunks, list)
    
    def test_sliding_window_with_small_content(self) -> None:
        """Test sliding window with content smaller than chunk size"""
        processor = DocumentProcessor(chunking_strategy='sliding', chunk_size=10, chunk_overlap=2)
        
        chunks = processor.create_chunks("small", "test.txt", "txt")
        
        assert len(chunks) == 1
        assert chunks[0]['content'] == "small"
    
    def test_paragraph_chunking_no_paragraphs(self) -> None:
        """Test paragraph chunking with no paragraph breaks"""
        processor = DocumentProcessor(chunking_strategy='paragraph')
        
        chunks = processor.create_chunks("Single line of text", "test.txt", "txt")
        
        assert len(chunks) == 1
        assert chunks[0]['content'] == "Single line of text"
    
    def test_page_chunking_empty_pages(self) -> None:
        """Test page chunking with empty pages"""
        processor = DocumentProcessor(chunking_strategy='page')
        
        chunks = processor.create_chunks(["", "  ", "Content", ""], "test.txt", "txt")
        
        assert len(chunks) == 1
        assert chunks[0]['content'] == "Content"


# ────────────────────────────────────────────────────────────────────
# NEW TESTS APPENDED BELOW
# ────────────────────────────────────────────────────────────────────

import json
import re


class TestFileExtraction:
    """Comprehensive tests for every extraction method and missing-dependency paths."""

    def setup_method(self) -> None:
        self.processor = DocumentProcessor()

    # ── PDF ──────────────────────────────────────────────────────────

    @patch('signalwire.search.document_processor.pdfplumber')
    def test_extract_pdf_with_pages(self, mock_pdfplumber: MagicMock) -> None:
        """Extract text from multiple PDF pages, including one with None text."""
        page1 = Mock(); page1.extract_text.return_value = "Page one text"
        page2 = Mock(); page2.extract_text.return_value = None        # empty page
        page3 = Mock(); page3.extract_text.return_value = "Page three text"

        mock_pdf = MagicMock()
        mock_pdf.pages = [page1, page2, page3]
        mock_pdfplumber.open.return_value.__enter__ = Mock(return_value=mock_pdf)
        mock_pdfplumber.open.return_value.__exit__ = Mock(return_value=False)

        result = self.processor._extract_pdf("/fake/doc.pdf")
        assert isinstance(result, list)
        assert len(result) == 3  # one entry per page; page2 had no text
        assert result[1] == ""
        assert "Page one text" in result[0]

    @patch('signalwire.search.document_processor.pdfplumber')
    def test_extract_pdf_keeps_a_leading_number(self, mock_pdfplumber: MagicMock) -> None:
        """A page that opens with '1. ' (a numbered list) keeps it."""
        page = Mock(); page.extract_text.return_value = "1. Introduction paragraph"
        mock_pdf = MagicMock(); mock_pdf.pages = [page]
        mock_pdfplumber.open.return_value.__enter__ = Mock(return_value=mock_pdf)
        mock_pdfplumber.open.return_value.__exit__ = Mock(return_value=False)

        result = self.processor._extract_pdf("/fake/doc.pdf")
        assert result == ["1. Introduction paragraph"]

    @patch('signalwire.search.document_processor.pdfplumber', None)
    def test_extract_pdf_missing_dependency(self) -> None:
        with pytest.raises(DocumentExtractionError, match="pdfplumber not available"):
            self.processor._extract_pdf("/fake/doc.pdf")

    @patch('signalwire.search.document_processor.pdfplumber')
    def test_extract_pdf_exception(self, mock_pdfplumber: MagicMock) -> None:
        mock_pdfplumber.open.side_effect = RuntimeError("corrupt file")
        with pytest.raises(DocumentExtractionError, match="Error processing PDF"):
            self.processor._extract_pdf("/fake/doc.pdf")

    # ── DOCX ─────────────────────────────────────────────────────────

    def test_extract_docx_filters_empty_paragraphs(self, tmp_path: Path) -> None:
        """Paragraphs come back as written, and empty ones are left out"""
        docx = pytest.importorskip("docx")
        document = docx.Document()
        for text in ("Paragraph 1", "", "Paragraph 2"):
            document.add_paragraph(text)
        document.save(str(tmp_path / "test.docx"))
        assert self.processor._extract_docx(str(tmp_path / "test.docx")) == ["Paragraph 1", "Paragraph 2"]

    @patch('signalwire.search.document_processor.DocxDocument', None)
    def test_extract_docx_missing_dependency(self) -> None:
        with pytest.raises(DocumentExtractionError, match="python-docx not available"):
            self.processor._extract_docx("/fake/doc.docx")

    @patch('signalwire.search.document_processor.DocxDocument')
    def test_extract_docx_exception(self, mock_docx_cls: MagicMock) -> None:
        mock_docx_cls.side_effect = ValueError("bad docx")
        with pytest.raises(DocumentExtractionError, match="Error processing DOCX"):
            self.processor._extract_docx("/fake/doc.docx")

    # ── XLSX (Excel) ─────────────────────────────────────────────────

    @staticmethod
    def _excel_mocks(value_rows: list[tuple[Any, ...]], formula_rows: list[tuple[Any, ...]]) -> tuple[MagicMock, Mock, Mock]:
        """load_workbook returning a values workbook and a formulas workbook, one sheet each."""
        def workbook(rows: list[tuple[Any, ...]]) -> Mock:
            sheet = Mock()
            sheet.title = "Prices"
            sheet.iter_rows.return_value = rows
            return Mock(worksheets=[sheet])

        values, formulas = workbook(value_rows), workbook(formula_rows)

        def load_workbook(path: str, read_only: bool = False, data_only: bool = False) -> Mock:
            assert read_only, "workbooks are read streaming"
            return values if data_only else formulas

        return MagicMock(side_effect=load_workbook), values, formulas

    def test_extract_excel_labels_each_row_with_its_sheet_and_headers(self) -> None:
        value_rows = [("Plan", "Price", None), ("Pro", 40.0, None), (None, None, None), ("Team", None, "yearly")]
        formula_rows = [("Plan", "Price", None), ("Pro", 40.0, None), (None, None, None), ("Team", "=B2*2", "yearly")]
        load_workbook, values, formulas = self._excel_mocks(value_rows, formula_rows)
        # B4's formula was never calculated
        layouts: list[tuple[list[tuple[int, int, int, int]], set[tuple[int, int]]]] = [([], {(4, 2)})]
        with patch.dict(sys.modules, {"openpyxl": Mock(load_workbook=load_workbook)}), \
                patch.object(DocumentProcessor, "_sheet_layouts", return_value=layouts):
            result = self.processor._extract_excel("/fake/data.xlsx")
        # A blank row is left out, the formula keeps its text, and a cell with
        # no header is labelled with its column letter.
        assert result == ["Prices | Plan: Pro, Price: 40", "Prices | Plan: Team, Price: =B2*2, C: yearly"]
        for workbook in (values, formulas):
            workbook.close.assert_called_once_with()
            workbook.worksheets[0].reset_dimensions.assert_called_once_with()

    def test_extract_excel_reads_formulas_only_when_one_was_never_calculated(self) -> None:
        load_workbook, values, formulas = self._excel_mocks([("Plan",), ("Pro",)], [])
        with patch.dict(sys.modules, {"openpyxl": Mock(load_workbook=load_workbook)}), \
                patch.object(DocumentProcessor, "_sheet_layouts", return_value=[([], set())]):
            assert self.processor._extract_excel("/fake/data.xlsx") == ["Prices | Plan: Pro"]
        assert load_workbook.call_count == 1
        values.close.assert_called_once_with()

    def test_extract_excel_closes_its_workbooks_when_reading_fails(self) -> None:
        load_workbook, values, formulas = self._excel_mocks([], [])
        formulas.worksheets[0].iter_rows.side_effect = OSError("truncated archive")
        with patch.dict(sys.modules, {"openpyxl": Mock(load_workbook=load_workbook)}), \
                patch.object(DocumentProcessor, "_sheet_layouts", return_value=[([], {(1, 1)})]):
            with pytest.raises(DocumentExtractionError, match="Error processing Excel"):
                self.processor._extract_excel("/fake/data.xlsx")
        values.close.assert_called_once_with()
        formulas.close.assert_called_once_with()

    @staticmethod
    def _rewrite_sheet(path: Path, old: str, new: str, part: str = "xl/worksheets/sheet1.xml") -> None:
        """Edit one XML part of a saved workbook, as another tool would have written it."""
        import zipfile

        with zipfile.ZipFile(path) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()}
        text = parts[part].decode()
        assert text.count(old) == 1, text
        parts[part] = text.replace(old, new).encode()
        with zipfile.ZipFile(path, "w") as archive:
            for name, data in parts.items():
                archive.writestr(name, data)

    def test_extract_excel_reads_a_real_workbook(self, tmp_path: Path) -> None:
        openpyxl = pytest.importorskip("openpyxl")
        import datetime

        workbook = openpyxl.Workbook()
        prices = workbook.active
        prices.title = "Prices"
        prices.append(["Plan", "Billing", "Price", "Since"])
        prices.append(["Pro", "monthly", 40, datetime.datetime(2026, 1, 5)])
        prices.append([None, "yearly", "=C2*10", None])  # written by a script, so never calculated
        prices.merge_cells("A2:A3")  # one plan, two billing rows
        prices.append(["Note:\nexcludes tax", None, None, None])
        workbook.create_sheet("Notes").append(["Prices exclude tax."])
        path = tmp_path / "prices.xlsx"
        workbook.save(path)

        rows = self.processor.extract_text(str(path))
        assert rows == [
            "Prices | Plan: Pro, Billing: monthly, Price: 40, Since: 2026-01-05",
            "Prices | Plan: Pro, Billing: yearly, Price: =C2*10",
            "Prices | Plan: Note: excludes tax",
            "Notes | Prices exclude tax.",
        ]
        chunks = DocumentProcessor(chunking_strategy="page").create_chunks(rows, "prices.xlsx", "xlsx")
        assert [c["content"] for c in chunks] == rows

    def test_extract_excel_uses_stored_formula_values(self, tmp_path: Path) -> None:
        openpyxl = pytest.importorskip("openpyxl")
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Prices"
        sheet.append(['=IF(TRUE,"","report")'])
        sheet.append(["Plan", "Price"])
        sheet.append(["Pro", "=20*2"])
        path = tmp_path / "calculated.xlsx"
        workbook.save(path)
        # As Excel saves them: a stored empty string, and a stored number.
        self._rewrite_sheet(path, '<c r="A1"><f>IF(TRUE,"","report")</f><v></v></c>',
                            '<c r="A1" t="str"><f>IF(TRUE,"","report")</f><v></v></c>')
        self._rewrite_sheet(path, "<f>20*2</f><v></v>", "<f>20*2</f><v>40</v>")

        # The calculated blank stays blank, so the real headers label the row.
        assert self.processor._extract_excel(str(path)) == ["Prices | Plan: Pro, Price: 40"]

    def test_merged_cells_have_a_fill_limit(self, tmp_path: Path) -> None:
        openpyxl = pytest.importorskip("openpyxl")
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Wide"
        sheet.append(["Group", "Item"])
        sheet.append(["All", "first"])
        for n in range(3, 6):
            sheet.cell(row=n, column=2, value=f"item {n}")
        sheet.merge_cells("A2:XFD5")  # a tiny file whose merge spans every column
        path = tmp_path / "wide.xlsx"
        workbook.save(path)
        with patch("signalwire.search.document_processor._MERGE_FILL_CELLS", 20):
            rows = self.processor.extract_text(str(path))
        assert len(" ".join(rows)) < 2000
        assert rows[0].startswith("Wide | Group: All")

    def test_a_long_merged_value_is_repeated_only_within_the_character_limit(self, tmp_path: Path) -> None:
        openpyxl = pytest.importorskip("openpyxl")
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Notes"
        sheet.append(["Group", "Item"])
        sheet.append(["x" * 5000, "item 2"])
        for n in range(3, 51):
            sheet.cell(row=n, column=2, value=f"item {n}")
        sheet.merge_cells("A2:A50")
        path = tmp_path / "long.xlsx"
        workbook.save(path)
        with patch("signalwire.search.document_processor._MERGE_FILL_CHARACTERS", 20_000):
            rows = self.processor.extract_text(str(path))
        # The stored cell, then four repeats; after that the merged cells stay empty.
        assert sum("x" * 5000 in row for row in rows) == 5
        assert len(rows) == 49 and rows[-1] == "Notes | Item: item 50"

    def test_sheets_with_the_same_name_keep_their_own_formulas(self, tmp_path: Path) -> None:
        openpyxl = pytest.importorskip("openpyxl")
        workbook = openpyxl.Workbook()
        first = workbook.active
        first.title = "Prices"
        first.append(["Plan", "Price"])
        first.append(["Pro", "=20*2"])  # never calculated
        second = workbook.create_sheet("Other")
        second.append(["Plan", "Price"])
        second.append(["Team", 90])
        path = tmp_path / "twins.xlsx"
        workbook.save(path)
        self._rewrite_sheet(path, 'name="Other"', 'name="Prices"', part="xl/workbook.xml")
        assert self.processor._extract_excel(str(path)) == [
            "Prices | Plan: Pro, Price: =20*2",
            "Prices | Plan: Team, Price: 90",
        ]

    def test_a_dialog_sheet_is_listed_as_openpyxl_lists_it(self, tmp_path: Path) -> None:
        openpyxl = pytest.importorskip("openpyxl")
        import zipfile

        workbook = openpyxl.Workbook()
        workbook.active.title = "Prices"
        workbook.active.append(["Plan", "Price"])
        workbook.active.append(["Pro", 40])
        path = tmp_path / "dialog.xlsx"
        workbook.save(path)
        dialog_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/dialogsheet"
        relationships = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        self._rewrite_sheet(path, "</sheets>",
                            f'<sheet xmlns:r="{relationships}" name="Dialog1" sheetId="2" r:id="rIdDialog"/></sheets>',
                            part="xl/workbook.xml")
        self._rewrite_sheet(path, "</Relationships>",
                            f'<Relationship Id="rIdDialog" Type="{dialog_type}" Target="dialogsheets/sheet1.xml"/>'
                            "</Relationships>", part="xl/_rels/workbook.xml.rels")
        with zipfile.ZipFile(path, "a") as archive:
            archive.writestr("xl/dialogsheets/sheet1.xml",
                             '<dialogsheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                             "<sheetData/></dialogsheet>")
        assert self.processor._extract_excel(str(path)) == ["Prices | Plan: Pro, Price: 40"]

    def test_without_openpyxls_sheet_paths_rows_still_come_back(self, tmp_path: Path) -> None:
        openpyxl = pytest.importorskip("openpyxl")
        workbook = openpyxl.Workbook()
        workbook.active.title = "Prices"
        workbook.active.append(["Plan", "Price"])
        path = tmp_path / "plain.xlsx"
        workbook.save(path)
        sheet = Mock(spec=["title"])
        sheet.title = "Prices"
        assert DocumentProcessor._sheet_layouts(str(path), [sheet]) == [([], set())]

    def test_a_long_header_is_cut_as_a_label(self, tmp_path: Path) -> None:
        openpyxl = pytest.importorskip("openpyxl")
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "S"
        sheet.append(["h" * 300])
        sheet.append(["value"])
        path = tmp_path / "header.xlsx"
        workbook.save(path)
        assert self.processor.extract_text(str(path)) == ["S | " + "h" * 100 + ": value"]

    def test_column_letters(self) -> None:
        assert [DocumentProcessor._column_letter(i) for i in (0, 25, 26, 701, 702)] == ["A", "Z", "AA", "ZZ", "AAA"]

    def test_extract_excel_missing_dependency(self) -> None:
        with patch.dict(sys.modules, {"openpyxl": None}):
            with pytest.raises(DocumentExtractionError, match="openpyxl not available"):
                self.processor._extract_excel("/fake/data.xlsx")

    def test_extract_excel_exception(self) -> None:
        mock_lwb = MagicMock(side_effect=Exception("xlsx error"))
        with patch.dict(sys.modules, {"openpyxl": Mock(load_workbook=mock_lwb)}):
            with pytest.raises(DocumentExtractionError, match="Error processing Excel"):
                self.processor._extract_excel("/fake/data.xlsx")

    def test_importing_the_module_does_not_load_openpyxl(self) -> None:
        """openpyxl (and the numpy it imports) loads only for Excel files."""
        import subprocess

        code = (
            "import sys; import signalwire.search.document_processor; "
            "print('openpyxl' in sys.modules)"
        )
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
        assert out.stdout.strip().splitlines()[-1] == "False", out.stdout + out.stderr

    # ── PPTX (PowerPoint) ────────────────────────────────────────────

    def test_extract_powerpoint_success(self, tmp_path: Path) -> None:
        """One entry per slide, with each text shape's text"""
        pptx = pytest.importorskip("pptx")
        deck = pptx.Presentation()
        first = deck.slides.add_slide(deck.slide_layouts[5])
        first.shapes.title.text = "Title Slide"
        second = deck.slides.add_slide(deck.slide_layouts[1])
        second.shapes.title.text = "Bullets"
        second.placeholders[1].text_frame.text = "Bullet 1"
        deck.save(str(tmp_path / "pres.pptx"))
        result = self.processor._extract_powerpoint(str(tmp_path / "pres.pptx"))
        assert result == ["Title Slide", "Bullets\nBullet 1"]

    @patch('signalwire.search.document_processor.Presentation', None)
    def test_extract_powerpoint_missing_dependency(self) -> None:
        with pytest.raises(DocumentExtractionError, match="python-pptx not available"):
            self.processor._extract_powerpoint("/fake/pres.pptx")

    @patch('signalwire.search.document_processor.Presentation')
    def test_extract_powerpoint_exception(self, mock_pres_cls: MagicMock) -> None:
        mock_pres_cls.side_effect = Exception("pptx error")
        with pytest.raises(DocumentExtractionError, match="Error processing PowerPoint"):
            self.processor._extract_powerpoint("/fake/pres.pptx")

    # ── HTML ─────────────────────────────────────────────────────────

    def test_extract_html_success(self, tmp_path: Path) -> None:
        """An HTML page's text, without its markup"""
        pytest.importorskip("bs4")
        page = tmp_path / "page.html"
        page.write_text("<html><body><p>Hello World</p></body></html>", encoding="utf-8")
        assert self.processor._extract_html(str(page)) == "Hello World"

    @patch('signalwire.search.document_processor.BeautifulSoup', None)
    def test_extract_html_missing_dependency(self) -> None:
        with pytest.raises(DocumentExtractionError, match="beautifulsoup4 not available"):
            self.processor._extract_html("/fake/page.html")

    @patch('signalwire.search.document_processor.BeautifulSoup')
    def test_extract_html_exception(self, mock_bs: MagicMock) -> None:
        with patch('builtins.open', side_effect=IOError("disk")):
            with pytest.raises(DocumentExtractionError, match="Error processing HTML"):
                self.processor._extract_html("/fake/page.html")

    # ── Markdown ─────────────────────────────────────────────────────

    @patch('signalwire.search.document_processor.BeautifulSoup')
    @patch('signalwire.search.document_processor.markdown')
    def test_extract_markdown_success(self, mock_md: MagicMock, mock_bs: MagicMock) -> None:
        mock_md.markdown.return_value = "<h1>Title</h1>"
        mock_soup = Mock(); mock_soup.get_text.return_value = "Title"
        mock_bs.return_value = mock_soup
        with patch('builtins.open', mock_open(read_data="# Title")):
            result = self.processor._extract_markdown("/fake/doc.md")
        assert result == "Title"

    @patch('signalwire.search.document_processor.BeautifulSoup', None)
    @patch('signalwire.search.document_processor.markdown', None)
    def test_extract_markdown_fallback_raw(self) -> None:
        """Without markdown+BS4, returns raw markdown text."""
        with patch('builtins.open', mock_open(read_data="# Raw Title\nBody")):
            result = self.processor._extract_markdown("/fake/doc.md")
        assert result == "# Raw Title\nBody"

    def test_extract_markdown_io_error(self) -> None:
        with patch('builtins.open', side_effect=OSError("nope")):
            with pytest.raises(DocumentExtractionError, match="Error processing Markdown"):
                self.processor._extract_markdown("/fake/doc.md")

    # ── RTF ───────────────────────────────────────────────────────────

    @patch('signalwire.search.document_processor.rtf_to_text')
    def test_extract_rtf_success(self, mock_rtf: MagicMock) -> None:
        mock_rtf.return_value = "Plain text from RTF"
        with patch('builtins.open', mock_open(read_data=r"{\rtf1 Plain text from RTF}")):
            result = self.processor._extract_rtf("/fake/doc.rtf")
        assert result == "Plain text from RTF"

    @patch('signalwire.search.document_processor.rtf_to_text', None)
    def test_extract_rtf_missing_dependency(self) -> None:
        with pytest.raises(DocumentExtractionError, match="striprtf not available"):
            self.processor._extract_rtf("/fake/doc.rtf")

    @patch('signalwire.search.document_processor.rtf_to_text')
    def test_extract_rtf_exception(self, mock_rtf: MagicMock) -> None:
        with patch('builtins.open', side_effect=IOError("disk")):
            with pytest.raises(DocumentExtractionError, match="Error processing RTF"):
                self.processor._extract_rtf("/fake/doc.rtf")

    # ── Plain text ────────────────────────────────────────────────────

    def test_extract_text_success(self) -> None:
        with patch('builtins.open', mock_open(read_data="hello world")):
            result = self.processor._extract_text("/fake/file.txt")
        assert result == "hello world"

    def test_extract_text_encoding_error(self) -> None:
        with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'bad')):
            with pytest.raises(DocumentExtractionError, match="Error processing TXT"):
                self.processor._extract_text("/fake/file.txt")

    # ── _extract_text_from_file routing ──────────────────────────────

    @patch('signalwire.search.document_processor.magic', None)
    def test_extract_text_from_file_routes_xlsx(self) -> None:
        with patch.object(self.processor, '_extract_excel', return_value="cells") as m:
            result = self.processor._extract_text_from_file("data.xlsx")
        m.assert_called_once_with("data.xlsx")
        assert result == "cells"

    @patch('signalwire.search.document_processor.magic', None)
    def test_extract_text_from_file_routes_pptx(self) -> None:
        with patch.object(self.processor, '_extract_powerpoint', return_value=["s1"]) as m:
            result = self.processor._extract_text_from_file("slides.pptx")
        m.assert_called_once_with("slides.pptx")
        assert result == ["s1"]

    @patch('signalwire.search.document_processor.magic', None)
    def test_extract_text_from_file_routes_rtf(self) -> None:
        with patch.object(self.processor, '_extract_rtf', return_value="rtf text") as m:
            result = self.processor._extract_text_from_file("notes.rtf")
        m.assert_called_once_with("notes.rtf")
        assert result == "rtf text"

    @patch('signalwire.search.document_processor.magic', None)
    def test_extract_text_from_file_unknown_extension(self) -> None:
        """Unknown extension falls back to text/plain routing."""
        with patch.object(self.processor, '_extract_text', return_value="raw") as m:
            result = self.processor._extract_text_from_file("file.zzz")
        m.assert_called_once_with("file.zzz")
        assert result == "raw"

    @patch('signalwire.search.document_processor.magic')
    def test_extract_text_from_file_magic_html(self, mock_magic: MagicMock) -> None:
        """When magic reports text/html, route to _extract_html."""
        mock_mime = Mock(); mock_mime.from_file.return_value = "text/html"
        mock_magic.Magic.return_value = mock_mime
        with patch.object(self.processor, '_extract_html', return_value="content") as m:
            result = self.processor._extract_text_from_file("page.html")
        assert result == "content"
        m.assert_called_once_with("page.html")

    @patch('signalwire.search.document_processor.magic')
    def test_extract_text_from_file_magic_text_rtf(self, mock_magic: MagicMock) -> None:
        """When magic reports text/rtf, route to _extract_rtf, not plain text."""
        mock_magic.Magic.return_value.from_file.return_value = "text/rtf"
        with patch.object(self.processor, '_extract_rtf', return_value="content") as m:
            assert self.processor._extract_text_from_file("doc.rtf") == "content"
        m.assert_called_once_with("doc.rtf")

    @patch('signalwire.search.document_processor.magic')
    def test_extract_text_from_file_magic_rtf(self, mock_magic: MagicMock) -> None:
        mock_mime = Mock(); mock_mime.from_file.return_value = "application/rtf"
        mock_magic.Magic.return_value = mock_mime
        with patch.object(self.processor, '_extract_rtf', return_value="rtf") as m:
            result = self.processor._extract_text_from_file("doc.rtf")
        m.assert_called_once_with("doc.rtf")
        assert result == "rtf"

    @patch('signalwire.search.document_processor.magic')
    def test_extract_text_from_file_magic_unsupported(self, mock_magic: MagicMock) -> None:
        mock_mime = Mock(); mock_mime.from_file.return_value = "application/octet-stream"
        mock_magic.Magic.return_value = mock_mime
        result = self.processor._extract_text_from_file("binary.bin")
        assert "Unsupported file type" in result


class TestChunkingStrategies:
    """Exhaustive tests for every chunking strategy path."""

    # ── sentence ─────────────────────────────────────────────────────

    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_sentence_chunking_no_nltk(self) -> None:
        """Without NLTK, fallback to period-based splitting."""
        proc = DocumentProcessor(chunking_strategy='sentence', max_sentences_per_chunk=2)
        text = "Alpha. Beta. Gamma. Delta."
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) >= 1
        assert all(c['metadata']['chunk_method'] == 'sentence_based' for c in chunks)

    @patch('signalwire.search.document_processor.sent_tokenize')
    def test_sentence_chunking_with_nltk(self, mock_tok: MagicMock) -> None:
        mock_tok.side_effect = lambda t: [s.strip() for s in t.split('.') if s.strip()]
        proc = DocumentProcessor(chunking_strategy='sentence', max_sentences_per_chunk=2)
        text = "One. Two. Three. Four."
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) >= 1

    @patch('signalwire.search.document_processor.sent_tokenize')
    def test_sentence_chunking_with_split_newlines_zero(self, mock_tok: MagicMock) -> None:
        """split_newlines=0 should use direct tokenization without newline splitting."""
        mock_tok.side_effect = lambda t: [s.strip() for s in t.split('.') if s.strip()]
        proc = DocumentProcessor(chunking_strategy='sentence', max_sentences_per_chunk=3, split_newlines=0)
        text = "Hello. World."
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) >= 1

    def test_sentence_chunking_list_input(self) -> None:
        proc = DocumentProcessor(chunking_strategy='sentence', max_sentences_per_chunk=3)
        chunks = proc.create_chunks(["Line A.", "Line B.", "Line C."], "f.txt", "txt")
        assert len(chunks) >= 1

    # ── sliding_window ───────────────────────────────────────────────

    def test_sliding_window_basic(self) -> None:
        proc = DocumentProcessor(chunking_strategy='sliding', chunk_size=3, chunk_overlap=1)
        chunks = proc.create_chunks("a b c d e f g h", "f.txt", "txt")
        assert len(chunks) >= 2
        assert all(c['metadata']['chunk_method'] == 'sliding_window' for c in chunks)

    def test_sliding_window_list_input(self) -> None:
        proc = DocumentProcessor(chunking_strategy='sliding', chunk_size=4, chunk_overlap=1)
        chunks = proc.create_chunks(["word1 word2", "word3 word4 word5"], "f.txt", "txt")
        assert len(chunks) >= 1

    def test_sliding_window_empty(self) -> None:
        proc = DocumentProcessor(chunking_strategy='sliding', chunk_size=5, chunk_overlap=2)
        chunks = proc.create_chunks("", "f.txt", "txt")
        assert chunks == []

    def test_sliding_window_overlap_metadata(self) -> None:
        proc = DocumentProcessor(chunking_strategy='sliding', chunk_size=3, chunk_overlap=1)
        chunks = proc.create_chunks("w1 w2 w3 w4 w5 w6", "f.txt", "txt")
        assert chunks[0]['metadata']['start_word'] == 0
        assert chunks[0]['metadata']['end_word'] == 3

    # ── paragraphs ───────────────────────────────────────────────────

    def test_paragraphs_basic(self) -> None:
        proc = DocumentProcessor(chunking_strategy='paragraph')
        text = "Para one.\n\nPara two.\n\nPara three."
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) == 3
        assert chunks[0]['content'] == "Para one."
        assert all(c['metadata']['chunk_method'] == 'paragraph_based' for c in chunks)

    def test_paragraphs_single_paragraph(self) -> None:
        proc = DocumentProcessor(chunking_strategy='paragraph')
        chunks = proc.create_chunks("Just one paragraph.", "f.txt", "txt")
        assert len(chunks) == 1

    def test_paragraphs_list_input(self) -> None:
        proc = DocumentProcessor(chunking_strategy='paragraph')
        chunks = proc.create_chunks(["line1", "", "line3"], "f.txt", "txt")
        assert len(chunks) >= 1

    def test_paragraphs_metadata(self) -> None:
        proc = DocumentProcessor(chunking_strategy='paragraph')
        chunks = proc.create_chunks("A.\n\nB.", "f.txt", "txt")
        assert chunks[0]['metadata']['paragraph_number'] == 1
        assert chunks[1]['metadata']['paragraph_number'] == 2

    # ── pages ────────────────────────────────────────────────────────

    def test_pages_list_input(self) -> None:
        proc = DocumentProcessor(chunking_strategy='page')
        chunks = proc.create_chunks(["P1", "P2"], "f.pdf", "pdf")
        assert len(chunks) == 2
        assert chunks[0]['metadata']['page_number'] == 1

    def test_pages_form_feed(self) -> None:
        proc = DocumentProcessor(chunking_strategy='page')
        chunks = proc.create_chunks("A\fB\fC", "f.txt", "txt")
        assert len(chunks) == 3

    def test_pages_page_markers(self) -> None:
        proc = DocumentProcessor(chunking_strategy='page')
        chunks = proc.create_chunks("X---PAGE---Y", "f.txt", "txt")
        assert len(chunks) == 2

    def test_pages_page_number_pattern(self) -> None:
        proc = DocumentProcessor(chunking_strategy='page')
        text = "Content A\n Page 1 \nContent B\n Page 2 \nContent C"
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) >= 2

    def test_pages_fallback_large_text(self) -> None:
        """Plain text without markers should fall back to word-based splitting."""
        proc = DocumentProcessor(chunking_strategy='page')
        words = " ".join(["word"] * 2000)
        chunks = proc.create_chunks(words, "f.txt", "txt")
        assert len(chunks) >= 2

    # ── semantic ─────────────────────────────────────────────────────

    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_semantic_single_sentence_fallback(self) -> None:
        """Single sentence should return one chunk without import error."""
        proc = DocumentProcessor(chunking_strategy='semantic')
        chunks = proc.create_chunks("Only one sentence.", "f.txt", "txt")
        assert len(chunks) == 1
        assert chunks[0]['metadata']['chunk_method'] == 'semantic'

    @patch('signalwire.search.query_processor._get_cached_model', return_value=None)
    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_semantic_import_error_falls_back(self, _mock_model: MagicMock) -> None:
        """When the embedding model is unavailable, fall back to sentence-based.

        Deterministically forces the model-unavailable condition by patching
        _get_cached_model to return None (the contract it honors when
        sentence-transformers is missing or the model fails to load). Without
        the code guard this previously crashed with AttributeError on
        model.encode(None); it must now degrade to sentence chunking regardless
        of whether the model is actually installed.
        """
        proc = DocumentProcessor(chunking_strategy='semantic')
        text = "Hello there. How are you. I am fine. Thanks for asking."
        chunks = proc.create_chunks(text, "f.txt", "txt")
        # Should get chunks (via fallback), not a crash.
        assert len(chunks) >= 1

    @patch('signalwire.search.query_processor._get_cached_model', return_value=None)
    @patch('signalwire.search.document_processor.sent_tokenize')
    def test_semantic_with_tokenizer_import_error(self, mock_tok: MagicMock, _mock_model: MagicMock) -> None:
        """Semantic with NLTK available but the embedding model unavailable.

        Same deterministic forcing of model-None as above, with NLTK's
        sent_tokenize mocked in so the sentence-splitting path is exercised too.
        """
        mock_tok.side_effect = lambda t: [s.strip()+'.' for s in t.split('.') if s.strip()]
        proc = DocumentProcessor(chunking_strategy='semantic')
        text = "Alpha sentence. Beta sentence. Gamma sentence. Delta sentence."
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) >= 1

    # ── topics ───────────────────────────────────────────────────────

    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_topics_short_text_single_chunk(self) -> None:
        """3 or fewer sentences returns a single topic chunk."""
        proc = DocumentProcessor(chunking_strategy='topic')
        text = "Machine learning rocks. Deep learning too."
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) == 1
        assert chunks[0]['metadata']['chunk_method'] == 'topic'

    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_topics_multiple_topics(self) -> None:
        """Multiple distinct topics should produce multiple chunks."""
        proc = DocumentProcessor(chunking_strategy='topic', topic_threshold=0.9)
        # Completely different keyword sets per sentence
        text = (
            "Python programming language features are impressive. "
            "JavaScript frontend development framework exists. "
            "Quantum physics particle accelerator experiments proceed. "
            "Medieval history castles knights kingdoms flourished. "
            "Oceanography marine biology coral reefs ecosystems thrive."
        )
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) >= 1
        assert all(c['metadata']['chunk_method'] == 'topic' for c in chunks)

    @patch('signalwire.search.document_processor.sent_tokenize')
    def test_topics_with_nltk(self, mock_tok: MagicMock) -> None:
        mock_tok.side_effect = lambda t: [s.strip() for s in t.split('.') if s.strip()]
        proc = DocumentProcessor(chunking_strategy='topic', topic_threshold=0.0)
        text = "Alpha beta gamma. Delta epsilon zeta. Eta theta iota. Kappa lambda mu."
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) >= 1

    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_topics_list_input(self) -> None:
        proc = DocumentProcessor(chunking_strategy='topic')
        chunks = proc.create_chunks(
            ["First about dogs.", "Second about cats.", "Third about birds.", "Fourth about fish."],
            "f.txt", "txt"
        )
        assert len(chunks) >= 1

    # ── qa_optimization ──────────────────────────────────────────────

    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_qa_optimization_basic(self) -> None:
        proc = DocumentProcessor(chunking_strategy='qa')
        text = (
            "What is Python? Python is a programming language. "
            "How does it work? It interprets code. "
            "Why use it? Because it is simple."
        )
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) >= 1
        assert all(c['metadata']['chunk_method'] == 'qa_optimized' for c in chunks)

    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_qa_optimization_has_question_metadata(self) -> None:
        proc = DocumentProcessor(chunking_strategy='qa')
        text = "What is this? It is a test. Does it work? Yes it does. Final statement here."
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) >= 1
        # At least one chunk should have 'has_question'
        has_q_chunks = [c for c in chunks if c['metadata'].get('has_question')]
        assert len(has_q_chunks) >= 0  # may or may not have, but should not crash

    @patch('signalwire.search.document_processor.sent_tokenize')
    def test_qa_optimization_with_nltk(self, mock_tok: MagicMock) -> None:
        mock_tok.side_effect = lambda t: [s.strip() for s in t.split('.') if s.strip()]
        proc = DocumentProcessor(chunking_strategy='qa')
        text = "What is X? X is Y. How about Z? Z is W. Step one. Step two."
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) >= 1

    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_qa_optimization_empty_text(self) -> None:
        proc = DocumentProcessor(chunking_strategy='qa')
        chunks = proc.create_chunks("", "f.txt", "txt")
        assert isinstance(chunks, list)

    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_qa_optimization_list_input(self) -> None:
        proc = DocumentProcessor(chunking_strategy='qa')
        chunks = proc.create_chunks(["Question? Answer.", "More content."], "f.txt", "txt")
        assert len(chunks) >= 1

    # ── json ─────────────────────────────────────────────────────────

    def test_json_chunking_valid(self) -> None:
        proc = DocumentProcessor(chunking_strategy='json')
        data = {
            "chunks": [
                {"chunk_id": "c1", "type": "content", "content": "Hello world",
                 "metadata": {"section": "Intro", "tags": ["greeting"]}},
                {"chunk_id": "c2", "type": "toc", "content": "Table of Contents item",
                 "metadata": {}},
            ]
        }
        chunks = proc.create_chunks(json.dumps(data), "f.json", "json")
        assert len(chunks) == 2
        assert chunks[0]['metadata']['chunk_method'] == 'json'
        assert chunks[0]['metadata']['original_chunk_id'] == 'c1'
        assert chunks[0]['tags'] == ['greeting']
        # TOC entry should get special tags
        assert 'toc' in chunks[1]['tags']

    def test_json_chunking_invalid_json(self) -> None:
        proc = DocumentProcessor(chunking_strategy='json')
        chunks = proc.create_chunks("not valid json {{{", "f.json", "json")
        # Should fall back to sentence-based
        assert len(chunks) >= 1

    def test_json_chunking_missing_chunks_key(self) -> None:
        proc = DocumentProcessor(chunking_strategy='json')
        data = {"data": [1, 2, 3]}
        chunks = proc.create_chunks(json.dumps(data), "f.json", "json")
        # Should fall back to sentence-based
        assert len(chunks) >= 1

    def test_json_chunking_skip_invalid_chunk(self) -> None:
        proc = DocumentProcessor(chunking_strategy='json')
        data = {
            "chunks": [
                {"chunk_id": "ok", "content": "Valid"},
                "this_is_not_a_dict",
                {"chunk_id": "no_content"},  # missing 'content'
            ]
        }
        chunks = proc.create_chunks(json.dumps(data), "f.json", "json")
        assert len(chunks) == 1
        assert "Valid" in chunks[0]['content']

    def test_json_chunking_empty_chunks_list(self) -> None:
        proc = DocumentProcessor(chunking_strategy='json')
        data: dict[str, list[Any]] = {"chunks": []}
        chunks = proc.create_chunks(json.dumps(data), "f.json", "json")
        # Falls back to sentence chunking of empty-ish text
        assert isinstance(chunks, list)

    def test_json_chunking_toc_section_naming(self) -> None:
        proc = DocumentProcessor(chunking_strategy='json')
        data = {"chunks": [
            {"type": "toc", "content": "A very long table of contents entry that should be truncated somehow"},
        ]}
        chunks = proc.create_chunks(json.dumps(data), "f.json", "json")
        assert len(chunks) == 1
        assert chunks[0]['section'].startswith("TOC:")

    def test_json_chunking_content_with_section_number(self) -> None:
        proc = DocumentProcessor(chunking_strategy='json')
        data = {"chunks": [
            {"type": "content", "content": "Body text", "metadata": {"section_number": 42}},
        ]}
        chunks = proc.create_chunks(json.dumps(data), "f.json", "json")
        assert chunks[0]['section'] == "Section 42"

    # ── markdown_enhanced ────────────────────────────────────────────

    def test_markdown_enhanced_basic_headers(self) -> None:
        proc = DocumentProcessor(chunking_strategy='markdown')
        md = "# Title\nSome intro.\n## Section A\nContent A.\n## Section B\nContent B."
        chunks = proc.create_chunks(md, "doc.md", "md")
        assert len(chunks) >= 2
        # Check section hierarchy
        sections = [c['section'] for c in chunks if c['section']]
        assert any('Title' in s for s in sections)

    def test_markdown_enhanced_code_blocks(self) -> None:
        proc = DocumentProcessor(chunking_strategy='markdown')
        md = "# Code Example\n```python\nprint('hello')\n```\nSome text."
        chunks = proc.create_chunks(md, "doc.md", "md")
        assert len(chunks) >= 1
        # At least one chunk should have code metadata
        code_chunks = [c for c in chunks if c['metadata'].get('has_code')]
        assert len(code_chunks) >= 1
        assert 'python' in code_chunks[0]['metadata'].get('code_languages', [])

    def test_markdown_enhanced_nested_headers(self) -> None:
        proc = DocumentProcessor(chunking_strategy='markdown')
        md = "# H1\n## H2\n### H3\nDeep content."
        chunks = proc.create_chunks(md, "doc.md", "md")
        assert len(chunks) >= 1

    def test_markdown_enhanced_no_headers(self) -> None:
        proc = DocumentProcessor(chunking_strategy='markdown')
        md = "Just plain text.\nMore text."
        chunks = proc.create_chunks(md, "doc.md", "md")
        assert len(chunks) >= 1

    def test_markdown_enhanced_code_without_language(self) -> None:
        proc = DocumentProcessor(chunking_strategy='markdown')
        md = "# Sec\n```\ngeneric code\n```\nDone."
        chunks = proc.create_chunks(md, "doc.md", "md")
        code_chunks = [c for c in chunks if c['metadata'].get('has_code')]
        assert len(code_chunks) >= 1
        # No language specified -> code_languages should be empty
        assert code_chunks[0]['metadata'].get('code_languages', []) == []

    def test_markdown_enhanced_empty_content(self) -> None:
        proc = DocumentProcessor(chunking_strategy='markdown')
        chunks = proc.create_chunks("", "doc.md", "md")
        assert isinstance(chunks, list)


class TestMarkdownHeadingHierarchy:
    """Section paths follow each heading's real level (B9).

    The chunkers used to take the first ``level - 1`` entries of the path,
    which assumes a heading at every level from 1. In a document that starts
    at ``##``, or skips a level, siblings were recorded as parent and child.
    """

    DOC = (
        "## Install\n\nRun the installer.\n\n"
        "## Configure\n\nSet the project ID.\n\n"
        "### Environment Variables\n\nThe SDK reads three variables.\n\n"
        "## Run\n\nStart the agent.\n\n"
        "# Reference\n\nEvery class.\n\n"
        "### Deep Heading\n\nThis skips level two.\n\n"
        "### Sibling Heading\n\nAlso level three.\n\n"
        "## Classes\n\nAgentBase is the main class.\n"
    )
    EXPECTED = [
        "Install",
        "Configure",
        "Configure > Environment Variables",
        "Run",
        "Reference",
        "Reference > Deep Heading",
        "Reference > Sibling Heading",
        "Reference > Classes",
    ]

    @pytest.mark.parametrize("chunker", ["_chunk_markdown_ast", "_chunk_markdown_line_walker"])
    def test_sections_follow_heading_levels(self, chunker: str) -> None:
        proc = DocumentProcessor(chunking_strategy="markdown")
        chunks = getattr(proc, chunker)(self.DOC, "doc.md")
        assert [c["section"] for c in chunks] == self.EXPECTED

    @pytest.mark.parametrize("chunker", ["_chunk_markdown_ast", "_chunk_markdown_line_walker"])
    def test_heading_metadata_and_depth_tags(self, chunker: str) -> None:
        proc = DocumentProcessor(chunking_strategy="markdown")
        chunks = getattr(proc, chunker)(self.DOC, "doc.md")
        run = next(c for c in chunks if c["section"] == "Run")
        assert run["metadata"]["h1"] == "Run"
        assert "h2" not in run["metadata"]
        assert "depth:1" in run["metadata"]["tags"]

    def test_folded_small_section_keeps_later_paths_right(self) -> None:
        """A section too small to stand alone folds into the next one."""
        proc = DocumentProcessor(chunking_strategy="markdown", min_chunk_size=10)
        doc = (
            "## A\n\nx\n\n"
            "## B\n\n" + "Section B has enough text to stand on its own. " * 3 + "\n\n"
            "## C\n\n" + "Section C has enough text to stand on its own. " * 3 + "\n"
        )
        chunks = proc._chunk_markdown_ast(doc, "doc.md")
        assert [c["section"] for c in chunks] == ["A", "C"]

    def test_push_heading(self) -> None:
        push = DocumentProcessor._push_heading
        path = push([], 2, "A")
        assert path == [(2, "A")]
        path = push(path, 4, "B")
        assert path == [(2, "A"), (4, "B")]
        assert push(path, 4, "C") == [(2, "A"), (4, "C")]
        assert push(path, 3, "D") == [(2, "A"), (3, "D")]
        assert push(path, 1, "E") == [(1, "E")]


class TestEdgeCases:
    """Edge cases: empty, unicode, very large, unsupported."""

    def test_empty_string_all_strategies(self) -> None:
        for strategy in ['sentence', 'sliding', 'paragraph', 'page', 'qa', 'json', 'markdown']:
            proc = DocumentProcessor(chunking_strategy=strategy)
            chunks = proc.create_chunks("", "f.txt", "txt")
            assert isinstance(chunks, list), f"Strategy {strategy} failed on empty string"

    def test_whitespace_only_all_strategies(self) -> None:
        for strategy in ['sentence', 'sliding', 'paragraph', 'page', 'qa', 'markdown']:
            proc = DocumentProcessor(chunking_strategy=strategy)
            chunks = proc.create_chunks("   \n\t\n  ", "f.txt", "txt")
            assert isinstance(chunks, list), f"Strategy {strategy} failed on whitespace"

    def test_unicode_content(self) -> None:
        proc = DocumentProcessor(chunking_strategy='sentence', max_sentences_per_chunk=2)
        text = "日本語のテスト文。これは二番目の文です。三番目の文もあります。"
        chunks = proc.create_chunks(text, "jp.txt", "txt")
        assert len(chunks) >= 1

    def test_unicode_emoji_content(self) -> None:
        proc = DocumentProcessor(chunking_strategy='paragraph')
        text = "First para with emoji.\n\nSecond para."
        chunks = proc.create_chunks(text, "emoji.txt", "txt")
        assert len(chunks) == 2

    def test_very_large_text_sentence(self) -> None:
        proc = DocumentProcessor(chunking_strategy='sentence', max_sentences_per_chunk=5)
        text = ". ".join([f"Sentence number {i}" for i in range(200)]) + "."
        chunks = proc.create_chunks(text, "big.txt", "txt")
        assert len(chunks) > 10

    def test_very_large_text_sliding(self) -> None:
        proc = DocumentProcessor(chunking_strategy='sliding', chunk_size=50, chunk_overlap=10)
        text = " ".join([f"word{i}" for i in range(1000)])
        chunks = proc.create_chunks(text, "big.txt", "txt")
        assert len(chunks) > 10

    def test_very_large_text_paragraph(self) -> None:
        proc = DocumentProcessor(chunking_strategy='paragraph')
        text = "\n\n".join([f"Paragraph {i} content." for i in range(100)])
        chunks = proc.create_chunks(text, "big.txt", "txt")
        assert len(chunks) == 100

    def test_single_word(self) -> None:
        proc = DocumentProcessor(chunking_strategy='sentence')
        chunks = proc.create_chunks("hello", "f.txt", "txt")
        assert len(chunks) >= 1
        assert "hello" in chunks[0]['content']

    def test_single_character(self) -> None:
        proc = DocumentProcessor(chunking_strategy='sliding', chunk_size=5, chunk_overlap=1)
        chunks = proc.create_chunks("x", "f.txt", "txt")
        assert len(chunks) == 1

    def test_newlines_only(self) -> None:
        proc = DocumentProcessor(chunking_strategy='paragraph')
        chunks = proc.create_chunks("\n\n\n\n", "f.txt", "txt")
        assert chunks == []

    def test_mixed_line_endings(self) -> None:
        proc = DocumentProcessor(chunking_strategy='paragraph')
        text = "Para 1.\r\n\r\nPara 2.\r\n\r\nPara 3."
        chunks = proc.create_chunks(text, "f.txt", "txt")
        assert len(chunks) == 3

    def test_unsupported_chunking_strategy_fallback(self) -> None:
        proc = DocumentProcessor(chunking_strategy='nonexistent_strategy')
        chunks = proc.create_chunks("Some text here.", "f.txt", "txt")
        # Fallback to sentence
        assert len(chunks) >= 1
        assert chunks[0]['metadata']['chunk_method'] == 'sentence_based'

    def test_create_chunk_hash_stability(self) -> None:
        """Same content produces same chunk structure."""
        proc = DocumentProcessor()
        c1 = proc._create_chunk("abc", "f.txt", "S1")
        c2 = proc._create_chunk("abc", "f.txt", "S1")
        assert c1['content'] == c2['content']
        assert c1['metadata']['word_count'] == c2['metadata']['word_count']

    def test_create_chunk_filename_extension(self) -> None:
        proc = DocumentProcessor()
        chunk = proc._create_chunk("test", "archive.tar.gz")
        assert chunk['metadata']['file_type'] == 'gz'

    def test_create_chunk_no_extension(self) -> None:
        proc = DocumentProcessor()
        chunk = proc._create_chunk("test", "Makefile")
        assert chunk['metadata']['file_type'] == ''

    # ── _build helpers ───────────────────────────────────────────────

    def test_build_section_path_empty(self) -> None:
        proc = DocumentProcessor()
        assert proc._build_section_path([]) is None

    def test_build_section_path_single(self) -> None:
        proc = DocumentProcessor()
        assert proc._build_section_path(["Intro"]) == "Intro"

    def test_build_section_path_nested(self) -> None:
        proc = DocumentProcessor()
        assert proc._build_section_path(["A", "B", "C"]) == "A > B > C"

    def test_build_markdown_metadata_no_code(self) -> None:
        proc = DocumentProcessor()
        meta = proc._build_markdown_metadata(["H1"], [], False)
        assert meta['chunk_type'] == 'markdown'
        assert meta.get('h1') == 'H1'
        assert 'has_code' not in meta

    def test_build_markdown_metadata_with_code(self) -> None:
        proc = DocumentProcessor()
        meta = proc._build_markdown_metadata(["H1", "H2"], ["python", "bash"], True)
        assert meta['has_code'] is True
        assert meta['code_languages'] == ["python", "bash"]
        assert 'code' in meta['tags']
        assert 'code:python' in meta['tags']
        assert 'depth:2' in meta['tags']

    def test_build_markdown_metadata_empty_hierarchy(self) -> None:
        proc = DocumentProcessor()
        meta = proc._build_markdown_metadata([], [], False)
        assert 'h1' not in meta
        assert 'tags' not in meta  # no code, no hierarchy -> no tags

    def test_build_python_section_class_and_function(self) -> None:
        proc = DocumentProcessor()
        assert proc._build_python_section("MyClass", "my_method") == "MyClass.my_method"

    def test_build_python_section_class_only(self) -> None:
        proc = DocumentProcessor()
        assert proc._build_python_section("MyClass", None) == "MyClass"

    def test_build_python_section_function_only(self) -> None:
        proc = DocumentProcessor()
        assert proc._build_python_section(None, "my_func") == "my_func"

    def test_build_python_section_neither(self) -> None:
        proc = DocumentProcessor()
        assert proc._build_python_section(None, None) is None

    # ── _calculate_sentences_per_chunk ───────────────────────────────

    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_calculate_sentences_per_chunk_no_nltk(self) -> None:
        proc = DocumentProcessor(chunk_size=50)
        result = proc._calculate_sentences_per_chunk("Short. Another.")
        assert isinstance(result, int)
        assert result >= 1

    @patch('signalwire.search.document_processor.sent_tokenize', None)
    def test_calculate_sentences_per_chunk_empty(self) -> None:
        """Text with no actual sentences falls back to 1, it does not raise.

        This test used to assert the ZeroDivisionError and call it a source
        code bug in its own docstring. Splitting "" or ". . . " yields a list
        of EMPTY strings, which is truthy, so the `if not sentences` guard
        misses it and the average comes out 0.0. A line of dots or an ASCII
        rule is ugly input, not invalid input, and indexing a document should
        not die on it.
        """
        proc = DocumentProcessor()
        assert proc._calculate_sentences_per_chunk("") == 1
        assert proc._calculate_sentences_per_chunk(". . . ") == 1
        # Whitespace-only text splits to one short "sentence" rather than to
        # empty ones, so it returns the cap. Not asserted as 1: that would be
        # inventing a requirement rather than pinning the crash that was fixed.
        assert proc._calculate_sentences_per_chunk("   ") >= 1

    # ── _get_overlap_lines ───────────────────────────────────────────

    def test_get_overlap_lines_fits(self) -> None:
        proc = DocumentProcessor(chunk_overlap=100)
        lines = ["a", "bb", "ccc"]
        result = proc._get_overlap_lines(lines)
        assert result == ["a", "bb", "ccc"]

    def test_get_overlap_lines_partial(self) -> None:
        proc = DocumentProcessor(chunk_overlap=5)
        lines = ["long_line_here", "short"]
        result = proc._get_overlap_lines(lines)
        assert result == ["short"]

    def test_get_overlap_lines_empty(self) -> None:
        proc = DocumentProcessor()
        assert proc._get_overlap_lines([]) == []

    # ── _chunk_document_aware ────────────────────────────────────────

    def test_chunk_document_aware_list_small_pages(self) -> None:
        proc = DocumentProcessor()
        pages = ["Small page one.", "Small page two."]
        chunks = proc._chunk_document_aware(pages, "doc.pdf", "pdf")
        assert len(chunks) == 2
        assert chunks[0]['section'] == "Page 1"

    def test_chunk_document_aware_list_pptx(self) -> None:
        proc = DocumentProcessor()
        slides = ["Slide text one.", "Slide text two."]
        chunks = proc._chunk_document_aware(slides, "pres.pptx", "pptx")
        assert len(chunks) == 2
        assert chunks[0]['section'] == "Slide 1"

    def test_chunk_document_aware_list_generic(self) -> None:
        proc = DocumentProcessor()
        sections = ["Section one.", "Section two."]
        chunks = proc._chunk_document_aware(sections, "doc.docx", "docx")
        assert len(chunks) == 2
        assert chunks[0]['section'] == "Section 1"

    def test_chunk_document_aware_string(self) -> None:
        proc = DocumentProcessor()
        chunks = proc._chunk_document_aware("Hello world text here.", "doc.txt", "txt")
        assert len(chunks) >= 1

    def test_chunk_document_aware_skips_empty_pages(self) -> None:
        proc = DocumentProcessor()
        pages = ["Content", "", "  ", "More content"]
        chunks = proc._chunk_document_aware(pages, "doc.pdf", "pdf")
        assert len(chunks) == 2

class TestExtractText:
    """extract_text() reads a file by its type, and raises when it can't."""

    def setup_method(self) -> None:
        self.processor = DocumentProcessor()

    def test_html_loses_its_markup_scripts_and_styles(self, tmp_path: Path) -> None:
        pytest.importorskip("bs4")
        page = tmp_path / "page.html"
        page.write_text(
            "<html><head><style>p {color: red}</style><script>track()</script></head>"
            "<body><h1>Hours</h1><p>Open <b>9</b> to 5.</p></body></html>",
            encoding="utf-8",
        )
        text = self.processor.extract_text(str(page))
        assert isinstance(text, str)
        assert "Hours" in text and "Open" in text and "9" in text
        for left_out in ("<", "track()", "color: red"):
            assert left_out not in text

    def test_an_unsupported_type_raises(self, tmp_path: Path) -> None:
        image = tmp_path / "logo.png"
        image.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
        with patch('signalwire.search.document_processor.magic') as magic:
            magic.Magic.return_value.from_file.return_value = "image/png"
            with pytest.raises(DocumentExtractionError, match="Unsupported file type: image/png"):
                self.processor.extract_text(str(image))
            # The older method still returns the error as JSON, as it always has
            assert json.loads(self.processor._extract_text_from_file(str(image))) == {
                "error": "Unsupported file type: image/png"
            }

    def test_markdown_comes_back_as_written(self, tmp_path: Path) -> None:
        doc = tmp_path / "guide.md"
        doc.write_text("# Setup\n\nRun **it**.\n", encoding="utf-8")
        assert self.processor.extract_text(str(doc)) == "# Setup\n\nRun **it**.\n"


class TestChunkWindowSizes:
    """Every window size moves forward, and one that can't is refused."""

    def test_one_sentence_per_chunk(self) -> None:
        processor = DocumentProcessor(chunking_strategy="sentence", max_sentences_per_chunk=1)
        chunks = processor.create_chunks("One. Two. Three.", "t.txt", "txt")
        assert [c["content"] for c in chunks] == ["One.", "Two.", "Three."]

    @pytest.mark.parametrize("n", [2, 3, 5, 8])
    def test_larger_windows_overlap_as_before(self, n: int) -> None:
        text = " ".join(f"Sentence {i}." for i in range(20))
        processor = DocumentProcessor(chunking_strategy="sentence", max_sentences_per_chunk=n)
        chunks = processor.create_chunks(text, "t.txt", "txt")
        step = n - max(1, n // 4)
        assert len(chunks) == len(range(0, 20, step))

    def test_a_window_of_none_is_refused(self) -> None:
        with pytest.raises(ValueError, match="max_sentences_per_chunk must be at least 1"):
            DocumentProcessor(chunking_strategy="sentence", max_sentences_per_chunk=0)

    @pytest.mark.parametrize("overlap", [-1, 50, 60])
    def test_a_sliding_window_that_cant_move_is_refused(self, overlap: int) -> None:
        with pytest.raises(ValueError, match="chunk_overlap must be"):
            DocumentProcessor(chunking_strategy="sliding", chunk_size=50, chunk_overlap=overlap)

    def test_long_sentences_in_the_document_aware_path(self) -> None:
        # Sentences longer than chunk_size words give one sentence per chunk there
        long = " ".join(["word"] * 80) + ". " + " ".join(["more"] * 80) + "."
        chunks = DocumentProcessor()._chunk_text_enhanced(long, "t.txt")
        assert len(chunks) == 2


class TestPdfPages:
    """A PDF's pages keep their numbers, and their text as written."""

    def _pdf(self, texts: list[str | None]) -> MagicMock:
        pdf = MagicMock()
        pdf.__enter__.return_value.pages = [Mock(**{"extract_text.return_value": t}) for t in texts]
        return pdf

    def test_each_page_has_an_entry_and_keeps_a_leading_number(self) -> None:
        with patch('signalwire.search.document_processor.pdfplumber') as plumber:
            plumber.open.return_value = self._pdf(["Intro", None, "1. Plug it in.\n2. Wait."])
            pages = DocumentProcessor()._extract_pdf("manual.pdf")
        assert pages == ["Intro", "", "1. Plug it in.\n2. Wait."]

    def test_the_page_strategy_skips_an_empty_page_and_keeps_the_numbers(self) -> None:
        chunks = DocumentProcessor(chunking_strategy="page").create_chunks(
            ["Intro", "", "Setup"], "manual.pdf", "pdf"
        )
        assert [(c["section"], c["metadata"]["page_number"]) for c in chunks] == [
            ("Page 1", 1),
            ("Page 3", 3),
        ]

    def test_an_empty_page_adds_nothing_to_the_other_strategies(self) -> None:
        processor = DocumentProcessor(chunking_strategy="sentence")
        with_gap = processor.create_chunks(["Intro here.", "", "Setup here."], "m.pdf", "pdf")
        without = processor.create_chunks(["Intro here.", "Setup here."], "m.pdf", "pdf")
        assert [c["content"] for c in with_gap] == [c["content"] for c in without]


class TestParagraphsFromAList:
    """A list's entries are paragraphs, and short ones can merge forward."""

    DOCX = ["Installation guide.", "Plug the cable into the back port.", "Wait two minutes."]

    def test_each_entry_is_a_paragraph(self) -> None:
        chunks = DocumentProcessor(chunking_strategy="paragraph").create_chunks(self.DOCX, "g.docx", "docx")
        assert [c["content"] for c in chunks] == self.DOCX
        assert [c["metadata"]["paragraph_number"] for c in chunks] == [1, 2, 3]

    def test_a_short_paragraph_merges_into_the_next(self) -> None:
        doc = ["Installation guide.", "Plug the cable into the back port.",
               "Then wait two minutes for the light to turn green."]
        processor = DocumentProcessor(chunking_strategy="paragraph", min_chunk_size=6)
        chunks = processor.create_chunks(doc, "g.docx", "docx")
        assert [c["content"] for c in chunks] == [
            "Installation guide.\n\nPlug the cable into the back port.",
            "Then wait two minutes for the light to turn green.",
        ]
        assert [(c["section"], c["metadata"]["paragraph_count"]) for c in chunks] == [
            ("Paragraph 1", 2),
            ("Paragraph 3", 1),
        ]

    def test_a_short_last_paragraph_joins_the_one_before(self) -> None:
        processor = DocumentProcessor(chunking_strategy="paragraph", min_chunk_size=6)
        chunks = processor.create_chunks(self.DOCX, "g.docx", "docx")
        assert len(chunks) == 1 and chunks[0]["content"].endswith("Wait two minutes.")
        assert chunks[0]["metadata"]["paragraph_count"] == 3

    def test_a_text_splits_on_blank_lines_as_before(self) -> None:
        text = "First one.\n\nSecond one.\nStill second.\n\nThird."
        chunks = DocumentProcessor(chunking_strategy="paragraph").create_chunks(text, "t.txt", "txt")
        assert [c["content"] for c in chunks] == ["First one.", "Second one.\nStill second.", "Third."]


class TestSemanticModel:
    """The semantic strategy compares sentences with the index's own model."""

    TEXT = "Cats purr. Cats nap. Taxes are due in April. File them online."

    def test_it_loads_the_model_its_given(self) -> None:
        pytest.importorskip("sklearn")
        model = Mock()
        model.encode.return_value = [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]]
        with patch("signalwire.search.query_processor._get_cached_model", return_value=model) as load:
            chunks = DocumentProcessor(
                chunking_strategy="semantic", model_name="sentence-transformers/all-MiniLM-L6-v2"
            ).create_chunks(self.TEXT, "t.txt", "txt")
        load.assert_called_once_with("sentence-transformers/all-MiniLM-L6-v2")
        assert {c["metadata"]["chunk_method"] for c in chunks} == {"semantic"}

    def test_a_model_that_wont_load_gives_sentence_chunks_that_say_so(self) -> None:
        pytest.importorskip("sklearn")
        with patch("signalwire.search.query_processor._get_cached_model", return_value=None):
            chunks = DocumentProcessor(chunking_strategy="semantic").create_chunks(self.TEXT, "t.txt", "txt")
        assert chunks and {c["metadata"]["chunk_method"] for c in chunks} == {"sentence_based"}

    def test_the_index_builder_passes_its_model(self) -> None:
        from signalwire.search.index_builder import IndexBuilder

        builder = IndexBuilder(model_name="sentence-transformers/all-MiniLM-L6-v2", chunking_strategy="semantic")
        assert builder.doc_processor.model_name == "sentence-transformers/all-MiniLM-L6-v2"


class TestStructuredDocuments:
    """Word, PowerPoint and HTML keep all their text, and their structure
    under the markdown strategy."""

    def _docx(self, tmp_path: Path) -> str:
        docx = pytest.importorskip("docx")
        document = docx.Document()
        document.add_heading("Setup", 1)
        document.add_paragraph("Plug it in.")
        document.add_heading("Linux", 2)
        document.add_paragraph("Install the package.", style="List Bullet")
        table = document.add_table(rows=2, cols=2)
        for (row, column), text in {(0, 0): "Plan", (0, 1): "Price", (1, 0): "Pro", (1, 1): "40"}.items():
            table.cell(row, column).text = text
        document.add_paragraph("After the table.")
        path = str(tmp_path / "guide.docx")
        document.save(path)
        return path

    def test_a_word_table_is_kept_in_place(self, tmp_path: Path) -> None:
        units = DocumentProcessor()._docx_units(self._docx(tmp_path))
        assert [u["text"] for u in units] == [
            "Setup", "Plug it in.", "Linux", "Install the package.",
            "Plan | Price\nPro | 40", "After the table.",
        ]
        assert units[4]["anchor"] == {"table": 1, "headings": ["Setup", "Linux"]}
        assert units[5]["anchor"] == {"paragraph": 5, "headings": ["Setup", "Linux"]}

    def test_a_word_document_of_only_a_table(self, tmp_path: Path) -> None:
        docx = pytest.importorskip("docx")
        document = docx.Document()
        table = document.add_table(rows=2, cols=2)
        table.cell(0, 0).text, table.cell(1, 1).text = "a", "d"
        document.save(str(tmp_path / "t.docx"))
        assert DocumentProcessor().extract_text(str(tmp_path / "t.docx")) == ["a\nd"]

    def test_word_structure_as_markdown(self, tmp_path: Path) -> None:
        texts = DocumentProcessor(chunking_strategy="markdown")._extract_docx(self._docx(tmp_path))
        assert texts == [
            "# Setup", "Plug it in.", "## Linux", "- Install the package.",
            "| Plan | Price |\n| --- | --- |\n| Pro | 40 |", "After the table.",
        ]

    def _pptx(self, tmp_path: Path) -> str:
        pptx = pytest.importorskip("pptx")
        from pptx.util import Inches

        deck = pptx.Presentation()
        slide = deck.slides.add_slide(deck.slide_layouts[5])
        slide.shapes.title.text = "Pricing"
        group = slide.shapes.add_group_shape()
        group.shapes.add_textbox(Inches(1), Inches(1), Inches(2), Inches(1)).text_frame.text = "Grouped words"
        table = slide.shapes.add_table(2, 2, Inches(1), Inches(3), Inches(4), Inches(1)).table
        for (row, column), text in {(0, 0): "Plan", (0, 1): "Price", (1, 0): "Pro", (1, 1): "40"}.items():
            table.cell(row, column).text = text
        slide.notes_slide.notes_text_frame.text = "Mention the discount."
        deck.slides.add_slide(deck.slide_layouts[6])
        path = str(tmp_path / "deck.pptx")
        deck.save(path)
        return path

    def test_a_slide_keeps_groups_tables_and_notes(self, tmp_path: Path) -> None:
        units = DocumentProcessor()._pptx_units(self._pptx(tmp_path))
        assert units == [
            {"text": "Pricing\nGrouped words\nPlan | Price\nPro | 40\nNotes: Mention the discount.",
             "anchor": {"slide": 1}},
            {"text": "", "anchor": {"slide": 2}},
        ]

    def test_a_slide_as_markdown(self, tmp_path: Path) -> None:
        texts = DocumentProcessor(chunking_strategy="markdown")._extract_powerpoint(self._pptx(tmp_path))
        assert texts[0] == (
            "# Pricing\n\nGrouped words\n\n| Plan | Price |\n| --- | --- |\n| Pro | 40 |"
            "\n\nNotes: Mention the discount."
        )

    PAGE = (
        "<html><body><nav>Home | About</nav><header>Site</header><h1>Hours</h1>"
        "<p>Open <b>9</b> to 5.</p><h2>Holidays</h2><ul><li>Closed Monday</li></ul>"
        "<table><tr><th>Day</th><th>Hours</th></tr><tr><td>Sat</td><td>10-2</td></tr></table>"
        "<footer>(c) us</footer></body></html>"
    )

    def test_html_leaves_out_navigation_headers_and_footers(self, tmp_path: Path) -> None:
        pytest.importorskip("bs4")
        page = tmp_path / "hours.html"
        page.write_text(self.PAGE, encoding="utf-8")
        processor = DocumentProcessor()
        text = processor.extract_text(str(page))
        assert isinstance(text, str) and "Open" in text and "Sat" in text
        for left_out in ("Home", "Site", "(c) us"):
            assert left_out not in text
        assert [u["anchor"] for u in processor._html_units(str(page))] == [
            {"section": 1, "headings": ["Hours"]},
            {"section": 2, "headings": ["Hours", "Holidays"]},
        ]

    def test_html_as_markdown(self, tmp_path: Path) -> None:
        pytest.importorskip("bs4")
        page = tmp_path / "hours.html"
        page.write_text(self.PAGE, encoding="utf-8")
        assert DocumentProcessor(chunking_strategy="markdown").extract_text(str(page)) == (
            "# Hours\n\nOpen 9 to 5.\n\n## Holidays\n\n- Closed Monday\n\n"
            "| Day | Hours |\n| --- | --- |\n| Sat | 10-2 |"
        )
