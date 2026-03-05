"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for the Claude Skills skill module.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from signalwire_agents.skills.claude_skills.skill import ClaudeSkillsSkill
from signalwire_agents.core.function_result import SwaigFunctionResult


def _make_skill(params=None):
    """
    Helper to create a ClaudeSkillsSkill with a mocked agent.
    Does NOT call setup() — caller must do so after creating temp dirs.
    """
    default_params = {}
    if params is not None:
        default_params.update(params)

    mock_agent = Mock()
    mock_agent.define_tool = Mock()
    skill = ClaudeSkillsSkill(agent=mock_agent, params=default_params)
    return skill


def _write_skill_md(skill_dir, name, description="Test skill", body="Test body",
                    extra_frontmatter=None):
    """Helper to create a SKILL.md file in a skill directory."""
    skill_dir.mkdir(parents=True, exist_ok=True)
    frontmatter_dict = {"name": name, "description": description}
    if extra_frontmatter:
        frontmatter_dict.update(extra_frontmatter)

    lines = ["---"]
    for key, value in frontmatter_dict.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")
    lines.append(body)

    (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Class-level attributes
# ---------------------------------------------------------------------------

class TestClassAttributes:
    """Verify class-level constants and metadata."""

    def test_skill_name(self):
        assert ClaudeSkillsSkill.SKILL_NAME == "claude_skills"

    def test_skill_description(self):
        assert ClaudeSkillsSkill.SKILL_DESCRIPTION == "Load Claude SKILL.md files as agent tools"

    def test_skill_version(self):
        assert ClaudeSkillsSkill.SKILL_VERSION == "1.0.0"

    def test_required_packages(self):
        assert "yaml" in ClaudeSkillsSkill.REQUIRED_PACKAGES

    def test_required_env_vars(self):
        assert ClaudeSkillsSkill.REQUIRED_ENV_VARS == []

    def test_supports_multiple_instances(self):
        assert ClaudeSkillsSkill.SUPPORTS_MULTIPLE_INSTANCES is True


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

class TestParseSkillMd:
    """Test frontmatter parsing including all spec fields."""

    def test_basic_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "test-skill"
            _write_skill_md(skill_dir, "test-skill", "A test", "Hello world")
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            assert len(skill._skills) == 1
            assert skill._skills[0]["name"] == "test-skill"
            assert skill._skills[0]["description"] == "A test"
            assert skill._skills[0]["body"] == "Hello world"

    def test_license_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            _write_skill_md(skill_dir, "my-skill", extra_frontmatter={"license": "MIT"})
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            assert skill._skills[0]["license"] == "MIT"

    def test_compatibility_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            _write_skill_md(skill_dir, "my-skill", extra_frontmatter={"compatibility": "claude-code >= 1.0"})
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            assert skill._skills[0]["compatibility"] == "claude-code >= 1.0"

    def test_context_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            _write_skill_md(skill_dir, "my-skill", extra_frontmatter={"context": "fork"})
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            assert skill._skills[0]["context"] == "fork"

    def test_agent_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            _write_skill_md(skill_dir, "my-skill", extra_frontmatter={"agent": "Explore"})
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            assert skill._skills[0]["agent"] == "Explore"

    def test_allowed_tools_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            _write_skill_md(skill_dir, "my-skill", extra_frontmatter={"allowed-tools": "Read, Grep"})
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            assert skill._skills[0]["allowed_tools"] == "Read, Grep"

    def test_model_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            _write_skill_md(skill_dir, "my-skill", extra_frontmatter={"model": "opus"})
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            assert skill._skills[0]["model"] == "opus"

    def test_hooks_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            _write_skill_md(skill_dir, "my-skill", extra_frontmatter={"hooks": "pre-run"})
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            assert skill._skills[0]["hooks"] == "pre-run"

    def test_no_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "bare-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("Just plain markdown", encoding="utf-8")
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            assert skill._skills[0]["name"] == "bare-skill"
            assert skill._skills[0]["body"] == "Just plain markdown"


# ---------------------------------------------------------------------------
# Invocation control
# ---------------------------------------------------------------------------

class TestInvocationControl:
    """Test disable-model-invocation and user-invocable flags."""

    def test_disable_model_invocation_skips_tool_and_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "disabled-skill"
            _write_skill_md(skill_dir, "disabled-skill",
                            extra_frontmatter={"disable-model-invocation": True})
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()

            assert skill._skills[0]["_skip_tool"] is True
            assert skill._skills[0]["_skip_prompt"] is True

            skill.register_tools()
            skill.agent.define_tool.assert_not_called()

            sections = skill._get_prompt_sections()
            assert len(sections) == 0

    def test_user_invocable_false_skips_tool_keeps_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "knowledge-skill"
            _write_skill_md(skill_dir, "knowledge-skill", body="Knowledge content",
                            extra_frontmatter={"user-invocable": False})
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()

            assert skill._skills[0]["_skip_tool"] is True
            assert skill._skills[0]["_skip_prompt"] is False

            skill.register_tools()
            skill.agent.define_tool.assert_not_called()

            sections = skill._get_prompt_sections()
            assert len(sections) == 1
            assert sections[0]["title"] == "knowledge-skill"

    def test_ignore_invocation_control_registers_everything(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "disabled-skill"
            _write_skill_md(skill_dir, "disabled-skill",
                            extra_frontmatter={"disable-model-invocation": True})
            skill = _make_skill({"skills_path": tmpdir, "ignore_invocation_control": True})
            skill.setup()

            assert skill._skills[0]["_skip_tool"] is False
            assert skill._skills[0]["_skip_prompt"] is False

            skill.register_tools()
            skill.agent.define_tool.assert_called_once()

            sections = skill._get_prompt_sections()
            assert len(sections) == 1

    def test_default_behavior_registers_both(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "normal-skill"
            _write_skill_md(skill_dir, "normal-skill")
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()

            assert skill._skills[0]["_skip_tool"] is False
            assert skill._skills[0]["_skip_prompt"] is False

            skill.register_tools()
            skill.agent.define_tool.assert_called_once()

            sections = skill._get_prompt_sections()
            assert len(sections) == 1


# ---------------------------------------------------------------------------
# Shell injection
# ---------------------------------------------------------------------------

class TestShellInjection:
    """Test shell injection pattern handling."""

    def test_disabled_by_default_passes_through(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "shell-skill"
            _write_skill_md(skill_dir, "shell-skill", body="Result: !`echo hello`")
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            skill.register_tools()

            # Get handler and invoke
            call_kwargs = skill.agent.define_tool.call_args
            kwargs = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
            handler = kwargs["handler"]
            result = handler({"arguments": ""}, {})
            # Pattern passes through unchanged
            assert "!`echo hello`" in result.response

    def test_enabled_executes_command(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "shell-skill"
            _write_skill_md(skill_dir, "shell-skill", body="Result: !`echo hello`")
            skill = _make_skill({"skills_path": tmpdir, "allow_shell_injection": True})
            skill.setup()
            skill.register_tools()

            call_kwargs = skill.agent.define_tool.call_args
            kwargs = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
            handler = kwargs["handler"]
            result = handler({"arguments": ""}, {})
            assert "hello" in result.response
            assert "!`" not in result.response

    def test_timeout_handling(self):
        skill = _make_skill({"skills_path": "/tmp", "allow_shell_injection": True})
        skill._allow_shell_injection = True
        skill._shell_timeout = 1
        content = "!`sleep 10`"
        result = skill._execute_shell_injection(content, Path("/tmp"), timeout=1)
        assert "[command timed out:" in result

    def test_error_handling(self):
        skill = _make_skill({"skills_path": "/tmp", "allow_shell_injection": True})
        skill._allow_shell_injection = True
        content = "!`nonexistent_command_xyz_12345`"
        result = skill._execute_shell_injection(content, Path("/tmp"), timeout=5)
        # The command will produce stderr but still return (non-zero exit code)
        # subprocess.run doesn't raise on non-zero exit, so result is stdout (empty)
        # This is expected behavior — command runs but produces no stdout
        assert "!`" not in result


# ---------------------------------------------------------------------------
# Variable substitution
# ---------------------------------------------------------------------------

class TestVariableSubstitution:
    """Test ${CLAUDE_SKILL_DIR} and ${CLAUDE_SESSION_ID} substitution."""

    def test_skill_dir_replaced(self):
        skill = _make_skill({"skills_path": "/tmp"})
        content = "Path: ${CLAUDE_SKILL_DIR}/file.txt"
        result = skill._substitute_variables(content, Path("/opt/skills/my-skill"))
        assert result == "Path: /opt/skills/my-skill/file.txt"

    def test_session_id_replaced(self):
        skill = _make_skill({"skills_path": "/tmp"})
        content = "Session: ${CLAUDE_SESSION_ID}"
        result = skill._substitute_variables(content, Path("/tmp"), {"call_id": "abc-123"})
        assert result == "Session: abc-123"

    def test_missing_raw_data_graceful(self):
        skill = _make_skill({"skills_path": "/tmp"})
        content = "Session: ${CLAUDE_SESSION_ID}"
        result = skill._substitute_variables(content, Path("/tmp"), None)
        assert result == "Session: "

    def test_missing_call_id_graceful(self):
        skill = _make_skill({"skills_path": "/tmp"})
        content = "Session: ${CLAUDE_SESSION_ID}"
        result = skill._substitute_variables(content, Path("/tmp"), {"other_key": "val"})
        assert result == "Session: "


# ---------------------------------------------------------------------------
# Fallback argument appending
# ---------------------------------------------------------------------------

class TestFallbackArguments:
    """Test fallback argument appending when body lacks bare $ARGUMENTS."""

    def test_body_with_bare_arguments_no_fallback(self):
        skill = _make_skill({"skills_path": "/tmp"})
        result = skill._substitute_arguments("Use $ARGUMENTS here", "some input")
        assert result == "Use some input here"
        assert "ARGUMENTS:" not in result

    def test_body_without_arguments_appends_fallback(self):
        skill = _make_skill({"skills_path": "/tmp"})
        result = skill._substitute_arguments("Do the thing", "some input")
        assert "Do the thing" in result
        assert "\n\nARGUMENTS: some input" in result

    def test_indexed_form_triggers_fallback(self):
        skill = _make_skill({"skills_path": "/tmp"})
        result = skill._substitute_arguments("Use $ARGUMENTS[0] only", "hello world")
        # $ARGUMENTS[0] is indexed — bare $ARGUMENTS not present, so fallback appends
        assert "hello" in result
        assert "\n\nARGUMENTS: hello world" in result

    def test_empty_arguments_no_append(self):
        skill = _make_skill({"skills_path": "/tmp"})
        result = skill._substitute_arguments("Do the thing", "")
        assert result == "Do the thing"
        assert "ARGUMENTS:" not in result


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

class TestFileDiscovery:
    """Test scripts/ and assets/ discovery."""

    def test_disabled_no_file_discovery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "file-skill"
            _write_skill_md(skill_dir, "file-skill")
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "run.sh").write_text("#!/bin/bash\necho hi")

            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            assert skill._skills[0]["files"] == {}

    def test_enabled_discovers_scripts_and_assets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "file-skill"
            _write_skill_md(skill_dir, "file-skill")

            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "run.sh").write_text("#!/bin/bash\necho hi")

            assets_dir = skill_dir / "assets"
            assets_dir.mkdir()
            (assets_dir / "data.json").write_text('{"key": "value"}')

            skill = _make_skill({"skills_path": tmpdir, "allow_script_execution": True})
            skill.setup()

            files = skill._skills[0]["files"]
            assert "scripts/run.sh" in files["scripts"]
            assert "assets/data.json" in files["assets"]

    def test_files_listed_in_prompt_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "file-skill"
            _write_skill_md(skill_dir, "file-skill", body="Instructions")

            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "build.sh").write_text("#!/bin/bash")

            skill = _make_skill({"skills_path": tmpdir, "allow_script_execution": True})
            skill.setup()

            sections = skill._get_prompt_sections()
            assert len(sections) == 1
            assert "scripts/build.sh" in sections[0]["body"]

    def test_hidden_files_skipped(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "file-skill"
            _write_skill_md(skill_dir, "file-skill")

            (skill_dir / ".hidden_file").write_text("secret")
            pycache = skill_dir / "__pycache__"
            pycache.mkdir()
            (pycache / "cache.pyc").write_text("compiled")

            skill = _make_skill({"skills_path": tmpdir, "allow_script_execution": True})
            skill.setup()

            files = skill._skills[0]["files"]
            all_files = files["scripts"] + files["assets"] + files["other"]
            assert len(all_files) == 0


# ---------------------------------------------------------------------------
# Prompt section fix (renamed to _get_prompt_sections)
# ---------------------------------------------------------------------------

class TestPromptSectionFix:
    """Test that skip_prompt works correctly via base class."""

    def test_skip_prompt_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            _write_skill_md(skill_dir, "my-skill", body="Content here")
            skill = _make_skill({"skills_path": tmpdir, "skip_prompt": True})
            skill.setup()

            # get_prompt_sections() (base class) should return empty when skip_prompt=True
            sections = skill.get_prompt_sections()
            assert sections == []

    def test_no_skip_prompt_returns_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            _write_skill_md(skill_dir, "my-skill", body="Content here")
            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()

            sections = skill.get_prompt_sections()
            assert len(sections) == 1
            assert sections[0]["title"] == "my-skill"


# ---------------------------------------------------------------------------
# Unsupported feature warnings
# ---------------------------------------------------------------------------

class TestUnsupportedFeatureWarnings:
    """Test that unsupported frontmatter fields trigger warnings."""

    def test_context_fork_warning(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "forked"
            _write_skill_md(skill_dir, "forked", extra_frontmatter={"context": "fork"})
            skill = _make_skill({"skills_path": tmpdir})
            with patch("signalwire_agents.skills.claude_skills.skill.logger") as mock_logger:
                skill.setup()
            warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
            assert any("context: fork is not supported" in c for c in warning_calls)

    def test_agent_warning(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "agent-skill"
            _write_skill_md(skill_dir, "agent-skill", extra_frontmatter={"agent": "Explore"})
            skill = _make_skill({"skills_path": tmpdir})
            with patch("signalwire_agents.skills.claude_skills.skill.logger") as mock_logger:
                skill.setup()
            warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
            assert any("agent field is not supported" in c for c in warning_calls)

    def test_allowed_tools_warning(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "tools-skill"
            _write_skill_md(skill_dir, "tools-skill", extra_frontmatter={"allowed-tools": "Read, Grep"})
            skill = _make_skill({"skills_path": tmpdir})
            with patch("signalwire_agents.skills.claude_skills.skill.logger") as mock_logger:
                skill.setup()
            warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
            assert any("allowed-tools is not supported" in c for c in warning_calls)

    def test_model_warning(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "model-skill"
            _write_skill_md(skill_dir, "model-skill", extra_frontmatter={"model": "opus"})
            skill = _make_skill({"skills_path": tmpdir})
            with patch("signalwire_agents.skills.claude_skills.skill.logger") as mock_logger:
                skill.setup()
            warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
            assert any("model field is not supported" in c for c in warning_calls)

    def test_hooks_warning(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "hooks-skill"
            _write_skill_md(skill_dir, "hooks-skill", extra_frontmatter={"hooks": "pre-run"})
            skill = _make_skill({"skills_path": tmpdir})
            with patch("signalwire_agents.skills.claude_skills.skill.logger") as mock_logger:
                skill.setup()
            warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
            assert any("hooks field is not supported" in c for c in warning_calls)

    def test_shell_pattern_warning_when_disabled(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "shell-warn"
            _write_skill_md(skill_dir, "shell-warn", body="Run !`date` now")
            skill = _make_skill({"skills_path": tmpdir})
            with patch("signalwire_agents.skills.claude_skills.skill.logger") as mock_logger:
                skill.setup()
            warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
            assert any("shell injection pattern" in c and "allow_shell_injection is disabled" in c
                        for c in warning_calls)

    def test_no_warnings_for_clean_skill(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "clean"
            _write_skill_md(skill_dir, "clean", body="Just text")
            skill = _make_skill({"skills_path": tmpdir})
            with patch("signalwire_agents.skills.claude_skills.skill.logger") as mock_logger:
                skill.setup()
            warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
            unsupported_warnings = [c for c in warning_calls
                                     if "not supported" in c or "shell injection" in c]
            assert len(unsupported_warnings) == 0


# ---------------------------------------------------------------------------
# Handler pipeline integration
# ---------------------------------------------------------------------------

class TestHandlerPipeline:
    """Test the full handler processing pipeline."""

    def test_full_pipeline_ordering(self):
        """Shell injection -> variables -> arguments -> wrapping."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "pipeline-skill"
            body = "Dir: ${CLAUDE_SKILL_DIR} | Args: $ARGUMENTS"
            _write_skill_md(skill_dir, "pipeline-skill", body=body)

            skill = _make_skill({
                "skills_path": tmpdir,
                "response_prefix": "PREFIX",
                "response_postfix": "POSTFIX",
            })
            skill.setup()
            skill.register_tools()

            call_kwargs = skill.agent.define_tool.call_args
            kwargs = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
            handler = kwargs["handler"]
            result = handler({"arguments": "test-arg"}, {"call_id": "sess-1"})

            # Variables should be substituted
            assert str(skill_dir) in result.response
            # Arguments should be substituted
            assert "test-arg" in result.response
            # Prefix/postfix should wrap
            assert result.response.startswith("PREFIX")
            assert result.response.endswith("POSTFIX")

    def test_shell_then_variables_then_arguments(self):
        """Verify processing order: shell first, then vars, then args."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "order-skill"
            # Shell outputs something, then variable and arg substitution happens
            body = "Shell: !`echo shellout` | Dir: ${CLAUDE_SKILL_DIR} | Arg: $ARGUMENTS"
            _write_skill_md(skill_dir, "order-skill", body=body)

            skill = _make_skill({
                "skills_path": tmpdir,
                "allow_shell_injection": True,
            })
            skill.setup()
            skill.register_tools()

            call_kwargs = skill.agent.define_tool.call_args
            kwargs = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
            handler = kwargs["handler"]
            result = handler({"arguments": "myarg"}, {"call_id": "c1"})

            assert "shellout" in result.response
            assert str(skill_dir) in result.response
            assert "myarg" in result.response

    def test_variable_substitution_in_handler(self):
        """Test that ${CLAUDE_SESSION_ID} uses raw_data call_id."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "var-skill"
            _write_skill_md(skill_dir, "var-skill", body="ID: ${CLAUDE_SESSION_ID}")

            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            skill.register_tools()

            call_kwargs = skill.agent.define_tool.call_args
            kwargs = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
            handler = kwargs["handler"]
            result = handler({"arguments": ""}, {"call_id": "my-session-42"})

            assert "ID: my-session-42" in result.response

    def test_section_loading_with_pipeline(self):
        """Test that section files also go through the pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "section-skill"
            _write_skill_md(skill_dir, "section-skill", body="Main body")

            # Create a section file with variable placeholders
            (skill_dir / "reference.md").write_text(
                "Ref dir: ${CLAUDE_SKILL_DIR} | Args: $ARGUMENTS",
                encoding="utf-8"
            )

            skill = _make_skill({"skills_path": tmpdir})
            skill.setup()
            skill.register_tools()

            call_kwargs = skill.agent.define_tool.call_args
            kwargs = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
            handler = kwargs["handler"]
            result = handler({"section": "reference", "arguments": "ctx"}, {})

            assert str(skill_dir) in result.response
            assert "ctx" in result.response


# ---------------------------------------------------------------------------
# Parameter schema
# ---------------------------------------------------------------------------

class TestParameterSchema:
    """Test get_parameter_schema includes new params."""

    def test_schema_includes_new_params(self):
        schema = ClaudeSkillsSkill.get_parameter_schema()
        assert "allow_shell_injection" in schema
        assert schema["allow_shell_injection"]["type"] == "boolean"
        assert schema["allow_shell_injection"]["default"] is False

        assert "allow_script_execution" in schema
        assert schema["allow_script_execution"]["type"] == "boolean"

        assert "ignore_invocation_control" in schema
        assert schema["ignore_invocation_control"]["type"] == "boolean"

        assert "shell_timeout" in schema
        assert schema["shell_timeout"]["type"] == "integer"
        assert schema["shell_timeout"]["default"] == 30

    def test_schema_includes_existing_params(self):
        schema = ClaudeSkillsSkill.get_parameter_schema()
        assert "skills_path" in schema
        assert "include" in schema
        assert "exclude" in schema
        assert "tool_prefix" in schema
        assert "swaig_fields" in schema
        assert "skip_prompt" in schema
