"""
The caller's own words in a tool handler.

A SWAIG request carries the conversation as call_log only with
swaig_post_conversation on (actions.c). The recognizer's finals with their
word confidences come as ai.speech_detect AI events, posted to the call's
event_webhook_url as {"event_type", "timestamp", "params": {"text", "words",
"call_id"}} (webhook.c build_event_webhook_envelope).
"""

import json
from typing import Any

from fastapi.testclient import TestClient

from signalwire import AgentBase
from signalwire.core.ai_events import SpeechLog
from signalwire.core.post_prompt import caller_turns

AUTH = ("user", "pass")

CALL_LOG = [
    {"role": "system", "content": "You take orders.", "timestamp": 100},
    {"role": "assistant", "content": "What's your ZIP code?", "timestamp": 200},
    {"role": "user", "content": "10001", "timestamp": 300, "confidence": 0.98},
    {"role": "assistant", "content": "", "tool_calls": [{"id": "x"}], "timestamp": 350},
    {"role": "user", "content": "  ", "timestamp": 360},
    {"role": "user", "content": "and a large tea", "timestamp": 400},
]


def _agent() -> AgentBase:
    return AgentBase(name="words", route="/", basic_auth=AUTH, suppress_logs=True)


def _ai(agent: AgentBase) -> dict[str, Any]:
    main = json.loads(agent._render_swml())["sections"]["main"]
    return next(verb["ai"] for verb in main if "ai" in verb)


def _event(text: str, words: list[dict[str, Any]], call_id: str = "call-1",
           timestamp: float = 1700000000.5) -> dict[str, Any]:
    return {"event_type": "ai.speech_detect", "timestamp": timestamp,
            "project_id": "p", "space_id": "s",
            "params": {"text": text, "words": words, "call_id": call_id,
                       "node_id": "n", "segment_id": call_id}}


class TestCallerTurns:
    def test_the_callers_turns_in_order(self) -> None:
        assert caller_turns({"call_log": CALL_LOG}) == ["10001", "and a large tea"]

    def test_since_and_last(self) -> None:
        assert caller_turns({"call_log": CALL_LOG}, since=350) == ["and a large tea"]
        assert caller_turns(CALL_LOG, last=1) == ["and a large tea"]
        assert caller_turns(CALL_LOG, last=0) == []

    def test_the_raw_log_when_there_is_no_call_log(self) -> None:
        assert caller_turns({"raw_call_log": CALL_LOG}) == ["10001", "and a large tea"]

    def test_nothing_without_a_conversation(self) -> None:
        assert caller_turns({"call_id": "x"}) == []
        assert caller_turns({"call_log": "not a list"}) == []
        assert caller_turns(None) == []


class TestNeedsConversation:
    def test_it_turns_on_swaig_post_conversation(self) -> None:
        agent = _agent()
        agent.define_tool("find_store", "Find a store", {}, lambda a, r: "ok",
                          needs_conversation=True)
        ai = _ai(agent)
        assert ai["params"]["swaig_post_conversation"] is True
        assert "needs_conversation" not in ai["SWAIG"]["functions"][0]

    def test_an_explicit_false_is_left_alone(self) -> None:
        agent = _agent()
        agent.set_param("swaig_post_conversation", False)
        agent.define_tool("find_store", "Find a store", {}, lambda a, r: "ok",
                          needs_conversation=True)
        assert _ai(agent)["params"]["swaig_post_conversation"] is False

    def test_off_without_a_tool_that_needs_it(self) -> None:
        agent = _agent()
        agent.define_tool("find_store", "Find a store", {}, lambda a, r: "ok")
        assert "swaig_post_conversation" not in _ai(agent).get("params", {})


class TestAiEvents:
    def test_the_event_url_is_the_agents_own(self) -> None:
        agent = _agent().record_speech_finals()
        url = _ai(agent)["params"]["event_webhook_url"]
        assert url.split("?")[0].rstrip("/").endswith("/ai_events")

    def test_a_url_set_by_hand_is_kept(self) -> None:
        agent = _agent()
        agent.set_param("event_webhook_url", "https://events.example.com/in")
        agent.on_ai_event(lambda t, p, e: None)
        assert _ai(agent)["params"]["event_webhook_url"] == "https://events.example.com/in"

    def test_no_url_when_nothing_handles_events(self) -> None:
        assert "event_webhook_url" not in _ai(_agent()).get("params", {})

    def test_posted_events_reach_the_log_and_the_handlers(self) -> None:
        seen: list[tuple[str, str]] = []
        agent = _agent().record_speech_finals()

        @agent.on_ai_event
        def heard(event_type: str, params: dict[str, Any], event: dict[str, Any]) -> None:
            seen.append((event_type, params.get("text", "")))

        words = [{"word": "S", "confidence": 0.73}, {"word": "m", "confidence": 0.95}]
        with TestClient(agent.get_app()) as client:
            ok = client.post("/ai_events", json=_event("S m", words), auth=AUTH)
            other = client.post("/ai_events", json={"event_type": "ai.response",
                                                    "params": {"call_id": "call-1"}}, auth=AUTH)
            refused = client.post("/ai_events", json=_event("x", []))
        assert (ok.status_code, other.status_code, refused.status_code) == (200, 200, 401)
        assert seen == [("ai.speech_detect", "S m"), ("ai.response", "")]
        assert agent.speech_finals("call-1") == [
            {"text": "S m", "words": words, "timestamp": 1700000000.5}]
        assert agent.speech_finals("another-call") == []

    def test_a_failing_handler_does_not_fail_the_post(self) -> None:
        agent = _agent()

        @agent.on_ai_event
        def broken(event_type: str, params: dict[str, Any], event: dict[str, Any]) -> None:
            raise RuntimeError("boom")

        with TestClient(agent.get_app()) as client:
            assert client.post("/ai_events", json=_event("hi", []), auth=AUTH).status_code == 200


class TestSpeechLog:
    def test_finals_are_kept_per_call_and_bounded(self) -> None:
        log = SpeechLog(max_calls=2, max_finals=2)
        for call in ("a", "b"):
            for n in range(3):
                log.add(_event(f"{call}{n}", [], call_id=call, timestamp=n))
        assert [f["text"] for f in log.finals("a")] == ["a1", "a2"]
        log.add(_event("c0", [], call_id="c"))
        assert log.finals("a") == []
        assert [f["text"] for f in log.finals("b", since=2)] == ["b2"]

    def test_malformed_events_are_ignored(self) -> None:
        log = SpeechLog()
        log.add({"event_type": "ai.speech_detect"})
        log.add({"params": {"text": 1, "call_id": "a"}})
        assert log.finals("a") == []

    def test_finals_are_copies(self) -> None:
        log = SpeechLog()
        log.add(_event("hi", [{"word": "hi", "confidence": 0.9}], call_id="a"))
        log.finals("a")[0]["words"][0]["word"] = "changed"
        assert log.finals("a")[0]["words"][0]["word"] == "hi"
