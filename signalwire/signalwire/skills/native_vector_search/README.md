# Native Vector Search Skill

The Native Vector Search skill provides document search capabilities using vector similarity and keyword search. It supports multiple storage backends including SQLite (local files) and PostgreSQL with pgvector extension.

## Features

- **Hybrid Search**: Combines vector similarity and keyword search for better results
- **Multiple Backends**: SQLite for local deployment, pgvector for scalable production use
- **Remote Search**: Connect to remote search servers
- **Auto-indexing**: Automatically build indexes from source directories
- **NLP Enhancement**: Query expansion and synonym matching
- **Tag Filtering**: Filter results by document tags

## Backends

### SQLite Backend (Default)
- Stores indexes in `.swsearch` files
- Good for single-agent deployments
- Portable and self-contained
- No external dependencies

### pgvector Backend
- Uses PostgreSQL with pgvector extension
- Scalable for multi-agent deployments
- Real-time updates capability
- Efficient similarity search with specialized indexes

### Remote Search Server
- Connect to centralized search API
- Lower memory usage per agent
- Shared knowledge base

## Configuration Parameters

### Basic Parameters
- `tool_name`: Name of the search tool (default: "search_knowledge")
- `description`: Tool description for the AI
- `count`: Number of results to return (default: 5)
- `distance_threshold`: Minimum similarity score (default: 0.0)
- `tags`: Filter results by these tags

### Backend Selection
- `backend`: Storage backend - "sqlite" or "pgvector" (default: "sqlite")

### SQLite Backend
- `index_file`: Path to .swsearch index file
- `build_index`: Auto-build index from source (default: false)
- `source_dir`: Directory to index if build_index=true

### pgvector Backend
- `connection_string`: PostgreSQL connection string (required)
- `collection_name`: Name of the collection to search (required)

### Remote Backend
- `remote_url`: URL of remote search server
- `index_name`: Name of index on remote server

### Response Formatting
- `response_prefix`: Text to prepend to results
- `response_postfix`: Text to append to results
- `no_results_message`: Message when no results found

### NLP Configuration
- `query_nlp_backend`: NLP backend for queries ("nltk" or "spacy")
- `index_nlp_backend`: NLP backend for indexing ("nltk" or "spacy")

## Usage Examples

### SQLite Backend (Local File)
```python
agent.add_skill("native_vector_search", {
    "tool_name": "search_docs",
    "description": "Search technical documentation",
    "index_file": "docs.swsearch",
    "count": 5
})
```

### pgvector Backend (PostgreSQL)
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
```python
agent.add_skill("native_vector_search", {
    "tool_name": "search_api",
    "description": "Search API documentation",
    "remote_url": "http://search-server:8001",
    "index_name": "api_docs"
})
```

### Auto-build Index
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
```bash
pip install signalwire-agents[search]
```

### For pgvector Backend
```bash
pip install signalwire-agents[search,pgvector]
```

### For All Features
```bash
pip install signalwire-agents[search-all]
```

## Building Indexes

### Using sw-search CLI

#### SQLite Backend
```bash
sw-search ./docs --output docs.swsearch
```

#### pgvector Backend
```bash
sw-search ./docs \
  --backend pgvector \
  --connection-string "postgresql://localhost/knowledge" \
  --output docs_collection
```

## Performance Considerations

### SQLite
- Fast for small to medium datasets (<100k documents)
- Linear search for vector similarity
- Single-file deployment

### pgvector
- Efficient for large datasets
- Uses IVFFlat or HNSW indexes
- Handles concurrent access well
- Requires PostgreSQL server

### NLP Backends
- `nltk`: Fast, good for most use cases (~50-100ms)
- `spacy`: Better quality, slower (~150-300ms)

## Environment Variables

None required - all configuration comes through skill parameters.

## Troubleshooting

### "Search dependencies not available"
Install the search extras:
```bash
pip install signalwire-agents[search]
```

### "pgvector dependencies not available"
Install pgvector support:
```bash
pip install signalwire-agents[pgvector]
```

### "Failed to connect to pgvector"
1. Ensure PostgreSQL is running
2. Check connection string
3. Verify pgvector extension is installed
4. Check collection exists

### Poor Search Results
1. Try different NLP backends
2. Adjust distance_threshold
3. Check document preprocessing
4. Verify index quality