# Fred Bot Tutorial: Building a Wikipedia AI Assistant

This tutorial builds Fred, a voice agent that answers questions from Wikipedia, using the SignalWire SDK. Each lesson adds one part of the agent, and by the end you run Fred locally and test it from the command line.

## What You'll Build

Fred is an AI voice agent with a friendly persona. It can:

- Search Wikipedia for information on a topic
- Share facts about Wikipedia itself
- Hold a conversation about what it finds
- Answer voice calls through the SignalWire platform

## Lessons

Each lesson builds on the one before it, so work through them in order:

1. [Introduction to SignalWire Agents](01-introduction.md): the SDK's core concepts and how an agent handles a call
2. [Setting Up Your Environment](02-setup.md): install the SDK and check that it works
3. [Creating Fred's Basic Structure](03-basic-agent.md): the agent class, its prompt, and its voice
4. [Adding the Wikipedia Search Skill](04-wikipedia-skill.md): add Wikipedia search with the skills system
5. [Creating Custom Functions](05-custom-functions.md): write a SWAIG function that shares facts about Wikipedia
6. [Running and Testing Fred](06-running-testing.md): run Fred, and test it with `swaig-test` and `curl`

The appendices are for reference:

- [Appendix A: Complete Code and Management Script](appendix-complete-code.md): `fred.py`, `fred.sh` and a quick start
- [Appendix B: Docker Deployment](appendix-docker-deployment.md): run Fred in a container

## Prerequisites

You need:

- Python 3.10 or later
- Basic Python knowledge
- Familiarity with the command line

Knowing how REST APIs or telephony applications work helps, but isn't required.

The tutorial takes 45 to 60 minutes in total, 5 to 10 minutes per lesson.

## Getting Help

These resources cover the SDK and the platform:

- **SignalWire documentation:** [signalwire.com/docs](https://signalwire.com/docs)
- **SDK documentation:** the [docs](../../../docs/) folder in this repository
- **GitHub Issues:** [github.com/signalwire/signalwire-python](https://github.com/signalwire/signalwire-python)

When you've built Fred, the [Full-Guardrails Agent tutorial](../../full-guardrails-agent/tutorial/README.md) goes further: an agent whose actions have consequences, kept correct by code instead of by the prompt.

Start with [Lesson 1: Introduction to SignalWire Agents](01-introduction.md).

---

*This tutorial was created for SignalWire SDK v3.4.3*
