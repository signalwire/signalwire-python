# AUTO-GENERATED from porting-sdk/relay-protocol/*.{params,result}.json — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
# (one TypedDict per RELAY method's params / ack result, from the canonical RELAY
#  wire schemas)
"""Typed RELAY WebSocket protocol payloads, generated from the wire schemas.

One ``TypedDict`` per RELAY method's request params (``<Method>Params``) and
acknowledgement result (``<Method>Result``). Static-only: at runtime each is a plain
``dict``; the wire layer stays untyped and tolerant.
"""

from __future__ import annotations
from typing import Any, TypeAlias, TypedDict


class CallingAiHoldParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.ai_hold` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``async`` (``bool | None``)
    """

    # non-identifier field 'async': bool | None
    call_id: str
    node_id: str
    prompt: str
    swml: bool | None
    timeout: str


class CallingAiMessageParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.ai_message` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``async`` (``bool | None``)
    """

    # non-identifier field 'async': bool | None
    call_id: str
    global_data: Any
    message_text: str
    node_id: str
    reset: Any
    role: str
    swml: bool | None


class CallingAiUnholdParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.ai_unhold` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``async`` (``bool | None``)
    """

    # non-identifier field 'async': bool | None
    call_id: str
    node_id: str
    prompt: str
    swml: bool | None


class CallingAmazonBedrockParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.amazon_bedrock` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``async`` (``bool | None``)
    """

    SWAIG: Any
    # non-identifier field 'async': bool | None
    call_id: str
    global_data: Any
    node_id: str
    params: Any
    post_prompt: Any
    post_prompt_url: str
    prompt: Any
    swml: bool | None


class CallingAnswerParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.answer` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    max_duration: int | None
    node_id: str


class CallingBeginParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.begin` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    device: dict[str, Any]
    max_duration: int | None
    node_id: str
    region: str
    tag: str


class CallingBindDigitParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.bind_digit` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    bind_method: str
    call_id: str
    digits: str
    max_triggers: int | None
    node_id: str
    params: Any
    realm: str
    swml: bool | None


CallingCallParams: TypeAlias = "dict[str, Any]"


class CallingClearDigitBindingsParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.clear_digit_bindings` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str
    realm: str
    swml: bool | None


class CallingCollectParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.collect` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``continue`` (``bool | None``)
    """

    call_id: str
    # non-identifier field 'continue': bool | None
    continuous: bool | None
    control_id: str
    digits: dict[str, Any]
    initial_timeout: float | None
    node_id: str
    partial_results: bool | None
    send_start_of_input: bool | None
    speech: dict[str, Any]
    start_input_timers: bool | None


class CallingCollectStartInputTimersParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.collect.start_input_timers` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingCollectStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.collect.stop` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingConnectParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.connect` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    devices: list[list[dict[str, Any]]]
    max_duration: int | None
    max_price_per_minute: float | None
    node_id: str
    ringback: list[dict[str, Any]]
    tag: str


class CallingDenoiseParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.denoise` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str


class CallingDenoiseStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.denoise.stop` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str


class CallingDetectParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.detect` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    detect: dict[str, Any]
    node_id: str
    timeout: float | None


class CallingDetectStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.detect.stop` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingDialParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.dial` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    devices: list[list[dict[str, Any]]]
    max_price_per_minute: float | None
    node_id: str
    region: str
    tag: str


class CallingDisconnectParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.disconnect` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str


class CallingEchoParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.echo` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str
    status_url: str
    swml: bool | None
    timeout: float | None


class CallingEndParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.end` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str
    reason: str


class CallingJoinConferenceParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.join_conference` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    acl: str
    beep: str
    call_id: str
    coach: str
    end_on_exit: bool | None
    max_participants: int | None
    muted: bool | None
    name: str
    node_id: str
    record: str
    recording_status_callback: str
    recording_status_callback_event: str
    recording_status_callback_event_type: str
    recording_status_callback_method: str
    region: str
    start_on_enter: bool | None
    status_callback: str
    status_callback_event: str
    status_callback_event_type: str
    status_callback_method: str
    stream: Any
    swml: bool | None
    trim: str
    wait_url: str


class CallingJoinRoomParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.join_room` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    hagrid_json_api_url: str
    hagrid_node_id: str
    name: str
    node_id: str
    status_url: str
    swml: bool | None


class CallingLeaveConferenceParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.leave_conference` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``async`` (``bool | None``)
    """

    # non-identifier field 'async': bool | None
    call_id: str
    conference_id: str
    node_id: str


class CallingLeaveRoomParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.leave_room` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``async`` (``bool | None``)
    """

    # non-identifier field 'async': bool | None
    call_id: str
    node_id: str


class CallingLiveTranscribeParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.live_transcribe` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``async`` (``bool | None``)
    """

    action: Any
    # non-identifier field 'async': bool | None
    call_id: str
    node_id: str
    swml: bool | None


class CallingLiveTranslateParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.live_translate` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``async`` (``bool | None``)
    """

    action: Any
    # non-identifier field 'async': bool | None
    call_id: str
    node_id: str
    status_url: str
    swml: bool | None


class CallingPassParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.pass` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str


class CallingPayParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.pay` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    bank_account_type: Any
    call_id: str
    charge_amount: str
    control_id: str
    currency: str
    description: str
    input: Any
    language: str
    max_attempts: str
    min_postal_code_length: str
    node_id: str
    parameters: list[dict[str, Any]]
    payment_connector_url: str
    payment_method: Any
    postal_code: str
    prompts: list[dict[str, Any]]
    security_code: str
    status_url: str
    timeout: str
    token_type: Any
    valid_card_types: str
    voice: str


class CallingPayStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.pay.stop` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingPlayParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    play: list[dict[str, Any]]
    volume: float | None


class CallingPlayPauseParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.pause` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingPlayResumeParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.resume` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingPlayStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.stop` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingPlayVolumeParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.volume` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    volume: float


class CallingPlayAndCollectParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    collect: dict[str, Any]
    control_id: str
    node_id: str
    play: list[dict[str, Any]]
    volume: float | None


class CallingPlayAndCollectStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect.stop` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingPlayAndCollectVolumeParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect.volume` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    volume: float


class CallingQueueEnterParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.queue.enter` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    queue_name: str
    status_url: str
    wait_url: str


class CallingQueueLeaveParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.queue.leave` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    queue_id: str
    queue_name: str
    status_url: str


class CallingReceiveParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    context: str
    contexts: list[str]


class CallingReceiveFaxParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive_fax` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingReceiveFaxStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive_fax.stop` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingRecordParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    record: dict[str, Any]


class CallingRecordPauseParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.pause` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    behavior: str
    call_id: str
    control_id: str
    node_id: str


class CallingRecordResumeParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.resume` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingRecordStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.stop` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingReferParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.refer` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    device: dict[str, Any]
    node_id: str


class CallingSendDigitsParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_digits` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    digits: str
    node_id: str


class CallingSendFaxParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_fax` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    document: str
    header_info: str
    identity: str
    node_id: str


class CallingSendFaxStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_fax.stop` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingStreamParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.stream` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``async`` (``bool | None``)
    """

    # non-identifier field 'async': bool | None
    authorization_bearer_token: str
    call_id: str
    codec: str
    control_id: str
    custom_parameters: Any
    name: str
    node_id: str
    status_url: str
    status_url_method: str
    swml: bool | None
    track: str
    url: str


class CallingStreamStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.stream.stop` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``async`` (``bool | None``)
    """

    # non-identifier field 'async': bool | None
    call_id: str
    control_id: str
    node_id: str
    swml: bool | None


class CallingTapParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.tap` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    device: dict[str, Any]
    node_id: str
    tap: dict[str, Any]


class CallingTapStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.tap.stop` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingTransferParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.transfer` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    dest: str
    node_id: str


class CallingUserEventParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.user_event` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``async`` (``bool | None``)
    """

    # non-identifier field 'async': bool | None
    call_id: str
    event: Any
    node_id: str
    swml: bool | None


class MessagingSendParams(TypedDict, total=False):
    """Permissive schema for the messaging.send RPC params.

    The server forwards the params as-is to the messaging gateway, so the schema is
    derived from the Python relay client (``signalwire/relay/client.py:send_message``).
    At least one of `body` or `media` is required.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    body: str
    context: str
    from_number: str
    media: list[str]
    region: str
    tags: list[str]
    to_number: str


class SignalwireConnectParams(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.connect` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    agent: str
    authentication: dict[str, Any]
    host: str
    identity: str
    params: dict[str, Any]
    protocols: list[dict[str, Any]]
    version: dict[str, Any]


class SignalwireDisconnectParams(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.disconnect` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    restart: bool


class SignalwireExecuteParams(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.execute` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    attempted: list[str]
    method: str
    params: Any
    protocol: str
    requester_identity: str
    requester_nodeid: str
    responder_identity: str
    responder_nodeid: str


class SignalwirePingParams(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.ping` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    payload: str
    timestamp: float | None


class SignalwireReauthenticateParams(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.reauthenticate` (params).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    authentication: dict[str, Any]
    dpop_token: str


class CallingAiHoldResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.ai_hold` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingAiMessageResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.ai_message` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingAiUnholdResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.ai_unhold` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingAmazonBedrockResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.amazon_bedrock` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingAnswerResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.answer` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str


class CallingBeginResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.begin` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str
    message_data: Any
    node_id: str


class CallingBindDigitResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.bind_digit` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


CallingCallResult: TypeAlias = "dict[str, Any]"


class CallingClearDigitBindingsResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.clear_digit_bindings` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingCollectResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.collect` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingCollectStartInputTimersResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.collect.start_input_timers` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingCollectStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.collect.stop` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingConnectResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.connect` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str
    message_data: Any


class CallingDenoiseResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.denoise` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingDenoiseStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.denoise.stop` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingDetectResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.detect` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingDetectStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.detect.stop` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingDialResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.dial` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str
    message_data: Any


class CallingDisconnectResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.disconnect` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str


class CallingEchoResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.echo` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingEndResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.end` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str


class CallingJoinConferenceResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.join_conference` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    conference_id: str
    data: Any
    message: str


class CallingJoinRoomResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.join_room` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingLeaveConferenceResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.leave_conference` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingLeaveRoomResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.leave_room` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingLiveTranscribeResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.live_transcribe` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingLiveTranslateResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.live_translate` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingPassResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.pass` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingPayResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.pay` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPayStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.pay.stop` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayPauseResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.pause` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayResumeResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.resume` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.stop` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayVolumeResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.volume` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayAndCollectResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayAndCollectStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect.stop` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayAndCollectVolumeResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect.volume` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingQueueEnterResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.queue.enter` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingQueueLeaveResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.queue.leave` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingReceiveResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    message: str


class CallingReceiveFaxResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive_fax` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingReceiveFaxStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive_fax.stop` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingRecordPauseResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.pause` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingRecordResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str
    url: str


class CallingRecordResumeResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.resume` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingRecordStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.stop` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingReferResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.refer` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str


class CallingSendDigitsResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_digits` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingSendFaxResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_fax` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingSendFaxStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_fax.stop` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingStreamResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.stream` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingStreamStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.stream.stop` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingTapResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.tap` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str
    source_device: dict[str, Any]


class CallingTapStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.tap.stop` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingTransferResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.transfer` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingUserEventResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.user_event` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class MessagingSendResult(TypedDict, total=False):
    """Permissive schema for the messaging.send RPC response.

    The message_id from the response is used to route subsequent messaging.state events.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    message: str
    message_id: str


class SignalwireConnectResult(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.connect` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    accesses: list[dict[str, Any]]
    authorization: dict[str, Any]
    authorizations: list[dict[str, Any]]
    host: str
    ice_servers: list[Any]
    identity: str
    master_nodeid: str
    nodeid: str
    protocol: str
    protocols: list[dict[str, Any]]
    protocols_uncertified: list[str]
    result: Any
    session_restored: bool
    sessionid: str
    subscriptions: list[dict[str, Any]]


SignalwireDisconnectResult: TypeAlias = "dict[str, Any]"


class SignalwireExecuteResult(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.execute` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    requester_nodeid: str
    responder_nodeid: str
    result: Any


class SignalwirePingResult(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.ping` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    payload: str
    timestamp: float | None


class SignalwireReauthenticateResult(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.reauthenticate` (result).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    authentication: str
    authorization: dict[str, Any]
    ice_servers: list[Any]
    result: Any
