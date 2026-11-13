"""
What a caller spelled, from the recognizer's text: letter by letter, with
letter names, "X as in Word", the NATO alphabet, "double", digits and the
symbols of an email address.
"""

from typing import Any

import pytest

from signalwire.speech.spelling import read_spelled, spelling_variants, spoken_email

SMITH = ["S", "M", "I", "T", "H"]


class TestReadSpelled:
    @pytest.mark.parametrize("said", [
        "s m i t h",
        "S as in Sam, M as in Mary, i t h",
        "sierra mike india tango hotel",
        "ess em eye tee aitch",
        "smith",
        "S-M-I-T-H",
    ])
    def test_the_ways_to_spell_smith(self, said: str) -> None:
        assert read_spelled(said) == SMITH

    def test_double_and_capital(self) -> None:
        assert read_spelled("capital j o double l y") == ["J", "O", "L", "L", "Y"]
        assert read_spelled("double you a") == ["W", "A"]

    def test_digits_and_oh(self) -> None:
        assert read_spelled("one two oh four 5") == ["1", "2", "O", "4", "5"]
        assert read_spelled("one two oh four", oh_is_zero=True) == ["1", "2", "0", "4"]
        assert read_spelled("123") == ["1", "2", "3"]

    def test_symbols(self) -> None:
        assert read_spelled("a dot b at c dash d underscore e") == [
            "A", ".", "B", "@", "C", "-", "D", "_", "E"]

    def test_nothing_spelled(self) -> None:
        assert read_spelled("") == []


class TestSpokenEmail:
    @pytest.mark.parametrize(("said", "address"), [
        ("john dot smith at example dot com", "john.smith@example.com"),
        ("j o h n underscore smith at example dot co dot uk", "john_smith@example.co.uk"),
        ("John.Smith@Example.com", "john.smith@example.com"),
        ("john . smith @ example . com", "john.smith@example.com"),
        ("anna at sign gmail dot com", "anna@gmail.com"),
        ("b as in boy o b at example dot com", "bob@example.com"),
        ("sales dash team at example dot org", "sales-team@example.org"),
        ("bravo oscar bravo one two at example dot net", "bob12@example.net"),
        ("double l at example dot com", "ll@example.com"),
    ])
    def test_addresses(self, said: str, address: str) -> None:
        assert spoken_email(said) == address


class TestSpellingVariants:
    def test_fewest_changes_first(self) -> None:
        assert spelling_variants(SMITH, {"S": "F", "M": "N"}) == [
            "SMITH", "FMITH", "SNITH", "FNITH"]

    def test_only_the_positions_in_doubt(self) -> None:
        assert spelling_variants(SMITH, {"S": "F", "M": "N"}, positions=[0]) == ["SMITH", "FMITH"]

    def test_a_group_with_several(self) -> None:
        assert spelling_variants(["B"], {"B": ["D", "P", "B"]}) == ["B", "D", "P"]

    def test_limit(self) -> None:
        groups: dict[str, Any] = {u: "XYZ" for u in SMITH}
        assert len(spelling_variants(SMITH, groups, limit=7)) == 7

    def test_no_groups(self) -> None:
        assert spelling_variants(SMITH, {}) == ["SMITH"]
