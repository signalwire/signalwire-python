"""Typed event wrappers for RELAY calling events.

These are convenience dataclasses over raw event dicts. All Call event handlers
also accept the raw dict, so these are optional.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RelayEvent:
    """Base event — wraps the raw params dict from a signalwire.event message."""

    event_type: str
    params: dict[str, Any]
    call_id: str = ""
    timestamp: float = 0.0

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RelayEvent":
        event_type = payload.get("event_type", "")
        params = payload.get("params", {})
        return cls(
            event_type=event_type,
            params=params,
            call_id=params.get("call_id", ""),
            timestamp=params.get("timestamp", 0.0),
        )


@dataclass
class CallStateEvent(RelayEvent):
    """Event for calling.call.state."""

    call_state: str = ""
    end_reason: str = ""
    direction: str = ""
    device: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "CallStateEvent":
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            call_state=p.get("call_state", ""),
            end_reason=p.get("end_reason", ""),
            direction=p.get("direction", ""),
            device=p.get("device", {}),
        )


@dataclass
class CallReceiveEvent(RelayEvent):
    """Event for calling.call.receive — inbound call notification."""

    call_state: str = ""
    direction: str = ""
    device: dict[str, Any] = field(default_factory=dict)
    node_id: str = ""
    project_id: str = ""
    context: str = ""
    segment_id: str = ""
    tag: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "CallReceiveEvent":
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            call_state=p.get("call_state", ""),
            direction=p.get("direction", ""),
            device=p.get("device", {}),
            node_id=p.get("node_id", ""),
            project_id=p.get("project_id", ""),
            context=p.get("context", p.get("protocol", "")),
            segment_id=p.get("segment_id", ""),
            tag=p.get("tag", ""),
        )


@dataclass
class PlayEvent(RelayEvent):
    """Event for calling.call.play."""

    control_id: str = ""
    state: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "PlayEvent":
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            control_id=p.get("control_id", ""),
            state=p.get("state", ""),
        )


@dataclass
class RecordEvent(RelayEvent):
    """Event for calling.call.record."""

    control_id: str = ""
    state: str = ""
    url: str = ""
    duration: float = 0.0
    size: int = 0
    record: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RecordEvent":
        base = RelayEvent.from_payload(payload)
        p = base.params
        rec = p.get("record", {})
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            control_id=p.get("control_id", ""),
            state=p.get("state", ""),
            url=rec.get("url", p.get("url", "")),
            duration=rec.get("duration", p.get("duration", 0.0)),
            size=rec.get("size", p.get("size", 0)),
            record=rec,
        )


@dataclass
class CollectEvent(RelayEvent):
    """Event for calling.call.collect."""

    control_id: str = ""
    result: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "CollectEvent":
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            control_id=p.get("control_id", ""),
            result=p.get("result", {}),
        )


@dataclass
class ConnectEvent(RelayEvent):
    """Event for calling.call.connect."""

    connect_state: str = ""
    peer: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ConnectEvent":
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            connect_state=p.get("connect_state", ""),
            peer=p.get("peer", {}),
        )


@dataclass
class DetectEvent(RelayEvent):
    """Event for calling.call.detect."""

    control_id: str = ""
    detect: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "DetectEvent":
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            control_id=p.get("control_id", ""),
            detect=p.get("detect", {}),
        )


# Map event_type string → typed event class
EVENT_CLASS_MAP: dict[str, type[RelayEvent]] = {
    "calling.call.state": CallStateEvent,
    "calling.call.receive": CallReceiveEvent,
    "calling.call.play": PlayEvent,
    "calling.call.record": RecordEvent,
    "calling.call.collect": CollectEvent,
    "calling.call.connect": ConnectEvent,
    "calling.call.detect": DetectEvent,
}


def parse_event(payload: dict[str, Any]) -> RelayEvent:
    """Parse a raw signalwire.event params dict into a typed event object."""
    event_type = payload.get("event_type", "")
    cls = EVENT_CLASS_MAP.get(event_type, RelayEvent)
    return cls.from_payload(payload)
