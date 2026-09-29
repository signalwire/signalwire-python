"""
pay() and join_conference() send the types and ranges the platform reads.

pay() sends timeout, max_attempts, min_postal_code_length, security_code and
a boolean postal_code as strings: the platform's SWML validation refuses a
security_code or postal_code that isn't a string, and its pay request reads
all five as strings. The bundled schema's integer and boolean types for them
are wrong, so these documents aren't checked against it. pay() checks each
value's type before sending it.
join_conference() defaulted max_participants to 250, left out an explicit
250 so the platform's default applied, and refused values above 250, which
the platform accepts: it requires 2 or more and sets no upper limit, and
reads it as a number.
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


def _pay(result: FunctionResult) -> Any:
    main = result.action[0]["SWML"]["sections"]["main"]
    return next(v["pay"] for v in main if "pay" in v)


class TestPayTypes:
    """The forms the platform's SWML validation and pay request accept."""

    def test_defaults_are_strings(self) -> None:
        pay = _pay(FunctionResult().pay("https://pay.example.com/c"))
        assert (
            pay["timeout"], pay["max_attempts"], pay["min_postal_code_length"],
            pay["security_code"], pay["postal_code"],
        ) == ("5", "1", "0", "true", "true")

    def test_postal_code_string_is_the_code(self) -> None:
        result = FunctionResult().pay("https://pay.example.com/c", postal_code="90210")
        assert _pay(result)["postal_code"] == "90210"

    def test_postal_code_false_is_the_string_false(self) -> None:
        result = FunctionResult().pay("https://pay.example.com/c", postal_code=False)
        assert _pay(result)["postal_code"] == "false"

    def test_numeric_strings_are_converted(self) -> None:
        # Strings aren't in the annotated types, so they're passed as Any
        strings: dict[str, Any] = {
            "timeout": "7",
            "max_attempts": "2",
            "security_code": "False",
        }
        result = FunctionResult().pay("https://pay.example.com/c", **strings)
        pay = _pay(result)
        assert (pay["timeout"], pay["max_attempts"], pay["security_code"]) == (
            "7",
            "2",
            "false",
        )

    def test_swml_variables_pass_through(self) -> None:
        variables: dict[str, Any] = {
            "timeout": "${pay_timeout}",
            "security_code": "%{needs_cvv}",
        }
        result = FunctionResult().pay("https://pay.example.com/c", **variables)
        pay = _pay(result)
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
    def test_two_or_more_is_accepted(self, value: int) -> None:
        result = FunctionResult().join_conference("room", max_participants=value)
        assert _verb(result, "join_conference")["max_participants"] == value

    def test_there_is_no_upper_limit(self) -> None:
        # The bundled schema caps max_participants at 100000, but the platform
        # sets no upper limit, so this isn't checked against the schema
        result = FunctionResult().join_conference("room", max_participants=250000)
        verb = result.action[0]["SWML"]["sections"]["main"][0]["join_conference"]
        assert verb["max_participants"] == 250000

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

    @pytest.mark.parametrize("value", [1, 0, "many", 2.5])
    def test_fewer_than_two_or_not_an_integer_is_refused(self, value: Any) -> None:
        with pytest.raises(ValueError) as excinfo:
            FunctionResult().join_conference("room", max_participants=value)
        assert str(excinfo.value) == (
            f"max_participants must be an integer of at least 2, got {value!r}"
        )
