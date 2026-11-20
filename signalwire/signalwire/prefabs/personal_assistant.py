"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

A personal assistant for one person, built on ``signalwire.operations``: it
asks who's calling and why, puts the call through when the person takes it,
and otherwise takes a message or books time on their calendar, each when you
give it one.

Putting a call through rings the person with a whisper: who is calling and
why, and a key to press to take it. The caller hears ringing meanwhile. If
the person doesn't answer or doesn't take it, the assistant carries on with
the caller. In a chat (``call.medium``), nobody is put through: the
assistant offers a message or a time instead.
"""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

from signalwire.core.function_result import FunctionResult
from signalwire.operations import (
    Appointments,
    Change,
    Field,
    Messages,
    Operation,
    ServiceAgent,
)
from signalwire.operations.agent import _Said
from signalwire.operations.infobot import InfoBotKnowledge
from signalwire.operations.wording import _Wording

ASSISTANT_WORDING: Mapping[str, str] = MappingProxyType(
    {
        "tool": "Put the caller through to {owner}, once they've said who they are and what it's about.",
        "tool.name": "Who is calling, as they said it.",
        "tool.reason": "What it's about, in a few words.",
        "ask.name": "Who's calling?",
        "ask.reason": "What's it about?",
        "whisper": "{name} is calling about {reason}. Press {key} to take the call.",
        "trying": "Seeing whether {owner} can take it.",
        "trying.then": "Tell them you'll see if {owner} can take it, and say nothing more.",
        "unavailable": "{owner} isn't taking calls now.",
        "chat": "{owner} can't be put through from a chat.",
        "not_taken": "{owner} didn't take the call (${connect_failed_reason}).",
        "then.message": "Tell them, and offer to take a message with {tool}.",
        "then.appointment": "Tell them, and offer to find a time with {tool}.",
        "then.message_or_appointment": "Tell them, and offer to take a message with {message} or find a time "
        "with {appointment}.",
        "then.nothing": "Tell them, and ask how else you can help.",
    }
)
"""Every key ``PersonalAssistantAgent``'s own words come from, with its
default (``PersonalAssistantAgent.WORDING``). The rest are its
``Operations``' and the packs'."""

_VARIABLE = re.compile(r"[$%]\{")


class PersonalAssistantAgent(ServiceAgent):
    """
    Answers the phone for one person: screens callers, puts them through when
    the person takes the call, and otherwise takes a message or books time.

    Example:
        assistant = PersonalAssistantAgent(
            role="You answer Ann Lee's phone. You are friendly and brief.",
            owner="Ann",
            reach="+15550100001",
            available=lambda call: not calendar.busy_now(),
            messages=Messages(save=lambda call, message: send_text(ANN, message)),
            appointments=Appointments(openings=calendar.open_near, book=calendar.book),
        )
    """

    WORDING: Mapping[str, str] = ASSISTANT_WORDING
    """Every key the assistant's own words come from, with its default; ``assistant_wording`` replaces any."""

    def __init__(
        self,
        name: str = "assistant",
        *,
        role: str,
        owner: str,
        reach: str,
        available: Callable[[Any], Any] | None = None,
        messages: Messages | None = None,
        appointments: Appointments | None = None,
        knowledge: InfoBotKnowledge | None = None,
        caller_id: str | None = None,
        ring_seconds: int = 20,
        answer_seconds: int = 15,
        whisper_voice: str | None = None,
        whisper_language: str | None = None,
        accept_key: str = "1",
        tool: str = "put_through",
        assistant_wording: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            name: The agent's name.
            role: Who the agent is and how it sounds, the prompt's Role
                section.
            owner: The person's name, as the assistant says it.
            reach: Where their calls go: a phone number in E.164 form, or a
                SIP address.
            available: ``available(call)`` says whether they're taking calls
                now (it may be ``async``); None for always. When they aren't,
                the call isn't put through.
            messages: The ``Messages`` pack, to take a message when they
                don't take the call.
            appointments: The ``Appointments`` pack, for their calendar.
            knowledge: An ``InfoBotKnowledge`` to answer questions from.
            caller_id: The number the put-through call comes from; None for
                the caller's own, so the person sees who it is.
            ring_seconds: How long to ring them.
            answer_seconds: How long they have, once they answer, to take
                the call.
            whisper_voice: The voice they hear the whisper in; the
                platform's default when None.
            whisper_language: The whisper's language code, such as
                ``"en-US"``; the platform's default when None.
            accept_key: The key they press to take the call.
            tool: The put-through tool's name.
            assistant_wording: Words in place of the assistant's own
                defaults, by key; the keys are those of
                ``PersonalAssistantAgent.WORDING``.
            **kwargs: ``ServiceAgent``'s: ``Operations``' keyword arguments
                and ``AgentBase``'s.
        """
        super().__init__(name, role=role, **kwargs)
        self._w_assistant = _Wording(
            ASSISTANT_WORDING,
            assistant_wording,
            "PersonalAssistantAgent",
            "PersonalAssistantAgent.WORDING",
        )
        self.owner, self._reach, self._available = owner, reach, available
        self._caller_id = caller_id
        self._ring, self._answer = ring_seconds, answer_seconds
        self._voice, self._language = whisper_voice, whisper_language
        if not (len(accept_key) == 1 and accept_key in "0123456789*#"):
            raise ValueError(
                f"accept_key must be one key of the keypad, not {accept_key!r}"
            )
        self._key = accept_key
        self._message_tool = messages.tool if messages is not None else None
        self._appointment_tool = (
            appointments.tools["openings"] if appointments is not None else None
        )
        if knowledge is not None:
            knowledge.install(self)
            self.offer(*knowledge.tools, before_identity=True)
        if messages is not None:
            messages.add_to(self)
        if appointments is not None:
            appointments.add_to(self)
        self._add_put_through(tool)

    def _otherwise(self) -> str:
        """What the model is told to offer when the call isn't put through."""
        w, message, appointment = (
            self._w_assistant,
            self._message_tool,
            self._appointment_tool,
        )
        if message and appointment:
            return w(
                "then.message_or_appointment", message=message, appointment=appointment
            )
        if message:
            return w("then.message", tool=message)
        if appointment:
            return w("then.appointment", tool=appointment)
        return w("then.nothing")

    def _add_put_through(self, tool: str) -> None:
        w, assistant = self._w_assistant, self
        fields = {
            "name": Field(str, w("tool.name"), ask=w("ask.name")),
            "reason": Field(str, w("tool.reason"), ask=w("ask.reason")),
        }

        async def prepare(self: Operation, call: Any, f: Any) -> Change:
            if call.medium == "chat":  # connecting is a call's
                raise _Said(w("chat", owner=assistant.owner), assistant._otherwise())
            if assistant._available is not None:
                taking = assistant._available(call)
                if inspect.isawaitable(taking):
                    taking = await taking
                if not taking:
                    raise _Said(
                        w("unavailable", owner=assistant.owner), assistant._otherwise()
                    )
            call.act(
                FunctionResult().execute_swml(assistant._ring_them(f.name, f.reason))
            )
            return Change(
                read_back="",
                done=w("trying", owner=assistant.owner),
                then=w("trying.then", owner=assistant.owner),
            )

        cls = type(
            "PutThrough",
            (Operation,),
            {
                "__doc__": w("tool", owner=self.owner),
                "prepare": prepare,
                "confirm": False,
                "before_identity": True,
                **fields,
            },
        )
        self.operation(cls, tool=tool, kind=tool)

    def _ring_them(self, name: str, reason: str) -> dict[str, Any]:
        """
        The SWML that rings them with the whisper. Their leg hears it once
        they answer, and the call is bridged only when they press the
        accept key; any other key, or none, hangs their leg up and the caller stays with the
        assistant. Once a bridged call ends, so does the caller's.
        """
        w = self._w_assistant
        whisper = w(
            "whisper", name=_spoken(name), reason=_spoken(reason), key=self._key
        )
        prompt: dict[str, Any] = {
            "play": f"say:{whisper}",
            "max_digits": 1,
            "initial_timeout": self._answer,
        }
        if self._voice:
            prompt["say_voice"] = self._voice
        if self._language:
            prompt["say_language"] = self._language
        connect: dict[str, Any] = {
            "to": self._reach,
            "timeout": self._ring,
            "confirm": [
                {"prompt": prompt},
                {
                    "switch": {
                        "variable": "prompt_value",
                        "case": {self._key: [{"set": {"screened": "taken"}}]},
                        "default": [{"hangup": {}}],
                    }
                },
            ],
            # From their answer: the whisper, then the time they have to press the key
            "confirm_timeout": self._answer + 30,
        }
        if self._caller_id:
            connect["from"] = self._caller_id
        not_taken = w("not_taken", owner=self.owner) + " " + self._otherwise()
        return {
            "version": "1.0.0",
            "sections": {
                "main": [
                    {"connect": connect},
                    {
                        "switch": {
                            "variable": "connect_result",
                            "case": {"connected": [{"hangup": {}}]},
                            "default": [{"set": {"ai_response": not_taken}}],
                        }
                    },
                ]
            },
        }


def _spoken(text: str) -> str:
    """A caller's words for the whisper, with nothing the platform would read as a variable."""
    return _VARIABLE.sub("", str(text)).strip()


__all__ = ["PersonalAssistantAgent"]
