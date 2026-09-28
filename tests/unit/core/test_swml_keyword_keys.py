"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Generated TypedDicts whose wire key is a Python keyword or not an identifier.

A class-form TypedDict cannot declare ``from``, ``else`` or ``nomatch-output``, so the
generator (porting-sdk/scripts/generate_python_rest_types.py) emits those declarations
in the functional form, ``X = TypedDict("X", {...}, total=False)``, and the key is
typed instead of left out.

This module is in the TYPECHECK gate's scope (mypy --strict over ``tests``, which
includes ``warn_unused_ignores``). The ``# type: ignore[<code>]`` below is a NEGATIVE
CONTROL: it marks a call mypy must reject, and if the typing stopped rejecting it the
ignore would be unused and the gate would fail. Calls without an ignore must
type-check as written, including the old-style calls in TestCompatibility.
"""

import typing
from typing import Any
from unittest.mock import Mock

import pytest

from signalwire.core import swml_verbs_generated as verbs
from signalwire.core.agent_base import AgentBase
from signalwire.core.swml_builder import SWMLBuilder
from signalwire.core.swml_service import SWMLService
from signalwire.rest.namespaces import swml_webhooks_types_generated as webhooks


def _builder() -> SWMLBuilder:
    return SWMLBuilder(SWMLService(name="keyword_keys", schema_validation=False))


def _main(builder: SWMLBuilder) -> list[Any]:
    main: list[Any] = builder.build()["sections"]["main"]
    return main


class TestConnectFrom:
    def test_from_key_type_checks_and_renders(self) -> None:
        builder = _builder()
        builder.connect({"from": "+15551230000", "to": "+15554560000", "timeout": 30})
        assert _main(builder) == [
            {"connect": {"from": "+15551230000", "to": "+15554560000", "timeout": 30}}
        ]

    def test_wrong_from_type_rejected_statically(self) -> None:
        builder = _builder()
        builder.connect({"from": 15551230000, "to": "+15554560000"})  # type: ignore[arg-type]  # from is a string
        assert _main(builder) == [
            {"connect": {"from": 15551230000, "to": "+15554560000"}}
        ]

    def test_other_keyword_keys_type_check(self) -> None:
        cond: verbs.CondItem = {"when": "vars.x == 1", "then": [], "else": []}
        pronounce: verbs.AiPronounceItem = {"replace": "SW", "with": "SignalWire"}
        expression: verbs.Expression = {
            "string": "x",
            "pattern": ".*",
            "nomatch-output": {},
        }
        assert cond["else"] == [] and pronounce["with"] == "SignalWire"
        assert "nomatch-output" in expression


class TestFunctionalFormAtRuntime:
    """The functional form is the same runtime object the class form was: a TypedDict
    type with the same keys (plus the keyword ones), the same totality, and the same
    docstring."""

    def test_keys_totality_and_docstring(self) -> None:
        cfg = verbs.ConnectConfig
        assert {"from", "to", "timeout", "from_name"} <= set(cfg.__annotations__)
        assert cfg.__total__ is False
        assert cfg.__doc__ is not None and cfg.__doc__.startswith("Dial a SIP URI")
        assert typing.is_typeddict(cfg)

    def test_webhook_request_from_key_declared(self) -> None:
        # Required[...] rides in the quoted annotation, as it did in the class form
        # (the module's ``from __future__ import annotations`` made those strings too),
        # so it is a static fact for the checker, not a runtime one.
        annotations = webhooks.SwmlRequestCallPhone.__annotations__
        assert "from" in annotations and "call_id" in annotations

    def test_no_key_left_as_a_comment(self) -> None:
        # The generator no longer drops a key to a "# non-identifier field" comment.
        import inspect

        for module in (verbs, webhooks):
            assert "non-identifier field" not in inspect.getsource(module)


class TestCompatibility:
    """Old-style calls: plain dicts and arbitrary kwargs.

    Under the strict entry-point typing these calls are REJECTED (each ignore below is
    used), which is what makes that typing a breaking change. They still run
    unchanged."""

    def test_ai_accepts_the_old_style_kwargs(self) -> None:
        builder = _builder()
        builder.ai(prompt_text="x", temperature=0.7, max_tokens=150)  # type: ignore[call-arg]  # BREAKING: rejected by _AiConfigKwargs
        assert _main(builder) == [
            {"ai": {"prompt": {"text": "x"}, "temperature": 0.7, "max_tokens": 150}}
        ]

    def test_params_setters_accept_a_plain_dict(self) -> None:
        with pytest.MonkeyPatch().context() as m:
            m.setattr("signalwire.core.agent_base.uvicorn", Mock())
            agent = AgentBase(
                name="keyword_keys", schema_validation=False, use_pom=False
            )
        params: dict[str, Any] = {"end_of_speech_timeout": 700, "custom_key": "v"}
        agent.set_params(params)  # type: ignore[arg-type]  # BREAKING: dict[str, Any] is not AiParams
        agent.set_param("any_key", 1)  # type: ignore[call-overload]  # BREAKING: not an AiParams key
        assert agent._params == {
            "end_of_speech_timeout": 700,
            "custom_key": "v",
            "any_key": 1,
        }

    def test_connect_accepts_the_keys_it_accepted_before(self) -> None:
        builder = _builder()
        builder.connect({"to": "+15554560000", "from_name": "SignalWire"})
        assert _main(builder) == [
            {"connect": {"to": "+15554560000", "from_name": "SignalWire"}}
        ]
