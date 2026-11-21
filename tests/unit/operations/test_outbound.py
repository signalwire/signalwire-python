"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The Dialer places a call only once every check passes, in the callee's own
time zone.
"""

from __future__ import annotations

from datetime import datetime, time, timezone
from typing import Any

import pytest

from signalwire.operations.outbound import Callee, Dialer, NotPlaced, calling_hours, consented


class Calling:
    def __init__(self) -> None:
        self.dialed: list[dict[str, Any]] = []

    def dial(self, **params: Any) -> dict[str, Any]:
        self.dialed.append(params)
        return {"id": "c1"}


class Client:
    def __init__(self) -> None:
        self.calling = Calling()


CONSENT = {"+15557654321": True, "+15550009999": False}
FRIDAY_1800_UTC = datetime(2026, 11, 20, 18, 0, tzinfo=timezone.utc)  # a Friday: 10:00 in Los Angeles


def dialer(client: Client, **kwargs: Any) -> Dialer:
    return Dialer(client, from_number="+15550001111", url="https://agents.example.com/reminders",
                  checks=[consented(lambda c: CONSENT.get(c.number)), calling_hours(time(9), time(20))], **kwargs)


def test_a_call_is_placed_once_every_check_passes() -> None:
    client = Client()
    out = dialer(client, timeout=25, status_url="https://x/status", status_events=["ended"]).place(
        Callee("+15557654321", "America/Los_Angeles", {"appointment": "a1"}), now=FRIDAY_1800_UTC)
    assert out == {"id": "c1"}
    assert client.calling.dialed == [{
        "from_": "+15550001111", "to": "+15557654321",
        "url": "https://agents.example.com/reminders?appointment=a1",
        "status_url": "https://x/status", "status_events": ["ended"], "extras": {"timeout": 25},
    }]


@pytest.mark.parametrize(("number", "zone", "reason"), [
    ("+15550009999", "America/New_York", "consent withdrawn"),
    ("+15550000000", "America/New_York", "no consent on record"),
    ("+15557654321", "Asia/Tokyo", "outside the calling hours, it is 03:00 in Asia/Tokyo"),
])
def test_an_objection_places_nothing(number: str, zone: str, reason: str) -> None:
    client = Client()
    with pytest.raises(NotPlaced) as e:
        dialer(client).place(Callee(number, zone), now=FRIDAY_1800_UTC)
    assert e.value.reason == reason and client.calling.dialed == []


def test_calling_days_and_bad_input() -> None:
    weekdays = Dialer(Client(), from_number="+1", swml={"version": "1.0.0", "sections": {"main": []}},
                      checks=[calling_hours(time(0), time(23, 59), days=[0, 1, 2, 3])])
    assert weekdays.why_not(Callee("+1555", "UTC"), now=FRIDAY_1800_UTC) == "not a calling day where they are (Friday in UTC)"
    with pytest.raises(ValueError, match="time zone"):
        weekdays.why_not(Callee("+1555", "Mars/Olympus"))
    with pytest.raises(ValueError, match="carry a time zone"):
        weekdays.why_not(Callee("+1555", "UTC"), now=datetime(2026, 11, 20, 12, 0))
    with pytest.raises(ValueError, match="one of them"):
        Dialer(Client(), from_number="+1")
