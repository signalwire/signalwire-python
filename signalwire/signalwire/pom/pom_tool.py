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

import argparse
import sys
import json
from pathlib import Path
import yaml
from signalwire.pom import PromptObjectModel


def detect_file_format(file_path: str) -> str:
    """Detect if the file is JSON or YAML based on extension and content."""
    ext = Path(file_path).suffix.lower()

    # First try to determine by extension
    if ext in [".json"]:
        return "json"
    if ext in [".yaml", ".yml"]:
        return "yaml"

    # If extension doesn't clearly indicate, try to parse the content
    with Path(file_path).open("r", encoding="utf-8") as file:
        content = file.read().strip()

    # Simple heuristic: JSON typically starts with { or [
    if content.startswith("{") or content.startswith("["):
        try:
            json.loads(content)
            return "json"
        except json.JSONDecodeError:
            pass

    # Try YAML parsing as a fallback
    try:
        yaml.safe_load(content)
        return "yaml"
    except yaml.YAMLError:
        pass

    # If we can't determine, default to JSON
    return "json"


def load_pom(file_path: str) -> "PromptObjectModel":
    """Load a POM from a file, auto-detecting the format."""
    format_type = detect_file_format(file_path)

    with Path(file_path).open("r", encoding="utf-8") as file:
        content = file.read()

    if format_type == "json":
        return PromptObjectModel.from_json(content)
    # yaml
    return PromptObjectModel.from_yaml(content)


def render_pom(pom: "PromptObjectModel", output_format: str) -> str:
    """Render the POM in the specified format."""
    if output_format == "md":
        return pom.render_markdown()
    if output_format == "xml":
        return pom.render_xml()
    if output_format == "json":
        return pom.to_json()
    if output_format == "yaml":
        return pom.to_yaml()
    raise ValueError(f"Unsupported output format: {output_format}")


def main() -> None:
    """Main entry point for the POM tool."""
    # §6.2-python: argparse (stdlib) replaced the unmaintained docopt — identical CLI
    # surface (same flags/defaults/usage), one fewer dependency.
    parser = argparse.ArgumentParser(
        prog="pom_tool",
        description="POM Tool - work with Prompt Object Model files",
    )
    parser.add_argument("input_file", help="POM file to load (JSON or YAML)")
    parser.add_argument(
        "--output",
        default="md",
        metavar="<format>",
        choices=["md", "xml", "json", "yaml"],
        help="Output format: md, xml, json, yaml [default: md]",
    )
    parser.add_argument(
        "--outfile",
        default=None,
        metavar="<file>",
        help="Output file (if not specified, prints to stdout)",
    )
    parser.add_argument(
        "--merge_pom",
        default=None,
        metavar="<arg>",
        help='Merge another POM into a section: "<section name>:<filename>"',
    )
    ns = parser.parse_args()

    input_file = ns.input_file
    output_format = ns.output
    output_file = ns.outfile
    merge_pom = ns.merge_pom

    try:
        # Load the POM
        pom = load_pom(input_file)

        # Handle merging another POM
        if merge_pom:
            section_name, filename = merge_pom.split(":", 1)
            pom_to_merge = load_pom(filename)
            pom.add_pom_as_subsection(section_name.strip(), pom_to_merge)

        # Render in the requested format
        output = render_pom(pom, output_format)

        # Output to file or stdout
        if output_file:
            with Path(output_file).open("w", encoding="utf-8") as file:
                file.write(output)
            print(f"Output written to {output_file}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    main()
