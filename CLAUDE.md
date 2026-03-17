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
```

## Commands

### Tests

```bash
# Run all tests (enforces 95% coverage minimum)
pytest

# Run by marker
pytest -m unit
pytest -m integration
pytest -m skills

# Run single file or test
pytest tests/unit/core/test_agent_base.py
pytest tests/unit/core/test_agent_base.py::TestClassName::test_method

# Parallel execution
pytest -n auto

# Skip coverage enforcement (useful during development)
pytest --no-cov
```

pytest.ini enables `--cov-fail-under=95` by default. Test timeout is 300s. Async mode is `auto` (pytest-asyncio).

### CLI Tools

```bash
swaig-test           # Test agents locally without a server
sw-search            # Build/manage vector search indexes
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
4. `SwaigFunctionResult` is the return type for all tool functions
5. `SWMLHandler` processes incoming AI verb callbacks

### Contexts & Steps

`ContextBuilder` creates multi-step agent workflows. Each `Context` contains `Step` objects with prompts, tools, and gather questions. Agents switch contexts at runtime.

### Data Maps

`DataMap` defines server-side API tools that execute REST calls without agent webhooks. Supports expression evaluation for conditional logic.

### Skills System

Skills are pluggable capabilities loaded via `SkillManager` and discovered through `registry.py`. Each skill is a directory under `skills/` with a `__init__.py` exporting a `SkillBase` subclass.

## Version Management

Version is tracked in three places (keep in sync): `pyproject.toml`, `signalwire_agents/__init__.py`, and `signalwire_agents/agent_server.py`. Use `version_bump.py` for bumping.

## Environment Variables

Key variables for local development:
- `SIGNALWIRE_PROJECT_ID`, `SIGNALWIRE_API_TOKEN`, `SIGNALWIRE_SPACE` — auth for RELAY/REST clients
- `SWML_BASIC_AUTH_USER`, `SWML_BASIC_AUTH_PASSWORD` — agent server auth (auto-generated if unset)
- `SWML_PROXY_URL_BASE` — external URL when behind a reverse proxy
- `SWML_SSL_ENABLED`, `SWML_SSL_CERT_PATH`, `SWML_SSL_KEY_PATH` — HTTPS config
