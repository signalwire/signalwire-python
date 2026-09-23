# Search Deployment Guide

This document covers storage backends, deployment patterns, migration procedures, performance optimization, and production architecture for the SignalWire Agents SDK search system. For an overview of the search system itself, see [search_overview.md](search_overview.md). For indexing details, see [search_indexing.md](search_indexing.md). For agent integration, see [search_integration.md](search_integration.md). For troubleshooting, see [search_troubleshooting.md](search_troubleshooting.md).

---

## Storage Backends

The SDK supports two storage backends for search indexes: SQLite (via `.swsearch` files) and PostgreSQL with the pgvector extension.

### SQLite (.swsearch Files)

#### How It Works

A `.swsearch` file is a SQLite database containing:

- Vector embeddings for all chunks
- Original text content
- Metadata and tags
- Search configuration
- Model information
- Full-text search index (SQLite FTS5)
- Synonym cache for query expansion

Everything resides in a single portable file:

```bash
ls -lh knowledge.swsearch
# -rw-r--r--  1 user  staff   2.3M  knowledge.swsearch
```

Deploy it alongside your agent, and search works immediately with no external services.

#### Advantages and Limitations

**Advantages:**

- **Portability**: A single file contains the entire knowledge base. Copy it to any machine and it works immediately, with no database setup and no connection strings.
- **Simplicity**: No external dependencies. SQLite is embedded, with no PostgreSQL installation, no connection pooling, no authentication, and no network calls.
- **Version control**: Treat knowledge bases like code artifacts, with different versions for different environments, such as staging and production.
- **Fast for single users**: SQLite is optimized for single-user access, with low latency and no network overhead.
- **Serverless-friendly**: Package the `.swsearch` file directly with AWS Lambda, Google Cloud Functions, or Azure Functions deployments.

**Limitations:**

- **No concurrent writes**: SQLite does not handle multiple writers well. One agent writing works fine, but multiple agents trying to update the same index cause contention. Read-only access by multiple agents is fine.
- **No live updates**: Updating the index requires rebuilding the entire file. Incremental append is not supported.
- **File size constraints**: Practical limits exist for large datasets:
  - 1M chunks: ~500MB file (manageable)
  - 10M chunks: ~5GB file (getting large)
  - 100M+ chunks: consider pgvector
- **No multi-collection management**: One file equals one collection. Multiple knowledge bases require multiple files, each loaded separately.

### pgvector (PostgreSQL)

#### What Is pgvector

pgvector is a PostgreSQL extension that adds vector data types and similarity search capabilities. It turns PostgreSQL into a vector database:

```sql
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(384),
    metadata JSONB
);

CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);
```

Prerequisites:

1. PostgreSQL 12+ with pgvector extension
2. Python packages: `pip install psycopg2-binary pgvector`
3. Docker (optional, to run PostgreSQL in a container)

#### Setup with Docker

Docker starts PostgreSQL with the pgvector extension already installed:

```bash
# Start PostgreSQL with pgvector
docker run -d \
  --name pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Create database and enable extension
docker exec -it pgvector psql -U postgres -c "CREATE DATABASE knowledge;"
docker exec -it pgvector psql -U postgres -d knowledge -c "CREATE EXTENSION vector;"
```

For systems without Docker, the pgvector project's [installation instructions](https://github.com/pgvector/pgvector#installation) cover each platform and PostgreSQL version. On common systems, the commands are:

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgresql-15-pgvector

# macOS with Homebrew
brew install postgresql pgvector

# Start PostgreSQL
sudo systemctl start postgresql
```

Then create the database:

```sql
CREATE DATABASE knowledge;
\c knowledge
CREATE EXTENSION vector;
```

#### Connection Configuration

Build connection strings from environment variables for production:

```python
import os

pg_user = os.getenv("PGVECTOR_DB_USER", "signalwire")
pg_pass = os.getenv("PGVECTOR_DB_PASSWORD", "password")
pg_host = os.getenv("PGVECTOR_HOST", "localhost")
pg_port = os.getenv("PGVECTOR_PORT", "5432")
pg_db = os.getenv("PGVECTOR_DB_NAME", "knowledge")

connection_string = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
```

Or use a single environment variable:

```bash
export PGVECTOR_CONNECTION="postgresql://user:pass@host:port/database"
```

#### Database Schema

pgvector creates the following tables for each collection:

```sql
-- Main chunks table
CREATE TABLE chunks_<collection_name> (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    processed_content TEXT,
    embedding vector(384),  -- or 768 depending on model
    filename TEXT,
    section TEXT,
    tags JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    metadata_text TEXT,  -- Searchable text representation of all metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configuration table (shared across collections)
CREATE TABLE collection_config (
    collection_name TEXT PRIMARY KEY,
    model_name TEXT,
    embedding_dimensions INTEGER,
    chunking_strategy TEXT,
    languages JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

The `metadata_text` field contains a searchable text representation of all metadata keys, values, tags, and section information. This enables hybrid search across content, vectors, and metadata simultaneously.

#### Advantages and Limitations

**Advantages:**

- **Multi-agent concurrent access**: Multiple agent instances query the same database without file contention or duplication.
- **Multiple collections**: Organize knowledge bases as separate collections within a single database, for example `signalwire_unified`, `pricing`, and `freeswitch`.
- **Incremental updates**: Add new documents to existing collections without rebuilding everything.
- **Scalability**: PostgreSQL scales to billions of rows with efficient indexes (IVFFlat, HNSW), partitioning, and replication.
- **Enterprise features**: Authentication, authorization, connection pooling, monitoring, backup, and point-in-time recovery.
- **Real-time updates**: Add or remove documents without rebuilding the entire index.

**Limitations:**

- **Infrastructure required**: Requires running and maintaining a PostgreSQL instance.
- **Network latency**: A remote database adds 1-5ms of network overhead per query.
- **Operational complexity**: Needs connection pooling, monitoring, and backup procedures.

### When to Use Which

**Use SQLite (.swsearch) when:**

- Deploying a single agent instance
- Developing and testing, where iteration speed and version control matter
- Running serverless deployments (Lambda, Cloud Functions, Azure Functions)
- Deploying to edge environments (embedded systems, IoT, offline operation)
- Managing small to medium knowledge bases (under 1M chunks, under 1GB)
- Building portable or demo agents

**Use pgvector when:**

- Deploying multiple agent instances sharing a knowledge base
- Managing large knowledge bases (1M+ chunks, multiple collections)
- Running production systems requiring high availability, backup, and monitoring
- Needing dynamic content with incremental or real-time indexing
- Organizing multiple knowledge domains with separate collections per domain
- Requiring concurrent read/write access

**A hybrid approach uses both:**

```bash
# Development: build with .swsearch files for fast iteration
sw-search ./docs --output dev.swsearch

# Staging: test with pgvector
sw-search ./docs \
  --backend pgvector \
  --connection-string "postgresql://localhost/staging" \
  --output docs

# Production: deploy to pgvector with replicas
sw-search ./docs \
  --backend pgvector \
  --connection-string "postgresql://prod-db/production" \
  --output docs
```

Same code, different backends via configuration.

| Feature | SQLite | pgvector |
|---------|--------|----------|
| Setup complexity | None | Requires PostgreSQL |
| Scalability | Limited | Excellent |
| Concurrent access | Poor (reads OK) | Excellent |
| Update capability | Rebuild required | Real-time |
| Performance (small) | Excellent | Good |
| Performance (large) | Poor | Excellent |
| Deployment | File copy | Database connection |
| Multi-agent | Separate copies | Shared knowledge |

---

## Query-Only Mode

### The Dependency Problem

Installing full search functionality brings approximately 500MB of dependencies:

- `torch` (~200MB): PyTorch deep learning framework
- `sentence-transformers` (~150MB): Embedding models
- `transformers` (~100MB): HuggingFace transformers
- `numpy`, `scipy` (~50MB): Scientific computing

These libraries are necessary for **generating embeddings** during index building. However, production agents do not need to build indexes. They only need to compare pre-computed vectors: multiplication and addition, with no ML models required.

### search-queryonly Installation

The `search-queryonly` install provides querying capabilities without the ML model stack:

```bash
pip install signalwire-sdk[search-queryonly]
```

**Total size:** ~400MB (vs ~500MB for full search)

**Included:**

- Vector comparison (cosine distance)
- SQLite backend for `.swsearch` files
- pgvector client for PostgreSQL
- Metadata filtering
- Hybrid search scoring

**Excluded:**

- PyTorch
- sentence-transformers models
- Embedding generation
- Document processing

**Savings:** ~100MB+ in dependencies

**Operations not available in query-only mode:**

- Building new indexes
- Generating embeddings
- Updating existing indexes
- Migrating indexes (requires embedding models)

**Verification:**

<!-- snippet: no-run documents a diagnostic helper not exported by signalwire.search -->
```python
from signalwire.search import check_dependencies

check_dependencies()
# Output:
# SQLite backend available
# pgvector client available
# Vector operations available
# sentence-transformers not installed (query-only mode)
# Document processing not available (query-only mode)
```

**Workflow separation:**

On the development or build machine, install full search to build indexes:

```bash
pip install signalwire-sdk[search-full]
sw-search ./docs --output knowledge.swsearch
```

On production, install query-only and deploy with pre-built indexes:

```bash
pip install signalwire-sdk[search-queryonly]
scp knowledge.swsearch prod:/app/
```

### CI/CD Integration

**Build phase** (CI server with full dependencies):

```yaml
# .github/workflows/build-indexes.yml
name: Build Search Indexes

on:
  push:
    paths:
      - 'docs/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install signalwire-sdk[search-full]

      - name: Build search index
        run: |
          sw-search ./docs \
            --model mini \
            --chunking-strategy markdown \
            --output knowledge.swsearch
        timeout-minutes: 15

      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: search-index
          path: knowledge.swsearch
```

**Deploy phase** (production with query-only):

```yaml
# .github/workflows/deploy.yml
name: Deploy Agent

on:
  workflow_run:
    workflows: ["Build Search Indexes"]
    types: [completed]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Download index
        uses: actions/download-artifact@v3
        with:
          name: search-index

      - name: Build Docker image
        run: |
          docker build \
            -f Dockerfile.queryonly \
            -t myagent:latest .

      - name: Push to registry
        run: docker push myagent:latest
```

**pgvector CI/CD strategy** (no file distribution needed):

```bash
# Build once in CI/CD
sw-search ./docs \
  --backend pgvector \
  --connection-string "$DATABASE_URL" \
  --output docs \
  --model mini

# Deploy query-only everywhere -- embeddings already in PostgreSQL
pip install signalwire-sdk[search-queryonly]
```

### Container Deployment Patterns

**Query-only Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install query-only dependencies
RUN pip install signalwire-sdk[search-queryonly]

# Copy pre-built index
COPY knowledge.swsearch /app/

# Copy agent code
COPY agent.py /app/

CMD ["python", "agent.py"]
```

**Container image size comparison:**

| Configuration | Image Size |
|---------------|------------|
| Full search (`signalwire-sdk[search]`) | ~1.2GB |
| Query-only (`signalwire-sdk[search-queryonly]`) | ~800MB |

For Kubernetes deployments with multiple replicas, the savings compound:

- 10 replicas x 400MB = 4GB saved
- Faster image pulls
- Less storage costs
- Quicker deployments

**Migration from full search to query-only in existing deployments:**

```bash
# 1. Separate index building into CI/CD
sw-search ./docs --output knowledge.swsearch
aws s3 cp knowledge.swsearch s3://bucket/indexes/

# 2. Update Dockerfile
# FROM python:3.11
# RUN pip install signalwire-sdk[search-queryonly]
# RUN wget https://bucket/indexes/knowledge.swsearch -O /app/knowledge.swsearch

# 3. Deploy
docker build -t agent:queryonly .
docker push agent:queryonly
kubectl rollout restart deployment/agent
```

---

## pgvector Setup

### Docker Quick Start

Start a PostgreSQL container with the pgvector extension enabled:

```bash
# Start PostgreSQL with pgvector
docker run -d \
  --name pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Create database and extension
docker exec -it pgvector psql -U postgres -c "CREATE DATABASE knowledge;"
docker exec -it pgvector psql -U postgres -d knowledge -c "CREATE EXTENSION vector;"
```

Docker Compose setup for both PostgreSQL and a search service. The `search-service` image needs its own `search_server.py`, since `signalwire.search.search_service` has no command-line entry point of its own (see [Running the Search Service Server](#running-the-search-service-server)):

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: signalwire
      POSTGRES_PASSWORD: signalwire123
      POSTGRES_DB: knowledge
    volumes:
      - pgvector_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  search-service:
    build: .
    environment:
      PGVECTOR_CONNECTION: "postgresql://signalwire:signalwire123@postgres:5432/knowledge"
      SWML_BASIC_AUTH_USER: "api-user"
      SWML_BASIC_AUTH_PASSWORD: "secure-password"
    ports:
      - "8001:8001"
    depends_on:
      - postgres
    command: python search_server.py

volumes:
  pgvector_data:
```

### Building Indexes with pgvector

**Basic index building:**

```bash
sw-search ./docs \
  --backend pgvector \
  --connection-string "postgresql://signalwire:signalwire123@localhost:5432/knowledge" \
  --output docs_collection

# With a specific model
sw-search ./docs \
  --backend pgvector \
  --connection-string "postgresql://signalwire:signalwire123@localhost:5432/knowledge" \
  --output docs_collection \
  --model mini

# From multiple sources
sw-search ./docs ./examples README.md \
  --backend pgvector \
  --connection-string "postgresql://signalwire:signalwire123@localhost:5432/knowledge" \
  --output comprehensive_collection \
  --file-types md,py,txt
```

**Advanced options:**

```bash
# Overwrite existing collection
sw-search ./docs \
  --backend pgvector \
  --connection-string "postgresql://signalwire:signalwire123@localhost:5432/knowledge" \
  --output docs_collection \
  --overwrite

# Semantic chunking
sw-search ./docs \
  --backend pgvector \
  --connection-string "postgresql://signalwire:signalwire123@localhost:5432/knowledge" \
  --output docs_collection \
  --chunking-strategy semantic \
  --semantic-threshold 0.6

# Add tags to all documents
sw-search ./docs \
  --backend pgvector \
  --connection-string "postgresql://signalwire:signalwire123@localhost:5432/knowledge" \
  --output docs_collection \
  --tags documentation,api
```

### Searching with pgvector

**Command-line search:**

```bash
# Basic search
sw-search search docs_collection "how to create an agent" \
  --backend pgvector \
  --connection-string "postgresql://signalwire:signalwire123@localhost:5432/knowledge"

# Search with options
sw-search search docs_collection "API reference" \
  --backend pgvector \
  --connection-string "postgresql://signalwire:signalwire123@localhost:5432/knowledge" \
  --count 10 \
  --verbose

# JSON output for scripting
sw-search search docs_collection "configuration" \
  --backend pgvector \
  --connection-string "postgresql://signalwire:signalwire123@localhost:5432/knowledge" \
  --count 10 \
  --json
```

### Agent Integration (Direct vs Remote Service)

**Direct connection mode** has the agent connect directly to PostgreSQL:

```python
from signalwire import AgentBase
import os

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__()

        self.add_skill("native_vector_search", {
            # Backend configuration
            "backend": "pgvector",
            "connection_string": os.environ.get(
                "PGVECTOR_CONNECTION",
                "postgresql://signalwire:signalwire123@localhost:5432/knowledge"
            ),
            "collection_name": "docs_collection",

            # Tool configuration
            "tool_name": "search_docs",
            "description": "Search the documentation database",

            # Model selection (mini or base)
            "model_name": "mini",

            # Search parameters
            "count": 5,
            "similarity_threshold": 0.1,

            # Auto-build from source (optional)
            "build_index": True,
            "source_dir": "./docs",
            "file_types": ["md", "txt"],
            "overwrite": False
        })
```

**Remote service mode** has the agent query a centralized search service over HTTP:

First, start the search service (see [Running the Search Service Server](#running-the-search-service-server) for what this script wraps):

```bash
python examples/search_server_standalone.py \
    --backend pgvector \
    --connection-string "postgresql://signalwire:signalwire123@localhost:5432/knowledge" \
    --port 8001
```

Then configure the agent:

```python
self.add_skill("native_vector_search", {
    "remote_url": "http://localhost:8001",
    "index_name": "docs_collection",
    "tool_name": "search_docs",
    "description": "Search documentation via remote service"
})
```

**Mode detection** is automatic:

- If `remote_url` is provided, the skill uses remote mode.
- If `index_file` or direct backend config is provided, the skill uses local mode.
- Remote mode takes priority if both are specified.

**Direct vs Remote comparison:**

| Aspect | Direct Connection | Remote Service |
|--------|-------------------|----------------|
| Latency | Lower (direct DB) | Higher (HTTP + DB) |
| Memory per agent | Higher (loads model) | Lower (model on server) |
| Index management | Per agent | Centralized |
| Update impact | Restart agents | Restart service only |
| Scalability | Each agent connects to DB | Service handles connections |

### Running the Search Service Server

The search service provides an HTTP API for searching across document collections stored in pgvector. It supports multiple collections, automatic model detection, hybrid search, authentication, result caching, and HTTPS/TLS.

The `signalwire.search.search_service` module has no command-line entry point of its own; it defines the `SearchService` class. The SDK's `examples/search_server_standalone.py` script wraps that class in a small argument parser, and is the starting point for running it:

**Basic startup:**

```bash
python examples/search_server_standalone.py \
    --backend pgvector \
    --connection-string "postgresql://user:password@localhost:5432/database" \
    --port 8001
```

**API endpoints:**

- `POST /search`: Search the indexes
- `GET /health`: Health check and available indexes
- `POST /reload_index`: Dynamically add or reload an index

**Search request:**

```bash
curl -X POST "http://localhost:8001/search" \
     -u "username:password" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "how to create an agent",
       "index_name": "signalwire_unified",
       "count": 5
     }'
```

**Search with filters:**

```bash
curl -X POST "http://localhost:8001/search" \
     -u "username:password" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "SDK examples",
       "index_name": "signalwire_unified",
       "count": 10,
       "similarity_threshold": 0.3,
       "tags": ["examples", "code"]
     }'
```

The request body accepts `query`, `index_name`, `count`, `similarity_threshold`, `tags`, and `language`. It has no `keyword_weight` field. `keyword_weight` is deprecated in the Python API, the skill and the CLI too, because it has no effect on ranking.

**Response format:**

```json
{
  "results": [
    {
      "content": "To create an AI agent, inherit from AgentBase...",
      "score": 0.8234,
      "metadata": {
        "filename": "docs/agent_guide.md",
        "section": "Creating Your First Agent",
        "tags": ["guide", "agents"],
        "title": "Agent Development Guide"
      }
    }
  ],
  "query_analysis": {
    "original_query": "SDK examples",
    "enhanced_query": "SDK examples",
    "detected_language": "en",
    "pos_analysis": null
  }
}
```

**Health check:**

```bash
curl "http://localhost:8001/health"
```

**Example response:**

```json
{
  "status": "healthy",
  "backend": "pgvector",
  "indexes": ["signalwire_unified"],
  "ssl_enabled": false,
  "auth_required": true,
  "connection_string": "***"
}
```

The `indexes` field lists the loaded index and collection names. Look up chunk and file counts per collection with the `/search` endpoint's `query_analysis`, or with `sw-search validate` for a `.swsearch` file.

**Dynamic index management:**

The `index_name` and `index_path` fields are query parameters, not a JSON body. For pgvector, `index_path` is the collection name:

```bash
curl -X POST "http://localhost:8001/reload_index?index_name=new_collection&index_path=new_collection" \
     -u "username:password"
```

#### Gunicorn / Production Setup

The `search_service` module defines the `SearchService` class, not a WSGI or ASGI factory function. Gunicorn needs a small wrapper module that builds the service and exposes its FastAPI app:

<!-- snippet: no-run connects to a live PostgreSQL database -->
```python
# search_wsgi.py
import os
from signalwire.search.search_service import SearchService

service = SearchService(
    port=8001,
    indexes={"signalwire_unified": "signalwire_unified"},
    backend="pgvector",
    connection_string=os.environ["PGVECTOR_CONNECTION"],
)
app = service.app
```

Point Gunicorn at that module's `app` object:

```bash
pip install gunicorn

gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8001 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    search_wsgi:app
```

#### systemd Service

Create `/etc/systemd/system/search-service.service`, running the same `search_wsgi:app` module:

```ini
[Unit]
Description=SignalWire Search Service
After=network.target postgresql.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/search-service
Environment="PGVECTOR_CONNECTION=postgresql://user:pass@localhost/knowledge"
Environment="SWML_BASIC_AUTH_USER=api-user"
Environment="SWML_BASIC_AUTH_PASSWORD=secure-password"
ExecStart=/usr/local/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8001 \
    --timeout 120 \
    search_wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable search-service
sudo systemctl start search-service
sudo systemctl status search-service
```

#### nginx Reverse Proxy

Terminate HTTPS at nginx and forward requests to the search service over plain HTTP:

```nginx
upstream search_backend {
    server localhost:8001;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name search.example.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://search_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long searches
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://search_backend/health;
        access_log off;
    }
}
```

#### Authentication and Security

The search service shares its security configuration with the rest of the SDK, through the same `SWML_*` variables the agent server reads.

**HTTPS configuration:**

```bash
export SWML_SSL_ENABLED="true"
export SWML_SSL_CERT_PATH="/path/to/cert.pem"
export SWML_SSL_KEY_PATH="/path/to/key.pem"
```

**API credentials** (auto-generated if not set):

```bash
export SWML_BASIC_AUTH_USER="your-username"
export SWML_BASIC_AUTH_PASSWORD="your-secure-password"
```

**CORS configuration** (comma-separated origins):

```bash
export SWML_CORS_ORIGINS="https://app.example.com,https://api.example.com"
```

**Rate limiting:**

<!-- snippet: no-run requires optional third-party package `slowapi` -->
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

**Network security best practices:**

- Run behind a firewall
- Use VPN or private networking between agents and the search service
- Restrict PostgreSQL access to trusted hosts only
- Use strong, unique passwords and rotate credentials regularly
- Store credentials in a secure secret management system

### Environment Variables

The variable names `PGVECTOR_CONNECTION`, `PGVECTOR_DB_USER`, and similar names used elsewhere on this page are a convention, not variables the SDK reads automatically. Your own code reads them with `os.getenv()` and passes the value to `connection_string` (see [Connection Configuration](#connection-configuration)). The search service does read the following variables, shared with the rest of the SDK:

| Variable | Description | Default |
|----------|-------------|---------|
| `SWML_BASIC_AUTH_USER` | HTTP API username | `signalwire` |
| `SWML_BASIC_AUTH_PASSWORD` | HTTP API password | Auto-generated |
| `SWML_SSL_ENABLED` | Enable HTTPS | `false` |
| `SWML_SSL_CERT_PATH` | Path to SSL certificate | None |
| `SWML_SSL_KEY_PATH` | Path to SSL private key | None |
| `SWML_CORS_ORIGINS` | Comma-separated allowed origins | `*` |
| `SWML_ALLOWED_HOSTS` | Comma-separated allowed hostnames | `*` |
| `SIGNALWIRE_LOG_LEVEL` | Log level (`debug`, `info`, `warning`, `error`, `critical`) | `info` |
| `SIGNALWIRE_LOG_FORMAT` | Log format (`console` or `json`) | `console` |

The result cache holds up to 100 queries with first-in-first-out eviction. It has no expiration and no environment variable controls its size.

---

## Migration

### SQLite to pgvector

**When to migrate:**

- Scaling to multiple agents
- Need concurrent access
- Want shared knowledge base
- Scaling beyond 100K chunks

**Step 1: Set up pgvector** (see [Docker Quick Start](#docker-quick-start)).

**Step 2: Verify the existing index:**

```bash
sw-search validate ./knowledge.swsearch
sw-search search ./knowledge.swsearch "test query" --verbose
```

Note the model used (mini, base, or large). It must match during migration.

**Step 3: Migrate using the CLI:**

```bash
# Basic migration
sw-search migrate ./knowledge.swsearch \
  --to-pgvector \
  --connection-string "postgresql://user:pass@localhost:5432/knowledge" \
  --collection-name docs

# Overwrite existing collection
sw-search migrate ./knowledge.swsearch \
  --to-pgvector \
  --connection-string "postgresql://user:pass@localhost:5432/knowledge" \
  --collection-name docs \
  --overwrite

# Verbose output with custom batch size
sw-search migrate ./knowledge.swsearch \
  --to-pgvector \
  --connection-string "postgresql://user:pass@localhost:5432/knowledge" \
  --collection-name docs \
  --batch-size 500 \
  --verbose

# Check index information before migration
sw-search migrate --info ./knowledge.swsearch
```

**What gets migrated:**

- All pre-computed embedding vectors (no recomputation needed)
- Content and processed content
- Keywords and tags
- Filenames, sections, line numbers, and metadata
- Configuration (model name, dimensions, chunking strategy, language settings)

**Step 4: Migrate using the Python API (alternative):**

<!-- snippet: no-run reads a data/index file that must be built first (needs a real artifact) -->
```python
from signalwire.search import SearchIndexMigrator

migrator = SearchIndexMigrator(verbose=True)

stats = migrator.migrate_sqlite_to_pgvector(
    sqlite_path="./knowledge.swsearch",
    connection_string="postgresql://user:pass@localhost:5432/knowledge",
    collection_name="docs",
    overwrite=True,
    batch_size=100
)

print(f"Migrated {stats['chunks_migrated']} chunks")
print(f"Errors: {stats['errors']}")
```

**Step 5: Verify the migration:**

```bash
sw-search search docs \
  --backend pgvector \
  --connection-string "$PGVECTOR_CONNECTION" \
  --model mini \
  "test query"
```

The collection name is the `index_source` argument, not a flag. Compare results to the original SQLite queries.

**Step 6: Update agent configuration:**

Before (SQLite):

```python
self.add_skill("native_vector_search", {
    "tool_name": "search_docs",
    "description": "Search documentation",
    "index_file": "./knowledge.swsearch"
})
```

After (pgvector):

```python
self.add_skill("native_vector_search", {
    "tool_name": "search_docs",
    "description": "Search documentation",
    "backend": "pgvector",
    "connection_string": os.getenv("PGVECTOR_CONNECTION"),
    "collection_name": "docs",
    "model_name": "mini"
})
```

**Step 7: Confirm the indexes.**

Migrating to pgvector creates the collection with `CREATE INDEX IF NOT EXISTS`, the same schema setup used when building a collection directly. An HNSW index on `embedding` already exists, along with GIN indexes on `content`, `tags`, `metadata`, and `metadata_text`. They live on the collection's own table (`chunks_docs` for a collection named `docs`). Confirm them with `psql`:

```sql
\c knowledge
\d chunks_docs
```

**Performance tips for migration:**

- **Batch size:** Default 100. Increase up to 500-1000 for faster migration.
- **Large indexes:** Migration speed is approximately 5-10K chunks per minute.
- **Network latency:** Run migration from a server close to PostgreSQL.
- **PostgreSQL tuning for migration:**

```sql
SET work_mem = '256MB';
ALTER TABLE chunks_collection_name SET (autovacuum_enabled = false);
-- After migration:
ALTER TABLE chunks_collection_name SET (autovacuum_enabled = true);
VACUUM ANALYZE chunks_collection_name;
```

### pgvector to SQLite

The SDK can't migrate a pgvector collection to a `.swsearch` file. `sw-search migrate --to-sqlite` prints "pgvector to SQLite migration not yet implemented" and exits without writing anything, and the same migration in the Python API raises `NotImplementedError` before it connects to the database. No `sw-search export` command exists either. `sw-search` recognizes only `search`, `validate`, `remote`, and `migrate` as subcommands, so `export` is treated as a source path to index, like any other unrecognized first argument.

To end up with a `.swsearch` file today, rebuild the index from the original source documents (see [Building Indexes with pgvector](#building-indexes-with-pgvector)). This recomputes the embeddings rather than reusing pgvector's copies. The collection's `chunks_<collection_name>` table is an ordinary PostgreSQL table, so reading it directly and writing the rows into a new `.swsearch` file is possible. The SDK does not provide a tool for it.

**Update agent configuration:**

Before (pgvector):

<!-- snippet: no-run illustrative fragment (references `os` established in the surrounding prose) -->
```python
{
    "backend": "pgvector",
    "connection_string": os.getenv("PGVECTOR_CONNECTION"),
    "collection_name": "docs",
    "model_name": "mini"
}
```

After (SQLite):

```python
{
    "index_file": "./knowledge.swsearch"
}
```

**Simplify dependencies:**

```dockerfile
# Before: needed PostgreSQL connection
FROM python:3.11-slim
RUN apt-get update && apt-get install -y libpq-dev
RUN pip install signalwire-sdk[search-queryonly] psycopg2-binary
ENV PGVECTOR_CONNECTION=postgresql://...
COPY agent.py /app/

# After: standalone
FROM python:3.11-slim
RUN pip install signalwire-sdk[search-queryonly]
COPY agent.py knowledge.swsearch /app/
```

### Between Collections

Each collection has its own table, named `chunks_<collection_name>`, plus a shared `collection_config` table keyed by collection name.

**SQL copy (fast, within same database):**

The destination table must already exist. Create it first by building or connecting a collection with that name, then copy the rows:

```sql
INSERT INTO chunks_new_collection (content, processed_content, embedding, filename, section, tags, metadata, metadata_text)
SELECT content, processed_content, embedding, filename, section, tags, metadata, metadata_text
FROM chunks_old_collection;

-- Verify
SELECT count(*) FROM chunks_new_collection;
```

**Rename a collection:**

```sql
ALTER TABLE chunks_old_name RENAME TO chunks_new_name;
UPDATE collection_config SET collection_name = 'new_name' WHERE collection_name = 'old_name';
```

There is no `sw-search export` command for copying a collection across databases. Use the SQL copy shown earlier within one database. Across databases, write a script against `psycopg2` that reads `chunks_old_collection` from one database and inserts the rows into the other.

**Delete old collection after verification:**

```sql
DROP TABLE chunks_old_collection;
DELETE FROM collection_config WHERE collection_name = 'old_collection';
```

### Changing Models

Embeddings cannot be reused across different models, so the entire index must be rebuilt from the source documents. There is no `sw-search export` command for pulling content back out of an existing `.swsearch` file.

**Step 1: Rebuild with the new model:**

```bash
sw-search ./docs --model base --output knowledge_base.swsearch
```

**Step 2: Compare quality:**

```bash
echo "test query" | while read query; do
  echo "Mini model:"
  sw-search search ./knowledge.swsearch "$query" --verbose

  echo "Base model:"
  sw-search search ./knowledge_base.swsearch "$query" --verbose
done
```

**Step 3: Benchmark before switching:**

<!-- snippet: no-run illustrative fragment (references `search_mini` established in the surrounding prose) -->
```python
import time

queries = ["query 1", "query 2", "query 3"]

# Time mini model
start = time.time()
for q in queries:
    mini_results = search_mini(q)
mini_time = time.time() - start

# Time base model
start = time.time()
for q in queries:
    base_results = search_base(q)
base_time = time.time() - start

print(f"Mini: {mini_time:.2f}s")
print(f"Base: {base_time:.2f}s")
print(f"Ratio: {base_time/mini_time:.2f}x")

for q, mini, base in zip(queries, mini_results, base_results):
    print(f"\nQuery: {q}")
    print(f"Mini top result: {mini[0]['similarity']:.3f}")
    print(f"Base top result: {base[0]['similarity']:.3f}")
```

**Model dimension reference:**

- Mini model: 384 dimensions
- Base/Large models: 768 dimensions
- Models cannot be mixed in the same collection

### Changing Chunking Strategies

**Step 1: Analyze the current strategy.**

A `.swsearch` file is a SQLite database, so its chunks are visible with the `sqlite3` command-line tool:

```bash
sqlite3 ./knowledge.swsearch "SELECT filename, substr(content, 1, 200) FROM chunks LIMIT 5;"
```

**Step 2: Rebuild with the new strategy:**

```bash
sw-search ./docs \
  --chunking-strategy markdown \
  --model mini \
  --output knowledge_markdown.swsearch
```

**Step 3: Compare results:**

```bash
QUERY="how to authenticate"

echo "Original (sentence):"
sw-search search ./knowledge.swsearch "$QUERY" --count 3

echo "New (markdown):"
sw-search search ./knowledge_markdown.swsearch "$QUERY" --count 3
```

**Step 4: A/B test in production:**

```python
class ABTestAgent(AgentBase):
    def __init__(self):
        super().__init__(name="ABTest")

        self.add_skill("native_vector_search", {
            "tool_name": "search_old",
            "description": "Search docs (old chunking)",
            "index_file": "./knowledge_sentence.swsearch"
        })

        self.add_skill("native_vector_search", {
            "tool_name": "search_new",
            "description": "Search docs (new chunking)",
            "index_file": "./knowledge_markdown.swsearch"
        })
```

**Common strategy migrations:**

| From | To | Command |
|------|----|---------|
| Sentence | Markdown (for code docs) | `sw-search ./docs --chunking-strategy markdown --model mini --output docs_improved.swsearch` |
| Paragraph | QA (for FAQ) | `sw-search ./faq --chunking-strategy qa --model mini --output faq_improved.swsearch` |
| Any | JSON (for manual curation) | Write chunks as JSON directly (see [JSON Workflow](search_integration.md#in-json-workflow)), then build with `--chunking-strategy json` |

### Production Update Procedures

**Zero-downtime updates using blue-green collections:**

```bash
# Current: collection "docs_v1" (green)
# Build new: collection "docs_v2" (blue)
sw-search ./updated-docs \
  --backend pgvector \
  --connection-string "$PGVECTOR_CONNECTION" \
  --output docs_v2 \
  --model mini

# Test new collection
sw-search search docs_v2 \
  --backend pgvector \
  --connection-string "$PGVECTOR_CONNECTION" \
  --model mini \
  "test queries"

# Switch agents to new collection (rolling update)
kubectl set env deployment/agent COLLECTION_NAME=docs_v2

# After verification, delete old collection
# DROP TABLE chunks_docs_v1;
```

**Staged rollout:**

```python
import random

class StagedRolloutAgent(AgentBase):
    def __init__(self):
        super().__init__(name="Staged")

        # 90% use old, 10% use new
        if random.random() < 0.1:
            collection = "docs_v2"
        else:
            collection = "docs_v1"

        self.add_skill("native_vector_search", {
            "tool_name": "search_docs",
            "description": "Search documentation",
            "backend": "pgvector",
            "connection_string": os.getenv("PGVECTOR_CONNECTION"),
            "collection_name": collection,
            "model_name": "mini"
        })

        logger.info(f"Using collection: {collection}")
```

Monitor metrics and gradually increase the percentage.

**Incremental updates for small changes:**

There is no `sw-search export` command for pulling an existing collection's chunks back out for editing. For small content changes, edit the source documents and rebuild into a new collection, following the blue-green pattern.

### Rollback

**Pre-migration checklist:**

- [ ] Backup current index/data
- [ ] Document current configuration (model, strategy, params)
- [ ] Test current performance (latency, quality)
- [ ] Create test queries for validation
- [ ] Plan rollback strategy

**During migration:**

- [ ] Export existing data
- [ ] Validate export (count chunks, sample content)
- [ ] Build new index/collection
- [ ] Test new index with same queries
- [ ] Compare results (quality, performance)
- [ ] Update agent configuration
- [ ] Test agent with new configuration

**Post-migration:**

- [ ] Monitor query latency
- [ ] Track no-result queries
- [ ] Compare quality metrics
- [ ] Verify all features work
- [ ] Update documentation
- [ ] Clean up old indexes/collections
- [ ] Update deployment scripts

**Rollback procedure:**

Keep the old index or collection available until the migration is fully verified. If issues arise:

1. Revert agent configuration to point to the old index/collection.
2. Redeploy agents.
3. Investigate the issues.
4. Fix and retry migration.

```python
# Emergency rollback
self.add_skill("native_vector_search", {
    "index_file": "./knowledge_old.swsearch"  # Revert to old index
})
```

**Dual-backend transition period:**

```python
# Keep both backends during transition
self.add_skill("native_vector_search", {
    "tool_name": "search_docs_new",
    "description": "Search documentation (new pgvector)",
    "backend": "pgvector",
    "connection_string": os.getenv("PGVECTOR_CONNECTION"),
    "collection_name": "docs",
    "model_name": "mini"
})

self.add_skill("native_vector_search", {
    "tool_name": "search_docs_old",
    "description": "Search documentation (old SQLite)",
    "index_file": "./knowledge.swsearch"
})
```

Test both, compare results, then remove the old one.

**Common migration issues:**

| Issue | Symptoms | Fix |
|-------|----------|-----|
| Different result quality | New index returns different results | Verify model matches with `sw-search validate`; ensure explicit `--model` flag during rebuild |
| Performance degradation | Queries slower after migration | Add pgvector indexes; check if model changed (mini vs base); check network latency |
| Missing content | Some chunks not in new index | Compare chunk counts with `sw-search validate` on both; investigate export completeness |

---

## Performance Optimization

### Index Build Performance

**Build time factors:**

| Factor | Impact |
|--------|--------|
| Content volume: 100 docs (~1MB) | 30-60 seconds |
| Content volume: 1,000 docs (~10MB) | 5-10 minutes |
| Content volume: 10,000 docs (~100MB) | 30-60 minutes |
| Chunking: sentence/paragraph | Fastest |
| Chunking: markdown | Moderate (needs parsing) |
| Chunking: semantic/topic | Slowest (requires inference) |
| Model: mini (384 dims) | ~1,000 chunks/second |
| Model: base or large (768 dims) | ~500 chunks/second |
| Hardware: CPU | Significant impact (embedding generation) |
| Hardware: Memory | Need ~2GB + index size |
| Hardware: Disk | I/O speed matters for pgvector |

**Build time benchmarks:**

Small knowledge base (100 docs, 2,000 chunks):

```bash
sw-search ./docs --model mini --chunking-strategy sentence --output docs.swsearch
# Time: 45 seconds
# Size: 8MB
```

Medium knowledge base (1,000 docs, 20,000 chunks):

```bash
sw-search ./docs --model mini --chunking-strategy markdown --output docs.swsearch
# Time: 8 minutes
# Size: 80MB
```

Large knowledge base (10,000 docs, 200,000 chunks):

```bash
sw-search ./docs --model base --chunking-strategy markdown \
  --backend pgvector --connection-string "$PG_CONN" \
  --output docs
# Time: 45 minutes
# Database size: 500MB
```

**Optimizing build performance:**

1. Use mini model when quality allows (2-3x faster than base).
2. Choose efficient chunking (sentence is fastest; markdown slightly slower but better for tech docs).
3. Process multiple directories in parallel:
   ```bash
   sw-search ./docs1 --output docs1.swsearch &
   sw-search ./docs2 --output docs2.swsearch &
   wait
   ```
4. Cache indexes in CI/CD artifacts to avoid unnecessary rebuilds.

### Query Performance

**Query time breakdown (SQLite):**

```
Total query time: 15-30ms
  Embedding generation: 5-10ms (depends on model)
  Vector search: 3-8ms (SQLite)
  Hybrid scoring: 2-5ms
  Result formatting: 1-2ms
```

**Query time breakdown (pgvector):**

```
Total query time: 20-50ms
  Embedding generation: 5-10ms (depends on model)
  Network latency: 1-5ms (if remote)
  Vector search: 10-25ms (PostgreSQL)
  Hybrid scoring: 2-5ms
  Result formatting: 1-2ms
```

**Performance by index size:**

| Index Size | SQLite | pgvector |
|------------|--------|----------|
| Small (< 5,000 chunks) | 10-20ms | 15-30ms |
| Medium (5,000-50,000 chunks) | 20-40ms | 25-50ms |
| Large (50,000+ chunks) | 40-80ms | 30-60ms |

pgvector scales better with size due to optimized indexing.

**Embedding model impact on query time:**

- Mini model: 5-8ms
- Base or large model: 10-15ms

Embedding generation accounts for 30-50% of total query time. The mini model provides a significant speedup.

**Optimizing query performance:**

1. **Use mini model:**
<!-- snippet: no-compile config-excerpt -->
   ```python
   {"model_name": "mini"}
   ```

2. **Reduce result count:**
<!-- snippet: no-compile config-excerpt -->
   ```python
   {"count": 3}  # Faster than 5 or 10
   ```

3. **Set appropriate threshold:**
<!-- snippet: no-compile config-excerpt -->
   ```python
   {"similarity_threshold": 0.4}  # Filters early, reduces processing
   ```

4. **The embedding and metadata indexes already exist:** Building or migrating a collection creates an HNSW index on `embedding`, plus GIN indexes on `content`, `tags`, `metadata`, and `metadata_text`, automatically. Rebuild one explicitly only if needed, using the collection's own table name:
   ```sql
   REINDEX INDEX idx_chunks_docs_embedding;
   ```

### Memory Usage

**Index build memory (peak):**

| Model | SQLite | pgvector |
|-------|--------|----------|
| Mini | ~2GB | ~2GB |
| Base or large | ~3GB | ~3GB |

**Query runtime memory:**

SQLite:
```
Runtime memory: ~1.5GB
  Embedding model: 1GB (mini), 2GB (base)
  SQLite index: Loaded on-demand (~50-100MB)
  Query processing: ~50MB
```

pgvector:
```
Runtime memory: ~1.5GB
  Embedding model: 1GB (mini), 2GB (base)
  Query processing: ~50MB
```

pgvector is more memory-efficient for queries because the index stays in the database.

**Optimizing memory:**

1. Use `search-queryonly` in production (saves ~400MB runtime memory).
2. Use mini model (1GB vs 2GB for base model).
3. In multi-agent deployments using `AgentServer`, the model instance is shared automatically.
4. Models use lazy loading: they load on first query, not at startup.

### Caching Strategies

**Query embedding cache:**

```python
from functools import lru_cache

class CachedSearchAgent(AgentBase):
    def __init__(self):
        super().__init__(name="CachedAgent")
        self._embedding_cache = {}

    @lru_cache(maxsize=100)
    def _cached_search(self, query: str):
        """Cache search results for identical queries."""
        pass
```

**Result caching for frequently asked questions:**

```python
import hashlib
import time

class CachingAgent(AgentBase):
    def __init__(self):
        super().__init__(name="CachingAgent")
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour

    def _get_cache_key(self, query):
        return hashlib.md5(query.lower().encode()).hexdigest()

    def search_with_cache(self, query):
        key = self._get_cache_key(query)
        now = time.time()

        if key in self._cache:
            result, timestamp = self._cache[key]
            if now - timestamp < self._cache_ttl:
                return result

        result = self.do_search(query)
        self._cache[key] = (result, now)
        return result
```

**Search service caching:**

The search service keeps an in-memory cache of the last 100 distinct queries, keyed by query text, index, result count, and tags. It evicts the oldest entry once that limit is reached, has no expiration, and is not configurable. Reloading an index through `/reload_index` clears it.

**PostgreSQL-level caching:**

```sql
-- In postgresql.conf:
shared_buffers = 4GB
effective_cache_size = 12GB
```

SQLite benefits from OS file cache. pgvector benefits from PostgreSQL `shared_buffers`.

### Connection Pooling

For pgvector with many agents, use connection pooling to prevent connection exhaustion.

**PgBouncer configuration:**

```ini
[databases]
knowledge = host=postgres-host port=5432 dbname=knowledge

[pgbouncer]
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
```

Agents connect to PgBouncer instead of directly to PostgreSQL:

```python
connection_string = "postgresql://user:pass@pgbouncer:6432/knowledge"
```

**SQLAlchemy connection pool (application-level):**

<!-- snippet: no-run requires optional third-party package `sqlalchemy` -->
```python
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    os.getenv("PGVECTOR_CONNECTION"),
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### Scaling Strategies

**Horizontal scaling with shared pgvector:**

```
Load Balancer
  Agent Instance 1 --\
  Agent Instance 2 ---+---> PostgreSQL (pgvector)
  Agent Instance 3 --/
  Agent Instance 4 --/
```

All instances query the same index with no duplication.

**Kubernetes deployment example:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: search-agent
spec:
  replicas: 4
  template:
    spec:
      containers:
      - name: agent
        image: my-agent:latest
        env:
        - name: PGVECTOR_CONNECTION
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: connection-string
```

**Read replicas for high query volume:**

```
Write: Main PostgreSQL --> Index updates
                            |
Read:  Agent 1 --> Replica 1
       Agent 2 --> Replica 2
       Agent 3 --> Replica 1
       Agent 4 --> Replica 2
```

Distribute query load across replicas.

**Sharding by collection for large deployments:**

```
Agent determines collection:
  User docs   --> DB1 (user_collection)
  API docs    --> DB2 (api_collection)
  Pricing     --> DB3 (pricing_collection)
```

Each database handles a subset of collections.

**PostgreSQL tuning for pgvector workloads:**

```
# postgresql.conf
shared_buffers = 4GB          # 25% of RAM
work_mem = 64MB
maintenance_work_mem = 1GB
effective_cache_size = 12GB   # 75% of RAM
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

**Index optimization queries:**

```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE tablename LIKE 'chunks_%'
ORDER BY idx_scan DESC;

-- Rebuild indexes if needed
REINDEX INDEX idx_chunks_collection_embedding;

-- Full index set for a collection (created automatically; shown for reference)
CREATE INDEX ON chunks_<collection_name> USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON chunks_<collection_name> USING gin (content gin_trgm_ops);
CREATE INDEX ON chunks_<collection_name> USING gin (to_tsvector('english', content));
CREATE INDEX ON chunks_<collection_name> USING gin (tags);
CREATE INDEX ON chunks_<collection_name> USING gin (metadata);
CREATE INDEX ON chunks_<collection_name> USING gin (metadata_text gin_trgm_ops);
```

### Performance Monitoring

**Metrics to track:**

```python
import time

def monitored_search(query):
    start = time.time()
    results = search(query)
    latency = time.time() - start
    logger.info(f"Search latency: {latency*1000:.1f}ms")
    return results
```

**Prometheus integration:**

<!-- snippet: no-run requires optional third-party package `prometheus_client` -->
```python
from prometheus_client import Counter, Histogram

search_queries = Counter('search_queries_total', 'Total search queries')
search_latency = Histogram('search_latency_seconds', 'Search query latency')
search_errors = Counter('search_errors_total', 'Search errors')
no_results = Counter('search_no_results_total', 'Queries with no results')

def monitored_search(query):
    search_queries.inc()

    with search_latency.time():
        try:
            results = search(query)
            if not results:
                no_results.inc()
            return results
        except Exception as e:
            search_errors.inc()
            raise
```

**PostgreSQL performance diagnostics:**

```sql
-- Check slow queries
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Monitor unused indexes
SELECT * FROM pg_stat_user_indexes
WHERE schemaname = 'public'
AND idx_scan = 0;

-- Analyze query plans
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM chunks_collection
WHERE embedding <=> '[...]'::vector
LIMIT 5;
```

**Health check monitoring:**

```bash
curl -f http://localhost:8001/health || exit 1
```

**Production performance reference (Sigmond agent):**

| Metric | Value |
|--------|-------|
| Collections | 3 (7,500 total chunks) |
| Agent instances | 4 (Kubernetes) |
| Backend | pgvector (single database) |
| Model | Mini |
| Queries/day | 1,000+ |
| Average query time | 25ms |
| P95 query time | 45ms |
| Memory per agent | 1.5GB |
| Cache hit rate | 35% |
| Error rate | < 0.1% |

### Optimization Checklist

**Query performance:**

- [ ] Use mini model when quality is sufficient
- [ ] Reduce result count (3-5 instead of 10+)
- [ ] Set appropriate `similarity_threshold` (0.4-0.5)
- [ ] Use pgvector for large indexes
- [ ] Add indexes to pgvector collections
- [ ] Implement connection pooling

**Memory efficiency:**

- [ ] Use `search-queryonly` in production
- [ ] Use mini model (1GB vs 2GB)
- [ ] Use pgvector (index not in memory)
- [ ] Lazy load search models

**Scalability:**

- [ ] Use pgvector for shared access
- [ ] Deploy multiple agent instances
- [ ] Implement connection pooling
- [ ] Consider read replicas for high volume
- [ ] Monitor query performance

**Build performance:**

- [ ] Use mini model for faster builds
- [ ] Choose efficient chunking strategy
- [ ] Cache indexes in CI/CD
- [ ] Build incrementally when possible

---

## Multi-Agent Architecture

### Shared pgvector Backend

Multiple agent instances sharing a single pgvector database is the recommended architecture for production multi-agent systems.

```
PostgreSQL Database
  signalwire_unified (5k chunks)
    SDK docs, developer guides, APIs
  pricing (500 chunks)
    Pricing information, plans
  freeswitch (2k chunks)
    FreeSWITCH telephony docs

Multiple Agent Instances
  Instance 1 --\
  Instance 2 ---+---> PostgreSQL (shared)
  Instance 3 --/
```

All instances share the same knowledge. Update once, and it is available everywhere.

Agent configuration with multiple collections:

```python
class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="MyAgent")

        pgvector_connection = os.getenv("PGVECTOR_CONNECTION")

        self.add_skill("native_vector_search", {
            "tool_name": "search_signalwire_knowledge",
            "backend": "pgvector",
            "connection_string": pgvector_connection,
            "collection_name": "signalwire_unified"
        })

        self.add_skill("native_vector_search", {
            "tool_name": "search_pricing",
            "backend": "pgvector",
            "connection_string": pgvector_connection,
            "collection_name": "pricing"
        })

        self.add_skill("native_vector_search", {
            "tool_name": "search_freeswitch_knowledge",
            "backend": "pgvector",
            "connection_string": pgvector_connection,
            "collection_name": "freeswitch"
        })
```

Three separate knowledge bases, one database, accessed by the same agent.

### Collection Isolation

Each collection is stored in its own database table (`chunks_<collection_name>`), providing natural isolation:

- Collections can use different embedding models (but dimensions must be compatible with the model specified at query time).
- Collections can be independently created, updated, or deleted.
- Access patterns can vary per collection.

**Managing collections:**

```bash
# List all collections
psql -U signalwire -d knowledge -c "SELECT collection_name FROM collection_config;"

# Check collection stats
psql -U signalwire -d knowledge -c "SELECT COUNT(*) FROM chunks_docs_collection;"

# Delete a collection
psql -U signalwire -d knowledge -c "DROP TABLE chunks_docs_collection;"
psql -U signalwire -d knowledge -c "DELETE FROM collection_config WHERE collection_name='docs_collection';"
```

**Creating multiple collections:**

```bash
sw-search ./docs --backend pgvector \
    --connection-string "$PGVECTOR_CONNECTION" \
    --output docs_collection

sw-search ./examples --backend pgvector \
    --connection-string "$PGVECTOR_CONNECTION" \
    --output examples_collection \
    --model mini
```

**Hybrid team development setup:**

1. A build server or DBA builds indexes to a shared development database:
   ```bash
   sw-search ./docs \
     --backend pgvector \
     --connection-string "postgresql://dev-db/knowledge" \
     --output docs
   ```

2. Developers install only query-only dependencies:
   ```bash
   pip install signalwire-sdk[search-queryonly]
   ```

3. Agents connect to the shared database:
<!-- snippet: no-compile indented-list-excerpt -->
   ```python
   agent.add_skill("native_vector_search", {
       "backend": "pgvector",
       "connection_string": os.getenv("DEV_DATABASE_URL"),
       "collection_name": "docs"
   })
   ```

This means developers do not need the full ML stack, local setup is faster, indexes are consistent across the team, and index management is centralized.

**Batch migration script for multiple indexes:**

<!-- snippet: no-run depends on an env var / user-provided skill not present in this environment -->
```python
#!/usr/bin/env python3
"""Migrate all development indexes to production."""

import os
from pathlib import Path
from signalwire.search import SearchIndexMigrator

DEV_DIR = "./indexes"
PROD_DB = os.environ["PGVECTOR_CONNECTION"]

migrator = SearchIndexMigrator(verbose=True)

for index_file in Path(DEV_DIR).glob("*.swsearch"):
    collection_name = index_file.stem

    print(f"\nMigrating {index_file.name} -> {collection_name}")

    try:
        stats = migrator.migrate_sqlite_to_pgvector(
            sqlite_path=str(index_file),
            connection_string=PROD_DB,
            collection_name=collection_name,
            overwrite=True
        )

        print(f"  Migrated {stats['chunks_migrated']} chunks")

    except Exception as e:
        print(f"  Failed: {e}")

print("\nMigration complete!")
```

## Examples

These scripts in the repository's `examples/` directory demonstrate the deployment patterns this document covers:

- `examples/pgvector_search_agent.py` - PGVector backend for document search with PostgreSQL
- `examples/search_server_standalone.py` - Standalone search server deployment
- `examples/sigmond_remote_search.py` - Remote search via HTTP endpoint
