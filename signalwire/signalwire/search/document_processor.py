"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import re
import bisect
import datetime
import json
from typing import Any, TYPE_CHECKING, cast
from pathlib import Path

# Document processing imports
if TYPE_CHECKING:
    import pdfplumber
else:
    try:
        import pdfplumber
    except ImportError:
        pdfplumber = None

if TYPE_CHECKING:
    from docx import Document as DocxDocument
else:
    try:
        from docx import Document as DocxDocument
    except ImportError:
        DocxDocument = None

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
else:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        BeautifulSoup = None

if TYPE_CHECKING:
    import markdown
else:
    try:
        import markdown
    except ImportError:
        markdown = None

if TYPE_CHECKING:
    from markdown_it import MarkdownIt
else:
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        MarkdownIt = None

if TYPE_CHECKING:
    from striprtf.striprtf import rtf_to_text
else:
    try:
        from striprtf.striprtf import rtf_to_text
    except ImportError:
        rtf_to_text = None

if TYPE_CHECKING:
    from pptx import Presentation
else:
    try:
        from pptx import Presentation
    except ImportError:
        Presentation = None


if TYPE_CHECKING:
    from nltk.tokenize import sent_tokenize
    import nltk
else:
    try:
        import nltk
        import nltk.tokenize

        sent_tokenize = None  # _punkt_sentences, once it's defined below
    except ImportError:
        sent_tokenize = None
        nltk = None

if TYPE_CHECKING:
    import magic
else:
    try:
        import magic
    except ImportError:
        magic = None

from signalwire.core.logging_config import get_logger
from signalwire.search.models import document_key

logger = get_logger(__name__)


def _punkt_sentences(text: str) -> list[str]:
    """NLTK's sentences, or, without its punkt_tab data, a split after each
    sentence's closing punctuation. Search never downloads the data."""
    from nltk.tokenize import sent_tokenize as nltk_sent_tokenize

    try:
        return cast("list[str]", nltk_sent_tokenize(text))
    except LookupError:
        from signalwire.search.nltk_data import note_missing

        note_missing("punkt_tab")
        return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


if not TYPE_CHECKING and nltk is not None:
    sent_tokenize = _punkt_sentences

# Namespaces of a workbook's XML parts.
_XLSX_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_CELL_REFERENCE = re.compile(r"\$?([A-Za-z]{1,3})\$?(\d+)")

# A merged range's value is repeated into each of its cells, so every row keeps
# it. These limits stop a small file with huge merged ranges from producing an
# enormous text: the cells a workbook's merges may visit while filling in, and
# the characters of repeated text they may add.
_MERGE_FILL_CELLS = 100_000
_MERGE_FILL_CHARACTERS = 1_000_000

# A header longer than this is cut to it as the label of each cell under it,
# since every labelled cell repeats its header.
_HEADER_LABEL_LIMIT = 100


class _MergeBudget:
    """What a workbook's merged ranges may still add."""

    def __init__(self) -> None:
        self.cells = _MERGE_FILL_CELLS
        self.characters = _MERGE_FILL_CHARACTERS

    @property
    def spent(self) -> bool:
        """Whether a limit was reached, so some merged cells stayed empty."""
        return self.cells <= 0 or self.characters < 0


class _Repeated:
    """A merged range's value, repeated into one of the range's other cells."""

    __slots__ = ("text",)

    def __init__(self, text: str) -> None:
        self.text = text


def _column_number(letters: str) -> int:
    """A column's number from its letters, counting from 1: A is 1, AA is 27."""
    number = 0
    for letter in letters.upper():
        number = number * 26 + ord(letter) - ord("A") + 1
    return number


def _range_bounds(reference: str) -> tuple[int, int, int, int] | None:
    """A range such as "A2:B3" as (first row, first column, last row, last
    column), counting from 1; None for anything else."""
    corners = [_CELL_REFERENCE.fullmatch(part) for part in reference.split(":")]
    if len(corners) != 2 or not all(corners):
        return None
    rows = [int(corner.group(2)) for corner in corners if corner]
    columns = [_column_number(corner.group(1)) for corner in corners if corner]
    return min(rows), min(columns), max(rows), max(columns)


_HTML_HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
# Elements whose text is a paragraph of its own in Markdown
_HTML_BLOCKS = {
    "p", "div", "li", "td", "th", "pre", "blockquote", "section", "article",
    "main", "aside", "figure", "figcaption", "dd", "dt", "address", "body",
    "ul", "ol", "dl", "table", "tr", "thead", "tbody", "tfoot", "form",
}  # fmt: skip


def _table_text(rows: list[list[str]], as_markdown: bool) -> str:
    """A table's rows: a Markdown table (its first row the header), or a line
    per row with its cells separated by " | "."""
    if not as_markdown:
        return "\n".join(" | ".join(cell for cell in row if cell) for row in rows)
    width = max(len(row) for row in rows)
    cells = [
        [cell.replace("|", "\\|") for cell in row] + [""] * (width - len(row))
        for row in rows
    ]
    lines = ["| " + " | ".join(cells[0]) + " |", "|" + " --- |" * width]
    lines.extend("| " + " | ".join(row) + " |" for row in cells[1:])
    return "\n".join(lines)


def _docx_heading_level(paragraph: Any) -> int:
    """A paragraph's heading level from its style (Title and Heading 1 are 1),
    or 0 for a paragraph that isn't a heading."""
    style = getattr(paragraph, "style", None)
    name = getattr(style, "name", "") or ""
    if name == "Title":
        return 1
    match = re.fullmatch(r"Heading ([1-9])", name)
    return int(match.group(1)) if match else 0


def _docx_markdown(paragraph: Any, text: str, level: int) -> str:
    """A Word paragraph as Markdown: a heading, a list item, or as written."""
    if level:
        return "#" * min(level, 6) + " " + " ".join(text.split())
    name = getattr(getattr(paragraph, "style", None), "name", "") or ""
    properties = getattr(paragraph._p, "pPr", None)
    numbered = properties is not None and getattr(properties, "numPr", None) is not None
    if name.startswith("List Number"):
        return "1. " + text.strip()
    if name.startswith("List") or numbered:
        return "- " + text.strip()
    return text


def _docx_table_rows(table: Any) -> list[list[str]]:
    """A Word table's rows of cell text; a merged cell counts once, and an
    empty row is left out."""
    rows = []
    for row in table.rows:
        cells: list[str] = []
        previous = None
        for cell in row.cells:
            if cell._tc is previous:  # a merged cell repeats across its span
                continue
            previous = cell._tc
            cells.append(" ".join(cell.text.split()))
        if any(cells):
            rows.append(cells)
    return rows


def _pptx_shape_texts(shape: Any, as_markdown: bool) -> list[str]:
    """A slide shape's texts: a group's shapes in turn, a table's rows, or the
    shape's own text."""
    if hasattr(shape, "shapes"):  # a group
        texts: list[str] = []
        for inner in shape.shapes:
            texts.extend(_pptx_shape_texts(inner, as_markdown))
        return texts
    if getattr(shape, "has_table", False):
        rows = []
        for row in shape.table.rows:
            cells = [" ".join(cell.text.split()) for cell in row.cells]
            if any(cells):
                rows.append(cells)
        return [_table_text(rows, as_markdown)] if rows else []
    if hasattr(shape, "text"):
        return [shape.text]
    return []


def _html_text_sections(soup: Any) -> list[tuple[list[str], list[str]]]:
    """An HTML page's strings, as get_text() gives them, in sections that
    start at each heading: (heading path, strings) pairs."""
    from bs4.element import CData, NavigableString, Tag

    sections: list[tuple[list[str], list[str]]] = [([], [])]
    headings: list[str] = []
    for node in soup.descendants:
        if isinstance(node, Tag) and node.name in _HTML_HEADINGS:
            level = int(node.name[1])
            headings = [*headings[: level - 1], " ".join(node.get_text(" ").split())]
            sections.append((list(headings), []))
        elif type(node) in (NavigableString, CData):
            sections[-1][1].append(str(node))
    return sections


def _html_markdown_sections(soup: Any) -> list[tuple[list[str], list[str]]]:
    """An HTML page as Markdown blocks, in sections that start at each
    heading: (heading path, blocks) pairs."""
    from bs4.element import NavigableString, Tag

    sections: list[tuple[list[str], list[str]]] = [([], [])]
    headings: list[str] = []

    def words(node: Any) -> str:
        return " ".join(node.get_text(" ").split())

    def walk(node: Any) -> None:
        inline: list[str] = []

        def flush() -> None:
            text = " ".join(" ".join(inline).split())
            if text:
                sections[-1][1].append(text)
            inline.clear()

        for child in node.children:
            if isinstance(child, Tag):
                name = child.name
                if name in _HTML_HEADINGS:
                    flush()
                    nonlocal headings
                    level = int(name[1])
                    headings = [*headings[: level - 1], words(child)]
                    sections.append(
                        (list(headings), ["#" * level + " " + words(child)])
                    )
                elif name == "table":
                    flush()
                    rows = [
                        [words(cell) for cell in row.find_all(["th", "td"])]
                        for row in child.find_all("tr")
                    ]
                    rows = [row for row in rows if any(row)]
                    if rows:
                        sections[-1][1].append(_table_text(rows, True))
                elif name == "li":
                    flush()
                    marker = (
                        "1."
                        if child.parent is not None and child.parent.name == "ol"
                        else "-"
                    )
                    if words(child):
                        sections[-1][1].append(f"{marker} {words(child)}")
                elif name in _HTML_BLOCKS or child.find(
                    list(_HTML_BLOCKS | _HTML_HEADINGS)
                ):
                    flush()
                    walk(child)
                else:
                    inline.append(child.get_text(" "))
            elif type(child) is NavigableString:
                inline.append(str(child))
        flush()

    walk(soup)
    return sections


class DocumentExtractionError(ValueError):
    """A file's text couldn't be extracted: its type isn't supported, the
    library its type needs isn't installed, or reading it failed."""


class ChunkFormatError(ValueError):
    """The ``json`` chunking strategy's input isn't the JSON chunk format: an
    object whose ``chunks`` is a list of objects, each with a string
    ``content``, where any ``metadata`` is an object, any ``section`` a string
    and any ``tags`` a list of strings."""


# A JSON value's text in a unit: scalars as JSON writes them, strings as they are.
def _json_scalar(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, bool):
        return "true" if value else "false"
    return json.dumps(value)


# A key path is cut to this many characters, from the front, as a line's
# label: every value under a key repeats its path.
_JSON_LABEL_LIMIT = 200


def _json_label(label: str) -> str:
    """A key path as a line's label, cut from the front past the limit, so the
    keys nearest the value stay."""
    if len(label) <= _JSON_LABEL_LIMIT:
        return label
    return "\u2026" + label[-(_JSON_LABEL_LIMIT - 1) :]


class _TextBudget:
    """The text a JSON document's lines may still add. Each value repeats its
    key path, so a small file of many values under long keys could otherwise
    make an enormous text."""

    def __init__(self, characters: int) -> None:
        self.characters = characters

    def add(self, source_characters: int) -> None:
        """Allow four times this much source text more."""
        self.characters += 4 * source_characters

    def spend(self, text: str) -> None:
        self.characters -= len(text)
        if self.characters < 0:
            raise DocumentExtractionError(
                "Error processing JSON: its key paths repeat more text than the limit allows"
            )


def _json_lines(value: Any, label: str, lines: list[str], budget: _TextBudget) -> None:
    """A JSON value as "key.path: value" lines, below the path ``label``.
    An array of scalars is one line; nulls and empty strings are left out."""
    if isinstance(value, dict):
        for key, item in value.items():
            _json_lines(
                item,
                _json_label(f"{label}.{key}" if label else str(key)),
                lines,
                budget,
            )
    elif isinstance(value, list):
        if all(not isinstance(item, (dict, list)) for item in value):
            texts = [
                _json_scalar(item) for item in value if item is not None and item != ""
            ]
            if texts:
                line = f"{label}: {', '.join(texts)}" if label else ", ".join(texts)
                budget.spend(line)
                lines.append(line)
        else:
            for index, item in enumerate(value):
                _json_lines(item, _json_label(f"{label}[{index}]"), lines, budget)
    elif value is not None and value != "":
        line = f"{label}: {_json_scalar(value)}" if label else _json_scalar(value)
        budget.spend(line)
        lines.append(line)


# What a JSON document's lines may add beyond four times its own text.
_JSON_TEXT_ALLOWANCE = 1_000_000

# The json strategy gives a subsection the heading above it, cut to this.
_HEADING_CONTEXT_LIMIT = 200


# libmagic names some valid files only by their container: a Word document or
# PowerPoint deck whose zip doesn't list [Content_Types].xml first, as
# python-docx and python-pptx write them, is "application/octet-stream". For
# these, the file's extension says what it is.
_CONTAINER_TYPES = {
    "application/octet-stream",
    "application/zip",
    "application/x-zip-compressed",
}
_EXTENSION_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def _pointer_token(key: str) -> str:
    """A key as one JSON Pointer token (RFC 6901)."""
    return key.replace("~", "~0").replace("/", "~1")


class DocumentProcessor:
    """Enhanced document processor with smart chunking capabilities"""

    def __init__(
        self,
        chunking_strategy: str = "sentence",
        max_sentences_per_chunk: int = 5,
        chunk_size: int = 50,
        chunk_overlap: int = 10,
        min_chunk_size: int = 0,
        split_newlines: int | None = None,
        index_nlp_backend: str = "nltk",
        verbose: bool = False,
        semantic_threshold: float = 0.5,
        topic_threshold: float = 0.3,
        model_name: str | None = None,
        model: Any | None = None,
    ):
        """
        Initialize document processor

        Args:
            chunking_strategy: Strategy for chunking documents:
                - 'sentence': Sentence-based chunking with overlap
                - 'sliding': Sliding window with word-based chunks
                - 'paragraph': Natural paragraph boundaries
                - 'page': Page-based chunking (for PDFs)
                - 'semantic': Semantic similarity-based chunking
                - 'topic': Topic modeling-based chunking
                - 'qa': Question-answer optimized chunking
                - 'json': JSON structure-aware chunking
                - 'markdown': Markdown structure-aware chunking with code block detection
            max_sentences_per_chunk: For sentence strategy (default: 5)
            min_chunk_size: For the markdown and paragraph strategies -
                minimum words in a chunk. A section (markdown) or paragraph
                shorter than this is merged forward into the next one instead
                of being emitted alone. Defaults to 0, which splits at every
                heading or paragraph.
            chunk_size: For sliding strategy - words per chunk (default: 50)
            chunk_overlap: For sliding strategy - overlap in words (default: 10)
            split_newlines: For sentence strategy - split on multiple newlines (optional)
            index_nlp_backend: NLP backend for indexing (default: 'nltk')
            verbose: Whether to enable verbose logging (default: False)
            semantic_threshold: Similarity threshold for semantic chunking (default: 0.5)
            topic_threshold: Similarity threshold for topic chunking (default: 0.3)
            model_name: The sentence transformer the semantic strategy compares
                sentences with; the index's own model, when an IndexBuilder
                makes the processor. Defaults to all-mpnet-base-v2. Where it
                can't be loaded, the semantic strategy falls back to sentence
                chunks, whose metadata says ``chunk_method`` ``sentence_based``.
            model: An already-loaded model for the semantic strategy: anything
                with SentenceTransformer's ``encode()``. It's used in place of
                model_name, so a caller that already holds the index's model
                doesn't load it a second time. An error its ``encode()``
                raises is the caller's to handle: there's no fallback for it.

        Raises:
            ValueError: For the sentence strategy, when max_sentences_per_chunk
                is less than 1; for the sliding strategy, when chunk_overlap is
                negative or not less than chunk_size.
        """
        if chunking_strategy == "sentence" and max_sentences_per_chunk < 1:
            raise ValueError(
                f"max_sentences_per_chunk must be at least 1, got {max_sentences_per_chunk}"
            )
        if chunking_strategy == "sliding" and not 0 <= chunk_overlap < chunk_size:
            raise ValueError(
                "chunk_overlap must be at least 0 and less than chunk_size, got "
                f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
            )
        self.chunking_strategy = chunking_strategy
        self.max_sentences_per_chunk = max_sentences_per_chunk
        self.chunk_size = chunk_size
        self.min_chunk_size = min_chunk_size
        self.chunk_overlap = chunk_overlap
        self.split_newlines = split_newlines
        self.semantic_threshold = semantic_threshold
        self.topic_threshold = topic_threshold
        self.model_name = model_name
        self.model = model

        # Legacy support for old character-based chunking
        self.chunk_overlap = chunk_overlap

    def create_chunks(
        self, content: str | list[str], filename: str, file_type: str
    ) -> list[dict[str, Any]]:
        """
        Create chunks from document content using specified chunking strategy

        Args:
            content: Document content, not a file path: a string, or the list
                of pages, paragraphs or slides extract_text() gives
            filename: Name of the file (for metadata)
            file_type: File extension/type

        Returns:
            List of chunk dictionaries
        """

        # Apply chunking strategy
        if self.chunking_strategy == "sentence":
            return self._chunk_by_sentences(content, filename, file_type)
        if self.chunking_strategy == "sliding":
            return self._chunk_by_sliding_window(content, filename, file_type)
        if self.chunking_strategy == "paragraph":
            return self._chunk_by_paragraphs(content, filename, file_type)
        if self.chunking_strategy == "page":
            return self._chunk_by_pages(content, filename, file_type)
        if self.chunking_strategy == "semantic":
            return self._chunk_by_semantic(content, filename, file_type)
        if self.chunking_strategy == "topic":
            return self._chunk_by_topics(content, filename, file_type)
        if self.chunking_strategy == "qa":
            return self._chunk_by_qa_optimization(content, filename, file_type)
        # The JSON and markdown strategies read one text
        text = self._joined(content, "\n\n")
        if self.chunking_strategy == "json":
            if file_type.lstrip(".").lower() != "json":
                # A build may mix curated JSON with other documents
                # (--file-types json,md): those are chunked by sentences.
                return self._chunk_by_sentences(text, filename, file_type)
            return self._chunk_from_json(text, filename, file_type)
        if self.chunking_strategy == "markdown":
            # Use markdown-aware chunking for better structure preservation
            return self._chunk_markdown_enhanced(text, filename)
        # Fallback to sentence-based chunking
        return self._chunk_by_sentences(content, filename, file_type)

    def _file_type(self, file_path: str) -> str:
        """A file's MIME type, by its content where python-magic is installed,
        otherwise by its extension."""
        if not magic:
            # Fallback to extension-based detection
            file_path_obj = Path(file_path)
            extension = file_path_obj.suffix.lower()

            if extension == ".pdf":
                file_type = "application/pdf"
            elif extension == ".docx":
                file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif extension in [".txt", ".md"]:
                file_type = "text/plain"
            elif extension == ".html":
                file_type = "text/html"
            elif extension == ".rtf":
                file_type = "application/rtf"
            elif extension == ".xlsx":
                file_type = (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            elif extension == ".pptx":
                file_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            else:
                file_type = "text/plain"
        else:
            try:
                mime = magic.Magic(mime=True)
                file_type = mime.from_file(file_path)
            except (FileNotFoundError, OSError):
                # Fall back to extension-based detection if magic can't read the file
                file_path_obj = Path(file_path)
                extension = file_path_obj.suffix.lower()
                ext_map = {
                    ".pdf": "application/pdf",
                    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    ".txt": "text/plain",
                    ".md": "text/plain",
                    ".html": "text/html",
                    ".rtf": "application/rtf",
                    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                }
                file_type = ext_map.get(extension, "text/plain")
        return file_type

    def extract_text(self, file_path: str) -> str | list[str]:
        """
        Extract a file's text, by its type, ready for create_chunks().

        A PDF comes back as a list of pages, a Word document as a list of its
        paragraphs and tables, a PowerPoint deck as a list of slides (with
        grouped shapes, tables and speaker notes) and an Excel workbook as a
        list of rows; anything else as one string. HTML loses its markup,
        scripts, styles, navigation, headers and footers. Under the markdown
        strategy, a Word document, a slide and an HTML page come back as
        Markdown: headings, lists and tables. A Markdown file comes back as
        written, so the markdown chunking strategy can read its headers.

        Args:
            file_path: The file to read.

        Returns:
            The file's text.

        Raises:
            DocumentExtractionError: When the file's type isn't supported, the
                library its type needs isn't installed, or reading it fails.
        """
        kind = self._kind(file_path)
        if kind == "pdf":
            return cast("str | list[str]", self._extract_pdf(file_path))
        if kind == "docx":
            return cast("str | list[str]", self._extract_docx(file_path))
        if kind == "xlsx":
            return self._extract_excel(file_path)
        if kind == "pptx":
            return cast("str | list[str]", self._extract_powerpoint(file_path))
        if kind == "html":
            return self._extract_html(file_path)
        if kind == "rtf":
            return self._extract_rtf(file_path)
        if kind in ("csv", "tsv", "json", "jsonl"):
            return [unit["text"] for unit in self._units(kind, file_path)]
        return self._extract_text(file_path)

    def extract_units(self, file_path: str) -> list[dict[str, Any]]:
        """
        Extract a file's text as units, each saying where in the file it came
        from: ``{"text": ..., "anchor": {...}}``.

        The units' texts are what extract_text() gives, in the same order. For
        HTML, extract_text() joins its sections' texts into one string; for
        another type it returns as one string, that string is the only unit.
        The anchors are:

        - PDF: ``{"page": n}``, one unit per page, ``""`` for a page without
          text (a scan);
        - Word: ``{"paragraph": n, "headings": [...]}``, n as the document
          numbers its paragraphs, or ``{"table": n, "headings": [...]}``, with
          the path of headings above it;
        - PowerPoint: ``{"slide": n}``, one unit per slide, ``""`` for a slide
          without text;
        - HTML: ``{"section": n, "headings": [...]}``, a section per heading;
        - Excel: ``{"sheet": name, "row": n}``, the row as Excel numbers it;
        - CSV and TSV: ``{"row": n}``, counting the file's rows from 1, its
          header included;
        - JSON: ``{"path": pointer}``, the JSON Pointer of the unit's value:
          each element of a top-level array, or each member of a top-level
          object;
        - JSON Lines: ``{"line": n}``, counting the file's lines from 1;
        - anything else: ``{}``, the whole file.

        Numbers count from 1.

        Args:
            file_path: The file to read.

        Returns:
            The file's units, in order.

        Raises:
            DocumentExtractionError: When the file's type isn't supported, the
                library its type needs isn't installed, or reading it fails.
        """
        return self._units(self._kind(file_path), file_path)

    def _kind(self, file_path: str) -> str:
        """Which extractor reads a file: by its MIME type, and by its
        extension for the types python-magic may report as plain text."""
        file_type = self._file_type(file_path)
        extension = Path(file_path).suffix.lower()
        if file_type in _CONTAINER_TYPES:
            file_type = _EXTENSION_TYPES.get(extension, file_type)
        # The specific types first: HTML, RTF and Markdown are text/* types
        # too, and a test for "text" would take them as plain text.
        if "pdf" in file_type:
            return "pdf"
        if "vnd.openxmlformats-officedocument.wordprocessingml.document" in file_type:
            return "docx"
        if "vnd.openxmlformats-officedocument.spreadsheetml.sheet" in file_type:
            return "xlsx"
        if "vnd.openxmlformats-officedocument.presentationml.presentation" in file_type:
            return "pptx"
        if "html" in file_type:
            return "html"
        if "rtf" in file_type:
            return "rtf"
        if "markdown" in file_type or file_path.endswith(".md"):
            return "markdown"
        # A structured text's extension says which it is: libmagic's guess
        # between them (a TSV whose cells hold commas as application/csv,
        # say) doesn't.
        structured = {
            ".jsonl": "jsonl",
            ".ndjson": "jsonl",
            ".json": "json",
            ".csv": "csv",
            ".tsv": "tsv",
        }
        if extension in structured:
            return structured[extension]
        if "ndjson" in file_type or "jsonl" in file_type:
            return "jsonl"
        if "json" in file_type:
            return "json"
        if "csv" in file_type:
            return "csv"
        if "tab-separated-values" in file_type:
            return "tsv"
        if "plain" in file_type or "text" in file_type:
            return "text"
        raise DocumentExtractionError(f"Unsupported file type: {file_type}")

    def _units(self, kind: str, file_path: str) -> list[dict[str, Any]]:
        """A file's units, read by the extractor for its kind."""
        if kind == "pdf":
            return [
                {"text": text, "anchor": {"page": number}}
                for number, text in enumerate(self._extract_pdf(file_path), start=1)
            ]
        if kind == "docx":
            return self._docx_units(file_path)
        if kind == "xlsx":
            return self._excel_units(file_path)
        if kind == "pptx":
            return self._pptx_units(file_path)
        if kind == "html":
            return self._html_units(file_path)
        if kind == "rtf":
            return [{"text": self._extract_rtf(file_path), "anchor": {}}]
        if kind in ("csv", "tsv"):
            return self._delimited_units(file_path, kind)
        if kind == "json":
            return self._json_units(file_path)
        if kind == "jsonl":
            return self._jsonl_units(file_path)
        return [{"text": self._extract_text(file_path), "anchor": {}}]

    def _delimited_units(self, file_path: str, kind: str) -> list[dict[str, Any]]:
        """A CSV or TSV file as one unit per row, labelled with the headers in
        its first non-empty row, as in ``"Plan: Pro, Price: 40"``. A cell
        without a header is labelled with its column letter, and empty cells
        are left out. A file with a single row comes back as that row's cells.
        TSV has no quoting: a quote is part of its cell."""
        import csv

        options: dict[str, Any] = (
            {"delimiter": ",", "strict": True}
            if kind == "csv"
            else {"delimiter": "\t", "quoting": csv.QUOTE_NONE, "strict": True}
        )
        header: list[str] | None = None
        header_row = 0
        header_cells: list[str] = []
        units: list[dict[str, Any]] = []
        try:
            with open(  # noqa: PTH123  # tests patch builtins.open; Path.open() would bypass the mock seam
                file_path, encoding="utf-8-sig", newline=""
            ) as file:
                for row_number, row in enumerate(csv.reader(file, **options), start=1):
                    cells = [self._cell_text(value) for value in row]
                    if header is None:
                        if any(cells):
                            header_row, header_cells = row_number, cells
                            header = [cell[:_HEADER_LABEL_LIMIT] for cell in cells]
                        continue
                    labelled = self._labelled(header, cells)
                    if labelled:
                        units.append(
                            {"text": ", ".join(labelled), "anchor": {"row": row_number}}
                        )
        except (UnicodeDecodeError, csv.Error, OSError) as e:
            raise DocumentExtractionError(
                f"Error processing {kind.upper()}: {e}"
            ) from e
        if header is not None and not units:
            units.append(
                {
                    "text": ", ".join(cell for cell in header_cells if cell),
                    "anchor": {"row": header_row},
                }
            )
        return units

    def _json_units(self, file_path: str) -> list[dict[str, Any]]:
        """A JSON document as one unit per element of a top-level array, or
        per member of a top-level object, each as ``"key.path: value"`` lines.
        A unit with no text (an empty object, a null) is left out."""
        try:
            with open(  # noqa: PTH123  # tests patch builtins.open; Path.open() would bypass the mock seam
                file_path, encoding="utf-8-sig"
            ) as file:
                source = file.read()
            data = json.loads(source)
        except RecursionError:
            raise DocumentExtractionError(
                "Error processing JSON: it's nested too deeply"
            ) from None
        except (ValueError, OSError) as e:
            raise DocumentExtractionError(f"Error processing JSON: {e}") from e
        budget = _TextBudget(_JSON_TEXT_ALLOWANCE)
        budget.add(len(source))
        if isinstance(data, list):
            parts = [(f"/{index}", item, "") for index, item in enumerate(data)]
        elif isinstance(data, dict):
            parts = [
                (f"/{_pointer_token(str(key))}", item, _json_label(str(key)))
                for key, item in data.items()
            ]
        else:
            parts = [("", data, "")]
        units = []
        for pointer, value, label in parts:
            lines: list[str] = []
            try:
                _json_lines(value, label, lines, budget)
            except RecursionError:
                raise DocumentExtractionError(
                    "Error processing JSON: it's nested too deeply"
                ) from None
            if lines:
                units.append({"text": "\n".join(lines), "anchor": {"path": pointer}})
        return units

    def _jsonl_units(self, file_path: str) -> list[dict[str, Any]]:
        """A JSON Lines file as one unit per line, each as ``"key.path: value"``
        lines. Blank lines are skipped; a line that isn't JSON fails the file."""
        units = []
        budget = _TextBudget(_JSON_TEXT_ALLOWANCE)
        try:
            with open(  # noqa: PTH123  # tests patch builtins.open; Path.open() would bypass the mock seam
                file_path, encoding="utf-8-sig"
            ) as file:
                for line_number, line in enumerate(file, start=1):
                    if not line.strip():
                        continue
                    budget.add(len(line))
                    nested = DocumentExtractionError(
                        f"Error processing JSON Lines: line {line_number} is nested too deeply"
                    )
                    try:
                        value = json.loads(line)
                    except RecursionError:
                        raise nested from None
                    except ValueError as e:
                        raise DocumentExtractionError(
                            f"Error processing JSON Lines: line {line_number} isn't JSON: {e}"
                        ) from e
                    lines: list[str] = []
                    try:
                        _json_lines(value, "", lines, budget)
                    except RecursionError:
                        raise nested from None
                    if lines:
                        units.append(
                            {"text": "\n".join(lines), "anchor": {"line": line_number}}
                        )
        except (UnicodeDecodeError, OSError) as e:
            raise DocumentExtractionError(f"Error processing JSON Lines: {e}") from e
        return units

    def _extract_text_from_file(self, file_path: str) -> Any:
        """extract_text(), with a failure returned as a JSON ``{"error": ...}``
        string, as this method always has."""
        try:
            return self.extract_text(file_path)
        except DocumentExtractionError as e:
            return json.dumps({"error": str(e)})

    def _extract_pdf(self, file_path: str) -> Any:
        """Extract text from PDF files"""
        if not pdfplumber:
            raise DocumentExtractionError("pdfplumber not available for PDF processing")

        try:
            with pdfplumber.open(file_path) as pdf:
                # One entry per page, "" for a page without text (a scan), so
                # an entry's index + 1 is its page number
                return [(page.extract_text() or "").strip() for page in pdf.pages]
        except Exception as e:
            raise DocumentExtractionError(f"Error processing PDF: {e}") from e

    def _extract_docx(self, file_path: str) -> list[str]:
        """A Word document's paragraphs and tables, in order; see _docx_units."""
        return [unit["text"] for unit in self._docx_units(file_path)]

    def _docx_units(self, file_path: str) -> list[dict[str, Any]]:
        """A Word document's paragraphs and tables in document order, each with
        its anchor: ``{"paragraph": n, "headings": [...]}``, where n counts the
        body's paragraphs from 1, or ``{"table": n, "headings": [...]}``, with
        the path of the Heading-styled paragraphs above it.

        A paragraph comes back as written and a table as one line per row,
        its cells separated by " | ". Under the markdown strategy, headings
        come back as Markdown headings, list items as list items and tables as
        Markdown tables, so the strategy splits on them.
        """
        if DocxDocument is None:
            raise DocumentExtractionError(
                "python-docx not available for DOCX processing"
            )

        try:
            from docx.table import Table
            from docx.text.paragraph import Paragraph

            doc = DocxDocument(file_path)
            as_markdown = self.chunking_strategy == "markdown"
            units: list[dict[str, Any]] = []
            headings: list[str] = []
            paragraphs = tables = 0
            for child in doc.element.body.iterchildren():
                kind = str(child.tag).rsplit("}", 1)[-1]
                if kind == "p":
                    paragraphs += 1
                    paragraph = Paragraph(child, doc)
                    text = paragraph.text
                    if not text.strip():
                        continue
                    level = _docx_heading_level(paragraph)
                    if level:
                        headings = [*headings[: level - 1], " ".join(text.split())]
                    if as_markdown:
                        text = _docx_markdown(paragraph, text, level)
                    units.append(
                        {
                            "text": text,
                            "anchor": {
                                "paragraph": paragraphs,
                                "headings": list(headings),
                            },
                        }
                    )
                elif kind == "tbl":
                    tables += 1
                    rows = _docx_table_rows(Table(child, doc))
                    if rows:
                        units.append(
                            {
                                "text": _table_text(rows, as_markdown),
                                "anchor": {"table": tables, "headings": list(headings)},
                            }
                        )
            return units
        except Exception as e:
            raise DocumentExtractionError(f"Error processing DOCX: {e}") from e

    def _extract_text(self, file_path: str) -> str:
        """Extract text from plain text files"""
        try:
            with open(  # noqa: PTH123  # tests patch builtins.open; Path.open() would bypass the mock seam
                file_path, encoding="utf-8"
            ) as file:
                return file.read()
        except Exception as e:
            raise DocumentExtractionError(f"Error processing TXT: {e}") from e

    def _extract_html(self, file_path: str) -> str:
        """An HTML page's text, its sections joined; see _html_units."""
        separator = "\n\n" if self.chunking_strategy == "markdown" else "\n"
        return separator.join(unit["text"] for unit in self._html_units(file_path))

    def _html_units(self, file_path: str) -> list[dict[str, Any]]:
        """An HTML page's sections, split at its headings, each with its
        anchor ``{"section": n, "headings": [...]}``: n counts the sections
        with text from 1, and headings is the path of h1-h6 headings above.

        Scripts, styles, navigation, headers and footers are left out. A
        section's text is its strings, one per line, as BeautifulSoup's
        get_text() gives them. Under the markdown strategy, headings come back
        as Markdown headings, list items as list items, tables as Markdown
        tables and each block as a paragraph.
        """
        if BeautifulSoup is None:
            raise DocumentExtractionError(
                "beautifulsoup4 not available for HTML processing"
            )

        try:
            with open(  # noqa: PTH123  # tests patch builtins.open; Path.open() would bypass the mock seam
                file_path, encoding="utf-8"
            ) as file:
                soup = BeautifulSoup(file, "html.parser")
            # Code, styling and the site's own navigation, not the page's content
            for tag in soup(
                ["script", "style", "noscript", "template", "nav", "header", "footer"]
            ):
                tag.decompose()
            if self.chunking_strategy == "markdown":
                sections = _html_markdown_sections(soup)
            else:
                sections = _html_text_sections(soup)
            units: list[dict[str, Any]] = []
            for headings, pieces in sections:
                text = ("\n\n" if self.chunking_strategy == "markdown" else "\n").join(
                    pieces
                )
                if text.strip():
                    units.append(
                        {
                            "text": text,
                            "anchor": {"section": len(units) + 1, "headings": headings},
                        }
                    )
            return units
        except Exception as e:
            raise DocumentExtractionError(f"Error processing HTML: {e}") from e

    def _extract_markdown(self, file_path: str) -> str:
        """Extract text from Markdown files"""
        try:
            with open(  # noqa: PTH123  # tests patch builtins.open; Path.open() would bypass the mock seam
                file_path, encoding="utf-8"
            ) as file:
                content = file.read()
                if markdown is not None and BeautifulSoup is not None:
                    html = markdown.markdown(content)
                    soup = BeautifulSoup(html, "html.parser")
                    md_text: str = soup.get_text(separator="\n")
                    return md_text
                # Fallback to raw markdown
                return content
        except Exception as e:
            raise DocumentExtractionError(f"Error processing Markdown: {e}") from e

    def _extract_rtf(self, file_path: str) -> str:
        """Extract text from RTF files"""
        if not rtf_to_text:
            raise DocumentExtractionError("striprtf not available for RTF processing")

        try:
            with open(  # noqa: PTH123  # tests patch builtins.open; Path.open() would bypass the mock seam
                file_path, encoding="utf-8"
            ) as file:
                # striprtf is untyped; rtf_to_text() returns the extracted str.
                return cast(str, rtf_to_text(file.read()))
        except Exception as e:
            raise DocumentExtractionError(f"Error processing RTF: {e}") from e

    def _extract_excel(self, file_path: str) -> list[str]:
        """Extract an Excel workbook as one entry per row.

        A sheet's first non-empty row is its header. Every row after it comes
        back labelled with the sheet's name and the headers, as in
        ``"Prices | Plan: Pro, Price: 40"``. A cell without a header is
        labelled with its column letter, a header longer than 100 characters
        is cut to them as a label, and empty cells are left out. A sheet with a
        single row comes back as that row's cells.

        extract_units() gives each row's sheet and row number too.

        A merged range's value applies to each of its cells, so a row keeps a
        value merged across the rows of its group. A workbook's merges may
        repeat a limited amount of text in all; past it, their other cells
        stay empty, as they're stored. Values are the ones Excel
        last calculated. A formula that was never calculated, as in a workbook
        a script wrote, has no stored value, so its formula text stands in for
        it.
        """
        return [unit["text"] for unit in self._excel_units(file_path)]

    def _excel_units(self, file_path: str) -> list[dict[str, Any]]:
        """An Excel workbook's rows, as _extract_excel() describes them, with
        their anchors: ``{"sheet": name, "row": n}``."""
        # Imported here rather than with the module: only Excel files need
        # openpyxl, and importing it loads numpy.
        try:
            from openpyxl import load_workbook
        except ImportError:
            raise DocumentExtractionError(
                "openpyxl not available for Excel processing"
            ) from None

        workbooks: list[Any] = []
        try:
            # Read-only workbooks stream their rows.
            values = load_workbook(file_path, read_only=True, data_only=True)
            workbooks.append(values)
            layouts = self._sheet_layouts(file_path, values.worksheets)
            formulas = None
            if any(uncalculated for _, uncalculated in layouts):
                # A second view of the workbook, with each cell's formula text.
                formulas = load_workbook(file_path, read_only=True)
                workbooks.append(formulas)
            budget = _MergeBudget()
            rows: list[dict[str, Any]] = []
            for index, value_sheet in enumerate(values.worksheets):
                formula_sheet = formulas.worksheets[index] if formulas else None
                rows.extend(
                    self._sheet_rows(value_sheet, formula_sheet, layouts[index], budget)
                )
            if budget.spent:
                logger.warning(
                    f"{file_path}: its merged cells repeat more than the limit allows; "
                    "the rest are left empty, as they are stored"
                )
            return rows
        except Exception as e:
            raise DocumentExtractionError(f"Error processing Excel: {e}") from e
        finally:
            for workbook in workbooks:
                workbook.close()  # a read-only workbook keeps its file open until closed

    @staticmethod
    def _sheet_layouts(
        file_path: str, sheets: list[Any]
    ) -> list[tuple[list[tuple[int, int, int, int]], set[tuple[int, int]]]]:
        """Each sheet's layout: its merged ranges, as (first row, first column,
        last row, last column), and the cells, as (row, column), whose formula
        has no stored value. Rows and columns count from 1.

        Read-only workbooks load neither, so they're read from the part each
        sheet was read from.
        """
        import zipfile

        layouts: list[tuple[list[tuple[int, int, int, int]], set[tuple[int, int]]]] = []
        with zipfile.ZipFile(file_path) as archive:
            for sheet in sheets:
                # openpyxl's own record of the sheet's part, so the parts read
                # here are exactly the sheets it lists.
                part = getattr(sheet, "_worksheet_path", None)
                if not isinstance(part, str):
                    logger.warning(
                        f"{file_path}: this openpyxl doesn't say where sheet "
                        f"{sheet.title!r} is stored, so its merged cells and "
                        "uncalculated formulas are read as they're stored"
                    )
                    layouts.append(([], set()))
                    continue
                with archive.open(part) as source:
                    layouts.append(DocumentProcessor._sheet_layout(source))
        return layouts

    @staticmethod
    def _sheet_layout(
        source: Any,
    ) -> tuple[list[tuple[int, int, int, int]], set[tuple[int, int]]]:
        """One sheet part's merged ranges and never-calculated formula cells.

        A formula's stored value is its ``<v>``. A cell with a formula and no
        ``<v>``, or an empty one that isn't a stored empty string
        (``t="str"``), was never calculated: that's how openpyxl and other
        scripts write formulas.
        """
        from openpyxl.xml.functions import iterparse  # defused, as openpyxl reads

        merged: list[tuple[int, int, int, int]] = []
        uncalculated: set[tuple[int, int]] = set()
        row = column = 0
        sheet_data = None
        for event, element in iterparse(source, events=("start", "end")):
            tag = element.tag
            if event == "start":
                if tag == f"{_XLSX_MAIN}sheetData":
                    sheet_data = element
                elif tag == f"{_XLSX_MAIN}row":
                    row = int(element.get("r") or row + 1)
                    column = 0
                continue
            if tag == f"{_XLSX_MAIN}c":
                reference = _CELL_REFERENCE.fullmatch(element.get("r", ""))
                column = _column_number(reference.group(1)) if reference else column + 1
                stored = element.find(f"{_XLSX_MAIN}v")
                if element.find(f"{_XLSX_MAIN}f") is not None and (
                    stored is None or (not stored.text and element.get("t") != "str")
                ):
                    uncalculated.add((row, column))
            elif tag == f"{_XLSX_MAIN}row" and sheet_data is not None:
                sheet_data.clear()  # done with the row: memory stays flat
            elif tag == f"{_XLSX_MAIN}mergeCell":
                bounds = _range_bounds(element.get("ref", ""))
                if bounds:
                    merged.append(bounds)
        return merged, uncalculated

    @classmethod
    def _sheet_rows(
        cls,
        value_sheet: Any,
        formula_sheet: Any,
        layout: tuple[list[tuple[int, int, int, int]], set[tuple[int, int]]],
        budget: _MergeBudget,
    ) -> list[dict[str, Any]]:
        """A sheet's rows, labelled with its name and headers, as units."""
        merged, uncalculated = layout
        pending: dict[int, list[int]] = {}
        for row_number, column_number in uncalculated:
            pending.setdefault(row_number, []).append(column_number)
        for sheet in (value_sheet, formula_sheet):
            if sheet is not None:
                # Read every row, whatever the file's recorded dimensions say:
                # files written by other tools often record them wrongly.
                sheet.reset_dimensions()

        value_rows = value_sheet.iter_rows(values_only=True)
        pairs: Any
        if formula_sheet is not None and pending:
            pairs = zip(
                value_rows, formula_sheet.iter_rows(values_only=True), strict=True
            )
        else:
            pairs = ((value_row, ()) for value_row in value_rows)

        # Rows with content, by row number (counting from 1, as openpyxl
        # yields an empty row for each one the file leaves out).
        grid: dict[int, list[Any]] = {}
        for row_number, (value_row, formula_row) in enumerate(pairs, start=1):
            row = list(value_row)
            for column_number in pending.get(row_number, ()):
                if column_number <= len(formula_row):
                    formula = formula_row[column_number - 1]
                    text = getattr(
                        formula, "text", formula
                    )  # an array formula keeps its text there
                    if isinstance(text, str) and text:
                        row.extend([None] * (column_number - len(row)))
                        if row[column_number - 1] is None:
                            row[column_number - 1] = text
            if any(value is not None for value in row):
                grid[row_number] = row

        numbers = sorted(grid)
        cls._fill_merged(grid, numbers, merged, budget)

        title = value_sheet.title
        header: list[str] | None = None
        header_row = 0
        rows: list[dict[str, Any]] = []
        for row_number in numbers:
            cells = cls._row_texts(grid[row_number], budget)
            if header is None:
                if any(cells):
                    header_row, header_cells = row_number, cells
                    header = [cell[:_HEADER_LABEL_LIMIT] for cell in cells]
                continue
            labelled = cls._labelled(header, cells)
            if labelled:
                rows.append(
                    {
                        "text": f"{title} | " + ", ".join(labelled),
                        "anchor": {"sheet": title, "row": row_number},
                    }
                )
        if header is not None and not rows:
            rows.append(
                {
                    "text": f"{title} | "
                    + ", ".join(cell for cell in header_cells if cell),
                    "anchor": {"sheet": title, "row": header_row},
                }
            )
        return rows

    @classmethod
    def _labelled(cls, header: list[str], cells: list[str]) -> list[str]:
        """A row's non-empty cells, each labelled with its header, or with its
        column letter where it has none."""
        return [
            f"{header[i] if i < len(header) and header[i] else cls._column_letter(i)}: {cell}"
            for i, cell in enumerate(cells)
            if cell
        ]

    @classmethod
    def _fill_merged(
        cls,
        grid: dict[int, list[Any]],
        numbers: list[int],
        merged: list[tuple[int, int, int, int]],
        budget: _MergeBudget,
    ) -> None:
        """Repeat each merged range's value into its other cells, in the rows
        that have content of their own, while the budget's cells last."""
        for first_row, first_column, last_row, last_column in merged:
            if budget.cells <= 0:
                return
            top = grid.get(first_row)
            if top is None or first_column > len(top) or top[first_column - 1] is None:
                continue
            first = top[first_column - 1]
            repeated = _Repeated(
                first.text if isinstance(first, _Repeated) else cls._cell_text(first)
            )
            # Positions, not a slice, so a tall range costs only the rows it visits.
            for position in range(
                bisect.bisect_left(numbers, first_row),
                bisect.bisect_right(numbers, last_row),
            ):
                row = grid[numbers[position]]
                for index in range(first_column - 1, last_column):
                    # Each cell visited counts, as does padding a short row out to it.
                    budget.cells -= max(index + 1 - len(row), 1)
                    if budget.cells < 0:
                        return
                    if index >= len(row):
                        row.extend([None] * (index + 1 - len(row)))
                    if row[index] is None:
                        row[index] = repeated

    @classmethod
    def _row_texts(cls, row: list[Any], budget: _MergeBudget) -> list[str]:
        """A row's cells as text. A merged range's repeated value counts against
        the budget's characters, and stays empty once they're spent."""
        texts = []
        for value in row:
            if isinstance(value, _Repeated):
                budget.characters -= len(value.text)
                texts.append(value.text if budget.characters >= 0 else "")
            else:
                texts.append(cls._cell_text(value))
        return texts

    @staticmethod
    def _cell_text(value: Any) -> str:
        """A cell's value as text on one line: whole numbers without ".0", a
        date without a midnight time, a formula as its text."""
        if value is None:
            return ""
        value = getattr(value, "text", value)  # an array formula keeps its text there
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        elif isinstance(value, datetime.datetime):
            value = value.isoformat(sep=" ").removesuffix(" 00:00:00")
        elif isinstance(value, (datetime.date, datetime.time)):
            value = value.isoformat()
        return " ".join(str(value).split())

    @staticmethod
    def _column_letter(index: int) -> str:
        """Excel's letter for a zero-based column index: 0 is A, 26 is AA."""
        letters = ""
        number = index + 1
        while number:
            number, remainder = divmod(number - 1, 26)
            letters = chr(ord("A") + remainder) + letters
        return letters

    def _extract_powerpoint(self, file_path: str) -> list[str]:
        """A PowerPoint deck's slides, one entry each; see _pptx_units."""
        return [unit["text"] for unit in self._pptx_units(file_path)]

    def _pptx_units(self, file_path: str) -> list[dict[str, Any]]:
        """A PowerPoint deck's slides, one unit each (``""`` for a slide
        without text), with the anchor ``{"slide": n}``.

        A slide's text is each shape's, one per line, in the slide's order,
        including the shapes inside groups and tables (a row per line, its
        cells separated by " | "), then its speaker notes after "Notes: ".
        Under the markdown strategy, the slide's title comes first as a
        heading, tables come back as Markdown tables, and each shape's text
        is a paragraph.
        """
        if Presentation is None:
            raise DocumentExtractionError(
                "python-pptx not available for PowerPoint processing"
            )

        try:
            as_markdown = self.chunking_strategy == "markdown"
            units: list[dict[str, Any]] = []
            for number, slide in enumerate(Presentation(file_path).slides, start=1):
                parts: list[str] = []
                title = slide.shapes.title
                title_id = None
                if as_markdown and title is not None and title.text.strip():
                    parts.append("# " + " ".join(title.text.split()))
                    title_id = title.shape_id
                for shape in slide.shapes:
                    if title_id is not None and shape.shape_id == title_id:
                        continue
                    parts.extend(_pptx_shape_texts(shape, as_markdown))
                if slide.has_notes_slide:
                    frame = slide.notes_slide.notes_text_frame
                    notes = frame.text.strip() if frame is not None else ""
                    if notes:
                        parts.append(f"Notes: {notes}")
                if as_markdown:
                    text = "\n\n".join(part for part in parts if part.strip())
                else:
                    text = "\n".join(parts)
                units.append({"text": text, "anchor": {"slide": number}})
            return units
        except Exception as e:
            raise DocumentExtractionError(f"Error processing PowerPoint: {e}") from e

    @staticmethod
    def _joined(content: str | list[str], separator: str = "\n") -> str:
        """A list's entries as one text, leaving out empty ones (a PDF page or
        a slide without text); a string as it is."""
        if not isinstance(content, list):
            return content
        return separator.join(entry for entry in content if entry and entry.strip())

    def _chunk_document_aware(
        self, content: Any, filename: str, file_type: str
    ) -> list[dict[str, Any]]:
        """Smart chunking for documents with natural structure"""
        chunks = []

        if isinstance(content, list):
            # Handle page-based or paragraph-based content (PDF, DOCX, PPTX)
            for i, page_content in enumerate(content):
                if not page_content or not page_content.strip():
                    continue

                # For each page/slide, use sentence-based chunking if it's large
                if (
                    len(page_content) > self.chunk_size * 6
                ):  # chunk_size is in words, ~6 chars/word
                    page_chunks = self._sentence_based_chunking(
                        page_content,
                        max_sentences_per_chunk=self._calculate_sentences_per_chunk(
                            page_content
                        ),
                    )
                    for j, chunk_content in enumerate(page_chunks):
                        chunks.append(
                            self._create_chunk(
                                content=chunk_content,
                                filename=filename,
                                section=f"Page {i + 1}"
                                if file_type == "pdf"
                                else f"Slide {i + 1}"
                                if file_type == "pptx"
                                else f"Section {i + 1}",
                                metadata={"page_number": i + 1, "chunk_index": j},
                            )
                        )
                else:
                    # Small page/slide - keep as single chunk
                    chunks.append(
                        self._create_chunk(
                            content=page_content,
                            filename=filename,
                            section=f"Page {i + 1}"
                            if file_type == "pdf"
                            else f"Slide {i + 1}"
                            if file_type == "pptx"
                            else f"Section {i + 1}",
                            metadata={"page_number": i + 1},
                        )
                    )
        else:
            # Single text content - use paragraph-aware chunking
            chunks = self._chunk_text_enhanced(content, filename)

        return chunks

    def _chunk_markdown_enhanced(
        self, content: str, filename: str
    ) -> list[dict[str, Any]]:
        """Enhanced markdown chunking with code block detection and rich metadata.

        Uses markdown-it-py AST when available to keep tables, fenced code,
        blockquotes, and lists atomic. Falls back to a line-based walker when
        markdown-it-py is unavailable.
        """
        if MarkdownIt is not None:
            return self._chunk_markdown_ast(content, filename)
        return self._chunk_markdown_line_walker(content, filename)

    def _chunk_markdown_ast(self, content: str, filename: str) -> list[dict[str, Any]]:
        """AST-based markdown chunker.

        Parses the doc with markdown-it-py, then walks the top-level block tokens,
        reconstructing each block from its source line range. Atomic blocks
        (tables, fenced code, blockquotes, lists, html blocks) are never split.
        Size-based splits only happen at block boundaries.
        """
        md = MarkdownIt("commonmark").enable(["table"])
        tokens = md.parse(content)
        lines = content.split("\n")
        threshold_chars = max(1, self.chunk_size * 6)
        # Minimum size before a heading is allowed to start a new chunk. Without
        # this the walker flushes at EVERY heading, so a document with dense
        # headings yields chunks that are a title plus one sentence -- true to
        # the structure but too thin to retrieve on, and they crowd out the
        # substantial chunks around them. 0 keeps the original behaviour.
        min_chars = max(0, self.min_chunk_size * 6)

        # Group top-level tokens into atomic blocks.
        # A "block" here = heading OR one non-heading container whose source
        # spans [map[0], map[1]) in the original lines.
        blocks = []  # each: {type, level?, hierarchy_update?, text, lines: [str], has_code, code_lang?}
        depth = 0
        current_open = None  # dict collecting the current container
        for tok in tokens:
            # Track nesting for container tokens so we only look at top-level opens.
            if tok.nesting == 1:
                if depth == 0:
                    current_open = {
                        "type": tok.type.replace("_open", ""),
                        "token": tok,
                        "map": tok.map,
                        "has_code": False,
                        "code_lang": None,
                    }
                depth += 1
            elif tok.nesting == -1:
                depth -= 1
                if depth == 0 and current_open is not None:
                    block = self._finalize_md_block(current_open, lines)
                    if block is not None:
                        blocks.append(block)
                    current_open = None
            else:
                # Leaf block at top level (fence, code_block, hr, html_block).
                # Skip thematic breaks ('---', '***', '___') - they are pure
                # presentational markup with no semantic content; embedding
                # them produces noise chunks that pollute search relevance.
                if depth == 0 and tok.map is not None and tok.type != "hr":
                    blocks.append(self._leaf_md_block(tok, lines))

        # Walk blocks, maintain heading hierarchy, emit chunks.
        chunks: list[dict[str, Any]] = []
        headings: list[tuple[int, str]] = []  # (level, text) from the top down
        hierarchy: list[str] = []
        current_lines: list[str] = []
        current_hierarchy: list[str] = []
        current_start_line: int | None = None
        current_end_line: int | None = None
        current_size = 0
        current_code_langs: list[str] = []
        current_has_code = False

        def flush() -> None:
            nonlocal current_lines, current_start_line, current_end_line
            nonlocal \
                current_size, \
                current_code_langs, \
                current_has_code, \
                current_hierarchy
            text = "\n".join(current_lines)
            if text.strip():
                meta = self._build_markdown_metadata(
                    current_hierarchy, current_code_langs, current_has_code
                )
                chunks.append(
                    self._create_chunk(
                        content=text,
                        filename=filename,
                        section=self._build_section_path(current_hierarchy),
                        start_line=current_start_line,
                        end_line=current_end_line,
                        metadata=meta,
                    )
                )
            current_lines = []
            current_start_line = None
            current_end_line = None
            current_size = 0
            current_code_langs = []
            current_has_code = False

        for block in blocks:
            if block["type"] == "heading":
                # Too small to stand alone: fold this section into the one being
                # built rather than emitting it. The heading line stays in the
                # text, so the reader still sees the structure; only the chunk
                # boundary moves.
                if min_chars and 0 < current_size < min_chars:
                    headings = self._push_heading(
                        headings, block["level"], block["heading_text"]
                    )
                    hierarchy = [text for _, text in headings]
                    current_lines.extend(block["source_lines"])
                    current_end_line = block["end_line"]
                    current_size += sum(len(line) + 1 for line in block["source_lines"])
                    continue
                # Flush whatever preceded this heading under the old hierarchy.
                flush()
                headings = self._push_heading(
                    headings, block["level"], block["heading_text"]
                )
                hierarchy = [text for _, text in headings]
                # Seed the new chunk with the heading line(s) themselves.
                current_hierarchy = list(hierarchy)
                current_lines = list(block["source_lines"])
                current_start_line = block["start_line"]
                current_end_line = block["end_line"]
                current_size = sum(len(line) + 1 for line in block["source_lines"])
                continue

            block_size = sum(len(line) + 1 for line in block["source_lines"])
            # If adding this block would push us over and we already have real
            # content, flush first. Keep the hierarchy for the follow-on chunk
            # so breadcrumbs continue across the split.
            if current_size + block_size > threshold_chars and current_size > 0:
                saved_hierarchy = list(current_hierarchy or hierarchy)
                flush()
                current_hierarchy = saved_hierarchy

            if not current_hierarchy:
                current_hierarchy = list(hierarchy)
            if current_start_line is None:
                current_start_line = block["start_line"]
            current_end_line = block["end_line"]
            current_lines.extend(block["source_lines"])
            current_size += block_size
            if block.get("has_code"):
                current_has_code = True
                lang = block.get("code_lang")
                if lang and lang not in current_code_langs:
                    current_code_langs.append(lang)

        flush()
        return chunks

    def _finalize_md_block(
        self, opened: dict[str, Any], lines: list[str]
    ) -> dict[str, Any] | None:
        """Turn an accumulated container token into a block record."""
        tok = opened["token"]
        tmap = opened["map"]
        if tmap is None:
            return None
        start, end = tmap  # [start, end) zero-indexed
        source_lines = lines[start:end]
        block_type = opened["type"]
        if block_type == "heading":
            level = int(tok.tag[1]) if tok.tag and tok.tag.startswith("h") else 1
            # Extract heading text from the first non-empty source line.
            heading_text = ""
            for line in source_lines:
                stripped = re.sub(r"^#{1,6}\s+", "", line).strip()
                if stripped:
                    heading_text = stripped
                    break
            return {
                "type": "heading",
                "level": level,
                "heading_text": heading_text,
                "source_lines": source_lines,
                "start_line": start + 1,
                "end_line": end,
                "has_code": False,
            }
        return {
            "type": block_type,
            "source_lines": source_lines,
            "start_line": start + 1,
            "end_line": end,
            "has_code": False,
        }

    def _leaf_md_block(self, tok: Any, lines: list[str]) -> dict[str, Any]:
        """Turn a leaf (fence, code_block, hr, html_block) token into a block."""
        start, end = tok.map
        source_lines = lines[start:end]
        block = {
            "type": tok.type,
            "source_lines": source_lines,
            "start_line": start + 1,
            "end_line": end,
            "has_code": False,
        }
        if tok.type in ("fence", "code_block"):
            block["has_code"] = True
            block["code_lang"] = (
                (tok.info.strip().split() or [None])[0]
                if tok.type == "fence" and tok.info
                else None
            )
        return block

    def _chunk_markdown_line_walker(
        self, content: str, filename: str
    ) -> list[dict[str, Any]]:
        """Legacy line-based markdown chunker. Kept as fallback when
        markdown-it-py is unavailable. Preserves original behavior with the
        empty-chunk guard applied.
        """
        chunks = []
        lines = content.split("\n")

        headings: list[tuple[int, str]] = []  # (level, text) from the top down
        current_hierarchy: list[str] = []  # Track header hierarchy
        current_chunk: list[str] = []
        current_size = 0
        line_start = 1
        in_code_block = False
        code_languages = []  # Track languages in current chunk
        has_code = False

        for line_num, line in enumerate(lines, 1):
            # Check for code block fences
            code_fence_match = re.match(r"^```(\w+)?", line)
            if code_fence_match:
                in_code_block = not in_code_block
                if in_code_block:
                    # Starting code block
                    has_code = True
                    lang = code_fence_match.group(1)
                    if lang and lang not in code_languages:
                        code_languages.append(lang)

            # Check for headers with hierarchy tracking
            header_match = (
                re.match(r"^(#{1,6})\s+(.+)", line) if not in_code_block else None
            )
            if header_match:
                header_level = len(header_match.group(1))
                header_text = header_match.group(2).strip()

                # Save current chunk if it exists and has real content
                if current_chunk and "\n".join(current_chunk).strip():
                    chunk_metadata = self._build_markdown_metadata(
                        current_hierarchy, code_languages, has_code
                    )
                    chunks.append(
                        self._create_chunk(
                            content="\n".join(current_chunk),
                            filename=filename,
                            section=self._build_section_path(current_hierarchy),
                            start_line=line_start,
                            end_line=line_num - 1,
                            metadata=chunk_metadata,
                        )
                    )

                # Update hierarchy
                headings = self._push_heading(headings, header_level, header_text)
                current_hierarchy = [text for _, text in headings]
                current_chunk = [line]
                current_size = len(line)
                line_start = line_num
                code_languages = []
                has_code = False

            else:
                current_chunk.append(line)
                current_size += len(line) + 1

                # Check if chunk is getting too large - use smart splitting
                # But don't split inside code blocks
                if (
                    current_size >= self.chunk_size * 6 and not in_code_block
                ):  # chunk_size is in words, ~6 chars/word
                    # Try to split at paragraph boundary first
                    split_point = self._find_best_split_point(current_chunk)

                    chunk_to_save = current_chunk[:split_point]
                    if "\n".join(chunk_to_save).strip():
                        chunk_metadata = self._build_markdown_metadata(
                            current_hierarchy, code_languages, has_code
                        )
                        chunks.append(
                            self._create_chunk(
                                content="\n".join(chunk_to_save),
                                filename=filename,
                                section=self._build_section_path(current_hierarchy),
                                start_line=line_start,
                                end_line=line_start + split_point - 1,
                                metadata=chunk_metadata,
                            )
                        )

                    # Start new chunk with overlap
                    overlap_lines = self._get_overlap_lines(chunk_to_save)
                    remaining_lines = current_chunk[split_point:]
                    current_chunk = overlap_lines + remaining_lines
                    current_size = sum(len(line) + 1 for line in current_chunk)
                    line_start = line_start + split_point - len(overlap_lines)
                    # Reset code tracking for new chunk
                    code_languages = []
                    has_code = False

        # Add final chunk
        if current_chunk and "\n".join(current_chunk).strip():
            chunk_metadata = self._build_markdown_metadata(
                current_hierarchy, code_languages, has_code
            )
            chunks.append(
                self._create_chunk(
                    content="\n".join(current_chunk),
                    filename=filename,
                    section=self._build_section_path(current_hierarchy),
                    start_line=line_start,
                    end_line=len(lines),
                    metadata=chunk_metadata,
                )
            )

        return chunks

    def _chunk_python_enhanced(
        self, content: str, filename: str
    ) -> list[dict[str, Any]]:
        """Enhanced Python code chunking with better function/class detection"""
        chunks = []
        lines = content.split("\n")

        current_function = None
        current_class = None
        current_chunk: list[str] = []
        current_size = 0
        line_start = 1
        indent_level = 0

        for line_num, line in enumerate(lines, 1):
            # Detect class definitions
            class_match = re.match(r"^(\s*)(class\s+([^(:\s]+))", line)
            if class_match:
                indent = len(class_match.group(1))
                class_name = class_match.group(3)

                # Save current chunk if switching context
                if current_chunk and (
                    indent <= indent_level or current_class != class_name
                ):
                    chunks.append(
                        self._create_chunk(
                            content="\n".join(current_chunk),
                            filename=filename,
                            section=self._build_python_section(
                                current_class, current_function
                            ),
                            start_line=line_start,
                            end_line=line_num - 1,
                        )
                    )
                    current_chunk = []
                    line_start = line_num

                current_class = class_name
                current_function = None
                indent_level = indent

            # Detect function definitions
            func_match = re.match(
                r"^(\s*)(def\s+([^(:\s]+)|async\s+def\s+([^(:\s]+))", line
            )
            if func_match:
                indent = len(func_match.group(1))
                func_name = func_match.group(3) or func_match.group(4)

                # Save current chunk if switching to new function at same or lower level
                if current_chunk and indent <= indent_level:
                    chunks.append(
                        self._create_chunk(
                            content="\n".join(current_chunk),
                            filename=filename,
                            section=self._build_python_section(
                                current_class, current_function
                            ),
                            start_line=line_start,
                            end_line=line_num - 1,
                        )
                    )
                    current_chunk = []
                    line_start = line_num

                if indent >= indent_level:  # Method within class or nested function
                    current_function = func_name
                else:  # Top-level function
                    current_function = func_name
                    current_class = None

                indent_level = indent

            current_chunk.append(line)
            current_size += len(line) + 1

            # Handle oversized chunks
            if (
                current_size >= self.chunk_size * 6
            ):  # chunk_size is in words, ~6 chars/word
                chunks.append(
                    self._create_chunk(
                        content="\n".join(current_chunk),
                        filename=filename,
                        section=self._build_python_section(
                            current_class, current_function
                        ),
                        start_line=line_start,
                        end_line=line_num,
                    )
                )

                # Start new chunk with minimal overlap for code
                overlap_lines = (
                    current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                )
                current_chunk = overlap_lines
                current_size = sum(len(line) + 1 for line in overlap_lines)
                line_start = line_num - len(overlap_lines) + 1

        # Add final chunk
        if current_chunk:
            chunks.append(
                self._create_chunk(
                    content="\n".join(current_chunk),
                    filename=filename,
                    section=self._build_python_section(current_class, current_function),
                    start_line=line_start,
                    end_line=len(lines),
                )
            )

        return chunks

    def _chunk_text_enhanced(self, content: str, filename: str) -> list[dict[str, Any]]:
        """Enhanced text chunking using sentence-based approach"""
        if isinstance(content, list):
            content = self._joined(content)

        # Use sentence-based chunking for better coherence
        max_sentences = self._calculate_sentences_per_chunk(content)
        sentences = self._sentence_based_chunking(content, max_sentences)

        chunks = []
        for i, chunk_content in enumerate(sentences):
            chunks.append(
                self._create_chunk(
                    content=chunk_content,
                    filename=filename,
                    section=f"Section {i + 1}",
                    metadata={"chunk_method": "sentence_based", "chunk_index": i},
                )
            )

        return chunks

    def _sentence_based_chunking(
        self, text: str, max_sentences_per_chunk: int, split_newlines: int = 2
    ) -> list[str]:
        """Sentence-based chunking with enhancements"""
        if not sent_tokenize:
            # Fallback to simple splitting
            sentences = text.split(". ")
            sentences = [s.strip() + "." for s in sentences if s.strip()]
        else:
            sentences = []

            if split_newlines > 0:
                # Create regex pattern for specified number of newlines
                newline_pattern = rf"(\n{{{split_newlines},}})"
                parts = re.split(newline_pattern, text)

                for part in parts:
                    part = part.strip()
                    if part and not re.match(newline_pattern, part):
                        sentences.extend(sent_tokenize(part))
                    elif re.match(newline_pattern, part):
                        sentences.append(part)
            else:
                sentences = [
                    sentence.strip()
                    for sentence in sent_tokenize(text)
                    if sentence.strip()
                ]

        # Create chunks of sentences with overlap: a quarter of each chunk, at
        # least one sentence, but never the whole chunk, so the window moves
        max_sentences_per_chunk = max(1, max_sentences_per_chunk)
        chunks = []
        overlap_sentences = min(
            max(1, max_sentences_per_chunk // 4), max_sentences_per_chunk - 1
        )

        for i in range(0, len(sentences), max_sentences_per_chunk - overlap_sentences):
            chunk_sentences = sentences[i : i + max_sentences_per_chunk]
            if chunk_sentences:
                chunks.append(" ".join(chunk_sentences))

        return chunks

    def _calculate_sentences_per_chunk(self, text: str) -> int:
        """Calculate optimal sentences per chunk based on average sentence length"""
        # Fallback to naive split when nltk's sent_tokenize is unavailable
        sentences = text.split(". ") if not sent_tokenize else sent_tokenize(text)

        if not sentences:
            return 1

        # `if not sentences` does not catch a list of EMPTY sentences, which is
        # what a line of dots or an ASCII rule splits into -- ". . . " becomes
        # ['', '', '', '']. That averages to 0.0 and the division below raises
        # ZeroDivisionError on a document that is merely ugly, not invalid.
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
        if avg_sentence_length <= 0:
            return 1
        # Target chunk size divided by average sentence length
        optimal_sentences = max(1, int(self.chunk_size / avg_sentence_length))
        return min(optimal_sentences, 10)  # Cap at 10 sentences for readability

    @staticmethod
    def _push_heading(
        headings: list[tuple[int, str]], level: int, text: str
    ) -> list[tuple[int, str]]:
        """Return the heading path after a heading at ``level``.

        A heading closes every open heading at its own level or deeper, and
        nests under the nearest shallower one. The path can't assume a
        heading at every level: a document that starts at ``##``, or skips
        from ``#`` to ``###``, would otherwise nest siblings as parent and
        child.
        """
        return [*(entry for entry in headings if entry[0] < level), (level, text)]

    def _build_section_path(self, hierarchy: list[str]) -> str | None:
        """Build hierarchical section path from header hierarchy"""
        return " > ".join(hierarchy) if hierarchy else None

    def _build_markdown_metadata(
        self, hierarchy: list[str], code_languages: list[str], has_code: bool
    ) -> dict[str, Any]:
        """Build rich metadata for markdown chunks

        Args:
            hierarchy: Current header hierarchy (e.g., ['Installation', 'Requirements', 'Python'])
            code_languages: List of code block languages found in chunk (e.g., ['python', 'bash'])
            has_code: Whether chunk contains any code blocks

        Returns:
            Dictionary with markdown-specific metadata including tags
        """
        metadata: dict[str, Any] = {
            "chunk_type": "markdown",
        }

        # Add header level metadata
        if hierarchy:
            for i, header in enumerate(hierarchy, 1):
                metadata[f"h{i}"] = header

        # Add code-related metadata
        if has_code:
            metadata["has_code"] = True
            if code_languages:
                metadata["code_languages"] = code_languages

        # Build tags for enhanced searching
        tags = []
        if has_code:
            tags.append("code")
            # Add language-specific tags
            tags.extend(f"code:{lang}" for lang in code_languages)

        # Add tags for header levels (searchable by section depth)
        if len(hierarchy) > 0:
            tags.append(f"depth:{len(hierarchy)}")

        if tags:
            metadata["tags"] = tags

        return metadata

    def _build_python_section(
        self, class_name: str | None, function_name: str | None
    ) -> str | None:
        """Build section name for Python code"""
        if class_name and function_name:
            return f"{class_name}.{function_name}"
        if class_name:
            return class_name
        if function_name:
            return function_name
        return None

    def _find_best_split_point(self, lines: list[str]) -> int:
        """Find the best point to split a chunk (prefer paragraph boundaries)"""
        # Look for empty lines (paragraph boundaries) in the last 25% of the chunk
        start_search = max(1, len(lines) * 3 // 4)

        for i in range(len(lines) - 1, start_search - 1, -1):
            if not lines[i].strip():  # Empty line
                return i

        # If no paragraph boundary found, split at 75% of chunk size
        return max(1, len(lines) * 3 // 4)

    def _create_chunk(
        self,
        content: str,
        filename: str,
        section: str | None = None,
        start_line: int | None = None,
        end_line: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create chunk dictionary with enhanced metadata"""
        base_metadata = {
            "file_type": Path(filename).suffix.lstrip("."),
            "chunk_size": len(content),
            "word_count": len(content.split()),
        }

        # Handle sentence count with fallback
        try:
            if sent_tokenize and content.strip():
                base_metadata["sentence_count"] = len(sent_tokenize(content))
            else:
                # Fallback: count sentences by periods
                base_metadata["sentence_count"] = len(
                    [s for s in content.split(".") if s.strip()]
                )
        except Exception as e:
            logger.warning(f"Error counting sentences: {e}")
            # Simple fallback: count periods
            base_metadata["sentence_count"] = len(
                [s for s in content.split(".") if s.strip()]
            )

        if metadata:
            base_metadata.update(metadata)

        return {
            "content": content.strip(),
            "filename": filename,
            "section": section,
            "start_line": start_line,
            "end_line": end_line,
            "metadata": base_metadata,
        }

    def _get_overlap_lines(self, lines: list[str]) -> list[str]:
        """Get overlap lines for chunk continuity"""
        if not lines:
            return []

        # Calculate overlap size in characters
        overlap_chars = self.chunk_overlap
        overlap_lines: list[str] = []
        char_count = 0

        # Take lines from the end until we reach overlap size
        for line in reversed(lines):
            if char_count + len(line) <= overlap_chars:
                overlap_lines.insert(0, line)
                char_count += len(line) + 1
            else:
                break

        return overlap_lines

    def _chunk_by_sentences(
        self, content: str | list[str], filename: str, file_type: str
    ) -> list[dict[str, Any]]:
        """Chunk content by sentences with specified max sentences per chunk"""
        if isinstance(content, list):
            content = self._joined(content)

        # Use sentence-based chunking
        split_newlines = self.split_newlines if self.split_newlines is not None else 2
        sentences = self._sentence_based_chunking(
            content, self.max_sentences_per_chunk, split_newlines
        )

        chunks = []
        for i, chunk_content in enumerate(sentences):
            chunks.append(
                self._create_chunk(
                    content=chunk_content,
                    filename=filename,
                    section=f"Section {i + 1}",
                    metadata={
                        "chunk_method": "sentence_based",
                        "chunk_index": i,
                        "max_sentences_per_chunk": self.max_sentences_per_chunk,
                        "split_newlines": split_newlines,
                    },
                )
            )

        return chunks

    def _chunk_by_sliding_window(
        self, content: str | list[str], filename: str, file_type: str
    ) -> list[dict[str, Any]]:
        """Chunk content using sliding window approach with word-based chunks"""
        if isinstance(content, list):
            content = self._joined(content)

        # Split content into words
        words = content.split()

        if not words:
            return []

        chunks = []
        chunk_index = 0

        # Create overlapping chunks
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i : i + self.chunk_size]
            if chunk_words:
                chunk_content = " ".join(chunk_words)
                chunks.append(
                    self._create_chunk(
                        content=chunk_content,
                        filename=filename,
                        section=f"Chunk {chunk_index + 1}",
                        metadata={
                            "chunk_method": "sliding_window",
                            "chunk_index": chunk_index,
                            "chunk_size_words": self.chunk_size,
                            "overlap_size_words": self.chunk_overlap,
                            "start_word": i,
                            "end_word": i + len(chunk_words),
                        },
                    )
                )
                chunk_index += 1

        return chunks

    def _chunk_by_paragraphs(
        self, content: str | list[str], filename: str, file_type: str
    ) -> list[dict[str, Any]]:
        """Chunk content by paragraphs: blank lines split a text, and each of a
        list's entries (a Word document's paragraphs, a PDF's pages) is at
        least a paragraph of its own. With min_chunk_size, a paragraph of fewer
        words merges forward into the next, so a bare heading isn't a chunk."""
        content = self._joined(content, "\n\n")

        # Split on blank lines to get paragraphs
        paragraphs = re.split(r"\n\s*\n", content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # (first paragraph's number, paragraphs) for each chunk
        groups: list[tuple[int, list[str]]] = []
        pending: list[str] = []
        first = 0
        for i, paragraph in enumerate(paragraphs):
            if not pending:
                first = i
            pending.append(paragraph)
            if sum(len(p.split()) for p in pending) >= self.min_chunk_size:
                groups.append((first, pending))
                pending = []
        if pending:
            # What's left is short: it joins the chunk before it, if any
            if groups:
                groups[-1][1].extend(pending)
            else:
                groups.append((first, pending))

        chunks = []
        for chunk_index, (first, group) in enumerate(groups):
            chunks.append(
                self._create_chunk(
                    content="\n\n".join(group),
                    filename=filename,
                    section=f"Paragraph {first + 1}",
                    metadata={
                        "chunk_method": "paragraph_based",
                        "chunk_index": chunk_index,
                        "paragraph_number": first + 1,
                        "paragraph_count": len(group),
                    },
                )
            )

        return chunks

    def _chunk_by_pages(
        self, content: str | list[str], filename: str, file_type: str
    ) -> list[dict[str, Any]]:
        """Chunk content by pages (for documents that have page boundaries)"""
        if isinstance(content, list):
            # A list (e.g., from PDF extraction) has one item per page
            pages = [str(page) for page in content]
        else:
            # For text content, try to detect page boundaries
            # Look for form feed characters or page break indicators
            if "\f" in content:
                pages = content.split("\f")
            elif "---PAGE---" in content:
                pages = content.split("---PAGE---")
            elif re.search(r"\n\s*Page\s+\d+\s*\n", content):
                # Split on "Page N" patterns
                pages = re.split(r"\n\s*Page\s+\d+\s*\n", content)
            else:
                # Fallback: split into roughly equal chunks
                words = content.split()
                words_per_page = max(500, len(words) // 10)  # Aim for ~10 pages
                pages = []
                for i in range(0, len(words), words_per_page):
                    page_words = words[i : i + words_per_page]
                    if page_words:
                        pages.append(" ".join(page_words))

        # A page without text gets no chunk, and the pages after it keep
        # their own numbers
        numbered = [(i, p.strip()) for i, p in enumerate(pages) if p.strip()]

        chunks = []
        for i, page_content in numbered:
            if page_content:
                chunks.append(
                    self._create_chunk(
                        content=page_content,
                        filename=filename,
                        section=f"Page {i + 1}",
                        metadata={
                            "chunk_method": "page_based",
                            "chunk_index": i,
                            "page_number": i + 1,
                        },
                    )
                )

        return chunks

    def _chunk_by_semantic(
        self, content: str | list[str], filename: str, file_type: str
    ) -> list[dict[str, Any]]:
        """Chunk based on semantic similarity between sentences"""
        if isinstance(content, list):
            content = self._joined(content)

        # Get sentences
        if sent_tokenize:
            sentences = sent_tokenize(content)
        else:
            sentences = content.split(". ")
            sentences = [s.strip() + "." for s in sentences if s.strip()]

        if len(sentences) <= 1:
            return [
                self._create_chunk(
                    content,
                    filename,
                    "Section 1",
                    metadata={"chunk_method": "semantic", "chunk_index": 0},
                )
            ]

        # Generate embeddings for sentences (using the same model as the index)
        in_callers_model = False
        try:
            # SentenceTransformer/np are availability probes here (ImportError
            # handled below); only cosine_similarity is referenced directly.
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np  # noqa: F401

            # The caller's own model, then model_name's, then the default
            model = self.model
            if model is None:
                from sentence_transformers import SentenceTransformer  # noqa: F401

                from signalwire.search.query_processor import _get_cached_model

                model = _get_cached_model(self.model_name)
            if model is None:
                # Model unavailable (sentence-transformers missing or load/download
                # failed, e.g. offline). Degrade gracefully to sentence chunking
                # instead of crashing on model.encode(None).
                logger.warning(
                    "Semantic chunking model unavailable; "
                    "falling back to sentence-based chunking"
                )
                return self._chunk_by_sentences(content, filename, file_type)
            # Whatever the caller's own model raises is the caller's to see
            in_callers_model = self.model is not None
            embeddings = model.encode(sentences, show_progress_bar=False)
            in_callers_model = False

            # Calculate similarity between adjacent sentences
            similarities = []
            for i in range(len(embeddings) - 1):
                sim = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
                similarities.append(sim)

            # Find split points where similarity drops below threshold
            split_points = [0]
            for i, sim in enumerate(similarities):
                if sim < self.semantic_threshold:
                    split_points.append(i + 1)
            split_points.append(len(sentences))

            # Create chunks
            chunks: list[dict[str, Any]] = []
            for i in range(len(split_points) - 1):
                start_idx = split_points[i]
                end_idx = split_points[i + 1]
                chunk_sentences = sentences[start_idx:end_idx]

                # Ensure minimum chunk size
                if len(chunk_sentences) < 2 and i > 0:
                    # Merge with previous chunk
                    chunks[-1]["content"] += " " + " ".join(chunk_sentences)
                    continue

                chunk_content = " ".join(chunk_sentences)
                chunks.append(
                    self._create_chunk(
                        content=chunk_content,
                        filename=filename,
                        section=f"Semantic Section {i + 1}",
                        metadata={
                            "chunk_method": "semantic",
                            "chunk_index": i,
                            "semantic_threshold": self.semantic_threshold,
                            "sentence_count": len(chunk_sentences),
                        },
                    )
                )

            return (
                chunks
                if chunks
                else [
                    self._create_chunk(
                        content,
                        filename,
                        "Section 1",
                        metadata={"chunk_method": "semantic", "chunk_index": 0},
                    )
                ]
            )

        except (ImportError, OSError) as e:
            # ImportError: optional deps (sentence-transformers/sklearn/numpy) missing.
            # OSError: model download/load failed at runtime (e.g. offline CI).
            # Either way, degrade gracefully to sentence-based chunking. A
            # passed model's own failure isn't a missing model: it's raised.
            if in_callers_model:
                raise
            logger.warning(
                f"Semantic chunking unavailable ({e}); falling back to sentence-based chunking"
            )
            return self._chunk_by_sentences(content, filename, file_type)

    def _chunk_by_topics(
        self, content: str | list[str], filename: str, file_type: str
    ) -> list[dict[str, Any]]:
        """Chunk based on topic changes using keyword analysis"""
        if isinstance(content, list):
            content = self._joined(content)

        if sent_tokenize:
            sentences = sent_tokenize(content)
        else:
            sentences = content.split(". ")
            sentences = [s.strip() + "." for s in sentences if s.strip()]

        if len(sentences) <= 3:
            return [
                self._create_chunk(
                    content,
                    filename,
                    "Topic 1",
                    metadata={"chunk_method": "topic", "chunk_index": 0},
                )
            ]

        try:
            # Simple topic detection using keyword overlap
            import re

            # Extract keywords from each sentence
            sentence_keywords = []
            for sentence in sentences:
                # Simple keyword extraction (could be enhanced with NLP)
                words = re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower())
                # Filter common words (basic stopwords)
                stopwords = {
                    "the",
                    "and",
                    "for",
                    "are",
                    "but",
                    "not",
                    "you",
                    "all",
                    "can",
                    "had",
                    "her",
                    "was",
                    "one",
                    "our",
                    "out",
                    "day",
                    "get",
                    "has",
                    "him",
                    "his",
                    "how",
                    "its",
                    "may",
                    "new",
                    "now",
                    "old",
                    "see",
                    "two",
                    "who",
                    "boy",
                    "did",
                    "man",
                    "way",
                    "she",
                    "use",
                    "many",
                    "oil",
                    "sit",
                    "set",
                    "run",
                    "eat",
                    "far",
                    "sea",
                    "eye",
                    "ask",
                    "own",
                    "say",
                    "too",
                    "any",
                    "try",
                    "us",
                    "an",
                    "as",
                    "at",
                    "be",
                    "he",
                    "if",
                    "in",
                    "is",
                    "it",
                    "my",
                    "of",
                    "on",
                    "or",
                    "to",
                    "up",
                    "we",
                    "go",
                    "no",
                    "so",
                    "am",
                    "by",
                    "do",
                    "me",
                }
                keywords = [w for w in words if w not in stopwords and len(w) > 3]
                sentence_keywords.append(set(keywords))

            # Find topic boundaries based on keyword overlap
            chunks: list[dict[str, Any]] = []
            current_chunk = [sentences[0]]
            current_keywords = sentence_keywords[0]

            for i in range(1, len(sentences)):
                # Calculate keyword overlap with current chunk
                overlap = len(current_keywords.intersection(sentence_keywords[i]))
                total_keywords = len(current_keywords.union(sentence_keywords[i]))

                similarity = overlap / total_keywords if total_keywords > 0 else 0

                # If similarity is low, start new chunk
                if similarity < self.topic_threshold and len(current_chunk) >= 2:
                    chunk_content = " ".join(current_chunk)
                    chunks.append(
                        self._create_chunk(
                            content=chunk_content,
                            filename=filename,
                            section=f"Topic {len(chunks) + 1}",
                            metadata={
                                "chunk_method": "topic",
                                "chunk_index": len(chunks),
                                "topic_keywords": list(current_keywords)[
                                    :10
                                ],  # Top keywords
                                "sentence_count": len(current_chunk),
                                "topic_threshold": self.topic_threshold,
                            },
                        )
                    )
                    current_chunk = [sentences[i]]
                    current_keywords = sentence_keywords[i]
                else:
                    current_chunk.append(sentences[i])
                    current_keywords = current_keywords.union(sentence_keywords[i])

            # Add final chunk
            if current_chunk:
                chunk_content = " ".join(current_chunk)
                chunks.append(
                    self._create_chunk(
                        content=chunk_content,
                        filename=filename,
                        section=f"Topic {len(chunks) + 1}",
                        metadata={
                            "chunk_method": "topic",
                            "chunk_index": len(chunks),
                            "topic_keywords": list(current_keywords)[:10],
                            "sentence_count": len(current_chunk),
                            "topic_threshold": self.topic_threshold,
                        },
                    )
                )

            return (
                chunks
                if chunks
                else [
                    self._create_chunk(
                        content,
                        filename,
                        "Topic 1",
                        metadata={"chunk_method": "topic", "chunk_index": 0},
                    )
                ]
            )

        except Exception:
            # Fallback to sentence-based chunking
            return self._chunk_by_sentences(content, filename, file_type)

    def _chunk_by_qa_optimization(
        self, content: str | list[str], filename: str, file_type: str
    ) -> list[dict[str, Any]]:
        """Create chunks optimized for question-answering"""
        if isinstance(content, list):
            content = self._joined(content)

        if sent_tokenize:
            sentences = sent_tokenize(content)
        else:
            sentences = content.split(". ")
            sentences = [s.strip() + "." for s in sentences if s.strip()]

        # Patterns that indicate Q&A structure
        question_patterns = [
            r"\?",  # Questions
            r"^(what|how|why|when|where|who|which|can|does|is|are|will|would|should)",
            r"(step|steps|process|procedure|method|way to)",
            r"(example|examples|instance|case)",
            r"(definition|meaning|refers to|means)",
        ]

        chunks: list[dict[str, Any]] = []
        current_chunk: list[str] = []
        current_context = []

        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower().strip()

            # Check if this sentence contains Q&A indicators
            is_qa_relevant = any(
                re.search(pattern, sentence_lower) for pattern in question_patterns
            )

            if is_qa_relevant or len(current_chunk) == 0:
                current_chunk.append(sentence)
                # Add surrounding context (previous and next sentences)
                if (
                    i > 0
                    and sentences[i - 1] not in current_chunk
                    and sentences[i - 1] not in current_context
                ):
                    current_context.append(sentences[i - 1])
                if (
                    i < len(sentences) - 1
                    and sentences[i + 1] not in current_chunk
                    and sentences[i + 1] not in current_context
                ):
                    current_context.append(sentences[i + 1])
            else:
                current_chunk.append(sentence)

            # Create chunk when we have enough content or reach a natural break
            if len(current_chunk) >= 3 and (
                i == len(sentences) - 1  # Last sentence
                or (sentence.endswith(".") and len(current_chunk) >= 5)
            ):  # Natural break
                # Combine chunk with context
                full_content = current_context + current_chunk
                chunk_content = " ".join(full_content)

                chunks.append(
                    self._create_chunk(
                        content=chunk_content,
                        filename=filename,
                        section=f"QA Section {len(chunks) + 1}",
                        metadata={
                            "chunk_method": "qa_optimized",
                            "chunk_index": len(chunks),
                            "has_question": any("?" in s for s in current_chunk),
                            "has_process": any(
                                re.search(r"(step|process|method)", s.lower())
                                for s in current_chunk
                            ),
                            "sentence_count": len(full_content),
                        },
                    )
                )

                current_chunk = []
                current_context = []

        # Handle remaining content
        if current_chunk:
            chunk_content = " ".join(current_context + current_chunk)
            chunks.append(
                self._create_chunk(
                    content=chunk_content,
                    filename=filename,
                    section=f"QA Section {len(chunks) + 1}",
                    metadata={
                        "chunk_method": "qa_optimized",
                        "chunk_index": len(chunks),
                        "sentence_count": len(current_context + current_chunk),
                    },
                )
            )

        return (
            chunks
            if chunks
            else [
                self._create_chunk(
                    content,
                    filename,
                    "QA Section 1",
                    metadata={"chunk_method": "qa_optimized", "chunk_index": 0},
                )
            ]
        )

    def _chunk_from_json(
        self, content: str, filename: str, file_type: str
    ) -> list[dict[str, Any]]:
        """
        Create chunks from pre-processed JSON content

        This strategy expects content to be a JSON string with the following structure:
        {
            "chunks": [
                {
                    "chunk_id": "unique_id",
                    "type": "content|toc",
                    "content": "text content",
                    "metadata": {
                        "url": "https://...",
                        "section_number": 1,
                        "related_toc": "toc_id",
                        ...
                    }
                },
                ...
            ]
        }

        Args:
            content: JSON string containing pre-chunked content
            filename: Name of the source file
            file_type: Should be 'json'

        A chunk's ``section`` is read from its metadata, or else from the chunk
        itself, where ``sw-search --output-format json`` writes it.

        Returns:
            List of chunk dictionaries formatted for the search index

        Raises:
            ChunkFormatError: When content isn't JSON in that format. Nothing
                is chunked: a malformed file isn't indexed as text instead.
        """
        if not content.strip():
            return []  # nothing to chunk, as for every other strategy
        entries = self.parse_json_chunks(content, filename)
        chunks = []
        # Heading carried down to the chunks beneath it. A reference doc
        # splits as "# send_fax" then "## Parameters", "## Returns",
        # "## Example" - and only the first chunk names the subject. The
        # rest are titled "**Parameters**" and contain no clue what they
        # parameterise, so they are unretrievable by name, while the
        # heading chunk is four words of prose that loses to any fatter
        # document with the same title.
        #
        # Measured on the shipped index, two docs both titled `send_fax`:
        #   idx 7223  SWML method, properties inline   -> 0.933
        #   idx 3739  Relay Python, heading + links    -> 0.280
        # The Relay doc holds the RelayClient example someone asking "how
        # do I send a fax with the python relay sdk" wants, and it could
        # not be surfaced by ANY phrasing tried - its distinguishing words
        # (Relay, Python, RelayClient, the code) all live in the sibling
        # chunks, which have no subject of their own.
        #
        # Prepending the heading makes every chunk self-describing: the
        # example chunk now carries "send_fax" AND "RelayClient", so it is
        # reachable by either. Chunk COUNT and order are untouched, so
        # chunk_index still addresses the same source chunk.
        current_heading = ""
        current_doc = None
        # The heading text the loop may add in all: each subsection repeats
        # its topic's heading, so a long one over many subsections could
        # otherwise make an enormous text. Past it, subsections go as written.
        inherited_budget = 4 * len(content) + _JSON_TEXT_ALLOWANCE
        for idx, json_chunk in enumerate(entries):
            # Extract metadata from JSON chunk
            json_metadata = json_chunk.get("metadata") or {}
            chunk_type = json_chunk.get("type", "content")

            # Build chunk metadata (excluding tags which go at top level)
            metadata = {
                "chunk_method": "json",
                "chunk_index": idx,
                "chunk_type": chunk_type,
                "original_chunk_id": json_chunk.get("chunk_id", f"chunk_{idx}"),
            }

            # Extract tags: merge top-level chunk.tags with metadata.tags so
            # neither source is silently dropped. build_index_from_sources
            # writes its --tags global tags to the TOP LEVEL of each chunk,
            # while the markdown chunker writes auto-tags (depth:N, code:LANG)
            # to chunk.metadata.tags. Reading only one would lose the other.
            tags = list(
                dict.fromkeys(
                    list(json_chunk.get("tags") or [])
                    + list(json_metadata.get("tags") or [])
                )
            )

            # Merge JSON metadata (this includes all fields including tags)
            # We'll keep tags in metadata for backward compatibility but also set at top level
            metadata.update(json_metadata)

            # Determine section name
            if chunk_type == "toc":
                section = f"TOC: {json_chunk.get('content', '')[:50]}"
            else:
                # The metadata's, or the chunk's own, as sw-search writes it
                named = json_metadata.get("section")
                if named is None:
                    named = json_chunk.get("section")
                section = (
                    named
                    if named is not None
                    else f"Section {json_metadata.get('section_number', idx + 1)}"
                )

            # Create chunk with proper structure
            chunk_text = json_chunk["content"]
            stripped = chunk_text.lstrip()

            # One JSON file routinely holds chunks from many source
            # documents, and current_heading would otherwise carry across
            # the boundary: the last heading of one document prepended to
            # the first subsection of the next, asserting a subject the
            # chunk does not have. It does not fire on the corpus this was
            # written for -- every chunk there opens with its own h1, so
            # the heading is reset each time, and a scan of 16,894 chunks
            # found no instance -- but that is a property of those inputs,
            # not of this loop. Reset when the document changes.
            doc_key = document_key(json_metadata)
            if doc_key != current_doc:
                current_doc = doc_key
                current_heading = ""
            if stripped.startswith("# ") and not stripped.startswith("## "):
                # A new topic: remember its heading, and leave it alone -
                # it already names itself.
                current_heading = stripped.split("\n", 1)[0].strip()
                if len(current_heading) > _HEADING_CONTEXT_LIMIT:
                    current_heading = (
                        current_heading[: _HEADING_CONTEXT_LIMIT - 1] + "\u2026"
                    )
            elif (
                current_heading
                and stripped.startswith("#")
                and len(current_heading) + 2 <= inherited_budget
                and current_heading.lower() not in chunk_text.lower()
            ):
                # A subsection of that topic: give it the subject back.
                inherited_budget -= len(current_heading) + 2
                chunk_text = f"{current_heading}\n\n{chunk_text}"
                metadata["heading_context"] = current_heading

            chunk = self._create_chunk(
                content=chunk_text,
                filename=filename,
                section=section,
                metadata=metadata,
            )

            # Set tags at the top level for proper tag filtering
            if tags:
                chunk["tags"] = tags
            elif chunk_type == "toc":
                # For TOC entries, add special tags if none provided
                chunk["tags"] = ["toc", "navigation"]

            chunks.append(chunk)

        if not chunks:
            logger.warning(f"No chunks in JSON file {filename}")
            return []

        logger.info(f"Created {len(chunks)} chunks from JSON file {filename}")
        return chunks

    @staticmethod
    def parse_json_chunks(
        content: str, filename: str = "chunks.json"
    ) -> list[dict[str, Any]]:
        """The entries of a document in the JSON chunk format, each checked
        against it, as the json strategy reads them, without chunking them.

        Use it to read a caller's own chunks as written: the json strategy
        also gives a subsection the heading above it.

        Args:
            content: The document's text.
            filename: Its name, for the error's message.

        Returns:
            The document's ``chunks``, in order, as they're written.

        Raises:
            ChunkFormatError: When content isn't JSON in that format, naming
                the first entry that's wrong.
        """
        try:
            data = json.loads(content)
        except RecursionError:
            raise ChunkFormatError(
                f"{filename}: the JSON is nested too deeply"
            ) from None
        except ValueError as e:
            raise ChunkFormatError(f"{filename}: not valid JSON: {e}") from None
        if not isinstance(data, dict) or not isinstance(data.get("chunks"), list):
            raise ChunkFormatError(
                f'{filename}: expected an object with a "chunks" list'
            )
        entries: list[dict[str, Any]] = data["chunks"]
        for index, entry in enumerate(entries):
            where = f"{filename}: chunk {index}"
            if not isinstance(entry, dict) or not isinstance(entry.get("content"), str):
                raise ChunkFormatError(f'{where} needs a string "content"')
            # Present means the right type: a null metadata or tags is out of
            # the format. A null section is what _create_chunk() writes.
            metadata = entry.get("metadata", {})
            if not isinstance(metadata, dict):
                raise ChunkFormatError(f'{where}: "metadata" must be an object')
            for holder in (entry, metadata):
                section = holder.get("section")
                if section is not None and not isinstance(section, str):
                    raise ChunkFormatError(f'{where}: "section" must be a string')
                tags = holder.get("tags", [])
                if not (
                    isinstance(tags, list) and all(isinstance(tag, str) for tag in tags)
                ):
                    raise ChunkFormatError(f'{where}: "tags" must be a list of strings')
        return entries
