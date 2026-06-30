"""Tests for signalwire.conversation_kit.dates.compute_date — `today` pinned for determinism."""

from datetime import date

from signalwire.conversation_kit import compute_date


def test_relative_today_tomorrow():
    today = date(2026, 6, 28)
    assert compute_date({"relative": "today"}, today) == today
    assert compute_date({"relative": "tomorrow"}, today) == date(2026, 6, 29)


def test_weekday_this_vs_next_midweek():
    # Wed 2026-07-01: 'this' = this week's upcoming day; 'next' = the FOLLOWING
    # calendar week. (On a week-boundary day like Sunday the two collapse, so the
    # distinction must be pinned mid-week.)
    wed = date(2026, 7, 1)
    assert compute_date({"weekday": "saturday", "which": "this"}, wed) == date(
        2026, 7, 4
    )
    assert compute_date({"weekday": "saturday", "which": "next"}, wed) == date(
        2026, 7, 11
    )
    # A bare weekday = the soonest upcoming one (same as 'this').
    assert compute_date({"weekday": "friday"}, wed) == date(2026, 7, 3)


def test_bare_same_weekday_rolls_to_next_week():
    # 'wednesday' ON a Wednesday -> next week's Wednesday, never today.
    assert compute_date({"weekday": "wednesday"}, date(2026, 7, 1)) == date(2026, 7, 8)


def test_explicit_day_month():
    today = date(2026, 6, 28)
    assert compute_date({"day": 4, "month": 7}, today) == date(2026, 7, 4)
    assert compute_date({"day": 15, "month": 8, "year": 2027}, today) == date(
        2027, 8, 15
    )


def test_explicit_bare_day_in_past_rolls_to_next_month():
    # 'the 4th' on Jun 28 -> Jul 4 (next month), not Jun 4.
    assert compute_date({"day": 4}, date(2026, 6, 28)) == date(2026, 7, 4)


def test_explicit_month_in_past_rolls_to_next_year():
    # 'the 10th of January' from June -> next January.
    assert compute_date({"day": 10, "month": 1}, date(2026, 6, 28)) == date(2027, 1, 10)


def test_unresolvable_returns_none():
    today = date(2026, 6, 28)
    assert compute_date({}, today) is None
    assert compute_date({"weekday": "funday"}, today) is None
    assert compute_date({"day": 99}, today) is None
