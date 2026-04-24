#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Auto-Vivified SWML Service Example

This example demonstrates using the auto-vivification feature of SWMLService
to directly call verb methods instead of using add_verb. This provides a cleaner
and more intuitive API for building SWML documents.

Example: service.play(url="say:Hello") instead of service.add_verb("play", {"url": "say:Hello"})
"""

import os
import sys
import json
import argparse
import logging
import types

# Import structlog for logger instance creation
import structlog

# Import the SWMLService class
from signalwire.core.swml_service import SWMLService

# Create structured logger for this example
logger = structlog.get_logger("auto_vivified")


class VoicemailService(SWMLService):
    """
    Simple voicemail service using auto-vivified verb methods
    """
    
    def __init__(self, host="0.0.0.0", port=3000):
        super().__init__(
            name="voicemail",
            route="/voicemail",
            host=host,
            port=port
        )
        
        # Debug: Print available verbs and schema details
        verb_names = self.schema_utils.get_all_verb_names()
        print(f"Available verbs: {verb_names}")
        print(f"Schema path: {self.schema_utils.schema_path}")
        print(f"Schema loaded: {bool(self.schema_utils.schema)}")
        print(f"Number of verbs extracted: {len(self.schema_utils.verbs)}")
        
        # Explicit testing of auto-vivification
        print("\n--- Testing Auto-Vivification Mechanism ---")
        
        # Try normal attribute access to see if __getattr__ gets triggered
        try:
            print("\nAttempting normal attribute access for 'play'...")
            print(f"Before getattr - 'play' in dir(self): {'play' in dir(self)}")
            play_method = getattr(self, "play", None)
            print(f"getattr result: {play_method}")
            print(f"After getattr - 'play' in dir(self): {'play' in dir(self)}")
            print(f"hasattr(self, 'play'): {hasattr(self, 'play')}")
        except Exception as e:
            print(f"Error in getattr: {type(e)}: {e}")
            
        # Examine the __dict__ to see if methods are being added
        print("\nExamining instance __dict__:")
        print(f"'play' in self.__dict__: {'play' in self.__dict__}")
        print(f"'_verb_methods_cache' in self.__dict__: {'_verb_methods_cache' in self.__dict__}")
        if hasattr(self, '_verb_methods_cache'):
            print(f"Cache contents: {list(self._verb_methods_cache.keys())}")
        
        print("--- End of Auto-Vivification Testing ---\n")
        
        # Build the SWML document
        self.build_voicemail_document()
    
    def build_voicemail_document(self):
        """Build the voicemail SWML document using auto-vivified methods"""
        # Reset the document
        self.reset_document()
        
        # Add answer verb - temporarily using add_verb
        self.add_answer_verb()
        
        # Add play verb for greeting - try using auto-vivified method
        try:
            print("Attempting to use auto-vivified play() method...")
            self.play(url="say:Hello, you've reached the voicemail service. Please leave a message after the beep.")
            print("Successfully used auto-vivified play() method")
        except Exception as e:
            print(f"Error using auto-vivified method: {type(e)}: {e}")
            # Fallback to add_verb
            self.add_verb("play", {
                "url": "say:Hello, you've reached the voicemail service. Please leave a message after the beep."
            })
            print("Fell back to add_verb")
        
        # Add a small pause - try using auto-vivified method
        try:
            print("Attempting to use auto-vivified sleep() method...")
            self.sleep(1000)  # 1 second in milliseconds
            print("Successfully used auto-vivified sleep() method")
        except Exception as e:
            print(f"Error using auto-vivified method: {type(e)}: {e}")
            # Fallback to add_verb
            self.add_verb("sleep", 1000)
            print("Fell back to add_verb")
        
        # Play a beep - try using auto-vivified method
        try:
            print("Attempting to use auto-vivified play() method for beep...")
            self.play(url="https://example.com/beep.wav")
            print("Successfully used auto-vivified play() method")
        except Exception as e:
            print(f"Error using auto-vivified method: {type(e)}: {e}")
            # Fallback to add_verb
            self.add_verb("play", {
                "url": "https://example.com/beep.wav"
            })
            print("Fell back to add_verb")
        
        # Record the message - try using auto-vivified method
        try:
            print("Attempting to use auto-vivified record() method...")
            self.record(
                format="mp3",
                stereo=False,
                beep=False,  # We already played a beep
                max_length=120,  # 2 minutes max
                terminators="#",  # Allow # to stop recording
                status_url="https://example.com/voicemail-status"
            )
            print("Successfully used auto-vivified record() method")
        except Exception as e:
            print(f"Error using auto-vivified method: {type(e)}: {e}")
            # Fallback to add_verb
            self.add_verb("record", {
                "format": "mp3",
                "stereo": False,
                "beep": False,
                "max_length": 120,
                "terminators": "#",
                "status_url": "https://example.com/voicemail-status"
            })
            print("Fell back to add_verb")
        
        # Thank the caller - try using auto-vivified method
        try:
            print("Attempting to use auto-vivified play() method for thank you...")
            self.play(url="say:Thank you for your message. Goodbye!")
            print("Successfully used auto-vivified play() method")
        except Exception as e:
            print(f"Error using auto-vivified method: {type(e)}: {e}")
            # Fallback to add_verb
            self.add_verb("play", {
                "url": "say:Thank you for your message. Goodbye!"
            })
            print("Fell back to add_verb")

        # Hang up - use the add_verb method
        self.add_verb("hangup", {})

        self.log.debug("voicemail_document_built")


class IvrMenuService(SWMLService):
    """
    Interactive Voice Response (IVR) menu system using auto-vivified verb methods
    """
    
    def __init__(self, host="0.0.0.0", port=3000):
        super().__init__(
            name="ivr",
            route="/ivr",
            host=host,
            port=port
        )
        
        # Build the SWML document
        self.build_ivr_document()
    
    def build_ivr_document(self):
        """Build the IVR menu SWML document using auto-vivified methods"""
        # Reset the document
        self.reset_document()
        
        # Add answer verb
        self.add_answer_verb()
        
        # Add main menu section
        self.add_section("main_menu")
        self.log.debug("adding_section", section="main_menu")
        
        # Add prompt verb for the main menu
        self.add_verb_to_section("main_menu", "prompt", {
            "play": "say:Welcome to our service. Press 1 for sales, 2 for support, or 3 to leave a message.",
            "max_digits": 1,
            "terminators": "#",
            "digit_timeout": 5.0,
            "initial_timeout": 10.0
        })
        
        # Add switch verb to handle menu options
        self.add_verb_to_section("main_menu", "switch", {
            "variable": "prompt_digits",
            "case": {
                "1": [
                    {"transfer": {"dest": "sales"}}
                ],
                "2": [
                    {"transfer": {"dest": "support"}}
                ],
                "3": [
                    {"transfer": {"dest": "voicemail"}}
                ]
            },
            "default": [
                {"play": {"url": "say:I'm sorry, I didn't understand your selection."}},
                {"transfer": {"dest": "main_menu"}}
            ]
        })
        
        # Add sales section
        self.add_section("sales")
        self.log.debug("adding_section", section="sales")
        
        # Add play and connect verbs to sales section
        self.add_verb_to_section("sales", "play", {"url": "say:Connecting you to sales. Please hold."})
        self.add_verb_to_section("sales", "connect", {"to": "+15551234567"})
        
        # Add support section
        self.add_section("support")
        self.log.debug("adding_section", section="support")
        
        # Add play and connect verbs to support section
        self.add_verb_to_section("support", "play", {"url": "say:Connecting you to support. Please hold."})
        self.add_verb_to_section("support", "connect", {"to": "+15557654321"})
        
        # Add voicemail section
        self.add_section("voicemail")
        self.log.debug("adding_section", section="voicemail")
        
        # Add verbs to voicemail section
        self.add_verb_to_section("voicemail", "play", {"url": "say:Please leave a message after the beep."})
        self.add_verb_to_section("voicemail", "sleep", 1000)  # 1 second pause
        self.add_verb_to_section("voicemail", "record", {
            "format": "mp3",
            "max_length": 120,
            "terminators": "#"
        })
        self.add_verb_to_section("voicemail", "play", {"url": "say:Thank you for your message. Goodbye!"})
        self.add_verb_to_section("voicemail", "hangup", {})
        
        # Start with the main menu
        self.add_verb("transfer", {
            "dest": "main_menu"
        })
        
        self.log.debug("ivr_document_built")


class CallTransferService(SWMLService):
    """
    Call transfer service with parallel dialing using auto-vivified verb methods
    """
    
    def __init__(self, host="0.0.0.0", port=3000):
        super().__init__(
            name="transfer",
            route="/transfer",
            host=host,
            port=port
        )
        
        # Build the SWML document
        self.build_transfer_document()
    
    def build_transfer_document(self):
        """Build the call transfer SWML document using auto-vivified methods"""
        # Reset the document
        self.reset_document()
        
        # Add answer verb
        self.add_answer_verb()
        
        # Add play verb for greeting
        self.add_verb("play", {
            "url": "say:Thank you for calling. We'll connect you with the next available agent."
        })
        
        # Add connect verb with parallel dialing
        self.log.debug("setting_up_parallel_dialing", agents=3)
        self.add_verb("connect", {
            "from": "+15551234567",  # Using "from" directly in the config
            "timeout": 30,
            "answer_on_bridge": True,
            "ringback": ["ring:us"],
            "parallel": [
                {"to": "+15552223333"},
                {"to": "+15554445555"},
                {"to": "+15556667777"}
            ]
        })
        
        # Add fallback if no one answers
        self.add_verb("play", {
            "url": "say:We're sorry, but all of our agents are currently busy. Please leave a message."
        })
        
        # Record a message if no agents available
        self.add_verb("record", {
            "format": "mp3",
            "stereo": False,
            "beep": True,
            "max_length": 120,
            "terminators": "#"
        })
        
        # Thank the caller
        self.add_verb("play", {
            "url": "say:Thank you for your message. We'll get back to you as soon as possible."
        })

        # Hang up
        self.add_verb("hangup", {})

        self.log.debug("transfer_document_built")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Auto-Vivified SWML Service Examples")
    parser.add_argument("--service", choices=["voicemail", "ivr", "transfer"], 
                        default="voicemail", help="Which service to run")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=3000, help="Port to bind to")
    parser.add_argument("--show-swml", action="store_true", help="Show SWML document only, don't start server")
    parser.add_argument("--suppress-logs", action="store_true", help="Suppress structured logs")
    
    args = parser.parse_args()
    
    # Set log level based on suppress-logs flag
    if args.suppress_logs:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Create the selected service
    if args.service == "voicemail":
        service = VoicemailService(host=args.host, port=args.port)
    elif args.service == "ivr":
        service = IvrMenuService(host=args.host, port=args.port)
    elif args.service == "transfer":
        service = CallTransferService(host=args.host, port=args.port)
    
    # Either show the SWML or start the server
    if args.show_swml:
        swml_doc = service.render_document()
        logger.info("displaying_swml_document", service=args.service, size=len(swml_doc))
        print(json.dumps(json.loads(swml_doc), indent=2))
    else:
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
        
        # Start the server
        try:
            service.run(host=args.host, port=args.port)
        except KeyboardInterrupt:
            logger.info("server_shutdown")
            print("\nShutting down...")


if __name__ == "__main__":
    main() 