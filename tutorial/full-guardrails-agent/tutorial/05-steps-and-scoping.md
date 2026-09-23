# Lesson 5: Steps and Scoping

This lesson gives Penny's conversation its shape. `workflow.py` turns the table from Lesson 2 into contexts and steps, and it enforces the two rules every step must follow.

## Table of Contents

1. [Contexts and Steps](#contexts-and-steps)
2. [One Helper for Every Step](#one-helper-for-every-step)
3. [Triage: Where Every Call Starts](#triage-where-every-call-starts)
4. [The Booking Steps](#the-booking-steps)
5. [The Inheritance Trap](#the-inheritance-trap)
6. [Why No Step Criteria, and No `set_end`](#why-no-step-criteria-and-no-set_end)
7. [Checking the Contract](#checking-the-contract)

---

## Contexts and Steps

A **context** is a mode of work: triage, booking, managing a reservation, taking a message. A **step** is the one task that's active inside it. Penny has four contexts:

| Context | Steps | Entered by |
|---|---|---|
| `default` | triage | The start of every call |
| `booking` | collect, search, choose, review, booked | `start_booking` |
| `manage` | verify, details, confirm_cancel, cancelled, locked | `manage_booking` |
| `help` | take_message, save_message, message_saved | `request_human` when nobody is at the host stand |

Tools are registered once, on the agent (you did that in Lesson 4). Each step then decides which of them the model can see while that step is active.

## One Helper for Every Step

Every step goes through this function, so neither rule can be forgotten:

<!-- source: workflow.py#scoped --> <!-- snippet: no-run an excerpt of workflow.py, checked against the file by test_penny.py -->
```python
def scoped(step: Step, text: str, tools: list[str], history: str = "default") -> Step:
    """Give a step its task, its tools, and no way to leave on its own."""
    return (step.set_text(text)
            .set_functions(tools)
            .set_valid_steps([])
            .set_valid_contexts([])
            .set_history(history))
```

Besides the step's text, the helper sets three things on every step:

- `set_functions(tools)` names the step's tools, and `[]` means none
- `set_valid_steps([])` and `set_valid_contexts([])` give the model nowhere to go. The only way out of a step is a tool handler returning `swml_change_step` or `swml_change_context` after it has checked the real state.
- `set_history` chooses how much of the earlier conversation the model still sees. Lesson 7 explains the options.

## Triage: Where Every Call Starts

Every call starts in the `default` context, whose only step is `triage`:

<!-- source: workflow.py#triage --> <!-- snippet: no-run an excerpt of workflow.py, checked against the file by test_penny.py -->
```python
def _triage(builder: ContextBuilder) -> None:
    ctx = builder.add_context("default")
    scoped(ctx.add_step("triage"),
           "The greeting has already been played; don't repeat it. The host stand is "
           "${global_data.host_stand} right now. As soon as the caller says what they want, "
           "act on it without asking again: for a new reservation call start_booking; to "
           "check, change or cancel one they already have, call manage_booking. Answer "
           "general questions with house_info. If they ask for a person, call "
           "request_human. If they're done, call finish.",
           ["start_booking", "manage_booking", *LOOKUPS, "finish"])
    ctx.set_initial_step("triage")
```

`start_booking` and `manage_booking` are **router tools**. They don't book or cancel anything. They move the conversation, and because they're tools, code performs the move and can reset state on the way (Lesson 6). The model can't drift into the manage context on its own.

`${global_data.host_stand}` is filled in by the platform when the step runs. Lesson 7 shows where the value comes from.

> **A wording fix from a live test.** The first version of this text told the model to find out whether the caller wanted a new reservation or an existing one. In a live test, a caller opened with "I'd like to book a table", and Penny still asked "new or existing?". The wording now says to act as soon as the caller has said what they want.
>
> PGI doesn't make prompt wording irrelevant. It makes wording low-stakes. A clumsy instruction here costs one extra question. It can't book the wrong table, because triage has no tool that books anything.

## The Booking Steps

The `collect` step uses gather mode, which is the next lesson. Here is the chain after it:

<!-- source: workflow.py#booking-steps --> <!-- snippet: no-run an excerpt of workflow.py, checked against the file by test_penny.py -->
```python
scoped(ctx.add_step("search"),
       "The details are collected. Call find_tables now. Say nothing about "
       "availability until it returns. If the caller changes a detail, pass only "
       "that detail to find_tables.",
       ["find_tables", *LOOKUPS])
scoped(ctx.add_step("choose"),
       "Offer the options from the last find_tables result by number, and nothing "
       "else. When the caller picks one, call hold_table with its number. If they "
       "want a different time, date or party size, call find_tables with only what "
       "changed.",
       ["hold_table", "find_tables", *LOOKUPS])
scoped(ctx.add_step("review"),
       "A table is on hold. Read the proposal back as the last tool result gave it "
       "and ask the caller to confirm. Only if they clearly say yes, call "
       "confirm_booking with the proposal's revision number. If they want a change, "
       "call find_tables with only what changed.",
       ["confirm_booking", "find_tables", *LOOKUPS])
scoped(ctx.add_step("booked"),
       "The reservation is confirmed: ${global_data.booking.summary}. The "
       "confirmation code is ${global_data.booking.code_spoken}. Make sure the caller "
       "has the code, offer to text the details with send_confirmation_text, and "
       "answer last questions with house_info. When they're done, call finish.",
       ["send_confirmation_text", "house_info", "finish"])
ctx.set_initial_step("collect")
```

Read the tools on each step against the design table from Lesson 2:

- `search` can only look up availability. It can't hold anything.
- `choose` can hold one of the options the search offered.
- `review` is the **only** step with `confirm_booking`, and it's only reached after `hold_table` has created a proposal.
- `booked` has no booking tools at all, so a confused model can't book twice.

Every step has at most five tools. The model chooses more reliably from a short, specific list.

`set_initial_step("collect")` names the entry step. The step is also listed first, and each context is built the same way, so the entry point is unambiguous however the context is entered.

## The Inheritance Trap

Tool inheritance is a common bug in multi-step agents, so it gets its own test:

<!-- source: test_penny.py#test-trap --> <!-- snippet: no-run an excerpt of test_penny.py, checked against the file by test_penny.py -->
```python
def test_leaving_out_tools_is_not_the_same_as_no_tools(self) -> None:
    self.assertNotIn("functions", Step("omitted").set_text("Ask.").to_dict())
    self.assertEqual(Step("empty").set_text("Ask.").set_functions([]).to_dict()["functions"], [])
```

A step with no `functions` key doesn't mean "no tools". It means "keep whatever the last step had". If `booked` left out its list, the model could still call `confirm_booking` from `review`. The `scoped` helper makes the mistake impossible: every step gets an explicit list, even when it's `[]`.

## Why No Step Criteria, and No `set_end`

Penny deliberately doesn't use two methods from the contexts API:

- **`set_step_criteria`** tells the model when a step is done, so the model can decide to move on. Penny's model never decides to move on. Code moves it, after checking. Criteria would be guidance on a decision the model doesn't make.
- **`set_end(True)`** leaves step mode after the step. It does **not** hang up. It would leave the model outside step mode, with no step limiting its tools, which is the opposite of a locked-down ending. Penny's final steps keep explicit, short tool lists, and `finish` hangs up with a real action (Lesson 9).

## Checking the Contract

The tests fetch the SWML from the app Penny serves, the way SignalWire fetches it. They check the design there, rather than in the Python that built it:

<!-- source: test_penny.py#test-scoping --> <!-- snippet: no-run an excerpt of test_penny.py, checked against the file by test_penny.py -->
```python
def test_every_step_names_its_tools_and_cannot_navigate(self) -> None:
    for where, step in self.steps.items():
        with self.subTest(step=where):
            self.assertIn("functions", step)  # omitted would inherit the last step's tools
            self.assertEqual(step["valid_steps"], [])
            self.assertEqual(step["valid_contexts"], [])
            self.assertNotIn("end", step)

def test_every_tool_a_step_names_is_registered(self) -> None:
    registered = {f["function"] for f in self.ai["SWAIG"]["functions"]}
    for where, step in self.steps.items():
        gathered = [f for q in step.get("gather_info", {}).get("questions", [])
                    for f in q.get("functions", [])]
        for tool in step["functions"] + gathered:
            with self.subTest(step=where, tool=tool):
                self.assertIn(tool, registered)

def test_consequential_tools_live_in_exactly_one_step(self) -> None:
    homes = {"hold_table": "booking/choose", "confirm_booking": "booking/review",
             "send_confirmation_text": "booking/booked",
             "verify_reservation": "manage/verify", "request_cancel": "manage/details",
             "confirm_cancel": "manage/confirm_cancel", "save_message": "help/save_message"}
    for tool, home in homes.items():
        with self.subTest(tool=tool):
            self.assertEqual([w for w, s in self.steps.items() if tool in s["functions"]], [home])
```

The second test is the tool-scoping contract in one line per tool: each consequential tool lives in exactly one step. Add `confirm_booking` to `choose` by mistake and this test fails.

You can look at the rendered steps yourself:

```bash
swaig-test penny.py --agent-class Penny --dump-swml
```

Find the `contexts` section inside the `ai` verb. Every step has a `functions` list and empty `valid_steps` and `valid_contexts`.

## Key Takeaways

- Register tools once, then expose a few per step
- Give the model nowhere to navigate. Tool handlers move the conversation after checking.
- An omitted tool list inherits the last one. Write `[]`, and let a helper enforce it.
- Test the SWML the agent serves, not the builder code

## Review Questions

1. What would the model be able to do if the `booked` step had no `functions` key?
2. Why are `start_booking` and `manage_booking` tools instead of allowed context changes?
3. What's the difference between `set_end(True)` and hanging up?

## Next Steps

The steps decide what the model can ask for. Next, write the handlers that decide what actually happens. Continue with [Lesson 6: Tools That Decide](06-tools-that-decide.md).

---

[Previous: The Agent Shell](04-the-shell.md) | [Overview](README.md) | [Next: Tools That Decide](06-tools-that-decide.md)
