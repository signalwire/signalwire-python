"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import os
import requests
import time
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
from typing import Optional, List, Dict, Any, Tuple

from signalwire.core.skill_base import SkillBase
from signalwire.core.function_result import FunctionResult

class GoogleSearchScraper:
    """Google Search and Web Scraping functionality with quality scoring"""

    def __init__(self, api_key: str, search_engine_id: str, max_content_length: int = 32768):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.max_content_length = max_content_length
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_google(self, query: str, num_results: int = 5) -> list:
        """Search Google using Custom Search JSON API"""
        url = "https://www.googleapis.com/customsearch/v1"

        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': min(num_results, 10)
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'items' not in data:
                return []

            results = []
            for item in data['items'][:num_results]:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })

            return results

        except Exception as e:
            return []

    def extract_text_from_url(self, url: str, content_limit: int = None, timeout: int = 10) -> Tuple[str, Dict[str, Any]]:
        """
        Scrape a URL and extract readable text content with quality metrics

        Returns:
            Tuple of (text_content, quality_metrics)
        """
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract main content areas (common content selectors)
            main_content = None
            content_selectors = [
                'article', 'main', '[role="main"]', '.content', '#content',
                '.post', '.entry-content', '.article-body', '.story-body',
                '.markdown-body', '.wiki-body', '.documentation'
            ]

            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break

            # If no main content found, use the whole body
            if not main_content:
                main_content = soup.find('body') or soup

            # Clone for processing
            content_soup = BeautifulSoup(str(main_content), 'html.parser')

            # Remove unwanted elements from the content area
            unwanted_tags = ["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe"]
            for tag in unwanted_tags:
                for element in content_soup(tag):
                    element.decompose()

            # Remove elements with unwanted classes/ids
            unwanted_patterns = [
                'sidebar', 'navigation', 'menu', 'advertisement', 'ads', 'banner',
                'popup', 'modal', 'cookie', 'gdpr', 'subscribe', 'newsletter',
                'comments', 'related', 'share', 'social'
            ]

            for pattern in unwanted_patterns:
                # Remove by class
                for element in content_soup.find_all(class_=re.compile(pattern, re.I)):
                    element.decompose()
                # Remove by id
                for element in content_soup.find_all(id=re.compile(pattern, re.I)):
                    element.decompose()

            # Extract text
            text = content_soup.get_text()

            # Clean up the text
            lines = [line.strip() for line in text.splitlines()]
            # Remove empty lines and join
            lines = [line for line in lines if line]
            text = ' '.join(lines)

            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text).strip()

            # Calculate quality metrics
            quality_metrics = self._calculate_content_quality(text, url)

            # Limit text length
            limit = content_limit if content_limit is not None else self.max_content_length
            if len(text) > limit:
                text = text[:limit]

            return text, quality_metrics

        except Exception as e:
            return "", {"error": str(e), "quality_score": 0}

    def _calculate_content_quality(self, text: str, url: str) -> Dict[str, Any]:
        """
        Calculate quality metrics for extracted content

        Quality factors:
        - Text length (substantive content)
        - Word diversity (not repetitive)
        - Sentence structure (proper formatting)
        - Lack of boilerplate phrases
        - Domain reputation
        """
        if not text:
            return {"quality_score": 0, "text_length": 0}

        metrics = {}

        # Text length (prefer 500-5000 chars of actual content)
        text_length = len(text)
        metrics['text_length'] = text_length
        if text_length < 100:
            length_score = 0
        elif text_length < 500:
            length_score = text_length / 500
        elif text_length <= 5000:
            length_score = 1.0
        else:
            length_score = max(0.7, 1.0 - (text_length - 5000) / 10000)

        # Word diversity (unique words / total words)
        words = text.lower().split()
        if words:
            unique_words = len(set(words))
            total_words = len(words)
            diversity_score = min(1.0, unique_words / (total_words * 0.4))  # Expect 40% unique
            metrics['word_diversity'] = unique_words / total_words if total_words > 0 else 0
        else:
            diversity_score = 0
            metrics['word_diversity'] = 0

        # Check for boilerplate/navigation text
        boilerplate_phrases = [
            'cookie', 'privacy policy', 'terms of service', 'subscribe',
            'sign up', 'log in', 'advertisement', 'sponsored', 'copyright',
            'all rights reserved', 'skip to', 'navigation', 'breadcrumb',
            'reddit inc', 'google llc', 'expand navigation'
        ]

        lower_text = text.lower()
        boilerplate_count = sum(1 for phrase in boilerplate_phrases if phrase in lower_text)
        boilerplate_penalty = max(0, 1.0 - (boilerplate_count * 0.1))  # -10% per boilerplate phrase
        metrics['boilerplate_count'] = boilerplate_count

        # Sentence detection (properly formed content)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if len(s.strip()) > 20])
        sentence_score = min(1.0, sentence_count / 5)  # At least 5 sentences
        metrics['sentence_count'] = sentence_count

        # Domain quality (prefer known content sites)
        domain = urlparse(url).netloc.lower()
        quality_domains = [
            'wikipedia.org', 'stackexchange.com', 'stackoverflow.com',
            'github.com', 'medium.com', 'dev.to', 'arxiv.org',
            'nature.com', 'sciencedirect.com', 'ieee.org'
        ]

        low_quality_domains = [
            'reddit.com', 'youtube.com', 'facebook.com', 'twitter.com',
            'instagram.com', 'pinterest.com'
        ]

        if any(d in domain for d in quality_domains):
            domain_score = 1.2  # Bonus for quality domains
        elif any(d in domain for d in low_quality_domains):
            domain_score = 0.5  # Penalty for social media (often poor extraction)
        else:
            domain_score = 1.0

        metrics['domain'] = domain

        # Calculate final quality score
        quality_score = (
            length_score * 0.3 +
            diversity_score * 0.2 +
            boilerplate_penalty * 0.2 +
            sentence_score * 0.2 +
            domain_score * 0.1
        )

        metrics['quality_score'] = round(quality_score, 3)
        metrics['length_score'] = round(length_score, 3)
        metrics['diversity_score'] = round(diversity_score, 3)
        metrics['boilerplate_penalty'] = round(boilerplate_penalty, 3)
        metrics['sentence_score'] = round(sentence_score, 3)
        metrics['domain_score'] = round(domain_score, 3)

        return metrics

    def search_and_scrape_best(self, query: str, num_results: int = 3,
                               oversample_factor: float = 2.5, delay: float = 0.5,
                               min_quality_score: float = 0.3) -> str:
        """
        Search and scrape with quality filtering

        Args:
            query: Search query
            num_results: Number of best results to return
            oversample_factor: How many extra results to fetch (e.g., 2.5 = fetch 2.5x)
            delay: Delay between requests
            min_quality_score: Minimum quality score to include a result

        Returns:
            Formatted string with the best N results
        """
        # Fetch more results than requested
        fetch_count = min(10, int(num_results * oversample_factor))
        search_results = self.search_google(query, fetch_count)

        if not search_results:
            return f"No search results found for query: {query}"

        # Process all results and collect quality metrics
        processed_results = []

        for result in search_results:
            # Extract content and quality metrics
            page_text, metrics = self.extract_text_from_url(result['url'])

            if metrics.get('quality_score', 0) >= min_quality_score and page_text:
                processed_results.append({
                    'title': result['title'],
                    'url': result['url'],
                    'snippet': result['snippet'],
                    'content': page_text,
                    'metrics': metrics,
                    'quality_score': metrics.get('quality_score', 0)
                })

            # Small delay between requests
            if delay > 0:
                time.sleep(delay)

        # Sort by quality score and take top N
        processed_results.sort(key=lambda x: x['quality_score'], reverse=True)
        best_results = processed_results[:num_results]

        if not best_results:
            return f"No quality results found for query: {query}. Try a different search term."

        # Calculate per-result content budget for the best results
        estimated_overhead_per_result = 400  # Including quality info
        total_overhead = len(best_results) * estimated_overhead_per_result
        available_for_content = self.max_content_length - total_overhead
        per_result_limit = max(1000, available_for_content // len(best_results))

        # Format the best results
        all_text = []
        all_text.append(f"Found {len(processed_results)} quality results from {len(search_results)} searched. Showing top {len(best_results)}:\n")

        for i, result in enumerate(best_results, 1):
            text_content = f"=== RESULT {i} (Quality: {result['quality_score']:.2f}) ===\n"
            text_content += f"Title: {result['title']}\n"
            text_content += f"URL: {result['url']}\n"
            text_content += f"Snippet: {result['snippet']}\n"

            # Add quality indicators
            metrics = result['metrics']
            text_content += f"Content Quality: {metrics.get('text_length', 0)} chars, "
            text_content += f"{metrics.get('sentence_count', 0)} sentences, "
            text_content += f"diversity: {metrics.get('word_diversity', 0):.2f}\n"
            text_content += f"Content:\n"

            # Truncate content if needed
            content = result['content']
            if len(content) > per_result_limit:
                content = content[:per_result_limit] + "..."
            text_content += content

            text_content += f"\n{'='*50}\n\n"
            all_text.append(text_content)

        return '\n'.join(all_text)

    def search_and_scrape(self, query: str, num_results: int = 3, delay: float = 0.5) -> str:
        """
        Backward compatible method that uses the improved search
        """
        return self.search_and_scrape_best(
            query=query,
            num_results=num_results,
            oversample_factor=2.5,
            delay=delay,
            min_quality_score=0.3
        )


class WebSearchSkill(SkillBase):
    """Web search capability using Google Custom Search API with quality filtering"""

    SKILL_NAME = "web_search"
    SKILL_DESCRIPTION = "Search the web for information using Google Custom Search API"
    SKILL_VERSION = "2.0.0"  # Bumped version for improved functionality
    REQUIRED_PACKAGES = ["bs4", "requests"]
    REQUIRED_ENV_VARS = []

    # Enable multiple instances support
    SUPPORTS_MULTIPLE_INSTANCES = True

    def get_instance_key(self) -> str:
        """Get the key used to track this skill instance"""
        search_engine_id = self.params.get('search_engine_id', 'default')
        tool_name = self.params.get('tool_name', 'web_search')
        return f"{self.SKILL_NAME}_{search_engine_id}_{tool_name}"

    def setup(self) -> bool:
        """Setup the web search skill"""
        # Validate required parameters
        required_params = ['api_key', 'search_engine_id']
        missing_params = [param for param in required_params if not self.params.get(param)]
        if missing_params:
            self.logger.error(f"Missing required parameters: {missing_params}")
            return False

        if not self.validate_packages():
            return False

        # Set parameters from config
        self.api_key = self.params['api_key']
        self.search_engine_id = self.params['search_engine_id']

        # Set default parameters
        self.default_num_results = self.params.get('num_results', 3)
        self.default_delay = self.params.get('delay', 0.5)
        self.max_content_length = self.params.get('max_content_length', 32768)

        # Quality control parameters (new)
        self.oversample_factor = self.params.get('oversample_factor', 2.5)
        self.min_quality_score = self.params.get('min_quality_score', 0.3)

        self.no_results_message = self.params.get('no_results_message',
            "I couldn't find quality results for '{query}'. "
            "The search returned only low-quality or inaccessible pages. "
            "Try rephrasing your search or asking about a different topic."
        )

        # Tool name (for multiple instances)
        self.tool_name = self.params.get('tool_name', 'web_search')

        # Initialize the improved search scraper
        self.search_scraper = GoogleSearchScraper(
            api_key=self.api_key,
            search_engine_id=self.search_engine_id,
            max_content_length=self.max_content_length
        )

        return True

    def register_tools(self) -> None:
        """Register web search tool with the agent"""
        self.define_tool(
            name=self.tool_name,
            description="Search the web for high-quality information, automatically filtering low-quality results",
            parameters={
                "query": {
                    "type": "string",
                    "description": "The search query - what you want to find information about"
                }
            },
            handler=self._web_search_handler
        )

    def _web_search_handler(self, args, raw_data):
        """Handler for web search tool with quality filtering"""
        query = args.get("query", "").strip()

        if not query:
            return FunctionResult(
                "Please provide a search query. What would you like me to search for?"
            )

        # Use the configured number of results
        num_results = self.default_num_results

        self.logger.info(f"Web search requested: '{query}' (requesting {num_results} quality results)")

        # Perform the improved search
        try:
            search_results = self.search_scraper.search_and_scrape_best(
                query=query,
                num_results=num_results,
                oversample_factor=self.oversample_factor,
                delay=self.default_delay,
                min_quality_score=self.min_quality_score
            )

            if not search_results or "No quality results found" in search_results or "No search results found" in search_results:
                formatted_message = self.no_results_message.format(query=query) if '{query}' in self.no_results_message else self.no_results_message
                return FunctionResult(formatted_message)

            response = f"Quality web search results for '{query}':\n\n{search_results}"
            return FunctionResult(response)

        except Exception as e:
            self.logger.error(f"Error performing web search: {e}")
            return FunctionResult(
                "Sorry, I encountered an error while searching. Please try again later."
            )

    def get_hints(self) -> List[str]:
        """Return speech recognition hints"""
        return []

    def get_global_data(self) -> Dict[str, Any]:
        """Return global data for agent context"""
        return {
            "web_search_enabled": True,
            "search_provider": "Google Custom Search",
            "quality_filtering": True
        }

    def get_prompt_sections(self) -> List[Dict[str, Any]]:
        """Return prompt sections to add to agent"""
        return [
            {
                "title": "Web Search Capability (Quality Enhanced)",
                "body": f"You can search the internet for high-quality information using the {self.tool_name} tool.",
                "bullets": [
                    f"Use the {self.tool_name} tool when users ask for information you need to look up",
                    "The search automatically filters out low-quality results like empty pages",
                    "Results are ranked by content quality, relevance, and domain reputation",
                    "Summarize the high-quality results in a clear, helpful way"
                ]
            }
        ]

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Dict[str, Any]]:
        """Get the parameter schema for the web search skill"""
        schema = super().get_parameter_schema()

        # Add web search specific parameters
        schema.update({
            "api_key": {
                "type": "string",
                "description": "Google Custom Search API key",
                "required": True,
                "hidden": True,
                "env_var": "GOOGLE_SEARCH_API_KEY"
            },
            "search_engine_id": {
                "type": "string",
                "description": "Google Custom Search Engine ID",
                "required": True,
                "hidden": True,
                "env_var": "GOOGLE_SEARCH_ENGINE_ID"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of high-quality results to return",
                "default": 3,
                "required": False,
                "min": 1,
                "max": 10
            },
            "delay": {
                "type": "number",
                "description": "Delay between scraping pages in seconds",
                "default": 0.5,
                "required": False,
                "min": 0
            },
            "max_content_length": {
                "type": "integer",
                "description": "Maximum total response size in characters",
                "default": 32768,
                "required": False,
                "min": 1000
            },
            "oversample_factor": {
                "type": "number",
                "description": "How many extra results to fetch for quality filtering (e.g., 2.5 = fetch 2.5x requested)",
                "default": 2.5,
                "required": False,
                "min": 1.0,
                "max": 3.5
            },
            "min_quality_score": {
                "type": "number",
                "description": "Minimum quality score (0-1) for including a result",
                "default": 0.3,
                "required": False,
                "min": 0.0,
                "max": 1.0
            },
            "no_results_message": {
                "type": "string",
                "description": "Message to show when no quality results are found. Use {query} as placeholder.",
                "default": "I couldn't find quality results for '{query}'. The search returned only low-quality or inaccessible pages. Try rephrasing your search or asking about a different topic.",
                "required": False
            }
        })

        return schema