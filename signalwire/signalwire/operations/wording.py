"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The words an operations agent generates: its steps, tool descriptions, tool
results and prompts, gates, the transfer notice and the call's record. Each
has a key in ``DEFAULT_WORDING``; ``Operations(wording={...})`` replaces any
of them.

A ``{name}`` in a template is a placeholder, filled in when the words are
used. An override may leave out placeholders, but not add ones its default
doesn't have. Anything else is kept as it is written, including the
platform's ``${...}`` variables.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from types import MappingProxyType

_PLACEHOLDER = re.compile(r"(?<!\$)\{([a-z_]+)\}")

DEFAULT_WORDING: Mapping[str, str] = MappingProxyType(
    {
        # The medium, at the head of the record's ``now`` line once it's known
        "medium.voice": "This is a phone call.",
        "medium.chat": "This is a chat.",
        # Lists in running text
        "list.and": " and ",
        "list.or": " or ",
        "list.comma": ", ",
        # Steps
        "step.account": "Their account: {account}\n\n",
        "step.identify": "Ask for {ask}, and call {tool} with what they say. Nothing about an account can be "
        "shared or changed until it's found.{early}{transfer}",
        "step.identify.early": " For {lookups}, they needn't be identified.",
        "step.main": "{account}Help with what they ask, all of it. {help}",
        "step.confirm": "{account}A change was just read to them and waits for their answer. When they say yes, "
        "call {confirm}. If they want it different, call its tool again with what they want. If they don't want "
        "it, call {decline}. If they ask for another change as well, call its tool: the tool says which comes "
        "first, and nothing asked for is lost.{transfer}",
        "step.guidance": "{account}{guidance} When you have what it needs, call {tool}. {help}",
        "step.transferred": "The caller is being transferred. Say nothing more.",
        "step.more": "What else you can do",
        "step.lookups": "To look something up, call {lookups}. ",
        "step.operations": "To make a change, call its tool with everything the caller asked for: {operations}. "
        "The tool checks it and reads it back to them. ",
        "step.cannot": "If they ask for something these tools can't do, tell them so and what can be done instead.",
        "step.unfound": " If their account isn't found yet and they want something that needs it, ask for {ask} "
        "and call {tool}.",
        "step.transfer": " If they ask for a person, call {tool}.",
        "step.transfer.destinations": " To reach {destinations}, call {tool} with where they want to go.",
        # Tools and their arguments, as the model reads them
        "tool.identify": "Find the caller's account by {ask}.",
        "tool.identify.asked_for": "Everything the caller has asked for so far in this call, in their words.",
        "tool.identify.key": "Their {key}, as they said it.",
        "tool.lookup": "{description} Changes nothing.",
        "tool.operation": "{description}",
        "tool.operation.read_back": "{description} Reads it back first.",
        "tool.as_well": "Only while a change waits for their answer: true if they want this as well as it, false "
        "if in place of it. Leave it out if no change is waiting.",
        "tool.change": "What the change read back is.",
        "tool.confirm": "Make the change just read back, once the caller has said yes to it.",
        "tool.decline": "Leave the change just read back unmade, when the caller says they don't want it.",
        "tool.transfer": "Transfer the caller to a person, when they ask for one or say yes to being transferred.",
        "tool.transfer.destinations": "Transfer the caller where they ask to go.",
        "tool.transfer.summary": "What they need, in a sentence.",
        "tool.transfer.to": "Where they want to go: {destinations}",
        # How the identify keys are asked for: "their email, or their name and zip"
        "identify.keys": "their {keys}",
        "identify.or": ", or ",
        # Gates
        "gate.confirm": "Has the caller said yes, in `conversation`, to the change described in `semantic_state`? "
        'A yes counts however short it is ("okay", "sure", "that\'s right", "go ahead"), even if they said it '
        "while the agent was still asking, before the whole change was read, even if it comes with a request "
        "for something else as well, and whatever the agent has said since. It doesn't count if they asked for "
        "this change itself to be different, or for only part of it.",
        "gate.confirm.true": "They said yes to this change as it is, in any words, at any point while it was "
        "being asked or after, even with a request for something else as well.",
        "gate.confirm.false": "They said no, hesitated, only made a listening sound, only asked a question, asked "
        "for something else with no yes, asked for this change to be different, or haven't spoken since the "
        "change was asked.",
        "gate.confirm.refused": "{tool} was not run. The caller has not said yes to this change.",
        "gate.confirm.refused.then": 'Read it back, "{read_back}", and ask for a plain yes or no, or call {decline} '
        "if they no longer want it.",
        "gate.transfer": "In their latest turns in `conversation`, has the caller asked to speak with a person, or "
        "said yes when the agent offered to transfer them to one?",
        "gate.transfer.true": "They asked for a person, a human, a representative or a supervisor, or said yes to "
        "being transferred to one.",
        "gate.transfer.false": "They haven't asked for a person or said yes to being transferred.",
        "gate.transfer.refused": "Not transferred: the caller hasn't asked for a person.",
        "gate.transfer.refused.then": "Carry on helping them.",
        # What the model is told to do next, after a tool
        "then.going_on": "Tell them, and ask how they'd like to go on.",
        "then.ask": "Ask them: {ask}",
        "then.read_back": "Wait for the caller's answer. Call {confirm} only when they say yes to this read-back. "
        "If they want it different, call its tool again with what they want. If they ask for something more as "
        "well, call the tool for it (this change's own tool again with as_well: true, when it takes that). If "
        "they don't want it, call {decline}. If they ask something else first, answer it, then ask again whether "
        "to go ahead.",
        "then.anything_else": " If they've asked for anything else in this call that isn't done yet, call its tool "
        "now; if not, ask if there's anything else.",
        "then.next_up": ' Then, as they asked, call {tool} again for the change set aside: "{read_back}"',
        "then.its_tool": "its tool",
        # Tool results
        "read_back": "Read back to the caller: {read_back}",
        "refused.prefix": "Nothing is changed: ",
        "lookup.need": "Nothing was looked up yet: {ask}",
        "account.unfound": "Their account isn't found yet.",
        "account.unfound.then": "Ask for {ask}, and call {tool}.",
        "need": "Nothing is changed yet: {tool} needs more from the caller.",
        "need.then": "Ask them: {ask} Then call {tool} again with everything they asked for.",
        "stage.waits": 'Nothing is changed yet: a {kind} change already waits for their answer: "{read_back}"',
        "stage.as_well.ask": "Call {tool} again with as_well: true if they want this as well as it, false if in "
        "place of it; ask them if you can't tell.",
        "stage.merged": "What they just asked for is added to the {kind} change read back before, as one change. ",
        "stage.nothing_added": "Nothing is added: this call has nothing the {kind} change waiting for their "
        'answer doesn\'t have already: "{read_back}"',
        "stage.nothing_added.then": "Call {tool} again with as_well: true and what else they asked for, as they "
        "said it. If they asked for nothing more, get their yes or no.",
        "stage.same": 'That\'s the change already read back, the same in every detail: "{read_back}"',
        "stage.same.then": "It's still waiting for their answer. If they didn't hear it, say it to them yourself; "
        "if they asked for something else, tell them how this is it, or what could be different. Then get their "
        "yes or no.",
        "stage.both": "Nothing is changed yet: they can't have both, since {conflict}. The change waiting for their "
        'answer: "{read_back}"',
        "stage.both.then": "Tell them, and ask which one they want.",
        "stage.rest_fails": "Nothing is changed yet: this takes over part of the {kind} change waiting for their "
        "answer, and the rest of that one can't go through without it: {why}",
        "stage.since": ", since {why}",
        "stage.replaced.rest": "This takes the place of the {kind} change read back before for what both are "
        'for{since}; the rest of that one isn\'t made yet, and is kept for after this one: "{read_back}" ',
        "stage.replaced": "This takes the place of the change read back before, which was not made{since}: "
        '"{read_back}" ',
        "stage.after_waiting": 'Kept for right after the change waiting: "{read_back}" The {kind} change goes '
        "through first.",
        "stage.after_waiting.then": "Tell them you'll do that right after, and get their answer to the change "
        'waiting: "{read_back}"',
        "stage.set_aside": "The change read back before isn't made yet, and is kept for after this one: "
        '"{read_back}" ',
        "held.set_aside": "Nothing is changed yet: a {kind} change is already set aside for after another: "
        '"{read_back}"',
        "held.differ": "Nothing is changed yet: this and the {kind} change set aside differ in {fields}.",
        "held.differ.then": "Ask which they want for both.",
        "held.first": "Not read to them yet: the {after} change they asked for goes first{since}. Kept for right "
        'after it: "{read_back}"',
        "held.first.then": "Call {tool} now for it (ask them for anything it needs that they haven't said); this "
        "one comes right after it.",
        "queue.narrowed": 'The change set aside for later is now only this: "{read_back}" ',
        "queue.dropped": "The change set aside for later no longer goes ahead, since this one takes its place: "
        '"{read_back}" ',
        "write.unknown": "its outcome isn't known ({error})",
        "write.no_writer": "no writer is set for {write}",
        "applied.failed": "It didn't go through: {reason}.{part}",
        "applied.part": " What went through first: {done}",
        "applied": "Done. {done}",
        "applied.then": "Tell them.",
        "done.default": "It's done: {statement}",
        "waiting.none": "No change is waiting for an answer, so nothing was changed.",
        "waiting.none.then": "Ask what they'd like to do.",
        "waiting.other": "Nothing was changed: the change waiting for their answer is the {kind} change, this one: "
        '"{read_back}"',
        "waiting.other.then": 'If their answer was to that one, call this again with change "{kind}".',
        "confirm.stale": "Nothing was changed: their yes was to an earlier read-back, so this one is read to them "
        "again. ",
        "confirm.failed": "The change didn't go through: {reason}.{part}",
        "confirm.done": "Done. {done}{total}",
        "confirm.done.then": "Tell them it's done.",
        "confirm.done.total.then": "Tell them it's done, and what it all comes to.",
        "confirm.done.state": "done",
        "decline": 'Nothing was changed: they don\'t want this change: "{read_back}"',
        "decline.then": "Tell them it's left as it was.",
        "identify.incomplete": "Nothing was looked up: it takes {ask}.",
        "identify.incomplete.then": "Ask them for {ask}, then call {tool} with what they say.",
        "identify.none": "No account was found with that.",
        "identify.none.then": "Ask them for {ask} again, and check it with them.",
        "identify.need": "Not found yet: {ask}",
        "identify.found": "Found their account. {account}",
        "identify.found.then": "Help with what they asked for: {asked}",
        "identify.found.ask": "Ask how you can help.",
        "transfer.notice": "One moment, I'm transferring you to a person who can help.",
        "transfer.summary": "asked for a person",
        "transfer.nowhere": "Not transferred: {to} isn't one of the places it goes.",
        "transfer.nowhere.then": "Ask where they want to go: {destinations}.",
        "transfer.unnamed": "nowhere",
        "transfer.going": "The call is being transferred to {to}.",
        "transfer.person": "a person",
        "transfer.going.then": "Say nothing more; the transfer notice is playing.",
        # The call's record: its ``now`` line, and money
        "now.asked": "What they asked for: {asked}",
        "now.done": "Done in this call: {done}",
        "now.waiting": 'Waiting for their answer: "{read_back}"',
        "now.queued": "Set aside, to do next: {read_backs}",
        "now.queued.item": '"{read_back}"',
        "money.back": "{amount} back to them",
        "money.charged": "{amount} charged",
        "money.in_all": " In all, the changes made in this call come to {amounts}.",
    }
)
"""Every key an operations agent's words come from, with its default."""


def placeholders(template: str) -> set[str]:
    """The ``{name}`` placeholders in a template."""
    return set(_PLACEHOLDER.findall(template))


class _Wording:
    """The words in use: the defaults, with the developer's overrides checked against them."""

    def __init__(
        self,
        defaults: Mapping[str, str],
        overrides: Mapping[str, str] | None,
        owner: str,
        table: str = "DEFAULT_WORDING",
    ) -> None:
        overrides = dict(overrides or {})
        unknown = sorted(k for k in overrides if k not in defaults)
        if unknown:
            raise ValueError(
                f"{owner} has no wording {', '.join(map(repr, unknown))}; the keys are those of {table}"
            )
        for key, text in overrides.items():
            if not isinstance(text, str):
                raise TypeError(f"wording {key!r} must be a string")
            extra = placeholders(text) - placeholders(defaults[key])
            if extra:
                allowed = (
                    ", ".join(sorted(f"{{{p}}}" for p in placeholders(defaults[key])))
                    or "none"
                )
                raise ValueError(
                    f"wording {key!r} has {', '.join(sorted(f'{{{p}}}' for p in extra))}, which it can't fill "
                    f"(it can use {allowed})"
                )
        self._text = {**defaults, **overrides}

    def __call__(self, key: str, /, **values: object) -> str:
        """The words for ``key``, with its placeholders filled in."""
        return _PLACEHOLDER.sub(lambda m: str(values[m.group(1)]), self._text[key])

    def template(self, key: str) -> str:
        """The words for ``key`` with their placeholders left in."""
        return self._text[key]

    def joined(self, items: list[str], last: str = "list.and") -> str:
        """Items in running text: "a, b and c"."""
        items = [i for i in items if i]
        if len(items) <= 1:
            return items[0] if items else ""
        return self("list.comma").join(items[:-1]) + self(last) + items[-1]


__all__ = ["DEFAULT_WORDING"]
