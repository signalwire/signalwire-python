"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Voices with fallbacks (a voice field takes a list, the first speaking and the
rest tried in order when it fails), the default voice, duration strings,
calling.error's voice fields, and gather questions the platform says itself.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from signalwire import AgentBase, FunctionResult
from signalwire.relay.event import CallingErrorEvent

CHAIN = ["elevenlabs.rachel:eleven_turbo_v2_5", "rime.spore", "gcloud.en-US-Neural2-F"]


def agent() -> AgentBase:
    a = AgentBase(name="v", suppress_logs=True)
    a.prompt_add_section("Role", body="You help.")
    return a


def main_of(a: AgentBase, modifications: dict[str, Any] | None = None) -> list[Any]:
    return list(json.loads(a._render_swml(None, modifications))["sections"]["main"])


def ai_of(a: AgentBase) -> dict[str, Any]:
    return next(v["ai"] for v in main_of(a) if isinstance(v, dict) and "ai" in v)


def test_an_agent_with_no_voice_settings_renders_as_before() -> None:
    # Nothing new is sent unless the agent asks for it
    assert json.loads(AgentBase(name="v", suppress_logs=True)._render_swml()) == {
        "version": "1.0.0",
        "sections": {
            "main": [{"answer": {}}, {"ai": {"prompt": {"pom": []}, "params": {}}}]
        },
    }
    a = agent().add_language("English", "en-US", "elevenlabs.josh:eleven_turbo_v2_5")
    a.set_params({"end_of_speech_timeout": 700, "attention_timeout": 15000})
    main = main_of(a)
    assert main[0] == {"answer": {}} and len(main) == 2
    ai = main[1]["ai"]
    assert set(ai) == {"prompt", "params", "languages"}
    assert ai["languages"] == [
        {
            "name": "English",
            "code": "en-US",
            "voice": "josh",
            "engine": "elevenlabs",
            "model": "eleven_turbo_v2_5",
        }
    ]
    assert ai["params"] == {"end_of_speech_timeout": 700, "attention_timeout": 15000}


def test_a_language_takes_a_list_of_voices_as_sent() -> None:
    a = agent().add_language("English", "en-US", CHAIN)
    language = ai_of(a)["languages"][0]
    assert (
        language["voice"] == CHAIN
        and "engine" not in language
        and "model" not in language
    )
    one = agent().add_language("English", "en-US", "elevenlabs.josh:eleven_turbo_v2_5")
    assert ai_of(one)["languages"][0] == {
        "name": "English",
        "code": "en-US",
        "voice": "josh",
        "engine": "elevenlabs",
        "model": "eleven_turbo_v2_5",
    }
    with pytest.raises(ValueError, match="engine= and model= are for one voice"):
        agent().add_language("English", "en-US", CHAIN, engine="elevenlabs")
    with pytest.raises(ValueError, match="at most 8"):
        agent().add_language("English", "en-US", [f"rime.v{i}" for i in range(9)])
    with pytest.raises(ValueError, match="non-empty"):
        agent().add_language("English", "en-US", ["rime.spore", ""])


def test_the_agents_voice_and_fallback_voice_are_the_ai_verbs_own() -> None:
    a = agent().set_agent_voice(CHAIN).set_fallback_voice("gcloud.en-US-Neural2-C")
    ai = ai_of(a)
    assert ai["voice"] == CHAIN and ai["fallback_voice"] == "gcloud.en-US-Neural2-C"
    a.set_agent_voice(None).set_fallback_voice(None)
    assert "voice" not in ai_of(a) and "fallback_voice" not in ai_of(a)


@pytest.mark.parametrize(
    "voice",
    [
        "rime.spore",
        CHAIN,
        {"es": ["elevenlabs.lucia", "rime.luna"], "default": "rime.spore"},
    ],
)
def test_the_default_voice_is_set_just_before_the_ai_verb(voice: Any) -> None:
    a = agent().set_default_voice(voice)
    main = main_of(a)
    at = next(i for i, v in enumerate(main) if isinstance(v, dict) and "ai" in v)
    assert main[at - 1] == {"set": {"default_voice": voice}}
    # A per-request copy renders it the same way
    a.set_dynamic_config_callback(lambda q, b, h, copy: None)
    marker = a.on_swml_request({})
    copied = main_of(a, marker)
    at = next(i for i, v in enumerate(copied) if isinstance(v, dict) and "ai" in v)
    assert copied[at - 1] == {"set": {"default_voice": voice}}
    assert not any("set" in v for v in main_of(agent()) if isinstance(v, dict))


def test_a_default_voice_by_language_is_checked() -> None:
    with pytest.raises(ValueError, match="codes"):
        agent().set_default_voice({"": "rime.spore"})
    with pytest.raises(ValueError, match="at most 8"):
        agent().set_default_voice({"default": [f"rime.v{i}" for i in range(9)]})


def test_change_voice_takes_a_list() -> None:
    assert FunctionResult("ok").change_voice(CHAIN).to_dict()["action"] == [
        {"change_voice": CHAIN}
    ]
    assert FunctionResult("ok").change_voice("rime.spore").to_dict()["action"] == [
        {"change_voice": "rime.spore"}
    ]
    with pytest.raises(ValueError):
        FunctionResult("ok").change_voice([])


def test_timeouts_take_durations() -> None:
    r = (
        FunctionResult("ok")
        .set_end_of_speech_timeout("1.5s")
        .set_speech_event_timeout(800)
    )
    assert r.to_dict()["action"] == [
        {"end_of_speech_timeout": "1.5s"},
        {"speech_event_timeout": 800},
    ]
    assert FunctionResult("ok").hold(timeout="2m").to_dict()["action"] == [
        {"hold": "2m"}
    ]
    assert FunctionResult("ok").hold(timeout=1200).to_dict()["action"] == [
        {"hold": 900}
    ]
    with pytest.raises(ValueError, match="duration"):
        FunctionResult("ok").hold(timeout=" ")


def test_calling_error_carries_the_voice_that_failed_and_the_one_that_took_over() -> (
    None
):
    event = CallingErrorEvent.from_payload(
        {
            "event_type": "calling.error",
            "params": {
                "call_id": "c1",
                "error": "ai: Speech error\n",
                "error_reason": "voice_runtime_error",
                "engine": "elevenlabs",
                "language_code": "en-US",
                "voice": "rachel",
                "model": "eleven_turbo_v2_5",
                "fallback_engine": "rime",
                "fallback_language_code": "en-US",
                "fallback_voice": "spore",
                "fallback_model": "",
                "fallback_index": 1,
                "fallback_source": "voice",
            },
        }
    )
    assert (
        event.error_reason,
        event.voice,
        event.fallback_voice,
        event.fallback_index,
        event.fallback_source,
    ) == ("voice_runtime_error", "rachel", "spore", 1, "voice")
    assert not event.fatal and event.stall_ms is None
    fatal = CallingErrorEvent.from_payload(
        {
            "event_type": "calling.error",
            "params": {
                "error": "ai: no usable TTS voice.\n",
                "fatal": True,
                "error_reason": "voice_unrecoverable",
            },
        }
    )
    assert fatal.fatal and fatal.fallback_index is None


def test_a_gather_can_have_the_platform_say_its_questions() -> None:
    a = agent()
    step = (
        a.define_contexts()
        .add_context("default")
        .add_step("intake")
        .set_text("Gather their details.")
    )
    step.set_gather_info(say_questions=True)
    step.add_gather_question("name", "What's your name?")
    step.add_gather_question("reason", "What can we help with?", say=False)
    gather = ai_of(a)["prompt"]["contexts"]["default"]["steps"][0]["gather_info"]
    assert gather["say_questions"] is True
    assert (
        "say" not in gather["questions"][0] and gather["questions"][1]["say"] is False
    )
