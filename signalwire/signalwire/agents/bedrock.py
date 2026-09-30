"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Bedrock Agent - Amazon Bedrock voice-to-voice integration

This module provides BedrockAgent, which extends AgentBase to support
Amazon Bedrock's voice-to-voice model while maintaining compatibility
with all SignalWire agent features like skills, POM, and SWAIG functions.
"""

import json
import math
import re
from typing import Any
from signalwire.core.agent_base import AgentBase
from signalwire.core.logging_config import get_logger

logger = get_logger("bedrock_agent")

# A SWML variable reference, such as ${temperature}, which the schema accepts
# for temperature and top_p
_SWML_VAR = re.compile(r"^[$%]\{.*\}$")

# The keys the amazon_bedrock verb defines
_BEDROCK_VERB_KEYS = (
    "prompt",
    "SWAIG",
    "params",
    "global_data",
    "post_prompt",
    "post_prompt_url",
)

# The prompt keys copied from the ai verb's prompt. The platform's Bedrock
# session reads only these, voice_id, temperature and top_p; the last three
# are set from the agent's own settings, as is max_tokens.
_BEDROCK_PROMPT_KEYS = ("text", "pom")

# The prompt keys set from the agent's own settings
_AGENT_PROMPT_KEYS = ("voice_id", "temperature", "top_p", "max_tokens")

# What the ai verb keys the Bedrock verb or prompt leaves out are, for the
# warning
_FEATURE_NAMES = {
    "hints": "speech hints (add_hint(), add_hints() and skills' hints)",
    "languages": "languages (add_language())",
    "pronounce": "pronunciation rules (add_pronunciation())",
    "multilingual": "multilingual settings (set_multilingual())",
    "contexts": "contexts and steps (define_contexts())",
}


def _to_number(name: str, value: Any, *, integer: bool = False) -> Any:
    """Return ``value`` as a number for the Bedrock prompt, or raise.

    Accepts an int, a float or a numeric string. temperature and top_p may
    also be a SWML variable reference such as ``${temperature}``, which the
    schema allows and which is passed through as written.

    Raises:
        ValueError: If the value isn't a finite number (or an integer, for
            max_tokens).
    """
    if not integer and isinstance(value, str) and _SWML_VAR.match(value.strip()):
        return value.strip()
    kind = "an integer" if integer else "a number"
    if isinstance(value, bool):
        raise ValueError(f"BedrockAgent {name} must be {kind}, got {value!r}")
    try:
        number = float(value.strip() if isinstance(value, str) else value)
    except (TypeError, ValueError):
        raise ValueError(f"BedrockAgent {name} must be {kind}, got {value!r}") from None
    if not math.isfinite(number):
        raise ValueError(f"BedrockAgent {name} must be {kind}, got {value!r}")
    if integer:
        if not number.is_integer():
            raise ValueError(f"BedrockAgent {name} must be {kind}, got {value!r}")
        return int(number)
    return number


class BedrockAgent(AgentBase):
    """
    Agent implementation for Amazon Bedrock voice-to-voice model

    This agent extends AgentBase to provide full compatibility with
    SignalWire's agent ecosystem while using Amazon Bedrock as the
    AI backend. It supports all standard agent features including:
    - Prompt building with text and POM
    - Skills and SWAIG functions
    - Post-prompt functionality
    - Dynamic configuration

    The main difference from the standard agent is that it generates
    SWML with the "amazon_bedrock" verb instead of "ai". Speech hints,
    languages, pronunciation rules, multilingual settings and contexts
    aren't part of that verb, so they're left out of the SWML, with one
    warning per agent for each.
    """

    def __init__(
        self,
        name: str = "bedrock_agent",
        route: str = "/bedrock",
        system_prompt: str | None = None,
        voice_id: str = "matthew",
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> None:
        """
        Initialize BedrockAgent

        Args:
            name: Agent name
            route: HTTP route for the agent
            system_prompt: Initial system prompt (can be overridden with set_prompt)
            voice_id: Bedrock voice: tiffany, matthew, amy, lupe or carlos
                (default: matthew)
            temperature: Generation temperature (0-2)
            top_p: Nucleus sampling parameter (0-1)
            max_tokens: Maximum tokens to generate. The platform's Bedrock
                session doesn't read it; it uses 1024
            **kwargs: Additional arguments passed to AgentBase

        Raises:
            ValueError: If temperature or top_p isn't a number, or max_tokens
                isn't an integer
        """
        # Store Bedrock-specific parameters first
        self._voice_id = voice_id
        self._temperature = _to_number("temperature", temperature)
        self._top_p = _to_number("top_p", top_p)
        self._max_tokens = _to_number("max_tokens", max_tokens, integer=True)
        # Features already reported as left out of the amazon_bedrock verb,
        # so each is reported once per agent
        self._bedrock_dropped_warned: set[str] = set()

        # Initialize base class
        super().__init__(name=name, route=route, **kwargs)

        # Set initial prompt if provided (after super init)
        if system_prompt:
            self.set_prompt_text(system_prompt)

        logger.info(f"BedrockAgent initialized: {name} on route {route}")

    def _render_swml(
        self, call_id: str | None = None, modifications: dict[str, Any] | None = None
    ) -> str:
        """
        Render SWML document with amazon_bedrock verb

        This method overrides the base implementation to generate
        SWML with the amazon_bedrock verb structure that matches
        the ai verb structure for consistency.

        Args:
            call_id: Optional call ID for session-specific tokens
            modifications: Optional dict of modifications to apply

        Returns:
            SWML document as JSON string with amazon_bedrock verb
        """
        # Call parent to build the base SWML with ai verb
        base_swml_json = super()._render_swml(call_id, modifications)

        # Parse the JSON to modify it
        swml = json.loads(base_swml_json)

        # Find and transform the ai verb to amazon_bedrock
        sections = swml.get("sections", {})
        main_section = sections.get("main", [])

        # Look for ai verb and transform it
        for i, verb in enumerate(main_section):
            if "ai" in verb:
                ai_config = verb["ai"]

                # Build amazon_bedrock verb with same structure
                bedrock_verb = {
                    "amazon_bedrock": {
                        # Add voice configuration and inference params inside prompt
                        # Note: In Bedrock, voice and inference params are part of prompt config
                        "prompt": self._add_voice_to_prompt(
                            ai_config.get("prompt", {})
                        ),
                        # Copy SWAIG if present
                        "SWAIG": ai_config.get("SWAIG", {}),
                        # Include params only if they were explicitly set via set_params()
                        # The C++ code ignores params for now (marked for future extensibility)
                        "params": ai_config.get("params", {}),
                        # Copy global_data if present
                        "global_data": ai_config.get("global_data", {}),
                        # Copy post_prompt if present
                        "post_prompt": ai_config.get("post_prompt"),
                        # Copy post_prompt_url if present
                        "post_prompt_url": ai_config.get("post_prompt_url"),
                    }
                }

                # The ai verb's other keys (hints, languages, pronounce,
                # multilingual) have no place in the amazon_bedrock verb
                self._warn_dropped(
                    [key for key in ai_config if key not in _BEDROCK_VERB_KEYS],
                    "the amazon_bedrock verb has no",
                )

                # Remove None values
                bedrock_config = bedrock_verb["amazon_bedrock"]
                bedrock_verb["amazon_bedrock"] = {
                    k: v for k, v in bedrock_config.items() if v is not None
                }

                # Replace ai verb with amazon_bedrock verb
                main_section[i] = bedrock_verb
                break

        # Convert back to JSON string
        return json.dumps(swml)

    def _warn_dropped(self, keys: list[str], reason: str) -> None:
        """Log a warning, once per agent, for each feature left out of the SWML."""
        for key in keys:
            if key in self._bedrock_dropped_warned:
                continue
            self._bedrock_dropped_warned.add(key)
            if key in _FEATURE_NAMES:
                what = f"the agent's {_FEATURE_NAMES[key]} are"
            else:
                what = "it's"
            logger.warning(
                f"BedrockAgent: {reason} {key}, so {what} left out of the SWML"
            )

    def _add_voice_to_prompt(self, prompt_config: dict[str, Any]) -> dict[str, Any]:
        """
        Add voice configuration to the prompt object

        In Bedrock, voice configuration is part of the prompt object,
        not a separate field like in OpenAI.

        Args:
            prompt_config: Current prompt configuration

        Returns:
            Updated prompt configuration with voice
        """
        # Copy the prompt text. Anything else, such as confidence or
        # contexts, is left out: the platform's Bedrock session doesn't
        # read it.
        filtered_config = {
            key: value
            for key, value in prompt_config.items()
            if key in _BEDROCK_PROMPT_KEYS
        }
        # voice_id and the inference settings are replaced below, so only the
        # other keys are features the Bedrock prompt leaves out
        self._warn_dropped(
            [
                key
                for key in prompt_config
                if key not in _BEDROCK_PROMPT_KEYS and key not in _AGENT_PROMPT_KEYS
            ],
            "Bedrock's prompt has no",
        )

        # Add voice_id to the prompt configuration
        filtered_config["voice_id"] = self._voice_id

        # Add/override inference parameters (where C code expects them)
        filtered_config["temperature"] = self._temperature
        filtered_config["top_p"] = self._top_p
        filtered_config["max_tokens"] = self._max_tokens

        return filtered_config

    def set_voice(self, voice_id: str) -> None:
        """
        Set the Bedrock voice ID

        Args:
            voice_id: Bedrock voice: 'tiffany', 'matthew', 'amy', 'lupe' or 'carlos'
        """
        self._voice_id = voice_id
        logger.debug(f"Voice set to: {voice_id}")

    def set_inference_params(
        self,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """
        Update Bedrock inference parameters

        Each value may be a number or a numeric string, which is converted.
        temperature and top_p may also be a SWML variable reference such as
        ``${temperature}``.

        Args:
            temperature: Generation temperature (0-2)
            top_p: Nucleus sampling parameter (0-1)
            max_tokens: Maximum tokens to generate. The platform's Bedrock
                session doesn't read it; it uses 1024

        Raises:
            ValueError: If temperature or top_p isn't a number, or max_tokens
                isn't an integer. Nothing is changed when a value is refused.
        """
        # Convert all three before changing any, so a refused value leaves
        # the settings as they were
        new_temperature = (
            _to_number("temperature", temperature) if temperature is not None else None
        )
        new_top_p = _to_number("top_p", top_p) if top_p is not None else None
        new_max_tokens = (
            _to_number("max_tokens", max_tokens, integer=True)
            if max_tokens is not None
            else None
        )
        if new_temperature is not None:
            self._temperature = new_temperature
        if new_top_p is not None:
            self._top_p = new_top_p
        if new_max_tokens is not None:
            self._max_tokens = new_max_tokens

        logger.debug(
            f"Inference params updated: temp={self._temperature}, "
            f"top_p={self._top_p}, max_tokens={self._max_tokens}"
        )

    # Methods that may not be relevant to Bedrock
    # These are overridden to provide appropriate behavior or warnings

    def set_llm_model(self, model: str) -> None:
        """
        Set LLM model - not applicable for Bedrock

        Bedrock uses a fixed voice-to-voice model, so this method
        logs a warning and does nothing.

        Args:
            model: Model name (ignored)
        """
        logger.warning(
            f"set_llm_model('{model}') called but Bedrock uses a fixed voice-to-voice model"
        )

    def set_llm_temperature(self, temperature: float) -> None:
        """
        Set LLM temperature - redirects to set_inference_params

        Args:
            temperature: Temperature value
        """
        self.set_inference_params(temperature=temperature)

    def set_post_prompt_llm_params(self, **params: Any) -> None:
        """
        Set post-prompt LLM parameters - not applicable for Bedrock

        Bedrock uses OpenAI for post-prompt summarization, but those
        parameters are configured in the C code.

        Args:
            **params: Ignored parameters
        """
        logger.warning(
            "set_post_prompt_llm_params() called but Bedrock post-prompt uses OpenAI configured in C code"
        )

    def set_prompt_llm_params(self, **params: Any) -> "BedrockAgent":
        """
        Set the prompt's inference settings

        temperature, top_p and max_tokens update the inference settings, as
        set_inference_params() does. The platform's Bedrock session reads no
        other prompt setting, so anything else, such as confidence,
        presence_penalty or barge_confidence, is ignored with a warning.

        Args:
            **params: Prompt settings

        Returns:
            self for method chaining

        Raises:
            ValueError: If temperature or top_p isn't a number, or max_tokens
                isn't an integer
        """
        self.set_inference_params(
            temperature=params.pop("temperature", None),
            top_p=params.pop("top_p", None),
            max_tokens=params.pop("max_tokens", None),
        )
        if params:
            names = ", ".join(sorted(params))
            ignored = "it's" if len(params) == 1 else "they're"
            logger.warning(
                f"set_prompt_llm_params(): the platform's Bedrock session doesn't "
                f"use {names}, so {ignored} ignored"
            )
        return self

    # Note: We don't override prompt methods like set_prompt_text, set_prompt_pom
    # because those work fine - they just build the prompt structure that we
    # transform in _render_swml()

    def __repr__(self) -> str:
        """String representation of the agent"""
        return (
            f"BedrockAgent(name='{self.name}', route='{self.route}', "
            f"voice='{self._voice_id}')"
        )
