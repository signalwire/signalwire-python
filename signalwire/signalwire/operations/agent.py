"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

``ServiceAgent``: an agent written as what it can do. The developer registers
operations, lookups and how the caller is identified; the agent generates the
tools, the steps and the call's record, and runs every change through one
lifecycle: prepared, read back, agreed to, written, recorded.
"""

from __future__ import annotations

import copy
import inspect
import threading
import logging
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any

from signalwire.core.agent_base import AgentBase
from signalwire.core.function_result import FunctionResult
from signalwire.core.semantic_gate import SemanticGate
from signalwire.operations.model import (
    NOT_SAID,
    Change,
    Field,
    Need,
    Operation,
    Refuse,
    Values,
    Write,
    WriteFailed,
    _missing,
)
from signalwire.core.swaig_function import _resolve_awaitable as _resolve
from signalwire.operations.record import (
    RECORD,
    _in_all,
    _next_up,
    _now_line,
    _opening,
    _opening_data,
    _queued_entry,
    _record_of,
    _settle,
    _update,
    _waiting_entry,
    _whole,
)
from signalwire.patterns.proposal import Proposal, current

logger = logging.getLogger(__name__)

CONFIRM_TOOL = "confirm_change"
DECLINE_TOOL = "decline_change"
TRANSFER_TOOL = "transfer_to_human"
IDENTIFY_STEP, MAIN_STEP, CONFIRM_STEP = "identify", "main", "confirm"
TRANSFERRED = "transferred"

DEFAULT_RULES = (
    "This is a phone call. Keep each reply short, but give every fact the caller asks for.",
    "State only facts that came from a tool result. Never guess records, prices or policies.",
    "Nothing changes until the caller says yes to a change read back to them and it is confirmed.",
)
"""The rules every operations agent's prompt carries, unless replaced."""

AS_WELL = {
    "type": "boolean",
    "description": "Only while a change waits for their answer: true if they want this as well as it, false if in "
    "place of it. Leave it out if no change is waiting.",
}

_GOING_ON = "Tell them, and ask how they'd like to go on."


class CallContext:
    """
    One request of a call, as an operation, lookup or identify function sees it.

    ``call.data`` is the call's record (``global_data.ops``) as it came with
    the request;
    ``call.account_id`` is the account identified, and ``call.account`` what
    the agent's ``load`` function made of it. ``call.state`` is the
    developer's own state for the call (a game's hand, the results a caller
    may pick from), kept in ``global_data`` between requests.
    """

    def __init__(self, service: Operations, raw_data: Mapping[str, Any] | None) -> None:
        self.service = service
        self.raw_data: dict[str, Any] = (
            dict(raw_data) if isinstance(raw_data, Mapping) else {}
        )
        self.data = _record_of(raw_data)
        self.account: Any = None
        self.write_key = ""
        """While a write runs: a key unique to it in this call, for idempotent backends."""
        kept = self.data.get("state")
        self.state: dict[str, Any] = (
            copy.deepcopy(dict(kept)) if isinstance(kept, Mapping) else {}
        )
        self._state_was = copy.deepcopy(self.state)
        self._events: list[dict[str, Any]] = []
        self._acts: list[Any] = []
        self._next_step: str | None = None

    def act(self, result: FunctionResult) -> CallContext:
        """
        Add a platform action (or several) to this tool's result, after
        everything else it does: hang up, start recording, play hold music,
        hand the call on. ``result`` is a ``FunctionResult`` whose actions are
        taken; its text is not.
        """
        self._acts.extend(result.action)
        return self

    def show(self, event: Mapping[str, Any]) -> CallContext:
        """
        Send an event to the caller's screen (a SWML user event) with this
        tool's result, such as the order so far or the cards dealt.
        """
        self._events.append(dict(event))
        return self

    def go(self, step: str) -> CallContext:
        """
        Move to a step (a phase declared with ``Operations.phase``, or
        ``main``) when this tool's result goes back. Honoured from lookups,
        changes with no read-back, ``apply`` and identify; a change read back
        always waits in the confirm step.
        """
        self._next_step = step
        return self

    @property
    def account_id(self) -> str:
        """The identified account's id, or ``""``."""
        return str(self.data.get("account_id") or "")

    @property
    def call_id(self) -> str:
        """The platform's id for the call."""
        return str(self.raw_data.get("call_id") or "")


class _Lookup:
    def __init__(
        self,
        fn: Callable[..., Any],
        tool: str,
        description: str,
        fields: dict[str, Field],
        before_identity: bool,
        fillers: Any,
        secure: bool = True,
    ) -> None:
        self.fn, self.tool, self.description, self.fields = (
            fn,
            tool,
            description,
            fields,
        )
        self.before_identity, self.fillers, self.secure = (
            before_identity,
            fillers,
            secure,
        )


class _Identity:
    def __init__(
        self,
        any_of: Sequence[Sequence[str]],
        find: Callable[..., Any],
        load: Callable[..., Any] | None,
        describe: Callable[..., Any] | None,
        fields: Mapping[str, Field],
        tool: str,
        ask: str | None,
        fillers: Any,
        check_keys: bool,
        required: bool = True,
        prefill: Callable[..., Any] | None = None,
    ) -> None:
        self.required, self.prefill = required, prefill
        self.any_of = [list(s) for s in any_of]
        self.find, self.load, self.describe = find, load, describe
        keys = list(dict.fromkeys(k for s in self.any_of for k in s))
        self.fields = {
            k: fields.get(k)
            or Field(str, f"Their {k.replace('_', ' ')}, as they said it.")
            for k in keys
        }
        self.fields.update({k: f for k, f in fields.items() if k not in self.fields})
        self.tool, self.fillers, self.check_keys = tool, fillers, check_keys
        self.ask = ask or ", or ".join(
            "their " + _spoken_list([k.replace("_", " ") for k in s])
            for s in self.any_of
        )


class _Transfer:
    def __init__(
        self,
        fn: Callable[..., Any],
        tool: str,
        destinations: Mapping[str, str] | None,
        gated: bool,
        notice: str | None,
    ) -> None:
        self.fn, self.tool, self.gated, self.notice = fn, tool, gated, notice
        self.destinations = dict(destinations or {})

    def mention(self) -> str:
        if self.destinations:
            return f" To reach {_spoken_list(list(self.destinations))}, call {self.tool} with where they want to go."
        return f" If they ask for a person, call {self.tool}."

    def description(self) -> str:
        if self.destinations:
            return "Transfer the caller where they ask to go."
        return "Transfer the caller to a person, when they ask for one or say yes to being transferred."


class Operations:
    """
    What an agent can do for a caller, and the lifecycle every change goes
    through, installable on any agent (``install``). ``ServiceAgent`` is the
    prefab that owns one.

    Example:
        ops = Operations(role="You answer the phone for an online store.")
        ops.identify(any_of=[["email"], ["first_name", "last_name", "zip"]], find=find_account)

        @ops.operation(tool="cancel_order")
        class Cancel(Operation):
            '''Cancel pending orders.'''
            order_ids = Field(list[str], "The orders to cancel")

            def prepare(self, call, f):
                ...

        ops.install(agent)

    ``install`` gives the agent its prompt, tools, steps (identify, main,
    confirm, a step for each operation with ``guidance`` and each phase) and
    the call's record in ``global_data``, whose ``now`` the conscience shows
    on every request.
    """

    def __init__(
        self,
        *,
        role: str,
        rules: Sequence[str] | None = None,
        transfer_notice: str = "One moment, I'm transferring you to a person who can help.",
        step_text: Mapping[str, str] | None = None,
        confirm_gates: Sequence[SemanticGate] | None = None,
        tool_fillers: Mapping[str, Any] | None = None,
        gate_fillers: Mapping[str, Any] | None = None,
        wrap: Callable[[str, Callable[..., Any]], Callable[..., Any]] | None = None,
        customize: Callable[[Any], None] | None = None,
    ) -> None:
        """
        Args:
            role: Who the agent is and how it sounds, the prompt's Role section.
            rules: The prompt's Rules section; defaults to ``DEFAULT_RULES``
                (without the rule about changes when there are no
                operations).
            transfer_notice: What the platform says as a transfer starts.
            step_text: Text to use in place of a generated step's, by step
                name (``identify``, ``main``, ``confirm``).
            confirm_gates: Gates for ``confirm_change`` in place of the one
                ``confirm_gates()`` builds.
            tool_fillers: Fillers for the generated tools by name
                (``confirm_change``, ``decline_change``, ``transfer_to_human``,
                the identify tool), as ``define_tool`` takes them.
            gate_fillers: Fillers said while a generated tool's gates run.
            wrap: ``wrap(name, handler)`` returns the handler to register for
                each generated tool, for middleware of the developer's own.
            customize: ``customize(contexts)`` gets the generated
                ``ContextBuilder`` once the steps are made, to change them.
        """
        self._role = role
        self._step_text = dict(step_text or {})
        self._confirm_gates = list(confirm_gates) if confirm_gates is not None else None
        self._tool_fillers = dict(tool_fillers or {})
        self._gate_fillers = dict(gate_fillers) if gate_fillers else None
        self._wrap = wrap
        self._customize = customize
        self._rules = list(rules) if rules is not None else None
        self._operations: dict[str, Operation] = {}
        self._lookups: list[_Lookup] = []
        self._identity: _Identity | None = None
        self._writer: Callable[..., Any] | None = None
        self._transfer: _Transfer | None = None
        self._transfer_notice = transfer_notice
        self._offers: list[tuple[list[str], bool, list[str] | None]] = []
        self._phases: list[tuple[str, str, list[str] | None, bool]] = []
        self.proposal = Proposal(CONFIRM_TOOL, decline_tool=DECLINE_TOOL)

    # ------------------------------------------------------------------ registration

    def operation(
        self,
        cls: type[Operation] | None = None,
        *,
        tool: str | None = None,
        kind: str | None = None,
        guidance: str | None = None,
    ) -> Any:
        """
        Register an operation class; usable as ``@agent.operation`` or
        ``@agent.operation(tool="cancel_order")``.

        Args:
            cls: The ``Operation`` subclass.
            tool: The tool's name; defaults to the class's ``tool``, else its
                name in snake case.
            kind: Its name in the record; defaults to the class's ``kind``,
                else its name in lower case.
            guidance: Instructions for a step of its own (see
                ``Operation.guidance``).
        """

        def register(klass: type[Operation]) -> type[Operation]:
            if not (isinstance(klass, type) and issubclass(klass, Operation)):
                raise TypeError("@agent.operation registers an Operation subclass")
            op = klass()
            k = kind or klass.kind or klass.__name__.lower()
            t = tool or klass.tool or _snake(klass.__name__)
            g = guidance if guidance is not None else klass.guidance
            for attr, value in (("kind", k), ("tool", t), ("guidance", g)):
                setattr(op, attr, value)
            if k in self._operations:
                raise ValueError(f"an operation of kind {k!r} is already registered")
            if not klass.describe():
                raise ValueError(
                    f"{klass.__name__} needs a docstring: it is what the model reads about it"
                )
            self._operations[k] = op
            return klass

        return register(cls) if cls is not None else register

    def lookup(
        self,
        description: str,
        *,
        tool: str | None = None,
        fields: Mapping[str, Field] | None = None,
        before_identity: bool = False,
        fillers: Any = (),
        secure: bool = True,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Register a lookup: a tool that reads and answers, and changes nothing.

        The function is called as ``fn(call, **fields)`` and returns what to
        tell the model (a string or a ``FunctionResult``), or raises
        ``Refuse``. It may be ``async``.

        Args:
            description: What it reads, as the model reads it.
            tool: The tool's name; defaults to the function's name.
            fields: Its arguments; defaults to the function's parameters
                after ``call``, each a string.
            before_identity: True to offer it before the caller is identified.
                Account data never should be.
            fillers: Short phrases said while it runs: a list, or lists by
                language code.
            secure: Whether its tool takes the per-call security token.
        """

        def register(fn: Callable[..., Any]) -> Callable[..., Any]:
            params = list(inspect.signature(fn).parameters)[1:]
            found = (
                dict(fields)
                if fields is not None
                else {
                    p: Field(str, p.replace("_", " ").capitalize() + ".")
                    for p in params
                }
            )
            self._lookups.append(
                _Lookup(
                    fn,
                    tool or fn.__name__,
                    description,
                    found,
                    before_identity,
                    fillers,
                    secure,
                )
            )
            return fn

        return register

    def identify(
        self,
        *,
        any_of: Sequence[Sequence[str]],
        find: Callable[..., Any],
        load: Callable[..., Any] | None = None,
        describe: Callable[..., Any] | None = None,
        fields: Mapping[str, Field] | None = None,
        tool: str = "find_account",
        ask: str | None = None,
        fillers: Any = (),
        check_keys: bool = True,
        required: bool = True,
        prefill: Callable[..., Any] | None = None,
    ) -> Operations:
        """
        Identify the caller before account data is shared or changed.

        Args:
            any_of: Key sets, any one of which finds an account, such as
                ``[["email"], ["first_name", "last_name", "zip"]]``.
            find: ``find(call, keys)`` returns the account's id (None when no
                account has it), or raises ``Refuse`` or ``Need``. May be
                ``async``.
            load: ``load(call, account_id)`` returns the account as operations
                use it (``call.account``); defaults to the id itself.
            describe: ``describe(call)`` returns the account in a few words for
                the steps, read again after every change.
            fields: Descriptions of the keys (each defaults to a string), and
                any other arguments ``find`` takes, such as the letters a
                caller spelled.
            tool: The identify tool's name.
            ask: How to ask for the keys, such as "their email address, or
                their first name, last name and zip code".
            fillers: Short phrases said while it runs.
            check_keys: False to call ``find`` without a whole key set, when
                it recovers from partial or misheard keys itself.
            required: False for an agent that's useful to callers who aren't
                identified: there's no identify step, and the identify tool is
                offered with the rest. Operations still refuse until it's
                found, unless they're ``before_identity``.
            prefill: ``prefill(request_data, request)`` returns keys already
                known when the call starts (caller ID, a chat widget, the
                page), or None. With them, ``find`` runs before the call does,
                silently, and the call starts identified (``prefilled``).
                Implies ``required=False``.
        """
        if not any_of or not all(any_of):
            raise ValueError("identify needs at least one non-empty key set")
        self._identity = _Identity(
            any_of,
            find,
            load,
            describe,
            dict(fields or {}),
            tool,
            ask,
            fillers,
            check_keys,
            required,
            prefill,
        )
        return self

    def writes_with(self, writer: Callable[..., Any]) -> Operations:
        """
        Set the function that carries out every operation's writes:
        ``writer(call, write)``, raising ``WriteFailed`` when the backend
        refuses one. An operation's own ``apply`` takes precedence.
        """
        self._writer = writer
        return self

    def transfer_with(
        self,
        transfer: Callable[..., Any],
        *,
        destinations: Mapping[str, str] | None = None,
        gated: bool = True,
        tool: str = TRANSFER_TOOL,
        notice: str | None = None,
    ) -> Operations:
        """
        Offer a transfer: ``transfer(call, summary)`` (with ``destinations``,
        ``transfer(call, summary, to)``) hands the call over, by returning
        the platform action to do it (a ``FunctionResult`` with a connect or
        a SWML transfer) or doing it itself, or raises ``Refuse``. Adds its
        tool to every step.

        Args:
            transfer: The function.
            destinations: Where callers can go, by name, each with a
                description, such as ``{"sales": "buying something new"}``.
            gated: Whether the tool runs only once the caller has asked for a
                person or agreed to it. A router, whose callers say where to
                go, sets it False.
            tool: The tool's name.
            notice: What the platform says as the transfer starts; defaults to
                the service's ``transfer_notice``.
        """
        self._transfer = _Transfer(transfer, tool, destinations, gated, notice)
        return self

    def offer(
        self,
        *tools: str,
        before_identity: bool = False,
        steps: Sequence[str] | None = None,
    ) -> Operations:
        """
        Offer tools the service didn't make (skills, DataMap tools, MCP
        tools, another layer's tools, ``define_tool``) in its steps. Offers
        add up.

        Args:
            *tools: The tools' names, as registered on the agent.
            before_identity: True to offer them in the identify step too,
                before the caller is found, as ``lookup`` takes it.
            steps: The steps that offer them, by name, in place of the
                default: every generated step but ``identify`` and
                ``confirm``, where a change waits for the caller's yes.
        """
        self._offers.append(
            (list(tools), before_identity, list(steps) if steps is not None else None)
        )
        return self

    def phase(
        self,
        name: str,
        text: str,
        tools: Sequence[str] | None = None,
        *,
        initial: bool = False,
    ) -> Operations:
        """
        Declare a step of the call's own, such as a game's betting and
        playing, with the tools it offers. Tools move to it with
        ``call.go(name)``.

        Args:
            name: The step's name.
            text: What to do in it.
            tools: The tools it offers, by name; defaults to every lookup and
                operation, and the transfer.
            initial: True to start the call in it (after identify, if any,
                its tool moves here with ``call.go``).
        """
        if name in (IDENTIFY_STEP, MAIN_STEP, CONFIRM_STEP, TRANSFERRED) or any(
            p[0] == name for p in self._phases
        ):
            raise ValueError(f"a step named {name!r} already exists")
        self._phases.append(
            (name, text, list(tools) if tools is not None else None, initial)
        )
        return self

    def apply_write(self, call: CallContext, write: Write) -> Any:
        """Carry out one write with the agent's writer (``writes_with``)."""
        if self._writer is None:
            raise WriteFailed(f"no writer is set for {write.name}")
        return self._writer(call, write)

    # ------------------------------------------------------------------ generation

    def install(self, agent: AgentBase) -> AgentBase:
        """
        Give ``agent`` this service's prompt sections, record, conscience,
        tools and steps. Call it once per agent (or per request, for an agent
        configured per request). Other layers may install on the same agent,
        before or after: steps that exist already are added to, never
        replaced, and the conscience gets this service's line appended.
        """
        agent.prompt_add_section("Role", body=self._role)
        rules = (
            self._rules
            if self._rules is not None
            else [
                r
                for r in DEFAULT_RULES
                if self._operations or r is not DEFAULT_RULES[2]
            ]
        )
        if rules:
            agent.prompt_add_section("Rules", bullets=list(rules))
        if self._operations or self._identity is not None:
            agent.update_global_data(_opening_data())
            line = f"${{global_data.{RECORD}.now}}"
            had = str((getattr(agent, "_params", {}) or {}).get("conscience") or "")
            if line not in had:
                agent.set_param(
                    "conscience", f"{had}\n\n{line}" if had.strip() else line
                )
        self._define_tools(agent)
        self._define_steps(agent)
        return agent

    def prefilled(
        self, request_data: Mapping[str, Any] | None, request: Any = None
    ) -> dict[str, Any] | None:
        """
        The ``global_data`` a call starts with when ``identify``'s ``prefill``
        already knows the caller (caller ID, a chat widget, the page): the
        record, identified, or None. ``ServiceAgent`` applies it on each SWML
        request; an agent configured per request applies it itself.
        """
        idn = self._identity
        if idn is None or idn.prefill is None:
            return None
        try:
            keys = _resolve(idn.prefill(request_data or {}, request))
            if not keys:
                return None
            call = CallContext(self, {"global_data": {RECORD: _opening()}})
            found = _resolve(idn.find(call, dict(keys)))
            if found is None or str(found).strip() == "":
                return None
            call.data["account_id"] = str(found)
            call.account = (
                _resolve(idn.load(call, call.data["account_id"]))
                if idn.load
                else call.data["account_id"]
            )
            text = str(_resolve(idn.describe(call))) if idn.describe else ""
        except Exception:  # unknown: the call starts unidentified, and identify asks
            logger.exception("operations: prefill could not identify the caller")
            return None
        return _update(call.data, account_id=call.data["account_id"], account=text)

    def _gated(self) -> bool:
        """Whether the call starts in a step of its own that asks who the caller is."""
        idn = self._identity
        return idn is not None and idn.required and idn.prefill is None

    def _tools_for(self, step: str) -> list[str]:
        """The tools a generated step offers: every lookup and operation (those an operation scopes with
        ``offered_in`` only where it says), the identify tool where identify doesn't have a step of its own,
        tools offered with ``offer``, and the transfer."""
        idn = self._identity
        early = step == IDENTIFY_STEP
        tools: list[str] = []
        if early:
            tools += [idn.tool] if idn is not None else []
            tools += [lk.tool for lk in self._lookups if lk.before_identity]
            tools += [
                op.tool
                for op in self._operations.values()
                if op.before_identity and _offered(op, step)
            ]
        else:
            if idn is not None and not self._gated():
                tools.append(idn.tool)
            tools += [lk.tool for lk in self._lookups]
            tools += [
                op.tool
                for op in self._operations.values()
                if _offered(op, step) or op.kind == step
            ]
        for names, before_identity, steps in self._offers:
            if steps is not None:
                offered = step in steps
            else:
                offered = step != CONFIRM_STEP and (
                    step != IDENTIFY_STEP or before_identity
                )
            if offered:
                tools += list(names)
        if self._transfer:
            tools.append(self._transfer.tool)
        return list(dict.fromkeys(tools))

    def _define_steps(self, agent: AgentBase) -> None:
        builder = agent.define_contexts()
        ctx = builder.get_context("default") or builder.add_context("default")
        transfer = self._transfer.mention() if self._transfer else ""
        record = f"${{global_data.{RECORD}.account}}"
        where = f"Their account: {record}\n\n" if self._identity else ""
        idn = self._identity
        lookups = " or ".join(lk.tool for lk in self._lookups)
        ops = "; ".join(
            f"{op.tool} ({type(op).describe().rstrip('.')})"
            for op in self._operations.values()
        )
        unfound = (
            f" If their account isn't found yet and they want something that needs it, ask for {idn.ask} and call "
            f"{idn.tool}."
            if idn is not None and not self._gated()
            else ""
        )
        help_with = (
            (f"To look something up, call {lookups}. " if lookups else "")
            + (
                f"To make a change, call its tool with everything the caller asked for: {ops}. The tool checks it "
                "and reads it back to them. "
                if ops
                else ""
            )
            + "If they ask for something these tools can't do, tell them so and what can be done instead."
            + unfound
            + transfer
        )
        if self._gated():
            assert idn is not None  # noqa: S101  # type narrowing: _gated() means an identity is set
            early_lookups = [lk.tool for lk in self._lookups if lk.before_identity]
            early = (
                f" For {' or '.join(early_lookups)}, they needn't be identified."
                if early_lookups
                else ""
            )
            _contribute(
                ctx,
                IDENTIFY_STEP,
                self._step_text.get(IDENTIFY_STEP)
                or f"Ask for {idn.ask}, and call {idn.tool} with what they say. Nothing about an account can be shared "
                f"or changed until it's found.{early}{transfer}",
                self._tools_for(IDENTIFY_STEP),
            )
        _contribute(
            ctx,
            MAIN_STEP,
            self._step_text.get(MAIN_STEP)
            or f"{where}Help with what they ask, all of it. {help_with}",
            self._tools_for(MAIN_STEP),
        )
        if any(op.confirm for op in self._operations.values()):
            _contribute(
                ctx,
                CONFIRM_STEP,
                self._step_text.get(CONFIRM_STEP)
                or f"{where}A change was just read to them and waits for their answer. When they say yes, call "
                f"{CONFIRM_TOOL}. If they want it different, call its tool again with what they want. If they don't "
                f"want it, call {DECLINE_TOOL}. If they ask for another change as well, call its tool: the tool says "
                f"which comes first, and nothing asked for is lost.{transfer}",
                [CONFIRM_TOOL, DECLINE_TOOL, *self._tools_for(CONFIRM_STEP)],
            )
        for op in self._operations.values():
            if op.guidance:
                _contribute(
                    ctx,
                    op.kind,
                    f"{where}{op.guidance} When you have what it needs, call {op.tool}. {help_with}",
                    self._tools_for(op.kind),
                ).set_history("spoken")
        known = {
            *self._tools_for(MAIN_STEP),
            *self._tools_for(IDENTIFY_STEP),
            CONFIRM_TOOL,
            DECLINE_TOOL,
            *(n for names, _, _ in self._offers for n in names),
            *(op.tool for op in self._operations.values()),
        }
        first = None
        for pname, ptext, ptools, initial in self._phases:
            tools = ptools if ptools is not None else self._tools_for(pname)
            unknown = [t for t in tools if t not in known]
            if unknown:
                raise ValueError(
                    f"phase {pname!r} offers tools that don't exist: {', '.join(unknown)}"
                )
            _contribute(ctx, pname, f"{where}{ptext}", tools)
            first = first or (pname if initial else None)
        ctx.set_initial_step(IDENTIFY_STEP if self._gated() else first or MAIN_STEP)
        if self._transfer:
            gone = builder.get_context(TRANSFERRED) or builder.add_context(TRANSFERRED)
            _contribute(
                gone,
                TRANSFERRED,
                "The caller is being transferred. Say nothing more.",
                [],
            )
            gone.set_initial_step(TRANSFERRED)
        if self._customize is not None:
            self._customize(builder)

    def _define_tools(self, agent: AgentBase) -> None:
        idn = self._identity
        if idn is not None:
            params = {k: f.schema() for k, f in idn.fields.items()}
            params["asked_for"] = {
                "type": "string",
                "description": "Everything the caller has asked for so far in this call, in their words.",
            }
            agent.define_tool(
                idn.tool,
                f"Find the caller's account by {idn.ask}.",
                params,
                self._wrapped(idn.tool, self._identify),
                required=["asked_for"],
                vouched=True,
                nullable_optional=True,
                fillers=self._tool_fillers.get(idn.tool) or _fillers(idn.fillers),
            )
        for lk in self._lookups:
            agent.define_tool(
                lk.tool,
                f"{lk.description} Changes nothing.",
                {k: f.schema() for k, f in lk.fields.items()},
                self._wrapped(lk.tool, self._lookup_handler(lk)),
                required=[k for k, f in lk.fields.items() if f.required and not f.ask],
                nullable_optional=True,
                fillers=_fillers(lk.fillers),
                secure=lk.secure,
            )
        for op in self._operations.values():
            fields = op.fields()
            params = {k: _with_not_said(f) for k, f in fields.items()}
            if op.confirm and (
                op.combine is not None or _overrides(op, "conflicts_with")
            ):
                params["as_well"] = dict(AS_WELL)
            agent.define_tool(
                op.tool,
                f"{type(op).describe()}{' Reads it back first.' if op.confirm else ''}",
                params,
                self._wrapped(op.tool, self._operation_handler(op)),
                required=[k for k, f in fields.items() if f.required],
                vouched=True,
                nullable_optional=True,
                fillers=_fillers(op.fillers),
                secure=op.secure,
            )
        kinds = [k for k, op in self._operations.items() if op.confirm]
        if kinds:
            which = {
                "change": {
                    "type": "string",
                    "enum": kinds,
                    "description": "What the change read back is.",
                }
            }
            agent.define_tool(
                CONFIRM_TOOL,
                "Make the change just read back, once the caller has said yes to it.",
                which,
                self._wrapped(CONFIRM_TOOL, self._confirm),
                required=["change"],
                gates=self._confirm_gates
                if self._confirm_gates is not None
                else self.confirm_gates(),
                gate_fillers=self._gate_fillers,
                fillers=self._tool_fillers.get(CONFIRM_TOOL),
            )
            agent.define_tool(
                DECLINE_TOOL,
                "Leave the change just read back unmade, when the caller says they don't want it.",
                which,
                self._wrapped(DECLINE_TOOL, self._decline),
                required=["change"],
                fillers=self._tool_fillers.get(DECLINE_TOOL),
            )
        tr = self._transfer
        if tr is not None:
            params = {
                "summary": {
                    "type": "string",
                    "description": "What they need, in a sentence.",
                }
            }
            if tr.destinations:
                params["to"] = {
                    "type": "string",
                    "enum": list(tr.destinations),
                    "description": "Where they want to go: "
                    + "; ".join(f"{k}: {v}" for k, v in tr.destinations.items()),
                }
            agent.define_tool(
                tr.tool,
                tr.description(),
                params,
                self._wrapped(tr.tool, self._transfer_handler),
                required=["to"] if tr.destinations else None,
                gates=[_transfer_gate()] if tr.gated else None,
                gate_fillers=self._gate_fillers if tr.gated else None,
                fillers=self._tool_fillers.get(tr.tool),
            )

    def _wrapped(self, name: str, handler: Callable[..., Any]) -> Callable[..., Any]:
        return self._wrap(name, handler) if self._wrap is not None else handler

    def confirm_gates(self) -> list[SemanticGate]:
        """
        The confirm tool's gate: did the caller agree to the change read back.

        One gate. A yes counts however short, even said while the read-back
        was still playing, and even with a request for something else; it
        doesn't count when they asked for this change itself to be different.
        """
        agreed = next(g for g in self.proposal.confirm_gates() if g.id == "agreed")
        return [
            SemanticGate(
                "Has the caller said yes, in `conversation`, to the change described in `semantic_state`? A yes "
                'counts however short it is ("okay", "sure", "that\'s right", "go ahead"), even if they said it '
                "while the agent was still asking, before the whole change was read, even if it comes with a "
                "request for something else as well, and whatever the agent has said since. It doesn't count if "
                "they asked for this change itself to be different, or for only part of it.",
                threshold=agreed.threshold,
                on_fail=agreed.on_fail,
                id=agreed.id,
                dialogue=agreed.dialogue,
                true_means="They said yes to this change as it is, in any words, at any point while it was being "
                "asked or after, even with a request for something else as well.",
                false_means="They said no, hesitated, only made a listening sound, only asked a question, asked for "
                "something else with no yes, asked for this change to be different, or haven't spoken since the "
                "change was asked.",
            )
        ]

    # ------------------------------------------------------------------ handlers

    def _operation_handler(
        self, op: Operation
    ) -> Callable[..., Awaitable[FunctionResult]]:
        async def handler(
            args: dict[str, Any], raw_data: dict[str, Any]
        ) -> FunctionResult:
            call = CallContext(self, raw_data)
            try:
                if op.before_identity:
                    await self._load_account(call)
                else:
                    await self._require_account(call)
                change = await self._prepare(call, op, args)
                if not op.confirm:
                    return self._finish(
                        call, await self._apply_now(call, op, args, change)
                    )
                return self._finish(
                    call, await self._stage(call, op, args, change), go=False
                )
            except Need as e:
                return self._finish(call, self._need_result(call, op, e), go=False)
            except Refuse as e:
                return self._finish(call, _refused(e, "Nothing is changed: "), go=False)

        handler.__name__ = f"{op.tool}_handler"
        return handler

    def _lookup_handler(self, lk: _Lookup) -> Callable[..., Awaitable[FunctionResult]]:
        async def handler(
            args: dict[str, Any], raw_data: dict[str, Any]
        ) -> FunctionResult:
            call = CallContext(self, raw_data)
            try:
                if not lk.before_identity:
                    await self._require_account(call)
                kwargs = {
                    k: (None if _missing(args.get(k)) else args.get(k))
                    for k in lk.fields
                }
                answer = await _maybe(lk.fn(call, **kwargs))
            except Refuse as e:
                return self._finish(call, _refused(e, ""), go=False)
            except Need as e:
                return self._finish(
                    call,
                    FunctionResult(
                        tool_result=f"Nothing was looked up yet: {e.ask}",
                        tool_prompt=f"Ask them: {e.ask}",
                    ),
                    go=False,
                )
            return self._finish(
                call,
                answer
                if isinstance(answer, FunctionResult)
                else FunctionResult(tool_result=str(answer)),
            )

        handler.__name__ = f"{lk.tool}_handler"
        return handler

    async def _load_account(self, call: CallContext) -> None:
        idn = self._identity
        if idn is not None and call.account_id:
            call.account = (
                await _maybe(idn.load(call, call.account_id))
                if idn.load
                else call.account_id
            )

    async def _require_account(self, call: CallContext) -> None:
        idn = self._identity
        if idn is None:
            return
        if not call.account_id:
            raise Refuse(
                "Their account isn't found yet.",
                f"Ask for {idn.ask}, and call {idn.tool}.",
            )
        call.account = (
            await _maybe(idn.load(call, call.account_id))
            if idn.load
            else call.account_id
        )

    async def _prepare(
        self, call: CallContext, op: Operation, args: Mapping[str, Any]
    ) -> Change:
        fields = op.fields()
        missing = [
            k
            for k, f in fields.items()
            if f.required and f.ask and _missing(args.get(k))
        ]
        if missing and op.ask_in_order:
            missing = missing[:1]
        if missing:
            raise Need(" ".join(str(fields[k].ask) for k in missing), missing)
        change = await _maybe(op.prepare(call, Values(fields, args)))
        if not isinstance(change, Change):
            raise TypeError(
                f"{type(op).__name__}.prepare must return a Change, got {type(change).__name__}"
            )
        if op.confirm and not change.read_back.strip():
            raise ValueError(
                f"{type(op).__name__}.prepare returned a Change with no read_back"
            )
        return change

    @staticmethod
    def _finish(
        call: CallContext, result: FunctionResult, *, go: bool = True
    ) -> FunctionResult:
        """
        Put what the tool's own code asked for into its result. The record
        goes in one action object ahead of the rest, whole (the platform
        replaces a top-level key whole), with the tool's state in it, so a say
        the caller talks over can't keep it from being recorded; then the step
        it goes to and its screen events; its platform actions go last.
        """
        record = None
        kept: list[Any] = []
        for action in result.action:
            if (
                isinstance(action, dict)
                and isinstance(action.get("set_global_data"), dict)
                and RECORD in action["set_global_data"]
            ):
                record = action["set_global_data"][RECORD]
                rest = {
                    k: v for k, v in action["set_global_data"].items() if k != RECORD
                }
                others = {k: v for k, v in action.items() if k != "set_global_data"}
                if rest or others:
                    kept.append(
                        {**others, **({"set_global_data": rest} if rest else {})}
                    )
                continue
            kept.append(action)
        if call.state != call._state_was:
            record = _whole(
                record if record is not None else call.data, state=call.state
            )
        front = FunctionResult()
        if record is not None:
            front.update_global_data({RECORD: record})
        if go and call._next_step:
            kept = [a for a in kept if not (isinstance(a, dict) and "change_step" in a)]
            front.swml_change_step(call._next_step)
        for event in call._events:
            front.swml_user_event(event)
        result.action = [*front.action, *kept, *call._acts]
        return result

    def _need_result(self, call: CallContext, op: Operation, e: Need) -> FunctionResult:
        result = FunctionResult(
            tool_result=f"Nothing is changed yet: {op.tool} needs more from the caller.",
            tool_prompt=f"Ask them: {e.ask} Then call {op.tool} again with everything they asked for.",
        )
        if op.guidance and not (call.data.get("waiting") or {}).get("read_back"):
            result.swml_change_step(op.kind)
        return result

    async def _stage(
        self, call: CallContext, op: Operation, args: dict[str, Any], change: Change
    ) -> FunctionResult:
        """
        Hold a change for the caller's yes, weighed against the one waiting.

        One change waits at a time. A new one (N) against the one waiting (W):

        * the same operation made "as well" merges into W when ``combine``
          allows; for things W is already for, without ``as_well``, the model
          is asked which they meant;
        * the same operation otherwise, or one that ``conflicts_with`` W, takes
          W's place for what both are for, and the rest of W (``without``) is
          built again and set aside; if it can't go through without what N
          took, nothing is changed. A conflict asked for "as well" is refused:
          they can't have both;
        * W first when N's kind is in W's ``goes_before``: N is set aside;
        * otherwise N is read back now and W is set aside for after it.
        """
        data = call.data
        waiting = data.get("waiting") or {}
        queued = list(data.get("queued") or [])
        as_well = args.get("as_well")
        note, replaced = "", False
        if waiting.get("read_back"):
            wkind = str(waiting.get("kind") or "")
            wop = self._operations.get(wkind)
            held_touches = set(waiting.get("touches") or [])
            overlap = set(change.touches) & held_touches
            same = wkind == op.kind
            conflict = None
            if overlap and not same:
                theirs = _change_of(waiting)
                conflict = op.conflicts_with(wkind, change, theirs) or (
                    wop.conflicts_with(op.kind, theirs, change) if wop else None
                )
            within = set(change.touches) <= held_touches
            if same and op.combine is not None:
                if as_well is None and overlap and not within:
                    raise Refuse(
                        f'Nothing is changed yet: a {op.kind} change already waits for their answer: "{waiting["read_back"]}"',
                        f"Call {op.tool} again with as_well: true if they want this as well as it, false if in place "
                        "of it; ask them if you can't tell.",
                    )
                held = waiting.get("args") or {}
                if as_well is True and all(
                    _same_value(held.get(k), args.get(k)) for k in op.combine
                ):
                    args = op.merge(held, args)
                    change = await self._prepare(call, op, args)
                    note = f"What they just asked for is added to the {op.kind} change read back before, as one change. "
                    replaced = True
            if waiting.get("read_back") == change.read_back:
                raise Refuse(
                    f'That\'s the change already read back, the same in every detail: "{change.read_back}"',
                    "It's still waiting for their answer. If they didn't hear it, say it to them yourself; if they "
                    "asked for something else, tell them how this is it, or what could be different. Then get their "
                    "yes or no.",
                )
            if replaced:
                pass
            elif overlap and (same or conflict):
                if conflict and as_well is True:
                    raise Refuse(
                        f"Nothing is changed yet: they can't have both, since {conflict}. The change waiting for their "
                        f'answer: "{waiting["read_back"]}"',
                        "Tell them, and ask which one they want.",
                    )
                rest = wop.without(waiting.get("args") or {}, overlap) if wop else None
                kept = None
                if rest and wop is not None:
                    try:
                        kept = await self._prepare(call, wop, rest)
                    except (Need, Refuse) as e:
                        raise Refuse(
                            f"Nothing is changed yet: this takes over part of the {wkind} change waiting for their "
                            f"answer, and the rest of that one can't go through without it: {_why(e)}",
                            _GOING_ON,
                        ) from e
                why = f", since {conflict}" if conflict else ""
                if kept is not None and rest is not None:
                    queued.append(_queued_entry(wkind, rest, kept))
                    note = (
                        f"This takes the place of the {wkind} change read back before for what both are for{why}; the "
                        f'rest of that one isn\'t made yet, and is kept for after this one: "{kept.read_back}" '
                    )
                else:
                    note = f'This takes the place of the change read back before, which was not made{why}: "{waiting["read_back"]}" '
                replaced = True
            elif overlap and wop is not None and op.kind in wop.goes_before:
                entry = _queued_entry(op.kind, args, change)
                queued = [q for q in queued if not _same_request(q, entry)] + [entry]
                return FunctionResult(
                    tool_result=f'Kept for right after the change waiting: "{change.read_back}" The {wkind} change '
                    "goes through first.",
                    tool_prompt=f'Tell them you\'ll do that right after, and get their answer to the change waiting: "{waiting["read_back"]}"',
                ).update_global_data(_update(data, queued=queued))
            else:
                queued.append(
                    {
                        k: waiting.get(k)
                        for k in ("kind", "read_back", "touches", "args")
                    }
                )
                note = f'The change read back before isn\'t made yet, and is kept for after this one: "{waiting["read_back"]}" '
        queued, also = await self._reconcile_queue(call, op, change, queued)
        note += also
        history = (
            _settle(data, "replaced")["history"]
            if replaced
            else list(data.get("history") or [])
        )
        revision = int(data.get("proposals") or 0) + 1
        entry = _waiting_entry(op.kind, args, change, revision)
        result = (
            FunctionResult()
            .update_global_data(
                _update(
                    data,
                    history=history,
                    queued=queued,
                    waiting=entry,
                    proposals=revision,
                )
            )
            .swml_change_step(CONFIRM_STEP)
        )
        result = self.proposal.propose(
            change.read_back, raw_data=call.raw_data, result=result
        )
        if note and isinstance(result.response, dict):
            result.response["tool_result"] = note + str(
                result.response.get("tool_result") or ""
            )
        return result

    async def _reconcile_queue(
        self,
        call: CallContext,
        op: Operation,
        change: Change,
        queued: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], str]:
        """
        The changes set aside, weighed against the one now read back as the
        one waiting was: one of the same operation, or one it conflicts with,
        keeps only what the new one doesn't take over, built again; what
        can't go through without it no longer goes ahead.
        """
        kept: list[dict[str, Any]] = []
        notes: list[str] = []
        for q in queued:
            qop = self._operations.get(str(q.get("kind") or ""))
            qtouches = set(q.get("touches") or [])
            overlap = qtouches & set(change.touches)
            if not overlap or qop is None:
                kept.append(q)
                continue
            same = q.get("kind") == op.kind
            if same and qtouches == set(change.touches):
                continue  # this is that one, taken up now
            theirs = _change_of(q)
            conflict = (
                None
                if same
                else (
                    op.conflicts_with(qop.kind, change, theirs)
                    or qop.conflicts_with(op.kind, theirs, change)
                )
            )
            if not (same or conflict):
                kept.append(q)
                continue
            rest = qop.without(q.get("args") or {}, overlap)
            rebuilt = None
            if rest:
                try:
                    rebuilt = await self._prepare(call, qop, rest)
                except (Need, Refuse):
                    rebuilt = None
            if rebuilt is not None and rest is not None:
                kept.append(_queued_entry(qop.kind, rest, rebuilt))
                notes.append(
                    f'The change set aside for later is now only this: "{rebuilt.read_back}" '
                )
            else:
                notes.append(
                    f'The change set aside for later no longer goes ahead, since this one takes its place: "{q.get("read_back")}" '
                )
        return kept, "".join(notes)

    async def _run_writes(
        self, call: CallContext, op: Operation, writes: Sequence[Write], revision: int
    ) -> tuple[int, str]:
        made, reply = 0, ""
        for i, write in enumerate(writes):
            call.write_key = f"{call.call_id}:{revision}:{i}"
            try:
                await _maybe(op.apply(call, write))
            except WriteFailed as e:
                reply = e.reason
                break
            except Exception as e:  # an outcome nobody reported: not counted as made
                logger.exception("operations: %s write %s raised", op.kind, write.name)
                reply = f"its outcome isn't known ({type(e).__name__})"
                break
            made += 1
        return made, reply

    async def _account_text(self, call: CallContext) -> dict[str, Any]:
        idn = self._identity
        if idn is None or idn.describe is None or not call.account_id:
            return {}
        try:
            call.account = (
                await _maybe(idn.load(call, call.account_id))
                if idn.load
                else call.account_id
            )
            return {"account": str(await _maybe(idn.describe(call)))}
        except Exception:  # what was written still counts
            logger.exception("operations: describing the account again failed")
            return {}

    async def _apply_now(
        self, call: CallContext, op: Operation, args: dict[str, Any], change: Change
    ) -> FunctionResult:
        data = call.data
        history = list(data.get("history") or [])
        revision = int(data.get("proposals") or 0) + 1
        made, reply = await self._run_writes(call, op, change.writes, revision)
        lines, moved = change.done_lines(), change.money_moved()
        done = _made_text(lines, list(change.writes), made)
        outcome = "made" if made == len(change.writes) else f"not made: {reply}"
        history.append(
            {
                "kind": op.kind,
                "touches": list(change.touches),
                "read_back": change.read_back,
                "outcome": outcome,
                "done": done,
                "money": round(sum(moved[:made]), 2),
                **(
                    {"writes_made": [w.to_dict() for w in change.writes[:made]]}
                    if outcome != "made"
                    else {}
                ),
            }
        )
        update = _update(
            data,
            **(await self._account_text(call)),
            history=history,
            proposals=revision,
        )
        if outcome != "made":
            part = f" What went through first: {done}" if made else ""
            return FunctionResult(
                tool_result=f"It didn't go through: {reply}.{part}",
                tool_prompt=_GOING_ON,
            ).update_global_data(update)
        return FunctionResult(
            tool_result=f"Done. {done}", tool_prompt="Tell them."
        ).update_global_data(update)

    def _waiting_named(
        self, call: CallContext, args: Mapping[str, Any]
    ) -> dict[str, Any]:
        waiting = call.data.get("waiting") or {}
        if not waiting.get("read_back"):
            raise Refuse(
                "No change is waiting for an answer, so nothing was changed.",
                "Ask what they'd like to do.",
            )
        if args.get("change") != waiting.get("kind"):
            raise Refuse(
                f"Nothing was changed: the change waiting for their answer is the {waiting.get('kind')} change, this "
                f'one: "{waiting["read_back"]}"',
                f'If their answer was to that one, call this again with change "{waiting.get("kind")}".',
            )
        return waiting

    async def _confirm(
        self, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        call = CallContext(self, raw_data)
        try:
            waiting = self._waiting_named(call, args)
            await self._require_account(call)
        except Refuse as e:
            return _refused(e, "")
        state = current(raw_data)
        if not state or state.get("proposal") != waiting["read_back"]:
            result = self.proposal.propose(waiting["read_back"], raw_data=raw_data)
            if isinstance(result.response, dict):
                result.response["tool_result"] = (
                    "Nothing was changed: their yes was to an earlier read-back, so this one is read to them again. "
                    + str(result.response.get("tool_result") or "")
                )
            return result
        op = self._operations[waiting["kind"]]
        writes = [Write.from_dict(w) for w in waiting.get("writes") or []]
        made, reply = await self._run_writes(
            call, op, writes, int(waiting.get("revision") or 0)
        )
        account = await self._account_text(call)
        data = call.data
        made_now = _made_text(list(waiting.get("done") or []), writes, made)
        tool_of = {k: o.tool for k, o in self._operations.items()}
        if made < len(writes):
            part = f" What went through first: {made_now}" if made else ""
            settled = _settle(data, f"not made: {reply}", made_now, made)
            settled["history"][-1]["writes_made"] = [w.to_dict() for w in writes[:made]]
            return self._finish(
                call,
                FunctionResult(
                    tool_result=f"The change didn't go through: {reply}.{part}",
                    tool_prompt=_GOING_ON + _next_up(data, tool_of),
                )
                .update_global_data(_update(data, **account, **settled))
                .swml_change_step(MAIN_STEP),
            )
        now = _settle(data, "made", made_now)
        total = _in_all(now["history"])
        result = FunctionResult(
            tool_result=f"Done. {made_now}{total}",
            tool_prompt=f"Tell them it's done{', and what it all comes to' if total else ''}."
            + (_next_up(data, tool_of) or " Ask if there's anything else."),
        )
        return self._finish(
            call,
            self.proposal.complete(made_now or "done", result)
            .update_global_data(_update(data, **account, **now))
            .swml_change_step(MAIN_STEP),
        )

    async def _decline(
        self, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        call = CallContext(self, raw_data)
        try:
            waiting = self._waiting_named(call, args)
        except Refuse as e:
            return _refused(e, "")
        tool_of = {k: o.tool for k, o in self._operations.items()}
        return (
            FunctionResult(
                tool_result=f'Nothing was changed: they don\'t want this change: "{waiting["read_back"]}"',
                tool_prompt="Tell them it's left as it was."
                + (_next_up(call.data, tool_of) or " Help with what they want next."),
            )
            .set_semantic_state({"declined": waiting["read_back"]})
            .update_global_data(_update(call.data, **_settle(call.data, "declined")))
            .swml_change_step(MAIN_STEP)
        )

    async def _identify(
        self, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        call = CallContext(self, raw_data)
        idn = self._identity
        assert idn is not None  # noqa: S101  # type narrowing: the tool exists only with an identity
        asked = str(args.get("asked_for") or call.data.get("asked") or "")
        keys = {k: args[k] for k in idn.fields if not _missing(args.get(k))}
        remember = _update(call.data, asked=asked)
        if idn.check_keys and not any(all(k in keys for k in s) for s in idn.any_of):
            return self._finish(
                call,
                FunctionResult(
                    tool_result=f"Nothing was looked up: it takes {idn.ask}.",
                    tool_prompt=f"Ask them for {idn.ask}, then call {idn.tool} with what they say.",
                ).update_global_data(remember),
            )
        try:
            found = await _maybe(idn.find(call, keys))
            if found is None or str(found).strip() == "":
                raise Refuse(
                    "No account was found with that.",
                    f"Ask them for {idn.ask} again, and check it with them.",
                )
            account_id = str(found)
        except Refuse as e:  # call.go is honoured: a lockout moves the call on
            return self._finish(call, _refused(e, "").update_global_data(remember))
        except Need as e:
            return self._finish(
                call,
                FunctionResult(
                    tool_result=f"Not found yet: {e.ask}",
                    tool_prompt=f"Ask them: {e.ask}",
                ).update_global_data(remember),
            )
        call.data["account_id"] = account_id
        text = (await self._account_text(call)).get("account", "")
        fresh = call.data.get("account_id") != _record_of(raw_data).get("account_id")
        update = {"account_id": account_id, "account": text, "asked": asked}
        if fresh and _record_of(raw_data).get(
            "account_id"
        ):  # a different account: nothing waits on the old one
            update.update(waiting={}, queued=[])
        found_it = FunctionResult(
            tool_result=f"Found their account. {text}".strip(),
            tool_prompt=(
                f"Help with what they asked for: {asked}"
                if asked
                else "Ask how you can help."
            ),
        ).update_global_data(_update(call.data, **update))
        return self._finish(
            call, found_it.swml_change_step(MAIN_STEP) if self._gated() else found_it
        )

    async def _transfer_handler(
        self, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        call = CallContext(self, raw_data)
        tr = self._transfer
        assert tr is not None  # noqa: S101  # type narrowing: the tool exists only with a transfer
        summary = str(args.get("summary") or "asked for a person")
        to = str(args.get("to") or "") if tr.destinations else ""
        if tr.destinations and to not in tr.destinations:
            return self._finish(
                call,
                FunctionResult(
                    tool_result=f"Not transferred: {to or 'nowhere'} isn't one of the places it goes.",
                    tool_prompt=f"Ask where they want to go: {_spoken_list(list(tr.destinations))}.",
                ),
            )
        try:
            handed = await _maybe(
                tr.fn(call, summary, to) if tr.destinations else tr.fn(call, summary)
            )
        except Refuse as e:  # call.go is honoured: a closed desk can move the call to take a message
            return self._finish(call, _refused(e, ""))
        result = FunctionResult(
            tool_result=f"The call is being transferred to {to or 'a person'}.",
            tool_prompt="Say nothing more; the transfer notice is playing.",
        ).say(tr.notice or self._transfer_notice)
        if isinstance(handed, FunctionResult):
            result.add_actions(handed.action)
        return self._finish(call, result.swml_change_context(TRANSFERRED), go=False)

    # ------------------------------------------------------------------ inspection

    def preview(self, agent: AgentBase | None = None) -> str:
        """
        What the model is given in each step: its text and its tools, plus
        the conscience, as plain text for review.

        Args:
            agent: An agent this was installed on; by default it's installed
                on a new one for the preview.
        """
        if agent is None:
            agent = self.install(AgentBase(name="preview", suppress_logs=True))
        contexts = agent.define_contexts().to_dict()
        lines = [
            f"Conscience: {(getattr(agent, '_params', {}) or {}).get('conscience', '')}",
            "",
        ]
        for cname, ctx in contexts.items():
            for step in ctx.get("steps") or []:
                lines.append(
                    f"== {cname}/{step.get('name')}  tools: {', '.join(step.get('functions') or []) or 'none'}"
                )
                lines.append(str(step.get("text") or ""))
                lines.append("")
        return "\n".join(lines)

    def record_text(self, global_data: Mapping[str, Any]) -> str:
        """The record's ``now`` line for a call's ``global_data``."""
        return _now_line(global_data)


class ServiceAgent(AgentBase):
    """
    An agent written as the operations it can do for a caller: the prefab
    over ``Operations``, installed before the first SWML or tool request.

    Example:
        agent = ServiceAgent("store", role="You answer the phone for an online store.")
        agent.identify(any_of=[["email"], ["first_name", "last_name", "zip"]], find=find_account)

        @agent.operation(tool="cancel_order")
        class Cancel(Operation):
            '''Cancel pending orders.'''
            ...
    """

    def __init__(
        self,
        name: str,
        *,
        role: str,
        rules: Sequence[str] | None = None,
        transfer_notice: str = "One moment, I'm transferring you to a person who can help.",
        **kwargs: Any,
    ) -> None:
        """
        Args:
            name: The agent's name.
            role: Who the agent is and how it sounds, the prompt's Role section.
            rules: The prompt's Rules section; defaults to ``DEFAULT_RULES``.
            transfer_notice: What the platform says as a transfer starts.
            **kwargs: Passed to ``AgentBase``.
        """
        super().__init__(name=name, **kwargs)
        self.ops = Operations(role=role, rules=rules, transfer_notice=transfer_notice)
        self._installed = False
        self._install_lock = threading.Lock()
        self.operation = self.ops.operation
        self.lookup = self.ops.lookup
        self.phase = self.ops.phase
        self.offer = self.ops.offer
        self.confirm_gates = self.ops.confirm_gates

    def identify(self, **kwargs: Any) -> ServiceAgent:
        """See ``Operations.identify``."""
        self.ops.identify(**kwargs)
        return self

    def writes_with(self, writer: Callable[..., Any]) -> ServiceAgent:
        """See ``Operations.writes_with``."""
        self.ops.writes_with(writer)
        return self

    def transfer_with(
        self, transfer: Callable[..., Any], **kwargs: Any
    ) -> ServiceAgent:
        """See ``Operations.transfer_with``."""
        self.ops.transfer_with(transfer, **kwargs)
        return self

    def on_swml_request(
        self,
        request_data: dict[str, Any] | None = None,
        callback_path: str | None = None,
        request: Any = None,
    ) -> dict[str, Any] | None:
        """Start the call identified when ``identify``'s ``prefill`` already knows the caller."""
        mods = super().on_swml_request(request_data, callback_path, request)
        if mods and mods.get("__use_ephemeral_agent"):
            return mods
        known = self.ops.prefilled(request_data, request)
        if not known:
            return mods
        mods = dict(mods or {})
        mods["global_data"] = {**(mods.get("global_data") or {}), **known}
        return mods

    def compile(self) -> ServiceAgent:
        """Install the operations on this agent, once; runs before the first SWML or tool request."""
        if not self._installed:
            # The first requests can come at once, on worker threads: one
            # installs, and the others wait for it rather than render a
            # half-installed agent
            with self._install_lock:
                if not self._installed:
                    self.ops.install(self)
                    self._installed = True
        return self

    def preview(self) -> str:
        """See ``Operations.preview``."""
        return self.ops.preview(self.compile())

    def _render_swml(
        self, call_id: str | None = None, modifications: dict[str, Any] | None = None
    ) -> str:
        self.compile()
        return super()._render_swml(call_id, modifications)

    def on_function_call(
        self, name: str, args: dict[str, Any], raw_data: dict[str, Any] | None = None
    ) -> Any:
        self.compile()
        return super().on_function_call(name, args, raw_data)


def _contribute(ctx: Any, name: str, text: str, tools: list[str]) -> Any:
    """
    A step with its text and its tools, and no way to leave on its own:
    handlers move it. A step another layer made already keeps what it has:
    the text and tools are added to its own (``Step._extend``).
    """
    step = ctx.get_step(name)
    if step is None:
        return (
            ctx.add_step(name)
            .set_text(text)
            .set_functions(list(tools))
            .set_valid_steps([])
        )
    return step._extend(text, tools, section="What else you can do")


def _offered(op: Operation, step: str) -> bool:
    return op.offered_in is None or step in op.offered_in


async def _maybe(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


def _refused(e: Refuse, prefix: str) -> FunctionResult:
    why = e.why if (not prefix or e.why.startswith("Nothing")) else prefix + e.why
    result = FunctionResult(tool_result=why, tool_prompt=e.then or _GOING_ON)
    return result.enable_extensive_data(False) if e.keep else result


def _made_text(done: Sequence[str], writes: Sequence[Write], made: int) -> str:
    """What went through, in the change's own words, or, where it has none for the writes made, the writes."""
    if not writes:
        return " ".join(d for d in done if d)
    said = " ".join(d for d in done[:made] if d)
    if said or made == 0 or made == len(writes):
        return said
    return (
        "; ".join(
            f"{w.name} ({', '.join(f'{k} {v}' for k, v in w.args.items())})"
            for w in writes[:made]
        )
        + "."
    )


def _with_not_said(f: Field) -> dict[str, Any]:
    """A field's schema; one that's asked for when missing takes "not said" as well, the model's honest answer."""
    schema = f.schema()
    if (
        f.ask
        and isinstance(schema.get("enum"), list)
        and NOT_SAID not in schema["enum"]
    ):
        schema["enum"] = [*schema["enum"], NOT_SAID]
    return schema


def _overrides(op: Operation, method: str) -> bool:
    return getattr(type(op), method) is not getattr(Operation, method)


def _why(e: Exception) -> str:
    return e.why if isinstance(e, Refuse) else e.ask if isinstance(e, Need) else str(e)


def _change_of(entry: Mapping[str, Any]) -> Change:
    return Change(
        read_back=str(entry.get("read_back") or ""),
        touches=list(entry.get("touches") or []),
        writes=[Write.from_dict(w) for w in entry.get("writes") or []],
        money=list(entry.get("money") or []),
        done=list(entry.get("done") or []),
    )


def _same_value(a: Any, b: Any) -> bool:
    return _normal(a) == _normal(b)


def _normal(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _same_request(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    return a.get("kind") == b.get("kind") and set(a.get("touches") or []) == set(
        b.get("touches") or []
    )


def _snake(name: str) -> str:
    return "".join(f"_{c.lower()}" if c.isupper() else c for c in name).lstrip("_")


def _spoken_list(items: Sequence[str]) -> str:
    items = list(items)
    if len(items) <= 1:
        return items[0] if items else ""
    return ", ".join(items[:-1]) + " and " + items[-1]


def _fillers(phrases: Any) -> dict[str, Any] | None:
    """Fillers as ``define_tool`` takes them: a list is en-US; lists by language code pass through."""
    if not phrases:
        return None
    return dict(phrases) if isinstance(phrases, Mapping) else {"en-US": list(phrases)}


def _transfer_gate() -> SemanticGate:
    return SemanticGate(
        "In their latest turns in `conversation`, has the caller asked to speak with a person, or said yes when the "
        "agent offered to transfer them to one?",
        threshold=0.8,
        id="wants_person",
        true_means="They asked for a person, a human, a representative or a supervisor, or said yes to being "
        "transferred to one.",
        false_means="They haven't asked for a person or said yes to being transferred.",
        on_fail=FunctionResult(
            tool_result="Not transferred: the caller hasn't asked for a person.",
            tool_prompt="Carry on helping them.",
        ).back_to_back_functions(False),
    )


__all__ = ["DEFAULT_RULES", "CallContext", "Operations", "ServiceAgent"]
