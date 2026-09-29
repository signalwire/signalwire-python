"""
pay() and join_conference() send the types and ranges the SWML schema defines.

pay() sent timeout, max_attempts, min_postal_code_length and security_code
(and a boolean postal_code) as strings, which the schema's integer and
boolean types reject. join_conference() defaulted max_participants to 250
and left out an explicit 250, so the platform's default of 100000 applied,
and it refused values above 250 that the schema allows (2 to 100000).
"""

from typing import Any

import pytest

from signalwire.core.function_result import FunctionResult
from signalwire.utils.schema_utils import SchemaUtils


def _verb(result: FunctionResult, name: str) -> Any:
    swml = result.action[0]["SWML"]
    ok, errors = SchemaUtils().validate_document(swml)
    assert ok, errors
    return next(v[name] for v in swml["sections"]["main"] if name in v)


class TestPayTypes:
    def test_defaults_are_native_and_valid(self) -> None:
        pay = _verb(FunctionResult().pay("https://pay.example.com/c"), "pay")
        assert pay["timeout"] == 5 and type(pay["timeout"]) is int
        assert pay["max_attempts"] == 1 and type(pay["max_attempts"]) is int
        assert pay["min_postal_code_length"] == 0
        assert type(pay["min_postal_code_length"]) is int
        assert pay["security_code"] is True
        assert pay["postal_code"] is True

    def test_postal_code_string_is_the_code(self) -> None:
        result = FunctionResult().pay("https://pay.example.com/c", postal_code="90210")
        assert _verb(result, "pay")["postal_code"] == "90210"

    def test_numeric_strings_are_converted(self) -> None:
        # Strings aren't in the annotated types, so they're passed as Any
        strings: dict[str, Any] = {
            "timeout": "7",
            "max_attempts": "2",
            "security_code": "False",
        }
        result = FunctionResult().pay("https://pay.example.com/c", **strings)
        pay = _verb(result, "pay")
        assert (pay["timeout"], pay["max_attempts"], pay["security_code"]) == (
            7,
            2,
            False,
        )

    def test_swml_variables_pass_through(self) -> None:
        variables: dict[str, Any] = {
            "timeout": "${pay_timeout}",
            "security_code": "%{needs_cvv}",
        }
        result = FunctionResult().pay("https://pay.example.com/c", **variables)
        pay = _verb(result, "pay")
        assert pay["timeout"] == "${pay_timeout}"
        assert pay["security_code"] == "%{needs_cvv}"

    @pytest.mark.parametrize(
        ("kwargs", "message"),
        [
            ({"timeout": "soon"}, "timeout must be an integer, got 'soon'"),
            ({"max_attempts": 1.5}, "max_attempts must be an integer, got 1.5"),
            ({"max_attempts": True}, "max_attempts must be an integer, got True"),
            ({"security_code": "yes"}, "security_code must be a boolean, got 'yes'"),
            ({"security_code": 1}, "security_code must be a boolean, got 1"),
        ],
    )
    def test_wrong_types_are_refused(
        self, kwargs: dict[str, Any], message: str
    ) -> None:
        with pytest.raises(ValueError) as excinfo:
            FunctionResult().pay("https://pay.example.com/c", **kwargs)
        assert str(excinfo.value) == message


class TestJoinConferenceMaxParticipants:
    def test_explicit_250_is_sent(self) -> None:
        result = FunctionResult().join_conference("room", max_participants=250)
        assert _verb(result, "join_conference") == {
            "name": "room",
            "max_participants": 250,
        }

    @pytest.mark.parametrize("value", [2, 251, 1000, 100000])
    def test_schema_range_is_accepted(self, value: int) -> None:
        result = FunctionResult().join_conference("room", max_participants=value)
        assert _verb(result, "join_conference")["max_participants"] == value

    def test_left_out_by_default(self) -> None:
        result = FunctionResult().join_conference("room", muted=True)
        assert _verb(result, "join_conference") == {"name": "room", "muted": True}

    def test_default_keeps_the_simple_form(self) -> None:
        swml = FunctionResult().join_conference("room").action[0]["SWML"]
        assert swml["sections"]["main"] == [{"join_conference": "room"}]

    def test_swml_variable_passes_through(self) -> None:
        room_size: Any = "${room_size}"
        result = FunctionResult().join_conference("room", max_participants=room_size)
        assert _verb(result, "join_conference")["max_participants"] == "${room_size}"

    @pytest.mark.parametrize("value", [1, 100001, "many", 2.5])
    def test_outside_the_schema_is_refused(self, value: Any) -> None:
        with pytest.raises(ValueError) as excinfo:
            FunctionResult().join_conference("room", max_participants=value)
        assert str(excinfo.value) == (
            f"max_participants must be an integer from 2 to 100000, got {value!r}"
        )
