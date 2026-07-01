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

WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

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
    # 1) Explicit calendar date: day (+ optional month/year). If it lands in the
    #    past with no year stated, roll forward to the next occurrence: an explicit
    #    month -> same date next year; a bare day -> the same day next month ("the
    #    4th" on Jun 26 = Jul 4, not Jun 4 next year).
    day = args.get("day")
    if isinstance(day, int) and 1 <= day <= 31:
        has_month = isinstance(args.get("month"), int) and 1 <= args["month"] <= 12
        has_year = isinstance(args.get("year"), int)
        month = args["month"] if has_month else today.month
        year = args["year"] if has_year else today.year
        try:
            target = date(year, month, day)
        except ValueError:
            return None
        if target < today and not has_year:
            try:
                if has_month:
                    target = date(year + 1, month, day)
                else:
                    target = (
                        date(year + 1, 1, day)
                        if month == 12
                        else date(year, month + 1, day)
                    )
            except ValueError:
                return None
        return target

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
    if isinstance(in_days, int) and in_days > 0:
        return today + timedelta(days=in_days)

    # 3) Weekday (+ which).
    wd = str(args.get("weekday") or "").strip().lower()
    if wd in WEEKDAYS:
        wd_idx = WEEKDAYS.index(wd)
        which = str(args.get("which") or "this").strip().lower()
        if which in ("next", "next_week", "following"):
            next_monday = today + timedelta(days=7 - today.weekday())
            return next_monday + timedelta(days=wd_idx)
        ahead = (wd_idx - today.weekday()) % 7
        return today + timedelta(days=ahead or 7)

    return None
