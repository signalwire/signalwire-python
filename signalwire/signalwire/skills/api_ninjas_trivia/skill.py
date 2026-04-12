"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
API Ninjas Trivia Skill

A configurable skill for getting trivia questions from API Ninjas with customizable
categories and multiple tool instances.
"""

from typing import Dict, Any, List
from signalwire.core import FunctionResult
from signalwire.core.skill_base import SkillBase


class ApiNinjasTriviaSkill(SkillBase):
    """
    Skill for getting trivia questions from API Ninjas with configurable categories.
    
    Supports multiple instances with different tool names and category combinations.
    Uses DataMap for serverless execution with dynamic enum generation.
    
    Configuration:
    - tool_name: Custom name for the generated SWAIG function
    - api_key: API Ninjas API key
    - categories: Array of category strings to enable
    
    Available categories:
    - artliterature: Art and Literature
    - language: Language  
    - sciencenature: Science and Nature
    - general: General Knowledge
    - fooddrink: Food and Drink
    - peopleplaces: People and Places
    - geography: Geography
    - historyholidays: History and Holidays
    - entertainment: Entertainment
    - toysgames: Toys and Games
    - music: Music
    - mathematics: Mathematics
    - religionmythology: Religion and Mythology
    - sportsleisure: Sports and Leisure
    
    Example:
        agent.add_skill("api_ninjas_trivia", {
            "tool_name": "get_science_trivia",
            "api_key": "your_api_key",
            "categories": ["sciencenature", "mathematics", "general"]
        })
    """
    
    SKILL_NAME = "api_ninjas_trivia"
    SKILL_DESCRIPTION = "Get trivia questions from API Ninjas"
    SUPPORTS_MULTIPLE_INSTANCES = True
    REQUIRED_ENV_VARS = []  # API key can be passed via params
    
    # Valid API Ninjas trivia categories with human-readable descriptions
    VALID_CATEGORIES = {
        "artliterature": "Art and Literature",
        "language": "Language",
        "sciencenature": "Science and Nature", 
        "general": "General Knowledge",
        "fooddrink": "Food and Drink",
        "peopleplaces": "People and Places",
        "geography": "Geography",
        "historyholidays": "History and Holidays",
        "entertainment": "Entertainment",
        "toysgames": "Toys and Games",
        "music": "Music",
        "mathematics": "Mathematics",
        "religionmythology": "Religion and Mythology",
        "sportsleisure": "Sports and Leisure"
    }
    
    def __init__(self, agent, params: Dict[str, Any] = None):
        """
        Initialize the skill with configuration parameters.
        
        Args:
            agent: The agent instance this skill belongs to
            params: Configuration dictionary containing:
                - tool_name: Custom tool name (default: "get_trivia")
                - api_key: API Ninjas API key (required)
                - categories: Array of category strings (default: all categories)
        """
        super().__init__(agent, params)
        
        # Extract configuration
        self.tool_name = self.params.get('tool_name', 'get_trivia')
        self.api_key = self.params.get('api_key')
        self.categories = self.params.get('categories', list(self.VALID_CATEGORIES.keys()))
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate the skill configuration."""
        # Validate API key
        if not self.api_key or not isinstance(self.api_key, str):
            raise ValueError("api_key parameter is required and must be a non-empty string")
        
        # Validate categories
        if not isinstance(self.categories, list) or len(self.categories) == 0:
            raise ValueError("categories parameter must be a non-empty list")
        
        # Validate each category
        for i, category in enumerate(self.categories):
            if not isinstance(category, str):
                raise ValueError(f"Category {i} must be a string")
            if category not in self.VALID_CATEGORIES:
                valid_cats = ', '.join(self.VALID_CATEGORIES.keys())
                raise ValueError(f"Category '{category}' is not valid. Valid categories: {valid_cats}")
    
    def setup(self) -> bool:
        """
        Setup the skill - validates API key is available.
        
        Returns:
            True if setup successful
        """
        # API key validation already done in _validate_config
        return True
    
    def register_tools(self) -> None:
        """Register SWAIG tools with the agent"""
        tools = self.get_tools()
        for tool in tools:
            # Merge any swaig_fields from params into the tool
            if self.swaig_fields:
                tool.update(self.swaig_fields)
            self.agent.register_swaig_function(tool)
    
    def get_instance_key(self) -> str:
        """
        Generate a unique instance key for this skill configuration.
        
        Returns:
            Unique key combining skill name and tool name
        """
        return f"{self.SKILL_NAME}_{self.tool_name}"
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Generate the SWAIG tool with DataMap webhook.
        
        Returns:
            List containing the generated tool configuration
        """
        # Build enum values and descriptions
        enum_values = []
        descriptions = []
        
        for category in self.categories:
            enum_values.append(category)
            descriptions.append(f"{category}: {self.VALID_CATEGORIES[category]}")
        
        # Build parameter description
        description = "Category for trivia question. Options: " + "; ".join(descriptions)
        
        # Create the tool configuration with DataMap webhook
        tool = {
            "function": self.tool_name,
            "description": f"Get trivia questions for {self.tool_name.replace('_', ' ')}",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": description,
                        "enum": enum_values
                    }
                },
                "required": ["category"]
            },
            "data_map": {
                "webhooks": [
                    {
                        "url": "https://api.api-ninjas.com/v1/trivia?category=%{args.category}",
                        "method": "GET",
                        "headers": {
                            "X-Api-Key": self.api_key
                        },
                        "output": FunctionResult(
                            "Category %{array[0].category} question: %{array[0].question} Answer: %{array[0].answer}, be sure to give the user time to answer before saying the answer."
                        ).to_dict()
                    }
                ],
                "error_keys": ["error"],
                "output": FunctionResult(
                    "Sorry, I cannot get trivia questions right now. Please try again later."
                ).to_dict()
            }
        }
        
        return [tool]
    
    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get the parameter schema for the API Ninjas Trivia skill.
        
        Returns parameter definitions for GUI configuration.
        """
        schema = super().get_parameter_schema()
        
        # Build categories enum description
        category_options = []
        for key, desc in cls.VALID_CATEGORIES.items():
            category_options.append(f"{key} ({desc})")
        
        schema.update({
            "api_key": {
                "type": "string",
                "description": "API Ninjas API key",
                "required": True,
                "hidden": True,
                "env_var": "API_NINJAS_KEY"
            },
            "categories": {
                "type": "array",
                "description": "List of trivia categories to enable. Available: " + ", ".join(category_options),
                "default": list(cls.VALID_CATEGORIES.keys()),
                "required": False,
                "items": {
                    "type": "string",
                    "enum": list(cls.VALID_CATEGORIES.keys())
                }
            }
        })
        
        return schema 