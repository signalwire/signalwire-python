#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Agent discovery and loading functionality
"""

import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import after checking if available
try:
    from signalwire.core.agent_base import AgentBase
    from signalwire.core.swml_service import SWMLService
    # Import the new service loader
    from .service_loader import ServiceCapture, load_agent_from_file as new_load_agent
    AGENT_BASE_AVAILABLE = True
    SWML_SERVICE_AVAILABLE = True
    NEW_LOADER_AVAILABLE = True
except ImportError:
    AgentBase = None
    SWMLService = None
    ServiceCapture = None
    new_load_agent = None
    AGENT_BASE_AVAILABLE = False
    SWML_SERVICE_AVAILABLE = False
    NEW_LOADER_AVAILABLE = False


def discover_services_in_file(service_path: str) -> List[Dict[str, Any]]:
    """
    Discover all available SWML services (including agents) in a Python file without instantiating them
    
    Args:
        service_path: Path to the Python file containing services
        
    Returns:
        List of dictionaries with service information
        
    Raises:
        ImportError: If the file cannot be imported
        FileNotFoundError: If the file doesn't exist
    """
    if not SWML_SERVICE_AVAILABLE:
        raise ImportError("SWMLService not available. Please install signalwire-agents package.")
    
    # Keep backward compatibility
    return _discover_services_impl(service_path)


def discover_agents_in_file(agent_path: str) -> List[Dict[str, Any]]:
    """
    Backward compatibility wrapper - discovers agents in a file
    
    Args:
        agent_path: Path to the Python file containing agents
        
    Returns:
        List of dictionaries with agent information
    """
    # Filter to only return AgentBase instances/classes
    all_services = discover_services_in_file(agent_path)
    return [s for s in all_services if s.get('is_agent', False)]


def _discover_services_impl(service_path: str) -> List[Dict[str, Any]]:
    """
    Internal implementation for discovering services
    """
    service_path = Path(service_path).resolve()
    
    if not service_path.exists():
        raise FileNotFoundError(f"Service file not found: {service_path}")
    
    if not service_path.suffix == '.py':
        raise ValueError(f"Service file must be a Python file (.py): {service_path}")
    
    # Add the module's directory to sys.path temporarily to allow local imports
    import sys
    module_dir = str(service_path.parent)
    sys_path_added = False
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
        sys_path_added = True
    
    # Load the module, but prevent main() execution by setting __name__ to something other than "__main__"
    spec = importlib.util.spec_from_file_location("service_module", service_path)
    module = importlib.util.module_from_spec(spec)
    
    try:
        # Set __name__ to prevent if __name__ == "__main__": blocks from running
        module.__name__ = "service_module"
        spec.loader.exec_module(module)
    except Exception as e:
        # Clean up sys.path if we added to it
        if sys_path_added:
            sys.path.remove(module_dir)
        raise ImportError(f"Failed to load service module: {e}")
    finally:
        # Clean up sys.path after successful load too
        if sys_path_added and module_dir in sys.path:
            sys.path.remove(module_dir)
    
    services_found = []
    
    # Look for SWMLService instances (including AgentBase which inherits from it)
    for name, obj in vars(module).items():
        if isinstance(obj, SWMLService):
            is_agent = isinstance(obj, AgentBase) if AgentBase else False
            services_found.append({
                'name': name,
                'class_name': obj.__class__.__name__,
                'type': 'instance',
                'service_name': getattr(obj, 'name', 'Unknown'),
                'route': getattr(obj, 'route', 'Unknown'),
                'description': obj.__class__.__doc__,
                'object': obj,
                'is_agent': is_agent,
                'has_tools': is_agent and hasattr(obj, '_tool_registry')
            })
    
    # Look for SWMLService subclasses (that could be instantiated)
    for name, obj in vars(module).items():
        if (isinstance(obj, type) and 
            issubclass(obj, SWMLService) and 
            obj not in (SWMLService, AgentBase)):  # Don't include base classes
            # Check if we already found an instance of this class
            instance_found = any(service['class_name'] == name for service in services_found)
            if not instance_found:
                is_agent = AgentBase and issubclass(obj, AgentBase)
                try:
                    # Try to get class information without instantiating
                    service_info = {
                        'name': name,
                        'class_name': name,
                        'type': 'class',
                        'service_name': 'Unknown (not instantiated)',
                        'route': 'Unknown (not instantiated)',
                        'description': obj.__doc__,
                        'object': obj,
                        'is_agent': is_agent,
                        'has_tools': False  # Can't determine without instantiation
                    }
                    services_found.append(service_info)
                except Exception:
                    # If we can't get info, still record that the class exists
                    services_found.append({
                        'name': name,
                        'class_name': name,
                        'type': 'class',
                        'service_name': 'Unknown (not instantiated)',
                        'route': 'Unknown (not instantiated)',
                        'description': obj.__doc__ or 'No description available',
                        'object': obj,
                        'is_agent': is_agent,
                        'has_tools': False
                    })
    
    return services_found


def load_service_from_file(service_path: str, service_identifier: Optional[str] = None, prefer_route: bool = True) -> 'SWMLService':
    """
    Load a SWML service from a Python file
    
    Args:
        service_path: Path to the Python file containing the service
        service_identifier: Optional service identifier - can be class name or route
        prefer_route: If True, interpret identifier as route first, then class name
        
    Returns:
        SWMLService instance (could be AgentBase or basic SWMLService)
        
    Raises:
        ImportError: If the file cannot be imported
        ValueError: If no service is found in the file
    """
    if not SWML_SERVICE_AVAILABLE:
        raise ImportError("SWMLService not available. Please install signalwire-agents package.")
    
    # Use the main implementation
    return _load_service_impl(service_path, service_identifier, prefer_route)


def load_agent_from_file(agent_path: str, agent_class_name: Optional[str] = None) -> 'AgentBase':
    """
    Load an agent from a Python file
    
    Args:
        agent_path: Path to the Python file containing the agent
        agent_class_name: Optional name of the agent class to instantiate
        
    Returns:
        AgentBase instance
        
    Raises:
        ImportError: If the file cannot be imported
        ValueError: If no agent is found in the file
    """
    if not AGENT_BASE_AVAILABLE:
        raise ImportError("AgentBase not available. Please install signalwire-agents package.")
    
    # Check if we're being called from swaig-test --dump-swml (or similar)
    # We can detect this by checking the call stack or environment
    import inspect
    suppress_output = False
    
    # Check if we're in a context where output should be suppressed
    frame = inspect.currentframe()
    try:
        # Walk up the call stack to see if we're being called from dump_swml
        while frame:
            if 'dump_swml' in frame.f_code.co_filename or 'swml_dump' in frame.f_code.co_filename:
                suppress_output = True
                break
            frame = frame.f_back
    finally:
        del frame  # Avoid reference cycles
    
    # Use the old implementation but with a fix for the ordering
    return _load_service_impl(agent_path, agent_class_name, prefer_route=False)


def _load_service_impl(service_path: str, service_identifier: Optional[str] = None, prefer_route: bool = True) -> 'SWMLService':
    """
    Internal implementation for loading services with smart detection
    """
    service_path = Path(service_path).resolve()
    
    if not service_path.exists():
        raise FileNotFoundError(f"Service file not found: {service_path}")
    
    if not service_path.suffix == '.py':
        raise ValueError(f"Service file must be a Python file (.py): {service_path}")
    
    # Add the module's directory to sys.path temporarily to allow local imports
    import sys
    module_dir = str(service_path.parent)
    sys_path_added = False
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
        sys_path_added = True
    
    # Load the module, but prevent main() execution by setting __name__ to something other than "__main__"
    spec = importlib.util.spec_from_file_location("service_module", service_path)
    module = importlib.util.module_from_spec(spec)
    
    try:
        # Set __name__ to prevent if __name__ == "__main__": blocks from running
        module.__name__ = "service_module"
        spec.loader.exec_module(module)
    except Exception as e:
        # Clean up sys.path if we added to it
        if sys_path_added:
            sys.path.remove(module_dir)
        raise ImportError(f"Failed to load service module: {e}")
    finally:
        # Clean up sys.path after successful load too
        if sys_path_added and module_dir in sys.path:
            sys.path.remove(module_dir)
    
    # Find the service instance
    service = None
    
    # If service_identifier is specified and prefer_route is True, try to find by route first
    if service_identifier and prefer_route:
        # First, try to find an existing instance with matching route
        for name, obj in vars(module).items():
            if isinstance(obj, SWMLService) and hasattr(obj, 'route'):
                if obj.route == service_identifier:
                    service = obj
                    break
        
        # If not found, try instantiating classes to check their routes
        if service is None:
            for name, obj in vars(module).items():
                if (isinstance(obj, type) and 
                    issubclass(obj, SWMLService) and 
                    obj not in (SWMLService, AgentBase)):
                    try:
                        temp_instance = obj()
                        if hasattr(temp_instance, 'route') and temp_instance.route == service_identifier:
                            service = temp_instance
                            break
                    except Exception:
                        # Skip classes that can't be instantiated
                        pass
        
        # If still not found and service_identifier looks like a class name, fall back to class name
        if service is None and hasattr(module, service_identifier):
            obj = getattr(module, service_identifier)
            if isinstance(obj, type) and issubclass(obj, SWMLService):
                try:
                    service = obj()
                except Exception as e:
                    raise ValueError(f"No service found with route '{service_identifier}' and failed to instantiate class '{service_identifier}': {e}")
            elif isinstance(obj, SWMLService):
                service = obj
        
        if service is None:
            raise ValueError(f"No service found with route '{service_identifier}'")
    
    # If service_identifier is specified as a class name, try to instantiate that specific class first
    elif service_identifier and not prefer_route:
        if hasattr(module, service_identifier):
            obj = getattr(module, service_identifier)
            if isinstance(obj, type) and issubclass(obj, SWMLService):
                try:
                    service = obj()
                    if service and not service.route.endswith('dummy'):  # Avoid test services with dummy routes
                        pass  # Successfully created specific service
                    else:
                        service = obj()  # Create anyway if requested specifically
                except Exception as e:
                    raise ValueError(f"Failed to instantiate service class '{service_identifier}': {e}")
            elif isinstance(obj, SWMLService):
                # It's already an instance
                service = obj
            else:
                raise ValueError(f"'{service_identifier}' is not a valid SWMLService class or instance")
        else:
            raise ValueError(f"Service class '{service_identifier}' not found in {service_path}")
    
    # Strategy 1: Look for 'agent' or 'service' variable (most common pattern)
    if service is None:
        if hasattr(module, 'agent') and isinstance(module.agent, SWMLService):
            service = module.agent
        elif hasattr(module, 'service') and isinstance(module.service, SWMLService):
            service = module.service
    
    # Strategy 2: Look for any SWMLService instance in module globals
    if service is None:
        services_found = []
        for name, obj in vars(module).items():
            if isinstance(obj, SWMLService):
                services_found.append((name, obj))
        
        if len(services_found) == 1:
            service = services_found[0][1]
        elif len(services_found) > 1:
            # Multiple services found, prefer one named 'agent' or 'service'
            for name, obj in services_found:
                if name in ('agent', 'service'):
                    service = obj
                    break
            # If no preferred variable, use the first one
            if service is None:
                service = services_found[0][1]
                print(f"Warning: Multiple services found, using '{services_found[0][0]}'")
                print(f"Hint: Use --route or service identifier to choose specific service")
    
    # Strategy 3: Look for SWMLService subclass and try to instantiate it
    if service is None and not hasattr(module, 'main'):
        service_classes_found = []
        for name, obj in vars(module).items():
            if (isinstance(obj, type) and 
                issubclass(obj, SWMLService) and 
                obj not in (SWMLService, AgentBase)):
                service_classes_found.append((name, obj))
        
        if len(service_classes_found) == 1:
            try:
                service = service_classes_found[0][1]()
            except Exception as e:
                print(f"Warning: Failed to instantiate {service_classes_found[0][0]}: {e}")
        elif len(service_classes_found) > 1:
            # Multiple service classes found - get detailed info
            service_info = []
            for name, cls in service_classes_found:
                try:
                    # Try to instantiate temporarily to get route
                    temp_instance = cls()
                    route = getattr(temp_instance, 'route', 'Unknown')
                    service_name = getattr(temp_instance, 'name', 'Unknown')
                    service_info.append({
                        'class_name': name,
                        'route': route,
                        'service_name': service_name
                    })
                except Exception:
                    # If instantiation fails, still include the class
                    service_info.append({
                        'class_name': name,
                        'route': 'Unknown (instantiation failed)',
                        'service_name': 'Unknown'
                    })
            
            # Format error message with service details
            error_lines = ["Multiple service classes found:"]
            error_lines.append("")
            for info in service_info:
                error_lines.append(f"  {info['class_name']}:")
                error_lines.append(f"    Route: {info['route']}")
                error_lines.append(f"    Name: {info['service_name']}")
                error_lines.append("")
            error_lines.append("Please specify which service to use:")
            error_lines.append(f"  swaig-test {service_path} --agent-class <ClassName>")
            error_lines.append(f"  swaig-test {service_path} --route <route>")
            
            raise ValueError("\n".join(error_lines))
        else:
            # Try instantiating any SWMLService class we can find
            for name, obj in vars(module).items():
                if (isinstance(obj, type) and 
                    issubclass(obj, SWMLService) and 
                    obj not in (SWMLService, AgentBase)):
                    try:
                        service = obj()
                        break
                    except Exception as e:
                        print(f"Warning: Failed to instantiate {name}: {e}")
    
    # Strategy 4: Try calling a modified main() function that doesn't start the server
    if service is None and hasattr(module, 'main'):
        print("Warning: No agent instance found, attempting to call main() without server startup")
        try:
            # Temporarily patch serve() and run() on both SWMLService and AgentBase
            captured_services = []
            patches_applied = []
            
            def mock_serve(self, *args, **kwargs):
                captured_services.append(self)
                print(f"  (Intercepted serve() call, service captured for testing)")
                return self
            
            def mock_run(self, *args, **kwargs):
                captured_services.append(self)
                print(f"  (Intercepted run() call, service captured for testing)")
                return self
            
            # Apply patches to both base classes
            for base_class in [SWMLService, AgentBase]:
                if base_class:
                    if hasattr(base_class, 'serve'):
                        patches_applied.append((base_class, 'serve', base_class.serve))
                        base_class.serve = mock_serve
                    if hasattr(base_class, 'run'):
                        patches_applied.append((base_class, 'run', base_class.run))
                        base_class.run = mock_run
            
            try:
                result = module.main()
                if isinstance(result, SWMLService):
                    service = result
                elif captured_services:
                    # Use the last captured service (most likely the configured one)
                    service = captured_services[-1]
            finally:
                # Restore original methods
                for base_class, method_name, original_method in patches_applied:
                    setattr(base_class, method_name, original_method)
                
        except Exception as e:
            print(f"Warning: Failed to call main() function: {e}")
    
    if service is None:
        raise ValueError(f"No service found in {service_path}. The file must contain either:\n"
                        f"- A SWMLService instance (e.g., agent = MyAgent() or service = MyService())\n"
                        f"- A SWMLService subclass that can be instantiated\n"
                        f"- A main() function that creates and returns a service")
    
    return service