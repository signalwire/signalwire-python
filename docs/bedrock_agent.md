# BedrockAgent Documentation

## Overview

BedrockAgent is a specialized agent implementation that integrates Amazon Bedrock's voice-to-voice model with SignalWire's agent ecosystem. It extends AgentBase to provide full compatibility with all SignalWire agent features. It generates SWML (SignalWire Markup Language) documents with the `amazon_bedrock` verb instead of the standard `ai` verb.

## Key Features

BedrockAgent adds the following to the standard agent feature set:

- **Full Agent Compatibility**: Inherits all capabilities from AgentBase including skills, tools, POM (Prompt Object Model), and SWAIG (SignalWire AI Gateway) functions
- **Bedrock Integration**: Generates SWML with `amazon_bedrock` verb for native Bedrock support
- **Voice-to-Voice Model**: Uses Amazon Bedrock's fixed voice-to-voice model
- **Drop-in Migration**: Drop-in replacement for standard agents when using Bedrock

## Installation

BedrockAgent is included in the signalwire-sdk package:

```python
from signalwire import BedrockAgent
```

## Basic Usage

### Creating a BedrockAgent

Construct a `BedrockAgent` the same way you construct a standard agent, and run it the same way.

<!-- snippet: no-run starts a blocking server/client (covered by SNIPPET-COMPILE + EXAMPLES-RUN) -->
```python
from signalwire import BedrockAgent

# Create a basic Bedrock agent
agent = BedrockAgent(
    name="my_bedrock_agent",
    system_prompt="You are a helpful AI assistant.",
    voice_id="tiffany",
    temperature=0.7
)

# Run as SWML server
agent.run()
```

### With Skills and Tools

BedrockAgent loads skills and defines custom tools the same way a standard agent does.

<!-- snippet: no-run starts a blocking server/client (covered by SNIPPET-COMPILE + EXAMPLES-RUN) -->
```python
from signalwire import BedrockAgent, FunctionResult

agent = BedrockAgent(
    name="advanced_bedrock",
    system_prompt="You are an AI assistant with various capabilities.",
    voice_id="matthew",
    temperature=0.8,
    top_p=0.9,
    max_tokens=1024
)

# Add skills
agent.add_skill("datetime")
agent.add_skill("weather_api", {"api_key": "your_api_key"})

# Add a custom tool. A tool decorated outside a class body takes
# (args, raw_data), not (self, args, raw_data).
@agent.tool(
    "calculate_sum",
    description="Add two numbers together",
    parameters={
        "a": {"type": "integer", "description": "The first number"},
        "b": {"type": "integer", "description": "The second number"},
    },
)
def calculate_sum(args, raw_data):
    a = args.get("a", 0)
    b = args.get("b", 0)
    return FunctionResult(f"The sum of {a} and {b} is {a + b}")

# Run the agent
if __name__ == "__main__":
    agent.run()
```

## Constructor Parameters

The constructor accepts these parameters, all of which are optional:

<!-- snippet: no-compile signature-illustration -->
```python
BedrockAgent(
    name: str = "bedrock_agent",      # Agent name
    route: str = "/bedrock",          # HTTP route for the agent
    system_prompt: Optional[str] = None,  # Initial system prompt
    voice_id: str = "matthew",        # tiffany, matthew, amy, lupe or carlos
    temperature: float = 0.7,         # Generation temperature (0-1)
    top_p: float = 0.9,              # Nucleus sampling parameter (0-1)
    max_tokens: int = 1024,          # Maximum tokens to generate
    **kwargs                         # Additional arguments passed to AgentBase
)
```

### Available Voice IDs

The SWML schema accepts five Bedrock voice IDs:
- `tiffany`
- `matthew` (the default)
- `amy`
- `lupe`
- `carlos`

## Available Methods

### All AgentBase Methods

BedrockAgent inherits all methods from AgentBase, including:

#### Prompt Management
- `set_prompt_text(text)` - Set the prompt as raw text
- `set_prompt_pom(pom)` - Set the prompt as a POM dictionary
- `prompt_add_section(title, body, bullets)` - Add sections to the prompt
- `set_post_prompt(text)` - Set post-prompt for summary generation

#### Skills
- `add_skill(skill_name, params)` - Add a skill to the agent
- `remove_skill(skill_name)` - Remove a skill
- `list_skills()` - List loaded skills
- `has_skill(skill_name)` - Check if a skill is loaded

#### Tools/Functions
- `@agent.tool` - Decorator for defining SWAIG tools
- `define_tool(name, description, parameters, handler)` - Define a tool programmatically
- `register_swaig_function(function_dict)` - Register a raw SWAIG function

#### Configuration
- `add_hint(hint)` - Add hints for the AI
- `add_language(name, code, voice)` - Add language configuration
- `set_params(params)` - Set AI parameters
- `set_global_data(data)` - Set global data available to AI

#### Web Server & Routing
- `run()` - Start the agent (auto-detects environment)
- `serve(host, port)` - Start web server explicitly
- `enable_sip_routing()` - Enable SIP-based routing
- `register_sip_username(username)` - Register SIP username

### BedrockAgent-Specific Methods

#### Voice Configuration

Call `set_voice()` to change the voice after construction:

```python
agent.set_voice("amy")  # Change the Bedrock voice
```

#### Inference Parameters

Call `set_inference_params()` to change temperature, top_p, or max_tokens after construction:

```python
# Update inference parameters
agent.set_inference_params(
    temperature=0.8,
    top_p=0.95,
    max_tokens=2048
)
```

### Disabled/Modified Methods

The following methods have modified behavior in BedrockAgent:

1. **`set_llm_model(model)`** - Logs warning and does nothing (Bedrock uses fixed model)
2. **`set_llm_temperature(temperature)`** - Redirects to `set_inference_params()`
3. **`set_post_prompt_llm_params(**params)`** - Logs warning (post-prompt uses OpenAI)
4. **`set_prompt_llm_params(**params)`** - Accepts the settings the Bedrock `prompt` object defines. `temperature`, `top_p` and `max_tokens` update the inference settings, as `set_inference_params()` does. `confidence`, `presence_penalty` and `frequency_penalty` go into the prompt. Other settings, such as `barge_confidence`, log a warning and are ignored

## SWML Output Structure

BedrockAgent generates SWML with the `amazon_bedrock` verb:

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "answer": {}
      },
      {
        "amazon_bedrock": {
          "prompt": {
            "text": "Your system prompt here",
            "voice_id": "matthew",
            "temperature": 0.3,
            "top_p": 1.0,
            "max_tokens": 1024
          },
          "SWAIG": {
            "functions": [...],
            "defaults": {
              "web_hook_url": "http://..."
            }
          },
          "params": {},
          "global_data": {}
        }
      }
    ]
  }
}
```

## Key Differences from Standard Agent

BedrockAgent differs from a standard agent in five ways:

1. **Verb Name**: Generates `amazon_bedrock` verb instead of `ai`
2. **Voice Configuration**: Voice ID is included in the prompt object (Bedrock-specific)
3. **Fixed Model**: Cannot change the underlying model (always uses Bedrock voice-to-voice)
4. **Parameter Handling**: Simplified parameter configuration focused on inference settings
5. **Post-Prompt**: Post-prompt summarization still uses OpenAI

## Testing with swaig-test

BedrockAgent is fully compatible with swaig-test:

```bash
# List functions
swaig-test examples/bedrock_with_skills.py --list-tools

# Dump SWML
swaig-test examples/bedrock_with_skills.py --dump-swml

# Test a function
swaig-test examples/bedrock_with_skills.py --exec get_current_time
```

## Complete Example

This example combines a POM prompt, a language, two skills, two custom tools, and SIP routing in one agent.

<!-- snippet: no-run starts a blocking server/client (covered by SNIPPET-COMPILE + EXAMPLES-RUN) -->
```python
#!/usr/bin/env python3
from signalwire import BedrockAgent, FunctionResult
import os

# Create a BedrockAgent with full configuration
agent = BedrockAgent(
    name="production_bedrock",
    route="/api/bedrock",
    system_prompt="You are a professional AI assistant.",
    voice_id="matthew",
    temperature=0.7,
    top_p=0.9,
    max_tokens=1024
)

# Configure prompt with POM
agent.prompt_add_section(
    "Role",
    "You are a helpful customer service agent.",
    bullets=[
        "Be professional and courteous",
        "Provide accurate information",
        "Ask clarifying questions when needed"
    ]
)

# Add languages
agent.add_language(
    name="Spanish",
    code="es",
    voice="miguel"  # Bedrock will map this appropriately
)

# Add skills
agent.add_skill("datetime")
if os.environ.get("WEATHER_API_KEY"):
    agent.add_skill("weather_api", {
        "api_key": os.environ["WEATHER_API_KEY"]
    })

# Add custom tools
@agent.tool("transfer_to_support", description="Transfer the call to the support department")
def transfer_to_support(args, raw_data):
    return FunctionResult("Transferring you to support now.").connect("+15551234567")

@agent.tool(
    "check_order_status",
    description="Check the status of an order",
    parameters={"order_id": {"type": "string", "description": "The order ID to look up"}},
)
def check_order_status(args, raw_data):
    order_id = args.get("order_id", "")
    # Simulate an order lookup
    return FunctionResult(f"Order {order_id} is currently being processed and will ship tomorrow.")

# Enable SIP routing
agent.enable_sip_routing()
agent.register_sip_username("bedrock-support")

# Run the agent
if __name__ == "__main__":
    print(f"Starting BedrockAgent on {agent.get_full_url()}")
    agent.run()
```

## Deployment Considerations

Keep these points in mind when deploying a BedrockAgent:

1. **Environment Variables**: Set API keys for skills that require them
2. **Authentication**: Uses the same HTTP Basic Auth as standard agents: username `signalwire` and an auto-generated password unless `SWML_BASIC_AUTH_USER`/`SWML_BASIC_AUTH_PASSWORD` are set
3. **Port Configuration**: Default port 3000, configurable via constructor or environment
4. **Production**: Use proper authentication and HTTPS in production environments

## Migration from Standard Agent

Migrating from a standard Agent to BedrockAgent needs only a few changes:

```python
# Before
from signalwire import AgentBase
agent = AgentBase(name="my_agent")

# After
from signalwire import BedrockAgent
agent = BedrockAgent(name="my_agent", voice_id="matthew")
```

Most code will work without modification. Only adjust:
- Voice configuration (use Bedrock voice IDs)
- Model-specific parameters (use `set_inference_params()`)
- Remove any `set_llm_model()` calls

## Troubleshooting

### Common Issues

These issues come up most often:

1. **Voice not changing**: Ensure you're using valid Bedrock voice IDs
2. **Parameters not applying**: Bedrock's prompt defines `temperature`, `top_p`, `max_tokens`, `confidence`, `presence_penalty` and `frequency_penalty`. Other settings, such as `barge_confidence`, are ignored with a warning
3. **Skills not loading**: Check API keys are properly configured
4. **SWML not generating**: Verify the agent is running and accessible

### Debug Mode

Enable debug logging to troubleshoot:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

agent = BedrockAgent(name="debug_agent")
agent.enable_debug_routes()
```

## Best Practices

Follow these practices when building with BedrockAgent:

1. **Voice Selection**: Choose appropriate voices for your use case and language
2. **Temperature Settings**: Lower values (0.3-0.5) for factual responses, higher (0.7-0.9) for creative tasks
3. **Skill Loading**: Load only necessary skills to minimize token usage
4. **Error Handling**: Implement proper error handling in custom tools
5. **Testing**: Use swaig-test extensively before deployment

## Limitations

BedrockAgent carries these limits:

- Cannot change the underlying AI model (Bedrock uses a fixed voice-to-voice model)
- Post-prompt summarization uses OpenAI for compatibility with existing integrations
- Text-specific features like hints and pronunciation rules don't apply to voice models
- Voice options limited to Bedrock's available voices

## See Also

For more information, see:

- [AgentBase Documentation](agent_guide.md)
- [Skills Documentation](skills_system.md)
- [SWAIG Functions Documentation](swaig_reference.md)
- [SignalWire AI Gateway Documentation](https://docs.signalwire.com/topics/ai-gateway/)

## Amazon Bedrock Verb Keys

The `amazon_bedrock` verb in SWML supports the following keys:

**Top-level keys:**
- `prompt` - Prompt configuration with text/POM and voice settings
- `SWAIG` - Function definitions and webhook configuration
- `params` - Session settings such as `attention_timeout` and `inactivity_timeout`
- `global_data` - Global data available to all functions
- `post_prompt` - Post-prompt text for summary generation
- `post_prompt_url` - URL for posting conversation summaries

**Within nested objects:**
- **prompt**: `text` or `pom`, `voice_id`, `temperature`, `top_p`, `max_tokens`, `confidence`, `presence_penalty`, `frequency_penalty`
- **SWAIG**: `functions`, `defaults`
- **params**: session settings such as `attention_timeout`, `inactivity_timeout`, and `hard_stop_time`, not the inference settings in `prompt`
- **global_data**: (any custom key-value pairs)

**Features not applicable to voice-to-voice models:**
- `languages` - Language configuration (voice models handle languages natively through voice)
- `hints` - AI hints (voice models process audio directly without text hints)
- `pronounce` - Pronunciation rules (not needed as voice input preserves pronunciation)

These features are designed for text-based AI models and don't apply to Bedrock's voice-to-voice architecture. `BedrockAgent` passes `confidence`, `presence_penalty` and `frequency_penalty` through from `set_prompt_llm_params()`, and leaves out `barge_confidence`, which the Bedrock `prompt` object doesn't define.
