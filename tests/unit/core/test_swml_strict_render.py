"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

SWML strict-render contract (Wave-2 P#5).

Building / rendering an SWML document with a MISSHAPEN config, an UNKNOWN verb,
or a MISSPELLED key must RAISE a clear error — not silently drop or accept it.
The r5 dogfood reports named a "silent-drop family": unknown verbs accepted,
misspelled verb-config keys swallowed, and dangling SWAIG step-function
references emitted with no warning.

Most of this contract is already enforced at the ``add_verb`` choke point via
jsonschema-rs full-document validation (unknown verb, misspelled/unknown keys
on the closed verbs, wrong-typed config). The two gaps this suite pins RED
first, then closes:

  GAP 1 — the ``ai`` verb has a specialized ``AIVerbHandler`` whose hand-rolled
  ``validate_config`` only checked ``prompt``/``SWAIG`` shape, so it SILENTLY
  ACCEPTED unknown/misspelled top-level ``ai`` keys (``temperatur``, ``zzz``)
  that every schema-validated verb rejects. The AI object schema itself is
  closed (``unevaluatedProperties`` disallows extras); the handler simply
  wasn't consulting it. (The ``params`` sub-object stays intentionally open —
  LLM tuning params vary — so a key *inside* ``params`` is not a misspelling.)

  GAP 2 — ``ContextBuilder.validate()`` validated dangling ``valid_steps`` /
  ``valid_contexts`` references but NOT a step's ``set_functions([...])``
  references against the agent's registered SWAIG tool set + reserved native
  tools. A step whitelisting a nonexistent function (``get_datetime`` when the
  registered tool is ``get_current_time``) rendered a dangling reference
  silently.
"""

from typing import Any

import pytest

from signalwire.core.agent_base import AgentBase
from signalwire.core.swml_service import SWMLService
from signalwire.utils.schema_utils import SchemaValidationError


def _strict_service() -> SWMLService:
    """A SWMLService with schema validation ENABLED (the default in production;
    the shared ``mock_swml_service`` fixture disables it, which is why these
    tests build their own)."""
    return SWMLService(name="strict", route="/strict", schema_validation=True)


# ---------------------------------------------------------------------------
# Baseline: the already-enforced parts of the contract (regression guards so a
# future refactor can't quietly loosen them).
# ---------------------------------------------------------------------------


class TestUnknownVerbRejected:
    def test_unknown_verb_raises(self) -> None:
        svc = _strict_service()
        with pytest.raises(SchemaValidationError) as exc:
            svc.add_verb("foobar", {})
        assert "foobar" in str(exc.value)

    def test_good_verb_renders(self) -> None:
        svc = _strict_service()
        assert svc.add_verb("answer", {"max_duration": 5}) is True


class TestMisspelledKeyRejected:
    @pytest.mark.parametrize(
        ("verb", "config"),
        [
            ("answer", {"maxduration": 5}),  # misspelled max_duration
            ("answer", {"wibble": 1}),  # unknown key
            ("play", {"urlz": ["say:hi"]}),  # misspelled urls
            ("play", {"url": "say:hi", "foo": 1}),  # valid + unknown extra
            ("record", {"formatt": "wav"}),  # misspelled format
            ("prompt", {"txt": "hi"}),  # misspelled text
        ],
    )
    def test_misspelled_or_unknown_key_raises(self, verb: str, config: dict[str, Any]) -> None:
        svc = _strict_service()
        with pytest.raises(SchemaValidationError):
            svc.add_verb(verb, config)

    def test_wrong_typed_config_raises(self) -> None:
        svc = _strict_service()
        with pytest.raises(SchemaValidationError):
            svc.add_verb("answer", {"max_duration": "notanumber"})


# ---------------------------------------------------------------------------
# GAP 1 — the ``ai`` verb must reject unknown/misspelled top-level keys like
# every other verb (was silently accepted by AIVerbHandler).
# ---------------------------------------------------------------------------


class TestAiVerbStrictKeys:
    def test_ai_good_config_renders(self) -> None:
        svc = _strict_service()
        assert svc.add_verb("ai", {"prompt": {"text": "hi"}}) is True

    def test_ai_good_config_with_swaig_renders(self) -> None:
        svc = _strict_service()
        assert (
            svc.add_verb(
                "ai",
                {"prompt": {"text": "hi"}, "SWAIG": {"functions": []}},
            )
            is True
        )

    def test_ai_misspelled_top_level_key_raises(self) -> None:
        svc = _strict_service()
        with pytest.raises(SchemaValidationError):
            svc.add_verb("ai", {"prompt": {"text": "hi"}, "temperatur": 0.5})

    def test_ai_unknown_top_level_key_raises(self) -> None:
        svc = _strict_service()
        with pytest.raises(SchemaValidationError):
            svc.add_verb("ai", {"prompt": {"text": "hi"}, "zzz": 1})

    def test_ai_missing_prompt_still_raises(self) -> None:
        # The handler's own prompt check must survive alongside the new
        # schema pass.
        svc = _strict_service()
        with pytest.raises(SchemaValidationError):
            svc.add_verb("ai", {"post_prompt": {"text": "bye"}})

    def test_ai_params_subobject_stays_open(self) -> None:
        # ``params`` is the deliberate open door for LLM tuning params; a key
        # inside it is NOT a misspelling and must render.
        svc = _strict_service()
        assert (
            svc.add_verb(
                "ai",
                {"prompt": {"text": "hi"}, "params": {"some_future_param": 1}},
            )
            is True
        )


# ---------------------------------------------------------------------------
# GAP 2 — a step's set_functions([...]) referencing a function that is neither
# a registered SWAIG tool nor a reserved native tool must raise (dangling
# function reference — r5 F3).
# ---------------------------------------------------------------------------


class TestDanglingStepFunctionReference:
    def _agent(self) -> AgentBase:
        return AgentBase(name="ctxagent", route="/ctx", schema_validation=True)

    def test_dangling_function_ref_raises(self) -> None:
        agent = self._agent()
        agent.define_tool(
            name="order_status",
            description="look up an order",
            parameters={},
            handler=lambda args, raw: None,
        )
        contexts = agent.define_contexts()
        support = contexts.add_context("default")
        step = support.add_step("help")
        step.set_text("help the caller")
        step.set_functions(["order_status", "get_datetime"])  # get_datetime dangles

        with pytest.raises(ValueError) as exc:
            contexts.to_dict()
        assert "get_datetime" in str(exc.value)

    def test_registered_function_ref_renders(self) -> None:
        agent = self._agent()
        agent.define_tool(
            name="order_status",
            description="look up an order",
            parameters={},
            handler=lambda args, raw: None,
        )
        contexts = agent.define_contexts()
        support = contexts.add_context("default")
        step = support.add_step("help")
        step.set_text("help the caller")
        step.set_functions(["order_status"])

        # No raise — the referenced function is registered.
        doc = contexts.to_dict()
        assert "default" in doc

    def test_reserved_native_tool_ref_allowed(self) -> None:
        # next_step / change_context are auto-injected natives; referencing them
        # explicitly must not be treated as dangling.
        agent = self._agent()
        contexts = agent.define_contexts()
        support = contexts.add_context("default")
        step = support.add_step("help")
        step.set_text("help the caller")
        step.set_functions(["next_step", "change_context"])

        doc = contexts.to_dict()
        assert "default" in doc

    def test_functions_none_and_empty_render(self) -> None:
        # "none" and [] are explicit disable-all — never dangling.
        value: str | list[str]
        for value in ("none", []):
            agent = self._agent()
            contexts = agent.define_contexts()
            support = contexts.add_context("default")
            step = support.add_step("help")
            step.set_text("help the caller")
            step.set_functions(value)
            doc = contexts.to_dict()
            assert "default" in doc
