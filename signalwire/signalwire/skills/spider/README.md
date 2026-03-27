# Spider Skill

Fast web scraping and crawling capabilities for SignalWire AI Agents. Optimized for speed and token efficiency with sub-second response times.

## Features

- **Single page scraping** - Extract content from any web page in under 500ms
- **Multi-page crawling** - Follow links and crawl entire sections of websites
- **Structured data extraction** - Extract specific data using CSS/XPath selectors
- **Multiple output formats** - Plain text, markdown, or structured JSON
- **Smart text truncation** - Intelligently truncate long content while preserving key information
- **Response caching** - Cache pages to avoid redundant requests
- **Configurable crawling** - Control depth, page limits, and URL patterns

## Installation

```python
# Basic usage with defaults (single page scraping)
agent.add_skill("spider")

# Custom configuration
agent.add_skill("spider", {
    "delay": 0.5,
    "max_pages": 10,
    "max_depth": 2
})
```

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `delay` | float | 0.1 | Seconds between requests |
| `concurrent_requests` | int | 5 | Number of parallel requests |
| `timeout` | int | 5 | Request timeout in seconds |
| `max_pages` | int | 1 | Maximum pages to crawl |
| `max_depth` | int | 0 | How many links deep to crawl |
| `extract_type` | string | "fast_text" | Default extraction method |
| `max_text_length` | int | 3000 | Maximum characters per page |
| `clean_text` | bool | True | Remove extra whitespace |
| `cache_enabled` | bool | True | Enable response caching |
| `follow_robots_txt` | bool | False | Respect robots.txt |
| `user_agent` | string | "Spider/1.0" | User agent string |
| `headers` | dict | {} | Additional HTTP headers |

## Available Tools

### scrape_url

Extract text content from a single web page.

**Parameters:**
- `url` (required): The URL to scrape
- `extract_type` (optional): "fast_text", "markdown", or "structured"
- `selectors` (optional): CSS/XPath selectors for specific elements

**Examples:**
```
"Please get the content from https://example.com/article"
"Scrape the main text from https://docs.example.com in markdown format"
"Extract the product price from this page using the .price selector"
```

### crawl_site

Crawl multiple pages starting from a URL.

**Parameters:**
- `start_url` (required): Starting URL for the crawl
- `max_depth` (optional): How many links deep to crawl
- `follow_patterns` (optional): List of regex patterns for URLs to follow
- `max_pages` (optional): Maximum pages to crawl

**Examples:**
```
"Crawl the documentation starting from /docs with depth 2"
"Get all blog posts from the site, following only /blog/ URLs"
"Crawl up to 20 pages from their support section"
```

### extract_structured_data

Extract specific data from a web page using selectors.

**Parameters:**
- `url` (required): The URL to scrape
- `selectors` (required): Dictionary mapping field names to CSS/XPath selectors

**Examples:**
```
"Extract the title, price, and description from this product page"
"Get all the email addresses and phone numbers from the contact page"
```

## Usage Examples

### Basic Single Page Scraping (Default)
```python
agent.add_skill("spider")
# AI can now: "Get the content from https://example.com"
```

### Documentation Crawling
```python
agent.add_skill("spider", {
    "max_pages": 50,
    "max_depth": 3,
    "delay": 1.0,
    "extract_type": "markdown"
})
# AI can now: "Crawl the API documentation and summarize the endpoints"
```

### Fast News Aggregation
```python
agent.add_skill("spider", {
    "concurrent_requests": 10,
    "delay": 0.05,
    "max_pages": 20,
    "max_text_length": 1000,
    "cache_enabled": True
})
# AI can now: "Get the latest articles from the news section"
```

### Respectful External Scraping
```python
agent.add_skill("spider", {
    "delay": 2.0,
    "concurrent_requests": 1,
    "follow_robots_txt": True,
    "user_agent": "MyBot/1.0 (contact@example.com)"
})
# AI can now: "Carefully scrape competitor pricing data"
```

### Multiple Spider Instances
```python
# Fast spider for internal sites
agent.add_skill("spider", {
    "tool_name": "fast_spider",
    "delay": 0.1,
    "concurrent_requests": 10
})

# Slow spider for external sites
agent.add_skill("spider", {
    "tool_name": "polite_spider",
    "delay": 2.0,
    "concurrent_requests": 1,
    "follow_robots_txt": True
})
# AI can now use: fast_spider_scrape_url() and polite_spider_scrape_url()
```

## Output Examples

### Fast Text Output (Default)
```
Content from https://example.com/article (2,456 characters):

How to Build Better Web Applications
Published on January 15, 2024

In this comprehensive guide, we'll explore modern techniques for building
scalable and maintainable web applications...

Key Topics:
- Architecture patterns
- Performance optimization
- Security best practices
- Testing strategies

[...CONTENT TRUNCATED...]

For more information, visit our documentation portal.
```

### Crawl Summary Output
```
Crawled 5 pages from docs.example.com:

1. https://docs.example.com/ (depth: 0, 3,456 chars)
   Summary: Welcome to our documentation. This guide covers...

2. https://docs.example.com/quickstart (depth: 1, 2,890 chars)
   Summary: Quick Start Guide. Get up and running in 5 minutes...

3. https://docs.example.com/api (depth: 1, 4,567 chars)
   Summary: API Reference. Complete documentation of all endpoints...

Total content: 15,234 characters across 5 pages
```

## Performance Characteristics

- **Single page scrape**: ~300-500ms
- **10-page crawl**: ~2-3 seconds
- **Text extraction**: <50ms per page
- **Caching**: Subsequent requests ~10ms

## Best Practices

1. **Start with defaults** - The skill is optimized for single page scraping out of the box
2. **Use caching** - Enabled by default, saves time on repeated requests
3. **Set appropriate delays** - Be respectful of external sites (2+ seconds)
4. **Limit crawl scope** - Use `max_pages` and `max_depth` to control crawl size
5. **Use URL patterns** - Filter crawls with `follow_patterns` for focused results
6. **Monitor performance** - Check logs for timing and error information

## Limitations

- No JavaScript rendering (for speed)
- Basic text extraction only
- No authentication support
- No form submission
- Limited to HTML content
- No file downloads

## Error Handling

The skill handles common errors gracefully:
- **Timeouts**: Returns partial content with timeout notice
- **HTTP errors**: Reports status code and error message
- **Invalid URLs**: Clear error message
- **Rate limiting**: Respects 429 status codes
- **Network errors**: Returns descriptive error message

## Contributing

To enhance this skill:
1. Keep performance as the top priority
2. Maintain backward compatibility
3. Add tests for new features
4. Update this documentation
5. Consider token efficiency in outputs