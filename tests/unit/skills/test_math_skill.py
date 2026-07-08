"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for the Math skill module
"""

from typing import Any  # noqa: E402
from unittest.mock import Mock  # noqa: E402

from signalwire.skills.math.skill import MathSkill  # noqa: E402
from signalwire.core.function_result import FunctionResult  # noqa: E402


def _make_skill(params: dict[str, Any] | None = None) -> MathSkill:
    """
    Helper to create a MathSkill with a mocked agent.
    """
    default_params = {}
    if params is not None:
        default_params.update(params)

    mock_agent = Mock()
    mock_agent.define_tool = Mock()
    skill = MathSkill(agent=mock_agent, params=default_params)
    return skill  # noqa: RET504


# ---------------------------------------------------------------------------
# Class-level attributes
# ---------------------------------------------------------------------------

class TestMathSkillClassAttributes:
    """Verify class-level constants and metadata."""

    def test_skill_name(self) -> None:
        assert MathSkill.SKILL_NAME == "math"

    def test_skill_description(self) -> None:
        assert MathSkill.SKILL_DESCRIPTION == "Perform basic mathematical calculations"

    def test_skill_version(self) -> None:
        assert MathSkill.SKILL_VERSION == "1.0.0"

    def test_required_packages(self) -> None:
        assert MathSkill.REQUIRED_PACKAGES == []

    def test_required_env_vars(self) -> None:
        assert MathSkill.REQUIRED_ENV_VARS == []


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

class TestMathSkillSetup:
    """Tests for the setup method."""

    def test_setup_returns_true(self) -> None:
        skill = _make_skill()
        assert skill.setup() is True


# ---------------------------------------------------------------------------
# register_tools
# ---------------------------------------------------------------------------

class TestMathSkillRegisterTools:
    """Tests for register_tools."""

    def test_register_tools_calls_define_tool(self) -> None:
        skill = _make_skill()
        skill.register_tools()
        skill.agent.define_tool.assert_called_once()

    def test_register_tools_defines_calculate(self) -> None:
        skill = _make_skill()
        skill.register_tools()
        call_kwargs = skill.agent.define_tool.call_args
        kwargs = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
        assert kwargs.get("name") == "calculate"

    def test_register_tools_has_description(self) -> None:
        skill = _make_skill()
        skill.register_tools()
        call_kwargs = skill.agent.define_tool.call_args
        kwargs = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
        assert "description" in kwargs
        assert "mathematical" in kwargs["description"].lower() or "calculation" in kwargs["description"].lower()

    def test_register_tools_has_expression_parameter(self) -> None:
        skill = _make_skill()
        skill.register_tools()
        call_kwargs = skill.agent.define_tool.call_args
        kwargs = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
        assert "parameters" in kwargs
        assert "expression" in kwargs["parameters"]

    def test_register_tools_has_handler(self) -> None:
        skill = _make_skill()
        skill.register_tools()
        call_kwargs = skill.agent.define_tool.call_args
        kwargs = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
        assert "handler" in kwargs
        assert callable(kwargs["handler"])


# ---------------------------------------------------------------------------
# _calculate_handler - valid expressions
# ---------------------------------------------------------------------------

class TestCalculateHandlerValid:
    """Tests for _calculate_handler with valid expressions."""

    def test_addition(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "2+3"}, {})
        assert isinstance(result, FunctionResult)
        assert "5" in result.response

    def test_subtraction(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "10-4"}, {})
        assert "6" in result.response

    def test_multiplication(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "(2+3)*4"}, {})
        assert "20" in result.response

    def test_division(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "10/3"}, {})
        assert "3.333" in result.response

    def test_exponentiation(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "2**8"}, {})
        assert "256" in result.response

    def test_modulo(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "10%3"}, {})
        assert "1" in result.response

    def test_expression_with_spaces(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": " 2 + 3 "}, {})
        assert "5" in result.response

    def test_nested_parentheses(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "((2+3)*2)"}, {})
        assert "10" in result.response

    def test_float_numbers(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "1.5 + 2.5"}, {})
        assert "4" in result.response


# ---------------------------------------------------------------------------
# _calculate_handler - empty / missing expression
# ---------------------------------------------------------------------------

class TestCalculateHandlerEmpty:
    """Tests for _calculate_handler with empty or missing expressions."""

    def test_empty_string(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": ""}, {})
        assert isinstance(result, FunctionResult)
        assert "provide" in result.response.lower()

    def test_whitespace_only(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "   "}, {})
        assert isinstance(result, FunctionResult)
        assert "provide" in result.response.lower()

    def test_missing_expression_key(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({}, {})
        assert isinstance(result, FunctionResult)
        assert "provide" in result.response.lower()


# ---------------------------------------------------------------------------
# _calculate_handler - unsafe characters
# ---------------------------------------------------------------------------

class TestCalculateHandlerUnsafe:
    """Tests for _calculate_handler with unsafe / disallowed input."""

    def test_import_os_rejected(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "import os"}, {})
        assert isinstance(result, FunctionResult)
        assert "invalid" in result.response.lower()

    def test_letters_rejected(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "abc"}, {})
        assert isinstance(result, FunctionResult)
        assert "invalid" in result.response.lower()

    def test_dunder_rejected(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "__import__('os')"}, {})
        assert isinstance(result, FunctionResult)
        assert "invalid" in result.response.lower()

    def test_semicolon_rejected(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "1;2"}, {})
        assert isinstance(result, FunctionResult)
        assert "invalid" in result.response.lower()


# ---------------------------------------------------------------------------
# _calculate_handler - division by zero
# ---------------------------------------------------------------------------

class TestCalculateHandlerDivisionByZero:
    """Tests for _calculate_handler with division by zero."""

    def test_division_by_zero(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "1/0"}, {})
        assert isinstance(result, FunctionResult)
        assert "zero" in result.response.lower()

    def test_modulo_by_zero(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "10%0"}, {})
        assert isinstance(result, FunctionResult)
        assert "zero" in result.response.lower()


# ---------------------------------------------------------------------------
# _calculate_handler - invalid expression (syntax errors)
# ---------------------------------------------------------------------------

class TestCalculateHandlerInvalidExpression:
    """Tests for _calculate_handler with syntactically invalid expressions."""

    def test_incomplete_expression(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "2+"}, {})
        assert isinstance(result, FunctionResult)
        assert "error" in result.response.lower()

    def test_unmatched_parens(self) -> None:
        skill = _make_skill()
        result = skill._calculate_handler({"expression": "(2+3"}, {})
        assert isinstance(result, FunctionResult)
        assert "error" in result.response.lower()


# ---------------------------------------------------------------------------
# get_hints
# ---------------------------------------------------------------------------

class TestMathSkillGetHints:
    """Tests for get_hints."""

    def test_returns_list(self) -> None:
        skill = _make_skill()
        hints = skill.get_hints()
        assert isinstance(hints, list)

    def test_returns_empty_list(self) -> None:
        skill = _make_skill()
        assert skill.get_hints() == []


# ---------------------------------------------------------------------------
# get_prompt_sections
# ---------------------------------------------------------------------------

class TestMathSkillGetPromptSections:
    """Tests for get_prompt_sections."""

    def test_returns_list(self) -> None:
        skill = _make_skill()
        sections = skill.get_prompt_sections()
        assert isinstance(sections, list)

    def test_returns_one_section(self) -> None:
        skill = _make_skill()
        sections = skill.get_prompt_sections()
        assert len(sections) == 1

    def test_section_has_title(self) -> None:
        skill = _make_skill()
        section = skill.get_prompt_sections()[0]
        assert "title" in section
        assert section["title"] == "Mathematical Calculations"

    def test_section_has_body(self) -> None:
        skill = _make_skill()
        section = skill.get_prompt_sections()[0]
        assert "body" in section
        assert isinstance(section["body"], str)

    def test_section_has_bullets(self) -> None:
        skill = _make_skill()
        section = skill.get_prompt_sections()[0]
        assert "bullets" in section
        assert isinstance(section["bullets"], list)
        assert len(section["bullets"]) > 0


# ---------------------------------------------------------------------------
# get_parameter_schema
# ---------------------------------------------------------------------------

class TestMathSkillGetParameterSchema:
    """Tests for get_parameter_schema."""

    def test_returns_dict(self) -> None:
        schema = MathSkill.get_parameter_schema()
        assert isinstance(schema, dict)

    def test_schema_includes_swaig_fields(self) -> None:
        schema = MathSkill.get_parameter_schema()
        assert "swaig_fields" in schema
