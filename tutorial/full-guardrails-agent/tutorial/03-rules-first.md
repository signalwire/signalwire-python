# Lesson 3: The Rules First

The first file you write for a guardrailed agent doesn't import SignalWire at all. `reservations.py` is the reservation book: every business rule, every record, and every check. The agent will only ever *ask* it to do things.

## Table of Contents

1. [Setting Up](#setting-up)
2. [The House Policy](#the-house-policy)
3. [Dates Are Code's Job](#dates-are-codes-job)
4. [Finding Tables Without Revealing Them](#finding-tables-without-revealing-them)
5. [Holding a Table](#holding-a-table)
6. [Confirming Exactly Once](#confirming-exactly-once)
7. [Try It](#try-it)
8. [Testing the Rules](#testing-the-rules)

---

## Setting Up

Work in the tutorial's directory, with the SDK and its requirements installed:

```bash
cd tutorial/full-guardrails-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` asks for `signalwire-sdk>=3.4.4`, the first release that enforces webhook signatures and tool tokens on every path, and `tzdata`. `tzdata` supplies time zone data to containers that don't ship it, since Penny works in the restaurant's time zone.

## The House Policy

Everything the house decides lives in plain constants at the top of `reservations.py`. The model will never see any of them:

<!-- source: reservations.py#policy --> <!-- snippet: no-run an excerpt of reservations.py, checked against the file by test_penny.py -->
```python
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
SMS_RESEND_SECONDS = 120     # a repeat request sooner than this is a duplicate
MAX_SMS_PER_BOOKING = 3
```

Changing a rule means changing one line here. It never means editing a prompt and hoping.

Rules the agent can't satisfy raise a `PolicyError` carrying two strings: `fact` (what is true) and `ask` (what the agent should do about it). In Lesson 6, handlers turn those into the two things they tell the model.

## Dates Are Code's Job

Ask a language model what "next Friday" is and it will answer confidently, and sometimes wrongly. So Penny's model never does calendar arithmetic. It passes along the caller's own words, and code resolves them:

<!-- source: reservations.py#resolve-date --> <!-- snippet: no-run an excerpt of reservations.py, checked against the file by test_penny.py -->
```python
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
        return _next_day_of_month(day, today)
    return None
```

"Next Friday" is ambiguous even between people. Code picks one reading, and the ambiguity is settled the way a human host would settle it. Penny reads the resulting date back ("Friday, September 25"), and the caller confirms or corrects it. Code produces the canonical answer, and the caller checks it.

## Finding Tables Without Revealing Them

`find_options` validates the request, then looks for free tables near the requested time:

<!-- source: reservations.py#find-options --> <!-- snippet: no-run an excerpt of reservations.py, checked against the file by test_penny.py -->
```python
def find_options(self, call_id: str, party_size: Any, date_text: str,
                 time_text: str, name: str) -> tuple[Request, list[Option]]:
    """Up to three bookable seatings near the requested time.

    Tables are chosen here and never leave this module: the caller and the
    model only ever see option numbers.
    """
    party, day, wanted, clean_name = self._validate_request(
        party_size, date_text, time_text, name)
    with self._tx() as db:
        self._session(db, call_id)
        # A new search supersedes this call's old proposal.
        db.execute("UPDATE holds SET status='released' WHERE call_id=? AND status='live'",
                   (call_id,))
        options: list[Option] = []
        nearby = sorted((s for s in SEATINGS
                         if abs(s - wanted) <= 60 and not self._too_soon(day, s)),
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
```

Look at what comes back: numbered `Option`s. Each one carries a `table_id`, but the handler in Lesson 6 only ever passes the number and the time to the model. Table IDs never leave this module, so the model can't ask for "table 7" or promise a window seat. The offers are stored against the call, which also means one call can't hold an option another call was offered.

## Holding a Table

When the caller picks an option, the table is held for five minutes and becomes a numbered proposal:

<!-- source: reservations.py#hold-option --> <!-- snippet: no-run an excerpt of reservations.py, checked against the file by test_penny.py -->
```python
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
        self._check_notice(day, offer["start"])
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
```

Four properties matter here:

- **Holds are exclusive.** Another call can't be offered or hold a table this call is holding.
- **Holding the same option twice changes nothing.** Models sometimes fire a tool twice, and a repeat returns the same proposal.
- **Every new hold gets a new revision number.** If the caller changes their mind, the old proposal can no longer be confirmed.
- **The notice rule is checked again.** An option offered at 4:29 for a 5 PM seating can't be held at 4:32, because it's no longer 30 minutes away. `confirm` checks it once more. A rule checked only when something is offered can be dodged by waiting.

## Confirming Exactly Once

`confirm` is where a booking happens:

<!-- source: reservations.py#confirm --> <!-- snippet: no-run an excerpt of reservations.py, checked against the file by test_penny.py -->
```python
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
        self._check_notice(date.fromisoformat(hold["day"]), hold["start"])
        code = self._new_code(db)
        db.execute(
            "INSERT INTO reservations (code, hold_id, call_id, table_id, day, start, "
            "party_size, name, status) VALUES (?,?,?,?,?,?,?,?, 'confirmed')",
            (code, hold["id"], call_id, hold["table_id"], hold["day"], hold["start"],
             hold["party_size"], hold["name"]))
        db.execute("UPDATE holds SET status='confirmed' WHERE id=?", (hold["id"],))
        row = db.execute("SELECT * FROM reservations WHERE code=?", (code,)).fetchone()
        return self._reservation(row)
```

The `revision` ties the booking to the exact proposal the caller heard. A confirm with a stale revision is refused. A repeated confirm returns the same booking instead of making a second. The database's `UNIQUE` constraint on `hold_id` backs that up, even if two confirms race.

## Try It

You can drive the rules directly, with no agent. Run this in Python from the `tutorial/full-guardrails-agent` directory:

<!-- snippet: no-run imports reservations.py, so it runs from the tutorial directory -->
```python
from reservations import ReservationStore

store = ReservationStore("scratch.sqlite3")
request, options = store.find_options("call-1", 4, "Friday", "7:30 PM", "Maria Rivera")
print(request.spoken(), [option.spoken() for option in options])
proposal = store.hold_option("call-1", 1)
booking = store.confirm("call-1", proposal.revision)
print(booking.code, store.confirm("call-1", proposal.revision).code)  # the same code twice
```

## Testing the Rules

`test_penny.py` has a `TestRules` class that exercises the reservation book with a clock the tests control. Run only that layer:

```bash
python -m unittest -v test_penny.TestRules
```

Here are the two tests that prove a booking happens once, including four confirms racing on threads:

<!-- source: test_penny.py#test-idempotent --> <!-- snippet: no-run an excerpt of test_penny.py, checked against the file by test_penny.py -->
```python
def test_confirming_twice_books_once(self) -> None:
    self.store.find_options("call-1", 4, "friday", "7:30pm", "Rivera")
    proposal = self.store.hold_option("call-1", 1)
    first = self.store.confirm("call-1", proposal.revision)
    self.assertEqual(self.store.confirm("call-1", proposal.revision), first)
    self.assertEqual(count(self.store, "reservations"), 1)

def test_parallel_confirms_book_once(self) -> None:
    self.store.find_options("call-1", 4, "friday", "7:30pm", "Rivera")
    proposal = self.store.hold_option("call-1", 1)
    with ThreadPoolExecutor(max_workers=4) as pool:
        codes = set(pool.map(lambda _: self.store.confirm("call-1", proposal.revision).code,
                             range(4)))
    self.assertEqual(len(codes), 1)
    self.assertEqual(count(self.store, "reservations"), 1)
```

These tests never load a model. That's the substitution test from Lesson 1, passed: the rules hold no matter what sends the requests.

## Key Takeaways

- Put every business rule in a module with no SignalWire import, and test it first
- The model passes along the caller's words, code interprets them, and the caller confirms the result
- Revisions tie a commitment to exactly what was read back, and idempotency makes repeats harmless

## Review Questions

1. Why does `find_options` return option numbers rather than table IDs to the agent?
2. What happens if the model calls `confirm` with a revision from two proposals ago?
3. Which constant would you change to stop same-day bookings less than an hour out?

## Next Steps

The rules are done and tested. Next, build the agent around them, starting with the parts that must never depend on the model. Continue with [Lesson 4: The Agent Shell](04-the-shell.md).

---

[Previous: Design Before Code](02-design-first.md) | [Overview](README.md) | [Next: The Agent Shell](04-the-shell.md)
