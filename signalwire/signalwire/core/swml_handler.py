"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
SWML Verb Handlers - Interface and implementations for SWML verb handling

This module defines the base interface for SWML verb handlers and provides
implementations for specific verbs that require special handling.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple


class SWMLVerbHandler(ABC):
    """
    Base interface for SWML verb handlers
    
    This abstract class defines the interface that all SWML verb handlers
    must implement. Verb handlers provide specialized logic for complex
    SWML verbs that cannot be handled generically.
    """
    
    @abstractmethod
    def get_verb_name(self) -> str:
        """
        Get the name of the verb this handler handles
        
        Returns:
            The verb name as a string
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate the configuration for this verb
        
        Args:
            config: The configuration dictionary for this verb
            
        Returns:
            (is_valid, error_messages) tuple
        """
        pass
    
    @abstractmethod
    def build_config(self, **kwargs) -> Dict[str, Any]:
        """
        Build a configuration for this verb from the provided arguments
        
        Args:
            **kwargs: Keyword arguments specific to this verb
            
        Returns:
            Configuration dictionary
        """
        pass


class AIVerbHandler(SWMLVerbHandler):
    """
    Handler for the SWML 'ai' verb
    
    The 'ai' verb is complex and requires specialized handling, particularly
    for managing prompts, SWAIG functions, and AI configurations.
    """
    
    def get_verb_name(self) -> str:
        """
        Get the name of the verb this handler handles
        
        Returns:
            "ai" as the verb name
        """
        return "ai"
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate the configuration for the AI verb
        
        Args:
            config: The configuration dictionary for the AI verb
            
        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []
        
        # Check that prompt is present
        if "prompt" not in config:
            errors.append("Missing required field 'prompt'")
            return False, errors
        
        prompt = config["prompt"]
        if not isinstance(prompt, dict):
            errors.append("'prompt' must be an object")
            return False, errors
        
        # Check that prompt contains either text or pom (required)
        has_text = "text" in prompt
        has_pom = "pom" in prompt
        has_contexts = "contexts" in prompt
        
        # Require either text or pom (mutually exclusive)
        base_prompt_count = sum([has_text, has_pom])
        if base_prompt_count == 0:
            errors.append("'prompt' must contain either 'text' or 'pom' as base prompt")
        elif base_prompt_count > 1:
            errors.append("'prompt' can only contain one of: 'text' or 'pom' (mutually exclusive)")
        
        # Contexts are optional and can be combined with text or pom
        if has_contexts:
            contexts = prompt["contexts"]
            if not isinstance(contexts, dict):
                errors.append("'prompt.contexts' must be an object")
        
        # Validate SWAIG structure if present
        if "SWAIG" in config:
            swaig = config["SWAIG"]
            if not isinstance(swaig, dict):
                errors.append("'SWAIG' must be an object")
        
        return len(errors) == 0, errors
    
    def build_config(self, 
                    prompt_text: Optional[str] = None,
                    prompt_pom: Optional[List[Dict[str, Any]]] = None,
                    contexts: Optional[Dict[str, Any]] = None,
                    post_prompt: Optional[str] = None,
                    post_prompt_url: Optional[str] = None,
                    swaig: Optional[Dict[str, Any]] = None,
                    **kwargs) -> Dict[str, Any]:
        """
        Build a configuration for the AI verb
        
        Args:
            prompt_text: Text prompt for the AI (mutually exclusive with prompt_pom)
            prompt_pom: POM structure for the AI prompt (mutually exclusive with prompt_text)
            contexts: Optional contexts and steps configuration (can be combined with text or pom)
            post_prompt: Optional post-prompt text
            post_prompt_url: Optional URL for post-prompt processing
            swaig: Optional SWAIG configuration
            **kwargs: Additional AI parameters
            
        Returns:
            AI verb configuration dictionary
        """
        config = {}
        
        # Require either text or pom as base prompt (mutually exclusive)
        base_prompt_count = sum(x is not None for x in [prompt_text, prompt_pom])
        if base_prompt_count == 0:
            raise ValueError("Either prompt_text or prompt_pom must be provided as base prompt")
        elif base_prompt_count > 1:
            raise ValueError("prompt_text and prompt_pom are mutually exclusive")
        
        # Build prompt object with base prompt
        prompt_config = {}
        if prompt_text is not None:
            prompt_config["text"] = prompt_text
        elif prompt_pom is not None:
            prompt_config["pom"] = prompt_pom
            
        # Add contexts if provided (optional, activates steps feature)
        if contexts is not None:
            prompt_config["contexts"] = contexts
            
        config["prompt"] = prompt_config
        
        # Add post-prompt if provided
        if post_prompt is not None:
            config["post_prompt"] = {"text": post_prompt}
        
        # Add post-prompt URL if provided
        if post_prompt_url is not None:
            config["post_prompt_url"] = post_prompt_url
        
        # Add SWAIG if provided
        if swaig is not None:
            config["SWAIG"] = swaig
        
        # Add any additional parameters
        if "params" not in config:
            config["params"] = {}
            
        for key, value in kwargs.items():
            # Special handling for certain parameters
            if key == "languages":
                config["languages"] = value
            elif key == "hints":
                config["hints"] = value
            elif key == "pronounce":
                config["pronounce"] = value
            elif key == "global_data":
                config["global_data"] = value
            else:
                # Add to params object
                config["params"][key] = value
        
        return config


class VerbHandlerRegistry:
    """
    Registry for SWML verb handlers
    
    This class maintains a registry of handlers for special SWML verbs
    and provides methods for accessing and using them.
    """
    
    def __init__(self):
        """Initialize the registry with default handlers"""
        self._handlers = {}
        
        # Register default handlers
        self.register_handler(AIVerbHandler())
    
    def register_handler(self, handler: SWMLVerbHandler) -> None:
        """
        Register a new verb handler
        
        Args:
            handler: The handler to register
        """
        verb_name = handler.get_verb_name()
        self._handlers[verb_name] = handler
    
    def get_handler(self, verb_name: str) -> Optional[SWMLVerbHandler]:
        """
        Get the handler for a specific verb
        
        Args:
            verb_name: The name of the verb
            
        Returns:
            The handler if found, None otherwise
        """
        return self._handlers.get(verb_name)
    
    def has_handler(self, verb_name: str) -> bool:
        """
        Check if a handler exists for a specific verb
        
        Args:
            verb_name: The name of the verb
            
        Returns:
            True if a handler exists, False otherwise
        """
        return verb_name in self._handlers 