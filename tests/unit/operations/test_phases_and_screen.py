"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Phases, screen events, per-call state and changes with no read-back: a card
game in the shape of the blackjack demo, and an info-only bot.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from signalwire.operations import Change, Field, Operation, Refuse, ServiceAgent, Write
from signalwire.testing import CallSimulator

DECK = [10, 7, 5, 9]


def game() -> ServiceAgent:
    agent = ServiceAgent("dealer", role="You deal blackjack.")
    agent.writes_with(lambda call, w: None)

    @agent.operation(tool="place_bet")
    class Bet(Operation):
        """Place a bet and deal."""

        amount = Field(int, "The bet, in chips.")
        confirm = False

        def prepare(self, call: Any, f: Any) -> Change:
            if f.amount > call.state.get("chips", 100):
                raise Refuse("That's more chips than they have.")
            call.state.update(bet=f.amount, hand=[DECK[0], DECK[1]], chips=call.state.get("chips", 100))
            call.show({"type": "deal", "hand": call.state["hand"]})
            call.go("playing")
            return Change(read_back="", writes=[Write("bet", amount=f.amount)], done=f"Bet {f.amount}; dealt 10 and 7.")

    @agent.operation(tool="hit")
    class Hit(Operation):
        """Take another card."""

        confirm = False

        def prepare(self, call: Any, f: Any) -> Change:
            hand = call.state.get("hand") or []
            if not hand:
                raise Refuse("No hand is in play.")
            hand.append(DECK[len(hand)])
            call.state["hand"] = hand
            call.show({"type": "card", "card": hand[-1]})
            if sum(hand) > 21:
                call.go("betting")
                return Change(read_back="", done=f"Drew {hand[-1]}: bust at {sum(hand)}.")
            return Change(read_back="", done=f"Drew {hand[-1]}: {sum(hand)}.")

    agent.phase("betting", "Ask how much they'd like to bet, and call place_bet.", ["place_bet"], initial=True)
    agent.phase("playing", "They can hit or stand. Call hit when they want a card.", ["hit"])
    return agent


def events(out: Any) -> list[dict[str, Any]]:
    found = []
    for action in out.actions:
        swml = action.get("SWML") if isinstance(action, dict) else None
        if swml:
            text = json.dumps(swml)
            if "user_event" in text:
                found.append(swml)
    return found


def said(args: dict[str, Any]) -> dict[str, Any]:
    return {**args, "data_supplied_by_user": True}


def test_phases_state_screen_and_no_read_back() -> None:
    sim = CallSimulator(game())
    assert sim.step == "betting"
    assert sim.offered() == ["place_bet"]
    bet = sim.call("place_bet", said({"amount": 10}))
    assert bet.ran and bet.response == "Done. Bet 10; dealt 10 and 7."
    assert sim.step == "playing"
    assert sim.global_data["state"]["hand"] == [10, 7]
    assert len(events(bet)) == 1
    assert sim.global_data["history"][-1]["outcome"] == "made"
    first = [next(iter(a)) for a in bet.actions]
    assert first.index("set_global_data") < first.index("change_step"), "the tool's state goes ahead of its step"
    hit = sim.call("hit", said({}))
    assert hit.response == "Done. Drew 5: bust at 22." and sim.step == "betting"


def test_refusal_keeps_phase() -> None:
    sim = CallSimulator(game())
    out = sim.call("place_bet", said({"amount": 500}))
    assert out.response == "Nothing is changed: That's more chips than they have."
    assert sim.step == "betting" and "hand" not in sim.global_data.get("state", {})


def test_unknown_phase_tool_is_an_error() -> None:
    agent = ServiceAgent("x", role="r")
    agent.phase("p", "text", ["nope"])
    with pytest.raises(ValueError, match="nope"):
        agent.compile()


def test_info_only_bot_has_one_step() -> None:
    agent = ServiceAgent("info", role="You answer questions about the shop.")

    @agent.lookup("Opening hours for a day.", fields={"day": Field(str, "The day.")})
    def hours(call: Any, day: str | None) -> str:
        call.show({"type": "hours", "day": day})
        return f"{day}: 9 to 5."

    sim = CallSimulator(agent)
    assert sim.step == "main" and sim.offered() == ["hours"]
    out = sim.call("hours", {"day": "Monday"})
    assert out.response == "Monday: 9 to 5." and len(events(out)) == 1
    assert "confirm" not in agent.preview()
