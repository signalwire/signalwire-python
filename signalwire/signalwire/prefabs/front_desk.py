"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

A business's front desk, built on ``signalwire.operations``: it puts callers
through to the department they ask for while it's taking calls, books
appointments, takes messages and answers from the business's documents,
each when you give it one.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from signalwire.core.function_result import FunctionResult
from signalwire.operations import Appointments, Messages, Refuse, ServiceAgent
from signalwire.operations.infobot import InfoBotKnowledge
from signalwire.operations.wording import _Wording


@dataclass(frozen=True)
class Department:
    """Where the front desk puts a caller through to."""

    description: str
    """What callers go to it for, as the model reads it: "questions about a bill"."""
    to: str
    """Where the call goes: a phone number in E.164 form, or a SIP address."""
    open: Callable[[Any], Any] | None = None
    """``open(call)`` says whether it's taking calls now (it may be ``async``); None for always."""


FRONT_DESK_WORDING: Mapping[str, str] = MappingProxyType(
    {
        "closed": "{department} isn't taking calls now.",
        "closed.then": "Tell them, and offer to take a message with {tool}.",
        "closed.then.no_messages": "Tell them, and ask how else you can help.",
    }
)
"""Every key ``FrontDeskAgent``'s own words come from, with its default. The
rest of its words are its ``Operations``' and the packs'."""


class FrontDeskAgent(ServiceAgent):
    """
    A business's front desk: departments to put callers through to,
    appointments, messages and answers from its documents, each when given.

    Example:
        desk = FrontDeskAgent(
            role="You answer the phone for Bayside Dental. You are warm and brief.",
            departments={
                "billing": Department("questions about a bill", "+15550100001", open=billing_hours),
                "the hygienist": Department("questions about a cleaning", "+15550100002"),
            },
            appointments=Appointments(openings=calendar.open_near, book=calendar.book),
            messages=Messages(save=inbox.add),
            knowledge=InfoBotKnowledge(search=search_faq),
        )
    """

    def __init__(
        self,
        name: str = "front_desk",
        *,
        role: str,
        departments: Mapping[str, Department] | None = None,
        appointments: Appointments | None = None,
        messages: Messages | None = None,
        knowledge: InfoBotKnowledge | None = None,
        caller_id: str | None = None,
        desk_wording: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            name: The agent's name.
            role: Who the agent is and how it sounds, the prompt's Role
                section.
            departments: Where callers can be put through to, by the name
                callers use for it.
            appointments: The ``Appointments`` pack, to book them.
            messages: The ``Messages`` pack, to take them, and to offer when
                a department isn't taking calls.
            knowledge: An ``InfoBotKnowledge`` to answer from the business's
                documents; it's offered before the caller is identified.
            caller_id: The number calls put through come from; the
                platform's default when None.
            desk_wording: Words in place of the desk's own defaults, by key;
                the keys are those of ``FRONT_DESK_WORDING``.
            **kwargs: ``ServiceAgent``'s: ``Operations``' keyword arguments
                (``rules``, ``wording``, ``currency``, ``medium`` and the
                rest) and ``AgentBase``'s.
        """
        super().__init__(name, role=role, **kwargs)
        self._w_desk = _Wording(
            FRONT_DESK_WORDING, desk_wording, "FrontDeskAgent", "FRONT_DESK_WORDING"
        )
        self._departments = dict(departments or {})
        self._messages = messages
        self._caller_id = caller_id
        if knowledge is not None:
            knowledge.install(self)
            self.offer(*knowledge.tools, before_identity=True)
        if appointments is not None:
            appointments.add_to(self)
        if messages is not None:
            messages.add_to(self)
        if self._departments:
            self.transfer_with(
                self._put_through,
                destinations={k: d.description for k, d in self._departments.items()},
                gated=False,
            )

    async def _put_through(self, call: Any, summary: str, to: str) -> FunctionResult:
        department = self._departments[to]
        if department.open is not None:
            taking = department.open(call)
            if inspect.isawaitable(taking):
                taking = await taking
            if not taking:
                w = self._w_desk
                raise Refuse(
                    w("closed", department=to),
                    w("closed.then", tool=self._messages.tool)
                    if self._messages is not None
                    else w("closed.then.no_messages"),
                )
        return FunctionResult().connect(
            department.to, final=True, from_addr=self._caller_id
        )


__all__ = ["FRONT_DESK_WORDING", "Department", "FrontDeskAgent"]
