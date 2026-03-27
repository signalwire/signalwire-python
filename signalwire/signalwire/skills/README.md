# SignalWire Agents Skills System

This directory contains the modular skills system for SignalWire AI Agents. Skills provide reusable, configurable capabilities that can be easily added to any agent.

## Table of Contents

- [Overview](#overview)
- [Creating a New Skill](#creating-a-new-skill)
- [Skill Structure](#skill-structure)
- [Required Files](#required-files)
- [Skill Class Implementation](#skill-class-implementation)
- [DataMap Integration](#datamap-integration)
- [Package Configuration](#package-configuration)
- [Testing Your Skill](#testing-your-skill)
- [Documentation](#documentation)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Overview

The skills system provides:
- **Modular capabilities**: Reusable functionality across agents
- **Automatic discovery**: Skills are automatically found and registered
- **Configuration validation**: Parameter checking and error handling
- **DataMap integration**: Serverless API execution without custom webhooks
- **Documentation**: Built-in help and usage information

## Creating a New Skill

### Step 1: Create Skill Directory

Create a new directory under `signalwire_agents/skills/` with your skill name:

```bash
mkdir signalwire_agents/skills/your_skill_name
```

### Step 2: Required Files

Every skill needs these files:

```
signalwire_agents/skills/your_skill_name/
├── __init__.py          # Package initialization
├── skill.py            # Main skill implementation
└── README.md           # Skill documentation
```

### Step 3: Update Package Configuration

Add your skill to `pyproject.toml`:

```toml
[tool.setuptools]
packages = [
    # ... existing packages ...
    "signalwire_agents.skills.your_skill_name"
]
```

## Skill Structure

### `__init__.py`

Simple package initialization:

```python
"""Your Skill Name for SignalWire Agents"""
```

### `skill.py`

Main skill implementation inheriting from `SkillBase`:

```python
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from typing import List, Dict, Any

from signalwire_agents.core.skill_base import SkillBase
from signalwire_agents.core.data_map import DataMap
from signalwire_agents.core.function_result import SwaigFunctionResult


class YourSkillClass(SkillBase):
    """Your skill description"""
    
    SKILL_NAME = "your_skill_name"
    SKILL_DESCRIPTION = "Brief description of what your skill does"
    SKILL_VERSION = "1.0.0"
    REQUIRED_PACKAGES = []  # List of required Python packages
    REQUIRED_ENV_VARS = []  # List of required environment variables
    
    def setup(self) -> bool:
        """Setup and validate skill configuration"""
        # Validate required parameters
        required_params = ['param1', 'param2']
        missing_params = [param for param in required_params if not self.params.get(param)]
        if missing_params:
            self.logger.error(f"Missing required parameters: {missing_params}")
            return False
            
        # Store configuration
        self.param1 = self.params['param1']
        self.param2 = self.params.get('param2', 'default_value')
        
        return True
        
    def register_tools(self) -> None:
        """Register skill tools/functions"""
        # Implement your tool registration here
        pass
        
    def get_hints(self) -> List[str]:
        """Return speech recognition hints"""
        # Currently no hints provided, but you could add them like:
        # return ["hint1", "hint2", "phrase users might say"]
        return []
        
    def get_global_data(self) -> Dict[str, Any]:
        """Return global data for DataMap variables"""
        return {
            "skill_param": self.param1
        }
        
    def get_prompt_sections(self) -> List[Dict[str, Any]]:
        """Return prompt sections to add to agent"""
        return [
            {
                "title": "Your Skill Capability",
                "body": "Description of what the agent can do with this skill.",
                "bullets": [
                    "Specific capability 1",
                    "Specific capability 2"
                ]
            }
        ]
```

## Skill Class Implementation

### Required Class Attributes

- `SKILL_NAME`: Unique identifier for the skill
- `SKILL_DESCRIPTION`: Brief description shown in skill listings
- `SKILL_VERSION`: Version string for the skill
- `REQUIRED_PACKAGES`: List of Python packages needed
- `REQUIRED_ENV_VARS`: List of environment variables needed

### Required Methods

#### `setup(self) -> bool`
- Validate and store configuration parameters
- Return `True` if setup successful, `False` otherwise
- Access parameters via `self.params`

#### `register_tools(self) -> None`
- Register SWAIG functions/tools with the agent
- Use `self.agent.register_swaig_function()` for custom functions
- Use DataMap for external API integration

#### `get_hints(self) -> List[str]`
- Return phrases for speech recognition hints (optional)
- Help the ASR system recognize skill-related requests
- Can return empty list if no hints are needed

#### `get_global_data(self) -> Dict[str, Any]`
- Return data available to DataMap expressions
- Access via `${global.key}` in DataMap configurations

#### `get_prompt_sections(self) -> List[Dict[str, Any]]`
- Return prompt sections to add to the agent
- Structure: `{"title": str, "body": str, "bullets": List[str]}`

## DataMap Integration

For skills that need to call external APIs, use DataMap for serverless execution:

```python
def register_tools(self) -> None:
    """Register DataMap-based tool"""
    
    tool = (DataMap("tool_name")
        .description("What this tool does")
        .parameter("param1", "string", "Parameter description", required=True)
        .parameter("param2", "string", "Optional parameter", required=False)
        .webhook("GET", "https://api.example.com/endpoint/${args.param1}", 
                 headers={"Authorization": f"Bearer {self.api_key}"})
        .output(SwaigFunctionResult("Result: ${response.data}"))
        .error_keys(["error", "message"])
    )
    
    self.agent.register_swaig_function(tool.to_swaig_function())
```

### DataMap Features

- **Dynamic URLs**: Use `${args.param}` for user inputs
- **Headers**: Add authentication and other headers
- **Response Processing**: Extract data with `${response.field}`
- **Error Handling**: Specify error keys to watch for
- **Defaults**: Use `${args.param || "default"}` for fallbacks

## Package Configuration

After creating your skill, update `pyproject.toml` to include it in the package:

```toml
[tool.setuptools]
packages = [
    "signalwire_agents",
    "signalwire_agents.prefabs", 
    "signalwire_agents.utils",
    "signalwire_agents.core",
    "signalwire_agents.core.state",
    "signalwire_agents.core.security",
    "signalwire_agents.skills",
    "signalwire_agents.skills.web_search",
    "signalwire_agents.skills.datetime", 
    "signalwire_agents.skills.math",
    "signalwire_agents.skills.joke",
    "signalwire_agents.skills.datasphere",
    "signalwire_agents.skills.wikipedia_search",
    "signalwire_agents.skills.your_skill_name"  # Add your skill here
]
```

## Testing Your Skill

### 1. Install the Package

```bash
pip install . --force-reinstall
```

### 2. Test Skill Discovery

```python
from signalwire_agents.skills.registry import skill_registry

skill_registry.discover_skills()
skills = skill_registry.list_skills()
print(f"Found {len(skills)} skills:")
for skill in skills:
    print(f"  • {skill['name']}: {skill['description']}")
```

### 3. Test Skill Usage

```python
from signalwire_agents import AgentBase

class TestAgent(AgentBase):
    def __init__(self):
        super().__init__(name="Test Agent", route="/test")
        
        # Add your skill
        self.add_skill("your_skill_name", {
            "param1": "value1",
            "param2": "value2"
        })

agent = TestAgent()
# Test that skill loads without errors
```

## Documentation

### `README.md` Template

Create a comprehensive README for your skill:

```markdown
# Your Skill Name

Brief description of what the skill does.

## Description

Detailed explanation of the skill's purpose and capabilities.

## Features

- Feature 1
- Feature 2
- Feature 3

## Requirements

- Required service accounts or API keys
- Any external dependencies

## Configuration

### Required Parameters

- `param1`: Description of required parameter
- `param2`: Description of another required parameter

### Optional Parameters

- `optional_param`: Description with default value

## Usage

### Basic Usage

```python
from signalwire_agents import AgentBase

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="My Agent", route="/agent")
        
        self.add_skill("your_skill_name", {
            "param1": "value1",
            "param2": "value2"
        })

agent = MyAgent()
agent.serve()
```

### Advanced Configuration

Examples of advanced usage patterns.

## Generated Functions

List the SWAIG functions your skill creates and their parameters.

## Example Conversations

Show example interactions between users and agents using your skill.

## Troubleshooting

Common issues and solutions.
```

## Examples

Create example scripts in the `examples/` directory:

```python
#!/usr/bin/env python3
"""
Your Skill Demo - Description

This demo shows how to use your skill with the SignalWire Agents SDK.

Run with: python examples/your_skill_demo.py
"""

from signalwire_agents import AgentBase

class YourSkillAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="Your Skill Demo Agent",
            route="/your-skill-demo"
        )
        
        # Configure the agent
        self.prompt_add_section("Goal", body="What this demo agent does")
        
        # Add your skill
        self.add_skill("your_skill_name", {
            "param1": "demo-value"
        })

def main():
    print("=" * 60)
    print("YOUR SKILL DEMO")
    print("=" * 60)
    
    agent = YourSkillAgent()
    agent.serve(host="0.0.0.0", port=3000)

if __name__ == "__main__":
    main()
```

## Best Practices

### Configuration
- Always validate required parameters in `setup()`
- Provide sensible defaults for optional parameters
- Use descriptive parameter names
- Log errors clearly when configuration fails

### Error Handling
- Return `False` from `setup()` if configuration is invalid
- Handle API errors gracefully in DataMap configurations
- Use `self.logger` for consistent logging
- Provide helpful error messages

### Documentation
- Write clear, comprehensive README files
- Include working code examples
- Document all parameters and their purposes
- Show example conversations

### Security
- Never hard-code API keys or secrets
- Validate all user inputs
- Use HTTPS for all external API calls
- Be careful with user data in logs

### Performance
- Cache expensive operations when possible
- Use appropriate timeouts for external calls
- Consider rate limiting for API calls
- Keep skill setup fast

### Compatibility
- Avoid breaking changes in minor versions
- Test with different Python versions
- Document any external dependencies
- Use standard library when possible

## Troubleshooting

### Skill Not Found
- Check that the skill directory is in `signalwire_agents/skills/`
- Verify `pyproject.toml` includes your skill package
- Reinstall the package after changes: `pip install . --force-reinstall`

### Import Errors
- Ensure all required packages are installed
- Check import statements in your skill.py
- Verify Python path and virtual environment

### Configuration Errors
- Check parameter validation logic in `setup()`
- Ensure required parameters are being passed
- Look for typos in parameter names

### DataMap Issues
- Validate API endpoints and authentication
- Check response format matches your expectations
- Test API calls independently first
- Use `.error_keys()` to handle API errors

Remember to always test your skill thoroughly and provide clear documentation for other developers! 