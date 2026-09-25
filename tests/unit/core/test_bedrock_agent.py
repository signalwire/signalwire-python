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
