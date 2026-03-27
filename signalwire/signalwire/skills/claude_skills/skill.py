"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import os
import re
import subprocess
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Optional

import yaml

from signalwire.core.skill_base import SkillBase
from signalwire.core.function_result import FunctionResult
from signalwire.core.logging_config import get_logger

logger = get_logger(__name__)

# Frontmatter fields that are parsed but not supported in SignalWire agents
_UNSUPPORTED_FIELDS = {
    "context": "context: fork is not supported in SignalWire agents — skill '{name}' will run inline, not in a subagent",
    "agent": "agent field is not supported in SignalWire agents — skill '{name}' cannot select a subagent type",
    "allowed-tools": "allowed-tools is not supported in SignalWire agents — skill '{name}' tool restrictions will not be enforced",
    "model": "model field is not supported in SignalWire agents — skill '{name}' model selection is controlled at the agent level",
    "hooks": "hooks field is not supported in SignalWire agents — skill '{name}' lifecycle hooks will not fire",
}

# Regex for shell injection patterns: !`command`
_SHELL_INJECTION_RE = re.compile(r"!\`([^`]+)\`")


class ClaudeSkillsSkill(SkillBase):
    """
    Load Claude-style SKILL.md files as SignalWire agent tools.

    This skill parses Claude Code skill directories and makes them available
    as SWAIG tools that the AI can call. Each Claude skill becomes a tool
    that returns the skill's instructions when invoked.

    Claude skills use this format:
        ---
        name: skill-name
        description: When to use this skill
        ---

        Markdown instructions here...
        Use $ARGUMENTS for passed args.
    """

    SKILL_NAME = "claude_skills"
    SKILL_DESCRIPTION = "Load Claude SKILL.md files as agent tools"
    SKILL_VERSION = "1.0.0"
    REQUIRED_PACKAGES = ["yaml"]  # PyYAML - import name is 'yaml'
    REQUIRED_ENV_VARS = []
    SUPPORTS_MULTIPLE_INSTANCES = True

    def setup(self) -> bool:
        """
        Setup the Claude skills loader.

        Discovers and parses all SKILL.md files in the configured directory.
        """
        if not self.validate_packages():
            return False

        skills_path = self.params.get("skills_path")
        if not skills_path:
            logger.error("claude_skills: skills_path parameter is required")
            return False

        self._skills_path = Path(skills_path).expanduser().resolve()

        if not self._skills_path.exists():
            logger.error(f"claude_skills: skills_path does not exist: {self._skills_path}")
            return False

        if not self._skills_path.is_dir():
            logger.error(f"claude_skills: skills_path is not a directory: {self._skills_path}")
            return False

        # Load include/exclude patterns
        self._include_patterns = self.params.get("include", ["*"])
        self._exclude_patterns = self.params.get("exclude", [])

        # Store safety/control flags
        self._allow_shell_injection = self.params.get("allow_shell_injection", False)
        self._allow_script_execution = self.params.get("allow_script_execution", False)
        self._ignore_invocation_control = self.params.get("ignore_invocation_control", False)
        self._shell_timeout = self.params.get("shell_timeout", 30)

        if self._allow_shell_injection:
            logger.warning(
                "claude_skills: allow_shell_injection is enabled — "
                "skill bodies may execute arbitrary shell commands"
            )

        # Discover and parse skills
        self._skills = self._discover_skills()

        if not self._skills:
            logger.warning(f"claude_skills: no skills found in {self._skills_path}")
            # Return True anyway - empty skill set is valid

        logger.info(f"claude_skills: loaded {len(self._skills)} skills from {self._skills_path}")
        return True

    def _discover_skills(self) -> List[Dict[str, Any]]:
        """
        Discover and parse all SKILL.md files in the skills directory.

        Returns:
            List of parsed skill dictionaries with name, description, body, sections, etc.
        """
        skills = []

        # Look for skill directories (each containing SKILL.md)
        for item in self._skills_path.iterdir():
            if not item.is_dir():
                continue

            skill_file = item / "SKILL.md"
            if not skill_file.exists():
                continue

            # Check include/exclude patterns
            skill_name = item.name
            if not self._matches_patterns(skill_name):
                logger.debug(f"claude_skills: skipping {skill_name} (excluded by patterns)")
                continue

            # Parse the skill
            parsed = self._parse_skill_md(skill_file)
            if parsed:
                # Use directory name as fallback for skill name
                if not parsed.get("name"):
                    parsed["name"] = skill_name
                parsed["path"] = str(skill_file)
                parsed["skill_dir"] = item

                # Discover supporting files (all .md files except SKILL.md)
                parsed["sections"] = self._discover_sections(item)

                # Discover non-.md files if script execution is enabled
                if self._allow_script_execution:
                    parsed["files"] = self._discover_all_files(item)
                else:
                    parsed["files"] = {}

                # Warn about unsupported frontmatter fields
                self._warn_unsupported_fields(parsed)

                # Warn about shell injection patterns if disabled
                if not self._allow_shell_injection:
                    self._warn_shell_patterns(parsed)

                # Determine invocation control flags
                self._apply_invocation_control(parsed)

                skills.append(parsed)
                section_count = len(parsed["sections"])
                logger.debug(f"claude_skills: loaded skill '{parsed['name']}' from {skill_file} with {section_count} sections")

        return skills

    def _discover_sections(self, skill_dir: Path) -> Dict[str, Path]:
        """
        Find all .md files in skill directory (recursive), excluding SKILL.md.

        These become the enum values for the skill's section parameter.

        Args:
            skill_dir: Path to the skill directory

        Returns:
            Dictionary mapping section names to file paths.
            Keys are the filename stems (without .md extension).
            For nested files, the parent folder is prefixed (e.g., "references/api").
        """
        sections = {}

        for md_file in skill_dir.rglob("*.md"):
            # Skip SKILL.md
            if md_file.name.upper() == "SKILL.MD":
                continue

            # Calculate relative path from skill_dir
            relative = md_file.relative_to(skill_dir)

            # Build section key: parent_folder/filename_stem for nested, just stem for top-level
            if relative.parent != Path("."):
                # Nested file: include parent path
                key = str(relative.parent / md_file.stem)
            else:
                # Top-level file: just use stem
                key = md_file.stem

            # Normalize path separators to forward slashes
            key = key.replace("\\", "/")

            sections[key] = md_file

        return sections

    def _discover_all_files(self, skill_dir: Path) -> Dict[str, List[str]]:
        """
        Discover non-.md files recursively, categorized by location.

        Returns:
            Dictionary with keys 'scripts', 'assets', 'other' mapping to
            lists of relative file paths.
        """
        files = {"scripts": [], "assets": [], "other": []}

        for file_path in skill_dir.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip .md files (handled by _discover_sections)
            if file_path.suffix.lower() == ".md":
                continue

            # Skip hidden files and __pycache__
            relative = file_path.relative_to(skill_dir)
            parts = relative.parts
            if any(p.startswith(".") or p == "__pycache__" for p in parts):
                continue

            rel_str = str(relative).replace("\\", "/")

            # Categorize by top-level directory
            if parts[0] == "scripts":
                files["scripts"].append(rel_str)
            elif parts[0] == "assets":
                files["assets"].append(rel_str)
            else:
                files["other"].append(rel_str)

        # Sort for deterministic output
        for key in files:
            files[key].sort()

        return files

    def _matches_patterns(self, name: str) -> bool:
        """Check if a skill name matches include/exclude patterns."""
        # Check excludes first
        for pattern in self._exclude_patterns:
            if fnmatch.fnmatch(name, pattern):
                return False

        # Check includes
        for pattern in self._include_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True

        return False

    def _parse_skill_md(self, path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a SKILL.md file with YAML frontmatter and markdown body.

        Format:
            ---
            name: skill-name
            description: What this skill does
            ---

            Markdown instructions here...

        Returns:
            Dictionary with name, description, body, and other frontmatter fields
        """
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"claude_skills: failed to read {path}: {e}")
            return None

        # Check for YAML frontmatter
        if not content.startswith("---"):
            # No frontmatter - treat entire content as body
            return {
                "name": None,
                "description": None,
                "body": content.strip()
            }

        # Split frontmatter from body
        parts = content.split("---", 2)
        if len(parts) < 3:
            # Malformed frontmatter
            logger.warning(f"claude_skills: malformed frontmatter in {path}")
            return {
                "name": None,
                "description": None,
                "body": content.strip()
            }

        frontmatter_str = parts[1].strip()
        body = parts[2].strip()

        # Parse YAML frontmatter
        try:
            frontmatter = yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError as e:
            logger.warning(f"claude_skills: failed to parse YAML in {path}: {e}")
            frontmatter = {}

        return {
            "name": frontmatter.get("name"),
            "description": frontmatter.get("description"),
            "body": body,
            # Invocation control
            "disable_model_invocation": frontmatter.get("disable-model-invocation", False),
            "user_invocable": frontmatter.get("user-invocable", True),
            "argument_hint": frontmatter.get("argument-hint"),
            # Informational fields
            "license": frontmatter.get("license"),
            "compatibility": frontmatter.get("compatibility"),
            # Unsupported but parsed fields
            "context": frontmatter.get("context"),
            "agent": frontmatter.get("agent"),
            "allowed_tools": frontmatter.get("allowed-tools"),
            "model": frontmatter.get("model"),
            "hooks": frontmatter.get("hooks"),
            # Store full frontmatter for potential future use
            "_frontmatter": frontmatter
        }

    def _warn_unsupported_fields(self, parsed: Dict[str, Any]) -> None:
        """Log warnings for unsupported frontmatter fields that are set."""
        name = parsed.get("name", "unknown")

        # Map parsed dict keys to frontmatter field names
        field_mapping = {
            "context": "context",
            "agent": "agent",
            "allowed_tools": "allowed-tools",
            "model": "model",
            "hooks": "hooks",
        }

        for parsed_key, frontmatter_key in field_mapping.items():
            value = parsed.get(parsed_key)
            if value is not None:
                msg = _UNSUPPORTED_FIELDS[frontmatter_key].format(name=name)
                logger.warning(f"claude_skills: {msg}")

        # Log informational fields at debug level
        if parsed.get("license"):
            logger.debug(f"claude_skills: skill '{name}' has license: {parsed['license']}")
        if parsed.get("compatibility"):
            logger.debug(f"claude_skills: skill '{name}' has compatibility: {parsed['compatibility']}")

    def _warn_shell_patterns(self, parsed: Dict[str, Any]) -> None:
        """Warn about shell injection patterns when allow_shell_injection is disabled."""
        name = parsed.get("name", "unknown")
        body = parsed.get("body", "")

        for match in _SHELL_INJECTION_RE.finditer(body):
            command = match.group(1)
            logger.warning(
                f"claude_skills: shell injection pattern `!`{command}`` found in skill "
                f"'{name}' but allow_shell_injection is disabled — pattern will be "
                f"passed through as-is. Set allow_shell_injection=True to enable."
            )

    def _apply_invocation_control(self, parsed: Dict[str, Any]) -> None:
        """
        Set _skip_tool and _skip_prompt flags based on invocation control frontmatter.

        When ignore_invocation_control is True, both flags default to False (register everything).
        """
        if self._ignore_invocation_control:
            parsed["_skip_tool"] = False
            parsed["_skip_prompt"] = False
            return

        disable_model = parsed.get("disable_model_invocation", False)
        user_invocable = parsed.get("user_invocable", True)

        if disable_model:
            # disable-model-invocation: true → no tool, no prompt
            parsed["_skip_tool"] = True
            parsed["_skip_prompt"] = True
            logger.debug(f"claude_skills: skill '{parsed['name']}' has disable-model-invocation=true — skipping tool and prompt")
        elif not user_invocable:
            # user-invocable: false → no tool, yes prompt (knowledge-only)
            parsed["_skip_tool"] = True
            parsed["_skip_prompt"] = False
            logger.debug(f"claude_skills: skill '{parsed['name']}' has user-invocable=false — skipping tool, keeping prompt")
        else:
            # Default: register both
            parsed["_skip_tool"] = False
            parsed["_skip_prompt"] = False

    def _sanitize_tool_name(self, name: str) -> str:
        """
        Sanitize a skill name for use as a SWAIG tool name.

        Converts to lowercase, replaces invalid chars with underscores.
        """
        # Replace hyphens and spaces with underscores
        sanitized = re.sub(r"[-\s]+", "_", name.lower())
        # Remove any other invalid characters
        sanitized = re.sub(r"[^a-z0-9_]", "", sanitized)
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = "_" + sanitized
        return sanitized or "unnamed"

    def _execute_shell_injection(self, content: str, skill_dir: Path, timeout: int) -> str:
        """
        Process shell injection patterns in content.

        Replaces !`command` with the stdout of running the command.

        Args:
            content: The content string containing potential shell patterns
            skill_dir: Working directory for command execution
            timeout: Timeout in seconds for each command

        Returns:
            Content with shell patterns replaced by command output
        """
        def replace_command(match):
            command = match.group(1)
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(skill_dir)
                )
                return result.stdout.rstrip("\n")
            except subprocess.TimeoutExpired:
                logger.error(f"claude_skills: shell command timed out after {timeout}s: {command}")
                return f"[command timed out: {command}]"
            except Exception as e:
                logger.error(f"claude_skills: shell command failed: {command}: {e}")
                return f"[command error: {command}]"

        return _SHELL_INJECTION_RE.sub(replace_command, content)

    def _substitute_variables(self, content: str, skill_dir: Path, raw_data: Optional[Dict] = None) -> str:
        """
        Substitute variable placeholders in content.

        Supports:
            ${CLAUDE_SKILL_DIR} - absolute path to skill directory
            ${CLAUDE_SESSION_ID} - session/call ID from raw_data
        """
        content = content.replace("${CLAUDE_SKILL_DIR}", str(skill_dir))

        session_id = ""
        if raw_data:
            session_id = raw_data.get("call_id", "")
        content = content.replace("${CLAUDE_SESSION_ID}", session_id)

        return content

    def _substitute_arguments(self, body: str, arguments: str) -> str:
        """
        Substitute Claude skill argument placeholders.

        Supports:
            $ARGUMENTS - full arguments string
            $ARGUMENTS[N] - positional argument by index
            $0, $1, $2... - shorthand for positional arguments

        If the body does not contain bare $ARGUMENTS (not indexed) and arguments
        are non-empty, appends the arguments to the result.
        """
        if not arguments:
            arguments = ""

        # Check if body contains bare $ARGUMENTS before substitution
        has_bare_arguments = bool(re.search(r"\$ARGUMENTS(?!\[)", body))

        # Split into positional args
        positional = arguments.split() if arguments else []

        # Replace $ARGUMENTS[N] with positional args
        def replace_indexed(match):
            index = int(match.group(1))
            if index < len(positional):
                return positional[index]
            return ""

        result = re.sub(r"\$ARGUMENTS\[(\d+)\]", replace_indexed, body)

        # Replace $N shorthand (must do after $ARGUMENTS to avoid conflicts)
        def replace_shorthand(match):
            index = int(match.group(1))
            if index < len(positional):
                return positional[index]
            return ""

        result = re.sub(r"\$(\d+)(?!\d)", replace_shorthand, result)

        # Replace $ARGUMENTS with full string
        result = result.replace("$ARGUMENTS", arguments)

        # Fallback: append arguments if body had no bare $ARGUMENTS placeholder
        if not has_bare_arguments and arguments:
            result += f"\n\nARGUMENTS: {arguments}"

        return result

    def register_tools(self) -> None:
        """Register a SWAIG tool for each discovered Claude skill."""
        prefix = self.params.get("tool_prefix", "claude_")
        for skill in self._skills:
            # Check invocation control — skip tool registration if flagged
            if skill.get("_skip_tool", False):
                logger.debug(f"claude_skills: skipping tool registration for '{skill['name']}' (invocation control)")
                continue

            tool_name = f"{prefix}{self._sanitize_tool_name(skill['name'])}"

            # Get description (with override support)
            overrides = self.params.get("skill_descriptions", {})
            description = (
                overrides.get(skill["name"]) or
                skill.get("description") or
                f"Use the {skill['name']} skill"
            )

            # Build parameters
            parameters = {
                "arguments": {
                    "type": "string",
                    "description": skill.get("argument_hint") or "Arguments or context to pass to the skill"
                }
            }

            # Add section enum if there are supporting files
            section_names = list(skill.get("sections", {}).keys())
            if section_names:
                parameters["section"] = {
                    "type": "string",
                    "description": "Which reference section to load",
                    "enum": sorted(section_names)
                }

            # Get response prefix/postfix for wrapping results
            response_prefix = self.params.get("response_prefix", "")
            response_postfix = self.params.get("response_postfix", "")

            # Create handler that captures the skill and prefix/postfix
            def make_handler(s, rprefix, rpostfix):
                def handler(args, raw_data):
                    section = args.get("section")
                    arguments = args.get("arguments", "")

                    if section and section in s.get("sections", {}):
                        # Load the requested section file
                        try:
                            content = s["sections"][section].read_text(encoding="utf-8")
                        except Exception as e:
                            logger.error(f"claude_skills: failed to read section '{section}': {e}")
                            content = f"Error loading section '{section}'"
                    else:
                        # No section specified or invalid - return SKILL.md body
                        content = s["body"]

                    skill_dir = s.get("skill_dir", Path("."))

                    # 1. Shell injection (if enabled)
                    if self._allow_shell_injection:
                        content = self._execute_shell_injection(content, skill_dir, self._shell_timeout)

                    # 2. Variable substitution
                    content = self._substitute_variables(content, skill_dir, raw_data)

                    # 3. Argument substitution (with fallback append)
                    content = self._substitute_arguments(content, arguments)

                    # 4. Prefix/postfix wrapping
                    if rprefix or rpostfix:
                        parts = []
                        if rprefix:
                            parts.append(rprefix)
                        parts.append(content)
                        if rpostfix:
                            parts.append(rpostfix)
                        content = "\n\n".join(parts)

                    return FunctionResult(content)
                return handler

            self.define_tool(
                name=tool_name,
                description=description,
                parameters=parameters,
                handler=make_handler(skill, response_prefix, response_postfix)
            )

            section_info = f" with sections: {section_names}" if section_names else ""
            logger.debug(f"claude_skills: registered tool '{tool_name}'{section_info}")

    def get_hints(self) -> List[str]:
        """Return speech recognition hints based on loaded skills."""
        hints = []
        for skill in self._skills:
            # Add skill name words as hints
            name = skill.get("name", "")
            hints.extend(name.replace("-", " ").replace("_", " ").split())
        return list(set(hints))  # Deduplicate

    def _get_prompt_sections(self) -> List[Dict[str, Any]]:
        """
        Return prompt sections describing available Claude skills.

        Each skill's SKILL.md body becomes a prompt section (as a TOC).
        If the skill has supporting files, they are listed with instructions
        on how to load them.
        """
        if not self._skills:
            return []

        prefix = self.params.get("tool_prefix", "claude_")
        sections = []

        for skill in self._skills:
            # Skip skills marked to exclude from prompt
            if skill.get("_skip_prompt", False):
                continue

            tool_name = f"{prefix}{self._sanitize_tool_name(skill['name'])}"
            has_tool = not skill.get("_skip_tool", False)

            # Start with the SKILL.md body
            body = skill["body"]

            # Append available sections if any
            skill_sections = skill.get("sections", {})
            if skill_sections and has_tool:
                section_list = ", ".join(sorted(skill_sections.keys()))
                body += f"\n\nAvailable reference sections: {section_list}"
                body += f"\nCall {tool_name}(section=\"<name>\") to load a section."

            # Append discovered files if script execution is enabled
            if self._allow_script_execution:
                skill_files = skill.get("files", {})
                for category in ("scripts", "assets", "other"):
                    file_list = skill_files.get(category, [])
                    if file_list:
                        label = category.capitalize() if category != "other" else "Other files"
                        body += f"\n\n{label}: {', '.join(file_list)}"

            sections.append({
                "title": skill["name"],
                "body": body
            })

        return sections

    def get_instance_key(self) -> str:
        """Return unique key for this skill instance."""
        # Use skills_path to differentiate instances
        skills_path = self.params.get("skills_path", "default")
        return f"{self.SKILL_NAME}_{hash(skills_path) % 10000}"

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Dict[str, Any]]:
        """Get the parameter schema for the Claude skills loader."""
        schema = super().get_parameter_schema()

        schema.update({
            "skills_path": {
                "type": "string",
                "description": "Path to directory containing Claude skill folders (each with SKILL.md)",
                "required": True
            },
            "include": {
                "type": "array",
                "description": "Glob patterns for skills to include (default: ['*'])",
                "default": ["*"],
                "required": False
            },
            "exclude": {
                "type": "array",
                "description": "Glob patterns for skills to exclude",
                "default": [],
                "required": False
            },
            "prompt_title": {
                "type": "string",
                "description": "Title for the prompt section listing skills",
                "default": "Claude Skills",
                "required": False
            },
            "prompt_intro": {
                "type": "string",
                "description": "Introductory text for the prompt section",
                "default": "You have access to specialized skills. Call the appropriate tool when the user's question matches:",
                "required": False
            },
            "skill_descriptions": {
                "type": "object",
                "description": "Override descriptions for specific skills (skill_name -> description)",
                "default": {},
                "required": False
            },
            "tool_prefix": {
                "type": "string",
                "description": "Prefix for generated tool names (default: 'claude_'). Use empty string for no prefix.",
                "default": "claude_",
                "required": False
            },
            "response_prefix": {
                "type": "string",
                "description": "Text to prepend to skill results (e.g., instructions for the AI)",
                "default": "",
                "required": False
            },
            "response_postfix": {
                "type": "string",
                "description": "Text to append to skill results (e.g., reminders or constraints)",
                "default": "",
                "required": False
            },
            "allow_shell_injection": {
                "type": "boolean",
                "description": "Enable !`command` preprocessing in skill bodies. DANGEROUS: allows arbitrary shell execution.",
                "default": False,
                "required": False
            },
            "allow_script_execution": {
                "type": "boolean",
                "description": "Discover and list scripts/, assets/ files in prompt sections",
                "default": False,
                "required": False
            },
            "ignore_invocation_control": {
                "type": "boolean",
                "description": "Override disable-model-invocation and user-invocable flags, register everything",
                "default": False,
                "required": False
            },
            "shell_timeout": {
                "type": "integer",
                "description": "Timeout in seconds for shell injection commands",
                "default": 30,
                "required": False
            }
        })

        return schema
