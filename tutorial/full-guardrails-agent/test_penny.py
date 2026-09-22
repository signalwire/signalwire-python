"""
Penny's tests, in three layers plus the docs:

* TestRules      - the reservation book, with no agent at all
* TestWorkflow   - the SWML the agent actually serves: tools and navigation per step
* TestSecurity   - the HTTP edge of that same served app
* TestHandlers   - what each tool returns to the model and to the platform
* TestDocs       - every code block the lessons quote is still the real code

Run from this directory:  python -m unittest -v test_penny

None of this places a phone call. It proves the rules and the configuration;
speech, timing and the live platform still need a real call.

Copyright (c) 2025 SignalWire. Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import contextlib
import io
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from unittest import mock

# The agent refuses to start without real secrets; these are throwaway test values.
TEST_ENV = {"SWML_BASIC_AUTH_USER": "penny", "SWML_BASIC_AUTH_PASSWORD": "test-password",
            "SIGNALWIRE_SIGNING_KEY": "test-signing-key", "SIGNALWIRE_SWAIG_SECRET": "test-swaig"}
os.environ.update(TEST_ENV)
os.environ.setdefault("SIGNALWIRE_LOG_MODE", "off")

from signalwire import configure_logging  # noqa: E402

configure_logging()  # applies SIGNALWIRE_LOG_MODE, so the SDK stays quiet

from check_docs import check_docs  # noqa: E402
from handlers import GOODBYE, TRANSFER_NOTICE, PennyHandlers, Settings  # noqa: E402
from penny import GREETING, Penny  # noqa: E402
from reservations import (  # noqa: E402
    RESTAURANT_TZ,
    LargePartyError,
    LockedOutError,
    PolicyError,
    ReservationStore,
    resolve_date,
    resolve_time,
)
from signalwire.core.contexts import Step  # noqa: E402

# region: clock
TUESDAY_3PM = datetime(2026, 9, 22, 15, 0, tzinfo=RESTAURANT_TZ)


class Clock:
    """A clock the tests can move forward."""

    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now


def new_store(clock: Clock | None = None) -> ReservationStore:
    return ReservationStore(str(Path(tempfile.mkdtemp()) / "test.sqlite3"),
                            clock=clock or Clock(TUESDAY_3PM))
# endregion: clock


def count(store: ReservationStore, table: str) -> int:
    with store._tx() as db:
        return db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]  # noqa: S608 (the tests' own table names)


# region: served-app
def served_app(store: ReservationStore | None = None) -> Any:
    """The web app ``penny.run()`` serves, captured instead of started."""
    with mock.patch("uvicorn.run") as run, contextlib.redirect_stdout(io.StringIO()):
        Penny(store=store or new_store()).run()
    return run.call_args.args[0]
# endregion: served-app


# ── Layer 1: the rules, with no agent ───────────────────────────────────────

class TestRules(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = Clock(TUESDAY_3PM)
        self.store = new_store(self.clock)

    def book(self, call_id: str = "call-1", party: int = 4, when: str = "friday",
             time: str = "7:30 pm", option: int = 1) -> str:
        self.store.find_options(call_id, party, when, time, "Maria Rivera")
        proposal = self.store.hold_option(call_id, option)
        return self.store.confirm(call_id, proposal.revision).code

    def test_callers_words_become_dates_in_code(self) -> None:
        today = TUESDAY_3PM.date()
        self.assertEqual(resolve_date("Friday", today).isoformat(), "2026-09-25")
        self.assertEqual(resolve_date("tomorrow night", today).isoformat(), "2026-09-23")
        self.assertEqual(resolve_date("the 26th", today).isoformat(), "2026-09-26")
        self.assertEqual(resolve_date("Sept. 26th", today).isoformat(), "2026-09-26")
        self.assertEqual(resolve_date("9/26", today).isoformat(), "2026-09-26")
        self.assertEqual(resolve_date("next Tuesday", today).isoformat(), "2026-09-29")
        self.assertIsNone(resolve_date("whenever you're free", today))

    def test_dinner_times(self) -> None:
        self.assertEqual(resolve_time("7:30 PM"), 19 * 60 + 30)
        self.assertEqual(resolve_time("19:30"), 19 * 60 + 30)
        self.assertEqual(resolve_time("7"), 19 * 60)
        self.assertIsNone(resolve_time("noon"))

    def test_offers_the_nearest_free_seatings(self) -> None:
        request, options = self.store.find_options("call-1", 4, "friday", "7:30 pm", "Rivera")
        self.assertEqual(request.day.isoformat(), "2026-09-25")
        self.assertEqual([o.start for o in options], [19 * 60 + 30, 19 * 60, 20 * 60])
        self.assertTrue(all(o.table_id in ("T4", "T5", "T6", "T7", "T8") for o in options))

    def test_the_house_refuses_what_policy_forbids(self) -> None:
        with self.assertRaises(LargePartyError):
            self.store.find_options("call-1", 8, "friday", "7pm", "Big Group")
        for when, fact in [("monday", "closed on Mondays"), ("2026-09-01", "already passed"),
                           ("2026-12-25", "30 days ahead"), ("soonish", "couldn't be understood")]:
            with self.assertRaises(PolicyError) as refused:
                self.store.find_options("call-1", 2, when, "7pm", "Rivera")
            self.assertIn(fact, refused.exception.fact)

    def test_same_day_needs_thirty_minutes_notice(self) -> None:
        self.clock.now = TUESDAY_3PM.replace(hour=18, minute=50)
        _request, options = self.store.find_options("call-1", 2, "tonight", "7pm", "Rivera")
        self.assertEqual(min(o.start for o in options), 19 * 60 + 30)

    def test_a_hold_keeps_the_table_from_other_callers(self) -> None:
        # Only two tables seat six, so two holds at 7 PM leave nothing near 7 PM.
        for call_id in ("call-1", "call-2"):
            self.store.find_options(call_id, 6, "friday", "7pm", "Group")
            self.store.hold_option(call_id, 1)
        _request, options = self.store.find_options("call-3", 6, "friday", "7pm", "Group")
        self.assertEqual(options, [])

    def test_a_hold_expires(self) -> None:
        self.store.find_options("call-1", 6, "friday", "7pm", "Group")
        proposal = self.store.hold_option("call-1", 1)
        self.clock.now += timedelta(seconds=301)
        with self.assertRaises(PolicyError) as refused:
            self.store.confirm("call-1", proposal.revision)
        self.assertIn("expired", refused.exception.fact)
        self.assertEqual(count(self.store, "reservations"), 0)

    def test_repeating_a_hold_changes_nothing(self) -> None:
        self.store.find_options("call-1", 4, "friday", "7:30pm", "Rivera")
        first = self.store.hold_option("call-1", 1)
        self.assertEqual(self.store.hold_option("call-1", 1), first)

    def test_only_the_proposal_read_back_can_be_confirmed(self) -> None:
        self.store.find_options("call-1", 4, "friday", "7:30pm", "Rivera")
        old = self.store.hold_option("call-1", 1)
        self.store.hold_option("call-1", 2)  # the caller changed their mind
        with self.assertRaises(PolicyError) as refused:
            self.store.confirm("call-1", old.revision)
        self.assertIn("changed", refused.exception.fact)
        self.assertEqual(count(self.store, "reservations"), 0)

    # region: test-idempotent
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
    # endregion: test-idempotent

    def test_options_belong_to_the_call_that_searched(self) -> None:
        self.store.find_options("call-1", 4, "friday", "7:30pm", "Rivera")
        with self.assertRaises(PolicyError):
            self.store.hold_option("call-2", 1)

    def test_a_miss_never_says_which_half_was_wrong(self) -> None:
        code = self.book()
        with self.assertRaises(PolicyError) as wrong_code:
            self.store.verify("call-2", "ZZZZZZ", "Rivera")
        with self.assertRaises(PolicyError) as wrong_name:
            self.store.verify("call-3", code, "Smith")
        self.assertEqual(wrong_code.exception.fact, wrong_name.exception.fact)

    def test_verification_locks_after_three_misses(self) -> None:
        code = self.book()
        for _ in range(2):
            with self.assertRaises(PolicyError) as refused:
                self.store.verify("call-2", "ZZZZZZ", "Rivera")
            self.assertIs(type(refused.exception), PolicyError)  # not locked yet
        with self.assertRaises(LockedOutError):
            self.store.verify("call-2", "ZZZZZZ", "Rivera")
        with self.assertRaises(LockedOutError):
            self.store.verify("call-2", code, "Rivera")  # even the right answer, once locked

    def test_verification_takes_the_last_or_full_name(self) -> None:
        code = self.book()
        self.assertEqual(self.store.verify("call-2", code.lower(), "rivera").code, code)
        self.assertEqual(self.store.verify("call-3", " ".join(code), "Maria Rivera").code, code)
        with self.assertRaises(PolicyError):
            self.store.verify("call-4", code, "Smith")

    def test_cancelling_needs_verification_on_this_call(self) -> None:
        code = self.book()
        self.store.verify("call-2", code, "Rivera")
        with self.assertRaises(PolicyError):
            self.store.request_cancel("call-3")  # another call proved nothing

    def test_cancelling_needs_the_staged_revision_and_happens_once(self) -> None:
        code = self.book()
        self.store.verify("call-2", code, "Rivera")
        _found, revision = self.store.request_cancel("call-2")
        with self.assertRaises(PolicyError):
            self.store.confirm_cancel("call-2", revision + 1)
        self.assertEqual(self.store.confirm_cancel("call-2", revision).status, "cancelled")
        self.assertEqual(self.store.confirm_cancel("call-2", revision).status, "cancelled")

    def test_a_message_needs_a_real_callback_number_and_saves_once(self) -> None:
        with self.assertRaises(PolicyError):
            self.store.save_message("call-1", "Ana", "555-12", "Please call")
        first = self.store.save_message("call-1", "Ana", "(555) 123-4567", "Please call")
        self.store.save_message("call-1", "Someone Else", "5559999999", "Different")
        self.assertEqual(self.store.save_message("call-1", "Ana", "5551234567", "x"), first)
        self.assertEqual(count(self.store, "messages"), 1)

    def test_host_stand_hours(self) -> None:
        self.assertFalse(self.store.host_stand_open())  # Tuesday 3 PM
        self.clock.now = TUESDAY_3PM.replace(hour=17)
        self.assertTrue(self.store.host_stand_open())
        self.clock.now = TUESDAY_3PM.replace(day=21, hour=17)  # Monday
        self.assertFalse(self.store.host_stand_open())

    def test_call_records_come_from_the_store(self) -> None:
        self.book("call-1")
        self.assertEqual(self.store.record_call_end("call-1", 12), "booked")
        self.assertEqual(self.store.record_call_end("call-9", 3), "no_change")


# ── Layer 2: the workflow contract, read from the rendered SWML ─────────────

class TestWorkflow(unittest.TestCase):
    ai: dict[str, Any]
    steps: dict[str, dict[str, Any]]

    @classmethod
    def setUpClass(cls) -> None:
        from fastapi.testclient import TestClient
        # Fetch the SWML the way SignalWire does, from the app Penny serves.
        client = TestClient(served_app())
        document = client.get("/penny", auth=("penny", "test-password")).json()
        cls.ai = next(verb["ai"] for verb in document["sections"]["main"] if "ai" in verb)
        cls.contexts = cls.ai["prompt"]["contexts"]
        cls.steps = {f"{name}/{step['name']}": step
                     for name, context in cls.contexts.items() for step in context["steps"]}

    # region: test-scoping
    def test_every_step_names_its_tools_and_cannot_navigate(self) -> None:
        for where, step in self.steps.items():
            with self.subTest(step=where):
                self.assertIn("functions", step)  # omitted would inherit the last step's tools
                self.assertEqual(step["valid_steps"], [])
                self.assertEqual(step["valid_contexts"], [])
                self.assertNotIn("end", step)

    def test_every_tool_a_step_names_is_registered(self) -> None:
        registered = {f["function"] for f in self.ai["SWAIG"]["functions"]}
        for where, step in self.steps.items():
            gathered = [f for q in step.get("gather_info", {}).get("questions", [])
                        for f in q.get("functions", [])]
            for tool in step["functions"] + gathered:
                with self.subTest(step=where, tool=tool):
                    self.assertIn(tool, registered)

    def test_consequential_tools_live_in_exactly_one_step(self) -> None:
        homes = {"hold_table": "booking/choose", "confirm_booking": "booking/review",
                 "send_confirmation_text": "booking/booked",
                 "verify_reservation": "manage/verify", "request_cancel": "manage/details",
                 "confirm_cancel": "manage/confirm_cancel", "save_message": "help/save_message"}
        for tool, home in homes.items():
            with self.subTest(tool=tool):
                self.assertEqual([w for w, s in self.steps.items() if tool in s["functions"]], [home])
    # endregion: test-scoping

    def test_nothing_about_a_reservation_is_reachable_before_verifying(self) -> None:
        self.assertEqual(self.steps["manage/verify"]["functions"],
                         ["verify_reservation", "house_info", "request_human"])

    def test_every_context_starts_on_its_first_step(self) -> None:
        for name, context in self.contexts.items():
            with self.subTest(context=name):
                self.assertEqual(context["initial_step"], context["steps"][0]["name"])

    def test_every_gather_question_has_an_escape(self) -> None:
        for where in ("booking/collect", "help/take_message"):
            for question in self.steps[where]["gather_info"]["questions"]:
                with self.subTest(step=where, question=question["key"]):
                    self.assertTrue(question.get("functions"))

    # region: test-trap
    def test_leaving_out_tools_is_not_the_same_as_no_tools(self) -> None:
        self.assertNotIn("functions", Step("omitted").set_text("Ask.").to_dict())
        self.assertEqual(Step("empty").set_text("Ask.").set_functions([]).to_dict()["functions"], [])
    # endregion: test-trap

    def test_each_call_gets_its_own_facts(self) -> None:
        self.assertEqual(self.ai["global_data"], {"host_stand": "closed"})  # Tuesday, 3 PM

    def test_the_greeting_is_spoken_by_the_platform(self) -> None:
        self.assertEqual(self.ai["params"]["static_greeting"], GREETING)
        self.assertTrue(self.ai["params"]["static_greeting_no_barge"])

    def test_the_agent_refuses_to_start_without_its_secrets(self) -> None:
        with mock.patch.dict(os.environ, {"SIGNALWIRE_SWAIG_SECRET": ""}), \
                self.assertRaises(RuntimeError):
            Penny(store=new_store())


# region: test-security
class TestSecurity(unittest.TestCase):
    """The HTTP edge of the served app: a request needs the password, and SignalWire's signature."""

    def setUp(self) -> None:
        from fastapi.testclient import TestClient
        self.client = TestClient(served_app())
        self.tool_call = {"function": "finish", "argument": {"parsed": [{}]}, "call_id": "call-1"}

    def test_the_wrong_password_is_refused(self) -> None:
        self.assertEqual(self.client.get("/penny", auth=("penny", "guess")).status_code, 401)

    @unittest.expectedFailure  # signalwire-sdk 3.4.3's run() skips this check; remove once fixed
    def test_an_unsigned_tool_call_is_refused(self) -> None:
        response = self.client.post("/penny/swaig", json=self.tool_call,
                                    auth=("penny", "test-password"))
        self.assertEqual(response.status_code, 403)
# endregion: test-security


# ── Layer 3: what each tool tells the model and the platform ────────────────

def actions(result: dict[str, Any]) -> list[dict[str, Any]]:
    return result.get("action", [])


def action_keys(result: dict[str, Any]) -> list[str]:
    keys = []
    for act in actions(result):
        if "SWML" in act:
            keys.append(next(iter(act["SWML"]["sections"]["main"][0])))
        else:
            keys.extend(k for k in act if k != "transfer")
    return keys


def events(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [act["SWML"]["sections"]["main"][0]["user_event"]["event"] for act in actions(result)
            if "SWML" in act and "user_event" in act["SWML"]["sections"]["main"][0]]


def moved_to(result: dict[str, Any]) -> str | None:
    return next((act.get("change_step") or act.get("change_context") for act in actions(result)
                 if "change_step" in act or "change_context" in act), None)


class TestHandlers(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = Clock(TUESDAY_3PM)
        self.store = new_store(self.clock)
        self.tools = PennyHandlers(self.store, Settings(host_number="+15555550100",
                                                        sms_from="+15555550199"))

    def call(self, tool: str, args: Any = None, call_id: str | None = "call-1",
             **extra: Any) -> dict[str, Any]:
        raw: dict[str, Any] = {"global_data": extra.pop("global_data", {}), **extra}
        if call_id:
            raw["call_id"] = call_id
        return getattr(self.tools, tool)({} if args is None else args, raw).to_dict()

    def gathered(self, **answers: Any) -> dict[str, Any]:
        base = {"party_size": 4, "date": "Friday", "time": "7:30 PM", "name": "Maria Rivera"}
        return {"booking_request": {**base, **answers}}

    def test_a_whole_booking(self) -> None:
        found = self.call("find_tables", global_data=self.gathered())
        self.assertIn("option 1, 7:30 PM", found["response"]["tool_result"])
        self.assertEqual(moved_to(found), "choose")
        self.assertEqual(events(found)[0]["type"], "options_offered")

        held = self.call("hold_table", {"option": 1})
        self.assertIn("revision 1", held["response"]["tool_result"])
        self.assertEqual(moved_to(held), "review")

        booked = self.call("confirm_booking", {"revision": 1})
        self.assertEqual(moved_to(booked), "booked")
        code = events(booked)[0]["code"]
        self.assertIn(" ".join(code), booked["response"]["tool_result"])
        self.assertEqual(actions(booked)[0]["set_global_data"]["booking"]["code_spoken"],
                         " ".join(code))

        texted = self.call("send_confirmation_text", caller_id_num="+15555551234")
        self.assertEqual(action_keys(texted), ["send_sms"])
        again = self.call("send_confirmation_text", caller_id_num="+15555551234")
        self.assertEqual(actions(again), [])  # one text, however often the tool fires

    def test_corrections_override_what_was_gathered(self) -> None:
        found = self.call("find_tables", {"time": "5 PM"}, global_data=self.gathered())
        self.assertIn("option 1, 5 PM", found["response"]["tool_result"])

    def test_refusals_carry_facts_and_no_actions(self) -> None:
        self.call("find_tables", global_data=self.gathered())
        refused = self.call("hold_table", {"option": 9})
        self.assertIn("no option 9", refused["response"]["tool_result"])
        self.assertEqual(actions(refused), [])
        stale = self.call("confirm_booking", {"revision": 7})
        self.assertEqual(actions(stale), [])
        self.assertEqual(count(self.store, "reservations"), 0)

    def test_a_large_party_is_offered_a_person_not_a_table(self) -> None:
        refused = self.call("find_tables", global_data=self.gathered(party_size=9))
        self.assertIn("events team", refused["response"]["tool_result"])
        self.assertEqual(actions(refused), [])

    def test_no_call_context_means_nothing_happens(self) -> None:
        result = self.call("find_tables", call_id=None, global_data=self.gathered())
        self.assertIn("no call context", result["response"]["tool_result"])
        self.assertEqual(actions(result), [])

    def test_malformed_arguments_do_nothing(self) -> None:
        result = self.call("hold_table", args=["option", 1])
        self.assertEqual(actions(result), [])

    # region: test-crash
    def test_a_crash_never_sounds_like_success(self) -> None:
        with (mock.patch.object(self.store, "confirm", side_effect=RuntimeError("disk full")),
              self.assertLogs("penny", level="ERROR")):
            result = self.call("confirm_booking", {"revision": 1})
        self.assertIn("outcome is unknown", result["response"]["tool_result"])
        self.assertIn("Don't say it worked", result["response"]["tool_prompt"])
        self.assertEqual(actions(result), [])
    # endregion: test-crash

    # region: test-gate
    def test_asking_nicely_does_not_skip_verification(self) -> None:
        refused = self.call("request_cancel", call_id="call-2")
        self.assertIn("hasn't verified", refused["response"]["tool_result"])
        self.assertEqual(actions(refused), [])

    def test_verification_then_a_two_step_cancel(self) -> None:
        self.call("find_tables", global_data=self.gathered())
        self.call("hold_table", {"option": 1})
        code = events(self.call("confirm_booking", {"revision": 1}))[0]["code"]

        verified = self.call("verify_reservation",
                             {"confirmation_code": code, "last_name": "Rivera"}, call_id="call-2")
        self.assertEqual(moved_to(verified), "details")
        staged = self.call("request_cancel", call_id="call-2")
        self.assertEqual(moved_to(staged), "confirm_cancel")
        self.assertEqual(self.store.verified_reservation("call-2").status, "confirmed")
        done = self.call("confirm_cancel", {"revision": 1}, call_id="call-2")
        self.assertEqual(moved_to(done), "cancelled")
        self.assertEqual(self.store.verified_reservation("call-2").status, "cancelled")

    def test_three_misses_lock_the_lookup(self) -> None:
        wrong = {"confirmation_code": "ZZZZZZ", "last_name": "Nobody"}
        self.assertIsNone(moved_to(self.call("verify_reservation", wrong)))
        self.assertIsNone(moved_to(self.call("verify_reservation", wrong)))
        self.assertEqual(moved_to(self.call("verify_reservation", wrong)), "locked")
    # endregion: test-gate

    def test_a_person_only_when_someone_is_there(self) -> None:
        closed = self.call("request_human")  # Tuesday 3 PM: the host stand opens at 4
        self.assertEqual(moved_to(closed), "help")
        self.clock.now = TUESDAY_3PM.replace(hour=18)
        open_ = self.call("request_human")
        self.assertEqual(action_keys(open_), ["say", "connect"])  # announce, then transfer
        self.assertEqual(actions(open_)[0]["say"], TRANSFER_NOTICE)
        self.assertEqual(actions(open_)[1]["SWML"]["sections"]["main"][0]["connect"]["to"],
                         "+15555550100")

    def test_the_text_goes_only_to_the_calling_number(self) -> None:
        self.call("find_tables", global_data=self.gathered())
        self.call("hold_table", {"option": 1})
        self.call("confirm_booking", {"revision": 1})
        refused = self.call("send_confirmation_text", {"to_number": "+15550009999"},
                            caller_id_num="anonymous")
        self.assertEqual(actions(refused), [])  # the model can't name a destination
        sent = self.call("send_confirmation_text", {"to_number": "+15550009999"},
                         caller_id_num="+15555551234")
        sms = actions(sent)[0]["SWML"]["sections"]["main"][0]["send_sms"]
        self.assertEqual(sms["to_number"], "+15555551234")

    def test_a_message_is_taken_from_the_gathered_answers(self) -> None:
        taken = {"message": {"name": "Ana", "callback": "555 123 4567", "body": "Party of 12"}}
        saved = self.call("save_message", global_data=taken)
        self.assertEqual(moved_to(saved), "message_saved")
        self.assertIn("ending in 4567", saved["response"]["tool_result"])

    def test_goodbye_plays_in_full_before_the_hangup(self) -> None:
        result = self.call("finish")
        self.assertEqual(action_keys(result), ["say", "hangup"])
        self.assertEqual(actions(result)[0]["say"], GOODBYE)

    def test_the_call_record_is_written_from_the_store(self) -> None:
        with self.assertLogs("penny", level="INFO"):
            self.tools.capture_call([{"role": "user"}] * 5, {"call_id": "call-1"})
        self.assertEqual(count(self.store, "call_records"), 1)


# ── The docs ────────────────────────────────────────────────────────────────

class TestDocs(unittest.TestCase):
    def test_every_quoted_block_is_the_real_code(self) -> None:
        self.assertEqual(check_docs(), [])


if __name__ == "__main__":
    unittest.main()
