"""Polish verbalizer tests for signalwire.conversation_kit.verbalizer."""

from signalwire.conversation_kit.verbalizer import get

PL = get("pl")


def _check(cases, fn):
    bad = [(inp, exp, got) for inp, exp in cases if (got := fn(inp)) != exp]
    assert not bad, "\n".join(f"  {i!r}: expected {e!r}, got {g!r}" for i, e, g in bad)


def test_lang_dispatch():
    assert get("pl").lang == "pl"
    assert get("pl-PL").lang == "pl"
    assert get("PL").lang == "pl"
    assert get("fr").lang == "en"  # unknown -> English fallback
    assert get(None).lang == "en"


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
    g = PL.guidance({"severity": "nasilenie", "RMS vibration": "poziom drgań (RMS)"})
    assert "naturally and idiomatically" in g  # generic speak-naturally rule
    assert "EXACTLY as written" in g  # number rule (PL has MEASURE_UNITS)
    assert "narrate the assembly" in g  # email-narration rule (now shared/base)
    assert "never the ISO" in g  # date rule
    assert (
        "severity = nasilenie" in g and "poziom drgań (RMS)" in g
    )  # glossary woven in
    assert PL.INSTRUCTION.startswith("Mów po polsku")
    assert get("en").guidance() == ""  # English opts out
    # the number rule is gated on MEASURE_UNITS — a unit-less base verbalizer omits it
    from signalwire.conversation_kit.verbalizer.base import Verbalizer

    assert "EXACTLY as written" not in Verbalizer().guidance()


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("ALL PASS")
