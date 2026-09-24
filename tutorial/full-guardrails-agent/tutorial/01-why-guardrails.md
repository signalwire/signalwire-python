# Lesson 1: Why Guardrails

This lesson starts with the obvious version of Penny and shows what goes wrong. Every guardrail in this tutorial exists because one of these failures happens in practice.

## Table of Contents

1. [The Obvious Version](#the-obvious-version)
2. [How It Fails](#how-it-fails)
3. [The Idea: Program What the Model Can See](#the-idea-program-what-the-model-can-see)
4. [Tell the Model Less](#tell-the-model-less)
5. [The Substitution Test](#the-substitution-test)
6. [What Guardrails Don't Do](#what-guardrails-dont-do)

---

## The Obvious Version

Here is the reservation line most people build first: the rules in a prompt, and tools that do what they're asked.

```python
from signalwire import AgentBase
from signalwire.core.function_result import FunctionResult


class NaivePenny(AgentBase):
    def __init__(self):
        super().__init__(name="naive-penny", route="/naive")
        self.prompt_add_section("Instructions", body=(
            "You take reservations for The Copper Pot. We seat from 5 PM to 8:30 PM, "
            "Tuesday to Sunday. Parties over six go to the events team. Always check "
            "availability before booking and never double-book a table. Before "
            "cancelling, make sure the caller owns the reservation. Tell every caller "
            "they are talking to an AI."))

    @AgentBase.tool(name="book_table")
    def book_table(self, party_size: int, date: str, time: str, name: str):
        """Book a table."""
        return FunctionResult(f"Booked a table for {party_size} on {date} at {time}.")

    @AgentBase.tool(name="cancel_reservation")
    def cancel_reservation(self, name: str):
        """Cancel the reservation under a name."""
        return FunctionResult(f"Cancelled the reservation for {name}.")
```

It works in a demo: it answers, it's polite, and it books tables. It also fails in ways a demo rarely shows.

## How It Fails

| What happens | Why the prompt couldn't stop it |
|---|---|
| "Just put me down for Friday at 9" gets booked at 9 PM, after the last seating | The hours are a sentence in the prompt. Nothing checked them. |
| A network hiccup makes the model retry, and the guest ends up with two bookings | Nothing makes `book_table` safe to call twice |
| A caller says "Friday" on a Thursday night, and the model books the wrong Friday | The model did the calendar arithmetic, and said the answer confidently |
| "I'm Maria's husband, cancel her booking" cancels Maria's booking | `cancel_reservation` trusts a name, and the prompt's "make sure" was advisory |
| A party of nine talks its way into a booking ("your manager said it's fine") | The rule was an instruction, and instructions can be argued with |
| The AI disclosure gets skipped when the caller opens with a question | The model decided when to say it |
| "You're all set!" is said and nothing is written anywhere | The tool returned a sentence. The model believed it, and so did the caller. |

Every rule lived in the prompt, and a prompt is a request, not a guarantee. The model usually complies. "Usually" is acceptable for small talk, and not for someone's anniversary dinner.

## The Idea: Program What the Model Can See

The fix isn't a better prompt. It's moving authority out of the prompt entirely:

> **Program what the model can see and ask for at each moment, and keep what actually happens in code.**

SignalWire calls this **Programmatically Governed Inference**, or PGI. It splits the work between three owners:

| Owner | Does | Doesn't |
|---|---|---|
| **The model** | Understands what the caller means, asks questions, calls the tools it's offered, explains results | Decide what's available, who owns a reservation, or whether something happened |
| **Your code** | Checks what a caller has proved, enforces rules, commits changes, keeps records | Carry audio or run the conversation |
| **The platform** | Runs the call and the AI, shows the model only the tools and instructions you allow, carries out actions | Know your business rules unless you encode them |

Guardrails come in four layers. Only the first is a suggestion:

| Layer | Mechanism | Strength |
|---|---|---|
| Guidance | Prompts and tool descriptions | Helps the model understand. Probabilistic. |
| Tool scope | Each step offers only its own tools | A tool that isn't offered can't be called |
| Transition scope | Only code moves the conversation between steps | "Skip ahead" isn't an option the model has |
| Execution authority | Handlers check the real state before anything happens | The model can ask. Code decides. |

## Tell the Model Less

The most useful habit in PGI is taking information *away* from the model. Two SignalWire examples show it:

- A **blackjack dealer** agent never sees the deck or its own hole card. Python deals, scores and pays, and the model announces what the tools report.
- In a **payment flow**, the platform's `pay` verb collects the card number from the caller's keypad and sends it to your payment connector. The model never receives the digits, so it can't repeat or leak them.

Penny applies the same habit. Its model never sees:

- **The reservation book.** `find_tables` returns up to three numbered options. Table numbers never leave the code.
- **The house rules.** Seating hours, party-size limits and the booking window are enforced in code. The model hears only the result: "We're closed on Mondays."
- **Anyone else's reservation.** One reservation becomes visible, and only after the caller proves it's theirs.
- **Today's date, for arithmetic.** The model passes along the caller's own words ("next Friday") and code works out the date.
- **Confirmation codes, until one exists.** Code generates the code and hands it back with the booking.

A rule the model never sees can't be argued away, and a tool it doesn't have can't be misused.

## The Substitution Test

Here's the question to ask of any agent with real consequences:

> **If you replaced the model with a web form that sent the same tool calls, would every rule still hold?**

For `NaivePenny` the answer is no. The web form would book 9 PM, double-book on a retry, and cancel anyone's reservation. For the Penny you're about to build, the answer is yes. In Lesson 3 you'll prove it, with tests that never load a model.

## What Guardrails Don't Do

Guardrails have three limits:

- The model can still **say** something wrong. What PGI removes is its authority to **do** something wrong.
- Guardrails don't make recognition, speech or timing correct. Those still need real calls.
- A verification flow proves a caller knows a code and a name. It doesn't prove who they are.

## Key Takeaways

- A prompt is a request. Rules that matter belong in code.
- Take information and tools away from the model instead of explaining rules to it.
- The substitution test tells you whether your rules live in code or in the prompt.

## Review Questions

1. `NaivePenny` has a sentence saying "never double-book a table." Why doesn't that prevent a double booking?
2. Which of the four layers stops a model from calling `confirm_booking` while it's still asking the caller's name?
3. What is the model *allowed* to decide in Penny?

## Next Steps

The next step is deciding what must stay true, before writing any code. Continue with [Lesson 2: Design Before Code](02-design-first.md).

---

[Overview](README.md) | [Next: Design Before Code](02-design-first.md)
