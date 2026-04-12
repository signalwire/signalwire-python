#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Basic SWML Service Example

This example demonstrates using SWMLService directly to create
and serve SWML documents without AI components. It shows how to
build various SWML flows for telephony applications.

Examples include:
1. Voicemail system
2. Interactive phone menu (IVR)
3. Call transfer system
4. Call recording
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
from signalwire.core.swml_builder import SWMLBuilder

# Create structured logger for this example
logger = structlog.get_logger("basic_swml")


class VoicemailService(SWMLService):
    """
    Simple voicemail service that plays a greeting and records a message
    """
    
    def __init__(self, host="0.0.0.0", port=3000):
        super().__init__(
            name="voicemail",
            route="/voicemail",
            host=host,
            port=port
        )
        
        # Build the SWML document
        self.build_voicemail_document()
    
    def build_voicemail_document(self):
        """Build the voicemail SWML document"""
        # Reset the document
        self.reset_document()
        
        # Add answer verb
        self.add_answer_verb()
        
        # Add play verb for greeting
        self.add_verb("play", {
            "url": "say:Hello, you've reached the voicemail service. Please leave a message after the beep."
        })
        
        # Add a small pause
        self.add_verb("sleep", 1000)  # 1 second in milliseconds
        
        # Play a beep
        self.add_verb("play", {
            "url": "https://example.com/beep.wav"  # Replace with actual beep sound URL
        })
        
        # Record the message
        self.add_verb("record", {
            "format": "mp3",
            "stereo": False,
            "beep": False,  # We already played a beep
            "max_length": 120,  # 2 minutes max
            "terminators": "#",  # Allow # to stop recording
            "status_url": "https://example.com/voicemail-status"  # Replace with your status webhook
        })
        
        # Thank the caller
        self.add_verb("play", {
            "url": "say:Thank you for your message. Goodbye!"
        })
        
        # Hang up
        self.add_hangup_verb()
        
        self.log.debug("voicemail_document_built")


class IvrMenuService(SWMLService):
    """
    Interactive Voice Response (IVR) menu system
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
        """Build the IVR menu SWML document"""
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
        self.add_verb_to_section("sales", "play", {
            "url": "say:Connecting you to sales. Please hold."
        })
        self.add_verb_to_section("sales", "connect", {
            "to": "+15551234567"  # Replace with actual sales number
        })
        
        # Add support section
        self.add_section("support")
        self.log.debug("adding_section", section="support")
        self.add_verb_to_section("support", "play", {
            "url": "say:Connecting you to support. Please hold."
        })
        self.add_verb_to_section("support", "connect", {
            "to": "+15557654321"  # Replace with actual support number
        })
        
        # Add voicemail section
        self.add_section("voicemail")
        self.log.debug("adding_section", section="voicemail")
        self.add_verb_to_section("voicemail", "play", {
            "url": "say:Please leave a message after the beep."
        })
        self.add_verb_to_section("voicemail", "sleep", 1000)  # 1 second pause
        self.add_verb_to_section("voicemail", "record", {
            "format": "mp3",
            "max_length": 120,  # 2 minutes max
            "terminators": "#"
        })
        self.add_verb_to_section("voicemail", "play", {
            "url": "say:Thank you for your message. Goodbye!"
        })
        self.add_verb_to_section("voicemail", "hangup", {})
        
        # Start with the main menu
        self.add_verb("transfer", {
            "dest": "main_menu"
        })
        
        self.log.debug("ivr_document_built")


class CallTransferService(SWMLService):
    """
    Call transfer service with parallel dialing
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
        """Build the call transfer SWML document"""
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
            "from": "+15551234567",  # Replace with your from number
            "timeout": 30,  # 30 seconds timeout
            "answer_on_bridge": True,
            "ringback": ["ring:us"],  # US ringback tone
            "parallel": [
                {"to": "+15552223333"},  # Replace with actual agent numbers
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
            "max_length": 120,  # 2 minutes max
            "terminators": "#"  # Allow # to stop recording
        })
        
        # Thank the caller
        self.add_verb("play", {
            "url": "say:Thank you for your message. We'll get back to you as soon as possible."
        })
        
        # Hang up
        self.add_hangup_verb()
        
        self.log.debug("transfer_document_built")


class CallRecordingService(SWMLService):
    """
    Demonstrates call recording features
    """
    
    def __init__(self, host="0.0.0.0", port=3000):
        super().__init__(
            name="record",
            route="/record",
            host=host,
            port=port
        )
        
        # Build the SWML document
        self.build_recording_document()
    
    def build_recording_document(self):
        """Build the call recording SWML document"""
        # Reset the document
        self.reset_document()
        
        # Add answer verb
        self.add_answer_verb()
        
        # Start recording the call in the background
        self.log.debug("starting_call_recording", format="mp3", stereo=True)
        self.add_verb("record_call", {
            "control_id": "call_recording",
            "format": "mp3",
            "stereo": True,
            "direction": "both",
            "beep": True
        })
        
        # Inform the caller about recording
        self.add_verb("play", {
            "url": "say:This call is being recorded for quality and training purposes."
        })
        
        # Add play verb for prompt
        self.add_verb("play", {
            "url": "say:Please tell us about your experience with our product."
        })
        
        # Add sleep to wait for the caller's response
        self.add_verb("sleep", 30000)  # 30 seconds
        
        # Add play verb for closing
        self.add_verb("play", {
            "url": "say:Thank you for your feedback. Is there anything else you'd like to add?"
        })
        
        # Add sleep to wait for the caller's response
        self.add_verb("sleep", 30000)  # 30 seconds
        
        # Stop recording
        self.log.debug("stopping_call_recording", control_id="call_recording")
        self.add_verb("stop_record_call", {
            "control_id": "call_recording"
        })
        
        # Thank the caller
        self.add_verb("play", {
            "url": "say:Thank you for your time. Goodbye!"
        })
        
        # Hang up
        self.add_hangup_verb()
        
        self.log.debug("recording_document_built")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Basic SWML Service Examples")
    parser.add_argument("--service", choices=["voicemail", "ivr", "transfer", "record"], 
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
    elif args.service == "record":
        service = CallRecordingService(host=args.host, port=args.port)
    
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
        print(f"  - GET http://{args.host}:{args.port}{service.route}/")
        print(f"  - POST http://{args.host}:{args.port}{service.route}/")
        print("\nAll endpoints respond with the same SWML document.")
        
        # Start the server
        try:
            service.run(host=args.host, port=args.port)
        except KeyboardInterrupt:
            logger.info("server_shutdown")
            print("\nShutting down...")


if __name__ == "__main__":
    main() 