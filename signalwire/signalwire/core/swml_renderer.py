"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
SWML document rendering utilities for SignalWire AI Agents.
"""

import json
from typing import Dict, List, Any, Optional, Union

from signalwire.core.swml_service import SWMLService
from signalwire.core.swml_builder import SWMLBuilder


class SwmlRenderer:
    """
    Renders SWML documents for SignalWire AI Agents with AI and SWAIG components
    
    This class provides methods for rendering SWML documents using the SWMLService architecture.
    """
    
    @staticmethod
    def render_swml(
        prompt: Union[str, List[Dict[str, Any]]],
        service: SWMLService,
        post_prompt: Optional[str] = None,
        post_prompt_url: Optional[str] = None,
        swaig_functions: Optional[List[Dict[str, Any]]] = None,
        startup_hook_url: Optional[str] = None,
        hangup_hook_url: Optional[str] = None,
        prompt_is_pom: bool = False,
        params: Optional[Dict[str, Any]] = None,
        add_answer: bool = False,
        record_call: bool = False,
        record_format: str = "mp4",
        record_stereo: bool = True,
        format: str = "json",
        default_webhook_url: Optional[str] = None
    ) -> str:
        """
        Generate a complete SWML document with AI configuration
        
        Args:
            prompt: AI prompt text or POM structure
            service: SWMLService instance to use for document building
            post_prompt: Optional post-prompt text
            post_prompt_url: Optional post-prompt URL
            swaig_functions: List of SWAIG function definitions
            startup_hook_url: Optional startup hook URL
            hangup_hook_url: Optional hangup hook URL
            prompt_is_pom: Whether prompt is POM format
            params: Additional AI verb parameters
            add_answer: Whether to add answer verb
            record_call: Whether to add record_call verb
            record_format: Recording format
            record_stereo: Whether to record in stereo
            format: Output format (json or yaml)
            default_webhook_url: Default webhook URL for SWAIG functions
            
        Returns:
            SWML document as a string
        """
        # Use the service to build the document
        builder = SWMLBuilder(service)
        
        # Reset the document to start fresh
        builder.reset()
        
        # Add answer block if requested
        if add_answer:
            builder.answer()
        
        # Add record_call if requested
        if record_call:
            service.add_verb("record_call", {
                "format": record_format,
                "stereo": record_stereo
            })
        
        # Configure SWAIG object for AI verb
        swaig_config = {}
        functions = []
        
        # Add startup hook if provided
        if startup_hook_url:
            functions.append({
                "function": "startup_hook",
                "description": "Called when the call starts",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "web_hook_url": startup_hook_url
            })
        
        # Add hangup hook if provided
        if hangup_hook_url:
            functions.append({
                "function": "hangup_hook",
                "description": "Called when the call ends",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "web_hook_url": hangup_hook_url
            })
        
        # Add regular functions if provided
        if swaig_functions:
            for func in swaig_functions:
                # Skip special hooks as we've already added them
                if func.get("function") not in ["startup_hook", "hangup_hook"]:
                    functions.append(func)
        
        # Only add SWAIG if we have functions or a default URL
        if functions or default_webhook_url:
            # Add defaults if we have a default webhook URL
            if default_webhook_url:
                swaig_config["defaults"] = {
                    "web_hook_url": default_webhook_url
                }
            
            # Add functions if we have any
            if functions:
                swaig_config["functions"] = functions
        
        # Add AI verb with appropriate configuration
        builder.ai(
            prompt_text=None if prompt_is_pom else prompt,
            prompt_pom=prompt if prompt_is_pom else None,
            post_prompt=post_prompt,
            post_prompt_url=post_prompt_url,
            swaig=swaig_config if swaig_config else None,
            **(params or {})
        )
        
        # Get the document as a dictionary or string based on format
        if format.lower() == "yaml":
            import yaml
            return yaml.dump(builder.build(), sort_keys=False)
        else:
            return builder.render()
            
    @staticmethod
    def render_function_response_swml(
        response_text: str,
        service: SWMLService,
        actions: Optional[List[Dict[str, Any]]] = None,
        format: str = "json"
    ) -> str:
        """
        Generate a SWML document for a function response
        
        Args:
            response_text: Text response to include in the document
            service: SWMLService instance to use
            actions: Optional list of actions to perform
            format: Output format (json or yaml)
            
        Returns:
            SWML document as a string
        """
        # Use the service to build the document
        service.reset_document()
        
        # Add a play block for the response if provided
        if response_text:
            service.add_verb("play", {"text": response_text})
        
        # Add any actions that were provided
        if actions:
            for action in actions:
                if "play" in action:
                    service.add_verb("play", action["play"])
                elif "hangup" in action:
                    service.add_verb("hangup", action["hangup"])
                elif "transfer" in action:
                    service.add_verb("transfer", action["transfer"])
                elif "ai" in action:
                    service.add_verb("ai", action["ai"])
                # Add more action types as needed
        
        # Get the document as a dictionary or string based on format
        if format.lower() == "yaml":
            import yaml
            return yaml.dump(service.get_document(), sort_keys=False)
        else:
            return service.render_document()