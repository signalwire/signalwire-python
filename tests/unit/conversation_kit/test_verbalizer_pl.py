"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Polish verbalizer tests for signalwire.conversation_kit.verbalizer.
"""

import pytest

from signalwire.conversation_kit.verbalizer import get

PL = get("pl")


def _check(cases, fn):
    bad = [(inp, exp, got) for inp, exp in cases if (got := fn(inp)) != exp]
    assert not bad, "\n".join(f"  {i!r}: expected {e!r}, got {g!r}" for i, e, g in bad)


def test_lang_dispatch():
    assert get("pl").lang == "pl"
    assert get("pl-PL").lang == "pl"
    assert get("PL").lang == "pl"
    # An unregistered language falls back to the neutral BASE (lang "und"), NOT English,
    # so it keeps the base's generic guidance() instead of English's deliberate opt-out.
    assert get("fr").lang == "und"
    assert get(None).lang == "und"
    assert (
        get("de").guidance() != ""
    )  # generic guidance survives for an unknown language
    assert get("en").guidance() == ""  # the registered English plugin still opts out


def test_cardinals():
    _check(
        [
            ("0", "zero"),
            ("2", "dwa"),
            ("5", "pięć"),
            ("11", "jedenaście"),
            ("21", "dwadzieścia jeden"),
            ("156", "sto pięćdziesiąt sześć"),
            ("1000", "tysiąc"),
            ("2026", "dwa tysiące dwadzieścia sześć"),
            ("1019", "tysiąc dziewiętnaście"),
            ("5000", "pięć tysięcy"),
        ],
        PL.number,
    )


def test_decimals_place_value():
    _check(
        [
            ("2.6", "dwa przecinek sześć"),
            ("2,6", "dwa przecinek sześć"),  # comma input
            ("0.156", "zero przecinek sto pięćdziesiąt sześć"),
            ("30.3", "trzydzieści przecinek trzy"),
            ("0.05", "zero przecinek zero pięć"),  # leading fractional zero
            ("-1.5", "minus jeden przecinek pięć"),
        ],
        PL.number,
    )


def test_unit_agreement():
    cases = [
        (("1", "mm/s"), "jeden milimetr na sekundę"),
        (("2", "mm/s"), "dwa milimetry na sekundę"),
        (("5", "mm/s"), "pięć milimetrów na sekundę"),
        (("21", "mm/s"), "dwadzieścia jeden milimetrów na sekundę"),
        (("2.6", "mm/s"), "dwa przecinek sześć milimetra na sekundę"),
        (("30.3", "°C"), "trzydzieści przecinek trzy stopnia Celsjusza"),
        (("2", "Hz"), "dwa herce"),
        (("1019", "hPa"), "tysiąc dziewiętnaście hektopaskali"),
    ]
    bad = [(a, e, g) for a, e in cases if (g := PL.unit(*a)) != e]
    assert not bad, "\n".join(f"  {a}: expected {e!r}, got {g!r}" for a, e, g in bad)


def test_dates():
    _check(
        [
            (
                "2026-07-04",
                "sobota, czwartego lipca dwa tysiące dwudziestego szóstego roku",
            ),
            (
                "2026-06-30",
                "wtorek, trzydziestego czerwca dwa tysiące dwudziestego szóstego roku",
            ),
            (
                "2026-01-01",
                "czwartek, pierwszego stycznia dwa tysiące dwudziestego szóstego roku",
            ),
        ],
        PL.date,
    )


def test_measure_text():
    # real handler formats: spaced, attached, ranges, and things that must NOT match
    _check(
        [
            (
                "RMS velocity: 0.156 mm/s on x",
                "RMS velocity: zero przecinek sto pięćdziesiąt sześć milimetra na sekundę on x",
            ),
            (
                "PPV:2.6mm/s freq:100Hz",
                "PPV:dwa przecinek sześć milimetra na sekundę freq:sto herców",
            ),
            (
                "Temperature: 30.3°C",
                "Temperature: trzydzieści przecinek trzy stopnia Celsjusza",
            ),
            ("max 5.0 mm/s", "max pięć milimetrów na sekundę"),
            ("1019 hPa", "tysiąc dziewiętnaście hektopaskali"),
            (
                "range 20.5–25.3°C today",  # noqa: RUF001
                "range dwadzieścia przecinek pięć do dwadzieścia pięć przecinek trzy stopnia Celsjusza today",
            ),
            ("band 10-100 Hz", "band dziesięć do sto herców"),
            ("45% of the limit", "czterdzieści pięć procent of the limit"),
            ("peak 0.5 m/s²", "peak zero przecinek pięć metra na sekundę do kwadratu"),
            ("gusts 12 km/h", "gusts dwanaście kilometrów na godzinę"),
            # must be left alone (no unit / structural):
            ("ISO 10816 zone", "ISO 10816 zone"),
            ("DIN 4150-3 referenced", "DIN 4150-3 referenced"),
            ("on 2026-07-04 at 14:30", "on 2026-07-04 at 14:30"),
            ("version 2.5 build", "version 2.5 build"),
        ],
        PL.measure_text,
    )


def test_email():
    _check(
        [
            (
                "karolczyk.jakub@gmail.com",
                "karolczyk kropka jakub małpka gmail kropka com",
            ),
            ("a-b_c@x.pl", "a myślnik b podkreślnik c małpka x kropka pl"),
        ],
        PL.email,
    )


def test_guidance():
    # PL inherits the generic, language-agnostic guidance from the base.
    g = PL.guidance({"severity": "nasilenie", "threshold": "próg"})
    assert "naturally and idiomatically" in g  # generic speak-naturally rule
    assert "EXACTLY as written" in g  # number rule (PL has MEASURE_UNITS)
    assert "narrate the assembly" in g  # email-narration rule (now shared/base)
    assert "never the ISO" in g  # date rule
    assert "severity = nasilenie" in g and "threshold = próg" in g  # glossary woven in
    assert PL.INSTRUCTION.startswith("Mów po polsku")
    assert get("en").guidance() == ""  # English opts out
    # the number rule is gated on MEASURE_UNITS — a unit-less base verbalizer omits it
    from signalwire.conversation_kit.verbalizer.base import Verbalizer

    assert "EXACTLY as written" not in Verbalizer().guidance()


def test_spell_acronyms():
    # known acronyms -> spelled letter-by-letter in Polish; numbers untouched
    _check(
        [
            ("RMS", "er em es"),
            ("UTC", "u te ce"),
            ("ISO 10816", "i es o 10816"),
            ("DIN 4150-3", "de i en 4150-3"),
            ("Czas 08:13 UTC", "Czas 08:13 u te ce"),
            ("poziom RMS na ISO", "poziom er em es na i es o"),
            # NEVER spelled: lowercase word (case-sensitive), substring in a longer word,
            # a boundary near-miss, an unknown all-caps name (a customer code), or a
            # DOMAIN acronym not in the generic default (PPV — an app adds it by subclass):
            ("din w hali", "din w hali"),
            ("izolacja", "izolacja"),
            ("DINO", "DINO"),
            ("klient ACME", "klient ACME"),
            ("poziom PPV tu", "poziom PPV tu"),
        ],
        PL.spell_acronyms,
    )


def test_spell_acronyms_english():
    en = get("en")
    assert en.spell_acronyms("RMS at ISO 10816") == "R M S at I S O 10816"
    assert en.spell_acronyms("the din of the machine") == "the din of the machine"


def test_time():
    assert PL.time(11, 31) == "jedenasta trzydzieści jeden"
    assert (
        PL.time(8, 5) == "ósma zero pięć"
    )  # single-digit minute reads the leading zero
    assert PL.time(11, 0) == "jedenasta"  # on the hour: hour only
    assert PL.time(0, 31) == "zero trzydzieści jeden"
    assert PL.time(23, 59) == "dwudziesta trzecia pięćdziesiąt dziewięć"


def test_datetime_text():
    # combined timestamp -> spoken date (no weekday) + time; UTC left for the acronym pass
    assert PL.datetime_text("Czas: 2026-07-01 11:31 UTC") == (
        "Czas: pierwszego lipca dwa tysiące dwudziestego szóstego roku, "
        "jedenasta trzydzieści jeden UTC"
    )
    # a bare date -> full spoken date (weekday + day + month + year)
    out = PL.datetime_text("spike on 2026-06-28")
    assert "2026-06-28" not in out and "czerwca" in out
    # English / base read ISO dates natively -> no-op
    assert (
        get("en").datetime_text("Time: 2026-07-01 11:31 UTC")
        == "Time: 2026-07-01 11:31 UTC"
    )


def test_large_numbers():
    # millions / milliards must not KeyError (regression: cardinal() capped at thousands)
    _check(
        [
            ("1000000", "milion"),
            ("2000000", "dwa miliony"),
            ("5000000", "pięć milionów"),
            ("1000000000", "miliard"),
            (
                "1234567",
                "milion dwieście trzydzieści cztery tysiące "
                "pięćset sześćdziesiąt siedem",
            ),
        ],
        PL.number,
    )
    assert PL.unit("1000000", "Hz") == "milion herców"
    # a long fraction reads its digits as one cardinal, so it must scale too
    assert PL.number("1.1234567").startswith("jeden przecinek milion")
    # above the milliard scale we fail loudly rather than mis-say a number
    with pytest.raises(ValueError):
        PL.number("1" + "0" * 12)


def test_range_word():
    # base/English range connector is "to"; Polish overrides to "do"
    assert PL.measure_text("band 10-100 Hz") == "band dziesięć do sto herców"
    from signalwire.conversation_kit.verbalizer.base import Verbalizer

    class _EnLike(Verbalizer):
        MEASURE_UNITS = ("Hz",)

    assert _EnLike().measure_text("band 10-100 Hz") == "band 10 to 100 Hz"


def test_time_out_of_range():
    for bad in [(24, 0), (11, 60), (-1, 0), (0, -5)]:
        with pytest.raises(ValueError):
            PL.time(*bad)


def test_datetime_text_invalid_is_untouched():
    # date-shaped but impossible -> left exactly as-is (these passes are text-safe)
    assert PL.datetime_text("x 2026-13-45 y") == "x 2026-13-45 y"
    assert PL.datetime_text("t 2026-07-01 25:99 z") == "t 2026-07-01 25:99 z"
    assert PL.datetime_text("2026-02-30 11:31") == "2026-02-30 11:31"


def test_datetime_text_z_suffix():
    # ISO "11:31Z" (no space, Z) -> normalized to a spellable " UTC", not glued
    out = PL.datetime_text("2026-07-01T11:31Z")
    assert out.endswith("jedenasta trzydzieści jeden UTC")
    assert "jedenZ" not in out and "jedenastaZ" not in out


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("ALL PASS")
