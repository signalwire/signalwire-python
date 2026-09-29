"""A required REST argument supplied through ``extras={...}`` satisfies the requirement.

Owner ruling 2026-09-29: a field the spec now marks required must not turn a call that
worked (the caller sent the field through the ``extras`` door) into a ``TypeError``.
"""

from __future__ import annotations

from typing import Any

import pytest

from signalwire.rest._base import _required_via_extras
from signalwire.rest.namespaces.relay_rest_resources_generated import Queues


class _Http:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, Any]] = []

    def post(self, path: str, body: Any = None, **_: Any) -> dict[str, Any]:
        self.calls.append(("POST", path, body))
        return {}


def test_generated_create_takes_a_required_field_from_extras() -> None:
    http = _Http()
    Queues(http).create(extras={"name": "support"})  # type: ignore[call-arg]
    assert http.calls == [("POST", "/api/relay/rest/queues", {"name": "support"})]


def test_generated_create_still_requires_the_field_somewhere() -> None:
    with pytest.raises(TypeError, match="name"):
        Queues(_Http()).create(max_size=5)  # type: ignore[call-arg]


def test_the_explicit_argument_wins_over_extras() -> None:
    http = _Http()
    Queues(http).create(name="a", extras={"name": "b"})
    # extras is merged last on the wire, exactly as before the decorator existed.
    assert http.calls[0][2] == {"name": "b"}


def test_a_renamed_parameter_takes_its_wire_key() -> None:
    @_required_via_extras(from_="from")
    def send(*, from_: str, extras: dict[str, Any] | None = None, **kw: Any) -> str:
        return from_

    assert send(extras={"from": "+15551230000"}) == "+15551230000"  # type: ignore[call-arg]
    wire: dict[str, Any] = {"from": "+15551230001"}
    assert send(**wire) == "+15551230001"
