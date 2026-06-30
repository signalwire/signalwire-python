"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Typed-input skill — collect a value the caller TYPES on an on-screen keypad
(email, phone, account number, ...) for the cases speech-to-text can't capture
reliably.

The flow, deterministic by design so the model can never alter the value:
  1. request_<field>  speaks a short "type it on screen" line, emits an
     ``input_request`` user-event (so a connected app reveals + focuses the
     field), and parks via wait_for_user until the caller submits.
  2. The app posts the typed value into ``global_data['typed_<field>']``.
  3. confirm_<field>  reads that RAW value back (never a model argument, so a
     typo is never silently "corrected"), validates it, reopens the keypad if it
     is missing/invalid, otherwise reads it back for the caller to confirm.

Multi-instance: add it once per field. Prompts are per-language maps resolved
against ``global_data['language']`` at call time, so one instance serves a
multilingual agent. Validation, the user-event payload, and the spoken read-back
come from ``signalwire.conversation_kit``.
"""

from __future__ import annotations

from typing import Any, ClassVar

from signalwire.conversation_kit import input_request_payload, validate_input
from signalwire.conversation_kit.verbalizer import get as get_verbalizer
from signalwire.core.function_result import FunctionResult
from signalwire.core.skill_base import SkillBase

_DEFAULT_LANG = "en"


class TypedInputSkill(SkillBase):
    """Collect a typed value over the on-screen keypad channel (one instance per field)."""

    SKILL_NAME = "typed_input"
    SKILL_DESCRIPTION = (
        "Collect a value the caller types on an on-screen keypad (email, phone, ...) "
        "when speech-to-text can't capture it reliably"
    )
    SKILL_VERSION = "1.0.0"
    REQUIRED_PACKAGES: ClassVar[list[str]] = []
    REQUIRED_ENV_VARS: ClassVar[list[str]] = []
    SUPPORTS_MULTIPLE_INSTANCES = True

    @classmethod
    def get_parameter_schema(cls) -> dict[str, dict[str, Any]]:
        """Parameters: the field, its validation type, and the per-language prompts."""
        schema = super().get_parameter_schema()
        schema.update(
            {
                "field": {
                    "type": "string",
                    "description": (
                        "Field key, e.g. 'installer_email'. Tools become request_<field> / "
                        "confirm_<field>; the typed value lands in global_data['typed_<field>']."
                    ),
                    "required": True,
                },
                "input_type": {
                    "type": "string",
                    "description": "Validation + read-back style for the typed value.",
                    "default": "text",
                    "enum": ["email", "phone", "number", "text"],
                    "required": False,
                },
                "open_prompt": {
                    "type": "object",
                    "description": (
                        "Per-language map ({lang: text}) of the line spoken when the keypad "
                        "opens ('please type it on your screen'). Falls back to 'en'."
                    ),
                    "required": True,
                },
                "field_label": {
                    "type": "object",
                    "description": "Per-language map ({lang: text}) of the on-screen field label.",
                    "required": True,
                },
                "invalid_prompt": {
                    "type": "object",
                    "description": (
                        "Per-language map ({lang: text}) spoken when the typed value fails "
                        "validation, before the keypad reopens."
                    ),
                    "required": True,
                },
            }
        )
        return schema

    def get_instance_key(self) -> str:
        """One instance per field, so several typed fields can coexist on one agent."""
        field = self.params.get("field")
        return f"{self.SKILL_NAME}_{field}" if field else self.SKILL_NAME

    def setup(self) -> bool:
        """Validate params and derive the per-field tool/global-data names."""
        field = self.params.get("field")
        if not field or not isinstance(field, str):
            self.logger.error(
                "typed_input requires a non-empty string 'field' parameter"
            )
            return False
        self.field: str = field
        self.input_type: str = self.params.get("input_type", "text")
        self.gd_key: str = f"typed_{field}"
        self.request_tool: str = f"request_{field}"
        self.confirm_tool: str = f"confirm_{field}"
        self.open_prompt: dict[str, str] = self.params.get("open_prompt") or {}
        self.field_label: dict[str, str] = self.params.get("field_label") or {}
        self.invalid_prompt: dict[str, str] = self.params.get("invalid_prompt") or {}
        return True

    def register_tools(self) -> None:
        """Register the request_<field> opener and confirm_<field> read-back tools."""
        self.define_tool(
            name=self.request_tool,
            description=(
                f"Open the on-screen keypad for the caller to type their {self.field}. Use this "
                f"instead of asking for it by voice; the typed value arrives in "
                f"global_data.{self.gd_key}, then call {self.confirm_tool} to read it back."
            ),
            parameters={},
            handler=self._open_handler,
        )
        self.define_tool(
            name=self.confirm_tool,
            description=(
                f"Read back the {self.field} the caller typed (from global_data.{self.gd_key}) and "
                f"confirm it. Reopens the keypad if the value is missing or invalid. Call this after "
                f"{self.request_tool}, never before the value has been typed."
            ),
            parameters={},
            handler=self._confirm_handler,
        )

    # ------------------------------------------------------------------ #
    # Handlers
    # ------------------------------------------------------------------ #

    def _open_handler(
        self, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        """Speak the open prompt, reveal the keypad, and park until the value is typed."""
        return self._open(self._lang(raw_data))

    def _confirm_handler(
        self, args: dict[str, Any], raw_data: dict[str, Any]
    ) -> FunctionResult:
        """Validate the typed value; reopen on missing/invalid, else read it back to confirm."""
        lang = self._lang(raw_data)
        global_data = (
            raw_data.get("global_data", {}) if isinstance(raw_data, dict) else {}
        )
        value = str(global_data.get(self.gd_key) or "").strip()
        if not value or not validate_input(value, self.input_type):
            return self._open(lang, spoken=self._pick(self.invalid_prompt, lang))
        spoken = self._spoken_value(value, lang)
        return FunctionResult(
            f'The caller TYPED this on screen; read it back EXACTLY as "{spoken}" '
            "(do not voice any @ or dot symbols, and do not change it), then ask if it is "
            f"correct. On their YES, proceed with the value {value!r}. If it is wrong, call "
            f"{self.request_tool} to reopen the keypad so they re-type it; never ask for it by voice."
        )

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    def _open(self, lang: str, spoken: str | None = None) -> FunctionResult:
        """Open (or reopen) the keypad: speak ``spoken`` (default: the open prompt), emit the
        input-request user-event so the app focuses the field, and park for the typed value."""
        return (
            FunctionResult(
                spoken if spoken is not None else self._pick(self.open_prompt, lang)
            )
            .swml_user_event(
                input_request_payload(
                    self.gd_key,
                    label=self._pick(self.field_label, lang),
                    input_type=self.input_type,
                )
            )
            .wait_for_user(answer_first=True)
        )

    def _spoken_value(self, value: str, lang: str) -> str:
        """Read-back form: an email said as words, anything else spelled out so it is unambiguous."""
        v = get_verbalizer(lang)
        if self.input_type == "email":
            return v.email(value)
        return v.spell(value)

    @staticmethod
    def _lang(raw_data: dict[str, Any]) -> str:
        global_data = (
            raw_data.get("global_data", {}) if isinstance(raw_data, dict) else {}
        )
        return str(global_data.get("language") or _DEFAULT_LANG)

    def _pick(self, mapping: dict[str, str], lang: str) -> str:
        """Resolve a per-language map for the call language; fall back to English, then any value."""
        return (
            mapping.get(lang)
            or mapping.get(_DEFAULT_LANG)
            or (next(iter(mapping.values())) if mapping else "")
        )

    def get_hints(self) -> list[str]:
        """No ASR hints: the value is typed on the keypad, not spoken, so STT never sees it."""
        return []

    def get_prompt_sections(self) -> list[dict[str, Any]]:
        """Tell the model to route this field through the keypad, never voice."""
        return [
            {
                "title": f"Typed input: {self.field}",
                "body": (
                    f"To collect the caller's {self.field}, do NOT ask for it by voice. Call "
                    f"{self.request_tool} to open the on-screen keypad; the caller types it and the "
                    f"value arrives in global_data.{self.gd_key}. Then call {self.confirm_tool} to "
                    "read it back and confirm. If it is wrong, call the request tool again to reopen."
                ),
            }
        ]
