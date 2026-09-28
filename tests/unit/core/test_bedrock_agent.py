"""
Tests for BedrockAgent's amazon_bedrock rendering.

BedrockAgent stored max_tokens but never rendered it (B12), dropped the
presence_penalty and frequency_penalty settings the Bedrock prompt object
defines (B13), and its examples used a voice Bedrock does not offer (B14).
These tests render the document and validate it against the SWML schema.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from signalwire.agents.bedrock import BedrockAgent
from signalwire.utils.schema_utils import SchemaUtils

REPO = Path(__file__).resolve().parents[3]


def _render(agent: BedrockAgent) -> dict[str, Any]:
    document: dict[str, Any] = json.loads(agent._render_swml())
    return document


def _bedrock_verb(document: dict[str, Any]) -> dict[str, Any]:
    return next(
        v["amazon_bedrock"]
        for v in document["sections"]["main"]
        if "amazon_bedrock" in v
    )


@pytest.fixture
def agent() -> BedrockAgent:
    agent = BedrockAgent(
        name="bedrock", route="/bedrock", voice_id="tiffany", max_tokens=512
    )
    agent.set_prompt_text("You are a helpful assistant.")
    agent.set_prompt_llm_params(
        presence_penalty=0.3,
        frequency_penalty=0.2,
        confidence=0.5,
        barge_confidence=0.4,
    )
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


def test_an_unoffered_voice_is_accepted_and_the_offered_ones_are_annotated() -> None:
    """Bedrock refuses a voice outside its five (bedrock_config.cpp:224), but that refusal
    happens behind a SWML handler that DISCARDS relay's reply (mod_infrastructure
    `relay_result_discarded`, swml.c:5450): no SWML error, execution continues, the verb just
    does not run. Owner ruling 2026-09-27 -- a rejection the handler does not surface is
    "silently ignored" -> OPEN, with the offered voices stated as `x-known-values`."""
    agent = BedrockAgent(name="bedrock", route="/bedrock", voice_id="inworld.Mark")
    agent.set_prompt_text("You are a helpful assistant.")
    ok, errors = SchemaUtils().validate_document(_render(agent))
    assert ok, errors
    schema = json.loads(
        (REPO / "signalwire" / "signalwire" / "schema.json").read_text()
    )
    body = schema["$defs"]["AmazonBedrock"]["properties"]["amazon_bedrock"]
    obj = next(a for a in body["anyOf"] if a.get("type") == "object")
    voice = obj["properties"]["prompt"]["properties"]["voice_id"]
    arms = [voice, *voice.get("anyOf", [])]
    known = [a["x-known-values"] for a in arms if "x-known-values" in a]
    assert known and set(known[0]) == {"tiffany", "matthew", "amy", "lupe", "carlos"}
    assert not any("enum" in a for a in arms)


def test_examples_use_voices_bedrock_offers() -> None:
    allowed = {"tiffany", "matthew", "amy", "lupe", "carlos"}
    for example in sorted((REPO / "examples").glob("bedrock_*.py")):
        text = example.read_text()
        for line in text.splitlines():
            if "voice_id=" in line:
                voice = line.split("voice_id=")[1].split('"')[1]
                assert voice in allowed, f"{example.name}: {voice}"
