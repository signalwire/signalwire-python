#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

# -*- coding: utf-8 -*-
"""
Enhanced InfoGatherer example demonstrating dynamic configuration via callback

This example shows how to use the InfoGathererAgent with a callback function
to dynamically configure questions based on request parameters.

Test URLs:
- /contact (default questions)
- /contact?set=support (customer support questions)
- /contact?set=medical (medical intake questions)
- /contact?set=onboarding (employee onboarding questions)
"""

import os
import sys
import json
import argparse
from signalwire.prefabs import InfoGathererAgent

# Question sets for different scenarios
QUESTION_SETS = {
    "default": [
        {"key_name": "name", "question_text": "What is your full name?"},
        {"key_name": "phone", "question_text": "What is your phone number?", "confirm": True},
        {"key_name": "reason", "question_text": "How can I help you today?"}
    ],
    "support": [
        {"key_name": "customer_name", "question_text": "What is your name?"},
        {"key_name": "account_number", "question_text": "What is your account number?", "confirm": True},
        {"key_name": "issue", "question_text": "What issue are you experiencing?"},
        {"key_name": "priority", "question_text": "How urgent is this issue? (Low, Medium, High)"}
    ],
    "medical": [
        {"key_name": "patient_name", "question_text": "What is the patient's full name?"},
        {"key_name": "symptoms", "question_text": "What symptoms are you experiencing?", "confirm": True},
        {"key_name": "duration", "question_text": "How long have you had these symptoms?"},
        {"key_name": "medications", "question_text": "Are you currently taking any medications?"}
    ],
    "onboarding": [
        {"key_name": "full_name", "question_text": "What is your full name?"},
        {"key_name": "email", "question_text": "What is your email address?", "confirm": True},
        {"key_name": "company", "question_text": "What company do you work for?"},
        {"key_name": "department", "question_text": "What department will you be working in?"},
        {"key_name": "start_date", "question_text": "What is your start date?"}
    ]
}

def get_questions_callback(query_params, body_params, headers):
    """
    Callback function to determine which questions to ask based on request parameters
    
    Args:
        query_params: Dict of query string parameters
        body_params: Dict of POST body parameters  
        headers: Dict of HTTP headers
        
    Returns:
        List of question dictionaries
    """
    # Get the question set from query parameters
    question_set = query_params.get('set', 'default')
    
    # Log the request for debugging
    print(f"Dynamic configuration requested: set={question_set}")
    print(f"Query params: {query_params}")
    
    # Return the appropriate question set
    questions = QUESTION_SETS.get(question_set, QUESTION_SETS["default"])
    
    print(f"Using {len(questions)} questions for set '{question_set}'")
    return questions

def create_dynamic_agent():
    """Create an InfoGatherer with dynamic questions using callback"""
    
    # Create agent in dynamic mode (no static questions)
    agent = InfoGathererAgent(
        questions=None,  # Dynamic mode
        name="contact-form", 
        route="/contact"
    )
    
    # Set the callback function for dynamic configuration
    agent.set_question_callback(get_questions_callback)
    
    return agent

def main():
    """Run the dynamic InfoGathererAgent example"""
    
    print("Starting Dynamic InfoGatherer Agent...")
    print("This agent configures questions based on request parameters")
    print()
    print("Test with these URLs:")
    print("  /contact (default questions)")
    print("  /contact?set=support (customer support)")  
    print("  /contact?set=medical (medical intake)")
    print("  /contact?set=onboarding (employee onboarding)")
    print()
    
    # Create the dynamic agent
    agent = create_dynamic_agent()
    
    print("\nStarting agent server...")
    print("Note: Works in any deployment mode (server/CGI/Lambda)")
    agent.run()

if __name__ == "__main__":
    main() 