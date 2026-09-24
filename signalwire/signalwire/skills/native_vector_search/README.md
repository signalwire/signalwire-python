# Native Vector Search Skill

The Native Vector Search skill provides document search capabilities using vector similarity and keyword search. It supports multiple storage backends including SQLite (local files) and PostgreSQL with pgvector extension.

## Features

The skill covers these capabilities:

- **Hybrid Search**: Combines vector similarity and keyword search for better results
- **Multiple Backends**: SQLite for local deployment, pgvector for scalable production use
- **Remote Search**: Connect to remote search servers
- **Auto-indexing**: Automatically build indexes from source directories
- **NLP Enhancement**: Query expansion and synonym matching
- **Tag Filtering**: Filter results by document tags

## Backends

### SQLite Backend (Default)

The default backend needs no external services:

- Stores indexes in `.swsearch` files
- Good for single-agent deployments
- Portable and self-contained
- No external dependencies

### pgvector Backend

Choose this backend for a shared, multi-agent index:

- Uses PostgreSQL with pgvector extension
- Scalable for multi-agent deployments
- Real-time updates capability
- Efficient similarity search with specialized indexes

### Remote Search Server

Point the skill at a search server instead of a local index:

- Connect to centralized search API
- Lower memory usage per agent
- Shared knowledge base

## Configuration Parameters

### Basic Parameters

These parameters apply regardless of backend:

- `tool_name`: Name of the search tool (default: "search_knowledge")
- `description`: Tool description for the AI
- `count`: Number of results to return (default: 5)
- `similarity_threshold`: Minimum similarity score (default: 0.0)
- `tags`: Filter results by these tags

### Backend Selection

One parameter chooses between the local backends:

- `backend`: Storage backend - "sqlite" or "pgvector" (default: "sqlite")

### SQLite Backend

These parameters apply when `backend` is "sqlite":

- `index_file`: Path to .swsearch index file
- `build_index`: Auto-build index from source (default: false)
- `source_dir`: Directory to index if build_index=true

### pgvector Backend

These parameters apply when `backend` is "pgvector":

- `connection_string`: PostgreSQL connection string (required)
- `collection_name`: Name of the collection to search (required)

### Remote Backend

These parameters apply when `remote_url` is set:

- `remote_url`: URL of remote search server
- `index_name`: Name of index on remote server

### Response Formatting

These parameters shape the text the tool returns:

- `response_prefix`: Text to prepend to results
- `response_postfix`: Text to append to results
- `no_results_message`: Message when no results found

### NLP Configuration

These parameters control query expansion and indexing:

- `query_nlp_backend`: NLP backend for queries ("nltk" or "spacy")
- `index_nlp_backend`: NLP backend for indexing ("nltk" or "spacy")

## Usage Examples

### SQLite Backend (Local File)

Point `index_file` at a local `.swsearch` index:

```python
agent.add_skill("native_vector_search", {
    "tool_name": "search_docs",
    "description": "Search technical documentation",
    "index_file": "docs.swsearch",
    "count": 5
})
```

### pgvector Backend (PostgreSQL)

Set `backend` to "pgvector" and provide a connection string and collection name:

```python
agent.add_skill("native_vector_search", {
    "tool_name": "search_knowledge",
    "description": "Search the knowledge base",
    "backend": "pgvector",
    "connection_string": "postgresql://user:pass@localhost:5432/knowledge",
    "collection_name": "docs_collection",
    "count": 5
})
```

### Remote Search Server

Set `remote_url` to search a remote server instead of a local index:

```python
agent.add_skill("native_vector_search", {
    "tool_name": "search_api",
    "description": "Search API documentation",
    "remote_url": "http://search-server:8001",
    "index_name": "api_docs"
})
```

### Auto-build Index

Set `build_index` to build a `.swsearch` file from a source directory the first time the agent starts:

```python
agent.add_skill("native_vector_search", {
    "tool_name": "search_local",
    "build_index": True,
    "source_dir": "./documentation",
    "file_types": ["md", "txt"],
    "index_file": "auto_docs.swsearch"
})
```

### Multiple Search Instances

Each call to `add_skill` with a distinct `tool_name` registers a separate search tool:

```python
# Documentation search
agent.add_skill("native_vector_search", {
    "tool_name": "search_docs",
    "index_file": "docs.swsearch",
    "description": "Search documentation"
})

# Code examples search
agent.add_skill("native_vector_search", {
    "tool_name": "search_examples",
    "backend": "pgvector",
    "connection_string": "postgresql://localhost/knowledge",
    "collection_name": "examples",
    "description": "Search code examples"
})
```

## Installation

### For SQLite Backend

Install the `search` extra:

```bash
pip install signalwire-sdk[search]
```

### For pgvector Backend

Install the `search` and `pgvector` extras together:

```bash
pip install signalwire-sdk[search,pgvector]
```

### For All Features

Install every search-related extra, including spaCy and document processing:

```bash
pip install signalwire-sdk[search-all]
```

## Building Indexes

### Using sw-search CLI

#### SQLite Backend

Build a local `.swsearch` file from a directory of documents:

```bash
sw-search ./docs --output docs.swsearch
```

#### pgvector Backend

Build directly into a PostgreSQL collection instead of a local file:

```bash
sw-search ./docs \
  --backend pgvector \
  --connection-string "postgresql://localhost/knowledge" \
  --output docs_collection
```

## Performance Considerations

### SQLite

The SQLite backend suits smaller collections:

- Fast for small to medium datasets
- Linear search for vector similarity
- Single-file deployment

### pgvector

The pgvector backend suits larger, shared collections:

- Efficient for large datasets
- New collections use an HNSW index; collections built earlier with IVFFlat still work
- Handles concurrent access well
- Requires PostgreSQL server

### NLP Backends

The two NLP backends trade speed for quality:

- `nltk`: Fast, good for most use cases
- `spacy`: Better quality, slower

## Environment Variables

None required - all configuration comes through skill parameters.

## Troubleshooting

### "Search dependencies not available"
Install the search extras:
```bash
pip install signalwire-sdk[search]
```

### "pgvector dependencies not available"
Install pgvector support:
```bash
pip install signalwire-sdk[pgvector]
```

### "Failed to connect to pgvector"

Work through these checks in order:

1. Ensure PostgreSQL is running
2. Check connection string
3. Verify pgvector extension is installed
4. Check collection exists

### Poor Search Results

Try these adjustments in order:

1. Try different NLP backends
2. Adjust `similarity_threshold`
3. Check document preprocessing
4. Verify index quality