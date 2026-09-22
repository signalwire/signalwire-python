"""
The Copper Pot reservation book: every business rule, and no SignalWire import.

This module decides what is available, what a party may book, who has proved
they own a reservation, what is on hold, and what is committed. The voice
agent can only *ask* it to do those things. If the language model were swapped
for a web form tomorrow, every rule here would still hold.

Copyright (c) 2025 SignalWire. Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from __future__ import annotations

import json
import re
import secrets
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

RESTAURANT_TZ = ZoneInfo("America/New_York")

# region: policy
# The whole house policy. The model is never shown any of it.
TABLES = {"T1": 2, "T2": 2, "T3": 2, "T4": 4, "T5": 4, "T6": 4, "T7": 6, "T8": 6}
SEATINGS = [17 * 60 + 30 * i for i in range(8)]  # 5:00 PM to 8:30 PM, every 30 minutes
DINING_MINUTES = 90          # a table is busy for 90 minutes after seating
MAX_PHONE_PARTY = 6          # larger parties are booked by the events team
MAX_EXTRA_SEATS = 2          # never seat a party of 2 at a 6-top
BOOKING_WINDOW_DAYS = 30
CLOSED_WEEKDAYS = {0}        # Monday
SAME_DAY_LEAD_MINUTES = 30   # no seating sooner than 30 minutes from now
HOLD_SECONDS = 300           # a proposal holds its table for 5 minutes
MAX_VERIFY_ATTEMPTS = 3
HOST_STAND_HOURS = (16 * 60, 22 * 60)  # a person answers 4 PM to 10 PM, Tuesday to Sunday
# endregion: policy

# Short, speakable facts the agent may look up. Nothing here is a promise the
# kitchen or the host stand has to keep, so it is safe to say verbatim.
HOUSE_FACTS = {
    "hours": "Dinner is served Tuesday through Sunday, with seatings from 5 PM to 8:30 PM. We are closed on Mondays.",
    "location": "We're at 14 Worcester Street, across from the old train station.",
    "parking": "There is free street parking after 6 PM and a paid garage half a block away.",
    "dress_code": "There is no dress code. Come as you are.",
    "large_parties": "Parties larger than six are booked by our events team, who can arrange a private room.",
    "cancellation_policy": "You can cancel any time before your reservation at no charge.",
    "dietary": "The kitchen can adapt most dishes for vegetarian, vegan and gluten-free diets. Mention allergies to your server.",
}

CODE_ALPHABET = "ACDEFHJKMNPQRTUVWXY34679"  # no 0/O, 1/I, 2/Z, 5/S or 8/B to mishear
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
_FILLER = {"on", "the", "for", "this", "coming", "day", "night", "evening", "of"}


class PolicyError(ValueError):
    """A request the house cannot honor.

    ``fact`` is what is true; ``ask`` is what the agent should do about it.
    Handlers pass them to the model as tool_result and tool_prompt.
    """

    def __init__(self, fact: str, ask: str) -> None:
        super().__init__(fact)
        self.fact = fact
        self.ask = ask


class LargePartyError(PolicyError):
    """The party is bigger than the phone line may book."""


class LockedOutError(PolicyError):
    """Too many failed verification attempts on this call."""


# ── Speaking and hearing dates, times and codes ─────────────────────────────

# region: resolve-date
def resolve_date(text: str, today: date) -> date | None:
    """Turn the caller's own words for a date into a date, or None.

    The model passes along what the caller said ("next Friday", "the 26th");
    code does the calendar arithmetic, and the caller confirms the result when
    it is read back. The model never does date math.
    """
    t = re.sub(r"[,.]", " ", (text or "").lower())
    t = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", t)
    words = [w for w in t.split() if w not in _FILLER]
    if not words:
        return None
    joined = " ".join(words)

    if joined in ("today", "tonight"):
        return today
    if joined == "tomorrow":
        return today + timedelta(days=1)

    iso = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", joined)
    if iso:
        return _safe_date(int(iso[1]), int(iso[2]), int(iso[3]))

    strictly_after = words[0] == "next"
    if strictly_after:
        words = words[1:]
    if len(words) == 1 and words[0][:3] in [d[:3] for d in WEEKDAYS]:
        weekday = [d[:3] for d in WEEKDAYS].index(words[0][:3])
        ahead = (weekday - today.weekday()) % 7
        if ahead == 0 and strictly_after:
            ahead = 7
        return today + timedelta(days=ahead)

    numeric = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})", joined)
    if numeric:
        return _upcoming(int(numeric[1]), int(numeric[2]), today)

    month = next((MONTHS[w] for w in words if w in MONTHS), None)
    day = next((int(w) for w in words if w.isdigit() and 1 <= int(w) <= 31), None)
    if day is not None and month is not None:
        return _upcoming(month, day, today)
    if day is not None and len(words) == 1:
        # "the 26th" alone means the next 26th.
        return _upcoming(today.month, day, today) or _upcoming(today.month % 12 + 1, day, today)
    return None
# endregion: resolve-date


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _upcoming(month: int, day: int, today: date) -> date | None:
    """The next ``month``/``day`` on or after today."""
    candidate = _safe_date(today.year, month, day)
    if candidate is not None and candidate < today:
        candidate = _safe_date(today.year + 1, month, day)
    return candidate


def resolve_time(text: str) -> int | None:
    """Minutes after midnight for "7:30 pm", "19:30" or "7", or None.

    Dinner only: a bare "7:30" means 7:30 in the evening.
    """
    t = (text or "").lower().replace(".", "").replace("o'clock", "").strip()
    m = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm|a|p)?", t)
    if not m:
        return None
    hour, minute, meridiem = int(m[1]), int(m[2] or 0), m[3]
    if hour > 23 or minute > 59:
        return None
    if meridiem in ("pm", "p") and hour < 12:
        hour += 12
    elif meridiem in ("am", "a") and hour == 12:
        hour = 0
    elif meridiem is None and 1 <= hour <= 11:
        hour += 12
    return hour * 60 + minute


def spoken_date(d: date) -> str:
    return f"{d.strftime('%A, %B')} {d.day}"


def spoken_time(minutes: int) -> str:
    hour, minute = divmod(minutes, 60)
    suffix = "PM" if hour >= 12 else "AM"
    hour12 = hour - 12 if hour > 12 else (12 if hour == 0 else hour)
    return f"{hour12}:{minute:02d} {suffix}" if minute else f"{hour12} {suffix}"


def spoken_code(code: str) -> str:
    """"K7QP4M" -> "K 7 Q P 4 M", so text-to-speech reads it one character at a time."""
    return " ".join(code)


def normalize_code(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(text or "").upper())


# ── Values handed to the agent ──────────────────────────────────────────────

@dataclass(frozen=True)
class Option:
    number: int      # what the model and caller see
    table_id: str    # what they never see
    day: date
    start: int

    def spoken(self) -> str:
        return f"option {self.number}, {spoken_time(self.start)}"


@dataclass(frozen=True)
class Request:
    party_size: int
    day: date
    start: int
    name: str

    def spoken(self) -> str:
        return (f"a table for {self.party_size} on {spoken_date(self.day)} "
                f"around {spoken_time(self.start)}, under {self.name}")


@dataclass(frozen=True)
class Proposal:
    revision: int
    day: date
    start: int
    party_size: int
    name: str

    def spoken(self) -> str:
        return (f"a table for {self.party_size} on {spoken_date(self.day)} "
                f"at {spoken_time(self.start)}, under {self.name}")


@dataclass(frozen=True)
class Reservation:
    code: str
    day: date
    start: int
    party_size: int
    name: str
    status: str

    def spoken(self) -> str:
        return (f"a table for {self.party_size} on {spoken_date(self.day)} "
                f"at {spoken_time(self.start)}, under {self.name}")


# ── The store ───────────────────────────────────────────────────────────────

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    call_id TEXT PRIMARY KEY,
    request TEXT NOT NULL DEFAULT '{}',
    offers TEXT NOT NULL DEFAULT '[]',
    proposal_counter INTEGER NOT NULL DEFAULT 0,
    verified_code TEXT,
    verify_failures INTEGER NOT NULL DEFAULT 0,
    cancel_revision INTEGER,
    cancel_counter INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS holds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id TEXT NOT NULL,
    table_id TEXT NOT NULL,
    day TEXT NOT NULL,
    start INTEGER NOT NULL,
    party_size INTEGER NOT NULL,
    name TEXT NOT NULL,
    revision INTEGER NOT NULL,
    expires_at REAL NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reservations (
    code TEXT PRIMARY KEY,
    hold_id INTEGER UNIQUE,
    call_id TEXT,
    table_id TEXT NOT NULL,
    day TEXT NOT NULL,
    start INTEGER NOT NULL,
    party_size INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    sms_sent INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS messages (
    call_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    callback TEXT NOT NULL,
    body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS call_records (
    call_id TEXT PRIMARY KEY,
    turns INTEGER NOT NULL,
    outcome TEXT NOT NULL
);
"""


class ReservationStore:
    """The system of record. One SQLite file; every write is a transaction.

    State is keyed by ``call_id`` so it survives restarts and never depends on
    what the conversation remembers. A call id correlates a session; it is not
    proof of who is calling.
    """

    def __init__(self, path: str, clock: Callable[[], datetime] | None = None) -> None:
        self.path = path
        self.clock = clock or (lambda: datetime.now(RESTAURANT_TZ))
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(path, timeout=5)
        try:
            db.executescript(_SCHEMA)  # executescript manages its own commit
        finally:
            db.close()

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.execute("COMMIT")
        except BaseException:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    @staticmethod
    def _check_call(call_id: str) -> None:
        if not isinstance(call_id, str) or not call_id or len(call_id) > 256:
            raise ValueError("Missing or invalid call context.")

    def _session(self, db: sqlite3.Connection, call_id: str) -> sqlite3.Row:
        self._check_call(call_id)
        db.execute("INSERT OR IGNORE INTO sessions (call_id) VALUES (?)", (call_id,))
        return db.execute("SELECT * FROM sessions WHERE call_id=?", (call_id,)).fetchone()

    def _now(self) -> datetime:
        return self.clock()

    # ── Availability ────────────────────────────────────────────────────────

    def _table_free(self, db: sqlite3.Connection, table_id: str, day: date,
                    start: int, call_id: str) -> bool:
        busy = db.execute(
            "SELECT 1 FROM reservations WHERE table_id=? AND day=? AND status='confirmed' "
            "AND ABS(start - ?) < ?",
            (table_id, day.isoformat(), start, DINING_MINUTES)).fetchone()
        held = db.execute(
            "SELECT 1 FROM holds WHERE table_id=? AND day=? AND status='live' AND call_id<>? "
            "AND expires_at > ? AND ABS(start - ?) < ?",
            (table_id, day.isoformat(), call_id, self._now().timestamp(),
             start, DINING_MINUTES)).fetchone()
        return busy is None and held is None

    def _validate_request(self, party_size: Any, date_text: str, time_text: str,
                          name: str) -> tuple[int, date, int, str]:
        if isinstance(party_size, str) and party_size.strip().isdigit():
            party_size = int(party_size)
        if type(party_size) is not int or party_size < 1:
            raise PolicyError("The party size wasn't a number of people.",
                              "Ask how many people will be dining.")
        if party_size > MAX_PHONE_PARTY:
            raise LargePartyError(
                f"Parties larger than {MAX_PHONE_PARTY} are booked by the events team.",
                "Explain that, and offer to connect them with a person.")
        today = self._now().date()
        day = resolve_date(date_text, today)
        if day is None:
            raise PolicyError("That date couldn't be understood.",
                              "Ask for the date again, for example 'Friday' or 'September 26'.")
        if day < today:
            raise PolicyError(f"{spoken_date(day)} has already passed.",
                              "Ask for a date from today onward.")
        if day > today + timedelta(days=BOOKING_WINDOW_DAYS):
            raise PolicyError(f"Reservations open {BOOKING_WINDOW_DAYS} days ahead.",
                              "Ask for a date within the next month.")
        if day.weekday() in CLOSED_WEEKDAYS:
            raise PolicyError(f"We're closed on Mondays, and {day:%B} {day.day} is a Monday.",
                              "Ask for another date.")
        start = resolve_time(time_text)
        if start is None:
            raise PolicyError("That time couldn't be understood.",
                              "Ask what time they'd like, for example '7:30 PM'.")
        clean_name = " ".join((name or "").split())
        if not clean_name or len(clean_name) > 60:
            raise PolicyError("The reservation needs a name.", "Ask for the name for the reservation.")
        return party_size, day, start, clean_name

    # region: find-options
    def find_options(self, call_id: str, party_size: Any, date_text: str,
                     time_text: str, name: str) -> tuple[Request, list[Option]]:
        """Up to three bookable seatings near the requested time.

        Tables are chosen here and never leave this module: the caller and the
        model only ever see option numbers.
        """
        party, day, wanted, clean_name = self._validate_request(
            party_size, date_text, time_text, name)
        now = self._now()
        earliest = (now.hour * 60 + now.minute + SAME_DAY_LEAD_MINUTES
                    if day == now.date() else 0)
        with self._tx() as db:
            self._session(db, call_id)
            # A new search supersedes this call's old proposal.
            db.execute("UPDATE holds SET status='released' WHERE call_id=? AND status='live'",
                       (call_id,))
            options: list[Option] = []
            nearby = sorted((s for s in SEATINGS if abs(s - wanted) <= 60 and s >= earliest),
                            key=lambda s: (abs(s - wanted), s))
            for seating in nearby:
                fits = sorted((cap, tid) for tid, cap in TABLES.items()
                              if party <= cap <= party + MAX_EXTRA_SEATS)
                table = next((tid for _cap, tid in fits
                              if self._table_free(db, tid, day, seating, call_id)), None)
                if table:
                    options.append(Option(len(options) + 1, table, day, seating))
                if len(options) == 3:
                    break
            request = {"party_size": party, "day": day.isoformat(), "start": wanted,
                       "name": clean_name}
            db.execute(
                "UPDATE sessions SET request=?, offers=? WHERE call_id=?",
                (json.dumps(request),
                 json.dumps([{"number": o.number, "table_id": o.table_id,
                              "day": o.day.isoformat(), "start": o.start} for o in options]),
                 call_id))
        return Request(party, day, wanted, clean_name), options
    # endregion: find-options

    # region: hold-option
    def hold_option(self, call_id: str, number: Any) -> Proposal:
        """Reserve one offered option for HOLD_SECONDS and return a numbered proposal.

        Re-holding the option this call already holds returns the same proposal,
        so a model that fires the tool twice changes nothing.
        """
        if type(number) is not int:
            raise PolicyError("No option number was given.", "Ask which option they'd like.")
        with self._tx() as db:
            session = self._session(db, call_id)
            offer = next((o for o in json.loads(session["offers"]) if o["number"] == number), None)
            if offer is None:
                raise PolicyError(f"There is no option {number} on the list that was offered.",
                                  "Offer the options again by number.")
            request = json.loads(session["request"])
            day = date.fromisoformat(offer["day"])
            now_ts = self._now().timestamp()
            live = db.execute(
                "SELECT * FROM holds WHERE call_id=? AND status='live' AND expires_at > ?",
                (call_id, now_ts)).fetchone()
            if live and live["table_id"] == offer["table_id"] and live["start"] == offer["start"] \
                    and live["day"] == offer["day"]:
                return self._proposal(live)
            db.execute("UPDATE holds SET status='released' WHERE call_id=? AND status='live'",
                       (call_id,))
            if not self._table_free(db, offer["table_id"], day, offer["start"], call_id):
                raise PolicyError("That seating was just taken by another guest.",
                                  "Apologize and check availability again.")
            revision = session["proposal_counter"] + 1
            db.execute("UPDATE sessions SET proposal_counter=? WHERE call_id=?", (revision, call_id))
            cur = db.execute(
                "INSERT INTO holds (call_id, table_id, day, start, party_size, name, revision, "
                "expires_at, status) VALUES (?,?,?,?,?,?,?,?, 'live')",
                (call_id, offer["table_id"], offer["day"], offer["start"],
                 request["party_size"], request["name"], revision, now_ts + HOLD_SECONDS))
            row = db.execute("SELECT * FROM holds WHERE id=?", (cur.lastrowid,)).fetchone()
            return self._proposal(row)
    # endregion: hold-option

    @staticmethod
    def _proposal(row: sqlite3.Row) -> Proposal:
        return Proposal(row["revision"], date.fromisoformat(row["day"]), row["start"],
                        row["party_size"], row["name"])

    @staticmethod
    def _reservation(row: sqlite3.Row) -> Reservation:
        return Reservation(row["code"], date.fromisoformat(row["day"]), row["start"],
                           row["party_size"], row["name"], row["status"])

    # region: confirm
    def confirm(self, call_id: str, revision: Any) -> Reservation:
        """Commit the proposal the caller agreed to, exactly once.

        ``revision`` binds the commitment to the proposal that was read back:
        if anything changed since, the old revision no longer commits.
        """
        if type(revision) is not int or revision < 1:
            raise PolicyError("No proposal revision was given.",
                              "Read back the current proposal and ask the caller to confirm it.")
        with self._tx() as db:
            self._session(db, call_id)
            done = db.execute(
                "SELECT r.* FROM reservations r JOIN holds h ON r.hold_id = h.id "
                "WHERE h.call_id=? AND h.revision=?", (call_id, revision)).fetchone()
            if done:
                return self._reservation(done)  # a repeated confirm returns the same booking
            hold = db.execute("SELECT * FROM holds WHERE call_id=? AND status='live' "
                              "ORDER BY id DESC LIMIT 1", (call_id,)).fetchone()
            if hold is None:
                raise PolicyError("No table is on hold.", "Check availability again.")
            if hold["revision"] != revision:
                raise PolicyError("The proposal changed since it was read back.",
                                  "Read back the current proposal and ask again.")
            if hold["expires_at"] <= self._now().timestamp():
                db.execute("UPDATE holds SET status='released' WHERE id=?", (hold["id"],))
                raise PolicyError("The hold on that table expired.", "Check availability again.")
            code = self._new_code(db)
            db.execute(
                "INSERT INTO reservations (code, hold_id, call_id, table_id, day, start, "
                "party_size, name, status) VALUES (?,?,?,?,?,?,?,?, 'confirmed')",
                (code, hold["id"], call_id, hold["table_id"], hold["day"], hold["start"],
                 hold["party_size"], hold["name"]))
            db.execute("UPDATE holds SET status='confirmed' WHERE id=?", (hold["id"],))
            row = db.execute("SELECT * FROM reservations WHERE code=?", (code,)).fetchone()
            return self._reservation(row)
    # endregion: confirm

    @staticmethod
    def _new_code(db: sqlite3.Connection) -> str:
        while True:
            code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(6))
            if not db.execute("SELECT 1 FROM reservations WHERE code=?", (code,)).fetchone():
                return code

    def booking_for_call(self, call_id: str) -> Reservation | None:
        """The most recent reservation this call created, if any."""
        self._check_call(call_id)
        with self._tx() as db:
            row = db.execute("SELECT * FROM reservations WHERE call_id=? AND status='confirmed' "
                             "ORDER BY rowid DESC LIMIT 1", (call_id,)).fetchone()
            return self._reservation(row) if row else None

    def mark_sms_sent(self, code: str) -> bool:
        """True the first time only, so a re-fired tool sends one text."""
        with self._tx() as db:
            cur = db.execute("UPDATE reservations SET sms_sent=1 WHERE code=? AND sms_sent=0",
                             (code,))
            return cur.rowcount == 1

    # ── Managing an existing reservation ────────────────────────────────────

    # region: verify
    def verify(self, call_id: str, code_text: str, last_name: str) -> Reservation:
        """Bind a reservation to this call if the caller knows its code and name.

        A wrong answer never says which half was wrong, and the third failure
        on a call locks the lookup for the rest of that call.
        """
        with self._tx() as db:
            session = self._session(db, call_id)
            if session["verify_failures"] >= MAX_VERIFY_ATTEMPTS:
                raise LockedOutError("Too many attempts on this call.",
                                     "Say you can't look it up by phone right now, and offer a person.")
            row = db.execute("SELECT * FROM reservations WHERE code=?",
                             (normalize_code(code_text),)).fetchone()
            said = " ".join((last_name or "").lower().split())
            on_file = row["name"].lower().split() if row else []
            if row and said and (said == " ".join(on_file) or said == on_file[-1]):
                db.execute("UPDATE sessions SET verified_code=?, cancel_revision=NULL "
                           "WHERE call_id=?", (row["code"], call_id))
                return self._reservation(row)
            failures = session["verify_failures"] + 1
            db.execute("UPDATE sessions SET verify_failures=? WHERE call_id=?",
                       (failures, call_id))
        # Raised after the transaction commits, so the failed attempt is counted.
        if failures >= MAX_VERIFY_ATTEMPTS:
            raise LockedOutError("Too many attempts on this call.",
                                 "Say you can't look it up by phone right now, and offer a person.")
        raise PolicyError("That code and last name don't match a reservation.",
                          "Ask the caller to check the code and say it again.")
    # endregion: verify

    # region: verified
    def _verified(self, db: sqlite3.Connection, call_id: str) -> tuple[sqlite3.Row, sqlite3.Row]:
        """Every manage operation starts here: what has *this* call verified?"""
        session = self._session(db, call_id)
        if not session["verified_code"]:
            raise PolicyError("This call hasn't verified a reservation.",
                              "Ask for the confirmation code and last name first.")
        row = db.execute("SELECT * FROM reservations WHERE code=?",
                         (session["verified_code"],)).fetchone()
        return session, row
    # endregion: verified

    def verified_reservation(self, call_id: str) -> Reservation:
        with self._tx() as db:
            _session, row = self._verified(db, call_id)
            return self._reservation(row)

    # region: cancel
    def request_cancel(self, call_id: str) -> tuple[Reservation, int]:
        """Stage a cancellation and return the revision that must confirm it."""
        with self._tx() as db:
            session, row = self._verified(db, call_id)
            if row["status"] == "cancelled":
                raise PolicyError("That reservation is already cancelled.",
                                  "Tell the caller, and ask if there's anything else.")
            revision = session["cancel_counter"] + 1
            db.execute("UPDATE sessions SET cancel_counter=?, cancel_revision=? WHERE call_id=?",
                       (revision, revision, call_id))
            return self._reservation(row), revision

    def confirm_cancel(self, call_id: str, revision: Any) -> Reservation:
        """Cancel, but only the staged cancellation the caller agreed to."""
        with self._tx() as db:
            session, row = self._verified(db, call_id)
            if row["status"] == "cancelled":
                return self._reservation(row)  # a repeated confirm is harmless
            if type(revision) is not int or session["cancel_revision"] != revision:
                raise PolicyError("There's no matching cancellation waiting to be confirmed.",
                                  "Read the reservation back and ask whether to cancel it.")
            db.execute("UPDATE reservations SET status='cancelled' WHERE code=?", (row["code"],))
            db.execute("UPDATE sessions SET cancel_revision=NULL WHERE call_id=?", (call_id,))
            row = db.execute("SELECT * FROM reservations WHERE code=?", (row["code"],)).fetchone()
            return self._reservation(row)
    # endregion: cancel

    def keep_reservation(self, call_id: str) -> Reservation:
        with self._tx() as db:
            _session, row = self._verified(db, call_id)
            db.execute("UPDATE sessions SET cancel_revision=NULL WHERE call_id=?", (call_id,))
            return self._reservation(row)

    # ── Messages, the host stand, and call records ──────────────────────────

    def save_message(self, call_id: str, name: str, callback: str, body: str) -> dict[str, str]:
        """Store one message per call; saving again returns the first one."""
        digits = re.sub(r"\D", "", callback or "")
        if not 10 <= len(digits) <= 15:
            raise PolicyError("The callback number didn't have enough digits.",
                              "Ask for a callback number including the area code.")
        clean_name, clean_body = " ".join((name or "").split()), " ".join((body or "").split())
        if not clean_name or not clean_body:
            raise PolicyError("The message needs a name and a few words.",
                              "Ask for whatever is missing.")
        with self._tx() as db:
            self._session(db, call_id)
            db.execute("INSERT OR IGNORE INTO messages VALUES (?,?,?,?)",
                       (call_id, clean_name[:60], digits, clean_body[:500]))
            row = db.execute("SELECT * FROM messages WHERE call_id=?", (call_id,)).fetchone()
            return {"name": row["name"], "callback": row["callback"], "body": row["body"]}

    def host_stand_open(self) -> bool:
        now = self._now()
        minute = now.hour * 60 + now.minute
        return (now.weekday() not in CLOSED_WEEKDAYS
                and HOST_STAND_HOURS[0] <= minute < HOST_STAND_HOURS[1])

    def record_call_end(self, call_id: str, turns: int) -> str:
        """Write what actually happened on this call, from the store, not the transcript."""
        with self._tx() as db:
            self._session(db, call_id)
            if db.execute("SELECT 1 FROM reservations WHERE call_id=? AND status='confirmed'",
                          (call_id,)).fetchone():
                outcome = "booked"
            elif db.execute("SELECT 1 FROM sessions s JOIN reservations r ON r.code = s.verified_code "
                            "WHERE s.call_id=? AND r.status='cancelled'", (call_id,)).fetchone():
                outcome = "cancelled"
            elif db.execute("SELECT 1 FROM messages WHERE call_id=?", (call_id,)).fetchone():
                outcome = "message"
            else:
                outcome = "no_change"
            db.execute("INSERT OR REPLACE INTO call_records VALUES (?,?,?)",
                       (call_id, int(turns), outcome))
            return outcome

    def seed_demo(self) -> str | None:
        """Add one known reservation (code K7QP4M, Rivera) so the manage flow can be tried."""
        with self._tx() as db:
            if db.execute("SELECT 1 FROM reservations").fetchone():
                return None
            day = self._now().date() + timedelta(days=2)
            while day.weekday() in CLOSED_WEEKDAYS:
                day += timedelta(days=1)
            db.execute(
                "INSERT INTO reservations (code, hold_id, call_id, table_id, day, start, "
                "party_size, name, status) VALUES ('K7QP4M', NULL, 'seed', 'T4', ?, ?, 4, "
                "'Maria Rivera', 'confirmed')", (day.isoformat(), 19 * 60))
            return "K7QP4M"
