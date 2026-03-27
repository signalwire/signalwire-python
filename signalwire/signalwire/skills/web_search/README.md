# Web Search Skill

The web_search skill provides web search capabilities using Google Custom Search API with web scraping functionality. It allows agents to search the internet for current information and extract content from the resulting web pages.

## Features

- Google Custom Search API integration
- Web page content scraping and extraction
- Configurable number of search results
- Configurable delay between requests
- Custom no-results messages with query placeholders
- **Multiple instance support** - run multiple search engines with different configurations

## Requirements

- **Packages**: `beautifulsoup4`, `requests`
- **API Access**: Google Custom Search API key and Search Engine ID

## Parameters

### Required Parameters

- `api_key` (string): Google Custom Search API key
- `search_engine_id` (string): Google Custom Search Engine ID

### Optional Parameters

- `num_results` (integer, default: 1): Number of search results to return (max: 10)
- `delay` (float, default: 0): Delay in seconds between web page requests
- `tool_name` (string, default: "web_search"): Custom name for the search tool (enables multiple instances)
- `no_results_message` (string): Custom message when no results are found
  - Default: "I couldn't find any results for '{query}'. This might be due to a very specific query or temporary issues. Try rephrasing your search or asking about a different topic."
  - Use `{query}` as placeholder for the search query

### Advanced Parameters

- `swaig_fields` (dict): Additional SWAIG function configuration
  - `secure` (boolean): Override security settings
  - `fillers` (dict): Language-specific filler phrases during search
  - Any other SWAIG function parameters

## Tools Created

- **Default**: `web_search` - Search the web for information
- **Custom**: Uses the `tool_name` parameter value

## Usage Examples

### Basic Usage

```python
# Minimal configuration
agent.add_skill("web_search", {
    "api_key": "your-google-api-key",
    "search_engine_id": "your-search-engine-id"
})
```

### Advanced Configuration

```python
# Comprehensive results with delay
agent.add_skill("web_search", {
    "api_key": "your-google-api-key",
    "search_engine_id": "your-search-engine-id",
    "num_results": 5,
    "delay": 1.0,
    "no_results_message": "Sorry, I couldn't find information about '{query}'. Try a different search term."
})
```

### Multiple Instances

```python
# General web search
agent.add_skill("web_search", {
    "api_key": "your-api-key",
    "search_engine_id": "general-search-engine-id",
    "tool_name": "search_general",
    "num_results": 1
})

# News-specific search
agent.add_skill("web_search", {
    "api_key": "your-api-key", 
    "search_engine_id": "news-search-engine-id",
    "tool_name": "search_news",
    "num_results": 3,
    "delay": 0.5
})

# Quick search for fast answers
agent.add_skill("web_search", {
    "api_key": "your-api-key",
    "search_engine_id": "quick-search-engine-id", 
    "tool_name": "quick_search",
    "num_results": 1,
    "delay": 0
})
```

### With Custom Fillers

```python
agent.add_skill("web_search", {
    "api_key": "your-api-key",
    "search_engine_id": "your-search-engine-id",
    "swaig_fields": {
        "fillers": {
            "en-US": [
                "Let me search the web for that...",
                "Looking that up online...",
                "Searching the internet now..."
            ],
            "es-ES": [
                "Déjame buscar eso en internet...",
                "Buscando en línea..."
            ]
        }
    }
})
```

## How It Works

1. **Search**: Uses Google Custom Search API to find relevant web pages
2. **Scrape**: Downloads and extracts readable content from each result page
3. **Format**: Presents results with titles, URLs, snippets, and extracted content
4. **Filter**: Removes unwanted elements (scripts, styles, navigation) for clean text

## Multiple Instance Support

The web_search skill supports multiple instances, allowing you to:

- Use different Google search engines for different types of content
- Have different configurations (number of results, delays) per instance
- Create specialized search tools (news, products, support, etc.)
- Customize tool names for clarity (`search_news`, `search_products`, etc.)

Each instance is uniquely identified by its `search_engine_id` and `tool_name` combination.

## Error Handling

- **No Results**: Returns custom `no_results_message` with query placeholder
- **Network Issues**: Returns friendly error message for timeouts/connectivity issues
- **Invalid Pages**: Gracefully handles pages that can't be scraped
- **Rate Limiting**: Built-in delay support to respect API limits

## Best Practices

1. **For Speed**: Use `num_results: 1` and `delay: 0` for customer service
2. **For Research**: Use `num_results: 3-5` and `delay: 0.5-1.0` for comprehensive results  
3. **For News**: Use a news-specific search engine ID with higher result count
4. **Rate Limiting**: Add delays when making frequent searches to respect API quotas
5. **Custom Messages**: Tailor `no_results_message` to your agent's personality and use case

## Getting Google Custom Search Setup

1. Create a Google Cloud Project
2. Enable the Custom Search JSON API
3. Create a Custom Search Engine at https://cse.google.com/
4. Get your API key from Google Cloud Console
5. Get your Search Engine ID from the Custom Search Engine settings 