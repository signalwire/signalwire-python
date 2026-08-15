"""Reading what a client declares it can render.

Both ends of this convention are SignalWire's -- the address widget writes it,
the SDK reads it -- which is the only reason it belongs here rather than in
each application.

The rule these tests exist to pin is that **absence means no**. Every path
resolves malformed or missing data to "not declared", because offering a caller
something they cannot reach is worse than never mentioning it: a PSTN caller
has no browser, and an agent that offers to put something on their screen has
simply lied to them.
"""

from typing import Any

import pytest

from signalwire.core.capabilities import (
    declared_capabilities,
    has_capability,
    user_variables,
)

BODY: dict[str, Any] = {
    "vars": {
        "userVariables": {
            "capabilities": {
                "display_content": True,
                "transcript": True,
                "chat_handoff": False,
            },
            "metadata": {"widget": {"opened_at": "2026-01-01T00:00:00Z"}},
        }
    }
}


class TestUserVariables:
    def test_extracts_from_the_nested_shape(self) -> None:
        assert "capabilities" in user_variables(BODY)

    @pytest.mark.parametrize(
        "junk",
        [
            None,
            {},
            "nonsense",
            42,
            {"vars": None},
            {"vars": {}},
            {"vars": {"userVariables": None}},
            {"vars": {"userVariables": "not a dict"}},
        ],
    )
    def test_missing_levels_yield_an_empty_dict(self, junk: Any) -> None:
        assert user_variables(junk) == {}


class TestDeclaredCapabilities:
    def test_only_truthy_names_are_returned(self) -> None:
        assert declared_capabilities(BODY) == frozenset(
            {"display_content", "transcript"}
        )

    def test_false_is_not_a_declaration(self) -> None:
        assert "chat_handoff" not in declared_capabilities(BODY)

    def test_accepts_already_extracted_user_variables(self) -> None:
        """Callers hold one or the other depending on where they are."""
        assert declared_capabilities({"capabilities": {"a": True}}) == frozenset({"a"})

    def test_a_name_this_sdk_has_never_heard_of_still_passes_through(self) -> None:
        """The producer evolves by adding booleans; an SDK release per
        capability would invert that."""
        assert has_capability({"capabilities": {"future_thing": True}}, "future_thing")

    @pytest.mark.parametrize(
        "junk",
        [
            None,
            {},
            "nonsense",
            42,
            {"vars": {"userVariables": {"capabilities": "not a dict"}}},
            {"vars": {"userVariables": {"capabilities": None}}},
            {"vars": {"userVariables": {}}},
        ],
    )
    def test_absence_and_malformation_both_mean_no(self, junk: Any) -> None:
        assert declared_capabilities(junk) == frozenset()
        assert not has_capability(junk, "display_content")


class TestHasCapability:
    def test_declared(self) -> None:
        assert has_capability(BODY, "display_content")

    def test_declared_false(self) -> None:
        assert not has_capability(BODY, "chat_handoff")

    def test_never_mentioned(self) -> None:
        assert not has_capability(BODY, "telepathy")
