"""Post-prompt normalization across the voice and chat engines.

The two engines emit the same artifact in different shapes, and the differences
are not discoverable from either end: a caller who handles one is silently
wrong about the other. ``post_prompt_data`` alone arrives three ways, and one
of them -- the object wrapped in a list under ``parsed`` -- survives every
structural check while missing every field lookup.

The chat engine additionally appends its own summary to ``call_log`` as a bare
``role: assistant`` turn. By role alone it is indistinguishable from real
speech; replayed into another medium the agent narrates a summary of itself in
the third person. Only a byte comparison against ``post_prompt_data.raw``
identifies it.
"""

from typing import Any, ClassVar

import pytest

from signalwire.core.post_prompt import (
    dialogue_turns,
    normalize_post_prompt,
    parse_post_prompt_data,
    strip_json_fence,
)

FENCED = '```json\n{"summary": "s", "already_answered": ["pricing"]}\n```'


class TestParseShapes:
    def test_flat_keys_from_the_voice_engine(self) -> None:
        assert parse_post_prompt_data({"summary": "s", "user_goal": "g"}) == {
            "summary": "s",
            "user_goal": "g",
        }

    def test_fenced_raw_from_the_chat_engine(self) -> None:
        assert parse_post_prompt_data({"raw": FENCED}) == {
            "summary": "s",
            "already_answered": ["pricing"],
        }

    def test_object_wrapped_in_a_list_under_parsed(self) -> None:
        """The shape that structurally survives and semantically vanishes."""
        assert parse_post_prompt_data(
            {"parsed": [{"summary": "s3"}], "raw": "..."}
        ) == {"summary": "s3"}

    def test_parsed_wrapper_wins_over_the_generic_sweep(self) -> None:
        """Without the unwrap this returns {"parsed": [...]} -- fine to look at,
        useless to read."""
        result = parse_post_prompt_data({"parsed": [{"summary": "s"}]})
        assert "parsed" not in result

    def test_parsed_as_a_bare_dict(self) -> None:
        assert parse_post_prompt_data({"parsed": {"summary": "s"}}) == {"summary": "s"}

    def test_prose_instead_of_json_is_kept(self) -> None:
        """A usable paragraph beats a discarded one."""
        assert parse_post_prompt_data({"raw": "They asked about pricing."}) == {
            "summary": "They asked about pricing."
        }

    def test_json_that_is_not_an_object(self) -> None:
        assert parse_post_prompt_data({"raw": '"just a string"'}) == {
            "summary": "just a string"
        }

    @pytest.mark.parametrize(
        "junk", [None, {}, "text", 42, [], {"raw": ""}, {"raw": "   "}, {"raw": None}]
    )
    def test_junk_degrades_rather_than_raising(self, junk: Any) -> None:
        """The conversation is already over; there is nobody to show an error to."""
        assert parse_post_prompt_data(junk) == {}


class TestStripFence:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ('```json\n{"a":1}\n```', '{"a":1}'),
            ("```\nplain\n```", "plain"),
            ("no fence at all", "no fence at all"),
            ("", ""),
        ],
    )
    def test_unwraps(self, raw: str, expected: str) -> None:
        assert strip_json_fence(raw) == expected


class TestDialogueTurns:
    # Deliberately heterogeneous: the last entry is not a dict at all,
    # which is exactly the malformed input this must survive.
    LOG: ClassVar[list[Any]] = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
        {"role": "system", "content": "the prompt"},
        {"role": "system-log", "content": "step trace"},
        {"role": "tool", "content": "tool output"},
        {"role": "assistant", "content": "", "tool_calls": [{"id": 1}]},
        {"role": "assistant-manual", "content": "let me look that up"},
        {"role": "assistant", "content": "   "},
        "not even a dict",
    ]

    def test_keeps_only_real_dialogue(self) -> None:
        assert dialogue_turns(self.LOG) == [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ]

    def test_drops_the_chat_summary_echo(self) -> None:
        log = [*self.LOG, {"role": "assistant", "content": FENCED}]
        assert {"role": "assistant", "content": FENCED} not in dialogue_turns(
            log, drop_echo=FENCED
        )

    def test_keeps_the_echo_when_not_asked_to_drop_it(self) -> None:
        """The voice engine delivers it as a tool call instead, so there is
        nothing to drop and a blanket rule would eat real speech."""
        log = [*self.LOG, {"role": "assistant", "content": FENCED}]
        assert len(dialogue_turns(log)) == 3

    @pytest.mark.parametrize("junk", [None, [], "nonsense", 42])
    def test_junk_logs_yield_nothing(self, junk: Any) -> None:
        assert dialogue_turns(junk) == []


class TestNormalize:
    def test_voice_body(self) -> None:
        result = normalize_post_prompt(
            {
                "conversation_type": "voice",
                "call_id": "c-1",
                "post_prompt_data": {"parsed": [{"summary": "v"}]},
                "raw_call_log": [{"role": "user", "content": "hi"}],
            }
        )
        assert result.medium == "voice"
        assert result.conversation_id is None  # voice does not send one
        assert result.summary == {"summary": "v"}
        assert result.call_id == "c-1"
        assert len(result.dialogue) == 1

    def test_chat_body(self) -> None:
        result = normalize_post_prompt(
            {
                "conversation_type": "chat",
                "conversation_id": "conv-9",
                "post_prompt_data": {"raw": FENCED},
                "raw_messages": [
                    {"role": "user", "content": "hi"},
                    {"role": "assistant", "content": FENCED},
                ],
            }
        )
        assert result.medium == "chat"
        assert result.conversation_id == "conv-9"
        assert result.summary["already_answered"] == ["pricing"]
        # The echo is gone; only the real turn survives.
        assert result.dialogue == [{"role": "user", "content": "hi"}]

    def test_call_log_key_is_also_accepted(self) -> None:
        result = normalize_post_prompt(
            {"call_log": [{"role": "user", "content": "hi"}]}
        )
        assert len(result.dialogue) == 1

    @pytest.mark.parametrize("junk", [None, "text", 42, []])
    def test_junk_body_yields_empty_fields(self, junk: Any) -> None:
        result = normalize_post_prompt(junk)
        assert result.medium == ""
        assert result.summary == {}
        assert result.dialogue == []

    def test_raw_is_preserved(self) -> None:
        body = {"conversation_type": "voice", "extra": "kept"}
        assert normalize_post_prompt(body).raw is body
