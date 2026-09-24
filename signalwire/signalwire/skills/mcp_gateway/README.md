# MCP Gateway Skill

Bridge MCP (Model Context Protocol) servers with SignalWire SWAIG functions, so agents can call MCP-based tools.

## Description

The MCP Gateway skill connects SignalWire agents to MCP servers through a centralized gateway service. It dynamically discovers and registers MCP tools as SWAIG functions, maintaining session state throughout each call.

## Features

The skill covers these capabilities:

- Dynamic tool discovery from MCP servers
- Session management tied to SignalWire call IDs
- Automatic cleanup on call hangup
- Support for multiple MCP services
- Selective tool loading
- HTTPS support with SSL verification
- Retry logic for resilient connections

## Requirements

The skill needs a running gateway and credentials to reach it:

- Running MCP Gateway service
- Network access to gateway
- Gateway credentials (username/password)

## Configuration

### Required Parameters

The skill needs a gateway URL and one authentication method, either basic auth credentials or a bearer token:
- `gateway_url`: URL of the MCP gateway service (required)
- `auth_user` + `auth_password`: Basic auth credentials
- or `auth_token`: Bearer token for authentication

### Optional Parameters

The rest of the parameters tune service selection and connection behavior:

- `services`: Array of services to load (default: all available)
  - `name`: Service name
  - `tools`: Array of tool names or "*" for all (default: all)
- `session_timeout`: Session timeout in seconds (default: 300)
- `tool_prefix`: Prefix for SWAIG function names (default: "mcp_")
- `retry_attempts`: Number of retry attempts (default: 3)
- `request_timeout`: HTTP request timeout in seconds (default: 30)
- `verify_ssl`: Verify SSL certificates (default: true)

## Usage

### Basic Usage (All Services)

Add the skill with a gateway URL and basic auth credentials to load every available service:

<!-- snippet: no-run starts a blocking server/client (covered by SNIPPET-COMPILE + EXAMPLES-RUN) -->
```python
from signalwire import AgentBase

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="My Agent")
        
        # Load all available MCP services
        self.add_skill("mcp_gateway", {
            "gateway_url": "http://localhost:8080",
            "auth_user": "admin",
            "auth_password": "changeme"
        })

agent = MyAgent()
agent.run()
```

### Selective Service Loading

List `services` to limit which services and tools the skill registers:

```python
# Load specific services with specific tools
self.add_skill("mcp_gateway", {
    "gateway_url": "https://gateway.example.com",
    "auth_user": "admin",
    "auth_password": "secret",
    "services": [
        {
            "name": "todo",
            "tools": ["add_todo", "list_todos"]  # Only these tools
        },
        {
            "name": "calculator",
            "tools": "*"  # All calculator tools
        }
    ],
    "session_timeout": 600,
    "tool_prefix": "ext_"
})
```

### HTTPS with Self-Signed Certificate

Set `verify_ssl` to false to connect to a gateway with a self-signed certificate:

```python
self.add_skill("mcp_gateway", {
    "gateway_url": "https://localhost:8443",
    "auth_user": "admin",
    "auth_password": "secret",
    "verify_ssl": False  # For self-signed certificates
})
```

### Bearer Token Authentication

Set `auth_token` instead of `auth_user`/`auth_password` to authenticate with a bearer token:

```python
self.add_skill("mcp_gateway", {
    "gateway_url": "https://gateway.example.com",
    "auth_token": "your-bearer-token-here",
    "services": [{
        "name": "todo"
    }]
})
```

## Generated Functions

The skill dynamically generates SWAIG functions based on discovered MCP tools. Function names follow the pattern:

`{tool_prefix}{service_name}_{tool_name}`

For example, with default settings:
- `mcp_todo_add_todo` - Add a todo item
- `mcp_todo_list_todos` - List todo items
- `mcp_calculator_add` - Calculator addition

## Example Conversations

### Using Todo Service

This exchange calls the todo service twice, once to add an item and once to list them:

```text
User: "Add a task to buy milk"
Assistant: "I'll add that to your todo list."
[Calls mcp_todo_add_todo with text="buy milk"]
Assistant: "I've added 'buy milk' to your todo list."

User: "What's on my todo list?"
Assistant: "Let me check your todos."
[Calls mcp_todo_list_todos]
Assistant: "Here are your current todos:
1. [medium] buy milk"
```

### Multiple Services

A single request can call tools from two different services:

```text
User: "Add 'finish report' to my todos and calculate 15% of 200"
Assistant: "I'll add that todo and do the calculation for you."
[Calls mcp_todo_add_todo with text="finish report"]
[Calls mcp_calculator_percent with value=200, percent=15]
Assistant: "I've added 'finish report' to your todos. 15% of 200 is 30."
```

## Session Management

The skill manages sessions automatically:

- Each SignalWire call gets its own MCP session
- Sessions persist across multiple tool calls
- Automatic cleanup on call hangup
- Configurable timeout for inactive sessions

### Custom Session ID

You can override the session ID by setting `mcp_call_id` in global_data:

```python
# In your agent code
self.set_global_data({
    "mcp_call_id": "custom-session-123"
})

# Or in a SWAIG function
result = SwaigFunctionResult("Session changed")
result.update_global_data({"mcp_call_id": "new-session-456"})
```

This is useful for:
- Managing multiple MCP sessions within a single call
- Sharing MCP sessions across different calls
- Custom session management strategies

## Troubleshooting

### Gateway Connection Failed

Check:
1. Gateway service is running
2. Correct URL and credentials
3. Network connectivity
4. Firewall rules

### SSL Certificate Errors

For self-signed certificates:
<!-- snippet: no-compile config-key-fragment (single dict entry, not a module) -->
```python
"verify_ssl": False
```

For custom CA certificates, ensure they're in the system trust store.

### Tool Not Found

Verify:
1. Service name is correct
2. Tool name matches exactly
3. Tool is included in service configuration
4. MCP server is returning tools correctly

### Session Timeouts

Increase timeout if needed:
<!-- snippet: no-compile config-key-fragment (single dict entry, not a module) -->
```python
"session_timeout": 600  # 10 minutes
```

## Gateway Setup

To run the MCP Gateway service:

```bash
mcp-gateway

# Or with custom config
mcp-gateway -c myconfig.json
```

## Security Considerations

Apply these five practices before you deploy a gateway:

1. Always use HTTPS in production
2. Use strong authentication credentials
3. Limit service access to required tools only
4. Monitor gateway logs for suspicious activity
5. Set appropriate session timeouts
