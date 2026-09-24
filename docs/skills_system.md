# SignalWire Agents Skills System

The examples on this page assume these imports:

<!-- snippet-setup: shared imports the examples on this page assume -->
```python
from signalwire import AgentBase, AgentServer, DataMap, FunctionResult, SwaigFunctionResult, SWMLService
from signalwire.core.skill_base import SkillBase
```


The SignalWire Agents SDK includes a modular skills system that lets you add capabilities to your agents with one-line calls and configurable parameters.

## Overview

Instead of manually implementing every agent capability, you can:

<!-- snippet: no-run skill setup needs an external backend/API key (e.g. web_search, mcp_gateway) -->
```python
from signalwire import AgentBase

# Create an agent
agent = AgentBase("My Assistant")

# Add skills with one-liners!
agent.add_skill("web_search")   # Web search capability with default settings
agent.add_skill("datetime")     # Current date/time info  
agent.add_skill("math")         # Mathematical calculations

# Add skills with custom parameters!
agent.add_skill("web_search", {
    "num_results": 3,  # Get 3 search results instead of default 1
    "delay": 0.5       # Add 0.5s delay between requests instead of default 0
})

# Your agent now has all these capabilities automatically
```

## Architecture

The skills system consists of:

### Core Infrastructure
- **`SkillBase`** - Abstract base class for all skills with parameter support
- **`SkillManager`** - Handles loading/unloading and lifecycle management with parameters
- **`AgentBase.add_skill()`** - Adds a skill to an agent, with optional parameters

### Discovery & Registry  
- **`SkillRegistry`** - Finds skills in the `skills/` directory
- **On-demand discovery** - Skills load the first time you request them by name, not at import time
- **Validation** - Checks dependencies and environment variables

### Built-in Skills

A few examples, out of everything under `signalwire/signalwire/skills/`:
- **`web_search`** - Google Custom Search API integration with web scraping
- **`datetime`** - Current date/time information with timezone support
- **`math`** - Basic mathematical calculations

## Available Skills

This section covers five skills in detail. For the full, current list and each skill's parameters, see the README in its directory under `signalwire/signalwire/skills/`.

### Web Search (`web_search`)
Search the internet and extract content from web pages.

**Requirements:**
- `api_key` and `search_engine_id` are required parameters. The schema suggests sourcing them from `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_ENGINE_ID`. You read those and pass the values to `add_skill()` yourself; the skill doesn't read the environment directly.
- Packages: `beautifulsoup4`, `requests`

**Parameters:**
- `num_results` (default: 3) - Number of search results to retrieve (1-10)
- `delay` (default: 0.5) - Delay in seconds between web requests

**Tools provided:**
- `web_search(query)` - Search and scrape web content; `num_results` and `delay` come from the skill's configuration, not from the call

**Usage examples:**

These three configurations trade result count against speed:

```python
# Default: 3 results, 0.5s delay
agent.add_skill("web_search")

# Custom: multiple results with delay
agent.add_skill("web_search", {
    "num_results": 3,
    "delay": 0.5
})

# Speed optimized: single result, no delay
agent.add_skill("web_search", {
    "num_results": 1,
    "delay": 0
})
```

### Date/Time (`datetime`)  
Get current date and time information.

**Requirements:**
- Packages: `pytz`

**Parameters:** None (no configurable parameters)

**Tools provided:**
- `get_current_time(timezone)` - Current time in any timezone
- `get_current_date(timezone)` - Current date in any timezone

### Math (`math`)
Perform mathematical calculations.

**Requirements:** None

**Parameters:** None (no configurable parameters)

**Tools provided:**
- `calculate(expression)` - Evaluate mathematical expressions safely

### Native Vector Search (`native_vector_search`)
Search local document collections using vector similarity and keyword search.

**Requirements:**
- Packages: `sentence-transformers`, `scikit-learn`, `numpy`
- Install with: `pip install signalwire-sdk[search]`

**Parameters:**
- `tool_name` (default: "search_knowledge") - Custom name for the search tool
- `index_file` (optional) - Path to local `.swsearch` index file
- `remote_url` (optional) - URL of remote search server
- `index_name` (default: "default") - Index name on remote server
- `build_index` (default: False) - Auto-build index if missing
- `source_dir` (optional) - Source directory for auto-building
- `count` (default: 3) - Number of search results to return
- `similarity_threshold` (default: 0.0) - Minimum similarity score
- `response_prefix` (optional) - Text to prepend to responses
- `response_postfix` (optional) - Text to append to responses

**Tools provided:**
- `search_knowledge(query, count)` - Search documents with hybrid vector/keyword search

**Usage examples:**

These four configurations cover local, remote, and multi-instance search:

```python
# Local mode with auto-build from concepts guide
agent.add_skill("native_vector_search", {
    "tool_name": "search_docs",
    "build_index": True,
    "source_dir": "./docs",  # Will build from directory
    "index_file": "concepts.swsearch"
})

# Or build from specific concepts guide file
agent.add_skill("native_vector_search", {
    "tool_name": "search_concepts",
    "index_file": "concepts.swsearch"  # Pre-built from concepts guide
})

# Remote mode
agent.add_skill("native_vector_search", {
    "remote_url": "http://localhost:8001",
    "index_name": "knowledge"
})

# Multiple instances for different document collections
agent.add_skill("native_vector_search", {
    "tool_name": "search_examples",
    "index_file": "examples.swsearch"
})
```

For complete documentation, see [Search Overview](search_overview.md).

### SWML Transfer (`swml_transfer`)
Transfer calls between agents using pattern matching.

**Requirements:** None (no additional packages or environment variables required)

**Parameters:**
- `tool_name` (default: "transfer_call") - Custom name for the transfer function
- `description` (default: "Transfer call based on pattern matching") - Tool description
- `parameter_name` (default: "transfer_type") - Name of the parameter for the transfer function
- `parameter_description` (default: "The type of transfer to perform") - Parameter description
- `transfers` (required) - Dictionary mapping regex patterns to transfer configurations:
  - Pattern (key): Regex pattern to match (e.g., "/sales/i")
  - Configuration (value): Dictionary with:
    - `url` (required): Transfer destination URL
    - `message` (optional): Pre-transfer message
    - `return_message` (optional): Post-transfer message
    - `post_process` (optional, default: True): Enable post-processing
- `default_message` (default: "Please specify a valid transfer type.") - Message when no pattern matches
- `default_post_process` (default: False) - Post-processing flag for default case
- `required_fields` (default: {}) - Object mapping field names to descriptions for data collection before transfer

**Tools provided:**
- `transfer_call(transfer_type, ...required_fields)` (or custom tool_name) - Transfer based on pattern matching with optional required fields

**Usage examples:**

These two configurations show a basic transfer and a custom parameter name:

```python
# Simple transfer between departments
agent.add_skill("swml_transfer", {
    "tool_name": "transfer_to_department",
    "transfers": {
        "/sales/i": {
            "url": "https://example.com/sales",
            "message": "Transferring to sales...",
            "return_message": "Sales transfer complete."
        },
        "/support/i": {
            "url": "https://example.com/support",
            "message": "Transferring to support...",
            "return_message": "Support transfer complete."
        }
    }
})

# Multiple instances for different transfer types
agent.add_skill("swml_transfer", {
    "tool_name": "route_call",
    "parameter_name": "department",
    "transfers": {
        "/sales|billing/i": {
            "url": "https://api.company.com/sales",
            "message": "Connecting to sales team...",
            "post_process": True
        },
        "/technical|support/i": {
            "url": "https://api.company.com/support",
            "message": "Connecting to support team...",
            "post_process": True
        }
    },
    "default_message": "Would you like sales or support?"
})
```

## Usage Examples

### Basic Usage

Add three skills with no parameters, then start the agent:

<!-- snippet: no-run starts a blocking server/client (covered by SNIPPET-COMPILE + EXAMPLES-RUN) -->
```python
from signalwire import AgentBase

# Create agent and add skills
agent = AgentBase("Assistant", route="/assistant")
agent.add_skill("datetime")
agent.add_skill("math") 
agent.add_skill("web_search")  # Uses defaults: 3 results, 0.5s delay

# Start the agent
agent.run()
```

### Skills with Custom Parameters

Pass a parameters dictionary to override a skill's defaults:

<!-- snippet: no-run starts a blocking server/client (covered by SNIPPET-COMPILE + EXAMPLES-RUN) -->
```python
from signalwire import AgentBase

# Create agent
agent = AgentBase("Research Assistant", route="/research")

# Add web search optimized for research (more results)
agent.add_skill("web_search", {
    "num_results": 5,   # Get more comprehensive results
    "delay": 1.0        # Be respectful to websites
})

# Add other skills without parameters
agent.add_skill("datetime")
agent.add_skill("math")

# Start the agent
agent.run()
```

### Different Parameter Configurations

These three configurations trade result count against response speed:

```python
# Speed-optimized for quick responses
agent.add_skill("web_search", {
    "num_results": 1,
    "delay": 0
})

# Comprehensive research mode
agent.add_skill("web_search", {
    "num_results": 5,
    "delay": 1.0
})

# Balanced approach
agent.add_skill("web_search", {
    "num_results": 3,
    "delay": 0.5
})
```

### Check Available Skills

List every skill the registry can find, whether or not it's loaded on an agent:

```python
from signalwire.skills.registry import skill_registry

# List all discovered skills
for skill in skill_registry.list_skills():
    print(f"- {skill['name']}: {skill['description']}")
    if skill['required_env_vars']:
        print(f"  Requires: {', '.join(skill['required_env_vars'])}")
```

### Runtime Skill Management

`list_skills()`, `remove_skill()`, and `has_skill()` manage skills after the agent is created:

<!-- snippet: no-run skill setup needs an external backend/API key (e.g. web_search, mcp_gateway) -->
```python
agent = AgentBase("Dynamic Agent")

# Add skills with different configurations
agent.add_skill("math")
agent.add_skill("datetime")
agent.add_skill("web_search", {"num_results": 2, "delay": 0.3})

# Check what's loaded
print("Loaded skills:", agent.list_skills())

# Remove a skill
agent.remove_skill("math")

# Check if specific skill is loaded
if agent.has_skill("datetime"):
    print("Date/time capabilities available")
```

## Creating Custom Skills

Create a new skill by extending `SkillBase` with parameter support:

```python
# signalwire/signalwire/skills/my_skill/skill.py
from typing import Any, Dict
from signalwire.core.skill_base import SkillBase
from signalwire.core.function_result import FunctionResult

class MyCustomSkill(SkillBase):
    SKILL_NAME = "my_skill"
    SKILL_DESCRIPTION = "Does something awesome with configurable parameters"
    SKILL_VERSION = "1.0.0"
    REQUIRED_PACKAGES = ["requests"]  # Optional
    REQUIRED_ENV_VARS = ["API_KEY"]   # Optional
    
    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Dict[str, Any]]:
        """Declare configurable parameters; required so the registry accepts the skill"""
        schema = super().get_parameter_schema()
        schema.update({
            "max_items": {"type": "integer", "description": "Maximum items to process", "default": 10, "required": False},
            "timeout": {"type": "integer", "description": "Request timeout in seconds", "default": 30, "required": False},
            "retry_count": {"type": "integer", "description": "Number of retries on failure", "default": 3, "required": False},
        })
        return schema
    
    def setup(self) -> bool:
        """Initialize the skill with parameters"""
        if not self.validate_env_vars() or not self.validate_packages():
            return False
            
        # Use parameters with defaults
        self.max_items = self.params.get('max_items', 10)
        self.timeout = self.params.get('timeout', 30)
        self.retry_count = self.params.get('retry_count', 3)
        
        return True
        
    def register_tools(self) -> None:
        """Register SWAIG tools with the agent"""
        self.define_tool(
            name="my_function",
            description=f"Does something cool (max {self.max_items} items)",
            parameters={
                "input": {
                    "type": "string",
                    "description": "Input parameter"
                }
            },
            handler=self._my_handler
        )
    
    def _my_handler(self, args, raw_data):
        """Handle the tool call using configured parameters"""
        # Use self.max_items, self.timeout, self.retry_count in your logic
        return FunctionResult(f"Processed with max_items={self.max_items}")
        
    def get_hints(self):
        """Speech recognition hints"""
        return ["custom", "skill", "awesome"]
        
    def get_prompt_sections(self):
        """Prompt sections to add to agent"""
        return [{
            "title": "Custom Capability",
            "body": f"You can do custom things with my_skill (configured for {self.max_items} items)."
        }]
```

The skill will be automatically discovered and available as:
```python
# Use defaults
agent.add_skill("my_skill")

# Use custom parameters
agent.add_skill("my_skill", {
    "max_items": 20,
    "timeout": 60,
    "retry_count": 5
})
```

## Quick Start

Follow these three steps to run the demo agent:

1. **Install dependencies.** These packages ship with the SDK, so this step confirms they're present:
   ```bash
   pip install pytz beautifulsoup4 requests
   ```

2. **Run the demo.** It loads `datetime`, `math`, and (if configured) `web_search`:
   ```bash
   python examples/skills_demo.py
   ```

3. **For web search, set environment variables, then read and pass them explicitly.** First, set the values:
   ```bash
   export GOOGLE_SEARCH_API_KEY="your_api_key"
   export GOOGLE_SEARCH_ENGINE_ID="your_engine_id"
   ```
   The skill doesn't read the environment itself; your code does:
   <!-- snippet: no-compile fragment continues the `agent` from the earlier step, not a standalone module -->
   ```python
   import os
   agent.add_skill("web_search", {
       "api_key": os.environ["GOOGLE_SEARCH_API_KEY"],
       "search_engine_id": os.environ["GOOGLE_SEARCH_ENGINE_ID"],
   })
   ```

## Testing

Test the skills system with parameters:

```bash
python3 -c "
from signalwire import AgentBase
from signalwire.skills.registry import skill_registry

# Show discovered skills
print('Available skills:', [s['name'] for s in skill_registry.list_skills()])

# Create agent and load skills with parameters
agent = AgentBase('Test', route='/test')
agent.add_skill('datetime')
agent.add_skill('math')
agent.add_skill('web_search', {
    'api_key': 'your-google-api-key',
    'search_engine_id': 'your-search-engine-id',
    'num_results': 2,
    'delay': 0.5
})

print('Loaded skills:', agent.list_skills())
print('Skills system with parameters working')
"
```

## Benefits

The skills system gives you these properties:

- **One-liner integration** - `agent.add_skill("skill_name")`
- **Configurable parameters** - `agent.add_skill("skill_name", {"param": "value"})`
- **On-demand discovery** - Drop a skill in the directory, and it's available the first time you request it
- **Dependency validation** - Checks packages and environment variables
- **Modular architecture** - Skills are self-contained and reusable
- **Extensible** - You can create custom skills with parameters
- **Clean separation** - Skills don't interfere with each other
- **Performance tuning** - Configure skills for speed vs. comprehensiveness

## Migration Guide

**Before (manual implementation):** every capability needed its own setup code, repeated in each agent:

```python
# Had to manually implement every capability
class WebSearchAgent(AgentBase):
    def __init__(self):
        super().__init__("WebSearchAgent")
        self.setup_google_search()
        self.define_tool("web_search", ...)
        # Lots of manual code...
```

**After (skills system with parameters):**

The same capability now takes one call:

<!-- snippet: no-run skill setup needs an external backend/API key (e.g. web_search, mcp_gateway) -->
```python
# Simple one-liner with custom configuration
agent = AgentBase("WebSearchAgent")
agent.add_skill("web_search", {
    "num_results": 3,  # Get more results
    "delay": 0.5       # Be respectful to servers
})
# Done! Full web search capability with custom settings.
```

The skills system makes SignalWire agents more modular, maintainable, and configurable. 
