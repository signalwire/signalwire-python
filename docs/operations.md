# Operations

An operations agent is written as what it can do for a caller. You write each operation once, for any caller: its fields, its rules and its writes. The SDK runs everything else the same way for every operation: finding the caller's account, reading each change back, taking the caller's yes, carrying the change out, and keeping the call's record. The helpers are in `signalwire.operations`.

## Table of Contents

- [A Store in One Page](#a-store-in-one-page)
- [Operations](#operations)
- [The Change Lifecycle](#the-change-lifecycle)
- [A Request While a Change Waits](#a-request-while-a-change-waits)
- [Identifying the Caller](#identifying-the-caller)
- [Lookups](#lookups)
- [What the SDK Generates](#what-the-sdk-generates)
- [Games, Kiosks and Screens](#games-kiosks-and-screens)
- [Installing on Your Own Agent](#installing-on-your-own-agent)
- [Testing](#testing)

## A Store in One Page

```python
from typing import Literal

from signalwire.operations import Change, Field, Operation, Refuse, ServiceAgent, Write
from signalwire.testing import CallSimulator

ORDERS = {"#W1": {"status": "pending", "total": 54.04}, "#W2": {"status": "delivered", "total": 20.00}}
WRITES = []

agent = ServiceAgent("store", role="You answer the phone for an online store. You are warm, brief and plain-spoken.")
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

A `Change` carries `read_back` (the words the caller says yes to: put the change itself in the first clause), `touches` (stable keys for what it acts on, such as `order:#W1`), `writes` (the backend writes, kept as data), `money` (what each write moves) and `done` (what to tell the caller once each write went through).

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
7. A change set aside for after this one is offered next.

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

## What the SDK Generates

- Steps: `identify` (with `identify`), `main`, `confirm`, a step per operation with `guidance`, each declared phase, and `transferred` (with `transfer_with`). Handlers move between them; the model never navigates. Every step but the last offers every operation tool and every lookup, so a caller who asks for something else is never stranded.
- The prompt's Role and Rules sections.
- The call's record in `global_data`: `account_id`, `account`, `asked`, `waiting`, `queued`, `history`, `proposals` and `now`. The conscience is `${global_data.now}`: where the call stands, on every request.
- `confirm_change` with its one gate, `decline_change`, and `transfer_to_human` gated on the caller asking for a person.

`agent.preview()` prints each step's text and tools, as the model gets them. Overrides: `step_text`, `confirm_gates`, `tool_fillers`, `gate_fillers`, `wrap` (middleware around every generated handler) and `customize(contexts)` (the generated `ContextBuilder`, to change it).

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

`ServiceAgent` is a prefab over `Operations`, which installs on any `AgentBase`, for an agent configured per request or one that already has its own setup:

```python
from signalwire import AgentBase
from signalwire.operations import Operations

ops = Operations(role="You answer the phone for an online store.")
agent = AgentBase(name="store", route="/store")
ops.install(agent)
```

Other layers can install on the same agent, before or after: a step that exists already is added to, never replaced. Tools the service didn't make, such as a skill's or another layer's, go into its steps with `offer(*tools)`: every generated step but `identify` and `confirm` by default, `identify` as well with `before_identity=True`, or exactly the steps named with `steps=[...]`.

## Testing

`signalwire.testing.CallSimulator` runs an operations agent offline: tool calls, the steps they move to, the gates (every gate passes unless you answer it) and the record in `call.global_data`. The examples above are tests of that kind.
