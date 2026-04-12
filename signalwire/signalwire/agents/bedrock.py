"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Bedrock Agent - Amazon Bedrock voice-to-voice integration

This module provides BedrockAgent, which extends AgentBase to support
Amazon Bedrock's voice-to-voice model while maintaining compatibility
with all SignalWire agent features like skills, POM, and SWAIG functions.
"""

import json
from typing import Dict, List, Any, Optional, Union
from signalwire.core.agent_base import AgentBase
from signalwire.core.logging_config import get_logger

logger = get_logger("bedrock_agent")


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
    SWML with the "amazon_bedrock" verb instead of "ai".
    """
    
    def __init__(
        self,
        name: str = "bedrock_agent",
        route: str = "/bedrock",
        system_prompt: Optional[str] = None,
        voice_id: str = "matthew",
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 1024,
        **kwargs
    ):
        """
        Initialize BedrockAgent
        
        Args:
            name: Agent name
            route: HTTP route for the agent
            system_prompt: Initial system prompt (can be overridden with set_prompt)
            voice_id: Bedrock voice ID (default: matthew)
            temperature: Generation temperature (0-1)
            top_p: Nucleus sampling parameter (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments passed to AgentBase
        """
        # Store Bedrock-specific parameters first
        self._voice_id = voice_id
        self._temperature = temperature
        self._top_p = top_p
        self._max_tokens = max_tokens
        
        # Initialize base class
        super().__init__(name=name, route=route, **kwargs)
        
        # Set initial prompt if provided (after super init)
        if system_prompt:
            self.set_prompt_text(system_prompt)
        
        logger.info(f"BedrockAgent initialized: {name} on route {route}")
    
    def _render_swml(self, call_id: str = None, modifications: Optional[dict] = None) -> str:
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
                        "prompt": self._add_voice_to_prompt(ai_config.get("prompt", {})),
                        
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
                        "post_prompt_url": ai_config.get("post_prompt_url")
                    }
                }
                
                # Remove None values
                bedrock_config = bedrock_verb["amazon_bedrock"]
                bedrock_verb["amazon_bedrock"] = {
                    k: v for k, v in bedrock_config.items() 
                    if v is not None
                }
                
                # Replace ai verb with amazon_bedrock verb
                main_section[i] = bedrock_verb
                break
        
        # Convert back to JSON string
        return json.dumps(swml)
    
    def _add_voice_to_prompt(self, prompt_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add voice configuration to the prompt object
        
        In Bedrock, voice configuration is part of the prompt object,
        not a separate field like in OpenAI.
        
        Args:
            prompt_config: Current prompt configuration
            
        Returns:
            Updated prompt configuration with voice
        """
        # Create a clean copy, filtering out text-model-specific parameters
        # that don't apply to Bedrock's voice-to-voice model
        filtered_config = {}
        
        # Copy over only the relevant fields
        for key, value in prompt_config.items():
            # Skip text-model-specific parameters
            if key in ['barge_confidence', 'presence_penalty', 'frequency_penalty']:
                continue
            filtered_config[key] = value
        
        # Add voice_id to the prompt configuration
        filtered_config["voice_id"] = self._voice_id
        
        # Add/override inference parameters (where C code expects them)
        filtered_config["temperature"] = self._temperature
        filtered_config["top_p"] = self._top_p
        
        return filtered_config
    
    def _build_bedrock_params(self, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Bedrock-specific parameters
        
        Merges base parameters with Bedrock-specific inference settings.
        
        Args:
            base_params: Base parameters from AgentBase
            
        Returns:
            Combined parameters for Bedrock
        """
        # Start with base params
        params = base_params.copy()
        
        # Add Bedrock inference parameters
        params.update({
            "temperature": self._temperature,
            "top_p": self._top_p,
            "max_tokens": self._max_tokens
        })
        
        return params
    
    def set_voice(self, voice_id: str) -> None:
        """
        Set the Bedrock voice ID
        
        Args:
            voice_id: Bedrock voice identifier (e.g., 'matthew', 'joanna')
        """
        self._voice_id = voice_id
        logger.debug(f"Voice set to: {voice_id}")
    
    def set_inference_params(
        self,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> None:
        """
        Update Bedrock inference parameters
        
        Args:
            temperature: Generation temperature (0-1)
            top_p: Nucleus sampling parameter (0-1)
            max_tokens: Maximum tokens to generate
        """
        if temperature is not None:
            self._temperature = temperature
        if top_p is not None:
            self._top_p = top_p
        if max_tokens is not None:
            self._max_tokens = max_tokens
        
        logger.debug(f"Inference params updated: temp={self._temperature}, "
                    f"top_p={self._top_p}, max_tokens={self._max_tokens}")
    
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
        logger.warning(f"set_llm_model('{model}') called but Bedrock uses a fixed voice-to-voice model")
    
    def set_llm_temperature(self, temperature: float) -> None:
        """
        Set LLM temperature - redirects to set_inference_params
        
        Args:
            temperature: Temperature value
        """
        self.set_inference_params(temperature=temperature)
    
    def set_post_prompt_llm_params(self, **params) -> None:
        """
        Set post-prompt LLM parameters - not applicable for Bedrock
        
        Bedrock uses OpenAI for post-prompt summarization, but those
        parameters are configured in the C code.
        
        Args:
            **params: Ignored parameters
        """
        logger.warning("set_post_prompt_llm_params() called but Bedrock post-prompt uses OpenAI configured in C code")
    
    def set_prompt_llm_params(self, **params) -> None:
        """
        Set prompt LLM parameters - use set_inference_params instead
        
        For Bedrock, use set_inference_params() to configure temperature,
        top_p, and max_tokens.
        
        Args:
            **params: Parameters (ignored, use set_inference_params)
        """
        logger.warning("set_prompt_llm_params() called - use set_inference_params() for Bedrock")
    
    # Note: We don't override prompt methods like set_prompt_text, set_prompt_pom
    # because those work fine - they just build the prompt structure that we
    # transform in _render_swml()
    
    def __repr__(self) -> str:
        """String representation of the agent"""
        return (f"BedrockAgent(name='{self.name}', route='{self.route}', "
                f"voice='{self._voice_id}')")