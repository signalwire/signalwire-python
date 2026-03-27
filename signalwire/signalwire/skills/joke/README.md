# Joke Skill

Tell jokes using the API Ninjas joke API with DataMap integration.

## Description

The Joke skill provides joke-telling capabilities to your SignalWire AI agents using the API Ninjas joke API. This skill demonstrates how to use DataMap for external API integration without requiring custom webhook endpoints.

## Features

- **Random Jokes**: Get random jokes from API Ninjas
- **Dad Jokes**: Specifically request dad jokes
- **DataMap Integration**: Uses DataMap for serverless API execution
- **Configurable Tool Name**: Support for custom tool names
- **Required Parameter Validation**: Ensures joke type is specified

## Requirements

- API Ninjas API key
- No additional Python packages required (DataMap handles API calls)

## Configuration

### Required Parameters

- `api_key`: Your API Ninjas API key

### Optional Parameters

- `tool_name`: Custom name for the joke function (default: "get_joke")

## Usage

### Basic Usage

```python
from signalwire_agents import AgentBase

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="Joke Agent", route="/jokes")
        
        # Add joke skill
        self.add_skill("joke", {
            "api_key": "your-api-ninjas-api-key"
        })

agent = MyAgent()
agent.serve()
```

### Advanced Usage

```python
# Custom tool name
self.add_skill("joke", {
    "api_key": "your-api-ninjas-api-key",
    "tool_name": "tell_joke"
})
```

## Function Details

### `get_joke(type: str)`

**Parameters:**
- `type` (required): Type of joke to get
  - `"jokes"` - Regular jokes
  - `"dadjokes"` - Dad jokes

**Returns:** A joke from the API Ninjas joke database

**Example Usage:**
- "Tell me a joke" (AI will choose the type)
- "Tell me a dad joke" (AI will use type="dadjokes")
- "Get me a regular joke" (AI will use type="jokes")

## API Integration

This skill integrates with the API Ninjas Jokes API:
- **Endpoint**: `https://api.api-ninjas.com/v1/{type}`
- **Method**: GET
- **Authentication**: X-Api-Key header
- **Response**: JSON array with joke objects

## Getting an API Key

1. Visit [API Ninjas](https://api.api-ninjas.com/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Use the key in your skill configuration

## Error Handling

- Missing API key: Skill setup will fail with clear error message
- Invalid joke type: Parameter validation ensures only valid types are accepted
- API errors: Handled gracefully with user-friendly error messages

## DataMap Implementation

This skill demonstrates DataMap usage with:

- **External API**: Calls API Ninjas joke endpoints
- **Dynamic URLs**: Uses `${args.type}` for different joke types  
- **Header Authentication**: Includes API key in request headers
- **Response Processing**: Extracts joke from API response array
- **Error Handling**: Handles API errors gracefully

## Troubleshooting

### Common Issues

1. **"Missing required parameters: ['api_key']"**
   - Ensure you provide a valid API Ninjas API key

2. **"No jokes returned"**
   - Check your API key is valid
   - Verify API Ninjas service is accessible
   - Check API quota/rate limits

3. **"Tool not found"**
   - Ensure skill loaded successfully
   - Check for any setup errors in logs

### Debugging

Enable debug logging to see API requests:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Reference

### API Ninjas Endpoints

- `GET /v1/jokes` - Random jokes
- `GET /v1/dadjokes` - Dad jokes

### Response Format

```json
[
  {
    "joke": "Why don't scientists trust atoms? Because they make up everything!"
  }
]
``` 