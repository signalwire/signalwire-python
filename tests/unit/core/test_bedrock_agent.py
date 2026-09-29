"""
Tests for BedrockAgent's amazon_bedrock rendering.

BedrockAgent stored max_tokens but never rendered it (B12), dropped the
presence_penalty and frequency_penalty settings the Bedrock prompt object
defines (B13), and its examples used a voice the schema rejects (B14).
These tests render the document and validate it against the SWML schema.
"""

import json
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from signalwire.agents.bedrock import BedrockAgent
from signalwire.utils.schema_utils import SchemaUtils

REPO = Path(__file__).resolve().parents[3]


def _render(agent: BedrockAgent) -> dict[str, Any]:
    document: dict[str, Any] = json.loads(agent._render_swml())
    return document


def _bedrock_verb(document: dict[str, Any]) -> dict[str, Any]:
    return next(v["amazon_bedrock"] for v in document["sections"]["main"] if "amazon_bedrock" in v)


@pytest.fixture
def agent() -> BedrockAgent:
    agent = BedrockAgent(name="bedrock", route="/bedrock", voice_id="tiffany", max_tokens=512)
    agent.set_prompt_text("You are a helpful assistant.")
    agent.set_prompt_llm_params(presence_penalty=0.3, frequency_penalty=0.2, confidence=0.5, barge_confidence=0.4)
    return agent


def test_prompt_carries_max_tokens(agent: BedrockAgent) -> None:
    assert _bedrock_verb(_render(agent))["prompt"]["max_tokens"] == 512


def test_set_inference_params_updates_max_tokens(agent: BedrockAgent) -> None:
    agent.set_inference_params(max_tokens=2048)
    assert _bedrock_verb(_render(agent))["prompt"]["max_tokens"] == 2048


def test_prompt_keeps_settings_the_bedrock_schema_defines(agent: BedrockAgent) -> None:
    prompt = _bedrock_verb(_render(agent))["prompt"]
    assert prompt["presence_penalty"] == 0.3
    assert prompt["frequency_penalty"] == 0.2
    assert prompt["confidence"] == 0.5
    assert "barge_confidence" not in prompt
    assert prompt["voice_id"] == "tiffany"


def test_rendered_document_is_valid_swml(agent: BedrockAgent) -> None:
    ok, errors = SchemaUtils().validate_document(_render(agent))
    assert ok, errors


def test_schema_rejects_a_voice_bedrock_does_not_offer() -> None:
    agent = BedrockAgent(name="bedrock", route="/bedrock", voice_id="inworld.Mark")
    agent.set_prompt_text("You are a helpful assistant.")
    ok, _ = SchemaUtils().validate_document(_render(agent))
    assert not ok


def test_examples_use_voices_bedrock_offers() -> None:
    allowed = {"tiffany", "matthew", "amy", "lupe", "carlos"}
    for example in sorted((REPO / "examples").glob("bedrock_*.py")):
        text = example.read_text()
        for line in text.splitlines():
            if "voice_id=" in line:
                voice = line.split("voice_id=")[1].split('"')[1]
                assert voice in allowed, f"{example.name}: {voice}"


# -- Features the amazon_bedrock verb leaves out ---------------------------


def _warnings(log: Mock) -> list[str]:
    return [str(call.args[0]) for call in log.warning.call_args_list]


def test_dropped_features_warn_once_each() -> None:
    with patch("signalwire.agents.bedrock.logger") as log:
        agent = BedrockAgent(name="bedrock", route="/bedrock")
        agent.set_prompt_text("You are a helpful assistant.")
        agent.add_hints(["SignalWire"])
        agent.add_language("English", "en-US", "rime.spore")
        agent.add_pronunciation("API", "A P I")
        agent.set_multilingual({"languages": ["en-US", "es-US"]})
        first = _bedrock_verb(_render(agent))
        _render(agent)
        _render(agent)

    for key in ("hints", "languages", "pronounce", "multilingual"):
        assert key not in first
    messages = _warnings(log)
    assert len(messages) == 4
    assert any(
        "the amazon_bedrock verb has no hints" in m and "add_hints()" in m
        for m in messages
    )
    assert any("has no languages" in m and "add_language()" in m for m in messages)
    assert any("has no pronounce" in m and "add_pronunciation()" in m for m in messages)
    assert any("has no multilingual" in m for m in messages)


def test_contexts_are_left_out_with_a_warning() -> None:
    with patch("signalwire.agents.bedrock.logger") as log:
        agent = BedrockAgent(name="bedrock", route="/bedrock")
        agent.set_prompt_text("You are a helpful assistant.")
        contexts = agent.define_contexts()
        contexts.add_context("default").add_step("greet").set_text("Say hello.")
        prompt = _bedrock_verb(_render(agent))["prompt"]

    assert "contexts" not in prompt
    assert _warnings(log) == [
        "BedrockAgent: Bedrock's prompt has no contexts, so the agent's contexts "
        "and steps (define_contexts()) are left out of the SWML"
    ]


def test_no_warning_without_dropped_features(agent: BedrockAgent) -> None:
    with patch("signalwire.agents.bedrock.logger") as log:
        _render(agent)
    assert _warnings(log) == []


# -- Inference settings are numbers ----------------------------------------


def test_numeric_strings_are_converted() -> None:
    # Strings aren't in the annotated types, so they're passed as Any
    settings: dict[str, Any] = {"temperature": "0.5", "top_p": " 0.8 ", "max_tokens": "2048"}
    agent = BedrockAgent(name="bedrock", route="/bedrock", **settings)
    agent.set_prompt_text("You are a helpful assistant.")
    prompt = _bedrock_verb(_render(agent))["prompt"]
    assert prompt["temperature"] == 0.5
    assert prompt["top_p"] == 0.8
    assert prompt["max_tokens"] == 2048
    assert isinstance(prompt["max_tokens"], int)


def test_swml_variable_passes_through_for_temperature_and_top_p() -> None:
    agent = BedrockAgent(name="bedrock", route="/bedrock")
    agent.set_prompt_text("You are a helpful assistant.")
    variables: dict[str, Any] = {"temperature": "${temp}", "top_p": "%{tp}"}
    agent.set_inference_params(**variables)
    prompt = _bedrock_verb(_render(agent))["prompt"]
    assert prompt["temperature"] == "${temp}"
    assert prompt["top_p"] == "%{tp}"
    ok, errors = SchemaUtils().validate_document(_render(agent))
    assert ok, errors


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"temperature": "hot"}, "BedrockAgent temperature must be a number, got 'hot'"),
        ({"top_p": [0.9]}, "BedrockAgent top_p must be a number, got [0.9]"),
        ({"temperature": True}, "BedrockAgent temperature must be a number, got True"),
        ({"temperature": float("nan")}, "BedrockAgent temperature must be a number, got nan"),
        ({"max_tokens": "lots"}, "BedrockAgent max_tokens must be an integer, got 'lots'"),
        ({"max_tokens": 10.5}, "BedrockAgent max_tokens must be an integer, got 10.5"),
        ({"max_tokens": "${max}"}, "BedrockAgent max_tokens must be an integer, got '${max}'"),
    ],
)
def test_non_numeric_values_are_refused(kwargs: dict[str, Any], message: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        BedrockAgent(name="bedrock", route="/bedrock", **kwargs)
    assert str(excinfo.value) == message


def test_refused_value_changes_nothing(agent: BedrockAgent) -> None:
    with pytest.raises(ValueError, match="max_tokens must be an integer"):
        refused: dict[str, Any] = {"temperature": 0.1, "max_tokens": "many"}
        agent.set_inference_params(**refused)
    prompt = _bedrock_verb(_render(agent))["prompt"]
    assert prompt["temperature"] == 0.7
    assert prompt["max_tokens"] == 512


def test_set_prompt_llm_params_validates_inference_settings(agent: BedrockAgent) -> None:
    with pytest.raises(ValueError, match="top_p must be a number"):
        agent.set_prompt_llm_params(top_p="high")
    agent.set_prompt_llm_params(temperature="0.3")
    assert _bedrock_verb(_render(agent))["prompt"]["temperature"] == 0.3


def test_set_llm_temperature_validates(agent: BedrockAgent) -> None:
    with pytest.raises(ValueError, match="temperature must be a number"):
        warm: Any = "warm"
        agent.set_llm_temperature(warm)


# -- Warning wording --------------------------------------------------------


def test_ignored_prompt_setting_warning_is_singular_for_one_key() -> None:
    with patch("signalwire.agents.bedrock.logger") as log:
        BedrockAgent(name="bedrock", route="/bedrock").set_prompt_llm_params(
            barge_confidence=0.4
        )
    assert _warnings(log) == [
        "set_prompt_llm_params(): Bedrock's prompt doesn't define "
        "barge_confidence, so it's ignored"
    ]


def test_ignored_prompt_setting_warning_is_plural_for_several_keys() -> None:
    with patch("signalwire.agents.bedrock.logger") as log:
        BedrockAgent(name="bedrock", route="/bedrock").set_prompt_llm_params(
            barge_confidence=0.4, model="x"
        )
    assert _warnings(log) == [
        "set_prompt_llm_params(): Bedrock's prompt doesn't define "
        "barge_confidence, model, so they're ignored"
    ]
