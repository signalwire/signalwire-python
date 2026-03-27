#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Configuration constants for the CLI tools
"""

# Default values for call configuration
DEFAULT_CALL_TYPE = "webrtc"
DEFAULT_CALL_DIRECTION = "inbound"
DEFAULT_CALL_STATE = "created"
DEFAULT_HTTP_METHOD = "POST"
DEFAULT_TOKEN_EXPIRY = 3600

# Default fake data values
DEFAULT_PROJECT_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
DEFAULT_SPACE_ID = "zzzzzzzz-yyyy-xxxx-wwww-vvvvvvvvvvvv"
DEFAULT_SPACE_NAME = "example-space"
DEFAULT_ENVIRONMENT = "production"

# Request timeouts
HTTP_REQUEST_TIMEOUT = 30

# Output formatting
RESULT_LINE_SEP = "-" * 60

# Platform-specific constants
SERVERLESS_PLATFORMS = ["lambda", "cgi", "cloud_function", "azure_function"]

# AWS Lambda defaults
AWS_DEFAULT_REGION = "us-east-1"
AWS_DEFAULT_STAGE = "prod"

# Google Cloud defaults
GCP_DEFAULT_REGION = "us-central1"

# Error messages
ERROR_MISSING_AGENT = "Error: Missing required argument."
ERROR_MULTIPLE_AGENTS = "Multiple agents found in file. Please specify --agent-class"
ERROR_NO_AGENTS = "No agents found in file: {file_path}"
ERROR_AGENT_NOT_FOUND = "Agent class '{class_name}' not found in file: {file_path}"
ERROR_FUNCTION_NOT_FOUND = "Function '{function_name}' not found in agent"
ERROR_CGI_HOST_REQUIRED = "CGI simulation requires --cgi-host"

# Help messages
HELP_DESCRIPTION = """Test SWAIG functions and generate SWML documents for SignalWire AI agents

IMPORTANT: When using --exec, ALL options (like --call-id, --verbose, etc.) must come BEFORE --exec.
Everything after --exec <function_name> is treated as arguments to the function."""

HELP_EPILOG_SHORT = """
examples:
  # Execute a function
  %(prog)s agent.py --exec search --query "test" --limit 5
  
  # Execute with persistent session (--call-id MUST come BEFORE --exec)
  %(prog)s agent.py --call-id my-session --exec add_todo --text "Buy milk"
  
  # WRONG: This won't work! --call-id is treated as a function argument
  %(prog)s agent.py --exec add_todo --text "Buy milk" --call-id my-session
  
  # Generate SWML
  %(prog)s agent.py --dump-swml --raw | jq '.'
  
  # Test with specific agent
  %(prog)s multi_agent.py --agent-class MattiAgent --list-tools
  
  # Simulate serverless
  %(prog)s agent.py --simulate-serverless lambda --exec my_function

For platform-specific options: %(prog)s --help-platforms
For more examples: %(prog)s --help-examples
"""