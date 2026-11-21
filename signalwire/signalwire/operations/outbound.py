"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Outbound calls placed only after your checks pass. A ``Dialer`` runs every
check against the person to be called (consent, the hours they may be called
in their own time zone, a do-not-call list, anything of yours) and dials only
when none objects; otherwise it raises ``NotPlaced`` with the reason, and no
request is made. Pacing, retries and outcomes are your scheduler's: call
``place`` from it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, time, timezone
from typing import Any
from urllib.parse import urlencode
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True)
class Callee:
    """The person to be called."""

    number: str
    """Their number, in E.164 form."""
    zone: str
    """Their time zone, an IANA name such as ``"America/Chicago"``: the hours they may be called are theirs."""
    data: Mapping[str, Any] = field(default_factory=dict)
    """What the call is about, passed to the agent as query parameters of its URL."""


class NotPlaced(Exception):
    """Raised by ``Dialer.place`` instead of dialing: a check objected."""

    def __init__(self, callee: Callee, reason: str) -> None:
        super().__init__(f"not calling {callee.number}: {reason}")
        self.callee = callee
        self.reason = reason


Check = Callable[[Callee, datetime], "str | None"]
"""``check(callee, now)`` returns why the call can't be placed now, or None. ``now`` is aware (UTC)."""


def calling_hours(
    start: time, end: time, *, days: Sequence[int] | None = None
) -> Check:
    """
    A check that the callee's own clock is within ``start``..``end`` (and on
    one of ``days``, Monday 0 to Sunday 6, when given).

    Args:
        start: The earliest local time a call may start.
        end: The latest local time a call may start.
        days: The weekdays calls may be placed on; None for every day.
    """
    allowed = set(days) if days is not None else None

    def check(callee: Callee, now: datetime) -> str | None:
        local = now.astimezone(_zone(callee))
        if allowed is not None and local.weekday() not in allowed:
            return f"not a calling day where they are ({local:%A} in {callee.zone})"
        if not start <= local.time() <= end:
            return f"outside the calling hours, it is {local:%H:%M} in {callee.zone}"
        return None

    return check


def consented(lookup: Callable[[Callee], bool | None]) -> Check:
    """
    A check that ``lookup(callee)`` is True: consent on record. False is
    withdrawn consent, None none on record; either stops the call.
    """

    def check(callee: Callee, now: datetime) -> str | None:
        given = lookup(callee)
        if given is None:
            return "no consent on record"
        return None if given else "consent withdrawn"

    return check


class Dialer:
    """
    Places outbound calls to an agent, once every check passes.

    Example:
        dialer = Dialer(
            RestClient(),
            from_number="+15550001111",
            url="https://agents.example.com/reminders",
            checks=[consented(lambda c: CONSENT.get(c.number)), calling_hours(time(9), time(20))],
        )
        try:
            dialer.place(Callee("+15557654321", "America/Los_Angeles", {"appointment": "a1"}))
        except NotPlaced as e:
            log.info(e.reason)
    """

    def __init__(
        self,
        client: Any,
        *,
        from_number: str,
        url: str | None = None,
        swml: Mapping[str, Any] | None = None,
        checks: Sequence[Check] = (),
        timeout: int | None = None,
        status_url: str | None = None,
        status_events: Sequence[str] | None = None,
    ) -> None:
        """
        Args:
            client: A ``RestClient``.
            from_number: The number calls come from.
            url: The agent's URL; the callee's ``data`` goes on it as query
                parameters, for the agent's per-request configuration.
            swml: A SWML document to run instead of an agent at a URL.
            checks: What must pass before a call is placed, in order: the
                first objection stops it.
            timeout: How long to ring, in seconds; the platform's default
                when None.
            status_url: Where the platform posts the call's progress.
            status_events: Which progress events to post, such as
                ``["answered", "ended"]``.
        """
        if (url is None) == (swml is None):
            raise ValueError(
                "Dialer takes url= (an agent) or swml= (a document), one of them"
            )
        self._client, self._from = client, from_number
        self._url, self._swml = url, dict(swml) if swml is not None else None
        self._checks = list(checks)
        self._timeout, self._status_url = timeout, status_url
        self._events = list(status_events) if status_events else None

    def why_not(self, callee: Callee, now: datetime | None = None) -> str | None:
        """
        Why a call to ``callee`` can't be placed now, or None when every check
        passes.

        Args:
            callee: The person to be called.
            now: The time to check at, for tests; it must carry a time zone.
                Defaults to the current time.
        """
        _zone(callee)
        when = _now(now)
        for check in self._checks:
            reason = check(callee, when)
            if reason:
                return reason
        return None

    def place(self, callee: Callee, now: datetime | None = None) -> Any:
        """
        Dial ``callee`` once every check passes; raises ``NotPlaced`` with the
        first objection otherwise, and makes no request. Returns the
        platform's answer to the dial.
        """
        reason = self.why_not(callee, now)
        if reason:
            raise NotPlaced(callee, reason)
        params: dict[str, Any] = {"from_": self._from, "to": callee.number}
        if self._url is not None:
            query = urlencode({k: str(v) for k, v in callee.data.items()})
            params["url"] = (
                f"{self._url}{'&' if '?' in self._url else '?'}{query}"
                if query
                else self._url
            )
        else:
            params["swml"] = self._swml
        if self._status_url:
            params["status_url"] = self._status_url
        if self._events:
            params["status_events"] = self._events
        if self._timeout is not None:
            params["extras"] = {"timeout": self._timeout}
        return self._client.calling.dial(**params)


def _zone(callee: Callee) -> ZoneInfo:
    try:
        return ZoneInfo(callee.zone)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError(
            f"{callee.zone!r} isn't a time zone; give an IANA name such as 'America/Chicago'"
        ) from None


def _now(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.utcoffset() is None:
        raise ValueError(
            "now must carry a time zone; a naive time would be read in the server's zone"
        )
    return now.astimezone(timezone.utc)


__all__ = ["Callee", "Check", "Dialer", "NotPlaced", "calling_hours", "consented"]
