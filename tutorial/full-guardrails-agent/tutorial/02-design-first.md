# Lesson 2: Design Before Code

A guardrailed agent is designed from the rules outward, not from the prompt inward. In this lesson you'll write down what must always be true, decide who enforces each rule, and map exactly what the model sees at every step. You won't write any Python yet.

## Table of Contents

1. [Start With What Must Stay True](#start-with-what-must-stay-true)
2. [Four Kinds of State](#four-kinds-of-state)
3. [The Workflow Contract](#the-workflow-contract)
4. [What the Model Sees, Step by Step](#what-the-model-sees-step-by-step)
5. [Two Rules for Every Step](#two-rules-for-every-step)

---

## Start With What Must Stay True

List the things that must hold even if the model misunderstands everything. Then give each one an owner that isn't the prompt:

| Must always be true | Enforced by |
|---|---|
| Only seatings that exist and are free get booked | The reservation book chooses tables. The model only sees option numbers. |
| A booking happens once, and only for the proposal the caller heard | Confirming needs the proposal's revision number. The database allows one booking per hold. |
| Nobody learns or changes a reservation they can't prove is theirs | Every lookup and cancel re-checks a verification recorded for this call |
| Parties over six aren't booked by phone | The reservation book refuses, and the caller is offered a person |
| The AI disclosure is always heard | The platform speaks a fixed greeting before the model says a word |
| Transfers go only to the restaurant's number, and only when someone is there | The number comes from server config, and code checks the host stand's hours |
| Texts go only to the number that called | The destination comes from the call, never from the model |
| A failure never sounds like success | Every handler turns an unexpected error into "the outcome is unknown" |

The right-hand column never says "the prompt tells the model to". Each rule is enforced where the model can't reach it.

## Four Kinds of State

A voice agent handles four kinds of state, and confusing them causes many bugs:

| Kind | In Penny | Treat it as |
|---|---|---|
| **What the model sees** | Step instructions, tool results | Curated, step by step |
| **Session data** (`global_data`) | The booking summary, the spoken confirmation code, the answers gathered from the caller | A projection for the prompt. Gathered answers are still caller input. |
| **The system of record** | The SQLite reservation book: reservations, holds, per-call sessions | The truth |
| **Call identifiers** | `call_id` | Links requests from the same call. It isn't proof of who is calling. |

The platform sends `global_data` with each tool request as a snapshot taken at the start of the model's turn. If the model calls two tools in one turn, both get the same snapshot. If both write it back, the second silently overwrites the first. So Penny keeps the truth in the reservation book, keyed by `call_id`, and uses `global_data` only to show the model small, finished facts.

## The Workflow Contract

Before writing steps, write the contract they'll implement. This is a design document, not configuration:

```yaml
outcome: book or cancel a table without breaking a house rule
contexts:
  default:                       # where every call starts
    triage:       {tools: [start_booking, manage_booking, house_info, request_human, finish]}
  booking:
    collect:      {gather: [party_size, date, time, name], then: search}
    search:       {tools: [find_tables], leaves_by: find_tables}
    choose:       {tools: [hold_table, find_tables], leaves_by: hold_table}
    review:       {tools: [confirm_booking, find_tables], leaves_by: confirm_booking}
    booked:       {tools: [send_confirmation_text, finish]}
  manage:
    verify:       {tools: [verify_reservation], leaves_by: "verify_reservation (match) or 3 misses"}
    details:      {tools: [request_cancel, finish], history: hide}
    confirm_cancel: {tools: [confirm_cancel, keep_reservation]}
    cancelled:    {tools: [finish]}
    locked:       {tools: [request_human, finish]}
  help:
    take_message: {gather: [name, callback, body], then: save_message}
    save_message: {tools: [save_message], leaves_by: save_message}
    message_saved: {tools: [finish]}
everywhere_useful: [house_info, request_human]   # read-only, or hands off to a person
model_navigation: none   # every move between steps is made by a tool handler
```

Here is the same contract as a diagram:

```
default/triage ─start_booking──► booking/collect ─(gather done)─► search ─find_tables─► choose
                                                                              │
                                        booked ◄─confirm_booking─ review ◄─hold_table
                                          │
                                        finish ─► goodbye, hang up

default/triage ─manage_booking─► manage/verify ─match─► details ─request_cancel─► confirm_cancel
                                        │                                              │
                                   3 misses ─► locked                 confirm_cancel ─► cancelled

most steps ─request_human─► someone at the host stand? ─yes─► announce, then transfer
                                                       └no──► help/take_message ─► save_message ─► message_saved
```

## What the Model Sees, Step by Step

Lessons 5 through 9 build this table. For each step, it lists the only instructions and tools the model has:

| Step | The model's whole task | Its tools | How the step ends |
|---|---|---|---|
| triage | Route the caller as soon as they say what they want | start_booking, manage_booking, house_info, request_human, finish | A router tool changes context |
| collect | Ask party size, date, time and name, one at a time | only gather's submit, plus house_info and request_human per question | Gather finishes and moves to search |
| search | Call find_tables now | find_tables, house_info, request_human | find_tables moves to choose |
| choose | Offer the numbered options, hold the one picked | hold_table, find_tables, house_info, request_human | hold_table moves to review |
| review | Read the proposal back, confirm on a clear yes | confirm_booking, find_tables, house_info, request_human | confirm_booking moves to booked |
| booked | Give the code, offer a text | send_confirmation_text, house_info, finish | finish hangs up |
| verify | Get the code and last name | verify_reservation, house_info, request_human | A match moves to details. Three misses lock. |
| details | Describe the verified reservation | request_cancel, house_info, request_human, finish | request_cancel moves to confirm_cancel |
| confirm_cancel | Read back the cancellation, cancel on a clear yes | confirm_cancel, keep_reservation, house_info, request_human | Either tool moves on |
| cancelled | Wrap up | house_info, finish | finish |
| locked | Offer a person | request_human, finish | Either tool |
| take_message | Ask name, callback number and message | only gather's submit, plus finish | Gather moves to save_message |
| save_message | Save it | save_message | save_message moves to message_saved |
| message_saved | Wrap up | house_info, finish | finish |

Look down the tools column. `confirm_booking` exists in exactly one step, the one where a proposal has been read back. `confirm_cancel` exists only after a cancellation was staged. No step lets the model skip straight to booking or cancelling.

## Two Rules for Every Step

Two rules apply to every step, and Lesson 5 enforces them in code so no step can forget:

1. **Every step names its tools.** A step that doesn't name any silently inherits the previous step's tools. "No tools" must be written as an empty list, never left out.
2. **The model can't navigate.** The model is given no step or context it may jump to. The only way to the next step is a tool handler that has checked the real state and moved the conversation itself.

## Key Takeaways

- Write the invariants first, and give each one an owner that isn't the prompt
- Keep the truth in a system of record. Treat `global_data` as a projection.
- The per-step table is your real prompt engineering: what the model sees is what it can do

## Review Questions

1. Why is `global_data` a poor place to keep the truth about a booking?
2. Which single step is allowed to confirm a booking, and what must have happened before it?
3. What would go wrong if the `search` step left out its tool list?

## Next Steps

With the design settled, build the part everything else depends on: the rules. Continue with [Lesson 3: The Rules First](03-rules-first.md).

---

[Previous: Why Guardrails](01-why-guardrails.md) | [Overview](README.md) | [Next: The Rules First](03-rules-first.md)
