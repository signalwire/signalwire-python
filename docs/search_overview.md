# Search System Overview

The SignalWire Agents SDK includes a local search system that provides Retrieval-Augmented Generation (RAG) capabilities without external dependencies. The system uses local embeddings, hybrid search techniques, and portable `.swsearch` index files to enable agents to search through document collections. This document consolidates the foundational concepts, installation, architecture, and usage of the search system.

For related documentation, see:

- [Search Indexing](search_indexing.md) - Building indexes, chunking strategies, embeddings
- [Search Integration](search_integration.md) - Agent integration, skills, and API usage
- [Search Deployment](search_deployment.md) - Production deployment, pgvector, scaling
- [Search Troubleshooting](search_troubleshooting.md) - Common issues and solutions

---

## What Is the Search System

### The Problem: Hallucinations and RAG

Large language models are trained on vast amounts of internet text, but they have no knowledge of your specific documentation, internal knowledge bases, or product details. When asked questions outside their training data, they do not say "I don't know." Instead, they generate plausible-sounding answers that are often completely fictional.

For AI agents representing a business, this is unacceptable. The agent needs to answer questions accurately based on actual documentation, not fabricate answers.

**Retrieval-Augmented Generation (RAG)** solves this problem:

1. When a user asks a question, search the knowledge base for relevant information.
2. Include that information in the prompt to the LLM.
3. Instruct the LLM to answer based on the retrieved information.

Instead of relying on the model's training data, the LLM becomes a natural language interface to a knowledge base.

Most RAG implementations require setting up a separate vector database (Pinecone, Weaviate, Qdrant, etc.) and writing embedding management code. They also mean handling retrieval logic, paying for additional infrastructure, and absorbing latency from multiple service calls. The SignalWire Agents SDK search system eliminates these requirements by integrating search directly into the agent framework.

### How It Works: Architecture

Documents flow into a portable index at build time, and agents query that index at runtime:

```
+-------------------+    +------------------+    +-------------------+
|   Documents       |--->|   Index Builder   |--->|  .swsearch DB     |
| (MD, PDF, etc.)   |    |                  |    |                   |
+-------------------+    +------------------+    +-------------------+
                                                          |
                                                          v
+-------------------+    +------------------+    +-------------------+
|     Agent         |--->|  Search Skill    |--->|  Search Engine    |
|                   |    |                  |    |                   |
+-------------------+    +------------------+    +-------------------+
```

**Indexing phase:** Documents are processed by the `IndexBuilder`, which scans files, extracts text, and breaks content into chunks. It then generates vector embeddings for each chunk and saves everything into a portable `.swsearch` SQLite database.

**Query phase:** At runtime, an agent equipped with the `native_vector_search` skill sends user queries through the `SearchEngine`. The engine converts the query to a vector embedding and compares it against all stored chunk vectors. It applies hybrid scoring (vector similarity, keyword matching, and metadata filtering) to return ranked results, and the LLM uses those results to generate an accurate response.

### Key Features

The search system provides these capabilities:

- **Offline search**: No external API calls or internet required at query time.
- **Hybrid search**: Combines vector similarity and keyword search with metadata filtering.
- **Document processing**: Supports Markdown, PDF, DOCX, HTML, Excel, PowerPoint, and more.
- **Smart chunking**: Nine chunking strategies including markdown-aware and semantic chunking.
- **Advanced query processing**: Optional NLP-enhanced query understanding with synonym expansion.
- **Flexible deployment**: Local embedded mode with `.swsearch` files, remote server mode, or PostgreSQL pgvector backend.
- **Portable indexes**: A single `.swsearch` file contains the entire knowledge base (embeddings, metadata, full-text index).
- **Voice-optimized**: Automatic response formatting adapted for voice conversations vs. text chat.
- **Production-ready backends**: Start with SQLite for development, scale to pgvector for multi-agent production systems.

---

## Installation

The search system uses optional dependencies to keep the base SDK lightweight. Choose the installation option that matches your use case.

### Installation Options

#### Basic Search (~500MB)

Install this level with pip:

```bash
pip install "signalwire-sdk[search]"
```

Includes core search functionality with sentence-transformers for embeddings, scikit-learn, NLTK, numpy, and SQLite FTS5 for keyword search. Supports text and markdown files.

Best for: Local development, CI/CD, resource-constrained environments.

#### Full Document Processing (~600MB)

Install this level with pip:

```bash
pip install "signalwire-sdk[search-full]"
```

Adds PDF processing (pdfplumber), DOCX processing (python-docx), Excel/PowerPoint (openpyxl, python-pptx), HTML processing (BeautifulSoup4), and additional file format support (markdown, striprtf, python-magic).

Best for: Production systems that need document processing but prioritize speed.

#### Advanced NLP (~600MB)

Install this level with pip:

```bash
pip install "signalwire-sdk[search-nlp]"
```

Adds spaCy for advanced text processing, improved POS tagging, named entity recognition, and enhanced query preprocessing.

**Additional setup required:**

```bash
python -m spacy download en_core_web_sm
```

**Performance note:** Advanced NLP features improve query understanding and synonym expansion, but they're slower than basic search. Two NLP backends are available:

- **NLTK (default):** faster query processing, good for most use cases.
- **spaCy:** slower query processing, better POS tagging and entity recognition, requires model download.

Configure via the `index_nlp_backend` and `query_nlp_backend` parameters, which both default to `nltk`:

```python
self.add_skill("native_vector_search", {
    "index_nlp_backend": "nltk",   # Fast, default
    "query_nlp_backend": "nltk"
})

self.add_skill("native_vector_search", {
    "index_nlp_backend": "spacy",  # Better quality, slower
    "query_nlp_backend": "spacy"
})
```

An older, single `nlp_backend` parameter still works but is deprecated in favor of these two separate parameters.

Best for: Applications where search quality is more important than speed.

#### All Search Features (~700MB)

Install this level with pip:

```bash
pip install "signalwire-sdk[search-all]"
```

Includes the packages from the options described earlier, plus pgvector support for PostgreSQL backends.

**Additional setup required:**

```bash
python -m spacy download en_core_web_sm
```

Best for: Full-featured applications with dedicated hardware.

### search-queryonly: Production Deployments

For production deployments where agents only need to query existing indexes (not build them):

```bash
pip install "signalwire-sdk[search-queryonly]"
```

**Size:** ~400MB, significantly smaller because it excludes the ML models needed to build indexes.

This option is designed for deploying agents in environments such as Lambda functions, Docker containers, or edge devices. The `.swsearch` index file is pre-built and shipped alongside the agent.

### Feature Comparison Table

| Feature | search | search-full | search-nlp | search-all | pgvector |
|---------|--------|-------------|------------|------------|----------|
| Vector embeddings | Yes | Yes | Yes | Yes | No |
| Keyword search (FTS5) | Yes | Yes | Yes | Yes | No |
| Text files (txt, md) | Yes | Yes | Yes | Yes | No |
| PDF processing | No | Yes | No | Yes | No |
| DOCX processing | No | Yes | No | Yes | No |
| Excel/PowerPoint | No | Yes | No | Yes | No |
| Advanced NLP (spaCy) | No | No | Yes | Yes | No |
| POS tagging | No | No | Yes | Yes | No |
| Named entity recognition | No | No | Yes | Yes | No |
| PostgreSQL support | No | No | No | Yes | Yes |
| Scalable vector search | No | No | No | Yes | Yes |
| Approximate size | ~500MB | ~600MB | ~600MB | ~700MB | varies |

pgvector support can also be installed independently:

```bash
pip install "signalwire-sdk[pgvector]"

# Or combined with search:
pip install "signalwire-sdk[search,pgvector]"
```

### Verifying Installation

Run this check to confirm the search package imported correctly:

```python
try:
    from signalwire.search import IndexBuilder, SearchEngine
    print("Search functionality is available")
except ImportError as e:
    print(f"Search not available: {e}")
    print("Install with: pip install signalwire-sdk[search]")
```

Common installation issues:

| Error | Solution |
|-------|----------|
| `No module named 'sentence_transformers'` | `pip install signalwire-sdk[search]` |
| `No module named 'pdfplumber'` | `pip install signalwire-sdk[search-full]` |
| NLTK data not found | `import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')` |
| spaCy model not found | `python -m spacy download en_core_web_sm` |

Note: The sentence-transformers library downloads pre-trained models (~400MB) on first use. This is cached locally after the initial download.

---

## Core Concepts

### Vector Embeddings

An embedding is a list of numbers (a vector) that represents the semantic meaning of a piece of text. Embeddings function as coordinates in a high-dimensional meaning space. Texts with similar meanings produce vectors that are close together, while unrelated texts produce vectors that are far apart.

Simplified example (real embeddings have hundreds of dimensions):

```
"How do I make a phone call?"     -> [0.2, 0.8, 0.1, ...]
"Initiating voice connections"    -> [0.3, 0.7, 0.2, ...]
"Pizza recipes"                    -> [0.9, 0.1, 0.8, ...]
```

The first two texts are close together in vector space (similar meanings), while the third is far away (different topic).

The embedding models used by the search system (such as `sentence-transformers/all-MiniLM-L6-v2`) are neural networks trained on large text corpora to learn semantic relationships. They understand that:

- "car" and "automobile" are synonyms
- "doctor" is related to "hospital" and "medicine"
- Context matters: "Python" can mean a snake or a programming language

During indexing, the model reads each chunk of text and processes it through the neural network. It outputs a vector (typically 384 or 768 numbers) and stores that vector alongside the original text. At query time, the same model converts the user's query into a vector and compares it to all stored chunk vectors.

**Available models:**

| Model | Dimensions | Speed | Quality | Notes |
|-------|-----------|-------|---------|-------|
| MiniLM ("mini", default) | 384 | Faster | Good for most use cases | Lower memory usage |
| MPNet ("base") | 768 | Slower | Better for complex queries | Previous default |

For detailed model comparisons and embedding strategies, see [Search Indexing](search_indexing.md).

### Semantic vs Keyword Search

Traditional keyword search looks for exact word matches. If documentation says "initiating voice connections" and a user asks "how do I make a phone call", keyword search finds nothing: not a single word matches.

Vector search finds it immediately because the meaning is similar. It understands that:

- "change" is approximately equivalent to "configuring" and "setting"
- "AI's voice" is approximately equivalent to "voice model"
- "speech settings" is approximately equivalent to "speech characteristics"

However, keyword search still matters for exact terms:

- Model names: "gpt-4o-mini" vs "GPT-4"
- API endpoints: "/api/v2/users" vs "/api/users"
- Error codes: "ERROR_404" vs "ERROR_500"
- Programming identifiers: `set_params()` vs `get_params()`

The search system combines both approaches (hybrid search) to handle semantic similarity and exact term matching.

### Cosine Similarity and Distance Threshold

The comparison between query vectors and chunk vectors uses **cosine similarity**, which measures the angle between two vectors. Vectors pointing in the same direction (similar meanings) have high similarity (close to 1.0), while vectors pointing in different directions have low similarity (close to 0.0).

```
Query: "how to handle errors"
Chunk A: "error handling guide"     -> similarity: 0.87 (very similar)
Chunk B: "installation instructions" -> similarity: 0.23 (not similar)
```

The `similarity_threshold` parameter (`--similarity-threshold` on the `sw-search` command line, or its older name, `--distance-threshold`) filters out low-similarity results. Only chunks with a score at or above the threshold are returned, so a higher threshold is stricter and a lower threshold is more permissive:

<!-- snippet: no-compile config-excerpt -->
```python
"similarity_threshold": 0.3  # Permissive - includes loosely related content
"similarity_threshold": 0.5  # Balanced - good matches
"similarity_threshold": 0.7  # Strict - only near-perfect matches
```

For precise, technical lookups, 0.6-0.7 is a good starting point. For creative content or broad topics, 0.3-0.4 may be more appropriate, since it admits more loosely related content. Too strict yields no results; too permissive yields irrelevant results.

Once embeddings are generated, search is extremely fast: comparing vectors is basic arithmetic (multiply and add operations). Modern CPUs can compare thousands of vectors per millisecond. The expensive embedding generation happens once during indexing; queries are cheap.

### Hybrid Search Algorithm

The search system implements a **vector-first** hybrid search algorithm. It combines vector similarity, keyword matching, and metadata filtering to produce higher-quality results than any single approach alone.

#### Vector-First Architecture

Many RAG systems use a keyword-first approach: try keyword search first, fall back to vector search if it fails. This treats vector search as a backup and misses semantically relevant content that lacks keyword matches.

The SignalWire search system takes the opposite approach:

1. **Always run vector search** as the primary signal.
2. **Run keyword, metadata, and filename matching in parallel** (not conditionally).
3. **Use agreement between signals as a tiebreaker**, not as an independent score.
4. **Return the best combined results.**

Vector search drives the results. Keyword, metadata, and filename matches can reorder candidates that are already close to each other. They cannot pull a weak semantic match above a strong one.

#### The Confirmation Principle

The core insight of hybrid search is **confirmation**: when multiple independent signals agree that a chunk is relevant, confidence in that result increases.

- Vector search is one signal: "This seems semantically related."
- Keyword search is another: "It contains the exact terms."
- Metadata is a third: "It is tagged as relevant."

When several signals agree, the result is more strongly confirmed, though agreement can only move a result within a narrow band. It cannot move a result past a chunk that is closer to the query.

#### Scoring Mechanics

The algorithm proceeds in these steps:

1. Vector search fetches a candidate pool of roughly three times the requested result count, so the later steps have room to work.
2. Keyword matching, weighted metadata field matching (category, product, tags, source, section, and description each carry a different weight), and filename matching run against that same pool.
3. Each candidate is scored. If it has a vector similarity score, that score is the base, and every additional agreeing signal adds a small boost, capped at a fixed maximum. Agreement can reorder near-ties; it cannot let a weak vector match outrank a stronger one.
4. A candidate found only through keyword or metadata matching, with no vector score, is scaled below the pool's strongest vector match. A non-semantic match can never outrank a genuine semantic one.
5. Near-duplicate chunks are removed, keeping the highest-scoring copy of each.
6. Results are penalized when several chunks come from the same file, so one document cannot dominate the result list. The second chunk from a file keeps 85% of its computed score, the third 70%, the fourth 50%, and the fifth or later 40%.
7. The top N results are returned.

**Concrete example:**

Consider a query for "how to configure voice settings":

```
Chunk A: vector similarity 0.78, also matched by keyword and metadata search
  Two agreeing signals add the maximum tiebreak bonus: 0.78 + 0.05 = 0.83

Chunk B: vector similarity 0.82, no keyword or metadata match
  No agreeing signals to add: 0.82

Chunk A now ranks ahead of Chunk B, because the two started as a near-tie.
A weaker vector match, for example 0.60, could not have passed Chunk B this way.
```

The exact boost values are internal and may change between releases. For tuning search quality, what matters is this: a strong vector match keeps its rank regardless of keyword or metadata agreement. The `count` parameter also affects how much room the candidate pool has, since the system searches for about 3x the requested count before scoring.

---

## Quick Start

### Building Your First Index

Use the `sw-search` CLI tool to create a `.swsearch` index file from your documents:

```bash
# Build from a directory of documentation
sw-search ./docs --output knowledge.swsearch

# Build from specific files
sw-search README.md docs/agent_guide.md docs/architecture.md --output knowledge.swsearch

# Build from mixed sources (files and directories) with file type filtering
sw-search docs/ examples/ README.md --file-types md,py,txt --output comprehensive.swsearch

# Include verbose output to see progress
sw-search ./docs --output knowledge.swsearch --verbose
```

The `sw-search` command will:

1. Recursively scan the specified sources.
2. Extract text from supported file types (markdown, txt, etc.).
3. Break the content into chunks.
4. Generate vector embeddings for each chunk.
5. Save everything to the output `.swsearch` file.

Example output:

```
Added 3 files from directory: docs
Found 3 files to process
Processing 3 files...
  docs/getting-started.md: 3 chunks
  docs/api-reference.md: 12 chunks
  docs/examples.md: 5 chunks
Created 20 total chunks
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Generating embeddings for 20 chunks...
  Progress: 20/20 chunks (100.0%)
Index created: knowledge.swsearch
Total chunks: 20

Search index created successfully: knowledge.swsearch
```

For full CLI reference, see [CLI Guide](cli_guide.md). For advanced indexing options (chunking strategies, model selection, pgvector backend), see [Search Indexing](search_indexing.md).

### Querying from an Agent

Add the `native_vector_search` skill to any agent to enable search:

<!-- snippet: no-run starts a blocking server/client (covered by SNIPPET-COMPILE + EXAMPLES-RUN) -->
```python
#!/usr/bin/env python3
import os
from signalwire import AgentBase

class DocsAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="DocsAgent",
            route="/docs",
            port=3000
        )

        # Add search capability pointing to a local .swsearch file
        self.add_skill("native_vector_search", {
            "tool_name": "search_docs",
            "description": "Search the documentation to answer user questions about features, APIs, and how-to guides",
            "index_file": "./knowledge.swsearch",
            "count": 5,
            "similarity_threshold": 0.4,
            "no_results_message": "I couldn't find information about '{query}' in the documentation. Could you rephrase your question?",
            "swaig_fields": {
                "fillers": {
                    "en-US": [
                        "Let me search the documentation for that...",
                        "Searching for information..."
                    ]
                }
            }
        })

        # Build the prompt
        self.prompt_add_section(
            "Your Role",
            bullets=[
                "You are a helpful documentation assistant.",
                "Always use search_docs to find information before answering technical questions.",
                "Base your answers on the search results, not general knowledge.",
                "If the search returns no results, admit you don't have that information."
            ]
        )

        self.add_language(
            name="English",
            code="en-US",
            voice="elevenlabs.adam"
        )

if __name__ == "__main__":
    agent = DocsAgent()
    print(f"Agent running at: {agent.get_full_url()}")
    agent.run()
```

When a user asks a question, the following occurs:

1. The query is converted to a vector embedding.
2. The search engine compares the query vector to all chunk vectors in the index.
3. Chunks are scored by cosine similarity.
4. Keyword and metadata matches boost scores (hybrid scoring).
5. Top results (above the distance threshold) are returned.
6. Results are formatted and provided to the LLM.
7. The LLM generates an answer grounded in the retrieved content.

### Testing Your Search

Use the `swaig-test` CLI to verify search functionality without running the full agent:

```bash
# List available tools
swaig-test docs_agent.py --list-tools
# Output: search_docs

# Execute a test search
swaig-test docs_agent.py --exec search_docs --query "how do I create an agent"
```

You can also test the index directly from the command line:

```bash
# Search within an index file
sw-search search knowledge.swsearch "how to create an agent"

# Search with options
sw-search search knowledge.swsearch "API reference" --count 3 --verbose

# JSON output for scripting
sw-search search knowledge.swsearch "error handling" --json | jq '.results[0].content'

# Validate index integrity and view statistics
sw-search validate knowledge.swsearch --verbose
```

---

## Comparison to Alternatives

### vs OpenAI Assistants

OpenAI Assistants provide a hosted file-search solution where documents are uploaded to OpenAI and everything is managed:

<!-- snippet: no-run requires optional third-party package `openai` -->
```python
from openai import OpenAI
client = OpenAI()

file = client.files.create(file=open("knowledge.pdf", "rb"), purpose="assistants")
assistant = client.beta.assistants.create(
    name="My Assistant",
    instructions="You are a helpful assistant",
    tools=[{"type": "file_search"}],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)
```

**Advantages of OpenAI Assistants:** Zero setup, managed infrastructure, automatic improvements.

**Disadvantages:** Vendor lock-in (OpenAI models only), no control over chunking or search tuning, and data privacy concerns, since documents reside on OpenAI servers. Latency is higher (multiple API round-trips), and the cost for search infrastructure is higher too, since it includes OpenAI's vector storage and inference charges. `.swsearch` files need no separate database server, and pgvector costs only what your own PostgreSQL hosting costs.

### vs LangChain + External Vector DB

LangChain combined with a managed vector database (Pinecone, Weaviate, Qdrant) provides a flexible but complex approach:

<!-- snippet: no-run requires optional third-party package `langchain` -->
```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pinecone

pinecone.init(api_key="...", environment="...")
loader = DirectoryLoader('./docs')
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
chunks = text_splitter.split_documents(documents)
embeddings = OpenAIEmbeddings()
vectorstore = Pinecone.from_documents(chunks, embeddings, index_name="knowledge")
results = vectorstore.similarity_search(query, k=5)
```

**Equivalent SignalWire approach:**

```python
agent.add_skill("native_vector_search", {
    "tool_name": "search_docs",
    "index_file": "./knowledge.swsearch"
})
# Agent automatically handles retrieval, formatting, and prompt integration
```

**Advantages of LangChain + VectorDB:** Highly flexible, large community, many integrations.

**Disadvantages:** Complex setup with many moving parts, and it requires a paid subscription to a managed vector database such as Pinecone. Network calls to external services add latency, and retrieval and the agent need manual integration code between them.

### vs DIY Approach

Building a custom solution with an embedding API (OpenAI, Cohere) and custom search logic:

<!-- snippet: no-run requires optional third-party package `openai` -->
```python
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Generate embeddings (per-call API cost)
doc_embeddings = []
for doc in documents:
    response = openai.Embedding.create(input=doc, model="text-embedding-3-small")
    doc_embeddings.append(response['data'][0]['embedding'])

# Manual storage, retrieval, ranking...
similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
top_k = np.argsort(similarities)[-5:][::-1]
```

**Advantages of DIY:** Full control over every aspect, minimal dependencies, good for learning.

**Disadvantages:** A longer development time than using the SDK, and an ongoing maintenance burden. Embeddings carry a per-call API cost, and optimizations like hybrid search and metadata boosting are missing.

Building a DIY solution means writing and testing your own document loading, chunking, embedding generation, storage layer, search implementation, hybrid search, and metadata filtering. The SignalWire SDK includes all of these, with nine chunking strategies built in, configured through the `add_skill` call shown earlier.

### Feature Matrix

| Feature | OpenAI Assistants | LangChain + VectorDB | DIY | SignalWire SDK |
|---------|-------------------|----------------------|-----|----------------|
| **Chunking Control** | No | Yes | Yes | Yes (9 strategies) |
| **Hybrid Search** | Unknown | Manual | Manual | Built-in |
| **Metadata Filtering** | Limited | Yes | Manual | Yes |
| **Vendor Lock-in** | High | Moderate | None | None |
| **Offline Operation** | No | No | Possible | Yes (.swsearch) |
| **Voice Optimized** | No | No | No | Yes |
| **Agent Integration** | Manual | Manual | Manual | Automatic |
| **Deployment Size** | N/A | Large | Medium | Small (query-only) |
| **LLM Choice** | OpenAI only | Any | Any | Any |
| **Data Privacy** | OpenAI servers | 3rd party | Your infra | Your infra |
| **Scalability** | Auto | Managed | DIY | pgvector |

Setup time, cost, and query latency all depend on your query volume, hosting choices, and hardware. See the sections earlier on this page for what each approach involves, and measure the ones that matter to you in your own environment.
