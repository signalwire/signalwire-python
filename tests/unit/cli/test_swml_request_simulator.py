"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
The request body ``swaig-test --dump-swml`` fabricates is the one the engine sends.

The oracle is the engine-derived ``webhook_request`` section of porting-sdk's
``combined-specs/swml.yaml`` (mod_infrastructure derives it from the C functions that
build the body the engine POSTs to a SWML webhook), converted to a JSON Schema by
porting-sdk's ``scripts/swml_webhook_request_shapes.py`` — the same reader the type
generator uses for ``swml_webhooks_types_generated``. The schema is closed where the
engine is closed, so a fabricated key the engine never writes is a failure here, not
a tolerated extra.

Negative controls prove the schema has teeth on exactly the shapes the simulator used
to fabricate: ``call.state`` instead of ``call.call_state``, and ``headers`` as an
object instead of an array of ``{name, value}``.
"""

import argparse
import copy
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import jsonschema_rs
import pytest

from signalwire.cli.simulation.data_generation import (
    CALL_TYPES,
    generate_fake_swml_post_data,
)
from signalwire.cli.simulation.data_overrides import (
    apply_convenience_mappings,
    apply_overrides,
)


def _porting_sdk() -> Path:
    """The adjacent ``porting-sdk`` checkout (same adjacency rule as the mock harness).

    Fails loudly rather than skipping: without the engine-derived section there is no
    oracle, and a skipped test would read as a pass."""
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        candidate = parent.parent / "porting-sdk"
        if (candidate / "scripts" / "swml_webhook_request_shapes.py").is_file():
            return candidate
    pytest.fail(
        "porting-sdk (with scripts/swml_webhook_request_shapes.py) is not adjacent — "
        "clone it next to signalwire-python"
    )


def _shapes_module(psdk: Path) -> ModuleType:
    path = psdk / "scripts" / "swml_webhook_request_shapes.py"
    spec = importlib.util.spec_from_file_location("swml_webhook_request_shapes", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def engine_schema() -> dict[str, Any]:
    psdk = _porting_sdk()
    schema: dict[str, Any] = _shapes_module(psdk).json_schema(psdk)
    return schema


@pytest.fixture(scope="module")
def validator(engine_schema: dict[str, Any]) -> jsonschema_rs.Draft202012Validator:
    return jsonschema_rs.Draft202012Validator(engine_schema)


def _errors(validator: jsonschema_rs.Draft202012Validator, body: Any) -> list[str]:
    return [str(e) for e in validator.iter_errors(body)]


def _cli_args(**overrides: Any) -> argparse.Namespace:
    """The attributes ``swaig-test``'s parser gives the convenience mappings."""
    base: dict[str, Any] = {
        "call_id": None,
        "project_id": None,
        "space_id": None,
        "call_type": "webrtc",
        "call_direction": "inbound",
        "call_state": "created",
        "from_number": None,
        "to_extension": None,
        "user_vars": None,
        "query_params": None,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def _variant_arm(engine_schema: dict[str, Any], call_type: str) -> dict[str, Any]:
    for arm in engine_schema["properties"]["call"]["oneOf"]:
        if arm["properties"].get("type", {}).get("const") == call_type:
            return dict(arm)
    raise AssertionError(f"no {call_type!r} variant in the engine schema")


class TestSimulatedBodyMatchesTheEngine:
    @pytest.mark.parametrize("call_type", CALL_TYPES)
    @pytest.mark.parametrize("direction", ["inbound", "outbound"])
    def test_default_body_validates(
        self,
        validator: jsonschema_rs.Draft202012Validator,
        call_type: str,
        direction: str,
    ) -> None:
        body = generate_fake_swml_post_data(
            call_type=call_type, call_direction=direction, call_state="created"
        )
        assert _errors(validator, body) == []

    @pytest.mark.parametrize("call_type", CALL_TYPES)
    def test_body_after_cli_mappings_validates(
        self, validator: jsonschema_rs.Draft202012Validator, call_type: str
    ) -> None:
        # The exact pipeline handle_dump_swml runs: generate, convenience-map, override.
        args = _cli_args(
            call_type=call_type,
            call_state="answered",
            call_direction="outbound",
            call_id="my-call",
            project_id="my-project",
            space_id="my-space",
            from_number="+15551234567",
            to_extension="support",
            user_vars='{"tier": "gold"}',
        )
        body = generate_fake_swml_post_data(
            call_type=args.call_type,
            call_direction=args.call_direction,
            call_state=args.call_state,
        )
        body = apply_convenience_mappings(body, args)
        body = apply_overrides(body, ["call.segment_id=seg-1"], [])
        assert _errors(validator, body) == []
        call = body["call"]
        assert call["call_id"] == "my-call"
        assert call["call_state"] == "answered"
        assert call["direction"] == "outbound"
        assert call["project_id"] == "my-project"
        assert call["space_id"] == "my-space"
        assert call["from"] == "+15551234567"
        assert body["vars"]["userVariables"] == {"tier": "gold"}
        if call_type == "phone":
            # A phone call carries each number twice; the mappings keep them in step.
            assert call["from_number"] == call["from"]
            assert call["to_number"] == call["to"]

    @pytest.mark.parametrize("call_type", CALL_TYPES)
    def test_body_carries_every_key_the_engine_always_writes(
        self, engine_schema: dict[str, Any], call_type: str
    ) -> None:
        body = generate_fake_swml_post_data(call_type=call_type)
        for key in engine_schema["required"]:
            assert key in body
        for key in _variant_arm(engine_schema, call_type)["required"]:
            assert key in body["call"], key

    @pytest.mark.parametrize("call_type", CALL_TYPES)
    def test_body_carries_no_key_the_engine_never_writes(
        self, engine_schema: dict[str, Any], call_type: str
    ) -> None:
        body = generate_fake_swml_post_data(call_type=call_type)
        assert set(body) <= set(engine_schema["properties"])
        arm = _variant_arm(engine_schema, call_type)
        assert set(body["call"]) <= set(arm["properties"])

    def test_sip_headers_are_name_value_objects(self) -> None:
        call = generate_fake_swml_post_data(call_type="sip")["call"]
        assert isinstance(call["headers"], list)
        assert call["headers"]
        for header in call["headers"]:
            assert set(header) == {"name", "value"}


class TestEngineSchemaRejectsTheOldShapes:
    """Negative controls: the schema the positive tests pass against is not vacuous."""

    def test_state_instead_of_call_state_is_rejected(
        self, validator: jsonschema_rs.Draft202012Validator
    ) -> None:
        body = generate_fake_swml_post_data(call_type="webrtc")
        assert _errors(validator, body) == []
        broken = copy.deepcopy(body)
        broken["call"]["state"] = broken["call"].pop("call_state")
        assert _errors(validator, broken) != []

    def test_object_form_headers_are_rejected(
        self, validator: jsonschema_rs.Draft202012Validator
    ) -> None:
        body = generate_fake_swml_post_data(call_type="sip")
        assert _errors(validator, body) == []
        broken = copy.deepcopy(body)
        broken["call"]["headers"] = {"User-Agent": "Test-SIP-Client/1.0.0"}
        assert _errors(validator, broken) != []

    def test_an_invented_call_key_is_rejected(
        self, validator: jsonschema_rs.Draft202012Validator
    ) -> None:
        body = generate_fake_swml_post_data(call_type="phone")
        broken = copy.deepcopy(body)
        broken["call"]["timeout"] = 30
        assert _errors(validator, broken) != []

    def test_missing_vars_is_rejected(
        self, validator: jsonschema_rs.Draft202012Validator
    ) -> None:
        body = generate_fake_swml_post_data()
        broken = copy.deepcopy(body)
        del broken["vars"]
        assert _errors(validator, broken) != []

    def test_phone_only_keys_on_a_webrtc_call_are_rejected(
        self, validator: jsonschema_rs.Draft202012Validator
    ) -> None:
        body = generate_fake_swml_post_data(call_type="webrtc")
        broken = copy.deepcopy(body)
        broken["call"]["from_number"] = "+15551234567"
        assert _errors(validator, broken) != []

    def test_call_state_outside_the_engine_enum_is_rejected(
        self, validator: jsonschema_rs.Draft202012Validator
    ) -> None:
        body = generate_fake_swml_post_data(call_state="test")
        assert _errors(validator, body) != []


class TestConvenienceMappingsDoNotFabricateACall:
    def test_a_body_without_a_call_object_gets_none(self) -> None:
        # A SWAIG function request carries no `call` object; the call.* mappings
        # (default --call-state included) must not invent one.
        body = apply_convenience_mappings({"function": "f"}, _cli_args(call_id="c1"))
        assert "call" not in body
        assert body["call_id"] == "c1"

    def test_input_body_is_not_mutated(self) -> None:
        body = generate_fake_swml_post_data()
        before = copy.deepcopy(body)
        apply_convenience_mappings(body, _cli_args(call_state="answered"))
        assert body == before


def test_unknown_call_type_is_refused() -> None:
    with pytest.raises(ValueError, match="call_type"):
        generate_fake_swml_post_data(call_type="pstn")
