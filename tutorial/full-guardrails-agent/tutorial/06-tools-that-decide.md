# Lesson 6: Tools That Decide

The steps decide what the model can ask for. The handlers in `handlers.py` decide what actually happens. Each one asks the reservation book to do something, then reports back to two different audiences.

## Table of Contents

1. [Tool Descriptions Are Prompts](#tool-descriptions-are-prompts)
2. [Two Audiences: the Model and the Platform](#two-audiences-the-model-and-the-platform)
3. [A Guard Around Every Handler](#a-guard-around-every-handler)
4. [Router Tools](#router-tools)
5. [Finding, Holding and Confirming](#finding-holding-and-confirming)
6. [The Rules for `global_data`](#the-rules-for-global_data)
7. [Try It: a Booking From the Command Line](#try-it-a-booking-from-the-command-line)

---

## Tool Descriptions Are Prompts

Every tool is registered once, in `_register_tools` in `penny.py`:

<!-- source: penny.py#tools --> <!-- snippet: no-run an excerpt of penny.py, checked against the file by test_penny.py -->
```python
def _register_tools(self, h: PennyHandlers) -> None:
    """Every tool the agent has. Which ones the model sees is decided per step."""
    revision = {"type": "integer", "minimum": 1,
                "description": "The revision number from the proposal the caller agreed to."}
    checking = {"en-US": ["Let me check the book.", "One moment while I look."]}

    self.define_tool("start_booking", "Start taking a new reservation.", {}, h.start_booking)
    self.define_tool("manage_booking",
                     "Start looking up the caller's existing reservation. It does not "
                     "reveal anything until the caller verifies it.", {}, h.manage_booking)
    self.define_tool("house_info", "Look up a fact about the restaurant.",
                     {"topic": {"type": "string", "enum": sorted(HOUSE_FACTS)}},
                     h.house_info, required=["topic"])
    self.define_tool(
        "find_tables",
        "Check which seatings are free, using the details the caller already gave. "
        "Pass only a detail the caller has changed. Holds and books nothing.",
        {"party_size": {"type": "integer", "minimum": 1, "maximum": 20,
                        "description": "Only if the caller changed the party size."},
         "date": {"type": "string", "description": "Only if the caller changed the date, "
                                                   "in their own words, e.g. 'Saturday'."},
         "time": {"type": "string", "description": "Only if the caller changed the time, "
                                                   "e.g. '8:00 PM'."},
         "name": {"type": "string", "description": "Only if the caller changed the name."}},
        h.find_tables, fillers=checking)
    self.define_tool("hold_table",
                     "Hold the option the caller picked for five minutes. Does not book it.",
                     {"option": {"type": "integer", "minimum": 1, "maximum": 3,
                                 "description": "The option number the caller chose."}},
                     h.hold_table, required=["option"])
    self.define_tool("confirm_booking",
                     "Book the table on hold, only after the caller agreed to the proposal "
                     "you read back.", {"revision": revision}, h.confirm_booking,
                     required=["revision"], fillers=checking)
    self.define_tool("send_confirmation_text",
                     "Text the confirmed reservation to the number this call comes from.",
                     {}, h.send_confirmation_text)
    self.define_tool("verify_reservation",
                     "Check a confirmation code and last name. Only a match unlocks the "
                     "reservation.",
                     {"confirmation_code": {"type": "string",
                                            "description": "The six characters the caller read out."},
                      "last_name": {"type": "string", "description": "The caller's last name."}},
                     h.verify_reservation, required=["confirmation_code", "last_name"],
                     fillers=checking)
    self.define_tool("request_cancel",
                     "Prepare to cancel the verified reservation. Cancels nothing yet.",
                     {}, h.request_cancel)
    self.define_tool("confirm_cancel",
                     "Cancel the verified reservation, only after the caller said yes to "
                     "the cancellation you read back.",
                     {"revision": revision}, h.confirm_cancel, required=["revision"])
    self.define_tool("keep_reservation", "Abandon the cancellation and keep the reservation.",
                     {}, h.keep_reservation)
    self.define_tool("request_human",
                     "Connect the caller with a person at the host stand, or take a message "
                     "if nobody is there.", {}, h.request_human)
    self.define_tool(
        "save_message",
        "Save the message just taken for the host stand. Pass a detail only to correct it.",
        {"name": {"type": "string"}, "callback": {"type": "string"},
         "body": {"type": "string"}},
        h.save_message)
    self.define_tool("finish", "Say goodbye and end the call.", {}, h.finish)
```

The platform sends each tool's description and parameters to the model on every turn. That makes them prompt text, and three habits keep them accurate:

- **Say what the tool doesn't do.** `find_tables` "holds and books nothing". `hold_table` "does not book it". `request_cancel` "cancels nothing yet". A model that knows a tool is harmless won't hesitate to use it, and won't mistake it for the final step.
- **Constrain arguments in the schema.** `house_info` takes a `topic` from a fixed `enum`, and `hold_table` takes an option from 1 to 3.
- **Cover the wait with fillers.** `find_tables`, `confirm_booking` and `verify_reservation` have short phrases the platform can say while the handler works, so the caller doesn't hear silence.

A schema limit helps the model ask correctly. It is not a check. Every handler validates its arguments again, because schemas are guidance too.

## Two Audiences: the Model and the Platform

A `FunctionResult` reaches two audiences, the model and the platform, through three parts:

| Part | Audience | Penny uses it for |
|---|---|---|
| `tool_result` | The model | What is true: "On hold for five minutes: a table for 4 on Friday, September 25 at 7:30 PM..." |
| `tool_prompt` | The model | What to do now: "Read the proposal back and ask the caller to confirm it." |
| Actions | The platform | What happens regardless of what the model says: change step, update session data, send UI events, say, transfer, hang up |

Keeping the parts separate matters. If the facts and the instructions share one string, the model may read the instructions aloud, or treat the facts as a suggestion. Actions don't rely on the model at all: when `confirm_booking` returns `swml_change_step("booked")`, the conversation moves whether or not the model mentions it.

## A Guard Around Every Handler

Every handler is wrapped in `guarded`:

<!-- source: handlers.py#guarded --> <!-- snippet: no-run an excerpt of handlers.py, checked against the file by test_penny.py -->
```python
def guarded(method: Handler) -> Handler:
    """Turn refusals into facts for the model, and never let a crash sound like success."""

    @functools.wraps(method)
    def wrapper(self: PennyHandlers, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
        try:
            if not isinstance(args, dict) or not isinstance(raw_data, dict):
                raise PolicyError("The request was malformed.", "Ask the caller to say that again.")
            return method(self, args, raw_data)
        except PolicyError as refusal:
            return FunctionResult(tool_result=refusal.fact, tool_prompt=refusal.ask)
        except MissingCallContext:
            return FunctionResult(tool_result="Nothing was done: the request had no call context.",
                                  tool_prompt="Apologize and offer to take a message.")
        except Exception:
            log.exception("tool %s failed", method.__name__)
            return FunctionResult(
                tool_result="The system couldn't finish that, so the outcome is unknown.",
                tool_prompt="Don't say it worked. Apologize and offer to try again.")

    return wrapper
```

It enforces three failure rules:

- **A refusal is a fact, not an error.** A `PolicyError` from the reservation book becomes `tool_result` and `tool_prompt`, with no actions attached.
- **No call context, no action.** A request without a `call_id` can't be tied to a session, so nothing happens.
- **A crash is never success.** Anything unexpected becomes "the outcome is unknown", with the instruction "Don't say it worked." The worst failure for a booking system is an agent telling the caller "you're all set" when nothing was saved.

## Router Tools

`start_booking` is the router tool for a new reservation:

<!-- source: handlers.py#start-booking --> <!-- snippet: no-run an excerpt of handlers.py, checked against the file by test_penny.py -->
```python
@guarded
def start_booking(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    self.store.reset_request(self._call_id(raw_data))
    return (FunctionResult(tool_result="A new reservation has been started.",
                           tool_prompt="Tell the caller you'll take a few details.")
            .update_global_data({"booking": {}, "booking_request": {}})
            .swml_change_context("booking"))
```

A router tool moves the conversation and resets what the next context depends on. Here, `reset_request` clears the call's draft, offers and holds in the reservation book. The `update_global_data` action clears the booking projection and the gathered answers, so a new booking starts clean.

## Finding, Holding and Confirming

`find_tables` applies any correction to the call's booking request, then asks the reservation book for numbered options:

<!-- source: handlers.py#find-tables --> <!-- snippet: no-run an excerpt of handlers.py, checked against the file by test_penny.py -->
```python
@guarded
def find_tables(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    call_id = self._call_id(raw_data)
    # What the caller has asked for: gather's answers, changed by every
    # correction since. A correction passed as an argument changes only
    # that detail, even if the last search was refused.
    draft = self.store.update_draft(call_id, args, self._gathered(raw_data, "booking_request"))
    try:
        request, options = self.store.find_options(
            call_id, draft["party_size"], draft["date"], draft["time"], draft["name"])
    except LargePartyError as refusal:
        return FunctionResult(tool_result=refusal.fact, tool_prompt=refusal.ask)

    if options:
        listed = "; ".join(option.spoken() for option in options)
        result = FunctionResult(
            tool_result=f"Open for {request.party_size} on {spoken_date(request.day)}: {listed}.",
            tool_prompt="Offer these options by number. When the caller picks one, "
                        "call hold_table with its number.")
    else:
        result = FunctionResult(
            tool_result=f"Nothing is open for {request.party_size} on "
                        f"{spoken_date(request.day)} within an hour of "
                        f"{spoken_time(request.start)}. Seatings run 5 PM to 8:30 PM.",
            tool_prompt="Say so, and ask whether another time or date would work. "
                        "Then call find_tables with only what changed.")
    return (result
            .update_global_data({"booking": {"request": request.spoken()}})
            .swml_change_step("choose")
            .swml_user_event({"type": "options_offered", "day": request.day.isoformat(),
                              "options": [{"number": o.number, "time": spoken_time(o.start)}
                                          for o in options]}))
```

Three details matter:

- **A correction changes one detail.** If the caller says "actually, make it 8", the model passes only `time`. Everything else stays as the caller last gave it, even after a refused search.
- **The large-party refusal carries no step change.** The model stays put and offers a person, which is the refusal's `ask`.
- **The model sees option numbers and times, never tables.** The UI event carries the same.

The reservation book keeps the request as a draft for each call:

<!-- source: reservations.py#update-draft --> <!-- snippet: no-run an excerpt of reservations.py, checked against the file by test_penny.py -->
```python
def update_draft(self, call_id: str, changes: dict[str, Any],
                 gathered: dict[str, Any]) -> dict[str, Any]:
    """Apply a correction to what this call has asked for, and return the result.

    The draft is kept whether or not a search passes the rules, so a correction
    to a refused search isn't lost. The first search starts from ``gathered``.
    """
    keys = ("party_size", "date", "time", "name")
    with self._tx() as db:
        draft = json.loads(self._session(db, call_id)["draft"])
        if not draft:
            draft = {key: gathered.get(key) for key in keys}
        draft.update({key: changes[key] for key in keys
                      if changes.get(key) not in (None, "")})
        db.execute("UPDATE sessions SET draft=? WHERE call_id=?", (json.dumps(draft), call_id))
    return draft
```

The first search starts from the gathered answers, and each correction updates the draft. The draft is saved before the search checks the rules, so a refused search doesn't lose the correction. Suppose gather collected a party of eight for Monday. The caller changes it to four, hears that the restaurant is closed on Mondays, and says "Friday, then". The next search is for four on Friday, not eight.

`hold_table` turns an option into a numbered proposal:

<!-- source: handlers.py#hold-table --> <!-- snippet: no-run an excerpt of handlers.py, checked against the file by test_penny.py -->
```python
@guarded
def hold_table(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    call_id = self._call_id(raw_data)
    proposal = self.store.hold_option(call_id, args.get("option"))
    return (FunctionResult(
                tool_result=f"On hold for five minutes: {proposal.spoken()}. "
                            f"This is proposal revision {proposal.revision}.",
                tool_prompt="Read the proposal back and ask the caller to confirm it. "
                            "If they clearly say yes, call confirm_booking with revision "
                            f"{proposal.revision}. If they want a change, call "
                            "find_tables with only what changed.")
            .update_global_data({"booking": {"proposal": proposal.spoken(),
                                             "revision": proposal.revision}})
            .swml_change_step("review")
            .swml_user_event({"type": "table_held", "revision": proposal.revision,
                              "day": proposal.day.isoformat(),
                              "time": spoken_time(proposal.start),
                              "party_size": proposal.party_size}))
```

The revision number goes to the model in both `tool_result` and `tool_prompt`, so it has the exact number to pass to `confirm_booking`.

`confirm_booking` commits the proposal:

<!-- source: handlers.py#confirm-booking --> <!-- snippet: no-run an excerpt of handlers.py, checked against the file by test_penny.py -->
```python
@guarded
def confirm_booking(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    call_id = self._call_id(raw_data)
    booking = self.store.confirm(call_id, args.get("revision"))
    code = spoken_code(booking.code)
    return (FunctionResult(
                tool_result=f"Confirmed: {booking.spoken()}. Confirmation code: {code}.",
                tool_prompt="Tell the caller it's booked and read the confirmation code "
                            "slowly, one character at a time. Then offer to text the details.")
            .update_global_data({"booking": {"summary": booking.spoken(), "code_spoken": code}})
            .swml_change_step("booked")
            .swml_user_event({"type": "booking_confirmed", "code": booking.code,
                              "day": booking.day.isoformat(),
                              "time": spoken_time(booking.start),
                              "party_size": booking.party_size}))
```

The confirmation code comes from the reservation book. Code spells it out ("K 7 Q P 4 M") so the voice reads one character at a time. The code is also projected into the `booked` step's text, so it's still there after the conversation moves on.

## The Rules for `global_data`

Penny's handlers follow four rules for session data:

1. **It's a projection, not the truth.** The reservation book holds the truth. `global_data` holds the few finished facts a step's text needs, like the booking summary and the spoken code.
2. **Write whole namespaces.** `update_global_data` merges keys at the top level. Each handler writes its whole `booking` or `manage` object, never a piece of one, so the value is always complete and self-consistent.
3. **Gathered answers are caller input.** What gather mode stores is what the caller said, and it's validated like any other input.
4. **Don't rely on another tool's write in the same turn.** Two tools called in one turn start from the same snapshot, so a handler can't see what another tool wrote in that turn.

UI events are another projection, for a screen instead of the model. Penny emits `options_offered`, `table_held`, `booking_confirmed`, `reservation_verified`, `reservation_cancelled` and `message_taken`. A web page can react to them without parsing speech.

## Try It: a Booking From the Command Line

`swaig-test` runs a tool handler directly, with no call. Because Penny keeps its state in the reservation book, keyed by call ID, you can walk through a whole booking in separate commands. Keep the variables from Lesson 4 exported:

```bash
export PENNY_DB_PATH=walkthrough.sqlite3
swaig-test penny.py --agent-class Penny --call-id demo-1 --exec find_tables --party_size 4 --date Friday --time "7:30 PM" --name "Maria Rivera"
swaig-test penny.py --agent-class Penny --call-id demo-1 --exec hold_table --option 1
swaig-test penny.py --agent-class Penny --call-id demo-1 --exec confirm_booking --revision 1
```

The results look like this. Your dates will follow your calendar, and your confirmation code will differ:

```
FunctionResult: {'tool_result': 'Open for 4 on Friday, September 25: option 1, 7:30 PM; option 2, 7 PM; option 3, 8 PM.', ...}
FunctionResult: {'tool_result': 'On hold for five minutes: a table for 4 on Friday, September 25 at 7:30 PM, under Maria Rivera. This is proposal revision 1.', ...}
FunctionResult: {'tool_result': 'Confirmed: a table for 4 on Friday, September 25 at 7:30 PM, under Maria Rivera. Confirmation code: W D M C D W.', ...}
```

Now try the things a confused model might do:

```bash
# Confirm again: the same booking comes back, and no second one is made
swaig-test penny.py --agent-class Penny --call-id demo-1 --exec confirm_booking --revision 1
# Confirm from a different call: that call holds nothing
swaig-test penny.py --agent-class Penny --call-id demo-2 --exec confirm_booking --revision 1
```

The second command gets "No table is on hold." A call can only confirm its own proposal.

## Key Takeaways

- Tool descriptions are prompts: say what each tool does *not* do
- Keep facts (`tool_result`), instructions (`tool_prompt`) and actions separate
- Guard every handler: refusals are facts, and failures are never success
- `global_data` is a projection. The reservation book is the truth.

## Review Questions

1. Why does `confirm_booking` change the step with an action instead of telling the model to move on?
2. What does the caller hear if the database is down when they confirm?
3. Why does `find_tables` let arguments override the gathered answers?

## Next Steps

The `search` step expects gathered answers to be waiting. Next, build the step that gathers them, and see how facts reach the model's instructions. Continue with [Lesson 7: Gather Mode and Projection](07-gather-and-projection.md).

---

[Previous: Steps and Scoping](05-steps-and-scoping.md) | [Overview](README.md) | [Next: Gather Mode and Projection](07-gather-and-projection.md)
