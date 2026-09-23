# MCP Integration

The SDK supports the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) in two ways:

1. **MCP Client**: connect to external MCP servers and use their tools in your agent
2. **MCP Server**: expose your agent's `@tool` functions as an MCP endpoint for other clients

These features are independent and can be used separately or together.

## Adding External MCP Servers

Use `add_mcp_server()` to connect your agent to remote MCP servers. Tools are discovered at call start via the MCP protocol and added to the AI's tool list alongside your `@tool` functions.

```python
from signalwire import AgentBase

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent", route="/agent")

        self.add_mcp_server(
            "https://mcp.example.com/tools",
            headers={"Authorization": "Bearer sk-xxx"}
        )
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `url` | str | MCP server HTTP endpoint URL |
| `headers` | dict | Optional HTTP headers for authentication |
| `resources` | bool | Fetch resources into `global_data` (default: False) |
| `resource_vars` | dict | Variables for URI template substitution |

### With Resources

MCP servers can expose read-only data as resources. When enabled, resources are fetched at session start and merged into `global_data`:

```python
self.add_mcp_server(
    "https://mcp.example.com/crm",
    headers={"Authorization": "Bearer sk-xxx"},
    resources=True,
    resource_vars={"caller_id": "${caller_id_number}"}
)
```

Resource data is available in prompts via `${global_data.key}` and included in every webhook call.

### Multiple Servers

Add more than one server, and the agent merges their tools into one list:

```python
self.add_mcp_server("https://mcp-search.example.com/tools",
    headers={"Authorization": "Bearer search-key"})
self.add_mcp_server("https://mcp-crm.example.com/tools",
    headers={"Authorization": "Bearer crm-key"})
```

Tools from all servers are merged into one list. If an MCP tool has the same name as a `@tool` function, your local function's description is used but execution routes through MCP.

## Exposing Tools as MCP Server

Use `enable_mcp_server()` to add an MCP endpoint at `/mcp` on your agent's server. An MCP client that has the agent's basic auth credentials can connect and use your `@tool` functions.

```python
from signalwire import AgentBase
from signalwire.core.function_result import FunctionResult

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent", route="/agent")
        self.enable_mcp_server()

    @AgentBase.tool("get_weather", description="Get weather for a location")
    def get_weather(self, args, raw_data):
        location = args.get("location", "unknown")
        return FunctionResult(f"72F sunny in {location}")
```

The `/mcp` endpoint handles the full MCP protocol:
- `initialize`: protocol version and capability negotiation
- `notifications/initialized`: ready signal
- `tools/list`: returns the agent's tools in MCP format, except DataMap and external webhook tools, which don't run in the agent
- `tools/call`: invokes the handler and returns the result
- `ping`: keepalive

### Connecting a Client

The endpoint uses the agent's basic auth credentials, like the agent's other endpoints, and answers 401 without them. Give your MCP client the endpoint's URL and an `Authorization: Basic` header built from those credentials. For example, this command adds the agent to Claude Code:

```bash
claude mcp add --transport http my-agent https://your-server.com/agent/mcp \
  --header "Authorization: Basic $(printf '%s' 'user:password' | base64)"
```

Your `@tool` functions are then available to the client.

## Using Both Together

The two features are independent:

```python
class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent", route="/agent")

        # Expose my tools as MCP (for Claude Desktop, other agents)
        self.enable_mcp_server()

        # Pull in tools from external MCP servers (for voice calls)
        self.add_mcp_server("https://mcp.example.com/crm",
            headers={"Authorization": "Bearer sk-xxx"},
            resources=True)

    @AgentBase.tool("transfer_call", description="Transfer the caller")
    def transfer_call(self, args, raw_data):
        # This tool is available both as MCP AND as SWAIG webhook
        return FunctionResult("Transferring now.")
```

In this setup:
- Voice calls use `transfer_call` via SWAIG webhook + CRM tools via MCP
- Claude Desktop uses `transfer_call` via MCP endpoint
- The same tool code serves both protocols

### Self-Referencing

If you want your agent's voice calls to also discover tools via MCP instead of webhooks:

```python
self.enable_mcp_server()
self.add_mcp_server("https://your-server.com/agent/mcp")
```

This is optional. By default, `enable_mcp_server()` only adds the endpoint, and doesn't affect the agent's own SWML output.

## MCP vs SWAIG Webhooks

| | SWAIG Webhooks | MCP Tools |
|---|---|---|
| Response format | JSON with `response`, `action`, `SWML` | Text content only |
| Call control | Can trigger hold, transfer, SWML | Response only |
| Discovery | Defined in SWML config | Auto-discovered via protocol |
| Auth | `web_hook_auth_user/password` | `headers` dict |

MCP tools are best for data retrieval. Use `@tool` functions with SWAIG webhooks when you need call control actions.
