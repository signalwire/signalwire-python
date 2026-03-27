# DataSphere Serverless Skill

The datasphere_serverless skill provides knowledge search capabilities using SignalWire DataSphere's RAG (Retrieval-Augmented Generation) stack with serverless execution via DataMap. This skill offers the same functionality as the standard datasphere skill but executes on SignalWire servers rather than your agent server.

## Features

- **Serverless Execution**: Runs on SignalWire infrastructure via DataMap
- **SignalWire DataSphere Integration**: Vector-based knowledge search
- **Identical API**: Same parameters and functionality as the standard datasphere skill
- **Multi-language Support**: Synonym expansion and language-specific search
- **Tag-based Filtering**: Targeted searches using document tags
- **Custom No-results Messages**: Configurable response templates
- **Multiple Instance Support**: Search different knowledge bases with different configurations
- **No Webhook Infrastructure**: No need to expose HTTP endpoints

## Requirements

- **Packages**: None (DataMap handles API calls serverlessly)
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
# Minimal configuration - same as standard datasphere skill
agent.add_skill("datasphere_serverless", {
    "space_name": "my-space",
    "project_id": "my-project-id",
    "token": "my-token",
    "document_id": "my-document-id"
})
```

### Advanced Configuration

```python
# Comprehensive search with filtering - identical to standard skill
agent.add_skill("datasphere_serverless", {
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
agent.add_skill("datasphere_serverless", {
    "space_name": "my-space",
    "project_id": "my-project-id",
    "token": "my-token",
    "document_id": "product-docs-id",
    "tool_name": "search_product_docs",
    "tags": ["Products", "Features"],
    "count": 2
})

# Support knowledge base search
agent.add_skill("datasphere_serverless", {
    "space_name": "my-space",
    "project_id": "my-project-id",
    "token": "my-token",
    "document_id": "support-kb-id",
    "tool_name": "search_support",
    "tags": ["Support", "Troubleshooting"],
    "count": 3,
    "distance": 4.0
})
```

## DataMap Implementation Details

This skill demonstrates advanced DataMap usage patterns:

### 1. **Serverless API Integration**
- API calls execute on SignalWire servers, not your agent server
- No webhook endpoints required
- Built-in authentication and error handling

### 2. **Dynamic Request Building**
```python
webhook_body = {
    "document_id": self.document_id,
    "query_string": "${args.query}",  # Dynamic from user input
    "distance": self.distance,         # Static from configuration
    "count": self.count               # Static from configuration
}

# Optional parameters added conditionally
if self.tags is not None:
    webhook_body["tags"] = self.tags
```

### 3. **Response Processing with Foreach**
```python
.foreach({
    "input_key": "results",           # API response key containing array
    "output_key": "formatted_results", # Name for built string
    "max": self.count,                # Limit processing
    "append": "=== RESULT ${this.index} ===\n${this.content}\n========\n\n"
})
```

The `foreach` mechanism:
- Iterates over the `results` array from DataSphere API response
- For each result, expands `${this.content}` with the result's content field
- Builds a concatenated string stored as `formatted_results`
- Limits processing to `max` items

### 4. **Variable Expansion in Output**
```python
.output(SwaigFunctionResult('I found ${results.length} result(s) for "${args.query}":\n\n${formatted_results}'))
```

References:
- `${results.length}`: Number of results from API
- `${args.query}`: User's search query
- `${formatted_results}`: String built by foreach

### 5. **Error Handling**
```python
.error_keys(['error', 'message'])
.fallback_output(SwaigFunctionResult(self.no_results_message.replace('{query}', '${args.query}')))
```

## Comparison: Standard vs Serverless

| Feature | Standard DataSphere | DataSphere Serverless |
|---------|-------------------|---------------------|
| **Execution** | Agent server | SignalWire servers |
| **Parameters** | Identical | Identical |
| **Functionality** | Full Python logic | DataMap templates |
| **Performance** | Agent server load | No agent server load |
| **Deployment** | Webhook infrastructure | No infrastructure needed |
| **Response Formatting** | Custom Python code | DataMap foreach/templates |
| **Error Handling** | Granular Python exceptions | DataMap error keys |
| **Use Case** | Complex custom logic | Standard API integration |

## When to Use Serverless vs Standard

### **Use DataSphere Serverless When:**
- You want simple deployment without webhook infrastructure
- Performance on agent server is a concern
- Standard response formatting is sufficient
- You prefer serverless execution model

### **Use Standard DataSphere When:**
- You need complex custom response formatting
- You want granular error handling with different messages per error type
- You need runtime decision-making logic
- You want full control over the search process

## Benefits of DataMap Implementation

1. **Simplified Deployment**: No HTTP endpoints to expose or manage
2. **Better Performance**: Executes on SignalWire infrastructure
3. **Reduced Complexity**: Declarative configuration vs imperative code
4. **Automatic Scaling**: SignalWire handles execution scaling
5. **Built-in Reliability**: Server-side execution with built-in retry logic

## How It Works

1. **Configuration**: Skill parameters are validated and stored during setup
2. **Tool Registration**: DataMap configuration is built with static values from setup
3. **Execution**: When called, DataMap executes on SignalWire servers:
   - Makes POST request to DataSphere API with user's query
   - Processes response array using foreach mechanism
   - Formats results using template expansion
   - Returns formatted response to agent
4. **Response**: Agent receives formatted results without any local processing

## Multiple Instance Support

Like the standard datasphere skill, this supports multiple instances:

- Each instance creates a tool with a unique name (`tool_name` parameter)
- Different configurations per instance (different documents, tags, etc.)
- Instance tracking via `get_instance_key()` method
- Same agent can search multiple knowledge bases

## Error Handling

- **API Errors**: Handled by `error_keys` configuration
- **No Results**: Uses `fallback_output` with custom message
- **Invalid Parameters**: Validated during skill setup
- **Timeout/Network**: Handled by SignalWire infrastructure

## Troubleshooting

### Common Issues

1. **"Missing required parameters"**
   - Ensure all required parameters are provided
   - Check parameter names match exactly

2. **"No results found"**
   - Verify document_id exists and is accessible
   - Check distance threshold isn't too restrictive
   - Ensure tags match document tags if specified

3. **"Authentication failed"**
   - Verify project_id and token are correct
   - Ensure token has DataSphere permissions

### Debugging

Enable debug logging to see DataMap execution:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

DataMap execution details are logged by the SignalWire server infrastructure. 