# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SignalWire Agents SDK — a Python framework for building AI-powered telephone/messaging agents on SignalWire's platform. Provides SWML (SignalWire Markup Language) document generation, SWAIG (SignalWire AI Gateway) tool calling, real-time call control (RELAY), REST APIs, vector search, and LiveKit compatibility.

## Development Setup

**Python 3.10+ required.** Always activate the venv before running commands:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .

# Install with search functionality (various levels)
pip install -e .[search-queryonly] # Query existing .swsearch files only (~400MB)
pip install -e .[search]           # Basic search functionality (~500MB)
pip install -e .[search-full]      # Full document processing (~600MB)
pip install -e .[search-nlp]       # Advanced NLP features (~600MB)
pip install -e .[search-all]       # All search features (~700MB)
```

## Commands

### Tests

```bash
# Run all tests (enforces 95% coverage minimum)
pytest

# Run by marker
pytest -m unit
pytest -m integration
pytest -m core
pytest -m skills
pytest -m cli

# Run tests in specific directories
pytest tests/unit/core/
pytest tests/unit/skills/

# Run single file or test
pytest tests/unit/core/test_agent_base.py
pytest tests/unit/core/test_agent_base.py::TestClassName::test_method

# Parallel execution
pytest -n auto

# Run with verbose output
pytest -v

# Skip coverage enforcement (useful during development)
pytest --no-cov

# Coverage reporting
pytest --cov=signalwire --cov-report=html
```

pytest.ini enables `--cov-fail-under=95` by default. Test timeout is 300s. Async mode is `auto` (pytest-asyncio).

### CLI Tools

```bash
# Test SWAIG functions locally
swaig-test examples/simple_agent.py --list-tools
swaig-test examples/simple_agent.py --exec tool_name --param value

# Multi-agent selection
swaig-test examples/multi_agent.py --route /agent-path --list-tools
swaig-test examples/multi_agent.py --agent-class AgentName --exec tool_name

# Control logging output
swaig-test examples/my_agent.py --exec tool_name  # Logs suppressed by default
swaig-test examples/my_agent.py --verbose --exec tool_name  # Show logs

# Simulate serverless environments
swaig-test examples/my_agent.py --simulate-serverless lambda --dump-swml

# Build search indexes
sw-search ./docs --output knowledge.swsearch
sw-search ./docs ./examples --file-types md,txt,py --output knowledge.swsearch

# Search operations
sw-search validate ./knowledge.swsearch
sw-search search ./knowledge.swsearch "query"
sw-search remote <endpoint> "query" --index-name <name>

# Other tools
sw-agent-init        # Scaffold new agent projects
sw-agent-dokku       # Dokku deployment helper
mcp-gateway          # MCP Gateway service
```

## Architecture

### Core Class Hierarchy

`AgentBase` is the central class. It extends `SWMLService` and composes features via mixins:

- `SWMLService` → base SWML document generation and FastAPI web service
- `PromptMixin` → Prompt Object Model (POM) structured prompt building
- `ToolMixin` → SWAIG function definition/execution (`@AgentBase.tool()` decorator)
- `SkillMixin` → skill loading/management
- `WebMixin` → static file serving, route management
- `AuthMixin` → basic auth, security headers
- `AIConfigMixin` → LLM parameter tuning (temperature, top_p, etc.)
- `ServerlessMixin` → cloud function environment detection
- `StateMixin` → per-session state management

### Agent Server

`AgentServer` hosts multiple agents on a single FastAPI process. Agents register at routes. Default port is 3000.

### Key Modules

| Module | Purpose |
|---|---|
| `core/` | AgentBase, SWML/SWAIG, contexts, data maps, mixins |
| `skills/` | 19 built-in skill plugins (weather, web_search, datetime, etc.) |
| `prefabs/` | Ready-made agent archetypes (InfoGatherer, Survey, FAQ, Receptionist, Concierge) |
| `relay/` | WebSocket RELAY client (Blade/JSON-RPC 2.0), async call control |
| `rest/` | Synchronous REST client, namespaced API (Fabric, Calling, Video, Datasphere) |
| `search/` | Vector search with sentence-transformers, multiple backends |
| `livewire/` | LiveKit-compatible API layer mapping to SignalWire |
| `mcp_gateway/` | Model Context Protocol bridge to SWAIG |
| `cli/` | CLI entry points (swaig-test, sw-search, sw-agent-init) |

### SWML/SWAIG Pipeline

1. `SWMLBuilder` constructs SWML JSON documents describing call flows
2. `SWMLService` serves these documents via FastAPI endpoints
3. `SwaigFunction` wraps Python functions as SWAIG tools (defined via `@AgentBase.tool()`)
4. `FunctionResult` is the return type for all tool functions
5. `SWMLHandler` processes incoming AI verb callbacks

### Contexts & Steps

`ContextBuilder` creates multi-step agent workflows. Each `Context` contains `Step` objects with prompts, tools, and gather questions. Agents switch contexts at runtime.
- Define contexts with `self.define_contexts()` in agent constructor
- Single context must be named "default"
- Use `set_valid_steps()` and `set_valid_contexts()` for navigation control
- Restrict functions per step with `set_functions(['function_name'])` or `set_functions("none")`
- Set completion criteria with `set_step_criteria("condition description")`

### Data Maps

`DataMap` defines server-side API tools that execute REST calls without agent webhooks. Supports expression evaluation for conditional logic.
- Created with fluent API: `DataMap('tool_name').description('...').webhook('GET', 'url').output(...)`
- Variable expansion: `${args.param}`, `${response.field}`, `${global_data.key}`
- Use DataMap for simple API integrations, webhooks for complex logic

### Skills System

Skills are pluggable capabilities loaded via `SkillManager` and discovered through `registry.py`. Each skill is a directory under `skills/` with a `__init__.py` exporting a `SkillBase` subclass.
- Skills are loaded on-demand to avoid startup overhead
- Use `agent.add_skill("skill_name", config_dict)` for configuration
- Skills automatically register with agent's SWAIG function registry
- Multiple instances of same skill supported with different `tool_name`

## Key Patterns

### Agent Creation
- Always inherit from `AgentBase` for standard agents
- Use `AgentServer` for multi-agent deployments
- Implement SWAIG functions with proper error handling
- State management is optional but recommended for complex workflows

### LLM Parameter Tuning
- Use `set_prompt_llm_params(**params)` to customize main prompt behavior
- Use `set_post_prompt_llm_params(**params)` for different post-prompt parameters
- Common parameters: temperature, top_p, barge_confidence, presence_penalty, frequency_penalty
- No defaults are sent unless explicitly set

### Security Considerations
- Basic auth credentials auto-generated unless environment variables set
- Session management via `SessionManager` for stateful interactions
- Function-specific security tokens supported
- SSL/HTTPS support with `SWML_SSL_ENABLED` environment variable

### Deployment Patterns
- **Local development**: Direct agent instantiation with `agent.serve()`
- **Multi-agent servers**: Use `AgentServer` class
- **Serverless**: Lambda, CGI, Cloud Functions, Azure Functions supported
- **Dynamic configuration**: Per-request agent customization for multi-tenancy

## Common Development Workflows

### Adding New Skills
1. Create directory in `signalwire/skills/skill_name/`
2. Implement skill class inheriting from `SkillBase` with required attributes:
   - `SKILL_NAME` (required)
   - `SKILL_DESCRIPTION` (required)
   - `SKILL_VERSION` (optional, defaults to "1.0.0")
   - `REQUIRED_PACKAGES` (list of required Python packages)
   - `REQUIRED_ENV_VARS` (list of required environment variables)
3. Implement required methods:
   - `setup()` method returning bool for success/failure
   - `register_tools()` method that calls `self.define_tool()`
4. Include README.md with usage documentation
5. Add unit tests in `tests/unit/skills/`

### Testing Agents
1. Use `swaig-test` for local function testing
2. Test SWML generation with `--dump-swml`
3. Simulate serverless environments with `--simulate-serverless`
4. Use pytest for comprehensive test coverage

### Building Search Indexes
1. Install search extras: `pip install -e .[search-full]`
2. Use `sw-search` CLI tool: `sw-search ./docs --output knowledge.swsearch`
3. Test with `SearchEngine` class or `sw-search search ./knowledge.swsearch "query"`
4. Deploy with `search-queryonly` for production efficiency

## Version Management

Version is tracked in three places (keep in sync): `pyproject.toml`, `signalwire/__init__.py`, and `signalwire/agent_server.py`. Use `version_bump.py` for bumping.

## Environment Variables

Key variables for local development:
- `SIGNALWIRE_PROJECT_ID`, `SIGNALWIRE_API_TOKEN`, `SIGNALWIRE_SPACE` — auth for RELAY/REST clients
- `SWML_BASIC_AUTH_USER`, `SWML_BASIC_AUTH_PASSWORD` — agent server auth (auto-generated if unset)
- `SWML_PROXY_URL_BASE` — external URL when behind a reverse proxy
- `SWML_SSL_ENABLED`, `SWML_SSL_CERT_PATH`, `SWML_SSL_KEY_PATH` — HTTPS config
