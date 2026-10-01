"""Typed event wrappers for RELAY calling events.

These are convenience dataclasses over raw event dicts. All Call event handlers
also accept the raw dict, so these are optional.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RelayEvent:
    """Base event — wraps the raw params dict from a signalwire.event message."""

    event_type: str
    params: dict[str, Any]
    call_id: str = ""
    timestamp: float = 0.0

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> RelayEvent:
        """Build a RelayEvent from a raw ``signalwire.event`` message payload.

        Reads ``event_type`` from the top level and ``call_id``/``timestamp`` out of
        the nested ``params`` object, keeping the whole ``params`` dict so callers can
        reach fields this wrapper does not model.

        Args:
            payload: The raw event payload dict from the RELAY WebSocket message.

        Returns:
            A RelayEvent carrying the event type, the raw params and the call id.
        """
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
    def from_payload(cls, payload: dict[str, Any]) -> CallStateEvent:
        """Build a CallStateEvent from a ``calling.call.state`` payload.

        Adds the call's lifecycle fields on top of the base event: ``call_state``
        (created/ringing/answered/ending/ended), ``end_reason``, ``direction`` and the
        ``device`` object describing the endpoint.

        Args:
            payload: The raw event payload dict.

        Returns:
            A CallStateEvent with the state fields extracted from ``params``.
        """
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
    def from_payload(cls, payload: dict[str, Any]) -> CallReceiveEvent:
        """Build a CallReceiveEvent from a ``calling.call.receive`` payload.

        This is the inbound-call notification, so it carries the routing identity a
        handler needs to decide whether to answer: ``node_id``, ``project_id``,
        ``context``, ``segment_id`` and ``tag``, alongside the call's ``call_state``,
        ``direction`` and ``device``.

        ``context`` falls back to the payload's ``protocol`` field when ``context`` is
        absent, because older RELAY servers name the same value ``protocol``.

        Args:
            payload: The raw event payload dict.

        Returns:
            A CallReceiveEvent describing the inbound call.
        """
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
    def from_payload(cls, payload: dict[str, Any]) -> PlayEvent:
        """Build a PlayEvent from a ``calling.call.play`` payload.

        Carries the ``control_id`` identifying the play operation and its ``state``
        (playing/paused/finished/error), which is how a caller correlates the event
        with the play it started.

        Args:
            payload: The raw event payload dict.

        Returns:
            A PlayEvent for the play operation named by ``control_id``.
        """
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
    def from_payload(cls, payload: dict[str, Any]) -> RecordEvent:
        """Build a RecordEvent from a ``calling.call.record`` payload.

        The recording's ``url``, ``duration`` and ``size`` are read from the nested
        ``record`` object when present and from the top level of ``params`` otherwise,
        since RELAY reports them in either position depending on the event stage. The
        whole ``record`` object is kept on the event so callers can read fields this
        wrapper does not model.

        Args:
            payload: The raw event payload dict.

        Returns:
            A RecordEvent with the recording metadata and its ``state``.
        """
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
    state: str = ""
    result: dict[str, Any] = field(default_factory=dict)
    final: bool | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> CollectEvent:
        """Build a CollectEvent from a ``calling.call.collect`` payload.

        Carries the ``result`` object holding what was collected (digits or speech)
        and ``final``, which distinguishes an interim result from the last one. Note
        ``final`` stays ``None`` when the payload omits it — absent is not False.

        Args:
            payload: The raw event payload dict.

        Returns:
            A CollectEvent for the collect operation named by ``control_id``.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            control_id=p.get("control_id", ""),
            state=p.get("state", ""),
            result=p.get("result", {}),
            final=p.get("final"),
        )


@dataclass
class ConnectEvent(RelayEvent):
    """Event for calling.call.connect."""

    connect_state: str = ""
    peer: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ConnectEvent:
        """Build a ConnectEvent from a ``calling.call.connect`` payload.

        Carries ``connect_state`` (connecting/connected/disconnected/failed) and the
        ``peer`` object identifying the far end of the connection.

        Args:
            payload: The raw event payload dict.

        Returns:
            A ConnectEvent describing the connection attempt.
        """
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
    def from_payload(cls, payload: dict[str, Any]) -> DetectEvent:
        """Build a DetectEvent from a ``calling.call.detect`` payload.

        Keeps the whole ``detect`` object, whose shape depends on the detector that
        produced it (machine, fax or DTMF), rather than flattening one detector's
        fields onto the event.

        Args:
            payload: The raw event payload dict.

        Returns:
            A DetectEvent for the detect operation named by ``control_id``.
        """
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


@dataclass
class FaxEvent(RelayEvent):
    """Event for calling.call.fax."""

    control_id: str = ""
    fax: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> FaxEvent:
        """Build a FaxEvent from a ``calling.call.fax`` payload.

        Keeps the whole ``fax`` object, which carries the direction-specific result
        (pages, identity, document URL) for the send or receive operation.

        Args:
            payload: The raw event payload dict.

        Returns:
            A FaxEvent for the fax operation named by ``control_id``.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            control_id=p.get("control_id", ""),
            fax=p.get("fax", {}),
        )


@dataclass
class TapEvent(RelayEvent):
    """Event for calling.call.tap."""

    control_id: str = ""
    state: str = ""
    tap: dict[str, Any] = field(default_factory=dict)
    device: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> TapEvent:
        """Build a TapEvent from a ``calling.call.tap`` payload.

        Carries the tap's ``state`` plus two objects: ``tap`` describing the media
        being tapped and ``device`` describing where it is being sent.

        Args:
            payload: The raw event payload dict.

        Returns:
            A TapEvent for the tap operation named by ``control_id``.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            control_id=p.get("control_id", ""),
            state=p.get("state", ""),
            tap=p.get("tap", {}),
            device=p.get("device", {}),
        )


@dataclass
class StreamEvent(RelayEvent):
    """Event for calling.call.stream."""

    control_id: str = ""
    state: str = ""
    url: str = ""
    name: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> StreamEvent:
        """Build a StreamEvent from a ``calling.call.stream`` payload.

        Carries the stream's ``state``, the destination ``url`` and the caller-assigned
        ``name`` used to address the stream in later requests.

        Args:
            payload: The raw event payload dict.

        Returns:
            A StreamEvent for the stream operation named by ``control_id``.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            control_id=p.get("control_id", ""),
            state=p.get("state", ""),
            url=p.get("url", ""),
            name=p.get("name", ""),
        )


@dataclass
class SendDigitsEvent(RelayEvent):
    """Event for calling.call.send_digits."""

    control_id: str = ""
    state: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> SendDigitsEvent:
        """Build a SendDigitsEvent from a ``calling.call.send_digits`` payload.

        Carries the ``state`` of the DTMF send, which is how a caller knows the digits
        have finished playing out.

        Args:
            payload: The raw event payload dict.

        Returns:
            A SendDigitsEvent for the operation named by ``control_id``.
        """
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
class DialEvent(RelayEvent):
    """Event for calling.call.dial."""

    tag: str = ""
    dial_state: str = ""
    call: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> DialEvent:
        """Build a DialEvent from a ``calling.call.dial`` payload.

        A dial is correlated by ``tag`` rather than ``control_id``. Carries
        ``dial_state`` and, once the dial succeeds, the ``call`` object describing the
        call that was created.

        Args:
            payload: The raw event payload dict.

        Returns:
            A DialEvent for the dial identified by ``tag``.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            tag=p.get("tag", ""),
            dial_state=p.get("dial_state", ""),
            call=p.get("call", {}),
        )


@dataclass
class ReferEvent(RelayEvent):
    """Event for calling.call.refer."""

    state: str = ""
    sip_refer_to: str = ""
    sip_refer_response_code: str = ""
    sip_notify_response_code: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ReferEvent:
        """Build a ReferEvent from a ``calling.call.refer`` payload.

        Carries the SIP REFER outcome: ``sip_refer_to`` (the target), plus the two
        response codes that report it — ``sip_refer_response_code`` for the REFER
        itself and ``sip_notify_response_code`` for the NOTIFY that reports the
        transfer result.

        Args:
            payload: The raw event payload dict.

        Returns:
            A ReferEvent describing the REFER and its responses.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            state=p.get("state", ""),
            sip_refer_to=p.get("sip_refer_to", ""),
            sip_refer_response_code=p.get("sip_refer_response_code", ""),
            sip_notify_response_code=p.get("sip_notify_response_code", ""),
        )


@dataclass
class DenoiseEvent(RelayEvent):
    """Event for calling.call.denoise."""

    denoised: bool = False

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> DenoiseEvent:
        """Build a DenoiseEvent from a ``calling.call.denoise`` payload.

        Carries ``denoised``, the boolean reporting whether noise reduction is now
        active on the call.

        Args:
            payload: The raw event payload dict.

        Returns:
            A DenoiseEvent reporting the denoise state.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            denoised=p.get("denoised", False),
        )


@dataclass
class PayEvent(RelayEvent):
    """Event for calling.call.pay."""

    control_id: str = ""
    state: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> PayEvent:
        """Build a PayEvent from a ``calling.call.pay`` payload.

        Carries the ``state`` of the payment session so a caller can follow it through
        to completion or failure.

        Args:
            payload: The raw event payload dict.

        Returns:
            A PayEvent for the pay operation named by ``control_id``.
        """
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
class QueueEvent(RelayEvent):
    """Event for calling.call.queue."""

    control_id: str = ""
    status: str = ""
    queue_id: str = ""
    queue_name: str = ""
    position: int = 0
    size: int = 0

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> QueueEvent:
        """Build a QueueEvent from a ``calling.call.queue`` payload.

        Carries the queue's identity (``queue_id``, ``queue_name``) and the call's
        place in it (``position`` within a queue of ``size``), alongside the
        operation ``status``.

        Args:
            payload: The raw event payload dict.

        Returns:
            A QueueEvent describing the call's position in the queue.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            control_id=p.get("control_id", ""),
            status=p.get("status", ""),
            queue_id=p.get("id", ""),
            queue_name=p.get("name", ""),
            position=p.get("position", 0),
            size=p.get("size", 0),
        )


@dataclass
class EchoEvent(RelayEvent):
    """Event for calling.call.echo."""

    state: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> EchoEvent:
        """Build an EchoEvent from a ``calling.call.echo`` payload.

        Carries the ``state`` of the echo operation, which loops the call's audio
        back to the caller for connectivity testing.

        Args:
            payload: The raw event payload dict.

        Returns:
            An EchoEvent reporting the echo state.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            state=p.get("state", ""),
        )


@dataclass
class TranscribeEvent(RelayEvent):
    """Event for calling.call.transcribe."""

    control_id: str = ""
    state: str = ""
    url: str = ""
    recording_id: str = ""
    duration: float = 0.0
    size: int = 0

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> TranscribeEvent:
        """Build a TranscribeEvent from a ``calling.call.transcribe`` payload.

        Carries the transcription's ``state`` plus the artifact it produced: ``url``,
        ``recording_id``, ``duration`` and ``size``. Unlike RecordEvent these are read
        only from the top level of ``params`` — transcribe has no nested object.

        Args:
            payload: The raw event payload dict.

        Returns:
            A TranscribeEvent for the operation named by ``control_id``.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            control_id=p.get("control_id", ""),
            state=p.get("state", ""),
            url=p.get("url", ""),
            recording_id=p.get("recording_id", ""),
            duration=p.get("duration", 0.0),
            size=p.get("size", 0),
        )


@dataclass
class HoldEvent(RelayEvent):
    """Event for calling.call.hold."""

    state: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> HoldEvent:
        """Build a HoldEvent from a ``calling.call.hold`` payload.

        Carries the ``state`` reporting whether the call is now held or resumed.

        Args:
            payload: The raw event payload dict.

        Returns:
            A HoldEvent reporting the hold state.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            state=p.get("state", ""),
        )


@dataclass
class ConferenceEvent(RelayEvent):
    """Event for calling.conference."""

    conference_id: str = ""
    name: str = ""
    status: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ConferenceEvent:
        """Build a ConferenceEvent from a ``calling.conference`` payload.

        Carries the conference's identity (``conference_id``, ``name``) and its
        ``status``. Note this is a conference-scoped event rather than a call-scoped
        one, so the inherited ``call_id`` may be empty.

        Args:
            payload: The raw event payload dict.

        Returns:
            A ConferenceEvent describing the conference state change.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            conference_id=p.get("conference_id", ""),
            name=p.get("name", ""),
            status=p.get("status", ""),
        )


@dataclass
class CallingErrorEvent(RelayEvent):
    """Event for calling.error."""

    code: str = ""
    message: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> CallingErrorEvent:
        """Build a CallingErrorEvent from a ``calling.error`` payload.

        Carries the error ``code`` and human-readable ``message`` reported by the
        calling service. This is the event a handler inspects when an operation fails
        rather than transitioning to its next state.

        Args:
            payload: The raw event payload dict.

        Returns:
            A CallingErrorEvent carrying the error code and message.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            code=p.get("code", ""),
            message=p.get("message", ""),
        )


@dataclass
class MessageReceiveEvent(RelayEvent):
    """Event for messaging.receive — inbound message notification."""

    message_id: str = ""
    context: str = ""
    direction: str = ""
    from_number: str = ""
    to_number: str = ""
    body: str = ""
    media: list[str] = field(default_factory=list)
    segments: int = 0
    message_state: str = ""
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> MessageReceiveEvent:
        """Build a MessageReceiveEvent from a ``messaging.receive`` payload.

        This is the inbound-message notification. Carries the message identity
        (``message_id``, ``context``, ``tags``), its addressing (``from_number``,
        ``to_number``, ``direction``) and its content (``body``, ``media`` URLs and the
        ``segments`` count), plus ``message_state``.

        Args:
            payload: The raw event payload dict.

        Returns:
            A MessageReceiveEvent describing the inbound message.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            message_id=p.get("message_id", ""),
            context=p.get("context", ""),
            direction=p.get("direction", ""),
            from_number=p.get("from_number", ""),
            to_number=p.get("to_number", ""),
            body=p.get("body", ""),
            media=p.get("media", []),
            segments=p.get("segments", 0),
            message_state=p.get("message_state", ""),
            tags=p.get("tags", []),
        )


@dataclass
class MessageStateEvent(RelayEvent):
    """Event for messaging.state — outbound message state change."""

    message_id: str = ""
    context: str = ""
    direction: str = ""
    from_number: str = ""
    to_number: str = ""
    body: str = ""
    media: list[str] = field(default_factory=list)
    segments: int = 0
    message_state: str = ""
    reason: str = ""
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> MessageStateEvent:
        """Build a MessageStateEvent from a ``messaging.state`` payload.

        Reports a state change on an OUTBOUND message. Carries the same identity,
        addressing and content fields as MessageReceiveEvent, plus ``reason`` — which
        is what explains a failed or undelivered ``message_state``.

        Args:
            payload: The raw event payload dict.

        Returns:
            A MessageStateEvent describing the outbound message's new state.
        """
        base = RelayEvent.from_payload(payload)
        p = base.params
        return cls(
            event_type=base.event_type,
            params=base.params,
            call_id=base.call_id,
            timestamp=base.timestamp,
            message_id=p.get("message_id", ""),
            context=p.get("context", ""),
            direction=p.get("direction", ""),
            from_number=p.get("from_number", ""),
            to_number=p.get("to_number", ""),
            body=p.get("body", ""),
            media=p.get("media", []),
            segments=p.get("segments", 0),
            message_state=p.get("message_state", ""),
            reason=p.get("reason", ""),
            tags=p.get("tags", []),
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
    "calling.call.fax": FaxEvent,
    "calling.call.tap": TapEvent,
    "calling.call.stream": StreamEvent,
    "calling.call.send_digits": SendDigitsEvent,
    "calling.call.dial": DialEvent,
    "calling.call.refer": ReferEvent,
    "calling.call.denoise": DenoiseEvent,
    "calling.call.pay": PayEvent,
    "calling.call.queue": QueueEvent,
    "calling.call.echo": EchoEvent,
    "calling.call.transcribe": TranscribeEvent,
    "calling.call.hold": HoldEvent,
    "calling.conference": ConferenceEvent,
    "calling.error": CallingErrorEvent,
    "messaging.receive": MessageReceiveEvent,
    "messaging.state": MessageStateEvent,
}


def parse_event(payload: dict[str, Any]) -> RelayEvent:
    """Parse a raw signalwire.event params dict into a typed event object."""
    event_type = payload.get("event_type", "")
    cls = EVENT_CLASS_MAP.get(event_type, RelayEvent)
    return cls.from_payload(payload)
