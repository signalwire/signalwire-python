# Full-Guardrails Agent Tutorial - Building Penny, a Reservation Line That Keeps Its Rules

In the [Fred tutorial](../../fred/tutorial/README.md) you gave an agent a personality and a skill. This tutorial builds an agent whose actions have consequences — booking tables and cancelling reservations — and keeps it correct when the model misunderstands, when a caller pushes, and when a tool fires twice.

## What You'll Build

Penny answers the phone at **The Copper Pot**, a neighborhood restaurant. She can:

- Book a table and read back a confirmation code
- Look up and cancel an existing reservation, but only after the caller proves it's theirs
- Answer questions about the restaurant
- Connect the caller with a person, or take a message when nobody is at the host stand
- Text the confirmation to the number that called

What makes Penny different from Fred is what she **doesn't** know. The model never sees the reservation book, the house rules, other guests' reservations or table numbers. At any moment it has one small task and a handful of tools. Code does everything that matters.

## The Idea in One Sentence

Program what the model can see and ask for at each moment, and keep what actually happens in code. SignalWire calls this **Programmatically Governed Inference** (PGI).

## Tutorial Structure

### 🧭 [Lesson 1: Why Guardrails](01-why-guardrails.md)
The obvious way to build this agent, the ways it fails, and the idea that fixes them.

### 📐 [Lesson 2: Design Before Code](02-design-first.md)
Decide what must always be true, who enforces it, and what the model sees at each step.

### 📒 [Lesson 3: The Rules First](03-rules-first.md)
Build the reservation book: every business rule, tested, with no agent in sight.

### 🏗️ [Lesson 4: The Agent Shell](04-the-shell.md)
Secrets that fail closed, a greeting the model can't skip, and a deliberately small prompt.

### 🪜 [Lesson 5: Steps and Scoping](05-steps-and-scoping.md)
Contexts and steps where every step names its tools and only code can move the conversation.

### 🛠️ [Lesson 6: Tools That Decide](06-tools-that-decide.md)
Handlers that check the real state, then tell the model and the platform what happened.

### 📝 [Lesson 7: Gather Mode and Projection](07-gather-and-projection.md)
Collect details one question at a time, and show the model only the facts each step needs.

### 🔐 [Lesson 8: The Verification Gate](08-the-verification-gate.md)
Nothing about a reservation is reachable until the caller proves it's theirs.

### 📞 [Lesson 9: People, Messages and Endings](09-people-and-endings.md)
Transfers, messages, texts and goodbyes that happen because code did them, not because the model said so.

### ✅ [Lesson 10: Testing and Running](10-testing-and-running.md)
Tests that prove the guardrails bite, adversarial scenarios, and running Penny for real.

### 📚 Appendices
- [Appendix A: Complete Code](appendix-complete-code.md)
- [Appendix B: Deployment](appendix-deployment.md)
- [Appendix C: Technique Map](appendix-technique-map.md), every technique and where Penny uses it

## Prerequisites

**Required:**
- Python 3.10 or higher
- The [Fred tutorial](../../fred/tutorial/README.md), or equivalent comfort with `AgentBase`, prompt sections and tools

**Time:** about two hours, 10-15 minutes per lesson

## The Files

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
└── tutorial/         you are here
```

Every code block in these lessons that is marked with a `source` comment is checked against the real files by `check_docs.py`, which runs as part of the tests. The lessons can't drift from the code without a test failing.

## Quick Start

```bash
cd tutorial/full-guardrails-agent
pip install -r requirements.txt
python -m unittest test_penny
```

## What Is and Isn't Verified

- **Verified by the tests:** the business rules, the SWML the agent serves (tools and navigation for every step), and what every tool returns to the model and the platform, including under attack
- **Verified in a real conversation:** a booking from first question to confirmation code, run through SignalWire's AI service with a live model (see [Lesson 10](10-testing-and-running.md))
- **Not verified here:** speech on a real phone line, including barge-in and timing, and a live transfer or text. Test those on your own number before going live.

## Getting Help

- **SDK documentation:** the [docs](../../../docs/) folder in this repository, especially the [contexts guide](../../../docs/contexts_guide.md) and the [SWAIG reference](../../../docs/swaig_reference.md)
- **GitHub Issues:** [github.com/signalwire/signalwire-python](https://github.com/signalwire/signalwire-python)

Ready? Start with [Lesson 1: Why Guardrails](01-why-guardrails.md).

---

*This tutorial was created for SignalWire SDK v3.4.4*
