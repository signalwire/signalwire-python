# Lesson 1: Creating Your First Agent

In this lesson, you'll learn how to create a simple AI-powered voice agent using the SignalWire Agents SDK. We'll build Morgan, a friendly sales specialist who can help customers with PC building recommendations.

## Table of Contents

1. [Understanding Agent Architecture](#understanding-agent-architecture)
2. [Creating a Basic Agent](#creating-a-basic-agent)
3. [Configuring Agent Prompts](#configuring-agent-prompts)
4. [Adding Voice and Language](#adding-voice-and-language)
5. [Running Your Agent](#running-your-agent)
6. [Testing Your Agent](#testing-your-agent)
7. [Enabling SSL/HTTPS](#enabling-sslhttps)
8. [Summary](#summary)

---

## Understanding Agent Architecture

SignalWire Agents are Python classes that inherit from `AgentBase`. Every agent has:

**Core Components:**

- **Name**: A descriptive name for your agent
- **Route**: The HTTP endpoint where the agent listens (e.g., `/`, `/sales`)
- **Host/Port**: Network configuration for the agent server
- **Prompt**: Instructions that define the agent's behavior
- **Language/Voice**: Text-to-speech configuration

**Key Concepts:**

- Agents handle voice conversations through the SignalWire platform
- Each agent exposes an HTTP endpoint that returns SWML (SignalWire Markup Language)
- The SWML document defines how the agent behaves during calls

---

## Creating a Basic Agent

Let's create our first agent. We'll build Morgan, a sales specialist for PC Builder Pro.

### Step 1: Import Required Modules

```python
#!/usr/bin/env python3
"""
Simple Sales Agent - Morgan
A friendly PC building sales specialist
"""

from signalwire import AgentBase

class SalesAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="PC Builder Sales Agent - Morgan",
            route="/",
            host="0.0.0.0",
            port=3000
        )
```

### Step 2: Understanding the Parameters

**Constructor Parameters:**

- `name`: Identifies your agent in logs and debugging
- `route`: The URL path where the agent listens (use `/` for root)
- `host`: Network interface to bind to (`0.0.0.0` listens on all interfaces)
- `port`: TCP port for the HTTP server (default: 3000)

---

## Configuring Agent Prompts

The Prompt Object Model (POM) provides a structured way to define agent behavior. Instead of one long prompt, you organize instructions into logical sections.

### Step 3: Add the Agent's Role

```python
def __init__(self):
    super().__init__(
        name="PC Builder Sales Agent - Morgan",
        route="/",
        host="0.0.0.0",
        port=3000
    )
    
    # Configure the agent's personality and role
    self.prompt_add_section(
        "AI Role",
        body=(
            "You are Morgan, a passionate PC building expert and sales specialist "
            "at PC Builder Pro. You're known for your deep knowledge of components "
            "and your ability to match customers with their perfect build. You get "
            "excited about the latest hardware and love sharing that enthusiasm. "
            "Always introduce yourself by name."
        )
    )
```

### Step 4: Define Areas of Expertise

```python
    # Add expertise section
    self.prompt_add_section(
        "Your Expertise",
        body="Areas of specialization:",
        bullets=[
            "Custom PC builds for all budgets",
            "Component compatibility and optimization",
            "Performance recommendations",
            "Price/performance analysis",
            "Current market trends"
        ]
    )
```

### Step 5: Define Tasks and Workflow

```python
    # Define the sales workflow
    self.prompt_add_section(
        "Your Tasks",
        body="Complete sales process workflow with passion and expertise:",
        bullets=[
            "Greet customers warmly and introduce yourself",
            "Understand their specific PC building requirements",
            "Ask about budget, intended use, and preferences",
            "Provide knowledgeable recommendations",
            "Share your enthusiasm for PC building",
            "Offer to explain technical details when helpful"
        ]
    )
```

### Step 6: Add Voice Instructions

```python
    # Voice and tone instructions
    self.prompt_add_section(
        "Voice Instructions",
        body=(
            "Share your passion for PC building and get excited about "
            "helping customers create their perfect system. Your enthusiasm "
            "should be genuine and infectious."
        )
    )
```

---

## Adding Voice and Language

SignalWire supports multiple text-to-speech voices. Let's configure Morgan's voice:

### Step 7: Configure Voice Settings

```python
    # Configure language and voice
    self.add_language(
        name="English",
        code="en-US",
        voice="rime.marsh"  # A friendly, enthusiastic voice
    )
```

**Available Voices:**

- `rime.spore` - Energetic and upbeat
- `rime.marsh` - Warm and friendly
- `rime.cove` - Calm and professional
- And many more...

---

## Running Your Agent

### Complete Code

Here's the complete `sales_agent.py`:

<!-- snippet: no-run starts a blocking server/client (covered by SNIPPET-COMPILE + EXAMPLES-RUN) -->
```python
#!/usr/bin/env python3
"""
Simple Sales Agent - Morgan
A friendly PC building sales specialist
"""

from signalwire import AgentBase

class SalesAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="PC Builder Sales Agent - Morgan",
            route="/",
            host="0.0.0.0",
            port=3000
        )
        
        # Configure the agent's personality and role
        self.prompt_add_section(
            "AI Role",
            body=(
                "You are Morgan, a passionate PC building expert and sales specialist "
                "at PC Builder Pro. You're known for your deep knowledge of components "
                "and your ability to match customers with their perfect build. You get "
                "excited about the latest hardware and love sharing that enthusiasm. "
                "Always introduce yourself by name."
            )
        )
        
        # Add expertise section
        self.prompt_add_section(
            "Your Expertise",
            body="Areas of specialization:",
            bullets=[
                "Custom PC builds for all budgets",
                "Component compatibility and optimization",
                "Performance recommendations",
                "Price/performance analysis",
                "Current market trends"
            ]
        )
        
        # Define the sales workflow
        self.prompt_add_section(
            "Your Tasks",
            body="Complete sales process workflow with passion and expertise:",
            bullets=[
                "Greet customers warmly and introduce yourself",
                "Understand their specific PC building requirements",
                "Ask about budget, intended use, and preferences",
                "Provide knowledgeable recommendations",
                "Share your enthusiasm for PC building",
                "Offer to explain technical details when helpful"
            ]
        )
        
        # Voice and tone instructions
        self.prompt_add_section(
            "Voice Instructions",
            body=(
                "Share your passion for PC building and get excited about "
                "helping customers create their perfect system. Your enthusiasm "
                "should be genuine and infectious."
            )
        )
        
        # Configure language and voice
        self.add_language(
            name="English",
            code="en-US",
            voice="rime.marsh"  # A friendly, enthusiastic voice
        )

def main():
    """Main function to run the agent"""
    agent = SalesAgent()
    
    print("Starting PC Builder Sales Agent - Morgan")
    print("=" * 50)
    print("Agent running at: http://localhost:3000/")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nShutting down agent...")

if __name__ == "__main__":
    main()
```

### Step 8: Run the Agent

```bash
# Make sure you're in the signalwire-agents directory
cd /path/to/signalwire-agents

# Run the agent
python tutorial/sales_agent.py
```

You should see:
```
Starting PC Builder Sales Agent - Morgan
==================================================
Agent running at: http://localhost:3000/
Press Ctrl+C to stop
==================================================
```

---

## Testing Your Agent

### Method 1: Get SWML Document

```bash
# Get the SWML configuration
curl http://localhost:3000/

# With pretty printing
curl http://localhost:3000/ | python -m json.tool
```

### Method 2: Test with swaig-test

```bash
# Install the SDK if not already done
pip install -e .

# Test the agent
swaig-test tutorial/sales_agent.py --dump-swml
```

### Understanding the SWML Output

The agent returns a JSON document that SignalWire uses to control the call:

```json
{
  "ai": {
    "voice": "rime.marsh",
    "language": {
      "name": "English",
      "code": "en-US",
      "voice": "rime.marsh"
    },
    "prompt": {
      "sections": [
        {
          "title": "AI Role",
          "body": "You are Morgan..."
        }
        // ... other sections
      ]
    }
  }
}
```

---

## Enabling SSL/HTTPS

For production deployments, you'll want to enable SSL/HTTPS:

### Method 1: Using Environment Variables

```bash
# Set SSL environment variables
export SWML_SSL_ENABLED=true
export SWML_SSL_CERT_PATH=/path/to/your/certificate.pem
export SWML_SSL_KEY_PATH=/path/to/your/private-key.pem
export SWML_DOMAIN=yourdomain.com

# Run the agent with SSL
python tutorial/sales_agent.py
```

### Method 2: Using a Single Command

```bash
SWML_SSL_ENABLED=true \
SWML_SSL_CERT_PATH=/path/to/cert.pem \
SWML_SSL_KEY_PATH=/path/to/key.pem \
SWML_DOMAIN=yourdomain.com \
python tutorial/sales_agent.py
```

### Self-Signed Certificates (Development Only)

For testing, you can create a self-signed certificate:

```bash
# Generate a self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Run with the self-signed cert
SWML_SSL_ENABLED=true \
SWML_SSL_CERT_PATH=cert.pem \
SWML_SSL_KEY_PATH=key.pem \
python tutorial/sales_agent.py
```

**Note:** Self-signed certificates will show security warnings. Use proper certificates from a Certificate Authority (CA) for production.

---

## Summary

Congratulations! You've created your first SignalWire agent. You've learned:

**Key Concepts:**

- ✅ How to create an agent by inheriting from `AgentBase`
- ✅ Using the Prompt Object Model (POM) to structure agent behavior
- ✅ Configuring voice and language settings
- ✅ Running agents locally and with SSL/HTTPS
- ✅ Testing agents with curl and swaig-test

**What's Next?**

In the next lesson, you'll learn how to make Morgan smarter by adding a searchable knowledge base. This will allow the agent to look up product information, pricing, and technical specifications in real-time.

### Practice Exercises

Before moving on, try these exercises:

1. **Change Morgan's Voice**: Try different voices like `rime.spore` or `rime.cove`
2. **Modify the Personality**: Make Morgan more formal or casual
3. **Add New Sections**: Add a section about return policies or warranties
4. **Change the Port**: Run the agent on port 3001 instead of 3000

### Troubleshooting Tips

**Common Issues:**

- **Port in use**: Change the port in the constructor or kill the process using the port
- **Import errors**: Make sure you've installed the SDK with `pip install -e .`
- **SSL errors**: Check that your certificate and key paths are correct

---

[← Back to Tutorial Overview](README.md) | [Next: Lesson 2 - Adding Intelligence with Knowledge Bases →](lesson2_knowledge_bases.md)
