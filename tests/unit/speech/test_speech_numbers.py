"""
Numbers as a voice should say them.

The platform normalizes text before its pronunciation rules run, so a bare
number reaches the rules as words already: a ZIP code given as digits is read
"ten thousand one". These functions give the words instead.
"""

from decimal import Decimal
from typing import Any

import pytest

from signalwire.speech import number_words, say_digits, say_last_digits, say_money


class TestNumberWords:
    @pytest.mark.parametrize(("n", "words"), [
        (0, "zero"), (7, "seven"), (13, "thirteen"), (40, "forty"), (42, "forty-two"),
        (100, "one hundred"), (105, "one hundred five"), (1405, "one thousand four hundred five"),
        (2_000_034, "two million thirty-four"), (-12, "minus twelve"),
        (999_999_999_999_999, "nine hundred ninety-nine trillion nine hundred ninety-nine "
                              "billion nine hundred ninety-nine million nine hundred "
                              "ninety-nine thousand nine hundred ninety-nine"),
    ])
    def test_words(self, n: int, words: str) -> None:
        assert number_words(n) == words

    @pytest.mark.parametrize("n", [10**15, 1.5, True, "3"])
    def test_refused(self, n: Any) -> None:
        with pytest.raises(ValueError):
            number_words(n)


class TestSayDigits:
    def test_the_texts_own_groups(self) -> None:
        assert say_digits("415-555-0192") == "four one five, five five five, zero one nine two"
        assert say_digits("10001") == "one zero zero zero one"
        assert say_digits(90210) == "nine zero two one zero"

    def test_given_groups(self) -> None:
        assert say_digits("123456", group=2) == "one two, three four, five six"
        assert say_digits("4155550192", group=(3, 3)) == (
            "four one five, five five five, zero one nine two")

    def test_zero_can_be_oh(self) -> None:
        assert say_digits("1007", zero="oh") == "one oh oh seven"

    def test_no_digits(self) -> None:
        assert say_digits("none") == ""

    @pytest.mark.parametrize("group", [0, (3, 0), (), True])
    def test_bad_groups(self, group: Any) -> None:
        with pytest.raises(ValueError):
            say_digits("123", group=group)


class TestSayLastDigits:
    def test_the_last_digits(self) -> None:
        assert say_last_digits("4111 1111 1111 1234") == "one two three four"
        assert say_last_digits("5551009", n=2, zero="oh") == "oh nine"
        assert say_last_digits("12", n=4) == "one two"

    def test_bad_counts(self) -> None:
        with pytest.raises(ValueError):
            say_last_digits("1234", n=0)


class TestSayMoney:
    @pytest.mark.parametrize(("amount", "currency", "words"), [
        (14.5, "USD", "fourteen dollars and fifty cents"),
        (1, "USD", "one dollar"),
        ("0.05", "USD", "five cents"),
        (0.005, "USD", "one cent"),  # half up
        (0, "USD", "zero dollars"),
        (Decimal("2.01"), "gbp", "two pounds and one penny"),
        (-3.5, "EUR", "minus three euros and fifty cents"),
        (1500, "JPY", "one thousand five hundred yen"),
        (99.99, "CAD", "ninety-nine dollars and ninety-nine cents"),
    ])
    def test_words(self, amount: Any, currency: str, words: str) -> None:
        assert say_money(amount, currency) == words

    @pytest.mark.parametrize(("amount", "currency"), [
        ("ten", "USD"), (float("nan"), "USD"), (True, "USD"), (5, "XYZ")])
    def test_refused(self, amount: Any, currency: str) -> None:
        with pytest.raises(ValueError):
            say_money(amount, currency)
