# Lesson 1: Introduction to SignalWire Agents

Before writing Fred, it helps to know what a SignalWire agent is and how a call reaches it. This lesson covers the platform, the SDK's building blocks, and the concepts the rest of the tutorial uses.

## Table of Contents

1. [What Is SignalWire?](#what-is-signalwire)
2. [Understanding AI Agents](#understanding-ai-agents)
3. [The SDK Architecture](#the-sdk-architecture)
4. [What You're Building](#what-youre-building)
5. [Key Concepts](#key-concepts)
6. [Why This Architecture?](#why-this-architecture)

---

## What Is SignalWire?

SignalWire is a communications platform for building voice, video and messaging applications. It carries the phone call and runs the AI conversation, and your agent tells it what to do. The platform provides:

- Voice calling
- Real-time communication
- AI integration
- Scalable infrastructure

## Understanding AI Agents

In the SignalWire SDK, an AI agent is a Python web application that does four things:

1. **Answers HTTP requests** from SignalWire when a call arrives
2. **Returns a SWML document** (SignalWire Markup Language) that describes the agent's behavior
3. **Lets the platform run the conversation**, turning speech into text and the model's replies into speech
4. **Runs functions** when the model asks for them during the call

The request flow looks like this:

```
Caller → SignalWire platform → Your agent → SWML response → AI conversation
```

## The SDK Architecture

Every agent is a Python class that inherits from `AgentBase`:

```python
from signalwire import AgentBase

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="My Agent", route="/agent")
```

The SDK has four core components:

1. **`AgentBase`**: the class every agent inherits from
2. **Skills**: ready-made capabilities you add with one line
3. **SWAIG functions**: tools the model can call during a conversation
4. **Prompt Object Model (POM)**: a structured way to write the agent's prompt

## What You're Building

Fred is a voice assistant that answers questions from Wikipedia. Building it covers four techniques:

- **Persona design**: giving the agent a consistent voice and manner
- **Skill integration**: adding the Wikipedia search skill
- **Custom functions**: writing a tool of your own
- **Voice configuration**: choosing a voice and speech settings

By the end of the tutorial, Fred can:

1. **Search Wikipedia** for a topic
2. **Share facts** about Wikipedia itself
3. **Hold a conversation** about what it finds
4. **Answer voice calls** through SignalWire

## Key Concepts

The rest of the tutorial relies on five concepts.

### 1. SWML (SignalWire Markup Language)

SWML is a JSON document that tells SignalWire how your agent behaves. It includes:

- The prompt: the agent's persona and instructions
- The functions the model can call
- Voice and language settings
- Conversation parameters

### 2. SWAIG (SignalWire AI Gateway)

SWAIG lets your agent run functions during a conversation. When a caller asks Fred about a topic, the model calls Fred's search function through SWAIG, and your code returns the result.

### 3. Skills

Skills are ready-made modules that add a capability to an agent. Instead of writing Wikipedia search yourself, you add the existing skill:

```python
agent.add_skill("wikipedia_search")
```

### 4. HTTP Endpoints

Your agent exposes HTTP endpoints that SignalWire calls:

- `/agent` returns the SWML document. SignalWire requests it with a `POST`, and you can fetch it with `GET` to inspect it.
- `POST /agent/swaig/` runs a function

### 5. Authentication

Agents protect their endpoints with HTTP Basic authentication. The SDK takes the credentials from environment variables, or generates random ones at startup.

## Why This Architecture?

Keeping the call on the platform and the logic in your code has four benefits:

1. **Separation of concerns**: your code handles logic, and the platform handles telephony
2. **Scalability**: the platform runs many calls at once against the same agent
3. **Flexibility**: a new capability is a skill or a function, not a rewrite
4. **Testing**: you can test an agent locally, without a phone line

## Review Questions

1. What is the purpose of SWML?
2. How do skills extend an agent?
3. Which two HTTP endpoints does an agent expose?

**Answers:**

1. SWML tells SignalWire how the agent behaves during a call: its prompt, functions and voice settings.
2. Skills add ready-made, tested capabilities with one line of code.
3. The agent's route, which returns SWML, and `/swaig`, which runs functions.

## Next Steps

With the concepts in place, the next step is installing the SDK. Continue with [Lesson 2: Setting Up Your Environment](02-setup.md).

---

[Overview](README.md) | [Next: Environment Setup](02-setup.md)
