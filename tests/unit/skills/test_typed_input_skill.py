"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Unit tests for the typed_input skill.
"""

import json
from unittest.mock import Mock

from signalwire.core.function_result import FunctionResult
from signalwire.skills.typed_input.skill import TypedInputSkill

_PARAMS = {
    "field": "installer_email",
    "input_type": "email",
    "open_prompt": {
        "en": "Please type the email on your screen.",
        "pl": "Wpisz adres e-mail na ekranie.",
    },
    "field_label": {"en": "Installer's email", "pl": "Adres e-mail instalatora"},
    "invalid_prompt": {
        "en": "That does not look like a valid email; please type it again.",
        "pl": "To nie wygląda na poprawny adres; wpisz go ponownie.",
    },
}


def _make_skill(params=None):
    """Create a TypedInputSkill with a mocked agent and run setup()."""
    skill = TypedInputSkill(
        agent=Mock(), params=dict(params if params is not None else _PARAMS)
    )
    assert skill.setup() is True
    return skill


def _actions_json(result: FunctionResult) -> str:
    return json.dumps(result.action, ensure_ascii=False)


class TestClassAttributes:
    def test_name_and_multi_instance(self):
        assert TypedInputSkill.SKILL_NAME == "typed_input"
        assert TypedInputSkill.SKILL_VERSION == "1.0.0"
        assert TypedInputSkill.SUPPORTS_MULTIPLE_INSTANCES is True
        assert TypedInputSkill.REQUIRED_PACKAGES == []


class TestParameterSchema:
    def test_declares_field_and_prompt_params(self):
        schema = TypedInputSkill.get_parameter_schema()
        for key in (
            "field",
            "input_type",
            "open_prompt",
            "field_label",
            "invalid_prompt",
        ):
            assert key in schema
        assert schema["field"]["required"] is True
        assert schema["input_type"]["enum"] == ["email", "phone", "number", "text"]


class TestSetup:
    def test_derives_per_field_names(self):
        skill = _make_skill()
        assert skill.gd_key == "typed_installer_email"
        assert skill.request_tool == "request_installer_email"
        assert skill.confirm_tool == "confirm_installer_email"

    def test_instance_key_is_per_field(self):
        assert _make_skill().get_instance_key() == "typed_input_installer_email"

    def test_setup_fails_without_field(self):
        skill = TypedInputSkill(
            agent=Mock(), params={"open_prompt": {}, "field_label": {}}
        )
        assert skill.setup() is False


class TestRegisterTools:
    def test_registers_request_and_confirm(self):
        skill = _make_skill()
        skill.agent.define_tool = Mock()
        skill.register_tools()
        names = [c.kwargs["name"] for c in skill.agent.define_tool.call_args_list]
        assert names == ["request_installer_email", "confirm_installer_email"]
        # the value comes from global_data, never a model argument
        for c in skill.agent.define_tool.call_args_list:
            assert c.kwargs["parameters"] == {}


class TestOpenHandler:
    def test_opens_keypad_in_call_language(self):
        skill = _make_skill()
        result = skill._open_handler({}, {"global_data": {"language": "pl"}})
        assert isinstance(result, FunctionResult)
        assert result.response == "Wpisz adres e-mail na ekranie."
        actions = _actions_json(result)
        assert "input_request" in actions
        assert "typed_installer_email" in actions
        assert "email" in actions
        assert "wait_for_user" in actions

    def test_falls_back_to_english_for_unknown_language(self):
        skill = _make_skill()
        result = skill._open_handler({}, {"global_data": {"language": "fr"}})
        assert result.response == "Please type the email on your screen."

    def test_defaults_to_english_with_no_language(self):
        skill = _make_skill()
        result = skill._open_handler({}, {})
        assert result.response == "Please type the email on your screen."


class TestConfirmHandler:
    def test_valid_email_reads_back_spoken_form(self):
        skill = _make_skill()
        raw = {
            "global_data": {"language": "pl", "typed_installer_email": "a.b@gmail.com"}
        }
        result = skill._confirm_handler({}, raw)
        # Polish spoken form, the raw value, and the reopen tool for a NO.
        assert "a kropka b małpka gmail kropka com" in result.response
        assert "a.b@gmail.com" in result.response
        assert "request_installer_email" in result.response
        # a read-back does NOT reopen the keypad
        assert "input_request" not in _actions_json(result)

    def test_missing_value_reopens_keypad(self):
        skill = _make_skill()
        result = skill._confirm_handler({}, {"global_data": {"language": "en"}})
        assert result.response == _PARAMS["invalid_prompt"]["en"]
        assert "input_request" in _actions_json(result)

    def test_invalid_email_reopens_keypad(self):
        skill = _make_skill()
        raw = {"global_data": {"language": "en", "typed_installer_email": "notanemail"}}
        result = skill._confirm_handler({}, raw)
        assert result.response == _PARAMS["invalid_prompt"]["en"]
        assert "input_request" in _actions_json(result)
