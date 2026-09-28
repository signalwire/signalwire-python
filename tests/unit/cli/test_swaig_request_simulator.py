"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
The body ``swaig-test --fake-full-data`` fabricates is the one the engine sends.

The oracle is porting-sdk's vendored ``swaig-specs/swaig-request.yaml`` (mod_openai
derives it from ``actions.c::execute_user_function``, the function that builds the body
the engine POSTs to a SWAIG function's ``web_hook_url``). Its ``SwaigRequest`` schema
lists that function's complete field set, so the test validates against it CLOSED at the
root: a key the engine never writes is a failure, not a tolerated extra.

Negative controls prove the schema has teeth: an invented key (the simulator used to add
``call``, ``vars``, ``meta_data.application``-style envelopes and more) is rejected, and
so is a body missing a key the engine always writes.
"""

import argparse
import copy
from pathlib import Path
from typing import Any

import jsonschema_rs
import pytest
import yaml

from signalwire.cli.simulation.data_generation import generate_comprehensive_post_data
from signalwire.cli.simulation.data_overrides import (
    apply_convenience_mappings,
    apply_overrides,
)


def _swaig_request_spec() -> Path:
    """The adjacent porting-sdk's vendored SWAIG request spec (fails loud, never skips)."""
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        candidate = parent.parent / "porting-sdk" / "swaig-specs" / "swaig-request.yaml"
        if candidate.is_file():
            return candidate
    pytest.fail(
        "porting-sdk (with swaig-specs/swaig-request.yaml) is not adjacent — clone it "
        "next to signalwire-python"
    )


@pytest.fixture(scope="module")
def engine_schema() -> dict[str, Any]:
    doc = yaml.safe_load(_swaig_request_spec().read_text(encoding="utf-8"))
    schema: dict[str, Any] = copy.deepcopy(doc["components"]["schemas"]["SwaigRequest"])
    # The spec's properties ARE execute_user_function's complete field set; close the
    # root so a fabricated key fails instead of passing as an open-shape extra.
    schema["additionalProperties"] = False
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    return schema


@pytest.fixture(scope="module")
def validator(engine_schema: dict[str, Any]) -> jsonschema_rs.Draft202012Validator:
    return jsonschema_rs.Draft202012Validator(engine_schema)


def _errors(validator: jsonschema_rs.Draft202012Validator, body: Any) -> list[str]:
    return [str(e) for e in validator.iter_errors(body)]


def _body(**kw: Any) -> dict[str, Any]:
    return generate_comprehensive_post_data("get_weather", {"city": "Austin"}, **kw)


class TestSimulatedBodyMatchesTheEngine:
    def test_full_body_validates(
        self, validator: jsonschema_rs.Draft202012Validator
    ) -> None:
        assert _errors(validator, _body()) == []

    def test_body_after_cli_mappings_validates(
        self, validator: jsonschema_rs.Draft202012Validator
    ) -> None:
        # The exact pipeline the --exec path runs: generate, convenience-map, override.
        args = argparse.Namespace(
            call_id="my-call",
            project_id=None,
            space_id=None,
            call_type="webrtc",
            call_direction="inbound",
            call_state="created",
            from_number=None,
            to_extension=None,
            user_vars=None,
            query_params=None,
        )
        body = apply_convenience_mappings(_body(), args)
        body = apply_overrides(body, ["app_name=my-app"], [])
        assert _errors(validator, body) == []
        assert body["call_id"] == "my-call"
        assert body["app_name"] == "my-app"
        assert "call" not in body

    def test_body_carries_every_key_the_engine_always_writes(
        self, engine_schema: dict[str, Any]
    ) -> None:
        body = _body()
        for key in engine_schema["required"]:
            assert key in body, key

    def test_function_schema_and_description_are_carried(
        self, validator: jsonschema_rs.Draft202012Validator
    ) -> None:
        desc = {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        }
        body = _body(description="Look up the weather", argument_desc=desc)
        assert _errors(validator, body) == []
        assert body["argument_desc"] == desc
        assert body["description"] == "Look up the weather"
        assert body["argument"]["parsed"] == [{"city": "Austin"}]

    def test_data_map_and_error_only_keys_are_not_fabricated(self) -> None:
        body = _body()
        for key in ("args", "input", "fatal_error", "error_reason"):
            assert key not in body


class TestEngineSchemaRejectsTheOldShapes:
    """Negative controls: the schema the positive tests pass against is not vacuous."""

    @pytest.mark.parametrize(
        "key", ["call", "vars", "params", "prompt_vars", "swml_env", "http_method"]
    )
    def test_an_invented_key_is_rejected(
        self, validator: jsonschema_rs.Draft202012Validator, key: str
    ) -> None:
        body = _body()
        assert _errors(validator, body) == []
        body[key] = {}
        assert _errors(validator, body) != []

    @pytest.mark.parametrize("key", ["function", "argument", "call_id", "version"])
    def test_a_missing_required_key_is_rejected(
        self, validator: jsonschema_rs.Draft202012Validator, key: str
    ) -> None:
        body = _body()
        del body[key]
        assert _errors(validator, body) != []

    def test_a_scalar_parsed_argument_is_rejected(
        self, validator: jsonschema_rs.Draft202012Validator
    ) -> None:
        body = _body()
        body["argument"]["parsed"] = ["Austin"]
        assert _errors(validator, body) != []
