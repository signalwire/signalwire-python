#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Webhook function execution (including external)
"""

import json
import requests
from typing import Dict, Any, TYPE_CHECKING
from ..config import HTTP_REQUEST_TIMEOUT

if TYPE_CHECKING:
    from signalwire.core.swaig_function import SWAIGFunction


def execute_external_webhook_function(func: 'SWAIGFunction', function_name: str, function_args: Dict[str, Any], 
                                    post_data: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """
    Execute an external webhook SWAIG function by making an HTTP request to the external service.
    This simulates what SignalWire would do when calling an external webhook function.
    
    Args:
        func: The SWAIGFunction object with webhook_url
        function_name: Name of the function being called
        function_args: Parsed function arguments
        post_data: Complete post data to send to the webhook
        verbose: Whether to show verbose output
        
    Returns:
        Response from the external webhook service
    """
    webhook_url = func.webhook_url
    
    if verbose:
        print(f"\nCalling EXTERNAL webhook: {function_name}")
        print(f"URL: {webhook_url}")
        print(f"Arguments: {json.dumps(function_args, indent=2)}")
        print("-" * 60)
    
    # Prepare the SWAIG function call payload that SignalWire would send
    swaig_payload = {
        "function": function_name,
        "argument": {
            "parsed": [function_args] if function_args else [{}],
            "raw": json.dumps(function_args) if function_args else "{}"
        }
    }
    
    # Add call_id and other data from post_data if available
    if "call_id" in post_data:
        swaig_payload["call_id"] = post_data["call_id"]
    
    # Add any other relevant fields from post_data
    for key in ["call", "device", "vars"]:
        if key in post_data:
            swaig_payload[key] = post_data[key]
    
    if verbose:
        print(f"Sending payload: {json.dumps(swaig_payload, indent=2)}")
        print(f"Making POST request to: {webhook_url}")
    
    try:
        # Make the HTTP request to the external webhook
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SignalWire-SWAIG-Test/1.0"
        }
        
        response = requests.post(
            webhook_url,
            json=swaig_payload,
            headers=headers,
            timeout=HTTP_REQUEST_TIMEOUT
        )
        
        if verbose:
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if verbose:
                    print(f"✓ External webhook succeeded")
                    print(f"Response: {json.dumps(result, indent=2)}")
                return result
            except json.JSONDecodeError:
                # If response is not JSON, wrap it in a response field
                result = {"response": response.text}
                if verbose:
                    print(f"✓ External webhook succeeded (text response)")
                    print(f"Response: {response.text}")
                return result
        else:
            error_msg = f"External webhook returned HTTP {response.status_code}"
            if verbose:
                print(f"✗ External webhook failed: {error_msg}")
                try:
                    error_detail = response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"Error response: {response.text}")
            
            return {
                "error": error_msg,
                "status_code": response.status_code,
                "response": response.text
            }
    
    except requests.Timeout:
        error_msg = f"External webhook timed out after {HTTP_REQUEST_TIMEOUT} seconds"
        if verbose:
            print(f"✗ {error_msg}")
        return {"error": error_msg}
    
    except requests.ConnectionError as e:
        error_msg = f"Could not connect to external webhook: {e}"
        if verbose:
            print(f"✗ {error_msg}")
        return {"error": error_msg}
    
    except requests.RequestException as e:
        error_msg = f"Request to external webhook failed: {e}"
        if verbose:
            print(f"✗ {error_msg}")
        return {"error": error_msg}