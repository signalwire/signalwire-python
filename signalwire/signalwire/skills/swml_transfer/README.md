# SWML Transfer Skill

Transfer calls between agents using SWML with pattern matching. This skill enables agents to transfer calls to other agents based on user input patterns, with full control over transfer messages and behaviors.

## Description

The SWML Transfer skill provides a flexible way to implement call transfers between agents. It uses pattern matching to determine where to transfer calls based on user input, making it ideal for routing scenarios like transferring to sales, support, or other specialized agents.

## Features

- **Pattern-based routing** - Use regex patterns to match user input
- **Multiple instances** - Load the skill multiple times with different configurations
- **Customizable messages** - Configure pre-transfer and post-transfer messages
- **Post-processing control** - Enable/disable post-processing per transfer
- **Dynamic URL support** - Transfer to any URL endpoint
- **Fallback handling** - Default behavior when no pattern matches
- **Automatic prompt sections** - Adds "Transferring" section listing all configured destinations
- **Required fields collection** - Collect any required data before transfer

## Requirements

- No additional Python packages required
- No environment variables required

## Configuration

### Required Parameters

- `transfers`: Dictionary mapping regex patterns to transfer configurations

### Optional Parameters

- `tool_name` (default: "transfer_call"): Name of the transfer function
- `description` (default: "Transfer call based on pattern matching"): Tool description
- `parameter_name` (default: "transfer_type"): Name of the parameter for the transfer function
- `parameter_description` (default: "The type of transfer to perform"): Parameter description
- `default_message` (default: "Please specify a valid transfer type."): Message when no pattern matches
- `default_post_process` (default: False): Post-processing flag for default case
- `required_fields` (default: {}): Object mapping field names to descriptions for data collection

### Transfer Configuration

Each entry in the `transfers` dictionary should have:
- **Pattern (key)**: Regex pattern to match (e.g., "/sales/i" for case-insensitive)
- **Configuration (value)**: Dictionary with:
  - **One of these required**:
    - `url`: Transfer to SWML endpoint (uses swml_transfer action)
    - `address`: Transfer to phone/SIP address (uses connect action)
  - `message` (optional): Pre-transfer message
  - `return_message` (optional): Post-transfer message (only used when `final` is False)
  - `post_process` (optional): Boolean for post-processing (default: True)
  - `final` (optional): Boolean for permanent transfer (default: True)
    - `True`: Permanent transfer - call exits agent completely (default)
    - `False`: Temporary transfer - control returns after transfer completes
  - `from_addr` (optional): Caller ID override for connect action (only with `address`)

## Usage

### Basic Usage

```python
from signalwire_agents import AgentBase

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="Routing Agent", route="/router")
        
        # Add transfer capability
        self.add_skill("swml_transfer", {
            "tool_name": "transfer_to_department",
            "transfers": {
                "/sales/i": {
                    "url": "https://example.com/sales",
                    "message": "I'll connect you with our sales team.",
                    "return_message": "Thank you for speaking with sales."
                },
                "/support/i": {
                    "url": "https://example.com/support",
                    "message": "Let me transfer you to technical support.",
                    "return_message": "I hope support was able to help!"
                }
            }
        })

agent = MyAgent()
agent.serve()
```

### Advanced Configuration

```python
# Multiple transfer types with custom messages
self.add_skill("swml_transfer", {
    "tool_name": "route_call",
    "description": "Route calls to appropriate departments",
    "parameter_name": "department",
    "parameter_description": "Which department to transfer to",
    "transfers": {
        "/sales|billing|pricing/i": {
            "url": "https://api.company.com/sales-agent",
            "message": "I'll connect you with our sales team for pricing and billing questions.",
            "return_message": "Thank you for contacting our sales department.",
            "post_process": True,
            "final": False  # Temporary transfer - returns control
        },
        "/support|technical|help/i": {
            "url": "https://api.company.com/support-agent",
            "message": "Let me transfer you to our technical support team.",
            "return_message": "I hope we were able to resolve your technical issue.",
            "post_process": True,
            "final": False  # Temporary transfer - returns control
        },
        "/manager|supervisor/i": {
            "url": "https://api.company.com/manager-agent",
            "message": "I understand you'd like to speak with a manager. One moment please.",
            "return_message": "Thank you for your patience.",
            "post_process": False,
            "final": False  # Temporary transfer - returns control
        },
        "/disconnect|goodbye/i": {
            "url": "https://api.company.com/closing-agent",
            "message": "Thank you for calling. Goodbye!",
            "post_process": True,
            "final": True  # Permanent transfer - exits this agent completely
        }
    },
    "default_message": "I can transfer you to sales, support, or a manager. Which would you prefer?",
    "default_post_process": False
})
```

### Permanent vs Temporary Transfers

```python
# Permanent transfer example - call exits agent completely
self.add_skill("swml_transfer", {
    "tool_name": "permanent_transfer",
    "transfers": {
        "/billing/i": {
            "url": "https://example.com/billing-specialist",
            "message": "I'll transfer you to our billing specialist. Goodbye!",
            "final": True  # Call won't return to this agent
        }
    }
})

# Temporary transfer example - call returns after transfer
self.add_skill("swml_transfer", {
    "tool_name": "temporary_transfer",
    "transfers": {
        "/specialist/i": {
            "url": "https://example.com/specialist",
            "message": "Let me connect you with a specialist.",
            "return_message": "Welcome back! Is there anything else I can help with?",
            "final": False  # Call returns to this agent after transfer
        }
    }
})
```

### Phone Number and SIP Address Transfers

```python
# Transfer to phone numbers and SIP addresses using 'address'
self.add_skill("swml_transfer", {
    "tool_name": "direct_transfer",
    "transfers": {
        "/emergency/i": {
            "address": "+15551234567",  # Phone number
            "message": "Transferring you to our emergency line.",
            "final": True
        },
        "/voicemail/i": {
            "address": "sip:voicemail@company.com",  # SIP address
            "message": "Transferring to voicemail.",
            "from_addr": "+15559876543",  # Optional caller ID
            "final": True
        },
        "/callback/i": {
            "address": "+15551111111",
            "message": "I'll connect you for a callback.",
            "return_message": "The callback is complete. Anything else?",
            "final": False  # Temporary transfer
        }
    }
})
```

### Mixed Transfer Types

```python
# Mix SWML endpoints and direct addresses in one skill
self.add_skill("swml_transfer", {
    "tool_name": "transfer",
    "transfers": {
        # SWML agent transfers
        "/sales|billing/i": {
            "url": "https://api.company.com/sales-agent",
            "message": "Transferring to our sales team.",
            "final": False
        },
        "/support/i": {
            "url": "https://api.company.com/support-agent",
            "message": "Transferring to technical support.",
            "final": False
        },
        # Direct phone transfers
        "/operator/i": {
            "address": "+18005551234",
            "message": "Connecting you with an operator.",
            "final": True
        },
        # SIP transfers
        "/conference/i": {
            "address": "sip:conference@company.com",
            "message": "Joining you to the conference.",
            "from_addr": "+15559876543",
            "final": True
        }
    }
})
```

### Multiple Instances

You can load the skill multiple times for different transfer scenarios:

```python
# General department transfers
self.add_skill("swml_transfer", {
    "tool_name": "transfer_to_department",
    "transfers": {
        "/sales/i": {"url": "https://example.com/sales"},
        "/support/i": {"url": "https://example.com/support"}
    }
})

# Language-specific transfers
self.add_skill("swml_transfer", {
    "tool_name": "transfer_to_language",
    "parameter_name": "language",
    "transfers": {
        "/spanish|español/i": {
            "url": "https://example.com/es-agent",
            "message": "Le transferiré a un agente que habla español."
        },
        "/french|français/i": {
            "url": "https://example.com/fr-agent",
            "message": "Je vais vous transférer à un agent francophone."
        }
    }
})

# With required fields collection
self.add_skill("swml_transfer", {
    "tool_name": "transfer_with_data",
    "required_fields": {
        "summary": "Summary of the conversation",
        "customer_name": "Customer's full name",
        "issue_type": "Type of issue (technical/billing/general)"
    },
    "transfers": {
        "/sales/i": {
            "url": "https://example.com/sales",
            "message": "I'll transfer you to sales with your information."
        },
        "/support/i": {
            "url": "https://example.com/support",
            "message": "I'll transfer you to support with your information."
        }
    }
})
```

## Generated Functions

The skill generates a single SWAIG function with the configured name:

### Function: `transfer_call` (or custom `tool_name`)

**Parameters:**
- `transfer_type` (or custom `parameter_name`): String parameter that will be matched against configured patterns
- Additional parameters defined in `required_fields` configuration

**Behavior:**
1. Takes the input parameter value
2. Matches it against configured regex patterns in order
3. If `required_fields` are configured, saves all field values to `global_data.call_data`
4. If a match is found, transfers to the corresponding URL with configured messages
5. If no match is found, returns the default message (data still saved if provided)

## Prompt Sections

The skill automatically adds prompt sections to help the AI understand available transfer destinations:

### Transferring Section
Lists all configured transfer destinations extracted from the patterns. For example:
```
## Transferring
You can transfer calls using the transfer_to_department function with the following destinations:
- "sales" - transfers to https://example.com/sales
- "support" - transfers to https://example.com/support
```

### Transfer Instructions Section
Provides usage instructions for the transfer capability:
```
## Transfer Instructions
How to use the transfer capability:
- Use the transfer_to_department function when a transfer is needed
- Pass the destination type to the 'department' parameter
- The system will match patterns and handle the transfer automatically
- After transfer completes, you'll regain control of the conversation
```

## Example Conversations

### Example 1: Department Transfer
```
User: "I need help with my order"
Agent: "I can help you with that. Would you like to speak with sales or support?"
User: "I think I need support"
Agent: [Uses transfer_to_department("support")]
System: "Let me transfer you to our technical support team."
[Transfer occurs]
System: "I hope we were able to resolve your technical issue."
```

### Example 2: Multi-pattern Match
```
User: "I want to talk to someone about pricing"
Agent: [Uses route_call("pricing")]
System: "I'll connect you with our sales team for pricing and billing questions."
[Transfer to sales agent]
```

### Example 3: No Match
```
User: "Transfer me to the CEO"
Agent: [Uses transfer_to_department("CEO")]
System: "I can transfer you to sales, support, or a manager. Which would you prefer?"
```

### Example 4: Transfer with Required Fields
```
User: "I need to speak with support about my PC that won't boot"
Agent: "I'll transfer you to support. Let me collect some information first."
Agent: [Uses transfer_with_data("support", "Customer experiencing boot failure with their PC. Initial troubleshooting not yet performed.", "John Smith", "technical")]
System: "I'll transfer you to support with your information."
[Transfer occurs with data saved to global_data.call_data]
Support Agent: [Can access the data via ${global_data.call_data.summary}, ${global_data.call_data.customer_name}, etc.]
```

## Troubleshooting

### Transfer Not Working
- Verify the URL is accessible and returns valid SWML
- Check that the pattern syntax is correct (regex format)
- Enable debug logging to see pattern matching results

### Pattern Not Matching
- Remember to use case-insensitive flag `/i` if needed
- Test patterns with online regex tools
- Use pipe `|` for multiple options: `/sales|billing/i`

### Authentication Issues
- Ensure URLs include authentication if required
- Use `agent.get_full_url(include_auth=True)` for building URLs in dynamic configs

## Best Practices

1. **Use Clear Patterns**: Make patterns specific enough to avoid false matches
2. **Provide Context**: Use descriptive messages so users know what's happening
3. **Handle Failures**: Always include a sensible default message
4. **Test Patterns**: Verify regex patterns match expected inputs
5. **Group Related Transfers**: Use pipe `|` to group similar departments/options

## Dynamic URL Configuration

For agents that need to build URLs dynamically (e.g., with proxy detection), implement the skill loading in a dynamic configuration callback:

```python
def configure_transfers(self, query_params, body_params, headers, agent):
    # Build URLs with proper proxy detection
    base_url = self.get_full_url(include_auth=True).rstrip('/')
    
    agent.add_skill("swml_transfer", {
        "transfers": {
            "/sales/i": {
                "url": f"{base_url}/sales",
                "message": "Transferring to sales..."
            }
        }
    })
```