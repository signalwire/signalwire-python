"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
SWML Builder - Fluent API for building SWML documents

This module provides a fluent builder API for creating SWML documents.
It allows for chaining method calls to build up a document step by step.
"""

import types
from typing import Dict, List, Any, Optional, Union, TypeVar
try:
    from typing import Self  # Python 3.11+
except ImportError:
    from typing_extensions import Self  # For Python 3.9-3.10

from signalwire.core.swml_service import SWMLService


T = TypeVar('T', bound='SWMLBuilder')


class SWMLBuilder:
    """
    Fluent builder for SWML documents
    
    This class provides a fluent interface for building SWML documents
    by chaining method calls. It delegates to an underlying SWMLService
    instance for the actual document creation.
    """
    
    def __init__(self, service: SWMLService):
        """
        Initialize with a SWMLService instance
        
        Args:
            service: The SWMLService to delegate to
        """
        self.service = service
        
        # Dictionary to cache dynamically created methods
        self._verb_methods_cache = {}
        
        # Create auto-vivified methods for all verbs
        self._create_verb_methods()
    
    def answer(self, max_duration: Optional[int] = None, codecs: Optional[str] = None) -> Self:
        """
        Add an 'answer' verb to the main section
        
        Args:
            max_duration: Maximum duration in seconds
            codecs: Comma-separated list of codecs
            
        Returns:
            Self for method chaining
        """
        config = {}
        if max_duration is not None:
            config["max_duration"] = max_duration
        if codecs is not None:
            config["codecs"] = codecs
        self.service.add_verb("answer", config)
        return self
    
    def hangup(self, reason: Optional[str] = None) -> Self:
        """
        Add a 'hangup' verb to the main section
        
        Args:
            reason: Optional reason for hangup
            
        Returns:
            Self for method chaining
        """
        config = {}
        if reason is not None:
            config["reason"] = reason
        self.service.add_verb("hangup", config)
        return self
    
    def ai(self, 
          prompt_text: Optional[str] = None,
          prompt_pom: Optional[List[Dict[str, Any]]] = None,
          post_prompt: Optional[str] = None,
          post_prompt_url: Optional[str] = None,
          swaig: Optional[Dict[str, Any]] = None,
          **kwargs) -> Self:
        """
        Add an 'ai' verb to the main section
        
        Args:
            prompt_text: Text prompt for the AI (mutually exclusive with prompt_pom)
            prompt_pom: POM structure for the AI prompt (mutually exclusive with prompt_text)
            post_prompt: Optional post-prompt text
            post_prompt_url: Optional URL for post-prompt processing
            swaig: Optional SWAIG configuration
            **kwargs: Additional AI parameters
            
        Returns:
            Self for method chaining
        """
        config = {}
        
        # Handle prompt (either text or POM, but not both)
        if prompt_text is not None:
            config["prompt"] = prompt_text
        elif prompt_pom is not None:
            config["prompt"] = prompt_pom
        
        # Add optional parameters
        if post_prompt is not None:
            config["post_prompt"] = post_prompt
        if post_prompt_url is not None:
            config["post_prompt_url"] = post_prompt_url
        if swaig is not None:
            config["SWAIG"] = swaig
        
        # Add any additional kwargs
        config.update(kwargs)
        
        self.service.add_verb("ai", config)
        return self
    
    def play(self, url: Optional[str] = None, urls: Optional[List[str]] = None, 
             volume: Optional[float] = None, say_voice: Optional[str] = None, 
             say_language: Optional[str] = None, say_gender: Optional[str] = None,
             auto_answer: Optional[bool] = None) -> Self:
        """
        Add a 'play' verb to the main section
        
        Args:
            url: Single URL to play (mutually exclusive with urls)
            urls: List of URLs to play (mutually exclusive with url)
            volume: Volume level (-40 to 40)
            say_voice: Voice for text-to-speech
            say_language: Language for text-to-speech
            say_gender: Gender for text-to-speech
            auto_answer: Whether to auto-answer the call
            
        Returns:
            Self for method chaining
        """
        # Create base config
        config = {}
        
        # Add play config (either single URL or list)
        if url is not None:
            config["url"] = url
        elif urls is not None:
            config["urls"] = urls
        else:
            raise ValueError("Either url or urls must be provided")
        
        # Add optional parameters
        if volume is not None:
            config["volume"] = volume
        if say_voice is not None:
            config["say_voice"] = say_voice
        if say_language is not None:
            config["say_language"] = say_language
        if say_gender is not None:
            config["say_gender"] = say_gender
        if auto_answer is not None:
            config["auto_answer"] = auto_answer
        
        # Add the verb
        self.service.add_verb("play", config)
        return self
    
    def say(self, text: str, voice: Optional[str] = None, 
            language: Optional[str] = None, gender: Optional[str] = None,
            volume: Optional[float] = None) -> Self:
        """
        Add a 'play' verb with say: prefix for text-to-speech
        
        Args:
            text: Text to speak
            voice: Voice for text-to-speech
            language: Language for text-to-speech
            gender: Gender for text-to-speech
            volume: Volume level (-40 to 40)
            
        Returns:
            Self for method chaining
        """
        # Create play config with say: prefix
        url = f"say:{text}"
        
        # Add the verb
        return self.play(
            url=url,
            say_voice=voice,
            say_language=language,
            say_gender=gender,
            volume=volume
        )
    
    def add_section(self, section_name: str) -> Self:
        """
        Add a new section to the document
        
        Args:
            section_name: Name of the section to add
            
        Returns:
            Self for method chaining
        """
        self.service.add_section(section_name)
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Build and return the SWML document
        
        Returns:
            The complete SWML document as a dictionary
        """
        return self.service.get_document()
    
    def render(self) -> str:
        """
        Build and render the SWML document as a JSON string
        
        Returns:
            The complete SWML document as a JSON string
        """
        return self.service.render_document()
    
    def reset(self) -> Self:
        """
        Reset the document to an empty state
        
        Returns:
            Self for method chaining
        """
        self.service.reset_document()
        return self
    
    def _create_verb_methods(self) -> None:
        """
        Create auto-vivified methods for all verbs at initialization time
        
        This creates methods for all SWML verbs defined in the schema,
        allowing for fluent chaining like builder.denoise().goto().play()
        """
        # Get all verb names from the schema
        if not hasattr(self.service, 'schema_utils') or not self.service.schema_utils:
            return
            
        verb_names = self.service.schema_utils.get_all_verb_names()
        
        # Create a method for each verb
        for verb_name in verb_names:
            # Skip verbs that already have specific methods
            if hasattr(self, verb_name):
                continue
            
            # Handle sleep verb specially since it takes an integer directly
            if verb_name == "sleep":
                def sleep_method(self_instance, duration=None, **kwargs):
                    """
                    Add the sleep verb to the document.
                    
                    Args:
                        duration: The amount of time to sleep in milliseconds
                    """
                    # Sleep verb takes a direct integer parameter in SWML
                    if duration is not None:
                        self_instance.service.add_verb("sleep", duration)
                    elif kwargs:
                        # Try to get the value from kwargs
                        self_instance.service.add_verb("sleep", next(iter(kwargs.values())))
                    else:
                        raise TypeError("sleep() missing required argument: 'duration'")
                    return self_instance
                
                # Set it as an attribute of self
                setattr(self, verb_name, types.MethodType(sleep_method, self))
                
                # Also cache it for later
                self._verb_methods_cache[verb_name] = sleep_method
                continue
                
            # Generate the method implementation for normal verbs
            def make_verb_method(name):
                def verb_method(self_instance, **kwargs):
                    """
                    Dynamically generated method for SWML verb - returns self for chaining
                    """
                    config = {}
                    for key, value in kwargs.items():
                        if value is not None:
                            config[key] = value
                    self_instance.service.add_verb(name, config)
                    return self_instance
                
                # Add docstring to the method
                if hasattr(self.service.schema_utils, 'get_verb_properties'):
                    verb_properties = self.service.schema_utils.get_verb_properties(name)
                    if "description" in verb_properties:
                        verb_method.__doc__ = f"Add the {name} verb to the document.\n\n{verb_properties['description']}\n\nReturns: Self for method chaining"
                    else:
                        verb_method.__doc__ = f"Add the {name} verb to the document.\n\nReturns: Self for method chaining"
                else:
                    verb_method.__doc__ = f"Add the {name} verb to the document.\n\nReturns: Self for method chaining"
                
                return verb_method
            
            # Create the method with closure over the verb name
            method = make_verb_method(verb_name)
            
            # Set it as an attribute of self
            setattr(self, verb_name, types.MethodType(method, self))
            
            # Also cache it for later
            self._verb_methods_cache[verb_name] = method
    
    def __getattr__(self, name: str) -> Any:
        """
        Dynamically generate and return SWML verb methods when accessed
        
        This method is called when an attribute lookup fails through the normal
        mechanisms. It checks if the attribute name corresponds to a SWML verb
        defined in the schema, and if so, dynamically creates a method for that verb.
        
        Args:
            name: The name of the attribute being accessed
            
        Returns:
            The dynamically created verb method if name is a valid SWML verb,
            otherwise raises AttributeError
            
        Raises:
            AttributeError: If name is not a valid SWML verb
        """
        # First check if this is a valid SWML verb
        if not hasattr(self.service, 'schema_utils') or not self.service.schema_utils:
            msg = f"'{self.__class__.__name__}' object has no attribute '{name}' (no schema available)"
            raise AttributeError(msg)
            
        verb_names = self.service.schema_utils.get_all_verb_names()
        
        if name in verb_names:
            # Check if we already have this method in the cache
            if not hasattr(self, '_verb_methods_cache'):
                self._verb_methods_cache = {}
                
            if name in self._verb_methods_cache:
                return types.MethodType(self._verb_methods_cache[name], self)
            
            # Handle sleep verb specially since it takes an integer directly
            if name == "sleep":
                def sleep_method(self_instance, duration=None, **kwargs):
                    """
                    Add the sleep verb to the document.
                    
                    Args:
                        duration: The amount of time to sleep in milliseconds
                    """
                    # Sleep verb takes a direct integer parameter in SWML
                    if duration is not None:
                        self_instance.service.add_verb("sleep", duration)
                    elif kwargs:
                        # Try to get the value from kwargs
                        self_instance.service.add_verb("sleep", next(iter(kwargs.values())))
                    else:
                        raise TypeError("sleep() missing required argument: 'duration'")
                    return self_instance
                
                # Cache the method for future use
                self._verb_methods_cache[name] = sleep_method
                
                # Return the bound method
                return types.MethodType(sleep_method, self)
            
            # Generate the method implementation for normal verbs
            def verb_method(self_instance, **kwargs):
                """
                Dynamically generated method for SWML verb - returns self for chaining
                """
                config = {}
                for key, value in kwargs.items():
                    if value is not None:
                        config[key] = value
                self_instance.service.add_verb(name, config)
                return self_instance
            
            # Add docstring to the method
            if hasattr(self.service.schema_utils, 'get_verb_properties'):
                verb_properties = self.service.schema_utils.get_verb_properties(name)
                if "description" in verb_properties:
                    verb_method.__doc__ = f"Add the {name} verb to the document.\n\n{verb_properties['description']}\n\nReturns: Self for method chaining"
                else:
                    verb_method.__doc__ = f"Add the {name} verb to the document.\n\nReturns: Self for method chaining"
            else:
                verb_method.__doc__ = f"Add the {name} verb to the document.\n\nReturns: Self for method chaining"
            
            # Cache the method for future use
            self._verb_methods_cache[name] = verb_method
            
            # Return the bound method
            return types.MethodType(verb_method, self)
        
        # Not a valid verb
        msg = f"'{self.__class__.__name__}' object has no attribute '{name}'"
        raise AttributeError(msg) 