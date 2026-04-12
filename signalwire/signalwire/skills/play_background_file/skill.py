"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Play Background File Skill

A configurable skill for managing background file playback with custom tool names
and multiple file collections. Supports both audio and video files.
"""

from typing import Dict, Any, List
from signalwire.core import FunctionResult
from signalwire.core.skill_base import SkillBase


class PlayBackgroundFileSkill(SkillBase):
    """
    Skill for playing background files (audio/video) with configurable tool names.
    
    Supports multiple instances with different tool names and file collections.
    Uses DataMap for serverless execution with dynamic enum generation.
    
    Configuration:
    - tool_name: Custom name for the generated SWAIG function
    - files: Array of file objects with key, description, url, and optional wait
    
    Example:
        agent.add_skill("play_background_file", {
            "tool_name": "play_testimonial",
            "files": [
                {
                    "key": "massey",
                    "description": "Customer success story from Massey Energy",
                    "url": "https://example.com/massey.mp4",
                    "wait": True
                }
            ]
        })
    """
    
    SKILL_NAME = "play_background_file"
    SKILL_DESCRIPTION = "Control background file playback"
    SUPPORTS_MULTIPLE_INSTANCES = True
    
    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Dict[str, Any]]:
        """Get parameter schema for Play Background File skill"""
        schema = super().get_parameter_schema()
        schema.update({
            "files": {
                "type": "array",
                "description": "Array of file configurations to make available for playback",
                "required": True,
                "items": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "Unique identifier for the file"
                        },
                        "description": {
                            "type": "string",
                            "description": "Human-readable description of the file"
                        },
                        "url": {
                            "type": "string",
                            "description": "URL of the audio/video file to play"
                        },
                        "wait": {
                            "type": "boolean",
                            "description": "Whether to wait for file to finish playing",
                            "default": False
                        }
                    },
                    "required": ["key", "description", "url"]
                }
            }
        })
        return schema
    
    def __init__(self, agent, params: Dict[str, Any] = None):
        """
        Initialize the skill with configuration parameters.
        
        Args:
            agent: The agent instance this skill belongs to
            params: Configuration dictionary containing:
                - tool_name: Custom tool name (default: "play_background_file")
                - files: Array of file objects with key, description, url, wait
        """
        super().__init__(agent, params)
        
        # Extract configuration
        self.tool_name = self.params.get('tool_name', 'play_background_file')
        self.files = self.params.get('files', [])
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate the skill configuration."""
        if not isinstance(self.files, list) or len(self.files) == 0:
            raise ValueError("files parameter must be a non-empty list")
        
        for i, file_obj in enumerate(self.files):
            if not isinstance(file_obj, dict):
                raise ValueError(f"File {i} must be a dictionary")
            
            required_fields = ['key', 'description', 'url']
            for field in required_fields:
                if field not in file_obj:
                    raise ValueError(f"File {i} missing required field: {field}")
                if not isinstance(file_obj[field], str) or not file_obj[field].strip():
                    raise ValueError(f"File {i} field '{field}' must be a non-empty string")
            
            # Validate optional wait field
            if 'wait' in file_obj and not isinstance(file_obj['wait'], bool):
                raise ValueError(f"File {i} field 'wait' must be a boolean")
            
            # Validate key format (alphanumeric, underscores, hyphens)
            key = file_obj['key']
            if not key.replace('_', '').replace('-', '').isalnum():
                raise ValueError(f"File {i} key '{key}' must contain only alphanumeric characters, underscores, and hyphens")
    
    def get_instance_key(self) -> str:
        """
        Generate a unique instance key for this skill configuration.
        
        Returns:
            Unique key combining skill name and tool name
        """
        return f"{self.SKILL_NAME}_{self.tool_name}"
    
    def setup(self) -> bool:
        """
        Setup the skill - no external dependencies needed.
        
        Returns:
            True if setup successful
        """
        return True
    
    def register_tools(self) -> None:
        """Register SWAIG tools with the agent"""
        tools = self.get_tools()
        for tool in tools:
            # Merge any swaig_fields from params into the tool
            if self.swaig_fields:
                tool.update(self.swaig_fields)
            self.agent.register_swaig_function(tool)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Generate the SWAIG tool with DataMap expressions.
        
        Returns:
            List containing the generated tool configuration
        """
        # Build enum values and descriptions
        enum_values = []
        descriptions = []
        
        for file_obj in self.files:
            enum_values.append(f"start_{file_obj['key']}")
            descriptions.append(f"start_{file_obj['key']}: {file_obj['description']}")
        
        enum_values.append("stop")
        descriptions.append("stop: Stop any currently playing background file")
        
        # Build parameter description
        description = "Action to perform. Options: " + "; ".join(descriptions)
        
        # Create the tool configuration
        tool = {
            "function": self.tool_name,
            "description": f"Control background file playback for {self.tool_name.replace('_', ' ')}",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": description,
                        "enum": enum_values
                    }
                },
                "required": ["action"]
            },
            "wait_for_fillers": True,
            "skip_fillers": True,
            "data_map": {
                "expressions": self._build_expressions()
            }
        }
        
        return [tool]
    
    def _build_expressions(self) -> List[Dict[str, Any]]:
        """
        Build DataMap expressions for file playback and stop actions.
        
        Returns:
            List of expression configurations
        """
        expressions = []
        
        # Add expressions for each file
        for file_obj in self.files:
            key = file_obj['key']
            url = file_obj['url']
            wait = file_obj.get('wait', False)
            description = file_obj['description']
            
            # Create the result with appropriate response
            result = FunctionResult(
                f"Tell the user you are now going to play {description} for them.",
                post_process=True
            ).play_background_file(url, wait=wait)
            
            expressions.append({
                "string": "${args.action}",
                "pattern": f"/start_{key}/i",
                "output": result.to_dict()
            })
        
        # Add stop expression
        stop_result = FunctionResult(
            "Tell the user you have stopped the background file playback."
        ).stop_background_file()
        
        expressions.append({
            "string": "${args.action}",
            "pattern": "/stop/i",
            "output": stop_result.to_dict()
        })
        
        return expressions 
