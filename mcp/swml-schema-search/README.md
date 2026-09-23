# SWML Schema MCP Server

An MCP (Model Context Protocol) server that provides tools to query SWML schema definitions. This allows LLMs to efficiently look up SWML method specifications without loading the entire schema file into context.

## Features

The server provides:

- **List all SWML methods** with brief descriptions
- **Get detailed schema** for any specific method
- **Search methods** by keyword in name or description
- Efficient on-demand access to the 385KB+ schema file

## Tools Provided

| Tool | Description |
|------|-------------|
| `list_swml_methods` | List all available SWML methods with brief descriptions |
| `get_swml_method` | Get the full schema definition for a specific method (e.g., 'ai', 'connect', 'play') |
| `search_swml_methods` | Search SWML methods by keyword in name or description |

## Installation

No additional dependencies required beyond Python 3.7+. The server uses only standard library modules.

## Configuration

### Schema Path

By default, the server looks for the schema two directories up from its own
location, at `signalwire/schema.json`. That path is wrong: the schema ships at
`signalwire/signalwire/schema.json`, one level deeper, so the server exits
with an error unless you set `SWML_SCHEMA_PATH`:

```bash
export SWML_SCHEMA_PATH=/path/to/your/swml-schema.json

# From a checkout of this repository:
export SWML_SCHEMA_PATH=signalwire/signalwire/schema.json
```

### Debug Logging

Enable debug logging by setting:

```bash
export SWML_SCHEMA_MCP_DEBUG=1
```

## Usage with Claude Code

Add to your Claude Code MCP settings (`~/.claude/claude_desktop_config.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "swml-schema": {
      "command": "python3",
      "args": ["/path/to/signalwire-python/mcp/swml-schema-search/swml_schema_mcp.py"],
      "env": {
        "SWML_SCHEMA_PATH": "/path/to/signalwire-python/signalwire/signalwire/schema.json"
      }
    }
  }
}
```

Or with uv:

```json
{
  "mcpServers": {
    "swml-schema": {
      "command": "uv",
      "args": ["run", "python3", "/path/to/signalwire-python/mcp/swml-schema-search/swml_schema_mcp.py"],
      "env": {
        "SWML_SCHEMA_PATH": "/path/to/signalwire-python/signalwire/signalwire/schema.json"
      }
    }
  }
}
```

## Example Tool Usage

### List all methods

Calling the tool with no arguments returns every method:

```
Tool: list_swml_methods
Arguments: {}

Output:
Available SWML Methods (39 total):

  ai
    Creates an AI agent that conducts voice conversations using automatic speech recognition (ASR),

  connect
    Dial a SIP URI or phone number.

  play
    Play file(s), ringtones, speech or silence.
  ...
```

The `list_swml_methods` output cuts each description at the method's first line, which is why the `ai` entry ends mid-sentence.

### Get method details

Passing a method name returns its full schema:

```
Tool: get_swml_method
Arguments: {"method_name": "ai"}

Output:
SWML Method: ai
Description: Creates an AI agent that conducts voice conversations using automatic speech recognition (ASR),

Schema Definition:
{
  "type": "object",
  "properties": {
    "ai": {
      "description": "Creates an AI agent that conducts voice conversations using automatic speech recognition (ASR), large language models (LLMs), and text-to-speech (TTS) synthesis...",
      "_definedIn": "AIObject",
      "properties": {
        "hints": {
          "description": "Hints help the AI agent understand certain words or phrases better...",
          "type": "array"
        },
        "languages": {
          "description": "An array of JSON objects defining supported languages in the conversation.",
          "type": "array"
        },
        ...
      }
    }
  }
}
```

The `properties` object also lists `prompt`, `SWAIG`, `params`, `global_data`, `post_prompt`, and `post_prompt_url`, each with its own real description and type.

### Search methods

Searching by keyword matches both the method name and its description:

```
Tool: search_swml_methods
Arguments: {"keyword": "audio"}

Output:
Methods matching 'audio' (2 found):

  join_conference
    Join an ad-hoc audio conference started on either the SignalWire or Compatibility API.

  record
    Record the call audio in the foreground, pausing further SWML execution until recording ends.
```

## How It Works

1. **Startup**: Loads and indexes the SWML schema JSON file
2. **Indexing**: Extracts all method definitions from `$defs.SWMLMethod.anyOf`
3. **Protocol**: Communicates via JSON-RPC over stdin/stdout (MCP standard)
4. **Efficiency**: Returns method details with shallow reference resolution, showing `_type` hints instead of fully expanding nested definitions

## Development

Run the server directly for testing. Run it from the repository root, so this schema path resolves:

```bash
SWML_SCHEMA_PATH=signalwire/signalwire/schema.json python3 mcp/swml-schema-search/swml_schema_mcp.py
```

Then send JSON-RPC messages via stdin:

```json
{"jsonrpc": "2.0", "method": "initialize", "id": 1}
{"jsonrpc": "2.0", "method": "tools/list", "id": 2}
{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "list_swml_methods", "arguments": {}}, "id": 3}
```
