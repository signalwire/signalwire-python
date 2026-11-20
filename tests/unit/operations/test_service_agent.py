"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

ServiceAgent end to end through the CallSimulator: a small shop with an
account lookup, cancel, return, exchange and address operations.
"""

from __future__ import annotations

from typing import Any, Literal

import pytest

from signalwire.operations import (
    Change,
    Field,
    Need,
    Operation,
    Refuse,
    ServiceAgent,
    Write,
    WriteFailed,
)
from signalwire.testing import CallSimulator

ORDERS: dict[str, dict[str, Any]] = {}
WRITES: list[tuple[str, dict[str, Any]]] = []
FAIL_ON: set[str] = set()
FAIL_IDS: set[str] = set()
KEYS: list[str] = []


def fresh_orders() -> None:
    ORDERS.clear()
    ORDERS.update(
        {
            "#W1": {"status": "pending", "items": {"a": 10.0, "b": 20.0}, "paid": "card"},
            "#W2": {"status": "pending", "items": {"c": 5.0}, "paid": "card"},
            "#W3": {"status": "delivered", "items": {"d": 30.0, "e": 40.0}, "paid": "card"},
        }
    )
    WRITES.clear()
    FAIL_ON.clear()
    FAIL_IDS.clear()
    KEYS.clear()


def write(call: Any, w: Write) -> None:
    KEYS.append(call.write_key)
    if w.name in FAIL_ON or w.args.get("order_id") in FAIL_IDS:
        raise WriteFailed(f"{w.name} was refused")
    WRITES.append((w.name, dict(w.args)))


def build_agent() -> ServiceAgent:
    agent = ServiceAgent("shop", role="You answer the phone for a small shop.", currency="USD")
    agent.identify(
        any_of=[["email"], ["name", "zip"]],
        find=lambda call, keys: "u1" if keys.get("email") == "a@b.c" or keys.get("zip") == "12345" else _no_account(),
        describe=lambda call: "Ann, orders #W1 #W2 #W3",
    )
    agent.writes_with(write)
    agent.transfer_with(lambda call, summary: None)

    @agent.lookup("An order's items and status.", fields={"order_id": Field(str, "The order's id.")})
    def order_details(call: Any, order_id: str | None) -> str:
        order = ORDERS.get(order_id or "")
        if order is None:
            raise Refuse(f"{order_id} isn't one of their orders.")
        return f"{order_id}: {order['status']}, items {', '.join(order['items'])}."

    @agent.operation(tool="cancel_order")
    class Cancel(Operation):
        """Cancel pending orders."""

        order_ids = Field(list[str], "The orders to cancel.")
        reason = Field(Literal["no longer needed", "ordered by mistake"], "Why.", ask="Why are they cancelling?")
        combine = ("reason",)

        def prepare(self, call: Any, f: Any) -> Change:
            orders = [(o, ORDERS[o]) for o in f.order_ids if o in ORDERS]
            if late := [o for o, order in orders if order["status"] != "pending"]:
                raise Refuse(f"{', '.join(late)} can't be cancelled: only pending orders can.")
            refund = [sum(order["items"].values()) for _, order in orders]
            return Change(
                read_back=f"Cancel {' and '.join(o for o, _ in orders)}, refunding ${sum(refund):.2f}. Shall I go ahead?",
                touches=[f"order:{o}" for o, _ in orders],
                writes=[Write("cancel", order_id=o, reason=f.reason) for o, _ in orders],
                money=[-r for r in refund],
                done=[f"{o} is cancelled." for o, _ in orders],
            )

    def delivered(order_id: str) -> dict[str, Any]:
        order = ORDERS.get(order_id)
        if not order or order["status"] != "delivered":
            raise Refuse(f"{order_id} isn't a delivered order.")
        return order

    @agent.operation(tool="return_items")
    class Return(Operation):
        """Return items of a delivered order."""

        order_id = Field(str, "The delivered order.")
        items = Field(list[str], "The items to return.")
        refund_to = Field(str, "Where the refund goes.", ask="Should the refund go to the card or a gift card?")
        combine = ("refund_to",)

        def prepare(self, call: Any, f: Any) -> Change:
            order = delivered(f.order_id)
            refund = sum(order["items"][i] for i in f.items)
            return Change(
                read_back=f"Return {', '.join(f.items)} from {f.order_id}, ${refund:.2f} to {f.refund_to}. Shall I?",
                touches=[f"order:{f.order_id}", *[f"item:{i}" for i in f.items]],
                writes=[Write("return", order_id=f.order_id, items=list(f.items), to=f.refund_to)],
                money=[-refund],
                done=f"The return of {', '.join(f.items)} is requested.",
            )

        def conflicts_with(self, other: str, mine: Change, theirs: Change) -> str | None:
            if other == "exchange" and mine.touches[0] in theirs.touches:
                return "a delivered order takes one return or one exchange, not both"
            return None

        def without(self, args: Any, gone: set[str]) -> dict[str, Any] | None:
            items = [i for i in args.get("items") or [] if f"item:{i}" not in gone]
            return {**args, "items": items} if items else None

    @agent.operation(tool="exchange_items")
    class Exchange(Operation):
        """Exchange items of a delivered order for other options."""

        order_id = Field(str, "The delivered order.")
        items = Field(list[str], "The items to exchange.")

        def prepare(self, call: Any, f: Any) -> Change:
            delivered(f.order_id)
            return Change(
                read_back=f"Exchange {', '.join(f.items)} in {f.order_id}. Shall I?",
                touches=[f"order:{f.order_id}", *[f"item:{i}" for i in f.items]],
                writes=[Write("exchange", order_id=f.order_id, items=list(f.items))],
            )

    @agent.operation(tool="change_address")
    class Address(Operation):
        """Change where pending orders ship."""

        order_ids = Field(list[str], "The pending orders.")
        address = Field(str, "The new address.")
        goes_before = ("cancel",)

        def without(self, args: Any, gone: set[str]) -> dict[str, Any] | None:
            left = [o for o in args.get("order_ids") or [] if f"order:{o}" not in gone]
            return {**args, "order_ids": left} if left else None

        def prepare(self, call: Any, f: Any) -> Change:
            return Change(
                read_back=f"Ship {' and '.join(f.order_ids)} to {f.address}. Shall I?",
                touches=[f"order:{o}" for o in f.order_ids],
                writes=[Write("address", order_id=o, address=f.address) for o in f.order_ids],
            )

    return agent


def _no_account() -> str:
    raise Refuse("No account was found with that.", "Ask them to spell it.")


@pytest.fixture
def sim() -> CallSimulator:
    fresh_orders()
    s = CallSimulator(build_agent())
    s.caller("Hi, it's ann, a@b.c")
    found = s.call("find_account", {"email": "a@b.c", "asked_for": "cancel an order", "data_supplied_by_user": True})
    assert found.ran and "Found their account" in found.response
    assert s.step == "main"
    return s


def said(args: dict[str, Any]) -> dict[str, Any]:
    return {**args, "data_supplied_by_user": True}


def test_generated_steps_and_tools() -> None:
    agent = build_agent()
    text = agent.preview()
    assert "== default/identify" in text and "== default/main" in text and "== default/confirm" in text
    assert "cancel_order (Cancel pending orders)" in text
    s = CallSimulator(agent)
    assert s.step == "identify"
    assert set(s.offered()) == {"find_account", "transfer_to_human"}
    assert s.global_data["ops"]["now"] == ""


def test_account_needed_first() -> None:
    fresh_orders()
    s = CallSimulator(build_agent())
    miss = s.call("find_account", {"email": "x@y.z", "asked_for": "", "data_supplied_by_user": True})
    assert "No account was found" in miss.response
    partial = s.call("find_account", {"name": "Ann", "asked_for": "", "data_supplied_by_user": True})
    assert "it takes their email, or their name and zip" in partial.response


def test_cancel_read_back_yes_and_record(sim: CallSimulator) -> None:
    proposed = sim.call("cancel_order", said({"order_ids": ["#W1"], "reason": "no longer needed"}))
    assert proposed.ran and sim.step == "confirm"
    assert sim.global_data["ops"]["waiting"]["read_back"].startswith("Cancel #W1, refunding $30.00")
    assert "Waiting for their answer" in sim.global_data["ops"]["now"]
    sim.caller("yes")
    done = sim.call("confirm_change", {"change": "cancel"})
    assert done.ran and done.response.startswith("Done. #W1 is cancelled.")
    assert WRITES == [("cancel", {"order_id": "#W1", "reason": "no longer needed"})]
    assert sim.step == "main"
    assert sim.global_data["ops"]["history"][-1]["outcome"] == "made"
    assert sim.global_data["ops"]["history"][-1]["money"] == "-30.0"
    assert sim.global_data["ops"]["history"][-1]["currency"] == "USD"


def test_missing_reason_is_asked_not_guessed(sim: CallSimulator) -> None:
    asked = sim.call("cancel_order", said({"order_ids": ["#W1"], "reason": "not said"}))
    assert "Why are they cancelling?" in (asked.tool_prompt or "")
    assert sim.step == "main" and not sim.global_data["ops"]["waiting"]


def test_refused_by_rule(sim: CallSimulator) -> None:
    refused = sim.call("cancel_order", said({"order_ids": ["#W3"], "reason": "no longer needed"}))
    assert refused.response == "Nothing is changed: #W3 can't be cancelled: only pending orders can."


def test_vouched(sim: CallSimulator) -> None:
    out = sim.call("cancel_order", {"order_ids": ["#W1"], "reason": "no longer needed", "data_supplied_by_user": False})
    assert not out.ran or "Get the answer" in (out.tool_prompt or "")


def test_as_well_asked_then_merged(sim: CallSimulator) -> None:
    sim.call("cancel_order", said({"order_ids": ["#W1"], "reason": "no longer needed"}))
    asked = sim.call("cancel_order", said({"order_ids": ["#W1", "#W2"], "reason": "no longer needed"}))
    assert "as_well" in (asked.tool_prompt or "")
    merged = sim.call("cancel_order", said({"order_ids": ["#W2"], "reason": "no longer needed", "as_well": True}))
    assert "added to the cancel change" in merged.response
    assert sim.global_data["ops"]["waiting"]["read_back"].startswith("Cancel #W1 and #W2, refunding $35.00")
    assert sim.global_data["ops"]["history"][-1]["outcome"] == "replaced"


def test_narrowing_replaces_without_asking(sim: CallSimulator) -> None:
    sim.call("cancel_order", said({"order_ids": ["#W1", "#W2"], "reason": "no longer needed"}))
    narrowed = sim.call("cancel_order", said({"order_ids": ["#W2"], "reason": "no longer needed"}))
    assert narrowed.ran and "takes the place" in narrowed.response
    assert sim.global_data["ops"]["waiting"]["read_back"].startswith("Cancel #W2,")


def test_conflict_takes_over_and_rest_is_kept(sim: CallSimulator) -> None:
    sim.call("return_items", said({"order_id": "#W3", "items": ["d", "e"], "refund_to": "card"}))
    swapped = sim.call("exchange_items", said({"order_id": "#W3", "items": ["d"], "as_well": False}))
    assert "takes the place of the return change" in swapped.response
    assert sim.global_data["ops"]["waiting"]["kind"] == "exchange"
    assert sim.global_data["ops"]["queued"][0]["read_back"].startswith("Return e from #W3")


def test_conflict_as_well_is_refused(sim: CallSimulator) -> None:
    sim.call("return_items", said({"order_id": "#W3", "items": ["d"], "refund_to": "card"}))
    both = sim.call("exchange_items", said({"order_id": "#W3", "items": ["e"], "as_well": True}))
    assert "can't have both" in both.response
    assert sim.global_data["ops"]["waiting"]["kind"] == "return"


def test_unrelated_request_reads_now_and_sets_waiting_aside(sim: CallSimulator) -> None:
    sim.call("cancel_order", said({"order_ids": ["#W1"], "reason": "no longer needed"}))
    other = sim.call("return_items", said({"order_id": "#W3", "items": ["d"], "refund_to": "card"}))
    assert "kept for after this one" in other.response
    assert sim.global_data["ops"]["waiting"]["kind"] == "return"
    sim.caller("yes")
    done = sim.call("confirm_change", {"change": "return"})
    assert 'call cancel_order again for the change set aside: "Cancel #W1' in (done.tool_prompt or "")


def test_goes_before_keeps_waiting_first(sim: CallSimulator) -> None:
    sim.call("change_address", said({"order_ids": ["#W1"], "address": "1 Main St"}))
    later = sim.call("cancel_order", said({"order_ids": ["#W1"], "reason": "no longer needed"}))
    assert "Kept for right after the change waiting" in later.response
    assert sim.global_data["ops"]["waiting"]["kind"] == "address"
    assert sim.global_data["ops"]["queued"][0]["kind"] == "cancel"


def test_confirm_names_the_waiting_change(sim: CallSimulator) -> None:
    sim.call("cancel_order", said({"order_ids": ["#W1"], "reason": "no longer needed"}))
    wrong = sim.call("confirm_change", {"change": "return"})
    assert "the change waiting for their answer is the cancel change" in wrong.response
    assert WRITES == []


def test_decline(sim: CallSimulator) -> None:
    sim.call("cancel_order", said({"order_ids": ["#W1"], "reason": "no longer needed"}))
    no = sim.call("decline_change", {"change": "cancel"})
    assert no.ran and "left as it was" in (no.tool_prompt or "")
    assert sim.global_data["ops"]["history"][-1]["outcome"] == "declined" and not sim.global_data["ops"]["waiting"]
    assert sim.step == "main"


def test_partial_failure_counts_only_what_went_through(sim: CallSimulator) -> None:
    FAIL_ON.add("cancel")
    sim.call("cancel_order", said({"order_ids": ["#W1"], "reason": "no longer needed"}))
    sim.caller("yes")
    out = sim.call("confirm_change", {"change": "cancel"})
    assert out.response.startswith("The change didn't go through: cancel was refused.")
    last = sim.global_data["ops"]["history"][-1]
    assert last["money"] == "0"
    assert (last["outcome"], last["reason"]) == ("not made", "cancel was refused"), "a code, and the reason apart"


def test_totals_after_two_changes(sim: CallSimulator) -> None:
    sim.call("cancel_order", said({"order_ids": ["#W1"], "reason": "no longer needed"}))
    sim.caller("yes")
    sim.call("confirm_change", {"change": "cancel"})
    sim.call("return_items", said({"order_id": "#W3", "items": ["d"], "refund_to": "card"}))
    sim.caller("yes")
    out = sim.call("confirm_change", {"change": "return"})
    assert "In all, the changes made in this call come to $60.00 back to them." in out.response


def test_need_before_account_is_refused() -> None:
    fresh_orders()
    s = CallSimulator(build_agent())
    s._enter_step("main")  # as if a step moved without identity
    out = s.call("cancel_order", said({"order_ids": ["#W1"], "reason": "no longer needed"}))
    assert "Their account isn't found yet." in out.response


def test_lookup_refusal(sim: CallSimulator) -> None:
    out = sim.call("order_details", {"order_id": "#W9"})
    assert out.response == "#W9 isn't one of their orders."


def test_as_well_within_the_waiting_change_keeps_all_of_it(sim: CallSimulator) -> None:
    """"the d as well, keep the e" must not drop e."""
    sim.call("return_items", said({"order_id": "#W3", "items": ["d", "e"], "refund_to": "card"}))
    sim.call("return_items", said({"order_id": "#W3", "items": ["d"], "refund_to": "card", "as_well": True}))
    waiting = sim.global_data["ops"]["waiting"]["read_back"]
    assert "d" in waiting.split("Return ")[1].split(" from")[0] and "e" in waiting.split("Return ")[1].split(" from")[0]


def test_read_back_state_goes_before_its_say(sim: CallSimulator) -> None:
    """a say the caller talks over skips the rest of its object, so the state goes first."""
    out = sim.call("cancel_order", said({"order_ids": ["#W1"], "reason": "no longer needed"}))
    says = [i for i, a in enumerate(out.actions) if "say" in a]
    states = [i for i, a in enumerate(out.actions) if "semantic_state" in (a.get("set_global_data") or {})]
    assert says and states and states[0] < says[0]
    assert all("set_global_data" not in out.actions[i] for i in says)


def test_write_keys_are_unique_across_changes(sim: CallSimulator) -> None:
    """two changes in one call must not share a write key."""
    for order in ("#W1", "#W2"):
        sim.call("cancel_order", said({"order_ids": [order], "reason": "no longer needed"}))
        sim.caller("yes")
        sim.call("confirm_change", {"change": "cancel"})
    assert len(KEYS) == 2 and len(set(KEYS)) == 2


def test_a_change_set_aside_gives_way_to_a_newer_one(sim: CallSimulator) -> None:
    """an address set aside for A and B, then A to another address: the set-aside one keeps only B."""
    sim.call("change_address", said({"order_ids": ["#W1", "#W2"], "address": "1 Main St"}))
    sim.call("return_items", said({"order_id": "#W3", "items": ["d"], "refund_to": "card"}))
    assert sim.global_data["ops"]["queued"][0]["read_back"].startswith("Ship #W1 and #W2 to 1 Main St")
    out = sim.call("change_address", said({"order_ids": ["#W1"], "address": "2 Oak St"}))
    assert "set aside for later is now only this" in out.response
    queued = [q for q in sim.global_data["ops"]["queued"] if q["kind"] == "address"]
    assert [q["read_back"] for q in queued] == ["Ship #W2 to 1 Main St. Shall I?"]


def test_partial_failure_with_one_done_line_still_says_what_went_through() -> None:
    """done given once for the whole change, the second write fails: the first is still reported."""
    fresh_orders()
    agent = ServiceAgent("shop2", role="r")
    agent.writes_with(write)

    @agent.operation(tool="cancel_order")
    class Cancel(Operation):
        """Cancel pending orders."""

        order_ids = Field(list[str], "The orders.")

        def prepare(self, call: Any, f: Any) -> Change:
            return Change(read_back=f"Cancel {' and '.join(f.order_ids)}. Shall I?", touches=list(f.order_ids),
                          writes=[Write("cancel", order_id=o) for o in f.order_ids], done="Both are cancelled.")

    s = CallSimulator(agent)
    s.call("cancel_order", said({"order_ids": ["#W1", "#W2"]}))
    FAIL_IDS.add("#W2")
    s.caller("yes")
    out = s.call("confirm_change", {"change": "cancel"})
    assert "What went through first: cancel (order_id #W1)." in out.response
    assert s.global_data["ops"]["history"][-1]["writes_made"] == [{"name": "cancel", "args": {"order_id": "#W1"}}]


def test_a_yes_to_an_earlier_read_back_writes_nothing(sim: CallSimulator) -> None:
    """The gate judged a yes against semantic_state; if that isn't the change waiting, it's read again, not made."""
    sim.call("cancel_order", said({"order_ids": ["#W1"], "reason": "no longer needed"}))
    sim.global_data["semantic_state"] = {"proposal": "Cancel #W2. Shall I?", "revision": 1}
    sim.caller("yes")
    out = sim.call("confirm_change", {"change": "cancel"})
    assert "their yes was to an earlier read-back" in out.response and WRITES == []
    assert sim.global_data["semantic_state"]["proposal"] == sim.global_data["ops"]["waiting"]["read_back"]
