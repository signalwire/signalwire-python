#!/usr/bin/env python
"""
POM Tool - Command line utility for working with Prompt Object Model files

Usage:
    pom_tool <input_file> [--output=<format>] [--outfile=<file>] [--merge_pom="<section name>:<filename>"]
    pom_tool (-h | --help)

Options:
    -h --help           Show this help message
    --output=<format>   Output format: md, xml, json, yaml [default: md]
    --outfile=<file>    Output file (if not specified, prints to stdout)
    --merge_pom=<arg>   Merge another POM into a section: "<section name>:<filename>"
"""

import os
import sys
import json
import yaml
from docopt import docopt
from signalwire.pom import PromptObjectModel

def detect_file_format(file_path):
    """Detect if the file is JSON or YAML based on extension and content."""
    ext = os.path.splitext(file_path)[1].lower()

    # First try to determine by extension
    if ext in ['.json']:
        return 'json'
    elif ext in ['.yaml', '.yml']:
        return 'yaml'

    # If extension doesn't clearly indicate, try to parse the content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()

    # Simple heuristic: JSON typically starts with { or [
    if content.startswith('{') or content.startswith('['):
        try:
            json.loads(content)
            return 'json'
        except json.JSONDecodeError:
            pass

    # Try YAML parsing as a fallback
    try:
        yaml.safe_load(content)
        return 'yaml'
    except yaml.YAMLError:
        pass

    # If we can't determine, default to JSON
    return 'json'

def load_pom(file_path):
    """Load a POM from a file, auto-detecting the format."""
    format_type = detect_file_format(file_path)

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    if format_type == 'json':
        return PromptObjectModel.from_json(content)
    else:  # yaml
        return PromptObjectModel.from_yaml(content)

def render_pom(pom, output_format):
    """Render the POM in the specified format."""
    if output_format == 'md':
        return pom.render_markdown()
    elif output_format == 'xml':
        return pom.render_xml()
    elif output_format == 'json':
        return pom.to_json()
    elif output_format == 'yaml':
        return pom.to_yaml()
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

def main():
    """Main entry point for the POM tool."""
    args = docopt(__doc__)

    input_file = args['<input_file>']
    output_format = args['--output'] or 'md'
    output_file = args['--outfile']
    merge_pom = args['--merge_pom']

    # Validate output format
    if output_format not in ['md', 'xml', 'json', 'yaml']:
        print(f"Error: Invalid output format '{output_format}'. Must be one of: md, xml, json, yaml")
        sys.exit(1)

    try:
        # Load the POM
        pom = load_pom(input_file)

        # Handle merging another POM
        if merge_pom:
            section_name, filename = merge_pom.split(':', 1)
            pom_to_merge = load_pom(filename)
            pom.add_pom_as_subsection(section_name.strip(), pom_to_merge)

        # Render in the requested format
        output = render_pom(pom, output_format)

        # Output to file or stdout
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(output)
            print(f"Output written to {output_file}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
