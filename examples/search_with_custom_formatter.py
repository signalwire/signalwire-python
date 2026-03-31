#!/usr/bin/env python3
"""
Example: Native Vector Search with Custom Response Formatting

This example demonstrates how to use the response_format_callback parameter
to customize how search results are presented to users.
"""

from signalwire import AgentBase


def basic_formatter(response, agent, query, results, **kwargs):
    """Basic formatter that adds visual enhancements"""
    if not results:
        return f"🔍 No results found for '{query}'. Try a different search term or check the documentation."
    
    # Add header with result count
    formatted = f"🔍 **Search Results** ({len(results)} matches for '{query}')\n"
    formatted += "─" * 50 + "\n\n"
    formatted += response
    formatted += "\n" + "─" * 50
    
    return formatted


def advanced_formatter(response, agent, query, results, skill, **kwargs):
    """Advanced formatter that analyzes results and provides context"""
    if not results:
        # Suggest alternative searches
        suggestions = []
        words = query.split()
        if len(words) > 1:
            suggestions.append(f"Try searching for individual terms: {', '.join(words)}")
        suggestions.append("Use more general terms")
        suggestions.append("Check spelling and terminology")
        
        return (
            f"❌ No results found for '{query}'\n\n"
            f"💡 Suggestions:\n" + 
            "\n".join(f"  • {s}" for s in suggestions)
        )
    
    # Analyze result quality
    best_score = results[0]['score']
    avg_score = sum(r['score'] for r in results) / len(results)
    
    # Build enhanced response
    formatted = f"📚 Search Analysis for '{query}':\n"
    
    # Quality indicator
    if best_score > 0.9:
        formatted += "✅ **Excellent matches found!**\n"
    elif best_score > 0.7:
        formatted += "👍 **Good matches found**\n"
    else:
        formatted += "🔎 **Partial matches** (consider refining your search)\n"
    
    formatted += f"\n📊 Statistics: Best match: {best_score:.2%}, Average: {avg_score:.2%}\n\n"
    
    # Add the original response
    formatted += response
    
    # Extract unique topics/sections from results
    sections = set()
    for result in results:
        if 'section' in result.get('metadata', {}):
            sections.add(result['metadata']['section'])
    
    if sections:
        formatted += f"\n\n📑 **Sections covered**: {', '.join(sorted(sections))}"
    
    # Add follow-up suggestions based on score
    if avg_score < 0.5:
        formatted += "\n\n💡 **Tip**: Results have lower confidence. Try:\n"
        formatted += "  • Using different keywords\n"
        formatted += "  • Being more specific\n"
        formatted += "  • Breaking down complex queries"
    
    return formatted


def context_aware_formatter(response, agent, query, results, **kwargs):
    """Formatter that uses agent conversation context"""
    # This example shows how to access agent state
    formatted = ""
    
    # Check if this appears to be a follow-up question
    if hasattr(agent, 'last_search_query'):
        if agent.last_search_query and query != agent.last_search_query:
            formatted += f"📝 *Following up from your previous search about '{agent.last_search_query}'*\n\n"
    
    # Store current query for next time
    agent.last_search_query = query
    
    # Add the response
    formatted += response
    
    # Add contextual help based on result count
    if results:
        if len(results) == 1:
            formatted += "\n\n💡 This is the only result I found. Would you like to broaden your search?"
        elif len(results) >= 5:
            formatted += "\n\n💡 I found many results. Would you like me to focus on a specific aspect?"
    
    return formatted


class SearchDemoAgent(AgentBase):
    def __init__(self):
        super().__init__()
        
        # Add information about formatters to prompt
        self.prompt_add_section(
            title="Search Result Formatting",
            body="Search results are enhanced with visual formatting and contextual information.",
            bullets=[
                "Pay attention to quality indicators (✅ excellent, 👍 good, 🔎 partial)",
                "Note the sections covered in results",
                "Use the suggestions provided for better searches",
                "The formatting helps identify the most relevant information quickly"
            ]
        )
        
        # Example 1: Basic formatter
        self.add_skill("native_vector_search", {
            "tool_name": "search_basic",
            "description": "Search with basic visual formatting",
            "index_file": "docs.swsearch",
            "response_format_callback": basic_formatter
        })
        
        # Example 2: Advanced formatter with analysis
        self.add_skill("native_vector_search", {
            "tool_name": "search_advanced", 
            "description": "Search with advanced result analysis",
            "index_file": "docs.swsearch",
            "response_format_callback": advanced_formatter
        })
        
        # Example 3: Context-aware formatter
        self.add_skill("native_vector_search", {
            "tool_name": "search_contextual",
            "description": "Search with conversation context tracking",
            "index_file": "docs.swsearch",
            "response_format_callback": context_aware_formatter
        })


def create_custom_formatter(emoji_style=True, include_stats=True, max_preview_length=200):
    """Factory function to create customized formatters"""
    def formatter(response, query, results, **kwargs):
        parts = []
        
        if emoji_style:
            parts.append(f"🔍 Results for '{query}'")
        else:
            parts.append(f"Results for '{query}'")
        
        if include_stats and results:
            total_docs = len(set(r['metadata'].get('filename', '') for r in results))
            parts.append(f"Found in {total_docs} document(s)")
        
        # Truncate long results
        for i, result in enumerate(results):
            if len(result['content']) > max_preview_length:
                # Truncate and add to response
                truncated = result['content'][:max_preview_length] + "..."
                response = response.replace(result['content'], truncated)
        
        parts.append(response)
        return "\n\n".join(parts)
    
    return formatter


if __name__ == "__main__":
    agent = SearchDemoAgent()
    agent.serve()