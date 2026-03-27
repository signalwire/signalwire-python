"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
ReceptionistAgent - Prefab agent for greeting callers and transferring them to appropriate departments
"""

from typing import List, Dict, Any, Optional, Union
import json

from signalwire.core.agent_base import AgentBase
from signalwire.core.function_result import FunctionResult


class ReceptionistAgent(AgentBase):
    """
    A prefab agent designed to act as a receptionist that:
    1. Greets callers
    2. Collects basic information about their needs
    3. Transfers them to the appropriate department
    
    Example:
        agent = ReceptionistAgent(
            departments=[
                {"name": "sales", "description": "For product inquiries, pricing, and purchasing", "number": "+15551235555"},
                {"name": "support", "description": "For technical help and troubleshooting", "number": "+15551236666"}
            ]
        )
    """
    
    def __init__(
        self,
        departments: List[Dict[str, str]],
        name: str = "receptionist", 
        route: str = "/receptionist",
        greeting: str = "Thank you for calling. How can I help you today?",
        voice: str = "rime.spore",
        **kwargs
    ):
        """
        Initialize a receptionist agent
        
        Args:
            departments: List of departments to transfer to, each with:
                - name: Department identifier (e.g., "sales")
                - description: Description of department's purpose
                - number: Phone number for transfer
            name: Agent name for the route
            route: HTTP route for this agent
            greeting: Initial greeting message
            voice: Voice ID to use
            **kwargs: Additional arguments for AgentBase
        """
        # Initialize the base agent
        super().__init__(
            name=name,
            route=route,
            use_pom=True,
            **kwargs
        )
        
        # Validate departments format
        self._validate_departments(departments)
        
        # Store greeting
        self._greeting = greeting
        
        # Set up global data with departments and initial state
        self.set_global_data({
            "departments": departments,
            "caller_info": {}
        })
        
        # Build a prompt
        self._build_prompt()
        
        # Configure agent settings
        self._configure_agent_settings(voice)
        
        # Register tools
        self._register_tools()
    
    def _validate_departments(self, departments):
        """Validate that departments are in the correct format"""
        if not departments:
            raise ValueError("At least one department is required")
            
        for i, dept in enumerate(departments):
            if "name" not in dept:
                raise ValueError(f"Department {i+1} is missing 'name' field")
            if "description" not in dept:
                raise ValueError(f"Department {i+1} is missing 'description' field")
            if "number" not in dept:
                raise ValueError(f"Department {i+1} is missing 'number' field")
    
    def _build_prompt(self):
        """Build the agent's prompt with personality, goals, and instructions"""
        
        # Set personality
        self.prompt_add_section(
            "Personality", 
            body="You are a friendly and professional receptionist. You speak clearly and efficiently while maintaining a warm, helpful tone."
        )
        
        # Set goal
        self.prompt_add_section(
            "Goal", 
            body="Your goal is to greet callers, collect their basic information, and transfer them to the appropriate department."
        )
        
        # Set instructions
        self.prompt_add_section(
            "Instructions", 
            bullets=[
                f"Begin by greeting the caller with: '{self._greeting}'",
                "Collect their name and a brief description of their needs.",
                "Based on their needs, determine which department would be most appropriate.",
                "Use the collect_caller_info function when you have their name and reason for calling.",
                "Use the transfer_call function to transfer them to the appropriate department.",
                "Before transferring, always confirm with the caller that they're being transferred to the right department.",
                "If a caller's request doesn't clearly match a department, ask follow-up questions to clarify."
            ]
        )
        
        # Add context with department information
        global_data = self._global_data
        departments = global_data.get("departments", [])
        
        department_bullets = []
        for dept in departments:
            department_bullets.append(f"{dept['name']}: {dept['description']}")
        
        self.prompt_add_section(
            "Available Departments",
            bullets=department_bullets
        )
        
        # Add a post-prompt for summary generation
        self.set_post_prompt("""
        Return a JSON summary of the conversation:
        {
            "caller_name": "CALLER'S NAME",
            "reason": "REASON FOR CALLING",
            "department": "DEPARTMENT TRANSFERRED TO",
            "satisfaction": "high/medium/low (estimated caller satisfaction)"
        }
        """)
    
    def _configure_agent_settings(self, voice):
        """Configure additional agent settings"""
        
        # Set AI behavior parameters
        self.set_params({
            "end_of_speech_timeout": 700,
            "speech_event_timeout": 1000,
            "transfer_summary": True  # Enable call summary transfer between agents
        })
        
        # Set language with specified voice
        self.add_language(
            name="English",
            code="en-US",
            voice=voice
        )
    
    def _register_tools(self):
        """Register the tools this agent needs"""
        
        # Define collect_caller_info tool
        self.define_tool(
            name="collect_caller_info",
            description="Collect the caller's information for routing",
            parameters={
                "name": {
                    "type": "string",
                    "description": "The caller's name"
                },
                "reason": {
                    "type": "string",
                    "description": "The reason for the call"
                }
            },
            handler=self._collect_caller_info_handler
        )
        
        # Define transfer_call tool
        # First, get the department names from global data
        global_data = self._global_data
        departments = global_data.get("departments", [])
        department_names = [dept["name"] for dept in departments]
        
        self.define_tool(
            name="transfer_call",
            description="Transfer the caller to the appropriate department",
            parameters={
                "department": {
                    "type": "string",
                    "description": "The department to transfer to",
                    "enum": department_names
                }
            },
            handler=self._transfer_call_handler
        )
    
    def _collect_caller_info_handler(self, args, raw_data):
        """Handler for collect_caller_info tool"""
        
        # Get the caller info
        name = args.get("name", "")
        reason = args.get("reason", "")
        
        # Create response with global data update
        result = FunctionResult(
            f"Thank you, {name}. I've noted that you're calling about {reason}."
        )
        
        # Update global data with caller info
        result.add_actions([
            {"set_global_data": {
                "caller_info": {
                    "name": name,
                    "reason": reason
                }
            }}
        ])
        
        return result
    
    def _transfer_call_handler(self, args, raw_data):
        """Handler for transfer_call tool"""
        
        # Get the department
        department_name = args.get("department", "")
        
        # Get global data
        global_data = raw_data.get("global_data", {})
        caller_info = global_data.get("caller_info", {})
        name = caller_info.get("name", "the caller")
        departments = global_data.get("departments", [])
        
        # Find the department in the list
        department = None
        for dept in departments:
            if dept["name"] == department_name:
                department = dept
                break
        
        # If department not found, return error
        if not department:
            return FunctionResult(f"Sorry, I couldn't find the {department_name} department.")
        
        # Get transfer number
        transfer_number = department.get("number", "")
        
        # Create result with transfer using the connect helper method
        # post_process=True allows the AI to speak the response before executing the transfer
        result = FunctionResult(
            f"I'll transfer you to our {department_name} department now. Thank you for calling, {name}!",
            post_process=True
        )
        
        # Use the connect helper instead of manually constructing SWML
        # final=True means this is a permanent transfer (call exits the agent)
        result.connect(transfer_number, final=True)
        
        # Alternative: Immediate transfer without AI speaking (faster but less friendly)
        # result = FunctionResult()  # No response text needed
        # result.connect(transfer_number, final=True)  # Executes immediately from function call
        
        return result
        
    def on_summary(self, summary, raw_data=None):
        """
        Process the conversation summary
        
        Args:
            summary: Summary data from the conversation
            raw_data: The complete raw POST data from the request
        """
        # Subclasses can override this to handle the summary
        pass 