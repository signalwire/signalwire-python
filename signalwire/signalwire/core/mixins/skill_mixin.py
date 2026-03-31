"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from typing import List, Dict, Any, Optional


class SkillMixin:
    """
    Mixin class containing all skill management methods for AgentBase
    """
    
    def add_skill(self, skill_name: str, params: Optional[Dict[str, Any]] = None) -> 'AgentBase':
        """
        Add a skill to this agent
        
        Args:
            skill_name: Name of the skill to add
            params: Optional parameters to pass to the skill for configuration
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If skill not found or failed to load with detailed error message
        """
        # Debug logging
        self.log.debug("add_skill_called",
                      skill_name=skill_name,
                      agent_id=id(self),
                      registry_id=id(self._tool_registry) if hasattr(self, '_tool_registry') else None,
                      is_ephemeral=getattr(self, '_is_ephemeral', False))
        
        success, error_message = self.skill_manager.load_skill(skill_name, params=params)
        if not success:
            raise ValueError(f"Failed to load skill '{skill_name}': {error_message}")
        return self

    def remove_skill(self, skill_name: str) -> 'AgentBase':
        """Remove a skill from this agent"""
        self.skill_manager.unload_skill(skill_name)
        return self

    def list_skills(self) -> List[str]:
        """List currently loaded skills"""
        return self.skill_manager.list_loaded_skills()

    def has_skill(self, skill_name: str) -> bool:
        """Check if skill is loaded"""
        return self.skill_manager.has_skill(skill_name)