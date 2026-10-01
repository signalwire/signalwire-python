"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The hand-written SWMLBuilder verb methods accept every public parameter the spec
publishes for their verb.

``answer``/``hangup``/``play`` are written by hand (richer ergonomics) instead of being
installed from schema.json, so nothing kept their parameter lists current with the
spec: ``answer`` lacked ``username``/``password`` and ``play`` lacked
``loop``/``status_url`` — all published in schema.json (the ARS output of the engine's
swml_schema.c allowlist). The completeness test reads the parameter set FROM the
bundled schema, so a parameter the spec gains later fails here until it is added.

Every emission test builds on a strict service (schema validation on), so the verb is
also accepted by the engine-derived schema, not just echoed back.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest

from signalwire.core.swml_builder import SWMLBuilder
from signalwire.core.swml_service import SWMLService
from signalwire.utils.schema_utils import SchemaValidationError

# Hand-written verb method -> the verb it emits. `ai` takes **kwargs (every key is
# reachable) and `say` is sugar over `play`, so neither has a fixed parameter list.
HAND_WRITTEN = {"answer": "answer", "hangup": "hangup", "play": "play"}

# Method parameters that are ergonomic spellings of a spec parameter, not extras.
RENAMED: dict[str, dict[str, str]] = {}


def _strict() -> SWMLService:
    return SWMLService(name="spec-params", route="/spec-params", schema_validation=True)


def _main(builder: SWMLBuilder) -> list[dict[str, Any]]:
    main: list[dict[str, Any]] = builder.build()["sections"]["main"]
    return main


@pytest.mark.parametrize("method", sorted(HAND_WRITTEN))
def test_hand_written_verb_accepts_every_public_spec_param(method: str) -> None:
    service = _strict()
    assert service.schema_utils is not None
    spec = service.schema_utils._verb_top_level_property_names(HAND_WRITTEN[method])
    assert spec, f"schema.json publishes no object-form params for {method}"
    params = set(inspect.signature(getattr(SWMLBuilder, method)).parameters) - {"self"}
    accepted = {RENAMED.get(method, {}).get(p, p) for p in params}
    missing = sorted(set(spec) - accepted)
    assert not missing, f"SWMLBuilder.{method} lacks spec params {missing}"


def test_answer_emits_sip_auth() -> None:
    builder = SWMLBuilder(_strict())
    builder.answer(
        max_duration=3600,
        codecs="PCMU,OPUS",
        username="user123",
        password="securepassword",
    )
    assert _main(builder) == [
        {
            "answer": {
                "max_duration": 3600,
                "codecs": "PCMU,OPUS",
                "username": "user123",
                "password": "securepassword",
            }
        }
    ]


def test_answer_accepts_codec_list_form() -> None:
    builder = SWMLBuilder(_strict())
    builder.answer(codecs=["PCMU", "OPUS"])
    assert _main(builder) == [{"answer": {"codecs": ["PCMU", "OPUS"]}}]


def test_answer_without_args_is_empty_object() -> None:
    builder = SWMLBuilder(_strict())
    builder.answer()
    assert _main(builder) == [{"answer": {}}]


def test_play_emits_loop_and_status_url() -> None:
    builder = SWMLBuilder(_strict())
    builder.play(
        url="https://example.com/hold.mp3",
        loop=3,
        status_url="https://example.com/play-status",
    )
    assert _main(builder) == [
        {
            "play": {
                "url": "https://example.com/hold.mp3",
                "loop": 3,
                "status_url": "https://example.com/play-status",
            }
        }
    ]


def test_play_rejects_a_negative_loop_via_the_schema() -> None:
    """`loop` is `minimum: 0` in the spec; the strict service's schema says so."""
    builder = SWMLBuilder(_strict())
    with pytest.raises(SchemaValidationError, match=r"-1|minimum"):
        builder.play(url="https://example.com/a.mp3", loop=-1)
