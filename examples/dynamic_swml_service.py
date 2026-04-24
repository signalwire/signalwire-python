#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Dynamic SWML Service Example

This example demonstrates creating a SWML service that generates
different responses based on POST data. It shows how to use the
on_request() method to customize SWML documents dynamically.
"""

import os
import sys
import json
import argparse
import logging

# Import structlog for logger instance creation
import structlog

# Import the SWMLService class - this will set up the logging configuration
from signalwire.core.swml_service import SWMLService

# Create structured logger for this example
logger = structlog.get_logger("dynamic_swml")


class DynamicGreetingService(SWMLService):
    """
    A service that customizes its greeting based on POST data
    """
    
    def __init__(self, host="0.0.0.0", port=3000):
        super().__init__(
            name="dynamic-greeting",
            route="/greeting",
            host=host,
            port=port
        )
        
        # Build the default SWML document
        self.build_default_document()
    
    def build_default_document(self):
        """Build the default SWML document with a generic greeting"""
        # Reset the document
        self.reset_document()
        
        # Add answer verb
        self.add_answer_verb()
        
        # Add play verb for generic greeting
        self.add_verb("play", {
            "url": "say:Hello, thank you for calling our service."
        })
        
        # Add a generic menu prompt
        self.add_verb("prompt", {
            "play": "say:Please press 1 for sales, 2 for support, or 3 to leave a message.",
            "max_digits": 1,
            "terminators": "#"
        })

        # Add hang up
        self.add_verb("hangup", {})

        self.log.debug("default_document_built")

    def on_request(self, request_data: dict = None) -> dict:
        """
        Customize the SWML document based on the request data
        
        Args:
            request_data: Dictionary containing the parsed POST body
            
        Returns:
            Modified SWML document or None to use the default
        """
        # If there's no request data, use the default document
        if not request_data:
            self.log.debug("no_request_data_using_default")
            return None
        
        self.log.debug("customizing_document", 
                      caller_name=request_data.get("caller_name"),
                      caller_type=request_data.get("caller_type"),
                      department=request_data.get("department"))
        
        # Reset the document to start fresh
        self.reset_document()
        
        # Add answer verb
        self.add_answer_verb()
        
        # Customize greeting based on caller_name if provided
        caller_name = request_data.get("caller_name")
        if caller_name:
            self.add_verb("play", {
                "url": f"say:Hello {caller_name}, welcome back to our service!"
            })
        else:
            self.add_verb("play", {
                "url": "say:Hello, thank you for calling our service."
            })
        
        # Customize menu based on caller_type
        caller_type = request_data.get("caller_type", "").lower()
        
        if caller_type == "vip":
            # VIP callers get priority routing
            self.add_verb("play", {
                "url": "say:As a VIP customer, you'll be connected to our priority support team immediately."
            })
            
            # Connect to VIP support
            self.add_verb("connect", {
                "to": "+15551234567",  # VIP support number
                "timeout": 30,
                "answer_on_bridge": True
            })
            
        elif caller_type == "existing":
            # Existing customers get customized options
            self.add_verb("prompt", {
                "play": "say:Please press 1 for account management, 2 for technical support, or 3 for billing.",
                "max_digits": 1,
                "terminators": "#"
            })
            
        elif caller_type == "new":
            # New customers get sales-focused options
            self.add_verb("prompt", {
                "play": "say:Please press 1 to learn about our products, 2 to speak with a sales representative, or 3 to request a demo.",
                "max_digits": 1,
                "terminators": "#"
            })
            
        else:
            # Generic options for unknown caller types
            self.add_verb("prompt", {
                "play": "say:Please press 1 for sales, 2 for support, or 3 to leave a message.",
                "max_digits": 1,
                "terminators": "#"
            })
        
        # Add dynamic routing based on department if specified
        department = request_data.get("department", "").lower()
        if department:
            self.add_verb("play", {
                "url": f"say:We'll connect you to our {department} department right away."
            })
            
            # Different phone numbers for different departments
            phone_numbers = {
                "sales": "+15551112222",
                "support": "+15553334444",
                "billing": "+15555556666",
                "technical": "+15557778888"
            }
            
            # Connect to the appropriate department
            to_number = phone_numbers.get(department, "+15559990000")  # Default number as fallback
            self.add_verb("connect", {
                "to": to_number,
                "timeout": 30,
                "answer_on_bridge": True
            })

        # Add hang up as fallback
        self.add_verb("hangup", {})
        
        self.log.info("document_customized", 
                     caller_type=caller_type,
                     department=department,
                     has_name=caller_name is not None)
        
        # Return None to use the document we just built
        return None  # The document has already been modified


class CallRouterService(SWMLService):
    """
    A service that routes calls based on POST data
    """
    
    def __init__(self, host="0.0.0.0", port=3000):
        super().__init__(
            name="call-router",
            route="/router",
            host=host,
            port=port
        )
        
        # Build the default SWML document
        self.build_default_document()
    
    def build_default_document(self):
        """Build the default SWML document with a fallback routing"""
        # Reset the document
        self.reset_document()
        
        # Add answer verb
        self.add_answer_verb()
        
        # Add play verb for greeting
        self.add_verb("play", {
            "url": "say:Thank you for calling. We'll connect you with an available agent."
        })
        
        # Add a fallback connection
        self.add_verb("connect", {
            "to": "+15551234567",  # Fallback number
            "timeout": 30
        })

        # Add hang up
        self.add_verb("hangup", {})

        self.log.debug("default_document_built")
    
    def on_request(self, request_data: dict = None) -> dict:
        """
        Route calls differently based on POST data
        
        Args:
            request_data: Dictionary containing the parsed POST body
            
        Returns:
            Modified SWML document or None to use the default
        """
        # If there's no request data, use the default document
        if not request_data:
            self.log.debug("no_request_data_using_default")
            return None
        
        self.log.debug("customizing_routing", 
                      region=request_data.get("region"),
                      high_volume=request_data.get("high_volume"),
                      queue_length=request_data.get("queue_length"),
                      callback_number=request_data.get("callback_number"))
        
        # Create a new document
        self.reset_document()
        self.add_answer_verb()
        
        # Check if this is a high-volume period
        high_volume = request_data.get("high_volume", False)
        
        # Get the caller's region
        region = request_data.get("region", "").lower()
        
        # Get agent queue status
        queue_length = request_data.get("queue_length", 0)
        
        # Check if this is a callback request
        callback_number = request_data.get("callback_number")
        
        # Handle callback requests
        if callback_number:
            self.log.info("processing_callback_request", callback_number=callback_number)
            self.add_verb("play", {
                "url": "say:We'll call you back at the number you provided. Thank you for your patience."
            })
            self.add_verb("hangup", {})
            return None
        
        # Inform caller if we're experiencing high volume
        if high_volume or queue_length > 10:
            self.log.info("high_volume_detected", queue_length=queue_length)
            self.add_verb("play", {
                "url": "say:We're currently experiencing higher than normal call volume. Your wait time may be extended."
            })
            
            # Offer callback option
            self.add_verb("prompt", {
                "play": "say:Press 1 to continue holding, or press 2 to receive a callback when an agent becomes available.",
                "max_digits": 1
            })
            
            # Add conditional logic with switch
            self.add_verb("switch", {
                "variable": "prompt_digits",
                "case": {
                    "2": [
                        {"play": {"url": "say:Please enter your 10-digit phone number followed by the pound key."}},
                        {"prompt": {"play": "silence:1", "max_digits": 10, "terminators": "#"}}
                        # In a real implementation, we'd have more logic here to handle the callback
                    ]
                },
                "default": [
                    {"play": {"url": "say:Thank you for your patience. Please hold for the next available agent."}}
                ]
            })
        else:
            self.add_verb("play", {
                "url": "say:Thank you for calling. We'll connect you with an agent shortly."
            })
        
        # Route based on region if provided
        if region:
            self.log.info("routing_by_region", region=region)
            region_numbers = {
                "east": ["+15551112222", "+15551113333"],
                "west": ["+15552223333", "+15552224444"],
                "central": ["+15553334444", "+15553335555"],
                "international": ["+15554445555"]
            }
            
            numbers = region_numbers.get(region, ["+15551234567"])  # Default to fallback
            
            # If we have multiple numbers for the region, try them in parallel
            if len(numbers) > 1:
                self.log.debug("using_parallel_connection", numbers=numbers)
                parallel_targets = [{"to": num} for num in numbers]
                self.add_verb("connect", {
                    "parallel": parallel_targets,
                    "timeout": 30,
                    "answer_on_bridge": True
                })
            else:
                # Just one number, connect directly
                self.log.debug("using_direct_connection", number=numbers[0])
                self.add_verb("connect", {
                    "to": numbers[0],
                    "timeout": 30,
                    "answer_on_bridge": True
                })
        else:
            # No region specified, use default routing
            self.log.info("using_default_routing")
            self.add_verb("connect", {
                "to": "+15551234567",  # Default number
                "timeout": 30
            })
        
        # Add fallback message and hangup
        self.add_verb("play", {
            "url": "say:We're sorry, but all of our agents are currently busy. Please try your call again later."
        })
        self.add_verb("hangup", {})
        
        return None  # The document has already been modified


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Dynamic SWML Service Examples")
    parser.add_argument("--service", choices=["greeting", "router"], 
                        default="greeting", help="Which service to run")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=3000, help="Port to bind to")
    parser.add_argument("--suppress-logs", action="store_true", help="Suppress structured logs")
    
    args = parser.parse_args()
    
    # Set log level based on suppress-logs flag
    if args.suppress_logs:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Create the selected service
    if args.service == "greeting":
        service = DynamicGreetingService(host=args.host, port=args.port)
    elif args.service == "router":
        service = CallRouterService(host=args.host, port=args.port)
    
    # Get auth credentials
    username, password = service.get_basic_auth_credentials()
    
    logger.info("starting_service", 
               service=args.service, 
               url=f"http://{args.host}:{args.port}{service.route}",
               username=username,
               password_length=len(password))
    
    print(f"Starting {args.service} service on http://{args.host}:{args.port}{service.route}")
    print(f"Basic Auth: {username}:{password}")
    print("\nYou can access this service via:")
    print(f"  - GET http://{args.host}:{args.port}{service.route}")
    print(f"  - POST http://{args.host}:{args.port}{service.route}")
    
    print("\nFor dynamic behavior, send POST requests with JSON data like:")
    
    if args.service == "greeting":
        print(json.dumps({
            "caller_name": "John Doe",
            "caller_type": "vip",
            "department": "technical"
        }, indent=2))
    elif args.service == "router":
        print(json.dumps({
            "region": "west",
            "high_volume": True,
            "queue_length": 15
        }, indent=2))
    
    # Start the server
    try:
        service.run(host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("server_shutdown")
        print("\nShutting down...")


if __name__ == "__main__":
    main() 