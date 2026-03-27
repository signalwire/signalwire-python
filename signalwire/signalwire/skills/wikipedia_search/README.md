# Wikipedia Search Skill

The Wikipedia Search skill provides agents with the ability to search Wikipedia articles and retrieve factual information. This skill uses the Wikipedia API to search for articles and return their introductory content, making it perfect for answering factual questions about people, places, concepts, and more.

## Features

- **Free Wikipedia API**: No API keys or credentials required
- **Article Summaries**: Returns introductory content from Wikipedia articles
- **Multiple Results**: Can return multiple article summaries for broader topics
- **Customizable Messages**: Custom no-results messages with query placeholders
- **Error Handling**: Graceful handling of network errors and API issues
- **Speech Recognition**: Includes hints for better voice recognition accuracy

## Requirements

- **Python Packages**: `requests` (automatically installed with SignalWire Agents)
- **API Keys**: None required - uses free Wikipedia API
- **Environment Variables**: None required

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_results` | int | 1 | Number of Wikipedia articles to return (minimum: 1) |
| `no_results_message` | str | Auto-generated | Custom message when no results found. Use `{query}` as placeholder |
| `swaig_fields` | dict | {} | Additional SWAIG function configuration (fillers, etc.) |

## Tools Created

This skill creates one SWAIG tool:

### `search_wiki`
- **Description**: Search Wikipedia for information about a topic and get article summaries
- **Parameters**:
  - `query` (string, required): The search term or topic to look up on Wikipedia

## Usage Examples

### Basic Usage

```python
from signalwire_agents import AgentBase

agent = AgentBase("Wikipedia Assistant")

# Add Wikipedia search with default settings
agent.add_skill("wikipedia_search")
```

### Custom Configuration

```python
# Custom number of results and no-results message
agent.add_skill("wikipedia_search", {
    "num_results": 2,  # Return up to 2 articles
    "no_results_message": "Sorry, I couldn't find any Wikipedia articles about '{query}'. Try different keywords or check the spelling."
})
```

### With SWAIG Fields (Fillers)

```python
# Add custom fillers for better user experience
agent.add_skill("wikipedia_search", {
    "num_results": 1,
    "swaig_fields": {
        "fillers": {
            "en-US": [
                "Let me check Wikipedia for that...",
                "Searching Wikipedia...",
                "Looking that up on Wikipedia...",
                "Checking the encyclopedia..."
            ]
        }
    }
})
```

### Advanced Configuration

```python
# Full configuration example
agent.add_skill("wikipedia_search", {
    "num_results": 3,
    "no_results_message": "I searched Wikipedia but couldn't find information about '{query}'. You might want to try rephrasing your question or searching for related topics.",
    "swaig_fields": {
        "fillers": {
            "en-US": [
                "Searching Wikipedia for factual information...",
                "Let me look that up in the encyclopedia...",
                "Checking Wikipedia's knowledge base..."
            ]
        },
        "meta": {
            "description": "Search Wikipedia for reliable, factual information"
        }
    }
})
```

## Multiple Instance Support

**This skill does NOT support multiple instances.** You can only load one instance of the Wikipedia search skill per agent. This is because:

- Wikipedia search is a general-purpose tool that doesn't need specialization
- The tool name `search_wiki` is fixed and meaningful
- Multiple instances would create confusion without added benefit

If you need different Wikipedia search behaviors, use the `num_results` parameter to control the scope of results.

## API Details

The skill uses the Wikipedia API with two steps:

1. **Search**: Uses the `action=query&list=search` endpoint to find matching articles
2. **Extract**: Uses the `action=query&prop=extracts` endpoint to get article summaries

### Search Process

```
1. Search for articles matching the query
   → GET https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srsearch={query}&srlimit={num_results}

2. For each result, get the article extract
   → GET https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&format=json&titles={title}

3. Format and return the results
```

## Response Format

### Single Result
```
**Article Title**

Article content summary...
```

### Multiple Results
```
**First Article Title**

First article content summary...

==================================================

**Second Article Title**

Second article content summary...
```

## Error Handling

The skill handles various error conditions gracefully:

- **No Results**: Returns the custom `no_results_message` with the query
- **Network Errors**: Returns "Error accessing Wikipedia: {error details}"
- **API Errors**: Returns "Error searching Wikipedia: {error details}"
- **Empty Extracts**: Returns "No summary available for this article"

## Speech Recognition Hints

The skill provides these hints to improve voice recognition:

- "Wikipedia"
- "wiki" 
- "search Wikipedia"
- "look up"
- "tell me about"
- "what is"
- "who is"
- "information about"
- "facts about"

## Best Practices

### Query Optimization
- Use specific terms for better results
- Try both full names and common names (e.g., "Einstein" vs "Albert Einstein")
- For disambiguation, be more specific (e.g., "Python programming language" vs "Python")

### Result Management
- Use `num_results: 1` for specific factual queries
- Use `num_results: 2-3` for broader topics that might have multiple relevant articles
- Avoid very high numbers as it can overwhelm users

### Error Messages
- Customize `no_results_message` to match your agent's personality
- Include suggestions for alternative searches
- Use the `{query}` placeholder to reference what the user searched for

### Integration Tips
- Combine with web search for comprehensive information gathering
- Use for factual verification of claims
- Great for educational and reference applications

## Example Conversations

**User**: "Tell me about quantum physics"
**Agent**: *Searching Wikipedia...* "Here's what I found about quantum physics: **Quantum mechanics** - Quantum mechanics is a fundamental theory that describes the behavior of nature at and below the scale of atoms..."

**User**: "Who was Marie Curie?"
**Agent**: *Let me check Wikipedia for that...* "**Marie Curie** - Marie Salomea Skłodowska-Curie was a Polish and naturalized-French physicist and chemist who conducted pioneering research on radioactivity..."

## Troubleshooting

### Common Issues

1. **Skill not loading**: Ensure `requests` package is installed
2. **No results for valid topics**: Try different search terms or check spelling
3. **Network timeouts**: The skill has a 10-second timeout for API calls

### Debug Information

The skill logs initialization and search activities:
```
Wikipedia search skill initialized with {num_results} max results
```

Enable debug logging to see detailed API interactions and error information.

## Related Skills

- **web_search**: For current information and broader web content
- **datasphere**: For searching custom knowledge bases
- **datetime**: For current date/time context in historical queries

The Wikipedia skill is perfect for factual, encyclopedic information, while web search is better for current events and specific products/services. 