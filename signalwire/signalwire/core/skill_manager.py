"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from typing import Dict, List, Type, Any, Optional
from signalwire.core.logging_config import get_logger
from signalwire.core.skill_base import SkillBase

class SkillManager:
    """Manages loading and lifecycle of agent skills"""
    
    def __init__(self, agent):
        self.agent = agent
        self.loaded_skills: Dict[str, SkillBase] = {}
        self.logger = get_logger("skill_manager")
        
    def load_skill(self, skill_name: str, skill_class: Type[SkillBase] = None, params: Optional[Dict[str, Any]] = None) -> tuple[bool, str]:
        """
        Load and setup a skill by name
        
        Args:
            skill_name: Name of the skill to load
            skill_class: Optional skill class (if not provided, will try to find it)
            params: Optional parameters to pass to the skill
            
        Returns:
            tuple: (success, error_message) - error_message is empty string if successful
        """
        # Get skill class from registry if not provided
        if skill_class is None:
            try:
                from signalwire.skills.registry import skill_registry
                skill_class = skill_registry.get_skill_class(skill_name)
                if skill_class is None:
                    error_msg = f"Skill '{skill_name}' not found in registry"
                    self.logger.error(error_msg)
                    return False, error_msg
            except ImportError:
                error_msg = f"Skills registry not available. Cannot load skill '{skill_name}'"
                self.logger.error(error_msg)
                return False, error_msg
        
        # Validate that the skill has a proper parameter schema
        if not hasattr(skill_class, 'get_parameter_schema') or not callable(getattr(skill_class, 'get_parameter_schema')):
            error_msg = f"Skill '{skill_name}' must have get_parameter_schema() classmethod"
            self.logger.error(error_msg)
            return False, error_msg
        
        try:
            # Validate the parameter schema
            schema = skill_class.get_parameter_schema()
            if not isinstance(schema, dict):
                error_msg = f"Skill '{skill_name}'.get_parameter_schema() must return a dictionary"
                self.logger.error(error_msg)
                return False, error_msg
                
            # Ensure it's not an empty schema
            if not schema:
                error_msg = f"Skill '{skill_name}'.get_parameter_schema() returned empty dictionary"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Check if the skill has overridden the method
            from signalwire.core.skill_base import SkillBase
            skill_method = getattr(skill_class, 'get_parameter_schema', None)
            base_method = getattr(SkillBase, 'get_parameter_schema', None)
            
            if skill_method and base_method:
                # For class methods, check the underlying function
                skill_func = skill_method.__func__ if hasattr(skill_method, '__func__') else skill_method
                base_func = base_method.__func__ if hasattr(base_method, '__func__') else base_method
                
                if skill_func is base_func:
                    # Get base schema to check if skill added any parameters
                    base_schema = SkillBase.get_parameter_schema()
                    if set(schema.keys()) == set(base_schema.keys()):
                        error_msg = f"Skill '{skill_name}' must override get_parameter_schema() to define its specific parameters"
                        self.logger.error(error_msg)
                        return False, error_msg
                
        except AttributeError as e:
            error_msg = f"Skill '{skill_name}' must properly implement get_parameter_schema() classmethod"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Skill '{skill_name}'.get_parameter_schema() failed: {e}"
            self.logger.error(error_msg)
            return False, error_msg
        
        try:
            # Create skill instance with parameters to get the instance key
            skill_instance = skill_class(self.agent, params)
            instance_key = skill_instance.get_instance_key()
            
            # Check if this instance is already loaded
            if instance_key in self.loaded_skills:
                # For single-instance skills, this is an error
                if not skill_instance.SUPPORTS_MULTIPLE_INSTANCES:
                    error_msg = f"Skill '{skill_name}' is already loaded and does not support multiple instances"
                    self.logger.error(error_msg)
                    return False, error_msg
                else:
                    # For multi-instance skills, just warn and return success
                    self.logger.warning(f"Skill instance '{instance_key}' is already loaded")
                    return True, ""
            
            # Validate environment variables with specific error details
            import os
            missing_env_vars = [var for var in skill_instance.REQUIRED_ENV_VARS if not os.getenv(var)]
            if missing_env_vars:
                error_msg = f"Missing required environment variables: {missing_env_vars}"
                self.logger.error(error_msg)
                return False, error_msg
                
            # Validate packages with specific error details  
            import importlib
            missing_packages = []
            for package in skill_instance.REQUIRED_PACKAGES:
                try:
                    importlib.import_module(package)
                except ImportError:
                    missing_packages.append(package)
            if missing_packages:
                error_msg = f"Missing required packages: {missing_packages}"
                self.logger.error(error_msg)
                return False, error_msg
                
            # Setup the skill
            if not skill_instance.setup():
                error_msg = f"Failed to setup skill '{skill_name}'"
                self.logger.error(error_msg)
                return False, error_msg
                
            # Register tools with agent
            skill_instance.register_tools()
            
            # Add hints and global data to agent
            hints = skill_instance.get_hints()
            if hints:
                self.agent.add_hints(hints)
                
            global_data = skill_instance.get_global_data()
            if global_data:
                self.agent.update_global_data(global_data)
                
            # Add prompt sections
            prompt_sections = skill_instance.get_prompt_sections()
            for section in prompt_sections:
                self.agent.prompt_add_section(**section)
            
            # Store loaded skill using instance key
            self.loaded_skills[instance_key] = skill_instance
            self.logger.info(f"Successfully loaded skill instance '{instance_key}' (skill: '{skill_name}')")
            return True, ""
            
        except ValueError as e:
            # Check if this is a duplicate tool registration (expected during agent cloning)
            if "already exists" in str(e):
                debug_msg = f"Skill '{skill_name}' already loaded, skipping duplicate registration"
                self.logger.debug(debug_msg)
                return True, ""  # Not an error, skill is already available
            else:
                error_msg = f"Error loading skill '{skill_name}': {e}"
                self.logger.error(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"Error loading skill '{skill_name}': {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def unload_skill(self, skill_identifier: str) -> bool:
        """
        Unload a skill and cleanup
        
        Args:
            skill_identifier: Either a skill name or an instance key
            
        Returns:
            bool: True if successfully unloaded, False otherwise
        """
        # Try to find the skill by identifier (could be skill name or instance key)
        skill_instance = None
        instance_key = None
        
        # First try as direct instance key
        if skill_identifier in self.loaded_skills:
            instance_key = skill_identifier
            skill_instance = self.loaded_skills[skill_identifier]
        
        if skill_instance is None:
            self.logger.warning(f"Skill '{skill_identifier}' is not loaded")
            return False
            
        try:
            skill_instance.cleanup()
            del self.loaded_skills[instance_key]
            self.logger.info(f"Successfully unloaded skill instance '{instance_key}'")
            return True
        except Exception as e:
            self.logger.error(f"Error unloading skill '{skill_identifier}': {e}")
            return False
    
    def list_loaded_skills(self) -> List[str]:
        """List instance keys of currently loaded skills"""
        return list(self.loaded_skills.keys())
    
    def has_skill(self, skill_identifier: str) -> bool:
        """
        Check if skill is currently loaded
        
        Args:
            skill_identifier: Either a skill name or an instance key
            
        Returns:
            bool: True if loaded, False otherwise
        """
        # First try as direct instance key
        if skill_identifier in self.loaded_skills:
            return True
        
        return False
    
    def get_skill(self, skill_identifier: str) -> Optional[SkillBase]:
        """
        Get a loaded skill instance by identifier
        
        Args:
            skill_identifier: Either a skill name or an instance key
            
        Returns:
            SkillBase: The skill instance if found, None otherwise
        """
        # First try as direct instance key
        if skill_identifier in self.loaded_skills:
            return self.loaded_skills[skill_identifier]
        
        return None
    
 