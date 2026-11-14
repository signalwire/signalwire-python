# Conversation Patterns

Each pattern here keeps a decision in your code that the model would otherwise make from the conversation. The helpers are in `signalwire.patterns` and `signalwire.speech`.

## Table of Contents

- [Confirming a Change](#confirming-a-change)
- [Read-Backs Callers Can Interrupt](#read-backs-callers-can-interrupt)
- [Recording What Was Done](#recording-what-was-done)
- [Questions That Carry Content](#questions-that-carry-content)
- [The Caller's Own Words](#the-callers-own-words)
- [Numbers the Way a Voice Should Say Them](#numbers-the-way-a-voice-should-say-them)
- [Tool Outcomes the Model Can Trust](#tool-outcomes-the-model-can-trust)
- [Requests to Come Back To](#requests-to-come-back-to)
- [What a Caller Spelled](#what-a-caller-spelled)
- [Testing a Call Flow](#testing-a-call-flow)

## Confirming a Change

A change the caller must agree to, such as placing an order or cancelling an account, needs a yes to that change, not a yes somewhere in the call. The platform's confirm pattern does this with semantic gates:

1. A function proposes the change. It reads the change back and records it in `semantic_state`, in one action object, so the proposal's dialogue starts with the read-back.
2. The tool that carries out the change has three gates, each judged on the proposal's dialogue: the caller's latest turn is an answer, the answer is a yes, and what they answered was a read-back of this change.

`Proposal` builds both halves. The gates' questions are the platform's own, which were replayed against logged confirmation checks.

```python
from signalwire import AgentBase, FunctionResult
from signalwire.patterns import Proposal

agent = AgentBase(name="orders", route="/orders")
order = Proposal("place_order", decline_tool="change_order")

ITEM = {
    "type": "object",
    "properties": {"item": {"type": "string", "description": "The item, with its size"}},
    "required": ["item"],
}

def review_order(args, raw_data):
    read_back = f"That's {args['item']} for pickup. Is that right?"
    return order.propose(read_back, raw_data=raw_data, details={"item": args["item"]})

def place_order(args, raw_data):
    item = raw_data["global_data"]["semantic_state"]["item"]
    return order.complete(f"The order for {item} is placed.")

agent.define_tool("review_order", "Read the order back to the caller", ITEM, review_order)
agent.define_tool("place_order", "Place the order the caller said yes to", {}, place_order,
                  gates=order.confirm_gates())
```

`propose()` says the read-back word for word, records `{"proposal": read_back, "revision": n}` with your details, and has the model wait for the caller's answer. When a gate blocks the confirm tool, the model is told why, with the proposal quoted from `semantic_state`, and chaining is turned off for the call, so it answers in words before it calls a tool again. To read the same change back again, use `ask_again(raw_data)`: the platform marks a new proposal only when `semantic_state` changes, so it records the next revision.

`Proposal(..., unclear=True, threshold=0.6)` lets the gates answer unclear as well, where the gate provider can, which asks the caller again. Give the confirm step only the confirm tool, the decline tool and a tool that notes other requests, so a "yes, and also..." becomes two calls.

## Read-Backs Callers Can Interrupt

A caller often answers before a read-back ends. Order it so the part they must hear comes first:

1. The change itself: "That's a large tea, not a small one."
2. The details of the change: "for pickup at five, on the card ending in one two three four."
3. What was already settled, last: "at the Main Street store."

A caller who cuts it off has heard the change. The confirm gates count a yes once the caller has heard what the change is, so a read-back that leads with it confirms sooner.

## Recording What Was Done

After the change is carried out, write a `semantic_state` that records it, rather than clearing it with `{}`. `Proposal.complete(summary)` does this. A state that changes starts the next proposal's dialogue there, so a later confirmation isn't judged on what was said before this one, and the model and the gates see what's settled.

## Questions That Carry Content

A one-word answer is hard to judge: "yes" may answer something else the agent said. Ask questions whose answers carry content. "Which size would you like, small or large?" gets "large", which a gate, the recognizer and your code can check. "Do you want a large?" gets "yes".

## The Caller's Own Words

A tool can check that an argument is something the caller said, rather than something the model inferred.

`define_tool(..., vouched=True)` asks the model. The tool gets a required boolean, `data_supplied_by_user`, and runs only when the model sets it to true. Otherwise the model is told to get the answer from the caller first.

`caller_turns(raw_data)` reads what the caller said from the request's conversation. A request carries the conversation only with `swaig_post_conversation` on, and `needs_conversation=True` on the tool turns it on.

```python
from signalwire import AgentBase, FunctionResult
from signalwire.core.post_prompt import caller_turns

agent = AgentBase(name="stores", route="/stores")
ZIP = {
    "type": "object",
    "properties": {"zip": {"type": "string", "description": "The caller's ZIP code"}},
    "required": ["zip"],
}

def find_store(args, raw_data):
    said = " ".join(caller_turns(raw_data, last=3))
    if args["zip"] not in said.replace(" ", ""):
        return FunctionResult(tool_result="find_store was not run.",
                              tool_prompt="Ask the caller for their ZIP code.")
    return FunctionResult(tool_result=f"The nearest store to {args['zip']} is on Main Street.")

agent.define_tool("find_store", "Find the store nearest a ZIP code", ZIP, find_store,
                  needs_conversation=True)
```

The conversation has the recognizer's final text, after hearing hints and number formatting. For the words as the recognizer heard them, with a confidence for each, call `agent.record_speech_finals()` and read `agent.speech_finals(raw_data["call_id"])`. The finals come from the platform's `ai.speech_detect` events, which the agent receives at its own `/ai_events` endpoint. A handler can ask the caller again about a word the recognizer wasn't sure of, such as a letter of a spelled name. `agent.on_ai_event(handler)` receives every AI event the platform posts.

## Numbers the Way a Voice Should Say Them

The platform normalizes text before its pronunciation rules run, so a bare number is already words by then. A ZIP code given as "10001" can be read "ten thousand one", and `add_pronunciation()` can't change that. Give the words to say instead:

```python
from signalwire.speech import say_digits, say_last_digits, say_money

say_digits("415-555-0192")         # "four one five, five five five, zero one nine two"
say_digits("10001", zero="oh")     # "one oh oh oh one"
say_last_digits("4111111111111234")  # "one two three four"
say_money(14.5)                    # "fourteen dollars and fifty cents"
```

Use them in a `say` action, or in the tool result the model reads back. They're English. `say_money` knows USD, CAD, AUD, NZD, EUR, GBP, MXN, INR and JPY.

When a step asks for a number with a known length, `Step.set_expected_answer(5)` tells the recognizer to end its wait once the caller has said that many digits. See the [Contexts and Steps Guide](contexts_guide.md#expected-answers).

## Tool Outcomes the Model Can Trust

The model reads a tool's result as what happened, so the result must not claim more than the handler knows.

- Raise `ToolRefusal(tool_result, tool_prompt)` to decline a call with an outcome you know, such as an item out of stock.
- Any other exception tells the model the function failed before it finished, so whether it took effect is unknown, and not to tell the caller it worked or that it didn't. The exception is logged, not sent.
- A dict without a `response` or an `action` is the handler's data, and the model gets it as JSON.

SignalWire sends a tool request again after a timeout, a failed connection or a 5xx, so a slow tool could run twice. The agent answers such a retry with the first attempt's result, and one that arrives while the first is still running waits for it. `set_tool_resend_dedupe(False)` turns this off. The record is kept in the agent's process: with several processes or replicas, a retry that reaches another one runs the tool again, so make tools that change things safe to run twice.

## Requests to Come Back To

A caller in the middle of one task often asks for another: "and can you also check my balance?" Taking it up at once loses the first task, and ignoring it loses the second. `RequestList` keeps such requests in the call's `global_data`. A tool notes each one, and the model tells the caller it's noted for right after this. The step text shows the list, so the agent takes the requests up when the current task is done.

```python
from signalwire import AgentBase
from signalwire.patterns import RequestList

agent = AgentBase(name="support", route="/support")
later = RequestList("later", openers={"balance": "You also asked about your balance."})
agent.set_global_data(later.defaults())

NOTE = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": ["balance", "question"]},
        "about": {"type": "string", "description": "What the caller asked, in a few words"},
    },
    "required": ["kind", "about"],
}

def note_request(args, raw_data):
    return later.note(raw_data, args["kind"], args["about"])

agent.define_tool("note_request", "Note something the caller asked to do later", NOTE,
                  note_request)
ctx = agent.define_contexts().add_context("default")
ctx.add_step("take_order").set_text("Take the order.\n\n${global_data.later_text}")
```

`later.next(raw_data)` gives the oldest request with its opener, and `later.done(raw_data)` removes it once it's taken up. The kinds and their openers are yours. A step's text is expanded when the step is entered, so return `refresh_step()` with a note to show the new list at once.

## What a Caller Spelled

A caller spells a name, a code or an email address in many ways: letter by letter, with letter names, with "S as in Sam", with the NATO alphabet, or with "double l". `signalwire.speech.spelling` reads them all from the recognizer's text.

```python
from signalwire.speech.spelling import read_spelled, spelling_variants, spoken_email

read_spelled("S as in Sam, m i t h")             # ["S", "M", "I", "T", "H"]
read_spelled("sierra mike india tango hotel")    # ["S", "M", "I", "T", "H"]
spoken_email("john dot smith at example dot com")  # "john.smith@example.com"
spelling_variants(["S", "M", "I", "T", "H"], {"S": "F", "M": "N"})
# ["SMITH", "FMITH", "SNITH", "FNITH"]
```

The recognizer confuses some letters, and which ones depends on the recognizer and the voice, so `spelling_variants` takes confusion groups you measure on your own calls; none are built in. Its `positions` argument limits the changes to the letters the recognizer was least sure of, which `agent.speech_finals()` gives a confidence for. Look each variant up in your records, in order: the first that matches is the likeliest.

## Testing a Call Flow

`swaig-test` runs one tool call. To test a flow, such as a confirmation across steps, `signalwire.testing.CallSimulator` runs the agent's tools through a simulated call. It reads the agent's rendered SWML as the platform would, and checks each call as the platform does: a tool the current step doesn't offer doesn't run, and a gated tool runs only when your gate callback lets it. Each result's actions change the call: global data and `semantic_state`, the step and context, the functions turned on, `say`, and the end of the call.

```python
from signalwire.testing import CallSimulator

def test_a_yes_places_the_order():
    sim = CallSimulator(agent, gates=lambda gate, sim, args: True)
    sim.caller("A large tea, please.")
    assert not sim.call("place_order").ran   # not offered until the read-back
    sim.call("review_order", {"item": "a large tea"})
    sim.caller("Yes.")
    assert sim.call("place_order").ran
    assert sim.semantic_state == {"done": "The a large tea is ordered."}
```

The gate callback gets each gate and returns True, False, a probability compared with the gate's threshold, or `"unclear"`. With `check_tool_mentions=True`, a call whose result names a tool that the step it leaves the call in doesn't offer raises `ToolMentionError`: the model would read the name and might call a tool it doesn't have. Give `stubs` for DataMap tools, which run on the platform. To check changed code against real calls, record tool requests with `RequestRecorder`, which is tool middleware, and run them again with `CallSimulator(agent).replay(requests)`. The requests carry what callers said, so keep a recording where you'd keep call recordings.

## Related Documentation

- [API Reference](api_reference.md#semantic-gates): semantic gates and every tool option
- [SWAIG Reference](swaig_reference.md): every `FunctionResult` action
- [Contexts and Steps Guide](contexts_guide.md): steps, their function lists and expected answers
