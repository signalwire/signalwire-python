#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Wrapper script for swaig-test that sets environment variables before importing any modules.
This allows proper control of logging before the logging system is initialized.
"""

import os
import sys
import subprocess


def main():
    """Main entry point for the swaig-test command"""
    # Determine if we should show logs based on arguments
    args = sys.argv[1:]
    
    # Check for verbose flag
    show_logs = '--verbose' in args or '-v' in args
    
    # Special cases that always suppress logs
    force_suppress = '--dump-swml' in args or '--raw' in args
    
    # Set logging mode
    if force_suppress:
        os.environ['SIGNALWIRE_LOG_MODE'] = 'off'
    elif show_logs:
        os.environ['SIGNALWIRE_LOG_MODE'] = 'default'
    else:
        # Default: suppress logs unless verbose is requested
        os.environ['SIGNALWIRE_LOG_MODE'] = 'off'
    
    # Execute the actual implementation
    # Use sys.executable to ensure we use the same Python interpreter
    # Add -W ignore::RuntimeWarning to suppress the sys.modules warning
    cmd = [sys.executable, '-W', 'ignore::RuntimeWarning', '-m', 'signalwire.cli.test_swaig'] + args
    
    # Run the command and exit with its exit code
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()