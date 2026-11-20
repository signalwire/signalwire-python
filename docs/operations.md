# Operations

An operations agent is written as what it can do for a caller. You write each operation once, for any caller: its fields, its rules and its writes. The SDK runs everything else the same way for every operation: finding the caller's account, reading each change back, taking the caller's yes, carrying the change out, and keeping the call's record. The helpers are in `signalwire.operations`.

## Table of Contents

- [A Store in One Page](#a-store-in-one-page)
- [Operations](#operations)
- [The Change Lifecycle](#the-change-lifecycle)
- [A Request While a Change Waits](#a-request-while-a-change-waits)
- [Identifying the Caller](#identifying-the-caller)
- [Lookups](#lookups)
- [Money](#money)
- [Appointments and Messages](#appointments-and-messages)
- [What the SDK Generates](#what-the-sdk-generates)
- [The Call's Record](#the-calls-record)
- [Words, Languages and the Medium](#words-languages-and-the-medium)
- [Games, Kiosks and Screens](#games-kiosks-and-screens)
- [Installing on Your Own Agent](#installing-on-your-own-agent)
- [Two Services on One Agent](#two-services-on-one-agent)
- [InfoBot: Answering From a Corpus](#infobot-answering-from-a-corpus)
- [Testing](#testing)

## A Store in One Page

```python
from typing import Literal

from signalwire.operations import Change, Field, Operation, Refuse, ServiceAgent, Write
from signalwire.testing import CallSimulator

ORDERS = {"#W1": {"status": "pending", "total": 54.04}, "#W2": {"status": "delivered", "total": 20.00}}
WRITES = []

agent = ServiceAgent("store", role="You answer the phone for an online store. You are warm, brief and plain-spoken.",
                     currency="USD")
agent.identify(any_of=[["email"]], find=lambda call, keys: "u1" if keys["email"] == "ann@example.com" else None,
               describe=lambda call: "Ann; orders #W1 (pending) and #W2 (delivered)")
agent.writes_with(lambda call, write: WRITES.append((write.name, write.args)))


@agent.lookup("An order's status and total.", fields={"order_id": Field(str, "The order's id.")})
def order_details(call, order_id):
    order = ORDERS.get(order_id)
    if order is None:
        raise Refuse(f"{order_id} isn't one of their orders.")
    return f"{order_id} is {order['status']}; total ${order['total']:.2f}."


@agent.operation(tool="cancel_order")
class Cancel(Operation):
    """Cancel a pending order."""

    order_id = Field(str, "The order to cancel.")
    reason = Field(Literal["no longer needed", "ordered by mistake"], "Why they're cancelling.",
                   ask="Why are they cancelling it?")

    def prepare(self, call, f):
        order = ORDERS.get(f.order_id)
        if order is None or order["status"] != "pending":
            raise Refuse(f"{f.order_id} can't be cancelled: only pending orders can.")
        return Change(
            read_back=f"Cancel order {f.order_id}, refunding ${order['total']:.2f}. Shall I go ahead?",
            touches=[f"order:{f.order_id}"],
            writes=[Write("cancel_order", order_id=f.order_id, reason=f.reason)],
            money=[-order["total"]],
            done=f"Order {f.order_id} is cancelled.",
        )


call = CallSimulator(agent)
call.call("find_account", {"email": "ann@example.com", "asked_for": "cancel an order", "data_supplied_by_user": True})
call.call("cancel_order", {"order_id": "#W1", "reason": "no longer needed", "data_supplied_by_user": True})
assert call.step == "confirm"
call.caller("Yes, please.")
done = call.call("confirm_change", {"change": "cancel"})
assert done.response == "Done. Order #W1 is cancelled."
assert WRITES == [("cancel_order", {"order_id": "#W1", "reason": "no longer needed"})]
```

That's the whole agent. Nothing above sets a step, a history mode, a gate or a global data key: the SDK generates them, the same for every operation.

## Operations

An operation is a class with `Field` attributes, a docstring (what it does, as the model reads it) and `prepare(call, fields)`. `call` is a `CallContext`: the request's record, the caller's account, your own state for the call, and ways to act on it. `prepare` checks the request, may look things up, and answers one of three ways:

| `prepare` | Meaning | What the SDK does |
| --- | --- | --- |
| returns `Change(...)` | The request is valid and complete | Freezes it as the change waiting for a yes, and the platform reads it back |
| raises `Need(ask)` | Something wasn't said | Tells the model what to ask; nothing is proposed |
| raises `Refuse(why, then)` | The request breaks a rule | Tells the model why and what can be done instead; nothing changes |

A `Change` carries `read_back` (the words the caller says yes to: put the change itself in the first clause), `touches` (stable keys for what it acts on, such as `order:#W1`), `writes` (the backend writes, kept as data), `money` (what each write moves, and `currency`, see [Money](#money)) and `done` (what to tell the caller once each write went through).

A change that has to wait for another one the caller asked for names that one's kind in `after` (and why, in `after_why`): an item change that would leave the order's address unchangeable, while they've also asked to change the address. It isn't read back yet. It's set aside, the model is told to call that kind's tool now, and it's offered once a change of that kind is settled.

A field with `ask` is asked for when the model sends it empty, null or as "not said" (a field with a fixed choice of values gets that option), before `prepare` runs, so the model is never pushed to invent it. Every operation tool also has the caller vouch for its details (`data_supplied_by_user`), and nothing runs without that.

Writes run through the agent's writer (`writes_with`) or the operation's own `apply(call, write)`. Raise `WriteFailed(reason)` when the backend refuses one: the writes before it stay made, and the model is told exactly what went through. `call.write_key` is unique to each write in the call, for backends that take an idempotency key.

## The Change Lifecycle

Every change goes through the same steps:

1. The model calls an operation's tool with everything the caller said.
2. `prepare` answers.
3. The change is frozen as the one waiting, and the platform reads it back. Its state is recorded ahead of the read-back, so a caller who talks over it doesn't lose it.
4. The model calls `confirm_change` or `decline_change`. `confirm_change` has one gate: did the caller agree to this read-back. A yes said while it was still being read counts.
5. The writes run in order, each outcome kept.
6. The change goes into the call's history, with the money it moved; after a second change that moves money, the model is told what the call comes to in all.
7. A change set aside for after this one is offered next; with none, the model is told to go on with anything else the caller asked for.

## A Request While a Change Waits

When the caller asks for something else while a change waits for their yes, the new request (N) is weighed against the one waiting (W) by what both touch:

| Case | What happens |
| --- | --- |
| N is the same operation, made "as well", and `combine` allows it | One change: `merge(W, N)`, read back as one |
| N is the same operation for things W is for, and "as well" wasn't said | Nothing changes; the model is told to ask "as well, or instead?" |
| N is the same operation otherwise, or `conflicts_with` W | N takes W's place for what both touch; the rest of W (`without`) is built again and set aside. If it can't go through without what N took, nothing changes |
| N conflicts with W and was asked for "as well" | Nothing changes; they can't have both, and the model is told why |
| W's operation lists N's kind in `goes_before` | W stays waiting; N is set aside for right after |
| Anything else | N is read back now; W is set aside for right after |

A change set aside is weighed against the new one the same way. The hooks are the operation's: `combine` (the fields that must match to merge), `merge(held, new)`, `conflicts_with(other, mine, theirs)`, `without(args, gone)` and `goes_before`.

```python
from signalwire.operations import Change, Field, Operation, ServiceAgent

agent = ServiceAgent("returns", role="You handle returns and exchanges.")


@agent.operation(tool="return_items")
class Return(Operation):
    """Return items of a delivered order."""

    order_id = Field(str, "The delivered order.")
    items = Field(list[str], "The items to return.")
    refund_to = Field(str, "Where the refund goes.")
    combine = ("refund_to",)  # "as well" merges when the refund goes to the same place

    def prepare(self, call, f):
        return Change(read_back=f"Return {', '.join(f.items)} from {f.order_id}. Shall I?",
                      touches=[f"order:{f.order_id}", *[f"item:{i}" for i in f.items]])

    def conflicts_with(self, other, mine, theirs):
        if other == "exchange" and mine.touches[0] in theirs.touches:
            return "a delivered order takes one return or one exchange, not both"
        return None

    def without(self, args, gone):
        items = [i for i in args.get("items") or [] if f"item:{i}" not in gone]
        return {**args, "items": items} if items else None
```

## Identifying the Caller

`identify(any_of=[...], find=...)` adds a step and a tool that find the caller's account by any one of the key sets. `find(call, keys)` returns the account's id, or raises `Refuse` (not found, with what to ask next) or `Need`. `load(call, account_id)` gives operations the account as `call.account`; `describe(call)` puts it in a few words for the steps, and is read again after every change. What the caller asked for before they were identified (`asked_for`) is kept in the record. With `check_keys=False`, `find` is called without a whole key set, for a search that recovers from misheard or spelled keys itself.

## Lookups

```python
from signalwire.operations import Field, ServiceAgent

agent = ServiceAgent("info", role="You answer questions about the shop.")


@agent.lookup("Opening hours for a day.", fields={"day": Field(str, "The day.")}, before_identity=True)
def hours(call, day):
    return f"{day}: 9 to 5."
```

A lookup reads and changes nothing. It returns text or a `FunctionResult`, or raises `Refuse`. Lookups are offered once the caller is identified, unless `before_identity=True`.

## Money

`Change.money` is what each write moves: more than 0 charged, less than 0 back to the caller. An amount can be an int, a float, a numeric string or a `Decimal`, and it's kept exactly. `Change.currency` is its ISO 4217 code, such as `"EUR"`; `currency=` on the service is the code for changes that don't give one. With no currency anywhere, amounts are stated without one.

After a second change that moves money, the model is told what the call comes to, for each currency apart: "$12.50 back to them and €5.00 charged". Amounts of different currencies are never added together.

`format_money(amount, currency)` writes an amount the way the model reads it: a symbol or code and the currency's own decimal places for the common currencies in `CURRENCIES` (`$54.04`, `€54.04`, `¥5,404`, `CA$12.00`, `KWD 1.235`), any other code after the amount (`54.04 XOF`), and a plain number with no currency. Use it in your own read-backs too. `money_format=fn(amount, currency)` replaces it for the totals the service states; `amount` is a `Decimal`, never below 0, and `currency` is the code or None.

```python
from signalwire.operations import ServiceAgent, format_money

agent = ServiceAgent("boutique", role="You answer the phone for a boutique in Lyon.", currency="EUR")
assert format_money(54.04, "EUR") == "€54.04"
```

## Appointments and Messages

Two task packs add common operations to a service with `add_to`, against a backend of yours given as functions. Each has its own wording table, and `tools=` or `tool=` renames what it generates.

`Appointments` finds open times and books, moves and cancels the caller's appointments. `openings(call, when, kind)` returns the `Slot`s open near when they'd like it, in their words ("Tuesday afternoon"); `book(call, slot, kind, note)` books one once they've said yes; `booked(call)`, `move` and `cancel` work on their own `Appointment`s. A slot or an appointment comes with its `label`, how it's said ("Tuesday the 3rd at 2 pm"), and the pack never reads or writes a date itself: the time zone, the calendar and the language are yours. Only a slot it found open can be booked. Moving and cancelling the same appointment can't both happen, so one takes the other's place. With `before_identity=True` a new customer can book before they're identified; their own appointments always need an account. The words are in `APPOINTMENTS_WORDING`.

`Messages` takes a message for someone, read back before it's passed on. `save(call, message)` gets a `Message` with the text, who it's from, a number to reach them, who it's for (one of `recipients`) and the call and account ids. Without a number, it offers the one they're calling from, read back for them to agree to. A second message for the same person while the first waits takes its place, so a caller can change what it says. The words are in `MESSAGES_WORDING`.

```python
from signalwire.operations import Appointments, Messages, ServiceAgent, Slot

OPEN = {"s1": "Tuesday at 2 pm", "s2": "Wednesday at 10 am"}
agent = ServiceAgent("dentist", role="You answer the phone for a dental practice.")
Appointments(
    openings=lambda call, when, kind: [Slot(i, label) for i, label in OPEN.items()],
    book=lambda call, slot, kind, note: OPEN.pop(slot.id),
    kinds=["cleaning", "check-up"],
    before_identity=True,
).add_to(agent)
Messages(save=lambda call, message: print(message), recipients={"Dr. Lee": "the dentist"}).add_to(agent)
```

## What the SDK Generates

- Steps: `identify` (with `identify`), `main`, `confirm`, a step per operation with `guidance`, each declared phase, and `transferred` (with `transfer_with`). Handlers move between them; the model never navigates. Every step but the last offers every operation tool and every lookup, so a caller who asks for something else is never stranded.
- The prompt's Role and Rules sections. The rules are `DEFAULT_RULES`, by key (`reply`, `facts`, `confirm`); `rules=` as a mapping changes them by key (a new key adds a rule, a key of theirs replaces it, None removes it), and as a list replaces them all.
- The call's record in `global_data` (see [The Call's Record](#the-calls-record)). The conscience is `${global_data.ops.now}`: where the call stands, on every request.
- `confirm_change` with its one gate, `decline_change`, and `transfer_to_human` gated on the caller asking for a person. A gate that refuses has the model answer in words before it calls a tool again (`back_to_back_functions(False)`, which lasts for the call), and every generated tool's result turns chaining back on (`"forever"`), so one refusal doesn't keep the model from chaining tools for the rest of the call.

`agent.preview()` prints each step's text and tools, as the model gets them. Overrides: `wording` (see [Words, Languages and the Medium](#words-languages-and-the-medium)), `confirm_gates`, `tool_fillers`, `gate_fillers`, `wrap` (middleware around every generated handler), `customize(contexts)` (the generated `ContextBuilder`, to change it), and `namespace` and `context` (see [Two Services on One Agent](#two-services-on-one-agent)).

## The Call's Record

The record is one `global_data` key, `ops` by default. Its `v` is `RECORD_VERSION`, which goes up when a key is renamed or changes meaning, never when one is added. These keys are for you to read, in prompts and SWML as `${global_data.ops.<key>}` and in your own code:

| Key | What it holds |
| --- | --- |
| `v` | The record's version |
| `account_id` | The account identified, or `""` |
| `account` | The account in a few words, as `describe` gives it |
| `asked` | What the caller asked for before they were identified |
| `medium` | `voice` or `chat`, found on the call's first request, or `""` |
| `history` | The changes settled: each one's `kind`, `touches`, `read_back`, `outcome` (`made`, `not made` with the backend's `reason`, `declined` or `replaced`), `done`, `money` (an exact decimal string) and `currency` |
| `now` | Where the call stands, in words, worked out again on every update |

`waiting`, `queued`, `proposals` and `state` are the service's own. Read your own state through `call.state`.

## Words, Languages and the Medium

Every string the service generates comes from a key in `DEFAULT_WORDING`: the steps' text, the tools' descriptions, tool results and prompts, the gates, the transfer notice and the record's `now` line. `wording=` replaces any of them. A `{name}` in a template is a placeholder; an override may leave placeholders out but not add any, and an unknown key or placeholder fails when the service is made. A platform variable such as `${global_data.today}` is kept as written.

```python
from signalwire.operations import Operations

ops = Operations(
    role="Atiendes el teléfono de una tienda. Hablas siempre en español.",
    wording={"transfer.notice": "Un momento, le paso con una persona."},
)
```

The model answers in the language its role asks for. The other words are instructions to the model, so English ones work in any language; the transfer notice is the one the platform speaks word for word. Fillers given as a plain list are for every language; give lists by language code for more than one.

The service doesn't assume a phone call. `medium="voice"` or `medium="chat"` is for a service that only takes calls, or only chats: the `reply` rule starts with it ("This is a phone call."). Without one, each call's medium is found on its first request, from the platform's `conversation_type`, kept in the record as `medium`, and stated at the head of `now`. `call.medium` gives it to your operations. `ServiceAgent` finds it on every SWML request; an agent configured per request gets it from `ops.prefilled(request_data)`, as global data.

## Games, Kiosks and Screens

`confirm = False` on an operation makes it a change that goes through when it's called, with no read-back, such as a move in a game. `phase(name, text, tools)` declares a step of your own; a tool moves to it with `call.go(name)`. `call.state` is your own state for the call, kept in `global_data`, and `call.show(event)` sends an event to the caller's screen with the tool's result.

```python
from signalwire.operations import Change, Field, Operation, ServiceAgent
from signalwire.testing import CallSimulator

agent = ServiceAgent("dealer", role="You deal cards.")


@agent.operation(tool="place_bet")
class Bet(Operation):
    """Place a bet and deal."""

    amount = Field(int, "The bet, in chips.")
    confirm = False

    def prepare(self, call, f):
        call.state["bet"] = f.amount
        call.show({"type": "deal", "cards": [10, 7]})
        call.go("playing")
        return Change(read_back="", done=f"Bet {f.amount}. You have 17.")


agent.phase("betting", "Ask how much they'd like to bet, and call place_bet.", ["place_bet"], initial=True)
agent.phase("playing", "They're playing their hand.", [])

call = CallSimulator(agent)
out = call.call("place_bet", {"amount": 10, "data_supplied_by_user": True})
assert out.response == "Done. Bet 10. You have 17." and call.step == "playing"
```

## Installing on Your Own Agent

`ServiceAgent` is a prefab over `Operations`, which installs on any `AgentBase`, for an agent configured per request or one that already has its own setup. `ServiceAgent` takes every `Operations` keyword argument, such as `rules`, `wording`, `currency` and `namespace`.

```python
from signalwire import AgentBase
from signalwire.operations import Operations

ops = Operations(role="You answer the phone for an online store.")
agent = AgentBase(name="store", route="/store")
ops.install(agent)
```

`install` adds to what the agent has, and replaces none of it: a Role or Rules section it has already gets the service's text after its own (a rule it has isn't repeated), a step that exists keeps its text and tools, an initial step it chose stands, and the conscience gets the service's line appended. Other layers can install on the same agent, before or after. A tool name the agent has already fails the install, before anything is changed. Tools the service didn't make, such as a skill's or another layer's, go into its steps with `offer(*tools)`: every generated step but `identify` and `confirm` by default, `identify` as well with `before_identity=True`, or exactly the steps named with `steps=[...]`.

For an agent configured per request, apply `ops.prefilled(request_data)` to the request's copy as global data, so the call starts with its medium and, with `identify`'s `prefill`, identified. `ServiceAgent` does this itself, with or without a per-request callback.

## Two Services on One Agent

`namespace=` names everything a service generates, so it can sit beside another service, or beside tools and steps of the same names: with `namespace="billing"` the tools are `confirm_billing_change`, `decline_billing_change`, `billing_transfer_to_human` and `billing_find_account`, the steps `billing_identify`, `billing_main` and `billing_confirm`, the transfer's context `billing_transferred`, and the record `global_data.billing`. `call.go("main")` and `offer(steps=["main"])` still name the generated steps as generated. `context=` puts the steps in a context other than `default`.

Each service's steps offer its own tools. To let a caller reach both from either, offer each one's tools in the other's steps:

```python
from signalwire import AgentBase
from signalwire.operations import Operations

billing = Operations(role="You handle billing.", namespace="billing")
orders = Operations(role="You handle orders.", namespace="orders")
# ... each service's operations, registered with billing.operation and orders.operation ...
billing.offer("confirm_orders_change", "decline_orders_change", steps=["main", "confirm"])
orders.offer("confirm_billing_change", "decline_billing_change", steps=["main", "confirm"])
agent = AgentBase(name="front", route="/front")
billing.install(agent)
orders.install(agent)
```

Each service keeps its own changes and record. The caller's yes is judged against the latest read-back, whichever service made it, so a yes heard for the other service's read-back reads this one's back again rather than carrying it out.

## InfoBot: Answering From a Corpus

`signalwire.operations.infobot` is the half of an operations agent that answers rather than changes.

`InfoBotKnowledge(search=fn)` adds a search tool, `search_knowledge`, that hands the model one grounded block of results. `search(query)` returns the raw results, each a dict with a `content` string and a `score`, and may be `async`; `use_search_service(url)` uses a SignalWire search service instead. The policy is yours, in hooks: `set_exclude`, `set_demote`, `set_authority`, `set_result_context`, `set_query_transform`, `set_fallback`, `set_expander`, `add_rule` and `add_result_rule`, and `add_query_type` for a `query_type` argument. With `contact=fn`, a second tool records the caller's details for a human follow-up: `contact_fields=` sets what it takes, and `contact_any_of=` which fields are enough, such as `[["email"], ["phone"]]`. Its words are in `KNOWLEDGE_WORDING`, and `wording=` replaces them. It installs in the `main` step (`step=` and `context=` choose another), before or after `Operations`, and the step keeps every layer's text and tools.

```python
from signalwire import AgentBase
from signalwire.operations.infobot import InfoBotKnowledge

docs = [{"content": "We open at 9 and close at 5.", "score": 0.9}]
agent = AgentBase(name="help", route="/help")
InfoBotKnowledge(search=lambda query: docs).install(agent)
```

`Continuity().install(agent)` carries a conversation across a switch between voice and chat. Each leg's transcript and medium are kept in a `LegStore` at the leg's end, and the next leg starts seeded with them (`build_seed`): a user turn recording the switch (`switch_turn`) and a note not to answer again what was handled (`switch_note`). It works through the agent's per-request callback, after the agent's own, so set that first. The default store is one JSON file per conversation on this host, for development; `store.set_store(load=..., append=...)` puts it in your database. `say_into_call(call_id, text)` speaks on a live call from elsewhere, through the REST API.

## Testing

`signalwire.testing.CallSimulator` runs an operations agent offline: tool calls, the steps they move to, the gates (every gate passes unless you answer it) and the record in `call.global_data`. The examples above are tests of that kind.
