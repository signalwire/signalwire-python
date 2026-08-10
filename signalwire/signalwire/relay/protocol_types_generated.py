# AUTO-GENERATED from porting-sdk/relay-protocol/*.{params,result}.json — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per RELAY method's params (<Method>Params) and ack result
# (<Method>Result), from the canonical switchblade wire schemas. STATIC-ONLY:
# at runtime each is a plain dict; the wire layer stays untyped and tolerant.
from __future__ import annotations
from typing import Any, TypeAlias, TypedDict


class CallingAiHoldParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.ai_hold` (params). Extracted from switchblade `PublicCallAiHoldParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    # non-identifier field 'async': bool | None
    call_id: str
    node_id: str
    prompt: str
    swml: bool | None
    timeout: str


class CallingAiMessageParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.ai_message` (params). Extracted from switchblade `PublicCallAiMessageParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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
    """Wire schema for the JSON payload of `calling.ai_unhold` (params). Extracted from switchblade `PublicCallAiUnholdParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    # non-identifier field 'async': bool | None
    call_id: str
    node_id: str
    prompt: str
    swml: bool | None


class CallingAmazonBedrockParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.amazon_bedrock` (params). Extracted from switchblade `PublicCallAmazonBedrockParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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
    """Wire schema for the JSON payload of `calling.answer` (params). Extracted from switchblade `PublicCallAnswerParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    max_duration: int | None
    node_id: str


class CallingBeginParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.begin` (params). Extracted from switchblade `PublicCallBeginParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    device: dict[str, Any]
    max_duration: int | None
    node_id: str
    region: str
    tag: str


class CallingBindDigitParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.bind_digit` (params). Extracted from switchblade `PublicCallBindDigitParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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
    """Wire schema for the JSON payload of `calling.clear_digit_bindings` (params). Extracted from switchblade `PublicCallClearDigitBindingsParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str
    realm: str
    swml: bool | None


class CallingCollectParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.collect` (params). Extracted from switchblade `PublicCallCollectParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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
    """Wire schema for the JSON payload of `calling.collect.start_input_timers` (params). Extracted from switchblade `PublicCallCollectStartInputTimersParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingCollectStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.collect.stop` (params). Extracted from switchblade `PublicCallCollectStopParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingConnectParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.connect` (params). Extracted from switchblade `PublicCallConnectParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    devices: list[list[dict[str, Any]]]
    max_duration: int | None
    max_price_per_minute: float | None
    node_id: str
    ringback: list[dict[str, Any]]
    tag: str


class CallingDenoiseParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.denoise` (params). Extracted from switchblade `PublicCallDenoiseParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str


class CallingDenoiseStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.denoise.stop` (params). Extracted from switchblade `PublicCallDenoiseStopParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str


class CallingDetectParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.detect` (params). Extracted from switchblade `PublicCallDetectParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    detect: dict[str, Any]
    node_id: str
    timeout: float | None


class CallingDetectStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.detect.stop` (params). Extracted from switchblade `PublicCallDetectStopParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingDialParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.dial` (params). Extracted from switchblade `PublicCallDialParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    devices: list[list[dict[str, Any]]]
    max_price_per_minute: float | None
    node_id: str
    region: str
    tag: str


class CallingDisconnectParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.disconnect` (params). Extracted from switchblade `PublicCallDisconnectParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str


class CallingEchoParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.echo` (params). Extracted from switchblade `PublicCallEchoParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str
    status_url: str
    swml: bool | None
    timeout: float | None


class CallingEndParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.end` (params). Extracted from switchblade `PublicCallEndParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str
    reason: str


class CallingJoinConferenceParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.join_conference` (params). Extracted from switchblade `PublicCallJoinConferenceParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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
    """Wire schema for the JSON payload of `calling.join_room` (params). Extracted from switchblade `PublicCallJoinRoomParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    hagrid_json_api_url: str
    hagrid_node_id: str
    name: str
    node_id: str
    status_url: str
    swml: bool | None


class CallingLeaveConferenceParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.leave_conference` (params). Extracted from switchblade `PublicCallLeaveConferenceParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    # non-identifier field 'async': bool | None
    call_id: str
    conference_id: str
    node_id: str


class CallingLeaveRoomParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.leave_room` (params). Extracted from switchblade `PublicCallLeaveRoomParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    # non-identifier field 'async': bool | None
    call_id: str
    node_id: str


class CallingLiveTranscribeParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.live_transcribe` (params). Extracted from switchblade `PublicCallLiveTranscribeParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    action: Any
    # non-identifier field 'async': bool | None
    call_id: str
    node_id: str
    swml: bool | None


class CallingLiveTranslateParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.live_translate` (params). Extracted from switchblade `PublicCallLiveTranslateParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    action: Any
    # non-identifier field 'async': bool | None
    call_id: str
    node_id: str
    status_url: str
    swml: bool | None


class CallingPassParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.pass` (params). Extracted from switchblade `PublicCallPassParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str


class CallingPayParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.pay` (params). Extracted from switchblade `PublicCallPayParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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
    """Wire schema for the JSON payload of `calling.pay.stop` (params). Extracted from switchblade `PublicCallPayStopParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingPlayParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play` (params). Extracted from switchblade `PublicCallPlayParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    play: list[dict[str, Any]]
    volume: float | None


class CallingPlayPauseParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.pause` (params). Extracted from switchblade `PublicCallPlayPauseParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingPlayResumeParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.resume` (params). Extracted from switchblade `PublicCallPlayResumeParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingPlayStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.stop` (params). Extracted from switchblade `PublicCallPlayStopParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingPlayVolumeParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.volume` (params). Extracted from switchblade `PublicCallPlayVolumeParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    volume: float


class CallingPlayAndCollectParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect` (params). Extracted from switchblade `PublicCallPlayAndCollectParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    collect: dict[str, Any]
    control_id: str
    node_id: str
    play: list[dict[str, Any]]
    volume: float | None


class CallingPlayAndCollectStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect.stop` (params). Extracted from switchblade `PublicCallPlayAndCollectStopParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingPlayAndCollectVolumeParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect.volume` (params). Extracted from switchblade `PublicCallPlayAndCollectVolumeParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    volume: float


class CallingQueueEnterParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.queue.enter` (params). Extracted from switchblade `PublicCallQueueEnterParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    queue_name: str
    status_url: str
    wait_url: str


class CallingQueueLeaveParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.queue.leave` (params). Extracted from switchblade `PublicCallQueueLeaveParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    queue_id: str
    queue_name: str
    status_url: str


class CallingReceiveParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive` (params). Extracted from switchblade `PublicCallReceiveParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    context: str
    contexts: list[str]


class CallingReceiveFaxParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive_fax` (params). Extracted from switchblade `PublicCallReceiveFaxParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingReceiveFaxStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive_fax.stop` (params). Extracted from switchblade `PublicCallReceiveFaxStopParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingRecordParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record` (params). Extracted from switchblade `PublicCallRecordParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str
    record: dict[str, Any]


class CallingRecordPauseParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.pause` (params). Extracted from switchblade `PublicCallRecordPauseParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    behavior: str
    call_id: str
    control_id: str
    node_id: str


class CallingRecordResumeParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.resume` (params). Extracted from switchblade `PublicCallRecordResumeParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingRecordStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.stop` (params). Extracted from switchblade `PublicCallRecordStopParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingReferParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.refer` (params). Extracted from switchblade `PublicCallReferParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    device: dict[str, Any]
    node_id: str


class CallingSendDigitsParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_digits` (params). Extracted from switchblade `PublicCallSendDigitsParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    digits: str
    node_id: str


class CallingSendFaxParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_fax` (params). Extracted from switchblade `PublicCallSendFaxParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    document: str
    header_info: str
    identity: str
    node_id: str


class CallingSendFaxStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_fax.stop` (params). Extracted from switchblade `PublicCallSendFaxStopParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingStreamParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.stream` (params). Extracted from switchblade `PublicCallStreamParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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
    """Wire schema for the JSON payload of `calling.stream.stop` (params). Extracted from switchblade `PublicCallStreamStopParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    # non-identifier field 'async': bool | None
    call_id: str
    control_id: str
    node_id: str
    swml: bool | None


class CallingTapParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.tap` (params). Extracted from switchblade `PublicCallTapParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    device: dict[str, Any]
    node_id: str
    tap: dict[str, Any]


class CallingTapStopParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.tap.stop` (params). Extracted from switchblade `PublicCallTapStopParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    control_id: str
    node_id: str


class CallingTransferParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.transfer` (params). Extracted from switchblade `PublicCallTransferParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    dest: str
    node_id: str


class CallingUserEventParams(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.user_event` (params). Extracted from switchblade `PublicCallUserEventParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    # non-identifier field 'async': bool | None
    call_id: str
    event: Any
    node_id: str
    swml: bool | None


class MessagingSendParams(TypedDict, total=False):
    """Permissive schema for the messaging.send RPC params. Switchblade forwards the JObject as-is to the messaging gateway, so the schema is derived from the Python relay client (``signalwire/relay/client.py:send_message``). At least one of `body` or `media` is required.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    body: str
    context: str
    from_number: str
    media: list[str]
    region: str
    tags: list[str]
    to_number: str


class SignalwireConnectParams(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.connect` (params). Extracted from switchblade `Messages/ConnectParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    agent: str
    authentication: dict[str, Any]
    host: str
    identity: str
    params: dict[str, Any]
    protocols: list[dict[str, Any]]
    version: dict[str, Any]


class SignalwireDisconnectParams(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.disconnect` (params). Extracted from switchblade `Messages/DisconnectParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    restart: bool


class SignalwireExecuteParams(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.execute` (params). Extracted from switchblade `Messages/ExecuteParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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
    """Wire schema for the Blade envelope `signalwire.ping` (params). Extracted from switchblade `Messages/PingParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    payload: str
    timestamp: float | None


class SignalwireReauthenticateParams(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.reauthenticate` (params). Extracted from switchblade `Messages/ReauthenticateParams.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    authentication: dict[str, Any]
    dpop_token: str


class CallingAiHoldResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.ai_hold` (result). Extracted from switchblade `PublicCallAiHoldResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingAiMessageResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.ai_message` (result). Extracted from switchblade `PublicCallAiMessageResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingAiUnholdResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.ai_unhold` (result). Extracted from switchblade `PublicCallAiUnholdResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingAmazonBedrockResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.amazon_bedrock` (result). Extracted from switchblade `PublicCallAmazonBedrockResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingAnswerResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.answer` (result). Extracted from switchblade `PublicCallAnswerResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str


class CallingBeginResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.begin` (result). Extracted from switchblade `PublicCallBeginResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str
    message_data: Any
    node_id: str


class CallingBindDigitResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.bind_digit` (result). Extracted from switchblade `PublicCallBindDigitResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


CallingCallResult: TypeAlias = "dict[str, Any]"


class CallingClearDigitBindingsResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.clear_digit_bindings` (result). Extracted from switchblade `PublicCallClearDigitBindingsResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingCollectResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.collect` (result). Extracted from switchblade `PublicCallCollectResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingCollectStartInputTimersResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.collect.start_input_timers` (result). Extracted from switchblade `PublicCallCollectStartInputTimersResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingCollectStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.collect.stop` (result). Extracted from switchblade `PublicCallCollectStopResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingConnectResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.connect` (result). Extracted from switchblade `PublicCallConnectResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str
    message_data: Any


class CallingDenoiseResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.denoise` (result). Extracted from switchblade `PublicCallDenoiseResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingDenoiseStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.denoise.stop` (result). Extracted from switchblade `PublicCallDenoiseStopResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingDetectResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.detect` (result). Extracted from switchblade `PublicCallDetectResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingDetectStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.detect.stop` (result). Extracted from switchblade `PublicCallDetectStopResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingDialResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.dial` (result). Extracted from switchblade `PublicCallDialResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str
    message_data: Any


class CallingDisconnectResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.disconnect` (result). Extracted from switchblade `PublicCallDisconnectResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str


class CallingEchoResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.echo` (result). Extracted from switchblade `PublicCallEchoResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingEndResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.end` (result). Extracted from switchblade `PublicCallEndResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str


class CallingJoinConferenceResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.join_conference` (result). Extracted from switchblade `PublicCallJoinConferenceResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    conference_id: str
    data: Any
    message: str


class CallingJoinRoomResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.join_room` (result). Extracted from switchblade `PublicCallJoinRoomResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingLeaveConferenceResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.leave_conference` (result). Extracted from switchblade `PublicCallLeaveConferenceResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingLeaveRoomResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.leave_room` (result). Extracted from switchblade `PublicCallLeaveRoomResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingLiveTranscribeResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.live_transcribe` (result). Extracted from switchblade `PublicCallLiveTranscribeResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingLiveTranslateResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.live_translate` (result). Extracted from switchblade `PublicCallLiveTranslateResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingPassResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.pass` (result). Extracted from switchblade `PublicCallPassResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingPayResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.pay` (result). Extracted from switchblade `PublicCallPayResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPayStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.pay.stop` (result). Extracted from switchblade `PublicCallPayStopResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayPauseResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.pause` (result). Extracted from switchblade `PublicCallPlayPauseResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play` (result). Extracted from switchblade `PublicCallPlayResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayResumeResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.resume` (result). Extracted from switchblade `PublicCallPlayResumeResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.stop` (result). Extracted from switchblade `PublicCallPlayStopResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayVolumeResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play.volume` (result). Extracted from switchblade `PublicCallPlayVolumeResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayAndCollectResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect` (result). Extracted from switchblade `PublicCallPlayAndCollectResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayAndCollectStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect.stop` (result). Extracted from switchblade `PublicCallPlayAndCollectStopResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingPlayAndCollectVolumeResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.play_and_collect.volume` (result). Extracted from switchblade `PublicCallPlayAndCollectVolumeResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingQueueEnterResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.queue.enter` (result). Extracted from switchblade `PublicCallQueueEnterResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingQueueLeaveResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.queue.leave` (result). Extracted from switchblade `PublicCallQueueLeaveResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingReceiveResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive` (result). Extracted from switchblade `PublicCallReceiveResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    message: str


class CallingReceiveFaxResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive_fax` (result). Extracted from switchblade `PublicCallReceiveFaxResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingReceiveFaxStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.receive_fax.stop` (result). Extracted from switchblade `PublicCallReceiveFaxStopResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingRecordPauseResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.pause` (result). Extracted from switchblade `PublicCallRecordPauseResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingRecordResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record` (result). Extracted from switchblade `PublicCallRecordResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str
    url: str


class CallingRecordResumeResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.resume` (result). Extracted from switchblade `PublicCallRecordResumeResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingRecordStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.record.stop` (result). Extracted from switchblade `PublicCallRecordStopResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingReferResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.refer` (result). Extracted from switchblade `PublicCallReferResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    data: Any
    message: str


class CallingSendDigitsResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_digits` (result). Extracted from switchblade `PublicCallSendDigitsResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingSendFaxResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_fax` (result). Extracted from switchblade `PublicCallSendFaxResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingSendFaxStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.send_fax.stop` (result). Extracted from switchblade `PublicCallSendFaxStopResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingStreamResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.stream` (result). Extracted from switchblade `PublicCallStreamResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingStreamStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.stream.stop` (result). Extracted from switchblade `PublicCallStreamStopResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingTapResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.tap` (result). Extracted from switchblade `PublicCallTapResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str
    source_device: dict[str, Any]


class CallingTapStopResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.tap.stop` (result). Extracted from switchblade `PublicCallTapStopResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    control_id: str
    data: Any
    message: str


class CallingTransferResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.transfer` (result). Extracted from switchblade `PublicCallTransferResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class CallingUserEventResult(TypedDict, total=False):
    """Wire schema for the JSON payload of `calling.user_event` (result). Extracted from switchblade `PublicCallUserEventResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    code: str
    data: Any
    message: str


class MessagingSendResult(TypedDict, total=False):
    """Permissive schema for the messaging.send RPC response. The message_id from the response is used to route subsequent messaging.state events.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    message: str
    message_id: str


class SignalwireConnectResult(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.connect` (result). Extracted from switchblade `Messages/ConnectResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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
    """Wire schema for the Blade envelope `signalwire.execute` (result). Extracted from switchblade `Messages/ExecuteResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    requester_nodeid: str
    responder_nodeid: str
    result: Any


class SignalwirePingResult(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.ping` (result). Extracted from switchblade `Messages/PingResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    payload: str
    timestamp: float | None


class SignalwireReauthenticateResult(TypedDict, total=False):
    """Wire schema for the Blade envelope `signalwire.reauthenticate` (result). Extracted from switchblade `Messages/ReauthenticateResult.cs`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    authentication: str
    authorization: dict[str, Any]
    ice_servers: list[Any]
    result: Any
