#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Service discovery and loading functionality - new simplified approach
"""

import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import asyncio
import sys
import io
import contextlib

# Import after checking if available
try:
    from signalwire.core.agent_base import AgentBase
    from signalwire.core.swml_service import SWMLService
    from fastapi import Request, Response
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    AgentBase = None
    SWMLService = None
    Request = None
    Response = None
    DEPENDENCIES_AVAILABLE = False


class ServiceCapture:
    """Captures SWMLService instances when they try to run/serve"""
    
    def __init__(self):
        self.captured_services: List[SWMLService] = []
        self.original_methods = {}
        
    def capture(self, service_path: str, suppress_output: bool = False) -> List[SWMLService]:
        """
        Execute a service file and capture any services that try to run
        
        Args:
            service_path: Path to the Python file
            suppress_output: If True, suppress stdout during module execution
            
        Returns:
            List of captured SWMLService instances
        """
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available. Please install signalwire-agents package.")
            
        service_path = Path(service_path).resolve()
        
        if not service_path.exists():
            raise FileNotFoundError(f"Service file not found: {service_path}")
            
        if not service_path.suffix == '.py':
            raise ValueError(f"Service file must be a Python file (.py): {service_path}")
        
        # Reset captured services
        self.captured_services = []
        
        # Apply patches
        self._apply_patches()
        
        # Context manager for optional stdout suppression
        stdout_context = io.StringIO() if suppress_output else None
        
        try:
            with contextlib.redirect_stdout(stdout_context) if suppress_output else contextlib.nullcontext():
                # Load and execute the module
                spec = importlib.util.spec_from_file_location("__main__", service_path)
                module = importlib.util.module_from_spec(spec)
                
                # Set __name__ to "__main__" to trigger if __name__ == "__main__": blocks
                module.__name__ = "__main__"
                
                try:
                    spec.loader.exec_module(module)
                except Exception as e:
                    # Module might have called run/serve which we intercepted
                    if not self.captured_services:
                        # If we didn't capture anything, the error is real
                        raise ImportError(f"Failed to load service module: {e}")
        finally:
            # Always restore original methods
            self._restore_patches()
            
        return self.captured_services
    
    def _apply_patches(self):
        """Apply patches to capture services"""
        
        # Store reference to self for use in closures
        capture_self = self
        
        def mock_run(service_instance, *args, **kwargs):
            """Capture service when run() is called"""
            capture_self.captured_services.append(service_instance)
            # Don't print during stdout suppression
            # Don't actually run - we're just capturing
            return service_instance
            
        def mock_serve(service_instance, *args, **kwargs):
            """Capture service when serve() is called"""
            capture_self.captured_services.append(service_instance)
            # Don't print during stdout suppression
            # Don't actually serve - we're just capturing
            return service_instance
            
        # Apply patches to both SWMLService and AgentBase
        for base_class in [SWMLService, AgentBase]:
            if base_class:
                if hasattr(base_class, 'run'):
                    self.original_methods[(base_class, 'run')] = base_class.run
                    base_class.run = mock_run
                    
                if hasattr(base_class, 'serve'):
                    self.original_methods[(base_class, 'serve')] = base_class.serve
                    base_class.serve = mock_serve
    
    def _restore_patches(self):
        """Restore original methods"""
        for (base_class, method_name), original_method in self.original_methods.items():
            setattr(base_class, method_name, original_method)
        self.original_methods.clear()


async def simulate_request_to_service(
    service: SWMLService,
    method: str = "POST",
    body: Optional[dict] = None,
    query_params: Optional[dict] = None,
    headers: Optional[dict] = None
) -> dict:
    """
    Simulate a request to a SWMLService instance
    
    Args:
        service: The SWMLService instance
        method: HTTP method (GET or POST)
        body: Request body for POST requests
        query_params: Query parameters
        headers: Request headers
        
    Returns:
        The service's response as a dict
    """
    # Create a mock request
    from signalwire.cli.simulation.mock_env import create_mock_request
    
    request = create_mock_request(
        method=method,
        headers=headers or {},
        query_params=query_params or {},
        body=body or {}
    )
    
    # Create a mock response
    response = Response()
    
    # Call the service's request handler
    result = await service._handle_request(request, response)
    
    # If result is a Response object, extract the content
    if hasattr(result, 'body'):
        # FastAPI Response
        import json
        return json.loads(result.body.decode())
    elif isinstance(result, dict):
        return result
    else:
        # Try to get content from response
        return {"error": "Unable to parse response"}


def load_and_simulate_service(
    service_path: str,
    route: Optional[str] = None,
    method: str = "POST",
    body: Optional[dict] = None,
    query_params: Optional[dict] = None,
    headers: Optional[dict] = None,
    suppress_output: bool = False
) -> dict:
    """
    Load a service file and simulate a request to it
    
    This is the main entry point that combines loading and request simulation
    
    Args:
        service_path: Path to the service file
        route: Optional route to request (for multi-service files)
        method: HTTP method
        body: Request body
        query_params: Query parameters
        headers: Request headers
        
    Returns:
        The service's response
    """
    # Capture services from the file
    capturer = ServiceCapture()
    services = capturer.capture(service_path, suppress_output=suppress_output)
    
    if not services:
        raise ValueError(f"No services found in {service_path}")
    
    # Select the appropriate service
    if len(services) == 1:
        service = services[0]
    else:
        # Multiple services - need to select by route
        if not route:
            # List available routes
            routes = [s.route for s in services]
            raise ValueError(
                f"Multiple services found. Please specify a route.\n"
                f"Available routes: {', '.join(routes)}"
            )
        
        # Find service by route
        service = None
        for s in services:
            if s.route == route:
                service = s
                break
                
        if not service:
            available = [s.route for s in services]
            raise ValueError(
                f"No service found for route '{route}'.\n"
                f"Available routes: {', '.join(available)}"
            )
    
    # Simulate the request
    return asyncio.run(simulate_request_to_service(
        service,
        method=method,
        body=body,
        query_params=query_params,
        headers=headers
    ))


# Backward compatibility
def load_agent_from_file(agent_path: str, agent_class_name: Optional[str] = None, suppress_output: bool = False) -> 'AgentBase':
    """
    Backward compatibility wrapper
    
    Note: This still uses the direct extraction approach for compatibility
    """
    # Use the new service capture but ensure we get an AgentBase
    capturer = ServiceCapture()
    services = capturer.capture(agent_path, suppress_output=suppress_output)
    
    # Filter to only agents
    agents = [s for s in services if isinstance(s, AgentBase)]
    
    if not agents:
        raise ValueError(f"No agents found in {agent_path}")
    
    if len(agents) == 1:
        return agents[0]
    
    # Multiple agents - try to match by class name
    if agent_class_name:
        for agent in agents:
            if agent.__class__.__name__ == agent_class_name:
                return agent
    
    # Return first agent
    return agents[0]


def discover_agents_in_file(agent_path: str) -> List[Dict[str, Any]]:
    """
    Backward compatibility wrapper
    """
    capturer = ServiceCapture()
    services = capturer.capture(agent_path)
    
    # Convert to old format
    agents_found = []
    for service in services:
        if isinstance(service, AgentBase):
            agents_found.append({
                'name': service.name,
                'class_name': service.__class__.__name__,
                'type': 'instance',
                'agent_name': service.name,
                'route': service.route,
                'description': service.__class__.__doc__,
                'object': service
            })
    
    return agents_found