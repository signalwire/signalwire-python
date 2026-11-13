"""
RequestList: what the caller asked for while the agent was busy, kept in the
call's global_data, to take up when the current task is done.
"""

from typing import Any

from signalwire.patterns import RequestList


def _raw(requests: list[dict[str, str]] | None) -> dict[str, Any]:
    return {"global_data": {"later": requests} if requests is not None else {}}


def _stored(result: Any) -> dict[str, Any]:
    stored: dict[str, Any] = result.to_dict()["action"][0]["set_global_data"]
    return stored


LATER = RequestList("later", openers={"balance": "You also asked about your balance.",
                                      "question": "You had a question: {about}."})


class TestRequestList:
    def test_note_adds_it_and_tells_the_model(self) -> None:
        result = LATER.note(_raw(None), "question", "the store hours").to_dict()
        assert result["response"]["tool_result"] == "Noted for right after this: the store hours."
        assert "carry on with what you were doing" in result["response"]["tool_prompt"]
        stored = result["action"][0]["set_global_data"]
        assert stored["later"] == [{"kind": "question", "about": "the store hours"}]
        assert stored["later_text"] == (
            "Noted for right after this:\n1. You had a question: the store hours.\n"
            "When the current task is done, take these up in order, then ask if "
            "there's anything else.")

    def test_notes_keep_their_order_and_aren_t_repeated(self) -> None:
        raw = _raw([{"kind": "balance", "about": "the balance"}])
        stored = _stored(LATER.note(raw, "question", "returns"))
        assert [r["about"] for r in stored["later"]] == ["the balance", "returns"]
        assert _stored(LATER.note(raw, "balance", "the balance"))["later"] == raw[
            "global_data"]["later"]

    def test_next_and_done(self) -> None:
        raw = _raw([{"kind": "balance", "about": "the balance"},
                    {"kind": "other", "about": "store hours"}])
        assert LATER.next(raw) == {"kind": "balance", "about": "the balance",
                                   "opener": "You also asked about your balance."}
        stored = _stored(LATER.done(raw))
        assert stored["later"] == [{"kind": "other", "about": "store hours"}]
        assert "1. store hours" in stored["later_text"]

    def test_empty(self) -> None:
        assert LATER.next(_raw(None)) is None
        assert _stored(LATER.done(_raw([{"kind": "x", "about": "y"}]))) == {
            "later": [], "later_text": ""}
        assert LATER.defaults() == {"later": [], "later_text": ""}

    def test_malformed_state_is_ignored(self) -> None:
        assert LATER.pending({"global_data": {"later": "x"}}) == []
        assert LATER.pending({"global_data": {"later": [1, {"kind": "a", "about": "b"}]}}) == [
            {"kind": "a", "about": "b"}]
        assert LATER.pending(None) == []

    def test_an_opener_with_other_braces(self) -> None:
        odd = RequestList("later", openers={"x": "{about} {and more}"})
        assert odd.opener({"kind": "x", "about": "hours"}) == "hours {and more}"
