"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from typing import List, Dict, Any
import re

from signalwire.core.skill_base import SkillBase
from signalwire.core.data_map import DataMap
from signalwire.core.function_result import FunctionResult


class SWMLTransferSkill(SkillBase):
    """Skill for transferring calls between agents using SWML with pattern matching"""
    
    SKILL_NAME = "swml_transfer"
    SKILL_DESCRIPTION = "Transfer calls between agents based on pattern matching"
    SKILL_VERSION = "1.0.0"
    REQUIRED_PACKAGES = []
    REQUIRED_ENV_VARS = []
    
    # Enable multiple instances support
    SUPPORTS_MULTIPLE_INSTANCES = True
    
    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Dict[str, Any]]:
        """Get parameter schema for SWML Transfer skill"""
        schema = super().get_parameter_schema()
        schema.update({
            "transfers": {
                "type": "object",
                "description": "Transfer configurations mapping patterns to destinations",
                "required": True,
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "SWML endpoint URL for agent transfer"
                        },
                        "address": {
                            "type": "string", 
                            "description": "Phone number or SIP address for direct connect"
                        },
                        "message": {
                            "type": "string",
                            "description": "Message to say before transferring",
                            "default": "Transferring you now..."
                        },
                        "return_message": {
                            "type": "string",
                            "description": "Message when returning from transfer",
                            "default": "The transfer is complete. How else can I help you?"
                        },
                        "post_process": {
                            "type": "boolean",
                            "description": "Whether to process message with AI before saying",
                            "default": True
                        },
                        "final": {
                            "type": "boolean",
                            "description": "Whether transfer is permanent (true) or temporary (false)",
                            "default": True
                        },
                        "from_addr": {
                            "type": "string",
                            "description": "Caller ID for connect action (optional)"
                        }
                    }
                }
            },
            "description": {
                "type": "string",
                "description": "Description for the transfer tool",
                "default": "Transfer call based on pattern matching",
                "required": False
            },
            "parameter_name": {
                "type": "string",
                "description": "Name of the parameter that accepts the transfer type",
                "default": "transfer_type",
                "required": False
            },
            "parameter_description": {
                "type": "string",
                "description": "Description for the transfer type parameter",
                "default": "The type of transfer to perform",
                "required": False
            },
            "default_message": {
                "type": "string",
                "description": "Message when no pattern matches",
                "default": "Please specify a valid transfer type.",
                "required": False
            },
            "default_post_process": {
                "type": "boolean",
                "description": "Whether to process default message with AI",
                "default": False,
                "required": False
            },
            "required_fields": {
                "type": "object",
                "description": "Additional required fields to collect before transfer",
                "default": {},
                "required": False,
                "additionalProperties": {
                    "type": "string",
                    "description": "Field description"
                }
            }
        })
        return schema
    
    def get_instance_key(self) -> str:
        """
        Get the key used to track this skill instance
        
        For SWML transfer, we use the tool name to differentiate instances
        """
        tool_name = self.params.get('tool_name', 'transfer_call')
        return f"{self.SKILL_NAME}_{tool_name}"
    
    def setup(self) -> bool:
        """Setup and validate skill configuration"""
        # Validate required parameters
        required_params = ['transfers']
        missing_params = [param for param in required_params if not self.params.get(param)]
        if missing_params:
            self.logger.error(f"Missing required parameters: {missing_params}")
            return False
        
        # Validate transfers structure
        transfers = self.params.get('transfers', {})
        if not isinstance(transfers, dict):
            self.logger.error("'transfers' parameter must be a dictionary")
            return False
        
        # Validate each transfer configuration
        for pattern, config in transfers.items():
            if not isinstance(config, dict):
                self.logger.error(f"Transfer config for pattern '{pattern}' must be a dictionary")
                return False
            
            # Must have either 'url' or 'address'
            if 'url' not in config and 'address' not in config:
                self.logger.error(f"Transfer config for pattern '{pattern}' must include either 'url' or 'address'")
                return False
            
            if 'url' in config and 'address' in config:
                self.logger.error(f"Transfer config for pattern '{pattern}' cannot have both 'url' and 'address'")
                return False
            
            # Set defaults for optional fields
            config.setdefault('message', f"Transferring you now...")
            config.setdefault('return_message', "The transfer is complete. How else can I help you?")
            config.setdefault('post_process', True)
            config.setdefault('final', True)  # Default to permanent transfer
            # from_addr is optional for connect action only
        
        # Store configuration
        self.tool_name = self.params.get('tool_name', 'transfer_call')
        self.description = self.params.get('description', 'Transfer call based on pattern matching')
        self.parameter_name = self.params.get('parameter_name', 'transfer_type')
        self.parameter_description = self.params.get('parameter_description', 'The type of transfer to perform')
        self.transfers = transfers
        self.default_message = self.params.get('default_message', 'Please specify a valid transfer type.')
        self.default_post_process = self.params.get('default_post_process', False)
        
        # Required fields configuration
        self.required_fields = self.params.get('required_fields', {})
        
        return True
    
    def register_tools(self) -> None:
        """Register the transfer tool with pattern matching"""
        
        # Build the DataMap tool with all patterns
        transfer_tool = (DataMap(self.tool_name)
            .description(self.description)
            .parameter(self.parameter_name, 'string', self.parameter_description, required=True)
        )
        
        # Add required fields as parameters
        for field_name, field_description in self.required_fields.items():
            transfer_tool = transfer_tool.parameter(
                field_name, 
                'string', 
                field_description, 
                required=True
            )
        
        # Add expression for each pattern
        for pattern, config in self.transfers.items():
            # Create the function result with transfer
            result = FunctionResult(
                config['message'], 
                post_process=config['post_process']
            )
            
            # Add required fields to global data under call_data key
            if self.required_fields:
                call_data = {}
                for field_name in self.required_fields.keys():
                    call_data[field_name] = f"${{args.{field_name}}}"
                result = result.update_global_data({
                    "call_data": call_data
                })
            
            # Add the transfer action based on whether url or address is provided
            if 'url' in config:
                # Use swml_transfer for SWML endpoints
                result = result.swml_transfer(
                    config['url'], 
                    config['return_message'],
                    config.get('final', True)
                )
            else:
                # Use connect for addresses (phone numbers, SIP, etc.)
                result = result.connect(
                    config['address'],
                    config.get('final', True),
                    config.get('from_addr', None)
                )
            
            # Add the expression to the DataMap
            transfer_tool = transfer_tool.expression(
                f'${{{f"args.{self.parameter_name}"}}}',
                pattern,
                result
            )
        
        # Add default fallback expression
        default_result = FunctionResult(
            self.default_message,
            post_process=self.default_post_process
        )
        
        # For fallback, still save required fields if provided
        if self.required_fields:
            call_data = {}
            for field_name in self.required_fields.keys():
                call_data[field_name] = f"${{args.{field_name}}}"
            default_result = default_result.update_global_data({
                "call_data": call_data
            })
        
        transfer_tool = transfer_tool.expression(
            f'${{{f"args.{self.parameter_name}"}}}',
            r'/.*/',  # Match anything as fallback
            default_result
        )
        
        # Register the tool with the agent
        if hasattr(self.agent, 'register_swaig_function'):
            self.agent.register_swaig_function(transfer_tool.to_swaig_function())
        else:
            # Fallback to define_tool if register_swaig_function is not available
            self.logger.error("Agent does not have register_swaig_function method")
    
    def get_hints(self) -> List[str]:
        """Return speech recognition hints"""
        hints = []
        
        # Extract common words from patterns for hints
        for pattern in self.transfers.keys():
            # Remove regex delimiters and flags
            clean_pattern = pattern
            # Remove leading and trailing slashes
            if clean_pattern.startswith('/'):
                clean_pattern = clean_pattern[1:]
            if clean_pattern.endswith('/'):
                clean_pattern = clean_pattern[:-1]
            # Remove flags after the pattern (e.g., 'i' for case-insensitive)
            elif clean_pattern.endswith('/i'):
                clean_pattern = clean_pattern[:-2]
            
            # Only add if it's not a catch-all pattern
            if clean_pattern and not clean_pattern.startswith('.'):
                # Handle patterns with alternatives (e.g., "sales|billing")
                if '|' in clean_pattern:
                    for part in clean_pattern.split('|'):
                        hints.append(part.strip().lower())
                else:
                    hints.append(clean_pattern.lower())
        
        # Add common transfer-related words
        hints.extend(['transfer', 'connect', 'speak to', 'talk to'])
        
        return hints
    
    def get_prompt_sections(self) -> List[Dict[str, Any]]:
        """Return prompt sections to add to agent"""
        sections = []
        
        # Build a list of transfer destinations with their patterns
        if self.transfers:
            transfer_bullets = []
            
            for pattern, config in self.transfers.items():
                # Extract meaningful name from pattern
                # Remove regex delimiters and flags
                clean_pattern = pattern
                # Remove leading and trailing slashes
                if clean_pattern.startswith('/'):
                    clean_pattern = clean_pattern[1:]
                if clean_pattern.endswith('/'):
                    clean_pattern = clean_pattern[:-1]
                # Remove flags after the pattern (e.g., 'i' for case-insensitive)
                elif clean_pattern.endswith('/i'):
                    clean_pattern = clean_pattern[:-2]
                
                # Only add if it's not a catch-all pattern
                if clean_pattern and not clean_pattern.startswith('.'):
                    # Create a description for this transfer destination
                    if 'url' in config:
                        destination = config['url']
                    else:
                        destination = config['address']
                    transfer_desc = f'"{clean_pattern}" - transfers to {destination}'
                    transfer_bullets.append(transfer_desc)
            
            # Add the Transferring section
            sections.append({
                "title": "Transferring",
                "body": f"You can transfer calls using the {self.tool_name} function with the following destinations:",
                "bullets": transfer_bullets
            })
            
            # Add usage instructions
            bullets = [
                f"Use the {self.tool_name} function when a transfer is needed",
                f"Pass the destination type to the '{self.parameter_name}' parameter"
            ]
            
            # Add required fields instructions if configured
            if self.required_fields:
                bullets.append("You must provide the following information before transferring:")
                for field_name, field_description in self.required_fields.items():
                    bullets.append(f"  - {field_name}: {field_description}")
                bullets.append("All required information will be saved under 'call_data' for the next agent")
            
            bullets.extend([
                f"The system will match patterns and handle the transfer automatically",
                "After transfer completes, you'll regain control of the conversation"
            ])
            
            sections.append({
                "title": "Transfer Instructions",
                "body": f"How to use the transfer capability:",
                "bullets": bullets
            })
        
        return sections