#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Validate a JSON file against a JSON Schema.

Usage:
    python validate_schema.py <schema_file> <json_file>
    
Example:
    python validate_schema.py schema.json steps3.json
"""

import json
import sys
import argparse
from pathlib import Path
from jsonschema import validate, ValidationError, Draft7Validator


def load_json_file(filepath):
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File '{filepath}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in '{filepath}': {e}")
        sys.exit(1)


def validate_json(schema_file, json_file, verbose=False):
    """Validate a JSON file against a schema."""
    # Load files
    print(f"Loading schema from: {schema_file}")
    schema = load_json_file(schema_file)
    
    print(f"Loading JSON from: {json_file}")
    data = load_json_file(json_file)
    
    # Try to validate
    try:
        validate(instance=data, schema=schema)
        print("\n✅ Validation PASSED!")
        return True
        
    except ValidationError as e:
        print(f"\n❌ Validation FAILED!")
        print(f"\nError: {e.message}")
        
        # Show the path where the error occurred
        if e.path:
            path_str = " -> ".join(str(p) for p in e.path)
            print(f"Location: {path_str}")
        
        # Show the failing value if verbose
        if verbose and e.instance is not None:
            print(f"\nFailing value: {json.dumps(e.instance, indent=2)[:200]}...")
        
        # Show all errors if there are multiple
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(data))
        
        if len(errors) > 1:
            print(f"\nFound {len(errors)} validation errors:")
            for i, error in enumerate(errors, 1):
                print(f"\n{i}. {error.message}")
                if error.path:
                    path_str = " -> ".join(str(p) for p in error.path)
                    print(f"   Location: {path_str}")
                
                # Show schema constraint that failed
                if verbose and error.validator:
                    print(f"   Failed constraint: {error.validator}")
                    if error.validator_value is not None:
                        print(f"   Expected: {json.dumps(error.validator_value, indent=2)[:100]}...")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Validate a JSON file against a JSON Schema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  python validate_schema.py schema.json data.json
  
  # With verbose output
  python validate_schema.py -v schema.json data.json
  
  # Validate AI config extracted from SWML
  python validate_schema.py --extract-ai schema.json steps3.json
        """
    )
    
    parser.add_argument('schema', help='Path to the JSON Schema file')
    parser.add_argument('json_file', help='Path to the JSON file to validate')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed error information')
    parser.add_argument('--extract-ai', action='store_true',
                        help='Extract and validate just the AI config from SWML format')
    
    args = parser.parse_args()
    
    # Check if files exist
    if not Path(args.schema).exists():
        print(f"❌ Error: Schema file '{args.schema}' not found")
        sys.exit(1)
    
    if not Path(args.json_file).exists():
        print(f"❌ Error: JSON file '{args.json_file}' not found")
        sys.exit(1)
    
    # Special handling for AI config extraction
    if args.extract_ai:
        print("Extracting AI config from SWML format...")
        data = load_json_file(args.json_file)
        schema = load_json_file(args.schema)
        
        # Extract AI config
        ai_config = None
        if 'sections' in data and 'main' in data.get('sections', {}):
            main_section = data.get('sections', {}).get('main', [])
            for item in main_section:
                if isinstance(item, dict) and 'ai' in item:
                    ai_config = item['ai']
                    break
        
        if not ai_config:
            print("❌ Error: No AI config found in SWML format")
            sys.exit(1)
        
        # Extract AI schema
        ai_schema = None
        if '$defs' in schema and 'AI' in schema['$defs']:
            ai_def = schema['$defs']['AI']
            if 'properties' in ai_def and 'ai' in ai_def['properties']:
                ai_schema = ai_def['properties']['ai'].copy()
                # Create a new schema with only necessary definitions
                ai_schema_full = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    **ai_schema,
                    "$defs": schema['$defs']
                }
        
        if not ai_schema:
            print("❌ Error: Could not extract AI schema")
            sys.exit(1)
        
        # Validate directly without writing temp files
        try:
            validate(instance=ai_config, schema=ai_schema_full)
            print("\n✅ AI config validation PASSED!")
            success = True
        except ValidationError as e:
            print(f"\n❌ AI config validation FAILED!")
            print(f"\nFirst error: {e.message}")
            if e.path:
                path_str = " -> ".join(str(p) for p in e.path)
                print(f"Location: {path_str}")
            
            # Show all errors
            validator = Draft7Validator(ai_schema_full)
            errors = list(validator.iter_errors(ai_config))
            
            if len(errors) > 1:
                print(f"\nFound {len(errors)} validation errors in total:")
                for i, error in enumerate(errors, 1):
                    print(f"\n{i}. {error.message}")
                    if error.path:
                        path_str = " -> ".join(str(p) for p in error.path)
                        print(f"   Location: {path_str}")
                    if args.verbose and error.validator:
                        print(f"   Failed constraint: {error.validator}")
            
            success = False
    else:
        # Normal validation
        success = validate_json(args.schema, args.json_file, args.verbose)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()