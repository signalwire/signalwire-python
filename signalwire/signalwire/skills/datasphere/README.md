# DataSphere Skill

The datasphere skill provides knowledge search capabilities using SignalWire DataSphere's RAG (Retrieval-Augmented Generation) stack. It allows agents to search through uploaded documents and knowledge bases to find relevant information.

## Features

- SignalWire DataSphere integration for knowledge search
- Vector-based similarity search with configurable distance thresholds
- Multi-language support and synonym expansion
- Tag-based filtering for targeted searches
- Custom no-results messages with query placeholders
- **Multiple instance support** - search different knowledge bases with different configurations

## Requirements

- **Packages**: `requests`
- **SignalWire Account**: DataSphere-enabled space with uploaded documents

## Parameters

### Required Parameters

- `space_name` (string): SignalWire space name
- `project_id` (string): SignalWire project ID
- `token` (string): SignalWire authentication token
- `document_id` (string): DataSphere document ID to search

### Optional Parameters

- `count` (integer, default: 1): Number of search results to return
- `distance` (float, default: 3.0): Distance threshold for search matching (lower = more similar)
- `tags` (list): List of tags to filter search results
- `language` (string): Language code to limit search (e.g., "en", "es")
- `pos_to_expand` (list): Parts of speech for synonym expansion (e.g., ["NOUN", "VERB"])
- `max_synonyms` (integer): Maximum number of synonyms to use for each word
- `tool_name` (string, default: "search_knowledge"): Custom name for the search tool (enables multiple instances)
- `no_results_message` (string): Custom message when no results are found
  - Default: "I couldn't find any relevant information for '{query}' in the knowledge base. Try rephrasing your question or asking about a different topic."
  - Use `{query}` as placeholder for the search query

### Advanced Parameters

- `swaig_fields` (dict): Additional SWAIG function configuration
  - `secure` (boolean): Override security settings
  - `fillers` (dict): Language-specific filler phrases during search
  - Any other SWAIG function parameters

## Tools Created

- **Default**: `search_knowledge` - Search the knowledge base for information
- **Custom**: Uses the `tool_name` parameter value

## Usage Examples

### Basic Usage

```python
# Minimal configuration
agent.add_skill("datasphere", {
    "space_name": "my-space",
    "project_id": "my-project-id",
    "token": "my-token",
    "document_id": "my-document-id"
})
```

### Advanced Configuration

```python
# Comprehensive search with filtering
agent.add_skill("datasphere", {
    "space_name": "my-space",
    "project_id": "my-project-id",
    "token": "my-token",
    "document_id": "my-document-id",
    "count": 3,
    "distance": 5.0,
    "tags": ["FAQ", "Support"],
    "language": "en",
    "pos_to_expand": ["NOUN", "VERB"],
    "max_synonyms": 3,
    "no_results_message": "I couldn't find information about '{query}' in our support documentation."
})
```

### Multiple Instances

```python
# Product documentation search
agent.add_skill("datasphere", {
    "space_name": "my-space",
    "project_id": "my-project-id",
    "token": "my-token",
    "document_id": "product-docs-id",
    "tool_name": "search_product_docs",
    "tags": ["Products", "Features"],
    "count": 2
})

# Support knowledge base search
agent.add_skill("datasphere", {
    "space_name": "my-space",
    "project_id": "my-project-id",
    "token": "my-token",
    "document_id": "support-kb-id",
    "tool_name": "search_support",
    "tags": ["Support", "Troubleshooting"],
    "count": 3,
    "distance": 4.0
})

# Policy and procedure search
agent.add_skill("datasphere", {
    "space_name": "my-space",
    "project_id": "my-project-id",
    "token": "my-token",
    "document_id": "policies-id",
    "tool_name": "search_policies",
    "tags": ["Policy", "Compliance"],
    "count": 1,
    "distance": 2.0
})
```

### With Custom Fillers

```python
agent.add_skill("datasphere", {
    "space_name": "my-space",
    "project_id": "my-project-id",
    "token": "my-token", 
    "document_id": "my-document-id",
    "swaig_fields": {
        "fillers": {
            "en-US": [
                "Searching our knowledge base...",
                "Looking through our documentation...",
                "Checking our information database..."
            ],
            "es-ES": [
                "Buscando en nuestra base de conocimientos...",
                "Revisando nuestra documentación..."
            ]
        }
    }
})
```

## How It Works

1. **Vector Search**: Uses semantic similarity to find relevant content chunks
2. **Distance Filtering**: Only returns results within the specified distance threshold
3. **Tag Filtering**: Optionally filters results by document tags
4. **Language Processing**: Supports synonym expansion and language-specific search
5. **Format Results**: Presents found content with metadata and relevance scores

## Multiple Instance Support

The datasphere skill supports multiple instances, allowing you to:

- Search different knowledge bases/documents with one agent
- Use different search parameters per knowledge domain
- Create specialized search tools (`search_products`, `search_support`, etc.)
- Apply different tag filtering per instance
- Customize distance thresholds based on content type

Each instance is uniquely identified by its `search_engine_id` (derived from space/project/document) and `tool_name` combination.

## Parameters Explained

### Distance Threshold
- **Lower values** (1.0-2.0): Very strict matching, only highly similar content
- **Medium values** (3.0-4.0): Balanced matching, good for most use cases
- **Higher values** (5.0+): More permissive matching, broader results

### Count vs Distance
- Use higher `count` with lower `distance` for precise, multiple results
- Use lower `count` with higher `distance` for broader, fewer results

### Tags Usage
- Pre-tag your documents in DataSphere with categories
- Use tags to create domain-specific searches (e.g., ["FAQ"], ["Legal"], ["Technical"])

### Language Support
- Specify language codes for multilingual knowledge bases
- Helps improve search accuracy for non-English content

## Error Handling

- **No Results**: Returns custom `no_results_message` with query placeholder
- **API Issues**: Returns friendly error message for authentication/connectivity issues
- **Invalid Documents**: Gracefully handles missing or inaccessible documents
- **Timeout Protection**: Built-in 30-second timeout for API requests

## Best Practices

1. **Document Organization**: Use meaningful tags when uploading to DataSphere
2. **Distance Tuning**: Start with default 3.0, adjust based on result quality
3. **Multiple Instances**: Separate different knowledge domains for better results
4. **Language Consistency**: Specify language when dealing with multilingual content
5. **Result Count**: Balance between comprehensive answers (higher count) and response speed (lower count)

## Setting Up DataSphere

1. Access your SignalWire space
2. Enable DataSphere in your space settings
3. Upload documents through the DataSphere interface
4. Note the document IDs for use in skill configuration
5. Apply appropriate tags during document upload
6. Get your project ID and token from SignalWire console 