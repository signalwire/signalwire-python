# Spider Skill

Fast web scraping and crawling capabilities for SignalWire AI Agents. Optimized for speed and token efficiency.

## Features

The skill covers these capabilities:

- **Single page scraping** - Extract content from any web page
- **Multi-page crawling** - Follow links and crawl entire sections of websites
- **Structured data extraction** - Extract specific data using CSS/XPath selectors
- **Multiple output formats** - Plain text, markdown, or structured JSON
- **Smart text truncation** - Intelligently truncate long content while preserving key information
- **Response caching** - Cache pages to avoid redundant requests
- **Configurable crawling** - Control depth, page limits, and URL patterns

## Installation

Add the skill with no parameters for single-page scraping, or configure crawling limits directly:

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

These parameters are set once with `add_skill()`; the tools themselves take only a URL, listed in [Available Tools](#available-tools).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `delay` | float | 0.1 | Seconds between requests |
| `concurrent_requests` | int | 5 | Deprecated, and has no effect: the spider fetches one page at a time. Setting it logs a warning |
| `timeout` | int | 5 | Request timeout in seconds |
| `max_pages` | int | 1 | Maximum pages to crawl |
| `max_depth` | int | 0 | How many links deep to crawl |
| `extract_type` | string | "fast_text" | Extraction method: "fast_text", "markdown", or "structured". Any other value stops the skill from loading |
| `selectors` | dict | {} | CSS/XPath selectors, used by `extract_structured_data` and by `scrape_url` when `extract_type` is "structured" |
| `follow_patterns` | list | [] | Regex patterns limiting which links `crawl_site` follows |
| `max_text_length` | int | 3000 | Maximum characters per page |
| `clean_text` | bool | True | Remove extra whitespace |
| `cache_enabled` | bool | True | Enable response caching |
| `follow_robots_txt` | bool | False | Skip pages, and redirects to pages, that the site's robots.txt disallows for `user_agent`. Rules are kept for 24 hours. If robots.txt can't be fetched, the page is skipped and the next request tries again |
| `user_agent` | string | "Spider/1.0 (SignalWire AI Agent)" | User agent string |
| `headers` | dict | {} | Additional HTTP headers |

## Available Tools

### scrape_url

Extract text content from a single web page.

**Parameters:**
- `url` (required): The URL to scrape

The extraction method and any selectors come from the skill's `extract_type` and `selectors` configuration, not from the call.

These are example requests a caller might make:

```text
"Please get the content from https://example.com/article"
"Scrape the main text from https://docs.example.com in markdown format"
"Extract the product price from this page using the .price selector"
```

### crawl_site

Crawl multiple pages starting from a URL.

**Parameters:**
- `start_url` (required): Starting URL for the crawl

The crawl depth, page limit, and link patterns come from the skill's `max_depth`, `max_pages`, and `follow_patterns` configuration, not from the call.

These are example requests a caller might make:

```text
"Crawl the documentation starting from /docs with depth 2"
"Get all blog posts from the site, following only /blog/ URLs"
"Crawl up to 20 pages from their support section"
```

### extract_structured_data

Extract specific data from a web page using selectors.

**Parameters:**
- `url` (required): The URL to scrape

The selectors come from the skill's `selectors` configuration, set with `add_skill()`. The tool returns a message instead of data if none are configured.

These are example requests a caller might make:

```text
"Extract the title, price, and description from this product page"
"Get all the email addresses and phone numbers from the contact page"
```

## Usage Examples

### Basic Single Page Scraping (Default)

With no parameters, the skill scrapes a single page per call:

```python
agent.add_skill("spider")
# AI can now: "Get the content from https://example.com"
```

### Documentation Crawling

This configuration crawls deeper and formats pages as markdown:

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

This configuration favors more pages and shorter per-page content over a low delay:

```python
agent.add_skill("spider", {
    "delay": 0.05,
    "max_pages": 20,
    "max_text_length": 1000,
    "cache_enabled": True
})
# AI can now: "Get the latest articles from the news section"
```

### Respectful External Scraping

This configuration adds a longer delay and honors `robots.txt`:

```python
agent.add_skill("spider", {
    "delay": 2.0,
    "follow_robots_txt": True,
    "user_agent": "MyBot/1.0 (contact@example.com)"
})
# AI can now: "Carefully scrape competitor pricing data"
```

### Multiple Spider Instances

Each call to `add_skill` with a distinct `tool_name` registers a separate set of tools:

```python
# Fast spider for internal sites
agent.add_skill("spider", {
    "tool_name": "fast_spider",
    "delay": 0.1
})

# Slow spider for external sites
agent.add_skill("spider", {
    "tool_name": "polite_spider",
    "delay": 2.0,
    "follow_robots_txt": True
})
# AI can now use: fast_spider_scrape_url() and polite_spider_scrape_url()
```

## Output Examples

### Fast Text Output (Default)

`scrape_url` returns a character count and the extracted text:

```text
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

`crawl_site` returns a numbered list of pages with a running total:

```text
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

A scrape takes about as long as the target site takes to respond, since fetching the page dominates the total time. Text extraction and formatting add comparatively little on top of that.

A cached page returns without a new request, since the skill serves it from its cache instead of fetching it again. A multi-page crawl takes longer as the page count and the configured delay increase.

## Best Practices

Keep these points in mind when you configure the skill:

1. **Start with defaults** - The skill is optimized for single page scraping out of the box
2. **Use caching** - Enabled by default, saves time on repeated requests
3. **Set appropriate delays** - Be respectful of external sites (2+ seconds)
4. **Limit crawl scope** - Use `max_pages` and `max_depth` to control crawl size
5. **Use URL patterns** - Filter crawls with `follow_patterns` for focused results
6. **Monitor performance** - Check logs for timing and error information

## Limitations

The skill does not cover these cases:

- No JavaScript rendering (for speed)
- Basic text extraction only
- No authentication support
- No form submission
- Limited to HTML content
- No file downloads

## Error Handling

The skill handles these cases:
- **Missing URL**: Prompts for a URL instead of failing
- **Invalid URLs**: Returns "Invalid URL: {url}" without making a request
- **Blocked URLs**: SSRF protection rejects a URL that resolves to a private or internal address. It also checks each redirect and each connection, so a public page that redirects to an internal address returns "Failed to fetch {url}". To allow private addresses, for example to crawl an internal site, set `SWML_ALLOW_PRIVATE_URLS=true`. The skill connects directly, ignoring `HTTP_PROXY` and `HTTPS_PROXY`, so that the check applies to each connection. To fetch through a proxy that blocks private destinations itself, set `SWML_URL_FETCH_USE_PROXY=true`.
- **Fetch failures**: Timeouts, HTTP errors (including 429), and connection errors all return "Failed to fetch {url}"; the specific error is logged, not returned to the caller

## Contributing

To enhance this skill:
1. Keep performance as the top priority
2. Maintain backward compatibility
3. Add tests for new features
4. Update this documentation
5. Consider token efficiency in outputs