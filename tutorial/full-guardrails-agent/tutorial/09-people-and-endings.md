# Lesson 9: People, Messages and Endings

The last tools reach past the conversation. They transfer the call, take a message, send a text or hang up, and none of that can be taken back. Each one follows the same rule as booking. The model can ask for it, and code decides where it goes, what it says and when it happens.

## Table of Contents

1. [Handing Off to a Person](#handing-off-to-a-person)
2. [Taking a Message](#taking-a-message)
3. [Texting the Confirmation](#texting-the-confirmation)
4. [Ending the Call](#ending-the-call)
5. [Keeping the Record](#keeping-the-record)
6. [Watching a Call](#watching-a-call)

---

## Handing Off to a Person

`request_human` connects the caller with the host stand, or starts taking a message when nobody is there:

<!-- source: handlers.py#request-human --> <!-- snippet: no-run an excerpt of handlers.py, checked against the file by test_penny.py -->
```python
@guarded
def request_human(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    self._call_id(raw_data)
    if self.settings.host_number and self.store.host_stand_open():
        # say() is an action, so it finishes before connect() runs. The
        # response text is spoken by the model on its own schedule and
        # could be cut off by the transfer.
        return (FunctionResult(tool_result="The call is being transferred to the host stand.",
                               tool_prompt="Say nothing more; the transfer notice is playing.")
                .say(TRANSFER_NOTICE)
                .connect(self.settings.host_number, final=True))
    return (FunctionResult(tool_result="Nobody is at the host stand right now.",
                           tool_prompt="Tell the caller nobody is at the host stand, and "
                                       "that you'll take a message for them.")
            .update_global_data({"message": {}})
            .swml_change_context("help"))
```

Three decisions are made here, and the model makes none of them:

- **Where the call goes.** `request_human` takes no arguments. The number comes from `PENNY_HOST_NUMBER` on the server. A tool that took a phone number would let a caller say "transfer me to this number" and have the model do it.
- **Whether anyone is there.** The handler checks the clock when the tool runs. The `host_stand` fact in the triage step only lets the model set expectations. It was worked out when the call started, and a call that starts at 3:58 may ask for a person at 4:02.
- **What the caller hears first.** The notice is a `say()` action. Actions run in order, so the whole notice plays before `connect()` transfers the call. The model's reply is spoken on its own schedule, and a transfer could start before it finished. `final=True` makes the transfer permanent: the call leaves Penny for good.

When nobody is at the host stand, or no host number is configured, the handler moves the call to the `help` context instead. It clears any earlier message on the way.

## Taking a Message

The `help` context takes a message with gather mode:

<!-- source: workflow.py#help --> <!-- snippet: no-run an excerpt of workflow.py, checked against the file by test_penny.py -->
```python
def _help(builder: ContextBuilder) -> None:
    ctx = builder.add_context("help")
    take = scoped(ctx.add_step("take_message"), "Take a message for the host stand.", [])
    take.set_gather_info(
        output_key="message",
        completion_action="save_message",
        prompt="Nobody is at the host stand, so you're taking a message for them.")
    take.add_gather_question(key="name", question="What's your name?", functions=["finish"])
    take.add_gather_question(
        key="callback", question="What's the best number to call you back on?",
        confirm=True, functions=["finish"])
    take.add_gather_question(
        key="body", question="What would you like me to pass along?", functions=["finish"])

    scoped(ctx.add_step("save_message"),
           "Call save_message now. Don't tell the caller it's saved until it returns. If "
           "it asks for a correction, ask the caller and pass only the corrected detail.",
           ["save_message"])
    scoped(ctx.add_step("message_saved"),
           "The message is saved. Tell the caller the host stand will call them back, "
           "answer last questions with house_info, then call finish.",
           ["house_info", "finish"])
    ctx.set_initial_step("take_message")
```

This is the booking pattern again, only smaller. Gather mode asks the questions, `completion_action` moves to a step whose only tool is `save_message`, and `save_message` moves on once the message is stored.

Three details keep messages useful and private:

- The callback number uses `confirm=True`. One misheard digit makes a message useless, so the model reads it back first.
- Every question offers `finish`, for a caller who changes their mind.
- No tool reads messages. The model can leave one for the host stand, and can never read what anyone else left.

`save_message` stores the message:

<!-- source: handlers.py#save-message --> <!-- snippet: no-run an excerpt of handlers.py, checked against the file by test_penny.py -->
```python
@guarded
def save_message(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    call_id = self._call_id(raw_data)
    taken = self._gathered(raw_data, "message")

    def detail(key: str) -> str:
        return str(args[key] if args.get(key) not in (None, "") else taken.get(key) or "")

    saved = self.store.save_message(call_id, detail("name"), detail("callback"), detail("body"))
    return (FunctionResult(
                tool_result=f"Message saved for the host stand, with a callback number "
                            f"ending in {saved['callback'][-4:]}.",
                tool_prompt="Tell the caller the host stand will call them back.")
            .swml_change_step("message_saved")
            .swml_user_event({"type": "message_taken"}))
```

`save_message` uses the gathered answers, and a detail passed as an argument replaces the gathered one. The reservation book requires a callback number with 10 to 15 digits, a name and a few words. It keeps one message per call, so a re-fired tool doesn't leave two. The model is told only the last four digits of the callback number, which is enough to reassure the caller.

## Texting the Confirmation

`send_confirmation_text` texts the booking this call made to the number the call comes from:

<!-- source: handlers.py#send-text --> <!-- snippet: no-run an excerpt of handlers.py, checked against the file by test_penny.py -->
```python
@guarded
def send_confirmation_text(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    call_id = self._call_id(raw_data)
    booking = self.store.booking_for_call(call_id)
    if booking is None:
        raise PolicyError("This call hasn't booked a reservation.", "Say there's nothing to text yet.")
    if not self.settings.sms_from:
        raise PolicyError("Texting isn't set up at the restaurant.",
                          "Apologize, and make sure they have the confirmation code.")
    # The destination is the number this call comes from. The model can't supply one.
    caller = str(raw_data.get("caller_id_num") or "")
    if not re.fullmatch(r"\+[1-9]\d{9,14}", caller):
        raise PolicyError("The number this call comes from can't receive a text.",
                          "Say you can't text this number, and make sure they have the code.")
    # The platform sends the text after this returns, so Penny can only say
    # a text was requested, never that it was sent or arrived.
    decision = self.store.request_sms(booking.code)
    if decision == "duplicate":
        return FunctionResult(
            tool_result="A text for this booking was requested moments ago.",
            tool_prompt="Tell the caller a text was requested a moment ago. If it hasn't "
                        "arrived in a couple of minutes, you can request it again.")
    if decision == "limit":
        raise PolicyError("A text for this booking has been requested as many times "
                          "as allowed.",
                          "Say you can't request another text, and make sure they have "
                          "the confirmation code.")
    body = (f"The Copper Pot: {booking.spoken()}. Confirmation code {booking.code}. "
            "Call us to change or cancel.")
    return (FunctionResult(
                tool_result=f"Requested a text of the details to the number ending in "
                            f"{caller[-4:]}.",
                tool_prompt="Tell the caller you've requested the text.")
            .send_sms(to_number=caller, from_number=self.settings.sms_from, body=body))
```

Three rules keep the text safe:

- **The tool has no parameters.** The destination is `caller_id_num` from the platform's tool request: the number the call comes from. If the model passes a `to_number` anyway, the handler never reads it. A test checks exactly that.
- **The content comes from the reservation book**: the booking this call made, and nothing from the conversation.
- **Every refusal is a fact.** The tool refuses when this call has no booking, when texting isn't configured, or when the caller ID can't receive texts. Each refusal says what to tell the caller.

The handler requests the text, and the platform sends it after the tool returns. Penny can't know whether the text arrived, so the model is told only that it was requested. The reservation book counts the requests:

<!-- source: reservations.py#request-sms --> <!-- snippet: no-run an excerpt of reservations.py, checked against the file by test_penny.py -->
```python
def request_sms(self, code: str) -> str:
    """Record a request to text a booking, and say whether to send it.

    The platform sends the text after the tool returns, so nothing here can
    know it arrived. A repeat within SMS_RESEND_SECONDS is a duplicate and
    isn't sent. After that, a caller who didn't get it may ask again, up to
    MAX_SMS_PER_BOOKING times. Returns "send", "duplicate" or "limit".
    """
    now = self._now().timestamp()
    with self._tx() as db:
        row = db.execute("SELECT sms_requests, sms_requested_at FROM reservations "
                         "WHERE code=?", (code,)).fetchone()
        if row["sms_requests"] >= MAX_SMS_PER_BOOKING:
            return "limit"
        if row["sms_requests"] and now - row["sms_requested_at"] < SMS_RESEND_SECONDS:
            return "duplicate"
        db.execute("UPDATE reservations SET sms_requests = sms_requests + 1, "
                   "sms_requested_at = ? WHERE code=?", (now, code))
        return "send"
```

A repeat within two minutes is treated as a tool fired twice, and isn't sent. After two minutes, a caller who didn't get the text can ask again, up to three requests in all.

Caller ID can be faked. The worst case is that a stranger receives a few texts about a booking they didn't make. That's why the text carries only this call's booking, and why the number of texts is capped.

## Ending the Call

`finish` plays a fixed goodbye, then hangs up:

<!-- source: handlers.py#finish --> <!-- snippet: no-run an excerpt of handlers.py, checked against the file by test_penny.py -->
```python
@guarded
def finish(self, args: dict[str, Any], raw_data: dict[str, Any]) -> FunctionResult:
    # The goodbye is a say() action, not response text: actions run in order,
    # so the caller hears all of it before hangup() ends the call.
    return (FunctionResult(tool_result="The goodbye is playing and the call will end.",
                           tool_prompt="Say nothing more.")
            .say(GOODBYE)
            .hangup())
```

The goodbye is a fixed sentence played by an action, and `hangup()` runs after it, so the caller always hears all of it. A goodbye left to the model's reply races the hangup, and on real calls the goodbye gets cut off. The `tool_prompt` tells the model to say nothing more, so it doesn't talk over the goodbye.

`finish` is offered where a call can reasonably end: triage, `booked`, `details`, `cancelled`, `locked`, `message_saved`, and the message questions. It isn't offered in the middle of a booking. A caller who wants to leave mid-booking hangs up, and any table they had on hold is released when the hold expires five minutes later.

As Lesson 5 explained, `set_end(True)` is not a hangup. Ending a call is an action.

## Keeping the Record

When the call ends, the SDK runs the `on_call_end` handlers with the call log. This is the `hangup_hook` you saw in Lesson 4's tool list. The platform fires it on hangup, and it's never offered to the model. Penny's handler writes down what happened:

<!-- source: handlers.py#capture-call --> <!-- snippet: no-run an excerpt of handlers.py, checked against the file by test_penny.py -->
```python
def capture_call(self, call_log: list[dict[str, Any]], raw_data: dict[str, Any]) -> None:
    """on_call_end: record what the store says happened, not what the transcript says."""
    call_id = raw_data.get("call_id") if isinstance(raw_data, dict) else None
    if not isinstance(call_id, str) or not call_id:
        log.warning("call ended without a call id; nothing recorded")
        return
    outcome = self.store.record_call_end(call_id, len(call_log or []))
    log.info("call %s ended: %s", call_id, outcome)
```

The outcome, `booked`, `cancelled`, `message` or `no_change`, comes from the reservation book. The call log only says how long the conversation was. A transcript records what was *said*, and a conversation can sound finished when nothing was saved.

Penny also asks the model for a two-sentence summary with `set_post_prompt`, and logs it:

<!-- source: penny.py#summary --> <!-- snippet: no-run an excerpt of penny.py, checked against the file by test_penny.py -->
```python
def on_summary(self, summary: Any, raw_data: Any = None) -> None:
    """The model's recap of the call: useful to read, never the record of what happened."""
    log.info("call summary (model-written, not authoritative): %s", summary)
```

A summary helps a person skimming calls. Nothing in Penny uses it to decide anything.

## Watching a Call

Set `PENNY_DEBUG_EVENTS=1` and the platform sends Penny debug events while a call runs: step changes, barge-ins, errors, and the start and end of the session. Penny logs each one. When something odd happens on a call, the log shows which step the model was in at the time. Debug events are for you to read. Nothing in Penny acts on them.

## Key Takeaways

- Destinations come from server settings or the call itself, never from tool arguments
- Check live facts when the tool runs. A projection is for setting expectations.
- Anything the caller must hear before a transfer or hangup goes in a `say()` action
- Record outcomes from the system of record, not the transcript or the model's summary

## Review Questions

1. Why does `request_human` take no parameters?
2. A caller asks Penny to text the confirmation to their partner's phone. What happens?
3. Why is the goodbye a `say()` action instead of the model's reply?
4. Why does `capture_call` ask the reservation book what happened instead of reading the call log?

## Next Steps

Penny is complete. The last lesson proves it, with tests that show the guardrails hold, command-line checks, and a real conversation. Continue with [Lesson 10: Testing and Running](10-testing-and-running.md).

---

[Previous: The Verification Gate](08-the-verification-gate.md) | [Overview](README.md) | [Next: Testing and Running](10-testing-and-running.md)
