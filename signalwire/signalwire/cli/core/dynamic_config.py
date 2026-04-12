#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Apply dynamic configuration to agents
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from signalwire.core.agent_base import AgentBase
    from ..simulation.mock_env import MockRequest


def apply_dynamic_config(agent: 'AgentBase', mock_request: Optional['MockRequest'] = None, verbose: bool = False) -> None:
    """
    Apply dynamic configuration callback if the agent has one
    
    Args:
        agent: The agent instance
        mock_request: Optional mock request object
        verbose: Whether to print verbose output
    """
    # Check if dynamic config has already been applied to this agent
    if hasattr(agent, '_dynamic_config_applied') and agent._dynamic_config_applied:
        if verbose:
            print("Dynamic configuration already applied, skipping...")
        return
    
    # Check if agent has dynamic config callback
    if hasattr(agent, '_dynamic_config_callback') and agent._dynamic_config_callback:
        try:
            # Create mock request data if not provided
            if mock_request is None:
                from ..simulation.mock_env import create_mock_request
                mock_request = create_mock_request()
            
            # Extract request data
            query_params = dict(mock_request.query_params)
            body_params = {}  # Empty for GET requests
            headers = dict(mock_request.headers)
            
            if verbose:
                print("Applying dynamic configuration callback...")
            
            # Call the user's configuration callback directly with the agent
            # This is what pc_builder_service.py expects - to get the agent itself
            agent._dynamic_config_callback(query_params, body_params, headers, agent)
            
            # Mark that dynamic config has been applied to prevent duplicate application
            agent._dynamic_config_applied = True
            
            if verbose:
                print("Dynamic configuration callback applied successfully")
                # Show loaded skills after dynamic config
                skills = agent.list_skills()
                if skills:
                    print(f"Skills loaded by dynamic config: {', '.join(skills)}")
                
        except Exception as e:
            if verbose:
                print(f"Warning: Failed to apply dynamic configuration: {e}")
                import traceback
                traceback.print_exc()