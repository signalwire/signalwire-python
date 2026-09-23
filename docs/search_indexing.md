# Search Indexing Guide

This guide covers building search indexes, chunking strategies, embedding models, and the full CLI reference for the SignalWire Agents SDK search system. For installation and architecture overview see [Search Overview](search_overview.md). For pgvector deployment details see [Search Deployment](search_deployment.md). For agent integration see [Search Integration](search_integration.md).

---

## Building Indexes

Search indexes are SQLite databases with the `.swsearch` extension that contain processed documents, embeddings, and search metadata. Indexes can also be stored in PostgreSQL via the pgvector backend.

### CLI Quick Start (sw-search)

The `sw-search` command-line tool is the primary interface for building, searching, validating, and migrating indexes.

**Single directory:**

```bash
sw-search ./docs --output knowledge.swsearch
```

**Multiple directories:**

```bash
sw-search ./docs ./examples ./tutorials --output knowledge.swsearch
```

**Specific files:**

```bash
sw-search README.md CONTRIBUTING.md docs/api.md --output knowledge.swsearch
```

**Mixed (directories and files):**

```bash
sw-search ./docs README.md ./examples/agent.py --output knowledge.swsearch
```

**Build from the comprehensive concepts guide:**

```bash
sw-search docs/agent_guide.md --output concepts.swsearch
```

**Full configuration example:**

```bash
sw-search docs/agent_guide.md ./examples README.md \
    --output ./knowledge.swsearch \
    --chunking-strategy sentence \
    --max-sentences-per-chunk 8 \
    --file-types md,txt,rst,py \
    --exclude "**/test/**,**/__pycache__/**" \
    --model mini \
    --tags documentation,api \
    --verbose
```

**Build to pgvector:**

```bash
sw-search ./docs \
  --backend pgvector \
  --connection-string "postgresql://user:pass@localhost:5432/db" \
  --output docs_collection \
  --chunking-strategy markdown
```

With pgvector, `--output` specifies the collection name, not a filename.

### Python API (IndexBuilder)

Build an index directly from Python instead of the CLI when an agent needs to construct its own index at startup:

<!-- snippet: no-run blocking/long-running call (server or live connection) -->
```python
from signalwire.search import IndexBuilder

# Create index builder
builder = IndexBuilder(
    model_name="sentence-transformers/all-mpnet-base-v2",
    chunk_size=500,
    chunk_overlap=50,
    verbose=True
)

# Build index
builder.build_index(
    source_dir="./docs",
    output_file="docs.swsearch",
    file_types=["md", "txt"],
    exclude_patterns=["**/test/**"],
    tags=["documentation"]
)
```

### Output Formats (.swsearch)

Each `.swsearch` file is a SQLite database containing:

- **Document chunks** with embeddings and metadata
- **Full-text search index** (SQLite FTS5)
- **Configuration** and model information
- **Synonym cache** for query expansion

The index can be distributed as a single portable file. For production multi-agent deployments, the pgvector backend provides concurrent access and real-time updates.

---

## Chunking Strategies

Before content can be searched, it must be broken into chunks. The chunking strategy has a significant impact on search quality. Each chunk should ideally be a self-contained unit that answers a question or explains a concept.

**Chunk size trade-offs:**

- **Small chunks:** More precise matching, less noise in results, but may lack context and can split related information.
- **Large chunks:** More context, keeps related information together, but less precise matching and more noise in results.

### Overview of All Strategies

The SDK provides nine chunking strategies, each optimized for different content types.

**1. Sentence-Based (Default)**

Groups sentences together, splitting at natural sentence boundaries.

```bash
sw-search ./docs --chunking-strategy sentence --max-sentences-per-chunk 5
```

Parameters:

- `max-sentences-per-chunk`: Number of sentences per chunk (default: 5)
- `split-newlines`: Minimum newlines to force a split (default: 2)

Best for general documentation, blog posts, plain text, and as a default starting point.

**2. Paragraph**

Splits at paragraph boundaries (double newlines).

```bash
sw-search ./docs --chunking-strategy paragraph
```

Best for content with clear paragraph structure and markdown files with distinct sections. Avoid for dense text with long paragraphs.

**3. Page**

Splits documents at page boundaries.

```bash
sw-search ./docs --chunking-strategy page --file-types pdf
```

Best for PDF documents, presentations, and reports with page-level organization. Not applicable to web content or markdown.

**4. Sliding Window**

Creates overlapping chunks by sliding a window across the text.

```bash
sw-search ./docs \
  --chunking-strategy sliding \
  --chunk-size 100 \
  --overlap-size 20
```

Parameters:

- `chunk-size`: Words per chunk
- `overlap-size`: Words that overlap between chunks

Best for ensuring context is not lost at chunk boundaries and for dense technical content. Trade-off: produces more chunks (larger index) due to overlap.

Example:

```
Text: "A B C D E F G H I J"
Chunk size: 5, Overlap: 2

Chunk 1: A B C D E
Chunk 2:     D E F G H
Chunk 3:         G H I J
```

**5. Semantic**

Groups sentences with similar embeddings together.

```bash
sw-search ./docs \
  --chunking-strategy semantic \
  --semantic-threshold 0.6
```

Parameters:

- `semantic-threshold`: Similarity threshold for grouping (0.0-1.0)

Best for content that naturally clusters by topic and long documents with shifting topics. Avoid for short documents or already well-structured content.

**6. Topic**

Detects topic changes and splits at those boundaries.

```bash
sw-search ./docs \
  --chunking-strategy topic \
  --topic-threshold 0.2
```

Parameters:

- `topic-threshold`: Sensitivity to topic changes (lower = more splits)

Best for long-form content covering multiple topics, articles, and meeting transcripts. Avoid for focused documents on a single topic.

**7. QA-Optimized**

Optimized for question-answering; preserves questions with their answers.

```bash
sw-search ./docs --chunking-strategy qa
```

Features:

- Detects question patterns (what, how, why, etc.)
- Keeps questions with surrounding context
- Adds metadata: `has_question`, `has_process`

Best for FAQ documents, tutorials, and troubleshooting guides.

Example:

```
Text:
"How do you create an agent? First, inherit from AgentBase. Then define your
configuration. Finally, call run() to start the server."

Chunk metadata: {has_question: true, has_process: true}
-> Preserved as single chunk with full context
```

**8. Markdown-Aware**

Chunks at header boundaries, detects code blocks, preserves document structure. See [Markdown Strategy (Deep Dive)](#markdown-strategy-deep-dive) for full details.

```bash
sw-search ./docs \
  --chunking-strategy markdown \
  --file-types md
```

Features:

- Chunks at `##` header boundaries
- Never splits code blocks
- Detects programming language in code blocks
- Adds tags: `code`, `code:python`, `code:bash`
- Preserves header hierarchy in metadata

Best for technical documentation with code examples, GitHub README files, API documentation, and developer guides.

**9. JSON (Pre-chunked Content)**

Reads pre-chunked content from JSON files. See [JSON Manual Curation Workflow](#json-manual-curation-workflow) for full details.

```bash
sw-search ./chunks/ \
  --chunking-strategy json \
  --file-types json
```

Best for manually curated knowledge bases, content from APIs that is already structured, and when precise control over chunks is required.

### Choosing the Right Strategy

Decision tree:

```
Do you need code examples to be findable?
+-- Yes -> Use markdown strategy
+-- No
   +-- Is it FAQ/tutorial content?
   |  +-- Yes -> Use qa strategy
   +-- No
      +-- Is it a PDF?
      |  +-- Yes -> Use page strategy
      +-- No
         +-- Need precise control?
         |  +-- Yes -> Use json strategy
         +-- No
            +-- Use sentence strategy (default)
```

#### Strategy Comparison Matrix

| Strategy | Best For | Chunk Size | Pros | Cons |
|----------|----------|------------|------|------|
| sentence | General text | Small | Fast, simple | May split context |
| paragraph | Articles, blogs | Medium | Natural boundaries | Variable size |
| page | Books, papers | Large | Preserves context | May be too large |
| sliding | Dense content | Medium | Overlapping context | Duplication |
| semantic | Narrative text | Variable | Topic coherence | Slower |
| topic | Long documents | Variable | Topic-based | Requires NLP |
| qa | FAQ content | Medium | Keeps Q&A together | Needs structure |
| markdown | Technical docs | Variable | Preserves code | Markdown required |
| json | Pre-chunked | Any | Full control | Manual work |

#### Strategy Comparison on Real Content

Original text (API docs):

```markdown
## Authentication

All API requests require authentication. Use your API key in the Authorization header.

### Python Example

import requests

headers = {
    "Authorization": "Bearer YOUR_API_KEY"
}
response = requests.get("https://api.example.com/data", headers=headers)

### Common Errors

Error 401 means invalid credentials. Error 403 means insufficient permissions.
```

**Sentence strategy result:**

- Chunk 1: "All API requests require authentication. Use your API key in the Authorization header."
- Chunk 2: "import requests headers = { "Authorization": "Bearer YOUR_API_KEY" } response = ..."
- Chunk 3: "Error 401 means invalid credentials. Error 403 means insufficient permissions."

Problem: Code is split from its context.

**Markdown strategy result:**

- Chunk 1 (## Authentication section): Full section including header and description. Metadata: `{h2: "Authentication"}`
- Chunk 2 (### Python Example section): Header + complete code block (unsplit). Metadata: `{h2: "Authentication", h3: "Python Example", has_code: true, tags: ["code", "code:python"]}`
- Chunk 3 (### Common Errors section): Header + error descriptions. Metadata: `{h2: "Authentication", h3: "Common Errors"}`

Code is intact, hierarchical context is preserved, and chunks are searchable by code tag.

### Chunk Size Recommendations

Starting points by strategy:

- **Sentence strategy:** 5-8 sentences per chunk
- **Paragraph strategy:** Let natural paragraphs define size
- **Sliding window:** 100-200 words, 20-40 word overlap
- **Markdown strategy:** Let headers define size (naturally varies)

### Markdown Strategy (Deep Dive)

The markdown chunking strategy is specifically designed for technical documentation. Generic chunking strategies (sentence, paragraph) treat documentation as plain text and do not understand code blocks, headers, or section hierarchy.

#### Header-Based Splitting

Headers (`##`, `###`, etc.) mark logical topic changes. The strategy uses them as natural chunk boundaries:

```markdown
## Authentication

Content about authentication...

## Configuration

Content about configuration...
```

This becomes two chunks, each containing the complete section content.

Each chunk knows its place in the document structure:

```markdown
# API Reference

## Authentication

### Bearer Tokens

Content here...
```

The "Bearer Tokens" chunk has full context:
- h1: "API Reference"
- h2: "Authentication"
- h3: "Bearer Tokens"

Best practices for headers:

```markdown
## Topic (h2 for main topics)
### Subtopic (h3 for subtopics)
#### Detail (h4 for details)
```

Avoid skipping levels (e.g., going from `##` directly to `####`).

#### Code Block Preservation

Code blocks are detected and treated as atomic units: they are never split across chunks.

```markdown
## Example

Here's how to create an agent:

    from signalwire import AgentBase

    class MyAgent(AgentBase):
        def __init__(self):
            super().__init__(name="MyAgent")

This creates a basic agent.
```

This entire section becomes one chunk with the complete code block intact.

Keep code examples under descriptive headers so that code chunks have descriptive headers in their metadata.

Always specify the language in code fences. Without language tags, code chunks miss language-specific metadata and tagging.

#### Language Detection

The strategy extracts the language from code fence syntax (e.g., ` ```python `, ` ```bash `, ` ```javascript `). Each chunk gets language-specific metadata and tags such as `code:python` or `code:javascript`.

These tags enable precise language-specific searches. For example, a query for "javascript example voice" will match chunks tagged `code:javascript` over chunks tagged `code:python`.

#### Hierarchy Metadata

Each chunk automatically receives rich metadata:

```python
{
    "h1": "Getting Started",           # Top-level header
    "h2": "Creating Your First Agent", # Second-level header
    "h3": "Python Example",            # Third-level header
    "has_code": True,                  # Contains code blocks
    "code_languages": ["python"],      # Languages in this chunk
    "tags": ["code", "code:python"],   # Searchable tags
    "depth": 3                         # Header nesting depth
}
```

Code and non-code chunks are scored by the same vector, keyword, and metadata signals described in [Search Overview](search_overview.md#hybrid-search-algorithm). The `code` and `code:<language>` tags do not add a separate ranking boost. They make code chunks reachable through tag filtering and keyword search on the language name.

**Building with the markdown strategy:**

```bash
sw-search ./docs \
  --chunking-strategy markdown \
  --file-types md \
  --output docs.swsearch
```

**With pgvector:**

```bash
sw-search ./docs \
  --chunking-strategy markdown \
  --backend pgvector \
  --connection-string "postgresql://user:pass@localhost:5432/knowledge" \
  --output signalwire_docs
```

**Limitations:**

- Does not help with non-markdown content
- Poorly structured markdown (missing headers) degrades results
- Code outside fenced blocks (inline code) is treated as plain text
- Documentation that does not use headers will not benefit

For content that lacks headers, consider the JSON workflow for manual structuring.

### JSON Manual Curation Workflow

The JSON workflow provides full manual control over what gets indexed, how it is structured, and what metadata is attached. It is suited for high-value knowledge bases, API documentation from structured sources, content from databases, and cases where quality control requires reviewing every chunk.

#### Two-Phase Workflow

**Phase 1: Export chunks to JSON**

Use automatic chunking to generate candidate chunks, then export to JSON for review:

```bash
# Export all chunks to a single JSON file
sw-search ./docs \
  --chunking-strategy markdown \
  --output-format json \
  --output all_chunks.json
```

Or export to separate files (one per source document):

```bash
# Export to directory with one JSON file per source
sw-search ./docs \
  --chunking-strategy markdown \
  --output-format json \
  --output-dir ./chunks/
```

**Phase 2: Build index from JSON**

After reviewing and editing the JSON, build the final index:

```bash
sw-search ./chunks/ \
  --chunking-strategy json \
  --file-types json \
  --output final.swsearch
```

Common edits during review:

- Add descriptive chunk IDs (replace auto-generated `chunk_0`, `chunk_1`)
- Add relevant tags for hybrid search boosting
- Add URLs to source documentation
- Add priority levels (`high`, `normal`, `low`)
- Link related chunks via `related_chunks`
- Remove low-value chunks (e.g., header-only content)
- Merge chunks that are always relevant together

**Combining automatic and manual chunks:**

```bash
# Export critical docs to JSON for curation
sw-search ./docs/critical/ \
  --output-format json \
  --output critical_chunks.json

# Edit critical_chunks.json manually

# Build index from both curated JSON and automatic chunking
sw-search ./critical_chunks.json ./docs/other/ \
  --chunking-strategy json \
  --file-types json,md \
  --output combined.swsearch
```

#### JSON Schema (Required/Optional Fields)

**Complete JSON Schema (draft-07):**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["chunks"],
  "properties": {
    "chunks": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["content"],
        "properties": {
          "content": {
            "type": "string",
            "minLength": 1,
            "description": "The text content of the chunk"
          },
          "metadata": {
            "type": "object",
            "properties": {
              "filename": { "type": "string", "description": "Source filename" },
              "section": { "type": "string", "description": "Section or chapter name" },
              "h1": { "type": "string", "description": "Top-level heading" },
              "h2": { "type": "string", "description": "Second-level heading" },
              "h3": { "type": "string", "description": "Third-level heading" },
              "h4": { "type": "string", "description": "Fourth-level heading" },
              "h5": { "type": "string", "description": "Fifth-level heading" },
              "h6": { "type": "string", "description": "Sixth-level heading" },
              "tags": {
                "type": "array",
                "items": { "type": "string" },
                "description": "Tags for filtering and hybrid search"
              },
              "category": { "type": "string", "description": "Content category" },
              "subcategory": { "type": "string", "description": "Content subcategory" },
              "priority": {
                "type": "string",
                "enum": ["critical", "high", "normal", "low"],
                "description": "Content priority"
              },
              "difficulty": {
                "type": "string",
                "enum": ["beginner", "intermediate", "advanced", "expert"],
                "description": "Content difficulty level"
              },
              "audience": { "type": "string", "description": "Target audience" },
              "language": {
                "type": "string",
                "pattern": "^[a-z]{2}(-[A-Z]{2})?$",
                "description": "Language code (e.g., en, en-US, fr)"
              },
              "has_code": { "type": "boolean", "description": "Whether chunk contains code" },
              "code_languages": {
                "type": "array",
                "items": { "type": "string" },
                "description": "Programming languages in chunk"
              },
              "has_url": { "type": "boolean", "description": "Whether chunk contains URLs" },
              "urls": {
                "type": "array",
                "items": { "type": "string", "format": "uri" },
                "description": "URLs mentioned in chunk"
              },
              "version": { "type": "string", "description": "Product version" },
              "created_at": { "type": "string", "format": "date-time", "description": "Creation timestamp" },
              "updated_at": { "type": "string", "format": "date-time", "description": "Last update timestamp" },
              "author": { "type": "string", "description": "Content author" },
              "source": { "type": "string", "description": "Content source" },
              "verified": { "type": "boolean", "description": "Whether content is verified" },
              "chunk_id": { "type": "string", "description": "Unique chunk identifier" },
              "related_chunks": {
                "type": "array",
                "items": { "type": "string" },
                "description": "IDs of related chunks"
              },
              "prerequisite": { "type": "string", "description": "Prerequisite chunk ID" },
              "next_topic": { "type": "string", "description": "Next topic chunk ID" }
            },
            "additionalProperties": true
          }
        }
      }
    }
  }
}
```

**Required fields:**

- `chunks` (array): Top-level array containing all chunk objects.
- `content` (string, per chunk): The actual text content. Minimum length: 1 character. Can include markdown formatting.

**All metadata fields are optional.** Custom metadata fields are allowed (`additionalProperties: true`) and are stored and preserved. They are not used by search unless custom logic is implemented.

**Minimal valid JSON:**

```json
{
  "chunks": [
    {
      "content": "This is a chunk of text."
    }
  ]
}
```

**Standard example:**

```json
{
  "chunks": [
    {
      "content": "To create an agent, inherit from AgentBase and implement your methods...",
      "metadata": {
        "filename": "getting_started.md",
        "section": "Creating Agents",
        "h1": "Getting Started",
        "h2": "Creating Your First Agent",
        "tags": ["agent", "getting-started", "tutorial"],
        "category": "documentation",
        "difficulty": "beginner",
        "has_code": true,
        "code_languages": ["python"]
      }
    }
  ]
}
```

**Complete example with all common fields:**

```json
{
  "chunks": [
    {
      "content": "Here's how to authenticate with the API:\n\n```python\nfrom signalwire import AgentBase\n\nagent = AgentBase(\n    name=\"MyAgent\",\n    api_key=\"your_key\"\n)\n```\n\nThis creates an authenticated agent instance.",
      "metadata": {
        "chunk_id": "auth_example_001",
        "filename": "authentication.md",
        "section": "API Authentication",
        "h1": "Authentication",
        "h2": "Getting Started",
        "h3": "Python Example",
        "tags": ["authentication", "api", "python", "code", "example", "getting-started"],
        "category": "documentation",
        "subcategory": "authentication",
        "priority": "high",
        "difficulty": "beginner",
        "audience": "developers",
        "language": "en-US",
        "has_code": true,
        "code_languages": ["python"],
        "has_url": false,
        "version": "2.0",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-20T15:30:00Z",
        "author": "docs-team",
        "source": "official-docs",
        "verified": true,
        "related_chunks": ["auth_example_002", "auth_troubleshooting"],
        "next_topic": "authorization"
      }
    }
  ]
}
```

**Multi-chunk example with relationships:**

```json
{
  "chunks": [
    {
      "content": "Authentication is the process of verifying identity...",
      "metadata": {
        "chunk_id": "auth_001",
        "h1": "Authentication",
        "h2": "Overview",
        "tags": ["authentication", "security", "overview"],
        "difficulty": "beginner"
      }
    },
    {
      "content": "To authenticate, use Bearer tokens...",
      "metadata": {
        "chunk_id": "auth_002",
        "h1": "Authentication",
        "h2": "Bearer Tokens",
        "tags": ["authentication", "security", "bearer-token"],
        "difficulty": "beginner",
        "prerequisite": "auth_001"
      }
    },
    {
      "content": "Here's a Python example of authentication...",
      "metadata": {
        "chunk_id": "auth_003",
        "h1": "Authentication",
        "h2": "Examples",
        "h3": "Python",
        "tags": ["authentication", "python", "code", "example"],
        "difficulty": "intermediate",
        "has_code": true,
        "code_languages": ["python"],
        "prerequisite": "auth_002"
      }
    }
  ]
}
```

#### Use Cases (API Docs, Custom Content)

**Scraping API documentation:**

<!-- snippet: no-run live REST/HTTP call to a real host (needs credentials/network) -->
```python
import json
import requests
from bs4 import BeautifulSoup

def scrape_api_docs(base_url):
    """Scrape API docs and create structured chunks"""
    chunks = []

    response = requests.get(f"{base_url}/api/docs")
    soup = BeautifulSoup(response.text, 'html.parser')

    for endpoint in soup.find_all('div', class_='endpoint'):
        method = endpoint.find('span', class_='method').text
        path = endpoint.find('span', class_='path').text
        description = endpoint.find('p', class_='description').text

        chunk = {
            "chunk_id": f"endpoint_{method}_{path.replace('/', '_')}",
            "type": "content",
            "content": f"{method} {path}\n\n{description}",
            "metadata": {
                "section": "API Endpoints",
                "method": method,
                "path": path,
                "tags": ["api", "endpoint", method.lower()],
                "url": f"{base_url}/api/docs#{path}"
            }
        }
        chunks.append(chunk)

    return {"chunks": chunks}

docs = scrape_api_docs("https://api.example.com")
with open("api_chunks.json", "w") as f:
    json.dump(docs, f, indent=2)
```

**Table of Contents entries:**

```json
{
  "chunks": [
    {
      "chunk_id": "toc_main",
      "type": "toc",
      "content": "Table of Contents: Getting Started, API Reference, Guides",
      "metadata": {
        "tags": ["toc", "navigation"],
        "section_number": 0
      }
    },
    {
      "chunk_id": "toc_getting_started",
      "type": "toc",
      "content": "Getting Started: Installation, Quick Start, First Agent",
      "metadata": {
        "tags": ["toc", "getting-started"],
        "related_toc": "toc_main",
        "section_number": 1
      }
    },
    {
      "chunk_id": "content_installation",
      "type": "content",
      "content": "Installation instructions...",
      "metadata": {
        "related_toc": "toc_getting_started",
        "tags": ["installation", "getting-started"]
      }
    }
  ]
}
```

**Programmatic generation (Python):**

```python
import json
from datetime import datetime
from typing import List

class ChunkBuilder:
    """Build JSON chunks programmatically"""

    def __init__(self):
        self.chunks = []

    def add_chunk(
        self,
        content: str,
        tags: List[str] = None,
        category: str = None,
        difficulty: str = None,
        has_code: bool = False,
        **extra_metadata
    ):
        chunk = {
            "content": content,
            "metadata": {
                "created_at": datetime.utcnow().isoformat() + "Z",
                **extra_metadata
            }
        }
        if tags:
            chunk["metadata"]["tags"] = tags
        if category:
            chunk["metadata"]["category"] = category
        if difficulty:
            chunk["metadata"]["difficulty"] = difficulty
        if has_code:
            chunk["metadata"]["has_code"] = has_code
        self.chunks.append(chunk)

    def to_json(self, output_path: str):
        with open(output_path, 'w') as f:
            json.dump({"chunks": self.chunks}, f, indent=2)

# Usage
builder = ChunkBuilder()

builder.add_chunk(
    content="Getting started with the API...",
    tags=["getting-started", "api"],
    category="documentation",
    difficulty="beginner",
    h1="Getting Started",
    h2="Overview"
)

builder.add_chunk(
    content="Here's a Python example:\n```python\ncode here\n```",
    tags=["python", "code", "example"],
    category="documentation",
    difficulty="intermediate",
    has_code=True,
    code_languages=["python"],
    h1="Getting Started",
    h2="Examples"
)

builder.to_json("chunks.json")
```

**Programmatic generation (JavaScript):**

```javascript
const fs = require('fs');

class ChunkBuilder {
  constructor() {
    this.chunks = [];
  }

  addChunk(content, metadata = {}) {
    this.chunks.push({
      content,
      metadata: {
        created_at: new Date().toISOString(),
        ...metadata
      }
    });
  }

  toJSON(outputPath) {
    const data = JSON.stringify({ chunks: this.chunks }, null, 2);
    fs.writeFileSync(outputPath, data);
  }
}

const builder = new ChunkBuilder();

builder.addChunk(
  "Getting started with the API...",
  {
    tags: ["getting-started", "api"],
    category: "documentation",
    difficulty: "beginner",
    h1: "Getting Started",
    h2: "Overview"
  }
);

builder.toJSON("chunks.json");
```

#### Validation

**Using JSON schema validator:**

<!-- snippet: no-run reads a data/index file that must be built first (needs a real artifact) -->
```python
import json
import jsonschema

with open('chunk_schema.json') as f:
    schema = json.load(f)

with open('chunks.json') as f:
    chunks = json.load(f)

try:
    jsonschema.validate(chunks, schema)
    print("Valid JSON")
except jsonschema.ValidationError as e:
    print(f"Invalid: {e.message}")
```

**Basic validation script:**

<!-- snippet: no-run reads a data/index file that must be built first (needs a real artifact) -->
```python
import json

def validate_chunks(filename):
    """Validate chunk JSON structure"""
    with open(filename) as f:
        data = json.load(f)

    if "chunks" not in data:
        print("ERROR: Missing 'chunks' key")
        return False

    for i, chunk in enumerate(data["chunks"]):
        if "content" not in chunk:
            print(f"ERROR: Chunk {i} missing 'content'")
            return False

        if not chunk["content"].strip():
            print(f"WARNING: Chunk {i} has empty content")

        if "chunk_id" not in chunk:
            print(f"WARNING: Chunk {i} missing 'chunk_id'")

        if "metadata" in chunk:
            if "tags" not in chunk["metadata"]:
                print(f"INFO: Chunk {i} has no tags")

    print(f"Validated {len(data['chunks'])} chunks")
    return True

validate_chunks("api_chunks.json")
```

**Command-line JSON syntax validation:**

```bash
python -m json.tool chunks.json > /dev/null && echo "Valid JSON"
```

**Common validation errors:**

- Missing `content` field (required)
- Empty content string (must be non-empty)
- Invalid `priority` value (must be `critical`, `high`, `normal`, or `low`)
- Invalid `language` code (must match ISO format like `en` or `en-US`)

### Inspecting and Testing Chunks

Export chunks to JSON to review how they are split:

```bash
sw-search ./docs \
  --chunking-strategy markdown \
  --output-format json \
  --output chunks.json
```

Review `chunks.json` for:

- Chunks that are too small (missing context)
- Chunks that are too large (too much noise)
- Code blocks that are split (indicates wrong strategy)
- Related concepts that are separated

Build test indexes with different strategies and compare:

```bash
sw-search ./docs --chunking-strategy sentence --output sentence.swsearch
sw-search ./docs --chunking-strategy markdown --output markdown.swsearch
sw-search ./docs --chunking-strategy qa --output qa.swsearch
```

Then test queries against each:

```bash
sw-search search sentence.swsearch "how to authenticate"
sw-search search markdown.swsearch "how to authenticate"
sw-search search qa.swsearch "how to authenticate"
```

---

## Embedding Models

The embedding model affects both search quality and performance. The SDK uses the sentence-transformers library and provides two model aliases, `mini` and `base`, plus a deprecated third, `large`.

### Available Models (mini, base, large)

| Model | Alias | Full Identifier | Dimensions | Parameters | Size | Speed |
|-------|-------|----------------|------------|------------|------|-------|
| Mini | `mini` | `sentence-transformers/all-MiniLM-L6-v2` | 384 | 22.7M | ~90MB | Fast |
| Base | `base` | `sentence-transformers/all-mpnet-base-v2` | 768 | 109M | ~420MB | Medium |

The `large` alias is deprecated. It loads the same model as `base`, so it changes nothing, and `sw-search` prints a warning when you use it. It can't be pointed at a bigger model, because indexes built with it would stop matching their queries. Use `base` instead.

These commands build an index with each model:

```bash
sw-search ./docs --model mini   # Recommended default
sw-search ./docs --model base   # Higher quality
```

**Mini (all-MiniLM-L6-v2)** is the recommended default:

- 6-layer transformer based on Microsoft's MiniLM
- 384-dimensional embeddings
- Embeds chunks and queries faster than base, on both CPU and GPU
- Uses less runtime memory than base
- Best for: production deployments, voice agents (latency-sensitive), large knowledge bases (>50K chunks), FAQ systems, general documentation

**Base (all-mpnet-base-v2)**:

- 12-layer transformer based on Microsoft's MPNet
- 768-dimensional embeddings
- Embeds chunks and queries more slowly than mini, on both CPU and GPU
- Uses more runtime memory than mini
- Best for: quality-critical applications, complex semantic searches, legal/medical documentation, nuanced language understanding

**Large**

The `large` alias currently points at the same `all-mpnet-base-v2` model as `base`, so it has the same specifications and behavior described earlier. Selecting `large` today does not give access to a bigger model.

### Speed vs Quality Tradeoffs

Mini and base sit on a tradeoff. Mini embeds faster and uses less memory. Base tends to retrieve more relevant results on tasks that need finer semantic distinctions, at the cost of speed and memory. Evaluate both models against your own documents and queries before choosing one for production.

Build time, query latency, and memory use all scale with the embedding model, the chunking strategy, the storage backend, and the host's hardware. Measure a representative build and a representative set of queries on your own corpus and hardware rather than relying on a generic table.

**When mini is sufficient (most cases):**

- Well-structured documentation with clear headings
- Distinct topics per section
- Code examples (combined with markdown strategy)
- Consistent terminology
- Conversational queries ("how do I install", "show me configuration example")

**When base provides meaningful improvement:**

- Subtle semantic distinctions (e.g., "latency" vs "lag" vs "delay", "authenticate" vs "authorize" vs "validate")
- Domain-specific technical jargon
- Multi-language content requiring cross-lingual similarity
- Small indexes where speed is not a concern

**Model selection by use case:**

| Use Case | Recommendation | Reason |
|----------|---------------|--------|
| Voice agents | Mini | Latency critical |
| Chat agents | Mini or Base | Latency less critical |
| FAQ systems | Mini | Queries are short and specific |
| Technical documentation | Mini | Good with structured text + markdown strategy |
| Legal/Medical | Base | Nuance and accuracy critical |
| Research/Academic | Base | Complex language, subtle distinctions |
| Multi-lingual | Base | Better cross-lingual transfer |

### Embedding Dimensions and Storage

Embeddings are vectors: lists of floating-point numbers representing meaning. Higher dimensions capture more subtle semantic nuances but require more computation and storage.

**Storage requirements per chunk:**

| Model | Calculation | Bytes per Chunk |
|-------|------------|-----------------|
| Mini | 384 floats x 4 bytes | 1,536 bytes |
| Base | 768 floats x 4 bytes | 3,072 bytes |
| Large | Same as Base | Same as Base |

**For 10,000 chunks (vectors only):**

- Mini: ~15MB
- Base: ~30MB
- Large: same as Base, ~30MB

Total index size is larger than the vector storage alone, since it also holds the chunk content, metadata, and search indexes.

**pgvector column definitions:**

```sql
-- Mini model (384 dimensions)
embedding vector(384)   -- 1,536 bytes per row

-- Base model, and large, which currently uses the same model (768 dimensions)
embedding vector(768)   -- 3,072 bytes per row
```

### Custom Models

Any sentence-transformers compatible model from HuggingFace can be used:

```bash
# Multi-lingual model
sw-search ./docs --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# Instruction-tuned model
sw-search ./docs --model hkunlp/instructor-base

# Domain-specific models
sw-search ./docs --model pritamdeka/S-PubMedBert-MS-MARCO    # Medical
sw-search ./docs --model sentence-transformers/allenai-specter  # Scientific
```

Requirements for custom models:

- Must be available on HuggingFace
- Must be compatible with sentence-transformers (supports `.encode()` method)
- Must output fixed-size embeddings
- Model downloads automatically on first use

**Model download and caching:**

Models are downloaded automatically on first use and cached locally:

- Linux/Mac: `~/.cache/huggingface/hub/`
- Windows: `C:\Users\<user>\.cache\huggingface\hub\`

Use the `TRANSFORMERS_CACHE` environment variable to customize the cache directory. Set `TRANSFORMERS_OFFLINE=1` to prevent model downloads (offline mode).

**GPU acceleration:**

All models embed faster on a GPU than on a CPU:

```python
import torch
from sentence_transformers import SentenceTransformer

if torch.cuda.is_available():
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
else:
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
```

Base needs more GPU VRAM than mini, and `large` needs the same amount as base, since it currently resolves to the same model.

**Hardware recommendations:**

Base needs more CPU, memory, and disk than mini at every stage, from local development through production with multiple agents. Provision your infrastructure by testing your own workload rather than a generic sizing table.

### Migrating Between Models

To change models, the index must be rebuilt. Embeddings from different models are not compatible and cannot be converted.

```bash
# Original index (base model)
sw-search ./docs --model base --output docs_base.swsearch

# Switch to mini model -- requires full rebuild
sw-search ./docs --model mini --output docs_mini.swsearch
```

Do not mix models in a single index. Indexes built with one model cannot be searched with a different model due to dimension mismatches (384 for mini vs. 768 for base and large). When searching an existing index, the system automatically detects and uses the model that was used to build it.

---

## CLI Reference

### Building Indexes (Options, File Types, Exclusions)

The build command takes one or more source paths followed by options:

```bash
sw-search [SOURCE_PATHS...] [OPTIONS]
```

**Arguments:**

- `SOURCE_PATHS`: One or more paths to directories or files to index

**Build options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--output PATH` | Output path for .swsearch file (or collection name for pgvector) | `<source_dir>.swsearch` |
| `--output-dir DIR` | Output directory for JSON export (one file per source), or for auto-named index files | -- |
| `--output-format {index,json}` | Output format: `index` (build a `.swsearch` index) or `json` (export chunks as JSON) | `index` |
| `--chunking-strategy STRATEGY` | Chunking method: `sentence`, `sliding`, `paragraph`, `page`, `semantic`, `topic`, `qa`, `json`, `markdown` | `sentence` |
| `--model MODEL` | Embedding model: `mini`, `base`, `large`, or full model name | `mini` |
| `--backend BACKEND` | Storage backend: `sqlite`, `pgvector` | `sqlite` |
| `--connection-string STRING` | PostgreSQL connection string (required for pgvector) | -- |
| `--overwrite` | Overwrite existing collection (pgvector only) | -- |
| `--tags TAG1,TAG2,...` | Comma-separated tags to add to all chunks | -- |
| `--file-types EXT1,EXT2,...` | Comma-separated file extensions to include for directories | `md,txt,rst` |
| `--exclude PATTERN1,...` | Glob patterns for files to exclude | -- |
| `--max-sentences-per-chunk N` | Sentences per chunk (for sentence strategy) | `5` |
| `--chunk-size N` | Words per chunk (for sliding strategy) | `50` |
| `--min-chunk-size N` | Markdown strategy: minimum words before a heading starts a new chunk. Shorter sections merge into the next one instead of standing alone | `0` (split at every heading) |
| `--overlap-size N` | Words of overlap between chunks (for sliding strategy) | `10` |
| `--split-newlines N` | Minimum newlines to force a split (for sentence strategy) | `2` |
| `--semantic-threshold FLOAT` | Similarity threshold for grouping (for semantic strategy) | `0.5` |
| `--topic-threshold FLOAT` | Topic change sensitivity (for topic strategy) | `0.3` |
| `--languages LANGS` | Comma-separated language codes | `en` |
| `--index-nlp-backend {nltk,spacy}` | NLP backend for document processing during indexing | `nltk` |
| `--verbose` | Enable verbose output | -- |
| `--validate` | Validate the created index after building | -- |

The top-level `sw-search --help` shortcut is hand-maintained and sometimes omits real flags, including `--backend` and `--connection-string`. Run `sw-search build --help` (any unrecognized first argument falls through to the build command) for the full, generated list.

**Supported file types:**

| Category | Extensions |
|----------|-----------|
| Text | `txt`, `md`, `rst`, `asciidoc` |
| Code | `py`, `js`, `ts`, `java`, `cpp`, `c`, `go`, `rs` |
| Documents | `pdf`, `docx`, `xlsx`, `pptx` |
| Web | `html`, `xml` |
| Data | `json`, `yaml`, `csv` |

**Exclude patterns** use glob syntax (`*`, `**`, `?`):

```bash
sw-search ./docs \
  --exclude "**/test/**,**/__pycache__/**,**/node_modules/**"

sw-search ./project \
  --exclude "*.log,*.tmp,**/build/**,**/dist/**"
```

**Verbose output example:**

```
Building search index:
  Backend: sqlite
  Sources: ['docs']
  Output file: docs.swsearch
  File types (for directories): ['md', 'txt', 'rst']
  Languages: ['en']
  Model: sentence-transformers/all-MiniLM-L6-v2
  Chunking strategy: sentence
  Index NLP backend: nltk

Added 42 files from directory: docs
Found 42 files to process
Processing 42 files...
  docs/getting-started.md: 3 chunks
  docs/api-reference.md: 12 chunks
  examples/agent.py: 5 chunks
  ...
Created 150 total chunks
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Generating embeddings for 150 chunks...
  Progress: 150/150 chunks (100.0%)
Index created: docs.swsearch
Total chunks: 150

Search index created successfully: docs.swsearch
```

### Searching Indexes

The search command takes an index path, a query, and options:

```bash
sw-search search [INDEX_PATH] [QUERY] [OPTIONS]
```

**Arguments:**

- `INDEX_PATH`: Path to `.swsearch` file (or collection name for pgvector)
- `QUERY`: Search query string

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--backend BACKEND` | Backend to search (`sqlite`, `pgvector`) | `sqlite` |
| `--connection-string STRING` | PostgreSQL connection string (for pgvector) | -- |
| `--shell` | Interactive shell mode: load the index once and run multiple searches | -- |
| `--model MODEL` | Override the embedding model for the query (must match the indexing model) | -- |
| `--count N` | Number of results to return | `5` |
| `--similarity-threshold FLOAT` | Minimum similarity score. Higher is stricter. `--distance-threshold` is the older name | `0.0` |
| `--tags TAG1,TAG2,...` | Filter by tags | -- |
| `--query-nlp-backend {nltk,spacy}` | NLP backend for query preprocessing | `nltk` |
| `--keyword-weight FLOAT` | Deprecated: accepted, but has no effect on ranking | -- |
| `--verbose` | Show similarity scores and metadata | -- |
| `--json` | Output results as JSON for scripting | -- |
| `--no-content` | Hide content in results (show only metadata) | -- |

`INDEX_PATH` doubles as the pgvector collection name; there is no separate `--collection-name` option for search.

**Basic search:**

```bash
sw-search search ./knowledge.swsearch "how to create an agent"
```

Output:

```
Found 3 result(s) for 'how to create an agent':
================================================================================

[1] Score: 0.8700
File: getting-started.md
Section: Creating Your First Agent

Content:
To create an agent, inherit from AgentBase and define your configuration...
--------------------------------------------------------------------------------

[2] Score: 0.8200
File: api-reference.md
Section: AgentBase Class

Content:
The AgentBase class is the foundation for all agents...
--------------------------------------------------------------------------------

[3] Score: 0.7800
File: simple_agent.py

Content:
class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="MyAgent")...
```

**Verbose output:**

```bash
sw-search search ./knowledge.swsearch "query" --verbose
```

The `--verbose` flag adds a preamble before the same result list. It states how many chunks and files the index contains, and which NLP backend and embedding model answered the query. It does not print a hybrid-scoring breakdown, and `--json` does not include one either.

```
Loading search index: knowledge.swsearch
Index contains 150 chunks from 42 files
Searching for: 'query'
Query NLP Backend: nltk
Using index model: sentence-transformers/all-MiniLM-L6-v2

Found 5 result(s) for 'query':
================================================================================
...
```

**JSON output (for scripting):**

```bash
sw-search search ./knowledge.swsearch "query" --json
```

Output:

```json
{
  "query": "how to create an agent",
  "enhanced_query": "how to create an agent",
  "count": 1,
  "results": [
    {
      "rank": 1,
      "score": 0.87,
      "metadata": {
        "filename": "getting-started.md",
        "section": "Creating Your First Agent",
        "tags": [],
        "metadata": {
          "file_type": "md"
        }
      },
      "content": "To create an agent, inherit from AgentBase and define your configuration..."
    }
  ]
}
```

**JSON output piped to jq:**

```bash
sw-search search concepts.swsearch "error handling" --json | jq '.results[0].content'
```

**Filter by tags:**

```bash
sw-search search ./knowledge.swsearch "query" --tags api,reference
```

**pgvector search:**

```bash
sw-search search docs_collection "how to create an agent" \
    --backend pgvector \
    --connection-string "postgresql://user:pass@localhost/dbname"
```

### Validating Indexes

The validate command takes a single index path:

```bash
sw-search validate [INDEX_PATH]
```

Checks index integrity and displays statistics.

```bash
sw-search validate ./knowledge.swsearch
```

Output:

```
Index is valid: knowledge.swsearch
  Chunks: 150
  Files: 42

Configuration:
  embedding_model: sentence-transformers/all-MiniLM-L6-v2
  embedding_dimensions: 384
  chunk_size: 50
  min_chunk_size: 0
  chunk_overlap: 10
  preprocessing_version: 1.0
  languages: ["en"]
  created_at: 2025-01-15T10:30:00
  sources: ["docs"]
  file_types: ["md", "txt", "rst"]
```

Add `--verbose` to include the `Configuration:` block; without it, `sw-search validate` prints only the chunk and file counts. `validate` takes an `index_file` path and `--verbose`; it has no `--backend` or `--connection-string` option, so it cannot check a pgvector collection directly.

**Validate using Python API:**

<!-- snippet: no-run constructs SearchEngine with an index file that must exist first -->
```python
from signalwire.search import SearchEngine
engine = SearchEngine(index_path='docs.swsearch')
print(f'Index stats: {engine.get_stats()}')
```

### Exporting to JSON

There is no separate export subcommand. JSON export uses the same build command as indexing, with `--output-format json` in place of the default `--output-format index`. It re-chunks the source documents; it does not read an existing `.swsearch` file. To inspect the chunks already in a built index, query the SQLite database directly: `sqlite3 knowledge.swsearch "SELECT filename, section, content FROM chunks"`.

**Export all chunks to single file:**

```bash
sw-search ./docs \
  --output-format json \
  --output all_chunks.json
```

**Export to separate files (one per source document):**

```bash
sw-search ./docs \
  --output-format json \
  --output-dir ./chunks/
```

Creates one JSON file per source document:

```
chunks/
  docs_getting-started.json
  docs_api-reference.json
  examples_agent.json
```

### Remote Search

The remote command queries a search server over HTTP instead of a local file:

```bash
sw-search remote [ENDPOINT] [QUERY] [OPTIONS]
```

**Arguments:**

- `ENDPOINT`: Search server URL
- `QUERY`: Search query

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--index-name NAME` | Index to search on remote server (required) | -- |
| `--count N` | Number of results | `5` |
| `--similarity-threshold FLOAT` | Minimum similarity score. Higher is stricter. `--distance-threshold` is the older name | `0.0` |
| `--tags TAG1,TAG2,...` | Filter by tags | -- |
| `--verbose` | Show detailed information | -- |
| `--json` | Output results as JSON | -- |
| `--no-content` | Hide content in results (show only metadata) | -- |
| `--timeout SECONDS` | Request timeout | `30` |
| `--user USER` | Basic auth user for the search server | -- |
| `--password PASSWORD` | Basic auth password. Without it, `sw-search` reads `SWML_BASIC_AUTH_PASSWORD`, or asks for it | -- |

**Basic remote search:**

```bash
sw-search remote http://localhost:8001 "query" --index-name docs
```

`sw-search remote` sends the request with a plain `Content-Type: application/json` header only. It has no `--auth-user` or `--auth-pass` option, so a remote search server behind authentication needs a proxy or gateway that handles it.

Remote search is useful for centralized search services, multiple agents querying the same index, and separating search from agent infrastructure.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRANSFORMERS_CACHE` | Directory for cached models | `~/.cache/huggingface/hub` |
| `TRANSFORMERS_OFFLINE` | Use offline mode, do not download models (set to `1`) | -- |

`sw-search` and the search module read no other environment variables: there is no `SW_SEARCH_MODEL`, `SW_SEARCH_VERBOSE`, or `PGVECTOR_CONNECTION` that the CLI picks up automatically. Model, output path, verbosity, and the pgvector connection string are always passed as explicit flags (`--model`, `--output`, `--verbose`, `--connection-string`).

Example:

```bash
export TRANSFORMERS_OFFLINE=1

sw-search ./docs --backend pgvector --connection-string "postgresql://user:pass@localhost:5432/knowledge" --output docs
```

### Batch Processing

**Process multiple directories:**

```bash
for dir in docs-v1 docs-v2 docs-v3; do
  sw-search ./$dir --output ${dir}.swsearch
done
```

**Build indexes in parallel:**

```bash
sw-search ./docs1 --output docs1.swsearch &
sw-search ./docs2 --output docs2.swsearch &
sw-search ./docs3 --output docs3.swsearch &
wait
```

**Multi-collection pgvector build:**

With pgvector, `--output` names the collection; there is no separate `--collection-name` option for the build command.

```bash
sw-search ./docs/api \
  --backend pgvector \
  --connection-string "$DATABASE_URL" \
  --output api_docs

sw-search ./docs/guides \
  --backend pgvector \
  --connection-string "$DATABASE_URL" \
  --output guides

sw-search ./docs/examples \
  --backend pgvector \
  --connection-string "$DATABASE_URL" \
  --output examples
```

`sw-search validate` has no `--backend` option, so it cannot check a pgvector collection. Query the collection's table directly with `psql`, or search it instead: `sw-search search <collection> "<query>" --backend pgvector --connection-string "$DATABASE_URL"`.

**Migration commands:**

```bash
# SQLite to pgvector
sw-search migrate ./knowledge.swsearch \
  --to-pgvector \
  --connection-string "postgresql://localhost/db" \
  --collection-name docs

# Get migration info
sw-search migrate --info ./knowledge.swsearch
```

The reverse direction, from a pgvector collection back to a `.swsearch` file, isn't implemented: `--to-sqlite` exits with an error without writing anything. To get a `.swsearch` file, build one from the source documents.

**Performance tuning:**

The build command has no `--batch-size` or `--workers` option; `--batch-size` only applies to `sw-search migrate`. To manage build-time memory and speed, choose a smaller embedding model instead:

```bash
# Memory-constrained environments: the mini model uses the least memory
sw-search ./docs --model mini
```

**Debugging build issues:**

```bash
# Maximum verbosity
sw-search ./docs --verbose

# Test on single file
sw-search ./docs/problematic.md --output test.swsearch --verbose

# Build and immediately validate
sw-search ./docs --output test.swsearch && \
sw-search validate test.swsearch
```

---

## Configuration Reference

### All Parameters

The `native_vector_search` skill accepts the following parameters. For full skill integration details, see [Search Integration](search_integration.md).

**Required parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_name` | string | SWAIG function name |
| `description` | string | Description of when the LLM should use this tool |

**Backend selection (choose one):**

| Parameter | Type | Description |
|-----------|------|-------------|
| `index_file` | string | Path to local `.swsearch` file |
| `remote_url` + `index_name` | string | Remote search server URL and index name |
| `backend` + `connection_string` + `collection_name` + `model_name` | string | pgvector database configuration |

**Search behavior parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | int | `5` | Number of results to return |
| `similarity_threshold` | float | `0.0` | Minimum similarity score (0.0 to 1.0). Higher is stricter |
| `tags` | list[str] | -- | Filter results by tags |
| `max_content_length` | int | `32768` | Maximum total response characters |

**User experience parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `no_results_message` | string | Message when no results found (use `{query}` placeholder) |
| `response_format_callback` | callable | Custom formatter: `(response, agent, query, results, **kwargs) -> str` |
| `swaig_fields` | dict | SWAIG configuration (fillers, wait files) |

**SWAIG fields structure:**

```python
{
    "swaig_fields": {
        "fillers": {
            "en-US": [
                "Searching...",
                "Let me look that up...",
                "Checking the documentation..."
            ]
        },
        "wait_file": "https://example.com/hold.wav",  # Optional
        "wait_file_loops": 3                            # Optional
    }
}
```

**Complete configuration example:**

```python
self.add_skill("native_vector_search", {
    # Identity
    "tool_name": "search_product_docs",
    "description": "Search comprehensive product documentation including features, APIs, configuration, and troubleshooting",

    # Backend (pgvector)
    "backend": "pgvector",
    "connection_string": "postgresql://user:pass@localhost:5432/knowledge",
    "collection_name": "product_docs",
    "model_name": "mini",

    # Search behavior
    "count": 5,
    "similarity_threshold": 0.4,
    "tags": ["documentation", "api"],
    "max_content_length": 32768,

    # User experience
    "no_results_message": "I couldn't find information about '{query}' in our documentation. Please rephrase or try a different question.",
    "response_format_callback": self._custom_formatter,

    # SWAIG configuration
    "swaig_fields": {
        "fillers": {
            "en-US": [
                "Let me search the documentation...",
                "I'm looking through our knowledge base...",
                "Searching for that information...",
                "Let me check the docs..."
            ]
        }
    }
})
```

### Similarity Threshold Guidelines

The `similarity_threshold` parameter controls how similar a chunk must be to the query to be included in results. Higher values are stricter; lower values are more permissive.

| Content Type | Recommended Threshold | Notes |
|--------------|----------------------|-------|
| Technical documentation | 0.5 | Balanced precision/recall |
| FAQ content | 0.4 | Moderate matching |
| Creative content | 0.3 | Broader matching |
| Exact lookups | 0.7 | Strict matching |
| Code examples | 0.5 | With markdown strategy |
| General knowledge | 0.4 | Permissive |

### Result Count Guidelines

The `count` parameter controls how many results are returned to the LLM.

| Use Case | Recommended Count | Notes |
|----------|------------------|-------|
| Specific questions | 3 | Focused answer |
| Exploratory questions | 5 | Balanced coverage |
| Research queries | 7-10 | Comprehensive |
| Voice agents | 3 | Concise for speech |
| Chat agents | 5 | Detailed for text |

### Max Content Length

The `max_content_length` parameter limits the total characters returned across all results.

| Agent Type | Recommended Length | Notes |
|------------|-------------------|-------|
| Voice agents | 16384 (16KB) | Faster, focused |
| Chat agents | 32768 (32KB) | Default, balanced |
| Complex queries | 65536 (64KB) | Comprehensive |
| Serverless | 16384 (16KB) | Minimize payload size |
