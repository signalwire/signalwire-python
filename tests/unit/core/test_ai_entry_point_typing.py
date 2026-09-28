"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Static typing of the SWML entry points that take schema-defined shapes.

``SWMLBuilder.ai(**kwargs)``, ``AgentBase.set_params`` and ``AgentBase.set_param``
are typed from the TypedDicts generated from schema.json (``_AiConfigKwargs``,
``AiParams`` and the per-key ``_AiParamsSetters`` overloads), and ``connect``'s
``from`` key is declared in the generated ``ConnectConfig``.

This module is in the TYPECHECK gate's scope (mypy --strict over ``tests``, which
includes ``warn_unused_ignores``). Each ``# type: ignore[<code>]`` below is a
NEGATIVE CONTROL: it marks a call mypy must reject. If the typing stopped rejecting
the call, the ignore would be unused and the gate would fail on it. The calls
without an ignore are the positive cases: they must type-check as written.

The tests also run, and show the rendered SWML is what these calls rendered before
the entry points were typed: typing is static only, and nothing is validated at
runtime.
"""

import json
from typing import Any
from unittest.mock import Mock

import pytest

from signalwire.core.agent_base import AgentBase
from signalwire.core.swml_builder import SWMLBuilder
from signalwire.core.swml_service import SWMLService


def _builder() -> SWMLBuilder:
    return SWMLBuilder(SWMLService(name="typing_test", schema_validation=False))


def _main(builder: SWMLBuilder) -> list[Any]:
    main: list[Any] = builder.build()["sections"]["main"]
    return main


def _agent() -> AgentBase:
    with pytest.MonkeyPatch().context() as m:
        m.setattr("signalwire.core.agent_base.uvicorn", Mock())
        return AgentBase(name="typing_test", schema_validation=False, use_pom=False)


def _ai_params(agent: AgentBase) -> dict[str, Any]:
    doc = json.loads(agent._render_swml())
    ai_verb = next(
        v for v in doc["sections"]["main"] if isinstance(v, dict) and "ai" in v
    )
    params: dict[str, Any] = ai_verb["ai"]["params"]
    return params


class TestSWMLBuilderAi:
    def test_typed_kwargs_render_unchanged(self) -> None:
        builder = _builder()
        builder.ai(
            prompt_text="You are helpful",
            post_prompt="Summarize",
            post_prompt_url="https://example.com/summary",
            params={"end_of_speech_timeout": 700, "attention_timeout": 10000},
            languages=[{"name": "English", "code": "en-US", "voice": "rime.spore"}],
            hints=["SignalWire"],
            global_data={"customer": "Ada"},
            voice="en-US-Neural2-F",
        )
        assert _main(builder) == [
            {
                "ai": {
                    "prompt": {"text": "You are helpful"},
                    "post_prompt": {"text": "Summarize"},
                    "post_prompt_url": "https://example.com/summary",
                    "params": {
                        "end_of_speech_timeout": 700,
                        "attention_timeout": 10000,
                    },
                    "languages": [
                        {"name": "English", "code": "en-US", "voice": "rime.spore"}
                    ],
                    "hints": ["SignalWire"],
                    "global_data": {"customer": "Ada"},
                    "voice": "en-US-Neural2-F",
                }
            }
        ]

    def test_prompt_and_swaig_kwargs_override_the_named_forms(self) -> None:
        # ``prompt`` and ``SWAIG`` are ai config keys, so they are typed kwargs too;
        # passed alongside the named shorthand, the kwarg wins (config.update order).
        builder = _builder()
        builder.ai(
            prompt_text="ignored",
            prompt={"text": "You are a pirate", "temperature": 0.3},
            SWAIG={"functions": [{"function": "lookup", "description": "Look up"}]},
        )
        assert _main(builder) == [
            {
                "ai": {
                    "prompt": {"text": "You are a pirate", "temperature": 0.3},
                    "SWAIG": {
                        "functions": [{"function": "lookup", "description": "Look up"}]
                    },
                }
            }
        ]

    def test_unknown_key_rejected_statically_passed_through_at_runtime(self) -> None:
        builder = _builder()
        builder.ai(prompt_text="x", temperature=0.7)  # type: ignore[call-arg]  # not an ai config key
        assert _main(builder) == [{"ai": {"prompt": {"text": "x"}, "temperature": 0.7}}]

    def test_wrong_value_type_rejected_statically(self) -> None:
        builder = _builder()
        builder.ai(prompt_text="x", hints="SignalWire")  # type: ignore[arg-type]  # hints is a list
        builder.ai(prompt_text="x", params={"end_of_speech_timeout": [700]})  # type: ignore[typeddict-item]  # int | str
        builder.ai(prompt_text="x", params={"temperature": 0.7})  # type: ignore[typeddict-unknown-key]  # not an AiParams key
        assert len(_main(builder)) == 3


class TestSetParams:
    def test_typed_params_render_unchanged(self) -> None:
        agent = _agent()
        agent.set_params({"end_of_speech_timeout": 700, "enable_barge": False})
        agent.set_param("attention_timeout", 10000)
        agent.set_param("ai_model", "gpt-4.1-nano")
        assert _ai_params(agent) == {
            "end_of_speech_timeout": 700,
            "enable_barge": False,
            "attention_timeout": 10000,
            "ai_model": "gpt-4.1-nano",
        }

    def test_setters_return_the_agent(self) -> None:
        agent = _agent()
        assert agent.set_param("end_of_speech_timeout", 700) is agent
        assert agent.set_params({"attention_timeout": 10000}) is agent

    def test_unknown_key_rejected_statically_stored_at_runtime(self) -> None:
        agent = _agent()
        agent.set_params({"temperature": 0.5})  # type: ignore[typeddict-unknown-key]  # prompt-level, not a param
        agent.set_param("barge_confidence", 1.0)  # type: ignore[call-overload]  # not an AiParams key
        assert _ai_params(agent) == {"temperature": 0.5, "barge_confidence": 1.0}

    def test_wrong_value_type_rejected_statically(self) -> None:
        agent = _agent()
        agent.set_params({"end_of_speech_timeout": [700]})  # type: ignore[typeddict-item]  # int | str
        agent.set_param("end_of_speech_timeout", [700])  # type: ignore[call-overload]  # int | str
        assert _ai_params(agent) == {"end_of_speech_timeout": [700]}


class TestConnectFrom:
    def test_from_key_typed_and_rendered(self) -> None:
        builder = _builder()
        builder.connect({"from": "+15551230000", "to": "+15554560000", "timeout": 30})
        assert _main(builder) == [
            {"connect": {"from": "+15551230000", "to": "+15554560000", "timeout": 30}}
        ]

    def test_wrong_from_type_rejected_statically(self) -> None:
        builder = _builder()
        builder.connect({"from": 15551230000, "to": "+15554560000"})  # type: ignore[arg-type]  # from is a string
        assert _main(builder) == [
            {"connect": {"from": 15551230000, "to": "+15554560000"}}
        ]
