# Lesson 2: Adding Intelligence with Knowledge Bases

This lesson adds a searchable knowledge base to Morgan, the sales agent from Lesson 1. It uses SignalWire's vector search, so Morgan can look up product details instead of relying only on the prompt.

## Table of Contents

1. [Understanding Vector Search](#understanding-vector-search)
2. [Installing Search Dependencies](#installing-search-dependencies)
3. [Creating Knowledge Bases](#creating-knowledge-bases)
4. [Building Search Indexes](#building-search-indexes)
5. [Adding Search to Your Agent](#adding-search-to-your-agent)
6. [Testing Knowledge Queries](#testing-knowledge-queries)
7. [Best Practices](#best-practices)
8. [Summary](#summary)

---

## Understanding Vector Search

Vector search allows your agent to find relevant information from large document collections using semantic similarity rather than exact keyword matching.

**Key Benefits:**

- **Semantic Understanding**: Finds related content even with different wording
- **Scalability**: Efficiently searches through thousands of documents
- **Context Awareness**: Returns the most relevant passages for the query
- **Real-time Updates**: Knowledge bases can be updated without changing code

**How It Works:**

1. Documents are converted into numerical vectors (embeddings)
2. User queries are converted to vectors using the same method
3. The system finds documents with similar vectors
4. Most relevant passages are returned to the agent

---

## Installing Search Dependencies

The search functionality requires additional packages for document processing and vector operations.

### Option 1: Basic Search (Recommended)

Install the SDK with the `search` extra for embeddings and basic document processing:

```bash
# Install with basic search support (~500MB)
pip install -e .[search]
```

This includes:
- Sentence transformers for embeddings
- Basic document processing
- SQLite for index storage

### Option 2: Full Document Processing

Install the `search-full` extra to index PDF and Office documents, not only Markdown and text:

```bash
# Install with full document support (~600MB)
pip install -e .[search-full]
```

Additional features:
- PDF processing
- Word/Excel document support
- Advanced text extraction

### Option 3: Query-Only (Production)

Install the `search-queryonly` extra where the agent only queries indexes built elsewhere:

```bash
# Minimal installation for querying existing indexes (~400MB)
pip install -e .[search-queryonly]
```

Use this when:
- You only need to query pre-built indexes
- Minimizing deployment size is important
- Index building happens elsewhere

### Dealing with PyTorch Compatibility

If building an index crashes with an "illegal instruction" error, the installed PyTorch build doesn't match your CPU. Reinstall it as the CPU build:

```bash
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

---

## Creating Knowledge Bases

Knowledge bases are markdown files containing information your agent can search.

### sales_knowledge.md Structure

The existing sales knowledge base follows a consistent heading structure:

```markdown
# PC Builder Pro Sales Knowledge Base

## Gaming PC Builds

### Budget Gaming Build ($800-$1000)
- **CPU**: AMD Ryzen 5 5600X or Intel Core i5-12400F
- **GPU**: NVIDIA RTX 4060 or AMD RX 7600
- **RAM**: 16GB DDR4 3200MHz (2x8GB)
- **Storage**: 500GB NVMe SSD
...

### Mid-Range Gaming Build ($1500-$2000)
- **CPU**: AMD Ryzen 7 7700X or Intel Core i5-13600K
- **GPU**: NVIDIA RTX 4070 or AMD RX 7800 XT
...
```

**Best Practices for Knowledge Documents:**

1. **Use Clear Headings**: Organize with markdown headers
2. **Be Specific**: Include model numbers, prices, specifications
3. **Structure Consistently**: Similar sections should follow similar patterns
4. **Update Regularly**: Keep information current

---

## Building Search Indexes

The `sw-search` CLI tool converts markdown documents into searchable indexes.

### Basic Usage

Point `sw-search` at a directory to build an index from every matching file in it:

```bash
# Build a search index from markdown files
sw-search ./tutorial --output sales_knowledge.swsearch

# Specify file types to include
sw-search ./tutorial --file-types md --output sales_knowledge.swsearch
```

### Advanced Options

Combine sources, chunk size, and tags to control how an index is built:

```bash
# Include multiple directories
sw-search ./docs ./examples ./tutorial --output combined.swsearch

# Specify chunk size for splitting documents
sw-search ./tutorial --chunk-size 512 --output sales_knowledge.swsearch

# Add metadata tags
sw-search ./tutorial --tags "product,sales" --output sales_knowledge.swsearch
```

### Validating Indexes

Check that an index file is well formed, or search it directly from the command line:

```bash
# Validate an existing index
sw-search validate ./sales_knowledge.swsearch

# Search within an index from command line
sw-search search ./sales_knowledge.swsearch "gaming PC under $1000"
```

### Building the Tutorial Indexes

The knowledge base files for this tutorial are already indexed. Here's how those indexes were built:

```bash
# The indexes are already built, but here's how they were created:
sw-search tutorial/multi_agents/sales_knowledge.md \
  --output tutorial/multi_agents/sales_knowledge.swsearch

sw-search tutorial/multi_agents/support_knowledge.md \
  --output tutorial/multi_agents/support_knowledge.swsearch
```

---

## Adding Search to Your Agent

This section gives Morgan the ability to search the knowledge base.

### Step 1: Add the Search Skill

Add the `native_vector_search` skill after the language configuration:

```python
# In the __init__ method, after language configuration:
self.add_skill("native_vector_search", {
    "tool_name": "search_sales_knowledge",
    "description": "Search sales and product information",
    "index_file": "tutorial/multi_agents/sales_knowledge.swsearch",
    "count": 3  # Return top 3 results
})
```

### Step 2: Update the Workflow

Add instructions for using the search tool:

```python
self.prompt_add_section(
    "Your Tasks",
    body="Complete sales process workflow with passion and expertise:",
    bullets=[
        "Greet customers warmly and introduce yourself",
        "Understand their specific PC building requirements",
        "Ask about budget, intended use, and preferences",
        "Use search_sales_knowledge to find relevant product information",
        "Provide knowledgeable recommendations based on search results",
        "Share your enthusiasm for PC building",
        "Offer to explain technical details when helpful"
    ]
)
```

### Step 3: Add Tool Usage Section

Add a section that tells Morgan when to use the new tool:

```python
self.prompt_add_section(
    "Tools Available",
    body="Use these tools to assist customers:",
    bullets=[
        "search_sales_knowledge: Find current product information and build recommendations",
        "Search when customers ask about specific budgets or use cases",
        "Use search results to provide accurate, up-to-date information"
    ]
)
```

### Complete Enhanced Agent

Here's the complete `sales_agent_with_search.py`:

<!-- snippet: no-run starts a blocking server/client (covered by SNIPPET-COMPILE + EXAMPLES-RUN) -->
```python
#!/usr/bin/env python3
"""
Sales Agent with Knowledge Base - Morgan
A PC building sales specialist with access to product knowledge
"""

from signalwire import AgentBase

class SalesAgentWithSearch(AgentBase):
    def __init__(self):
        super().__init__(
            name="PC Builder Sales Agent - Morgan (Enhanced)",
            route="/",
            host="0.0.0.0",
            port=3000
        )
        
        # Configure the agent's personality and role
        self.prompt_add_section(
            "AI Role",
            body=(
                "You are Morgan, a passionate PC building expert and sales specialist "
                "at PC Builder Pro. You're known for your deep knowledge of components "
                "and your ability to match customers with their perfect build. You get "
                "excited about the latest hardware and love sharing that enthusiasm. "
                "Always introduce yourself by name."
            )
        )
        
        # Add expertise section
        self.prompt_add_section(
            "Your Expertise",
            body="Areas of specialization:",
            bullets=[
                "Custom PC builds for all budgets",
                "Component compatibility and optimization",
                "Performance recommendations",
                "Price/performance analysis",
                "Current market trends"
            ]
        )
        
        # Define the sales workflow with search integration
        self.prompt_add_section(
            "Your Tasks",
            body="Complete sales process workflow with passion and expertise:",
            bullets=[
                "Greet customers warmly and introduce yourself",
                "Understand their specific PC building requirements",
                "Ask about budget, intended use, and preferences",
                "Use search_sales_knowledge to find relevant product information",
                "Provide knowledgeable recommendations based on search results",
                "Share your enthusiasm for PC building",
                "Offer to explain technical details when helpful"
            ]
        )
        
        # Voice and tone instructions
        self.prompt_add_section(
            "Voice Instructions",
            body=(
                "Share your passion for PC building and get excited about "
                "helping customers create their perfect system. Your enthusiasm "
                "should be genuine and infectious."
            )
        )
        
        # Tool usage instructions
        self.prompt_add_section(
            "Tools Available",
            body="Use these tools to assist customers:",
            bullets=[
                "search_sales_knowledge: Find current product information and build recommendations",
                "Search when customers ask about specific budgets or use cases",
                "Use search results to provide accurate, up-to-date information"
            ]
        )
        
        # Important guidelines
        self.prompt_add_section(
            "Important",
            body="Key guidelines for using knowledge search:",
            bullets=[
                "Always search when customers mention specific budgets",
                "Search for compatibility information when needed",
                "Use search results to support your recommendations",
                "Acknowledge when searching: 'Let me find the perfect options for you'"
            ]
        )
        
        # Configure language and voice
        self.add_language(
            name="English",
            code="en-US",
            voice="rime.marsh"
        )
        
        # Add search capability
        self.add_skill("native_vector_search", {
            "tool_name": "search_sales_knowledge",
            "description": "Search sales and product information",
            "index_file": "tutorial/multi_agents/sales_knowledge.swsearch",
            "count": 3
        })

def main():
    """Main function to run the enhanced agent"""
    agent = SalesAgentWithSearch()
    
    print("Starting PC Builder Sales Agent - Morgan (Enhanced)")
    print("=" * 60)
    print("Agent running at: http://localhost:3000/")
    print("Knowledge base: sales_knowledge.swsearch")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nShutting down agent...")

if __name__ == "__main__":
    main()
```

---

## Testing Knowledge Queries

### Method 1: Using swaig-test

List the agent's tools, then call the search tool directly with a query:

```bash
# List available tools
swaig-test tutorial/multi_agents/sales_agent_with_search.py --list-tools

# Test the search function
swaig-test tutorial/multi_agents/sales_agent_with_search.py \
  --exec search_sales_knowledge \
  --query "gaming PC under \$1500"
```

### Method 2: Interactive Testing

When you call the agent, try these prompts:
- "I need a gaming PC for around $1000"
- "What's the best build for video editing?"
- "Can you recommend components for a high-end gaming system?"

### Method 3: Direct Search Testing

Query the `.swsearch` index directly, without going through the agent:

```bash
# Test the search index directly
sw-search search tutorial/multi_agents/sales_knowledge.swsearch "RTX 4070"
```

### Understanding Search Results

`sw-search search --json` shows the structure behind both the CLI output and the `search_sales_knowledge` tool's results:

```json
{
  "query": "gaming PC under $1500",
  "count": 1,
  "results": [
    {
      "rank": 1,
      "score": 0.71,
      "metadata": {
        "filename": "sales_knowledge.md",
        "section": "Section 1",
        "metadata": {
          "chunk_index": 3
        }
      },
      "content": "### Mid-Range Gaming Build ($1500-$2000)\n- **CPU**: AMD Ryzen 7 7700X..."
    }
  ]
}
```

**Fields:**
- `content`: the matching text passage
- `score`: the relevance score, higher is better. There's no fixed upper bound, so scores above 1 are normal.
- `metadata.filename` and `metadata.section`: where the passage came from

---

## Best Practices

### Knowledge Base Design

**DO:**
- Keep information current and accurate
- Use consistent formatting
- Include specific model numbers and prices
- Organize with clear hierarchies
- Update regularly as products change

**DON'T:**
- Include outdated information
- Use inconsistent terminology
- Create overly long sections
- Mix different types of information

### Search Integration

**Effective Patterns:**

1. **Acknowledge Searching**:
   ```
   "Let me search for the best options in your budget..."
   "I'll find the latest recommendations for gaming builds..."
   ```

2. **Handle No Results**:
   ```
   "I don't have specific information about that, but based on similar builds..."
   ```

3. **Combine Results**:
   ```
   "Based on our current recommendations, I found three great options..."
   ```

### Performance Tips

Four habits keep a knowledge base fast to search and cheap to serve:

1. **Index Size**: Keep indexes focused on specific domains
2. **Result Count**: 3-5 results is usually optimal
3. **Caching**: Indexes are loaded once and cached in memory
4. **Updates**: Rebuild indexes when knowledge changes significantly

---

## Summary

This lesson gave Morgan a searchable product knowledge base. It covered:

**Key Skills:**
- Installing search dependencies with different feature sets
- Understanding vector search and embeddings
- Building search indexes with sw-search
- Integrating the native_vector_search skill
- Testing search functionality

**What's Next?**

In the next lesson, you'll learn how to build multi-agent systems where different specialists work together. You'll create a complete customer service system with triage, sales, and support agents.

### Practice Exercises

Before moving on, try these exercises:

1. **Create a Custom Knowledge Base**: Write a markdown file about PC accessories (monitors, keyboards, mice) and build an index
2. **Adjust Search Parameters**: Try different `count` values to see how it affects responses
3. **Add Search Refinement**: Update prompts to ask clarifying questions before searching
4. **Test Edge Cases**: See how the agent handles queries with no good matches

### Troubleshooting

**Common Issues:**

- **Module not found**: Ensure you installed with `pip install -e .[search]`
- **Index file not found**: Check the path is relative to where you run the agent
- **PyTorch "illegal instruction" errors**: Reinstall PyTorch as the CPU build, as described in [Dealing with PyTorch Compatibility](#dealing-with-pytorch-compatibility)
- **Empty results**: Verify the index was built from the correct files

---

[Previous: Lesson 1 - Creating Your First Agent](lesson1_first_agent.md) | [Tutorial Overview](README.md) | [Next: Lesson 3 - Building Multi-Agent Systems](lesson3_multi_agent_systems.md)
