"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Spoken-date resolution — the inverse of verbalizer's `date()` (spoken → ISO).

The model is good at NLU, bad at calendar math: it passes the SEMANTIC parts it
heard (a weekday + this/next, today/tomorrow, or an explicit day/month/year) and
`compute_date` does the arithmetic, so a voice agent can never speak a wrong date
(a live call once resolved 'next Saturday' to a Thursday).

No third-party dependencies; product-agnostic. The agent layer wraps
`compute_date` in whatever SWAIG result / wording it needs.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, timedelta
from typing import Any

WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)

# JSON-schema `properties` for a `resolve_date` tool — the universal contract
# (multilingual hints baked in). An agent drops this straight into its tool schema:
#     "resolve_date": {"type": "object", "properties": RESOLVE_DATE_PARAMS}
RESOLVE_DATE_PARAMS = {
    "weekday": {
        "type": "string",
        "enum": WEEKDAYS,
        "description": "Weekday the caller named, lowercase English (PL 'sobota'/'czwartek' -> 'saturday'/'thursday', DE 'Samstag' -> 'saturday').",
    },
    "which": {
        "type": "string",
        "enum": ["this", "next"],
        "description": "For a weekday: 'next' (caller said next / przyszły / nächste) = that weekday in the FOLLOWING calendar week; 'this' (this / coming / nearest / najbliższa / kommende, or a bare weekday) = the soonest upcoming one. Default 'this'.",
    },
    "relative": {
        "type": "string",
        "enum": ["today", "tomorrow"],
        "description": "Use instead of weekday for 'today'/'dziś'/'heute' or 'tomorrow'/'jutro'/'morgen'.",
    },
    "in_days": {
        "type": "integer",
        "description": "Relative day COUNT from today when the caller says 'in N days' ('za dwa dni'/'in two days' -> 2; 'za tydzień'/'in a week' -> 7). Use this for a spoken offset, NOT for a calendar day-of-month number.",
    },
    "day": {
        "type": "integer",
        "description": "Day-of-month for an explicit date ('the 15th' -> 15). A calendar day number, NOT an 'in N days' offset (that is in_days).",
    },
    "month": {
        "type": "integer",
        "description": "Month 1-12 for an explicit date ('July' -> 7). Omit to use the current month.",
    },
    "year": {
        "type": "integer",
        "description": "4-digit year, only if the caller stated one.",
    },
}


def compute_date(args: Mapping[str, Any], today: date) -> date | None:
    """Pure arithmetic for resolve_date (testable: pin `today`). Returns a date or
    None. Convention: 'next <weekday>' = that weekday in the FOLLOWING calendar
    week; this/coming/nearest/bare = the soonest upcoming one (never today — a
    same-day weekday rolls to next week; readback can adjust)."""
    # 1) Explicit calendar date: day (+ optional month/year). With no year stated,
    #    resolve to the SOONEST occurrence on/after `today`: a bare day rolls
    #    month-by-month to the next month that actually contains it ("the 4th" on
    #    Jun 26 = Jul 4; "the 31st" in a 30-day month = the next month with a 31st);
    #    an explicit month rolls to next year. `bool` is excluded (it is an `int`
    #    subclass, so `True` would otherwise read as day/month 1).
    day = args.get("day")
    if isinstance(day, int) and not isinstance(day, bool) and 1 <= day <= 31:
        month_arg = args.get("month")
        year_arg = args.get("year")
        # An explicitly-supplied month/year that is out of range is a hard error —
        # never silently substitute today's (a garbled 'month:13' must not book).
        if month_arg is not None and not (
            isinstance(month_arg, int)
            and not isinstance(month_arg, bool)
            and 1 <= month_arg <= 12
        ):
            return None
        if year_arg is not None and not (
            isinstance(year_arg, int)
            and not isinstance(year_arg, bool)
            and 1000 <= year_arg <= 9999
        ):
            return None
        # Fully-stated y/m/d: take it verbatim (even if past); an impossible date
        # (e.g. Feb 30) is None.
        if year_arg is not None:
            try:
                return date(year_arg, month_arg or today.month, day)
            except ValueError:
                return None
        # No year: soonest matching date >= today. With an explicit month the month
        # is fixed (rolls to next year); a bare day walks forward month by month.
        for i in range(14):
            y = today.year + (today.month - 1 + i) // 12
            m = (today.month - 1 + i) % 12 + 1
            if month_arg is not None and m != month_arg:
                continue
            try:
                cand = date(y, m, day)
            except ValueError:
                continue
            if cand >= today:
                return cand
        return None

    # 2) Relative day word.
    rel = str(args.get("relative") or "").strip().lower()
    if rel == "today":
        return today
    if rel == "tomorrow":
        return today + timedelta(days=1)

    # 2b) Relative day COUNT: "in N days" ("za dwa dni" -> today + 2). Kept distinct
    #     from `day` (a calendar day-of-month) so a spoken offset never lands on the
    #     wrong date.
    in_days = args.get("in_days")
    if isinstance(in_days, int) and not isinstance(in_days, bool) and in_days > 0:
        return today + timedelta(days=in_days)

    # 3) Weekday (+ which).
    wd = str(args.get("weekday") or "").strip().lower()
    if wd in WEEKDAYS:
        wd_idx = WEEKDAYS.index(wd)
        which = str(args.get("which") or "this").strip().lower()
        if which == "next":
            next_monday = today + timedelta(days=7 - today.weekday())
            return next_monday + timedelta(days=wd_idx)
        ahead = (wd_idx - today.weekday()) % 7
        return today + timedelta(days=ahead or 7)

    return None
