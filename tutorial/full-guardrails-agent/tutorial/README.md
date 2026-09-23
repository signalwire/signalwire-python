# Full-Guardrails Agent Tutorial: Building Penny, a Reservation Line That Keeps Its Rules

The [Fred tutorial](../../fred/tutorial/README.md) gave an agent a personality and a skill. This tutorial builds an agent whose actions have consequences, such as booking tables and cancelling reservations. It keeps that agent correct when the model misunderstands, when a caller pushes, and when a tool fires twice.

## What You'll Build

Penny answers the phone for **The Copper Pot**, a neighborhood restaurant. Callers can use Penny to:

- Book a table and hear a confirmation code
- Look up and cancel an existing reservation, after proving it's theirs
- Ask questions about the restaurant
- Reach a person, or leave a message when nobody is at the host stand
- Get the confirmation by text at the number they called from

What sets Penny apart from Fred is what the model **doesn't** know. It never sees the reservation book, the house rules, other guests' reservations or table numbers. At any moment it has one small task and a few tools, and code does everything that matters.

## The Idea in One Sentence

Program what the model can see and ask for at each moment, and keep what actually happens in code. SignalWire calls this **Programmatically Governed Inference** (PGI).

## Lessons

Each lesson builds on the one before it, so work through them in order:

1. [Why Guardrails](01-why-guardrails.md): the obvious way to build this agent, how it fails, and the idea that fixes it
2. [Design Before Code](02-design-first.md): what must always be true, who enforces it, and what the model sees at each step
3. [The Rules First](03-rules-first.md): the reservation book, with every business rule tested and no agent involved
4. [The Agent Shell](04-the-shell.md): secrets that fail closed, a greeting the model can't skip, and a small prompt
5. [Steps and Scoping](05-steps-and-scoping.md): contexts and steps where every step names its tools, and only code moves the conversation
6. [Tools That Decide](06-tools-that-decide.md): handlers that check the real state, then report to the model and the platform
7. [Gather Mode and Projection](07-gather-and-projection.md): questions asked one at a time, and only the facts each step needs
8. [The Verification Gate](08-the-verification-gate.md): nothing about a reservation is reachable until the caller proves it's theirs
9. [People, Messages and Endings](09-people-and-endings.md): transfers, messages, texts and goodbyes that code carries out
10. [Testing and Running](10-testing-and-running.md): tests that prove the guardrails hold, attack scenarios, and running Penny

The appendices are for reference:

- [Appendix A: Complete Code](appendix-complete-code.md): every file, in full
- [Appendix B: Deployment](appendix-deployment.md): settings, secrets, Docker and a checklist for going live
- [Appendix C: Technique Map](appendix-technique-map.md): every technique, where Penny uses it, and the lesson that teaches it

## Prerequisites

You need:

- Python 3.10 or later
- The [Fred tutorial](../../fred/tutorial/README.md), or working knowledge of `AgentBase`, prompt sections and tools

The lessons take about two hours in total, 10 to 15 minutes each.

## The Files

Penny is four Python modules. The rest of the directory tests them, checks these lessons, and runs Penny:

```
full-guardrails-agent/
├── reservations.py   the rules and the records (no SignalWire import)
├── workflow.py       what the model sees and may do, step by step
├── handlers.py       what each tool does, and what it tells the model and the platform
├── penny.py          the agent, which wires the other three together
├── test_penny.py     tests for all of the above, including these lessons
├── check_docs.py     proves the code in these lessons is the real code
├── penny.sh          start, stop, status, logs, test
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
└── tutorial/         the lessons
```

Code blocks that quote a file are checked against that file by `check_docs.py`, which runs with the tests. If the code changes and a lesson doesn't, a test fails.

## Quick Start

Install the requirements and run the tests from the tutorial directory:

```bash
cd tutorial/full-guardrails-agent
pip install -r requirements.txt
python -m unittest test_penny
```

## What Is and Isn't Verified

The tutorial separates what its tests prove from what still needs a real call:

- **Verified by the tests:** the business rules, the SWML the agent serves (tools and navigation for every step), and what every tool returns to the model and the platform, including under attack
- **Verified in a real conversation:** a booking from first question to confirmation code, run through SignalWire's AI service with a live model ([Lesson 10](10-testing-and-running.md))
- **Not verified here:** speech on a real phone line, including barge-in and timing, and a live transfer or text. Test those on your own number before going live.

## Getting Help

These resources cover the SDK features the lessons use:

- **SDK documentation:** the [docs](../../../docs/) folder in this repository, especially the [contexts guide](../../../docs/contexts_guide.md) and the [SWAIG reference](../../../docs/swaig_reference.md)
- **GitHub Issues:** [github.com/signalwire/signalwire-python](https://github.com/signalwire/signalwire-python)

Start with [Lesson 1: Why Guardrails](01-why-guardrails.md).

---

*This tutorial was created for SignalWire SDK v3.4.4*
