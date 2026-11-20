"""Typed event wrappers for RELAY calling events.

These are convenience dataclasses over raw event dicts. All Call event handlers
also accept the raw dict, so these are optional.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RelayEvent:
    """Base event — wraps the raw params dict from a signalwire.event message.

    Used directly for event types that have no typed subclass.

    Attributes:
        event_type: The event type string, such as `calling.call.state` or
            `messaging.receive`.
        params: The raw parameters dict from the payload, including fields the
            typed subclasses do not surface.
        call_id: The call identifier from `params`, or an empty string.
        timestamp: The server timestamp from `params`, or 0.0.
    """

    event_type: str
    params: dict[str, Any]
    call_id: str = ""
    timestamp: float = 0.0

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> RelayEvent:
        """Build a `RelayEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `RelayEvent` populated from the payload's `params`.
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
    """Event for `calling.call.state`. Emitted when the call state changes.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        call_state: The new call state: `created`, `ringing`, `answered`,
            `ending` or `ended`.
        end_reason: Why the call ended, once the platform reports it. One of
            `hangup`, `cancel`, `busy`, `noAnswer`, `decline`, `error`,
            `abandoned`, `maxDuration` or `notFound`. Empty otherwise.
        direction: Call direction.
        device: Device information for the call endpoint.
    """

    call_state: str = ""
    end_reason: str = ""
    direction: str = ""
    device: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> CallStateEvent:
        """Build a `CallStateEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `CallStateEvent` populated from the payload's `params`.
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
    """Event for `calling.call.receive`.

    Inbound call notification. The client delivers it to the handler registered with
    `RelayClient.on_call`.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        call_state: Initial call state.
        direction: Call direction.
        device: Device information for the caller.
        node_id: Identifier of the node handling the call.
        project_id: SignalWire project ID.
        context: The context the call was received on. Falls back to the payload's
            `protocol` key when `context` is absent.
        segment_id: Call segment identifier.
        tag: Correlation tag for the call.
    """

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
        """Build a `CallReceiveEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `CallReceiveEvent` populated from the payload's `params`.
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
    """Event for `calling.call.play`. Emitted when a play operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        control_id: Control ID of the play operation.
        state: Playback state.
    """

    control_id: str = ""
    state: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> PlayEvent:
        """Build a `PlayEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `PlayEvent` populated from the payload's `params`.
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
    """Event for `calling.call.record`. Emitted when a record operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        control_id: Control ID of the record operation.
        state: Recording state. Includes `recording`, `finished` and `no_input`.
        url: URL of the recording file.
        duration: Recording duration in seconds.
        size: Recording file size in bytes.
        record: The full record metadata object from the payload.
    """

    control_id: str = ""
    state: str = ""
    url: str = ""
    duration: float = 0.0
    size: int = 0
    record: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> RecordEvent:
        """Build a `RecordEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `RecordEvent` populated from the payload's `params`.
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
    """Event for `calling.call.collect`.

    Emitted when a collect or play-and-collect operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        control_id: Control ID of the collect operation.
        state: Collection state.
        result: The collected input result. Its `type` key names the kind of result,
            such as `digit`, `speech`, `no_input` or `no_match`.
        final: Whether this is the final result. `None` when the payload has no `final`
            key.
    """

    control_id: str = ""
    state: str = ""
    result: dict[str, Any] = field(default_factory=dict)
    final: bool | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> CollectEvent:
        """Build a `CollectEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `CollectEvent` populated from the payload's `params`.
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
    """Event for `calling.call.connect`. Emitted when a connect operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        connect_state: Connection state.
        peer: Information about the connected peer call.
    """

    connect_state: str = ""
    peer: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ConnectEvent:
        """Build a `ConnectEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `ConnectEvent` populated from the payload's `params`.
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
    """Event for `calling.call.detect`.

    Emitted when a detect operation reports a result.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        control_id: Control ID of the detect operation.
        detect: Detection result. Its structure depends on the detection type.
    """

    control_id: str = ""
    detect: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> DetectEvent:
        """Build a `DetectEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `DetectEvent` populated from the payload's `params`.
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
    """Event for `calling.call.fax`.

    Emitted when a send-fax or receive-fax operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        control_id: Control ID of the fax operation.
        fax: Fax result data.
    """

    control_id: str = ""
    fax: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> FaxEvent:
        """Build a `FaxEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `FaxEvent` populated from the payload's `params`.
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
    """Event for `calling.call.tap`. Emitted when a tap operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        control_id: Control ID of the tap operation.
        state: Tap state.
        tap: Tap configuration details.
        device: The device receiving the tapped media.
    """

    control_id: str = ""
    state: str = ""
    tap: dict[str, Any] = field(default_factory=dict)
    device: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> TapEvent:
        """Build a `TapEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `TapEvent` populated from the payload's `params`.
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
    """Event for `calling.call.stream`. Emitted when a stream operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        control_id: Control ID of the stream operation.
        state: Stream state.
        url: The WebSocket URL the stream is connected to.
        name: The stream name.
    """

    control_id: str = ""
    state: str = ""
    url: str = ""
    name: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> StreamEvent:
        """Build a `StreamEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `StreamEvent` populated from the payload's `params`.
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
    """Event for `calling.call.send_digits`.

    Emitted when a send-digits operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        control_id: Control ID of the send-digits operation.
        state: Send-digits state.
    """

    control_id: str = ""
    state: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> SendDigitsEvent:
        """Build a `SendDigitsEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `SendDigitsEvent` populated from the payload's `params`.
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
    """Event for `calling.call.dial`.

    Emitted during an outbound dial. The client consumes it to match the dialed leg to
    its `dial()` call by tag.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        tag: Correlation tag for the dial operation.
        dial_state: Dial state.
        call: Call information for the dialed leg.
    """

    tag: str = ""
    dial_state: str = ""
    call: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> DialEvent:
        """Build a `DialEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `DialEvent` populated from the payload's `params`.
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
    """Event for `calling.call.refer`. Emitted when a SIP REFER operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        state: Refer state.
        sip_refer_to: The SIP URI the call was referred to.
        sip_refer_response_code: SIP response code from the REFER request.
        sip_notify_response_code: SIP response code from the NOTIFY message.
    """

    state: str = ""
    sip_refer_to: str = ""
    sip_refer_response_code: str = ""
    sip_notify_response_code: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ReferEvent:
        """Build a `ReferEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `ReferEvent` populated from the payload's `params`.
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
    """Event for `calling.call.denoise`. Emitted when noise reduction state changes.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        denoised: Whether noise reduction is active.
    """

    denoised: bool = False

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> DenoiseEvent:
        """Build a `DenoiseEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `DenoiseEvent` populated from the payload's `params`.
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
    """Event for `calling.call.pay`. Emitted when a pay operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        control_id: Control ID of the pay operation.
        state: Payment state.
    """

    control_id: str = ""
    state: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> PayEvent:
        """Build a `PayEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `PayEvent` populated from the payload's `params`.
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
    """Event for `calling.call.queue`. Emitted when queue state changes.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        control_id: Control ID of the queue operation.
        status: Queue status.
        queue_id: The queue identifier (the payload's `id` key).
        queue_name: The queue name (the payload's `name` key).
        position: Current position in the queue.
        size: Total number of calls in the queue.
    """

    control_id: str = ""
    status: str = ""
    queue_id: str = ""
    queue_name: str = ""
    position: int = 0
    size: int = 0

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> QueueEvent:
        """Build a `QueueEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `QueueEvent` populated from the payload's `params`.
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
    """Event for `calling.call.echo`. Emitted when an echo operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        state: Echo state.
    """

    state: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> EchoEvent:
        """Build a `EchoEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `EchoEvent` populated from the payload's `params`.
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
    """Event for `calling.call.transcribe`.

    Emitted when a transcribe operation changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        control_id: Control ID of the transcribe operation.
        state: Transcribe state.
        url: URL of the transcription.
        recording_id: Identifier of the associated recording.
        duration: Duration in seconds.
        size: Size in bytes.
    """

    control_id: str = ""
    state: str = ""
    url: str = ""
    recording_id: str = ""
    duration: float = 0.0
    size: int = 0

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> TranscribeEvent:
        """Build a `TranscribeEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `TranscribeEvent` populated from the payload's `params`.
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
    """Event for `calling.call.hold`. Emitted when hold state changes.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        state: Hold state.
    """

    state: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> HoldEvent:
        """Build a `HoldEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `HoldEvent` populated from the payload's `params`.
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
    """Event for `calling.conference`. Emitted when conference state changes.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        conference_id: The conference identifier.
        name: The conference name.
        status: Conference status.
    """

    conference_id: str = ""
    name: str = ""
    status: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ConferenceEvent:
        """Build a `ConferenceEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `ConferenceEvent` populated from the payload's `params`.
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
    """Event for `calling.error`. Emitted when a calling error occurs.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        code: Error code.
        message: Error message.
    """

    code: str = ""
    message: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> CallingErrorEvent:
        """Build a `CallingErrorEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `CallingErrorEvent` populated from the payload's `params`.
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
    """Event for `messaging.receive`.

    Inbound message notification. The client delivers it to the handler registered with
    `RelayClient.on_message`.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        message_id: Message identifier.
        context: The context the message was received on.
        direction: Message direction.
        from_number: Sender phone number.
        to_number: Destination phone number.
        body: Text body of the message.
        media: List of media URLs.
        segments: Number of message segments.
        message_state: Message state.
        tags: Tags attached to the message.
    """

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
        """Build a `MessageReceiveEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `MessageReceiveEvent` populated from the payload's `params`.
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
    """Event for `messaging.state`. Emitted when an outbound message changes state.

    Inherits `event_type`, `params`, `call_id` and `timestamp` from
    `RelayEvent`.

    Attributes:
        message_id: Message identifier.
        context: The message context.
        direction: Message direction.
        from_number: Sender phone number.
        to_number: Destination phone number.
        body: Text body of the message.
        media: List of media URLs.
        segments: Number of message segments.
        message_state: Message state.
        reason: Reason given for a failed or undelivered state.
        tags: Tags attached to the message.
    """

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
        """Build a `MessageStateEvent` from a raw event payload.

        Args:
            payload: Raw event dict with `event_type` and `params` keys.

        Returns:
            A `MessageStateEvent` populated from the payload's `params`.
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
    """Parse a raw signalwire.event params dict into a typed event object.

    Looks up `event_type` in `EVENT_CLASS_MAP` and falls back to `RelayEvent`
    for unrecognized types.

    Args:
        payload: Raw event dict with `event_type` and `params` keys.

    Returns:
        The typed `RelayEvent` subclass for the event type, or a plain
        `RelayEvent` if there is none.
    """
    event_type = payload.get("event_type", "")
    cls = EVENT_CLASS_MAP.get(event_type, RelayEvent)
    return cls.from_payload(payload)
