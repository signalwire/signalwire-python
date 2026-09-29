"""
The simulator's fmt_ph helper, as the platform formats a phone number.

The platform formats with libphonenumber in the national format, assuming the
US, and gives INVALID NUMBER for a number it can't validate. The simulator
formatted only North American numbers and left anything else as it was,
silently. With the phonenumbers package it now does what the platform does;
without it, it says on stderr when it leaves a value unformatted.
"""

import sys

import pytest

from signalwire.cli.execution.datamap_exec import simple_template_expand


def _fmt(value: str) -> str:
    return simple_template_expand("${fmt_ph:args.phone}", {"args": {"phone": value}})


class TestWithoutPhonenumbers:
    @pytest.fixture(autouse=True)
    def _no_phonenumbers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(sys.modules, "phonenumbers", None)

    def test_a_north_american_number_is_formatted(self) -> None:
        assert _fmt("+1 202 555 0143") == "(202) 555-0143"

    def test_another_value_is_left_with_a_note(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert _fmt("12") == "12"
        assert "INVALID NUMBER" in capsys.readouterr().err


class TestWithPhonenumbers:
    @pytest.fixture(autouse=True)
    def _phonenumbers(self) -> None:
        pytest.importorskip("phonenumbers")

    def test_an_invalid_number_is_invalid_number(self) -> None:
        assert _fmt("12") == "INVALID NUMBER"
        assert _fmt("not a number") == "INVALID NUMBER"

    def test_a_valid_number_is_in_the_national_format(self) -> None:
        assert _fmt("+1 650 253 0000") == "(650) 253-0000"
        assert _fmt("+44 20 7031 3000") == "020 7031 3000"
