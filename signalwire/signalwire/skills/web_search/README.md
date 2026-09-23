# Web Search Skill

The web_search skill provides web search capabilities using Google Custom Search API with web scraping functionality. It allows agents to search the internet for current information and extract content from the resulting web pages.

## Features

The skill covers these capabilities:

- Google Custom Search API integration
- Web page content scraping and extraction
- Configurable number of search results
- Configurable delay between requests
- Custom no-results messages with query placeholders
- **Multiple instance support** - run multiple search engines with different configurations

## Requirements

The skill needs two packages and a Google Custom Search account:

- **Packages**: `beautifulsoup4`, `requests`
- **API Access**: Google Custom Search API key and Search Engine ID

## Parameters

### Required Parameters

The skill needs two parameters to query Google Custom Search:

- `api_key` (string): Google Custom Search API key
- `search_engine_id` (string): Google Custom Search Engine ID

### Optional Parameters

The rest of the parameters tune search behavior and have defaults:

- `num_results` (integer, default: 3): Number of search results to return (1 to 10)
- `delay` (float, default: 0.5): Delay in seconds between web page requests
- `tool_name` (string, default: "web_search"): Custom name for the search tool (enables multiple instances)
- `no_results_message` (string): Custom message when no results are found
  - Default: "I couldn't find quality results for '{query}'. The search returned only low-quality or inaccessible pages. Try rephrasing your search or asking about a different topic."
  - Use `{query}` as placeholder for the search query

### Quality and Performance Parameters

These parameters tune the quality scoring and scraping performance described in [Quality Filtering](#quality-filtering):

- `max_content_length` (integer, default: 32768, minimum: 1000): Maximum characters across all returned results, combined. Each result still keeps at least 2000 characters of content even if that pushes the total over this budget.
- `oversample_factor` (number, default: 2.5, range: 1.0 to 3.5): How many extra candidate pages to fetch and score before keeping the best `num_results` of them. For example, `num_results: 3` with the default factor fetches up to 7 candidates (fetching is always capped at 10).
- `min_quality_score` (number, default: 0.3, range: 0.0 to 1.0): Minimum quality score a scraped page needs to count as a result. See [Quality Filtering](#quality-filtering) for how the score is calculated.
- `per_page_timeout` (number, default: 2.0, minimum: 0.1): Maximum seconds to wait for a single page to load before giving up on it.
- `overall_deadline` (number, default: 10.0, minimum: 1.0): Total seconds allowed for the whole search, across every candidate page. Scrapes still running past this deadline are abandoned, and the skill falls back to Google's own result snippets instead of returning an error.
- `parallel_scrape` (boolean, default: true): Scrape candidate pages at the same time in a thread pool instead of one after another. `delay` has no effect while this is on, since there are no sequential requests left to space out.
- `snippets_only` (boolean, default: false): Skip page scraping and return Google's search snippets directly. This is the fastest mode, and it is also what the skill falls back to when no page meets `min_quality_score` before `overall_deadline`.
- `response_prefix` (string, default: ""): Text added before every non-empty search response.
- `response_postfix` (string, default: ""): Text added after every non-empty search response.

### Advanced Parameters

The skill accepts one advanced parameter, for SWAIG function configuration:

- `swaig_fields` (dict): Additional SWAIG function configuration
  - `secure` (boolean): Override security settings
  - `fillers` (dict): Language-specific filler phrases during search
  - Any other SWAIG function parameters

## Tools Created

The skill registers one tool, under a default or custom name:

- **Default**: `web_search` - Search the web for information
- **Custom**: Uses the `tool_name` parameter value

## Usage Examples

### Basic Usage

The minimal configuration needs only the two required parameters:

```python
# Minimal configuration
agent.add_skill("web_search", {
    "api_key": "your-google-api-key",
    "search_engine_id": "your-search-engine-id"
})
```

### Advanced Configuration

This configuration returns more results and adds a delay between requests:

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

Each call to `add_skill` with a distinct `tool_name` registers a separate search tool:

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

Add language-specific filler phrases the agent speaks while it searches:

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

A search moves through five stages:

1. **Search**: Uses Google Custom Search API to find candidate web pages
2. **Scrape**: Downloads each candidate page and extracts its readable text
3. **Score and filter**: Scores each page as described in [Quality Filtering](#quality-filtering), and drops any page below `min_quality_score`
4. **Select**: Sorts the remaining pages by score and keeps the best `num_results`, preferring one page per domain
5. **Format**: Presents the results with titles, URLs, snippets, and extracted content, truncated to fit `max_content_length`

## Quality Filtering

Each scraped page gets a quality score that combines six weighted factors, and the skill drops any page scoring below `min_quality_score`:

- **Content length (25%)**: pages with roughly 2,000 to 10,000 characters of text score highest.
- **Query relevance (25%)**: how many of the query's significant words, and consecutive word pairs, appear in the page.
- **Sentence structure (15%)**: how many sentences of at least 30 characters the page has, up to a target of 10.
- **Domain reputation (15%)**: a bonus for domains such as Wikipedia, Stack Overflow, and arXiv. A penalty applies to social media domains such as Reddit, YouTube, and X.
- **Word diversity (10%)**: how varied the page's vocabulary is. A page needs roughly 30% unique words to score well, guarding against repetitive or templated text.
- **Freedom from boilerplate (10%)**: a penalty for phrases common in cookie notices, navigation menus, subscription prompts and ads.

If every candidate page is dropped, or scraping runs past `overall_deadline`, the skill falls back to Google's own result snippets instead of returning an error. Setting `snippets_only` skips scraping and quality scoring entirely.

## Multiple Instance Support

The web_search skill supports multiple instances, allowing you to:

- Use different Google search engines for different types of content
- Have different configurations (number of results, delays) per instance
- Create specialized search tools (news, products, support, etc.)
- Customize tool names for clarity (`search_news`, `search_products`, etc.)

Each instance is uniquely identified by its `search_engine_id` and `tool_name` combination.

## Error Handling

The skill covers five failure cases:

- **No Results**: Returns custom `no_results_message` with query placeholder
- **Network Issues**: Returns friendly error message for timeouts/connectivity issues
- **Invalid Pages**: Gracefully handles pages that can't be scraped
- **Blocked Pages**: Skips a result page that resolves or redirects to a private or internal address. Page fetches connect directly, ignoring `HTTP_PROXY` and `HTTPS_PROXY`, so that the check applies to each connection; the Google API request still uses them. To fetch pages through a proxy that blocks private destinations itself, set `SWML_URL_FETCH_USE_PROXY=true`.
- **Rate Limiting**: Built-in delay support to respect API limits

## Best Practices

Match the configuration to the agent's purpose:

1. **For Speed**: Use `num_results: 1` and `delay: 0` for customer service
2. **For Research**: Use `num_results: 3-5` and `delay: 0.5-1.0` for comprehensive results  
3. **For News**: Use a news-specific search engine ID with higher result count
4. **Rate Limiting**: Add delays when making frequent searches to respect API quotas
5. **Custom Messages**: Tailor `no_results_message` to your agent's personality and use case

## Getting Google Custom Search Setup

Set up Google Custom Search before you add this skill:

1. Create a Google Cloud Project
2. Enable the Custom Search JSON API
3. Create a Custom Search Engine at https://cse.google.com/
4. Get your API key from Google Cloud Console
5. Get your Search Engine ID from the Custom Search Engine settings 