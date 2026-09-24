"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Spider skill for fast web scraping with SignalWire AI Agents.
"""

import re
import collections
import time
import urllib.robotparser
from typing import Any, ClassVar, TYPE_CHECKING, cast
from urllib.parse import urljoin, urlparse
import requests
from lxml import html
from lxml.etree import XPathEvalError

from signalwire.core.skill_base import SkillBase
from signalwire.core.function_result import FunctionResult
from signalwire.utils.url_validator import _PublicSession

if TYPE_CHECKING:
    from signalwire.core.agent_base import AgentBase


class SpiderSkill(SkillBase):
    """Fast web scraping skill optimized for speed and token efficiency."""

    SKILL_NAME = "spider"
    SKILL_DESCRIPTION = "Fast web scraping and crawling capabilities"
    SKILL_VERSION = "1.0.0"
    REQUIRED_PACKAGES: ClassVar[list[str]] = [
        "lxml"
    ]  # beautifulsoup4 and requests are in base dependencies
    REQUIRED_ENV_VARS: ClassVar[list[str]] = []  # No required env vars by default
    SUPPORTS_MULTIPLE_INSTANCES = True

    # Compiled regex for performance
    WHITESPACE_REGEX = re.compile(r"\s+")

    # Each setting's default. get_parameter_schema() and __init__ both read
    # this, so the schema can't advertise a default the skill doesn't use.
    _DEFAULTS: ClassVar[dict[str, Any]] = {
        "delay": 0.1,
        "concurrent_requests": 5,
        "timeout": 5,
        "max_pages": 1,
        "max_depth": 0,
        "extract_type": "fast_text",
        "max_text_length": 3000,
        "clean_text": True,
        "cache_enabled": True,
        "follow_robots_txt": False,
        "user_agent": "Spider/1.0 (SignalWire AI Agent)",
    }

    # The extraction methods scrape_url implements
    _EXTRACT_TYPES: ClassVar[tuple[str, ...]] = ("fast_text", "markdown", "structured")

    # Values the schema once advertised but that were never implemented. They
    # have always worked as fast_text, so they still do, with a warning.
    _LEGACY_EXTRACT_TYPES: ClassVar[frozenset[str]] = frozenset(
        {"clean_text", "full_text", "html", "custom"}
    )

    @classmethod
    def get_parameter_schema(cls) -> dict[str, dict[str, Any]]:
        """Get parameter schema for Spider skill"""
        schema = super().get_parameter_schema()
        schema.update(
            {
                "delay": {
                    "type": "number",
                    "description": "Delay between requests in seconds",
                    "default": cls._DEFAULTS["delay"],
                    "required": False,
                    "min": 0.0,
                },
                "concurrent_requests": {
                    "type": "integer",
                    "description": "Deprecated, and has no effect: the spider fetches one page at a time",
                    "default": cls._DEFAULTS["concurrent_requests"],
                    "required": False,
                    "min": 1,
                    "max": 20,
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "default": cls._DEFAULTS["timeout"],
                    "required": False,
                    "min": 1,
                    "max": 60,
                },
                "max_pages": {
                    "type": "integer",
                    "description": "Maximum number of pages to scrape",
                    "default": cls._DEFAULTS["max_pages"],
                    "required": False,
                    "min": 1,
                    "max": 100,
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum crawl depth (0 = single page only)",
                    "default": cls._DEFAULTS["max_depth"],
                    "required": False,
                    "min": 0,
                    "max": 5,
                },
                "extract_type": {
                    "type": "string",
                    "description": "Content extraction method",
                    "default": cls._DEFAULTS["extract_type"],
                    "required": False,
                    "enum": list(cls._EXTRACT_TYPES),
                },
                "max_text_length": {
                    "type": "integer",
                    "description": "Maximum text length to return",
                    "default": cls._DEFAULTS["max_text_length"],
                    "required": False,
                    "min": 100,
                    "max": 100000,
                },
                "clean_text": {
                    "type": "boolean",
                    "description": "Whether to clean extracted text",
                    "default": cls._DEFAULTS["clean_text"],
                    "required": False,
                },
                "selectors": {
                    "type": "object",
                    "description": "Custom CSS/XPath selectors for extraction",
                    "default": {},
                    "required": False,
                    "additionalProperties": {"type": "string"},
                },
                "follow_patterns": {
                    "type": "array",
                    "description": "URL patterns to follow when crawling",
                    "default": [],
                    "required": False,
                    "items": {"type": "string"},
                },
                "user_agent": {
                    "type": "string",
                    "description": "User agent string for requests",
                    "default": cls._DEFAULTS["user_agent"],
                    "required": False,
                },
                "headers": {
                    "type": "object",
                    "description": "Additional HTTP headers",
                    "default": {},
                    "required": False,
                    "additionalProperties": {"type": "string"},
                },
                "follow_robots_txt": {
                    "type": "boolean",
                    "description": "Skip pages that the site's robots.txt disallows for user_agent",
                    "default": cls._DEFAULTS["follow_robots_txt"],
                    "required": False,
                },
                "cache_enabled": {
                    "type": "boolean",
                    "description": "Whether to cache scraped pages",
                    "default": cls._DEFAULTS["cache_enabled"],
                    "required": False,
                },
            }
        )
        return schema

    def __init__(self, agent: "AgentBase", params: dict[str, Any]):
        """Initialize the spider skill with configuration parameters."""
        super().__init__(agent, params)

        defaults = self._DEFAULTS

        # Performance settings
        self.delay = self.params.get("delay", defaults["delay"])
        self.concurrent_requests = self.params.get(
            "concurrent_requests", defaults["concurrent_requests"]
        )
        self.timeout = self.params.get("timeout", defaults["timeout"])

        # Crawling limits
        self.max_pages = self.params.get("max_pages", defaults["max_pages"])
        self.max_depth = self.params.get("max_depth", defaults["max_depth"])

        # Content processing
        self.extract_type = self.params.get("extract_type", defaults["extract_type"])
        self.max_text_length = self.params.get(
            "max_text_length", defaults["max_text_length"]
        )
        self.clean_text = self.params.get("clean_text", defaults["clean_text"])

        # Features
        self.cache_enabled = self.params.get("cache_enabled", defaults["cache_enabled"])
        self.follow_robots_txt = self.params.get(
            "follow_robots_txt", defaults["follow_robots_txt"]
        )
        self.user_agent = self.params.get("user_agent", defaults["user_agent"])

        # robots.txt rules, per origin, with the time they expire, when
        # follow_robots_txt is on
        self._robots: dict[str, tuple[urllib.robotparser.RobotFileParser, float]] = {}

        # Optional headers
        self.headers = self.params.get("headers", {})
        self.headers["User-Agent"] = self.user_agent

        # Session for connection pooling. It refuses redirects and connections
        # to private or internal addresses, which a check before the fetch
        # can't catch.
        self.session = _PublicSession()
        self.session.headers.update(self.headers)

        # Cache for responses (bounded OrderedDict for LRU-style eviction)
        self._cache: collections.OrderedDict[str, requests.Response] | None = (
            collections.OrderedDict() if self.cache_enabled else None
        )
        self._cache_max_size = 100

        # XPath expressions for unwanted elements
        self.remove_xpaths = [
            "//script",
            "//style",
            "//nav",
            "//header",
            "//footer",
            "//aside",
            "//noscript",
        ]

    def get_instance_key(self) -> str:
        """Return unique key for this skill instance."""
        tool_name = self.params.get("tool_name", self.SKILL_NAME)
        return f"{self.SKILL_NAME}_{tool_name}"

    def setup(self) -> bool:
        """Validate configuration and setup the skill."""
        # Validate delay is reasonable
        if self.delay < 0:
            self.logger.error("Delay cannot be negative")
            return False

        # Validate concurrent requests
        if not 1 <= self.concurrent_requests <= 20:
            self.logger.error("Concurrent requests must be between 1 and 20")
            return False
        if "concurrent_requests" in self.params:
            self.logger.warning(
                "concurrent_requests is deprecated and has no effect: the spider "
                "fetches one page at a time"
            )

        # Validate the extraction method
        if self.extract_type in self._LEGACY_EXTRACT_TYPES:
            self.logger.warning(
                f"extract_type '{self.extract_type}' was never implemented and works "
                f"as fast_text; use one of {', '.join(self._EXTRACT_TYPES)}"
            )
            self.extract_type = "fast_text"
        elif self.extract_type not in self._EXTRACT_TYPES:
            self.logger.error(
                f"Unknown extract_type '{self.extract_type}'; use one of "
                f"{', '.join(self._EXTRACT_TYPES)}"
            )
            return False

        # Validate max pages and depth
        if self.max_pages < 1:
            self.logger.error("Max pages must be at least 1")
            return False

        if self.max_depth < 0:
            self.logger.error("Max depth cannot be negative")
            return False

        # Pre-compile follow patterns for performance
        self._compiled_follow_patterns = []
        follow_patterns = self.params.get("follow_patterns", [])
        for pattern in follow_patterns:
            try:
                self._compiled_follow_patterns.append(re.compile(pattern))
            except re.error as e:  # noqa: PERF203  # per-iteration error isolation: one invalid pattern must not abort compiling the rest
                self.logger.error(f"Invalid follow pattern '{pattern}': {e}")

        self.logger.info(
            f"Spider skill configured: delay={self.delay}s, max_pages={self.max_pages}, max_depth={self.max_depth}"
        )
        return True

    def register_tools(self) -> None:
        """Register the web scraping tools with the agent."""
        # Tool name prefix for multiple instances
        tool_prefix = self.params.get("tool_name", "")
        if tool_prefix:
            tool_prefix = f"{tool_prefix}_"

        # Register scrape_url tool
        self.define_tool(
            name=f"{tool_prefix}scrape_url",
            description="Extract text content from a single web page",
            parameters={"url": {"type": "string", "description": "The URL to scrape"}},
            required=["url"],
            handler=self._scrape_url_handler,
        )

        # Register crawl_site tool
        self.define_tool(
            name=f"{tool_prefix}crawl_site",
            description="Crawl multiple pages starting from a URL",
            parameters={
                "start_url": {
                    "type": "string",
                    "description": "Starting URL for the crawl",
                }
            },
            required=["start_url"],
            handler=self._crawl_site_handler,
        )

        # Register extract_structured_data tool
        self.define_tool(
            name=f"{tool_prefix}extract_structured_data",
            description="Extract specific data from a web page using selectors",
            parameters={"url": {"type": "string", "description": "The URL to scrape"}},
            required=["url"],
            handler=self._extract_structured_handler,
        )

    # How long to keep a site's robots.txt rules. RFC 9309 allows caching
    # them for up to 24 hours. A failed fetch isn't cached at all.
    _ROBOTS_TTL = 24 * 60 * 60

    def _allowed_by_robots(self, url: str) -> bool:
        """False if follow_robots_txt is on and the site's robots.txt disallows url.

        As in urllib.robotparser, a robots.txt answered with 401 or 403
        disallows everything, any other 4xx allows everything, and a
        server error or failed request disallows everything until the next
        request retries it.
        """
        if not self.follow_robots_txt:
            return True
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        cached = self._robots.get(origin)
        if cached is not None and cached[1] > time.monotonic():
            return cached[0].can_fetch(self.user_agent, url)

        parser = urllib.robotparser.RobotFileParser()
        try:
            response = self.session.get(f"{origin}/robots.txt", timeout=self.timeout)
            status = response.status_code
        except requests.exceptions.RequestException:
            status = 599
        if status >= 500:
            # Unavailable for now: disallow this request, and retry next time
            return False
        if status in (401, 403):
            parser.parse(["User-agent: *", "Disallow: /"])
        elif status >= 400:
            parser.parse([])  # no rules: everything is allowed
        else:
            parser.parse(response.text.splitlines())
        self._robots[origin] = (parser, time.monotonic() + self._ROBOTS_TTL)
        return parser.can_fetch(self.user_agent, url)

    # Redirects to follow in one fetch while checking robots.txt
    _MAX_REDIRECTS = 10

    def _get_following_robots(self, url: str) -> requests.Response | None:
        """GET url, following each redirect only if robots.txt allows its target."""
        response = self.session.get(url, timeout=self.timeout, allow_redirects=False)
        for _ in range(self._MAX_REDIRECTS):
            if not response.is_redirect:
                return response
            target = urljoin(response.url, response.headers["location"])
            if not self._allowed_by_robots(target):
                self.logger.info(f"robots.txt disallows the redirect to {target}")
                return None
            response = self.session.get(
                target, timeout=self.timeout, allow_redirects=False
            )
        self.logger.error(f"Too many redirects fetching {url}")
        return None

    def _fetch_url(self, url: str) -> requests.Response | None:
        """Fetch a URL with caching and error handling."""
        # Check cache first
        if self.cache_enabled and self._cache is not None and url in self._cache:
            self.logger.debug(f"Cache hit for {url}")
            return self._cache[url]

        try:
            if self.follow_robots_txt:
                # Each redirect's target needs its own robots.txt check
                fetched = self._get_following_robots(url)
                if fetched is None:
                    return None
                response = fetched
            else:
                response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Cache successful responses (with size limit)
            if self.cache_enabled and self._cache is not None:
                if len(self._cache) >= self._cache_max_size:
                    self._cache.popitem(last=False)  # Evict oldest
                self._cache[url] = response

            return response

        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout fetching {url}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None

    def _fast_text_extract(self, response: requests.Response) -> str:
        """Ultra-fast text extraction using lxml."""
        try:
            # Parse HTML with lxml
            tree = html.fromstring(response.content)

            # Remove unwanted elements in one pass
            for xpath in self.remove_xpaths:
                for elem in tree.xpath(xpath):
                    elem.drop_tree()

            # Extract text. lxml has no type stubs, so text_content() is Any;
            # it returns the element's concatenated text as a str.
            text = cast(str, tree.text_content())

            # Clean whitespace if requested
            if self.clean_text:
                text = self.WHITESPACE_REGEX.sub(" ", text).strip()

            # Smart truncation
            if len(text) > self.max_text_length:
                keep_start = self.max_text_length * 2 // 3
                keep_end = self.max_text_length // 3
                text = (
                    text[:keep_start]
                    + "\n\n[...CONTENT TRUNCATED...]\n\n"
                    + text[-keep_end:]
                )

            return text

        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return ""

    def _markdown_extract(self, response: requests.Response) -> str:
        """Extract content in markdown format."""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove unwanted tags
            for tag in ["script", "style", "nav", "header", "footer", "aside"]:
                for elem in soup.find_all(tag):
                    elem.decompose()

            # Convert to markdown-like format
            text_parts = []

            # Title
            title = soup.find("title")
            if title:
                text_parts.append(f"# {title.get_text().strip()}\n")

            # Main content
            for elem in soup.find_all(
                ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "code", "pre"]
            ):
                if elem.name.startswith("h"):
                    level = int(elem.name[1])
                    text_parts.append(f"\n{'#' * level} {elem.get_text().strip()}\n")
                elif elem.name == "p":
                    text_parts.append(f"\n{elem.get_text().strip()}\n")
                elif elem.name == "li":
                    text_parts.append(f"- {elem.get_text().strip()}")
                elif elem.name in ["code", "pre"]:
                    text_parts.append(f"\n```\n{elem.get_text().strip()}\n```\n")

            text = "\n".join(text_parts)

            # Truncate if needed
            if len(text) > self.max_text_length:
                text = text[: self.max_text_length] + "\n\n[...TRUNCATED...]"

            return text

        except ImportError:
            self.logger.warning(
                "BeautifulSoup not available, falling back to fast_text"
            )
            return self._fast_text_extract(response)
        except Exception as e:
            self.logger.error(f"Error in markdown extraction: {e}")
            return self._fast_text_extract(response)

    def _structured_extract(
        self, response: requests.Response, selectors: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Extract structured data using selectors."""
        try:
            tree = html.fromstring(response.content)
            result: dict[str, Any] = {
                "url": response.url,
                "status_code": response.status_code,
                "title": "",
                "data": {},
            }

            # Get title
            title_elem = tree.xpath("//title/text()")
            if title_elem:
                result["title"] = title_elem[0].strip()

            # Extract using provided selectors
            if selectors:
                for field, selector in selectors.items():
                    try:
                        if selector.startswith("/"):  # XPath
                            values = tree.xpath(selector)
                        else:  # CSS selector
                            from lxml.cssselect import CSSSelector

                            sel = CSSSelector(selector)
                            values = sel(tree)

                        # Extract text from elements
                        if values:
                            if len(values) == 1:
                                result["data"][field] = values[0].text_content().strip()
                            else:
                                result["data"][field] = [
                                    v.text_content().strip() for v in values
                                ]
                    except (XPathEvalError, Exception) as e:  # noqa: PERF203  # per-iteration error isolation: one bad selector must not abort extracting the other fields
                        self.logger.warning(f"Error with selector {selector}: {e}")
                        result["data"][field] = None

            return result

        except Exception as e:
            self.logger.error(f"Error in structured extraction: {e}")
            return {"error": str(e)}

    def _scrape_url_handler(
        self, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        """Handle single page scraping."""
        url = args.get("url", "").strip()
        if not url:
            return FunctionResult("Please provide a URL to scrape")

        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return FunctionResult(f"Invalid URL: {url}")

        # SSRF protection
        from signalwire.utils.url_validator import validate_url

        if not validate_url(url):
            return FunctionResult(
                "URL rejected: cannot access private or internal URLs"
            )

        if not self._allowed_by_robots(url):
            return FunctionResult(f"The site's robots.txt disallows fetching {url}")

        # Fetch the page
        response = self._fetch_url(url)
        if not response:
            return FunctionResult(f"Failed to fetch {url}")

        # Extract content based on configured type (not from args)
        extract_type = self.extract_type

        try:
            if extract_type == "structured":
                # For structured extraction, use predefined selectors from config if available
                selectors = self.params.get("selectors", {})
                result = self._structured_extract(response, selectors)
                return FunctionResult(f"Extracted structured data from {url}: {result}")
            if extract_type == "markdown":
                content = self._markdown_extract(response)
            else:  # fast_text (default)
                content = self._fast_text_extract(response)

            if not content:
                return FunctionResult(f"No content extracted from {url}")

            # Format response
            char_count = len(content)
            header = f"Content from {url} ({char_count} characters):\n\n"

            return FunctionResult(header + content)

        except Exception as e:
            self.logger.error(f"Error processing {url}: {e}")
            return FunctionResult(f"Error processing {url}: {e!s}")

    def _crawl_site_handler(
        self, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        """Handle multi-page crawling."""
        start_url = args.get("start_url", "").strip()
        if not start_url:
            return FunctionResult("Please provide a starting URL for the crawl")

        # SSRF protection
        from signalwire.utils.url_validator import validate_url

        if not validate_url(start_url):
            return FunctionResult(
                "URL rejected: cannot access private or internal URLs"
            )

        # Use configured parameters (not from args)
        max_depth = self.max_depth
        max_pages = self.max_pages
        follow_patterns = (
            self._compiled_follow_patterns
            if hasattr(self, "_compiled_follow_patterns")
            else []
        )

        # Validate parameters
        if max_depth < 0:
            return FunctionResult("Max depth cannot be negative")
        if max_pages < 1:
            return FunctionResult("Max pages must be at least 1")

        # Simple breadth-first crawl
        visited: set[Any] = set[Any]()
        disallowed: set[str] = set()
        to_visit = [(start_url, 0)]  # (url, depth)
        results = []

        while to_visit and len(visited) < max_pages:
            if not to_visit:
                break

            url, depth = to_visit.pop(0)

            # Skip if already visited, disallowed, or depth exceeded
            if url in visited or url in disallowed or depth > max_depth:
                continue

            if not self._allowed_by_robots(url):
                self.logger.info(f"robots.txt disallows {url}; skipping it")
                disallowed.add(url)
                continue

            # Fetch and process page
            response = self._fetch_url(url)
            if not response:
                continue

            visited.add(url)

            # Extract content
            content = self._fast_text_extract(response)
            if content:
                results.append(
                    {
                        "url": url,
                        "depth": depth,
                        "content_length": len(content),
                        "summary": content[:500] + "..."
                        if len(content) > 500
                        else content,
                    }
                )

            # Extract links if not at max depth
            if depth < max_depth:
                try:
                    tree = html.fromstring(response.content)
                    links = tree.xpath("//a[@href]/@href")

                    for link in links:
                        absolute_url = urljoin(url, link)

                        # Check if we should follow this link
                        if follow_patterns and not any(
                            pattern.search(absolute_url) for pattern in follow_patterns
                        ):
                            continue

                        # Only follow same domain by default
                        if (
                            urlparse(absolute_url).netloc == urlparse(start_url).netloc
                            and absolute_url not in visited
                        ):
                            to_visit.append((absolute_url, depth + 1))

                except Exception as e:
                    self.logger.warning(f"Error extracting links from {url}: {e}")

            # Respect delay between requests
            if self.delay > 0 and len(visited) < max_pages:
                import time

                time.sleep(self.delay)

        # Format results
        if not results:
            return FunctionResult(f"No pages could be crawled from {start_url}")

        summary = f"Crawled {len(results)} pages from {urlparse(start_url).netloc}:\n\n"

        for i, result in enumerate(results, 1):
            summary += f"{i}. {result['url']} (depth: {result['depth']}, {result['content_length']} chars)\n"
            summary += f"   Summary: {result['summary'][:100]}...\n\n"

        total_chars = sum(r["content_length"] for r in results)
        summary += (
            f"\nTotal content: {total_chars:,} characters across {len(results)} pages"
        )

        return FunctionResult(summary)

    def _extract_structured_handler(
        self, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        """Handle structured data extraction."""
        url = args.get("url", "").strip()

        if not url:
            return FunctionResult("Please provide a URL")

        # SSRF protection
        from signalwire.utils.url_validator import validate_url

        if not validate_url(url):
            return FunctionResult(
                "URL rejected: cannot access private or internal URLs"
            )

        # Use configured selectors from params
        selectors = self.params.get("selectors", {})
        if not selectors:
            return FunctionResult(
                "No selectors configured for structured data extraction"
            )

        if not self._allowed_by_robots(url):
            return FunctionResult(f"The site's robots.txt disallows fetching {url}")

        # Fetch the page
        response = self._fetch_url(url)
        if not response:
            return FunctionResult(f"Failed to fetch {url}")

        # Extract structured data
        result = self._structured_extract(response, selectors)

        if "error" in result:
            return FunctionResult(f"Error extracting data: {result['error']}")

        # Format the response
        output = f"Extracted data from {url}:\n\n"
        output += f"Title: {result.get('title', 'N/A')}\n\n"

        if result.get("data"):
            output += "Data:\n"
            for field, value in result["data"].items():
                output += f"- {field}: {value}\n"
        else:
            output += "No data extracted with provided selectors"

        return FunctionResult(output)

    def get_hints(self) -> list[str]:
        """Return speech recognition hints for this skill."""
        return [
            "scrape",
            "crawl",
            "extract",
            "web page",
            "website",
            "get content from",
            "fetch data from",
            "spider",
        ]

    def cleanup(self) -> None:
        """Clean up resources when skill is unloaded."""
        if hasattr(self, "session"):
            self.session.close()
        if hasattr(self, "_cache") and self._cache is not None:
            self._cache.clear()
        self.logger.info("Spider skill cleaned up")
