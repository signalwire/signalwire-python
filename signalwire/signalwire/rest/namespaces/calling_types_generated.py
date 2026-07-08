# AUTO-GENERATED from porting-sdk/rest-apis/calling/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


class AI(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai: AIObject


class AIObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    global_data: dict[str, Any]
    hints: list[str | Hint]
    languages: list[Languages]
    params: AIParams
    post_prompt: AIPostPrompt
    post_prompt_url: str
    pronounce: list[Pronounce]
    prompt: AIPrompt
    SWAIG: SWAIG


class AIParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    acknowledge_interruptions: bool | SWMLVar
    ai_model: Literal["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano"] | str
    ai_name: str
    ai_volume: int | SWMLVar
    app_name: str
    asr_smart_format: bool | SWMLVar
    attention_timeout: AttentionTimeout | Literal[0] | SWMLVar
    attention_timeout_prompt: str
    asr_diarize: bool | SWMLVar
    asr_speaker_affinity: bool | SWMLVar
    background_file: str
    background_file_loops: int | None | SWMLVar
    background_file_volume: int | SWMLVar
    enable_barge: str | bool | SWMLVar
    enable_inner_dialog: bool | SWMLVar
    enable_pause: bool | SWMLVar
    enable_turn_detection: bool | SWMLVar
    barge_match_string: str
    barge_min_words: int | SWMLVar
    barge_functions: bool | SWMLVar
    conscience: str
    convo: list[ConversationMessage]
    conversation_id: str
    conversation_sliding_window: int | SWMLVar
    debug_webhook_level: int | SWMLVar
    debug_webhook_url: str
    debug: bool | int | SWMLVar
    direction: Direction | SWMLVar
    digit_terminators: str
    digit_timeout: int | SWMLVar
    end_of_speech_timeout: int | SWMLVar
    enable_thinking: bool | SWMLVar
    enable_vision: bool | SWMLVar
    energy_level: float | SWMLVar
    first_word_timeout: int | SWMLVar
    function_wait_for_talking: bool | SWMLVar
    functions_on_no_response: bool | SWMLVar
    hard_stop_prompt: str
    hard_stop_time: str | SWMLVar
    hold_music: str
    hold_on_process: bool | SWMLVar
    inactivity_timeout: int | SWMLVar
    inner_dialog_model: Literal["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano"] | str
    inner_dialog_prompt: str
    inner_dialog_synced: bool | SWMLVar
    initial_sleep_ms: int | SWMLVar
    input_poll_freq: int | SWMLVar
    interrupt_on_noise: bool | SWMLVar
    interrupt_prompt: str
    # deprecated: languages_enabled
    languages_enabled: bool | SWMLVar
    local_tz: str
    llm_diarize_aware: bool | SWMLVar
    max_emotion: int | SWMLVar
    max_response_tokens: int | SWMLVar
    openai_asr_engine: str
    outbound_attention_timeout: int | SWMLVar
    persist_global_data: bool | SWMLVar
    pom_format: Literal["markdown", "xml"]
    save_conversation: bool | SWMLVar
    speech_event_timeout: int | SWMLVar
    speech_gen_quick_stops: int | SWMLVar
    speech_timeout: int | SWMLVar
    speak_when_spoken_to: bool | SWMLVar
    start_paused: bool | SWMLVar
    static_greeting: str
    static_greeting_no_barge: bool | SWMLVar
    summary_mode: Literal["string", "original"] | SWMLVar
    swaig_allow_settings: bool | SWMLVar
    swaig_allow_swml: bool | SWMLVar
    swaig_post_conversation: bool | SWMLVar
    swaig_set_global_data: bool | SWMLVar
    swaig_post_swml_vars: bool | list[str] | SWMLVar
    thinking_model: Literal["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano"] | str
    transparent_barge: bool | SWMLVar
    transparent_barge_max_time: int | SWMLVar
    transfer_summary: bool | SWMLVar
    turn_detection_timeout: int | SWMLVar
    tts_number_format: Literal["international", "national"]
    video_listening_file: str
    video_idle_file: str
    video_talking_file: str
    vision_model: Literal["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano"] | str
    vad_config: str
    wait_for_user: bool | SWMLVar
    wake_prefix: str
    eleven_labs_stability: float | SWMLVar
    eleven_labs_similarity: float | SWMLVar


AIPostPrompt: TypeAlias = "AIPostPromptText | AIPostPromptPom"


class AIPostPromptPom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    pom: list[POM]


class AIPostPromptText(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    text: str


AIPrompt: TypeAlias = "AIPromptText | AIPromptPom"


class AIPromptPom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    pom: list[POM]
    contexts: Contexts


class AIPromptText(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    text: str
    contexts: Contexts


Action: TypeAlias = "SWMLAction | ChangeContextAction | ChangeStepAction | ContextSwitchAction | HangupAction | HoldAction | PlaybackBGAction | SayAction | SetGlobalDataAction | SetMetaDataAction | StopAction | StopPlaybackBGAction | ToggleFunctionsAction | UnsetGlobalDataAction | UnsetMetaDataAction | UserInputAction"


class AllOfProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    allOf: list[SchemaType]


class AmazonBedrock(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    amazon_bedrock: AmazonBedrockObject


class AmazonBedrockObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    global_data: dict[str, Any]
    params: BedrockParams
    post_prompt: BedrockPostPrompt
    post_prompt_url: str
    prompt: BedrockPrompt
    SWAIG: BedrockSWAIG


class Answer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    answer: dict[str, Any]


class AnyOfProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    anyOf: list[SchemaType]


class ArrayProperty(TypedDict, total=False):
    """Base interface for all property types

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["array"]
    default: list[Any]
    items: SchemaType


AttentionTimeout: TypeAlias = "int"


class BedrockParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    attention_timeout: AttentionTimeout | Literal[0] | SWMLVar
    hard_stop_time: str | SWMLVar
    inactivity_timeout: int | SWMLVar
    video_listening_file: str
    video_idle_file: str
    video_talking_file: str
    hard_stop_prompt: str


BedrockPostPrompt: TypeAlias = "dict[str, Any]"

BedrockPrompt: TypeAlias = "dict[str, Any]"


class BedrockSWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    functions: list[BedrockSWAIGFunction]
    defaults: SWAIGDefaults
    native_functions: list[SWAIGNativeFunction]
    includes: list[SWAIGIncludes]


BedrockSWAIGFunction: TypeAlias = "dict[str, Any]"


class BooleanProperty(TypedDict, total=False):
    """Base interface for all property types

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["boolean"]
    default: bool | SWMLVar


class CallAIMessageRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.ai_message"]
    params: dict[str, Any]


class CallAIMessageResetParams(TypedDict, total=False):
    """Parameters for resetting the AI conversation state.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    full_reset: bool
    user_prompt: str
    system_prompt: str


class CallCreate422Error(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class CallCreateParamsSWML(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'from': str
    to: str
    caller_id: str
    fallback_url: str
    status_url: str
    status_events: list[
        Literal["answered", "queued", "initiated", "ringing", "ending", "ended"]
    ]
    url_method: str
    codecs: list[str] | str
    swml: SWMLObject


class CallCreateParamsURL(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'from': str
    to: str
    caller_id: str
    fallback_url: str
    status_url: str
    status_events: list[
        Literal["answered", "queued", "initiated", "ringing", "ending", "ended"]
    ]
    url_method: str
    url: str


class CallCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    command: Literal["dial"]
    params: CallCreateParamsURL | CallCreateParamsSWML


CallDirection: TypeAlias = "Literal['inbound', 'outbound', 'outbound-api']"


class CallHangupRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.end"]
    params: dict[str, Any]


class CallHoldRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.ai_hold"]
    params: dict[str, Any]


class CallLeg(TypedDict, total=False):
    """A Call leg (PSTN, SIP, or WebRTC).

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    # non-identifier field 'from': str
    to: str
    direction: CallDirection
    source: Literal["realtime_api"]
    url: str | None
    charge: float
    created_at: str
    charge_details: list[ChargeDetails]
    status: CallResponseStatus | None
    duration: int | None
    duration_ms: int | None
    billing_ms: int | None
    type: (
        Literal["relay_pstn_call"]
        | Literal["relay_sip_call"]
        | Literal["relay_webrtc_call"]
    )
    parent_id: uuid | None


class CallLiveTranscribeRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.live_transcribe"]
    params: dict[str, Any]


class CallLiveTranslateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.live_translate"]
    params: dict[str, Any]


CallRequest: TypeAlias = "CallCreateRequest | CallUpdateCurrentCallRequest | CallHangupRequest | CallHoldRequest | CallUnholdRequest | CallAIMessageRequest | CallLiveTranscribeRequest | CallLiveTranslateRequest | CallTransferRequest | CallUserEventRequest | CallDisconnectRequest | CallPlayRequest | CallPlayPauseRequest | CallPlayResumeRequest | CallPlayStopRequest | CallPlayVolumeRequest | CallRecordRequest | CallRecordPauseRequest | CallRecordResumeRequest | CallRecordStopRequest | CallCollectRequest | CallCollectStopRequest | CallCollectStartInputTimersRequest | CallDetectRequest | CallDetectStopRequest | CallTapRequest | CallTapStopRequest | CallStreamRequest | CallStreamStopRequest | CallDenoiseRequest | CallDenoiseStopRequest | CallTranscribeRequest | CallTranscribeStopRequest | CallAIStopRequest | CallSendFaxStopRequest | CallReceiveFaxStopRequest | CallReferRequest"


class CallDisconnectRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.disconnect"]
    params: dict[str, Any]


class CallPlayRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.play"]
    params: dict[str, Any]


class CallPlayPauseRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.play.pause"]
    params: dict[str, Any]


class CallPlayResumeRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.play.resume"]
    params: dict[str, Any]


class CallPlayStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.play.stop"]
    params: dict[str, Any]


class CallPlayVolumeRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.play.volume"]
    params: dict[str, Any]


class CallRecordRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.record"]
    params: dict[str, Any]


class CallRecordPauseRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.record.pause"]
    params: dict[str, Any]


class CallRecordResumeRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.record.resume"]
    params: dict[str, Any]


class CallRecordStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.record.stop"]
    params: dict[str, Any]


class CallCollectRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.collect"]
    params: dict[str, Any]


class CallCollectStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.collect.stop"]
    params: dict[str, Any]


class CallCollectStartInputTimersRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.collect.start_input_timers"]
    params: dict[str, Any]


class CallDetectRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.detect"]
    params: dict[str, Any]


class CallDetectStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.detect.stop"]
    params: dict[str, Any]


class CallTapRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.tap"]
    params: dict[str, Any]


class CallTapStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.tap.stop"]
    params: dict[str, Any]


class CallStreamRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.stream"]
    params: dict[str, Any]


class CallStreamStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.stream.stop"]
    params: dict[str, Any]


class CallDenoiseRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.denoise"]
    params: dict[str, Any]


class CallDenoiseStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.denoise.stop"]
    params: dict[str, Any]


class CallTranscribeRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.transcribe"]
    params: dict[str, Any]


class CallTranscribeStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.transcribe.stop"]
    params: dict[str, Any]


class CallAIStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.ai.stop"]
    params: dict[str, Any]


class CallSendFaxStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.send_fax.stop"]
    params: dict[str, Any]


class CallReceiveFaxStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.receive_fax.stop"]
    params: dict[str, Any]


class CallReferRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.refer"]
    params: dict[str, Any]


CallResponse: TypeAlias = "CallLeg | FabricDeviceLeg"

CallResponseStatus: TypeAlias = "Literal['queued', 'initiated', 'created', 'ringing', 'answered', 'ending', 'ended', 'failed', 'canceled', 'completed']"

CallStatus: TypeAlias = "Literal['created', 'ringing', 'answered', 'ended']"


class CallTransferRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.transfer"]
    params: dict[str, Any]


class CallUnholdRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.ai_unhold"]
    params: dict[str, Any]


class CallUpdateCurrentCallRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    command: Literal["update"]
    params: CallUpdateParamsURL | CallUpdateParamsSWML


class CallUpdateParamsSWML(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    fallback_url: str
    status: Literal["canceled", "completed"]
    status_url: str
    swml: SWMLObject


class CallUpdateParamsURL(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    fallback_url: str
    status: Literal["canceled", "completed"]
    status_url: str
    url: str


class CallUserEventRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.user_event"]
    params: dict[str, Any]


class ChangeContextAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    change_context: str


class ChangeStepAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    change_step: str


class ChargeDetails(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    charge: float


class Cond(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    cond: list[CondParams]


class CondElse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'else': list[SWMLMethod]


CondParams: TypeAlias = "CondReg | CondElse"


class CondReg(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    when: str
    then: list[SWMLMethod]
    # non-identifier field 'else': list[SWMLMethod]


class Connect(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    connect: (
        ConnectDeviceSingle
        | ConnectDeviceSerial
        | ConnectDeviceParallel
        | ConnectDeviceSerialParallel
    )


class ConnectDeviceParallel(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'from': str
    headers: list[ConnectHeaders]
    codecs: str
    webrtc_media: bool | SWMLVar
    session_timeout: int | SWMLVar
    ringback: list[str]
    result: ConnectSwitch | list[CondParams]
    timeout: int | SWMLVar
    max_duration: int | SWMLVar
    answer_on_bridge: bool | SWMLVar
    confirm: str | list[ValidConfirmMethods]
    confirm_timeout: int | SWMLVar
    username: str
    password: str
    encryption: Literal["mandatory", "optional", "forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    status_url: str
    parallel: list[ConnectDeviceSingle]


class ConnectDeviceSerial(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'from': str
    headers: list[ConnectHeaders]
    codecs: str
    webrtc_media: bool | SWMLVar
    session_timeout: int | SWMLVar
    ringback: list[str]
    result: ConnectSwitch | list[CondParams]
    timeout: int | SWMLVar
    max_duration: int | SWMLVar
    answer_on_bridge: bool | SWMLVar
    confirm: str | list[ValidConfirmMethods]
    confirm_timeout: int | SWMLVar
    username: str
    password: str
    encryption: Literal["mandatory", "optional", "forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    status_url: str
    serial: list[ConnectDeviceSingle]


class ConnectDeviceSerialParallel(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'from': str
    headers: list[ConnectHeaders]
    codecs: str
    webrtc_media: bool | SWMLVar
    session_timeout: int | SWMLVar
    ringback: list[str]
    result: ConnectSwitch | list[CondParams]
    timeout: int | SWMLVar
    max_duration: int | SWMLVar
    answer_on_bridge: bool | SWMLVar
    confirm: str | list[ValidConfirmMethods]
    confirm_timeout: int | SWMLVar
    username: str
    password: str
    encryption: Literal["mandatory", "optional", "forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    status_url: str
    serial_parallel: list[list[ConnectDeviceSingle]]


class ConnectDeviceSingle(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'from': str
    headers: list[ConnectHeaders]
    codecs: str
    webrtc_media: bool | SWMLVar
    session_timeout: int | SWMLVar
    ringback: list[str]
    result: ConnectSwitch | list[CondParams]
    timeout: int | SWMLVar
    max_duration: int | SWMLVar
    answer_on_bridge: bool | SWMLVar
    confirm: str | list[ValidConfirmMethods]
    confirm_timeout: int | SWMLVar
    username: str
    password: str
    encryption: Literal["mandatory", "optional", "forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    status_url: str
    to: str
    name: str
    codec: str
    realtime: bool | SWMLVar
    status_url_method: Literal["GET", "POST"]
    authorization_bearer_token: str
    custom_parameters: dict[str, Any]


class ConnectHeaders(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    value: str


class ConnectSwitch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    variable: str
    case: dict[str, Any]
    default: list[SWMLMethod]


class ConstProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    const: dict[str, Any]


class ContextPOMSteps(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    step_criteria: str
    functions: list[str]
    valid_contexts: list[str]
    skip_user_turn: bool | SWMLVar
    end: bool
    valid_steps: list[str]
    pom: list[POM]


ContextSteps: TypeAlias = "ContextPOMSteps | ContextTextSteps"


class ContextSwitchAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    context_switch: dict[str, Any]


class ContextTextSteps(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    step_criteria: str
    functions: list[str]
    valid_contexts: list[str]
    skip_user_turn: bool | SWMLVar
    end: bool
    valid_steps: list[str]
    text: str


class Contexts(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: ContextsObject


ContextsObject: TypeAlias = "ContextsPOMObject | ContextsTextObject"


class ContextsPOMObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    steps: list[ContextSteps]
    isolated: bool
    enter_fillers: list[FunctionFillers]
    exit_fillers: list[FunctionFillers]
    pom: list[POM]


class ContextsTextObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    steps: list[ContextSteps]
    isolated: bool
    enter_fillers: list[FunctionFillers]
    exit_fillers: list[FunctionFillers]
    text: str


class ConversationMessage(TypedDict, total=False):
    """A message object representing a single turn in the conversation history.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    role: ConversationRole
    content: str
    lang: str


ConversationRole: TypeAlias = "Literal['user', 'assistant', 'system']"

CustomTranslationFilter: TypeAlias = "str"


class DataMap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    output: Output
    expressions: list[Expression]
    webhooks: list[Webhook]


class Denoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    denoise: dict[str, Any]


class DetectMachine(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    detect_machine: dict[str, Any]


Direction: TypeAlias = "Literal['inbound', 'outbound']"


class EnterQueue(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    enter_queue: EnterQueueObject


class EnterQueueObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    queue_name: str
    transfer_after_bridge: str | SWMLVar
    status_url: str
    wait_url: str | SWMLVar
    wait_time: int | SWMLVar


class Execute(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    execute: dict[str, Any]


class ExecuteSwitch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    variable: str
    case: dict[str, Any]
    default: list[SWMLMethod]


class Expression(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    string: str
    pattern: str
    output: Output


class FabricDeviceLeg(TypedDict, total=False):
    """A Fabric subscriber device leg.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    # non-identifier field 'from': str
    to: str
    direction: CallDirection
    source: Literal["realtime_api"]
    url: str | None
    charge: float
    created_at: str
    charge_details: list[ChargeDetails]
    status: None
    type: Literal["fabric_subscriber_device_leg"]


FunctionFillers: TypeAlias = "dict[str, Any]"


class FunctionParameters(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["object"]
    properties: dict[str, Any]
    required: list[str]


class Goto(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    goto: dict[str, Any]


class HangUpHookSWAIGFunction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    purpose: str
    parameters: FunctionParameters
    fillers: FunctionFillers
    argument: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    skip_fillers: bool | SWMLVar
    web_hook_url: str
    wait_file: str
    wait_file_loops: int | str
    wait_for_fillers: bool | SWMLVar
    function: Literal["hangup_hook"]


class Hangup(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hangup: dict[str, Any]


class HangupAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hangup: bool | SWMLVar


HangupReason: TypeAlias = (
    "Literal['hangup', 'cancel', 'busy', 'noAnswer', 'decline', 'error']"
)


class Hint(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hint: str
    pattern: str
    replace: str
    ignore_case: bool | SWMLVar


class HoldAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hold: int | SWMLVar | dict[str, Any]


class InjectAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    inject: dict[str, Any]


class IntegerProperty(TypedDict, total=False):
    """Base interface for all property types

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["integer"]
    enum: list[int]
    default: int | SWMLVar


class JoinConference(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    join_conference: JoinConferenceObject


class JoinConferenceObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    muted: bool | SWMLVar
    beep: Literal["true", "false", "onEnter", "onExit"]
    start_on_enter: bool | SWMLVar
    end_on_exit: bool | SWMLVar
    wait_url: str | SWMLVar
    max_participants: int | SWMLVar
    record: Literal["do-not-record", "record-from-start"]
    region: str
    trim: Literal["trim-silence", "do-not-trim"]
    coach: str
    status_callback_event: Literal[
        "start",
        "end",
        "join",
        "leave",
        "mute",
        "hold",
        "modify",
        "speaker",
        "announcement",
    ]
    status_callback: str
    status_callback_method: Literal["GET", "POST"]
    recording_status_callback: str
    recording_status_callback_method: Literal["GET", "POST"]
    recording_status_callback_event: Literal["in-progress", "completed", "absent"]
    result: dict[str, Any] | list[CondParams]


class JoinRoom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    join_room: dict[str, Any]


class Label(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    label: str


class LanguageParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stability: float | SWMLVar
    similarity: float | SWMLVar


Languages: TypeAlias = "LanguagesWithSoloFillers | LanguagesWithFillers"


class LanguagesWithFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    code: str
    voice: str
    model: str
    emotion: Literal["auto"]
    speed: Literal["auto"]
    engine: str
    params: LanguageParams
    function_fillers: list[str]
    speech_fillers: list[str]


class LanguagesWithSoloFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    code: str
    voice: str
    model: str
    emotion: Literal["auto"]
    speed: Literal["auto"]
    engine: str
    params: LanguageParams
    fillers: list[str]


class LiveTranscribe(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_transcribe: dict[str, Any]


class LiveTranscribeStartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    start: dict[str, Any]


LiveTranscribeStopAction: TypeAlias = "Literal['stop']"


class LiveTranscribeSummarizeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    summarize: dict[str, Any]


class LiveTranslate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_translate: dict[str, Any]


class LiveTranslateInjectAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    inject: dict[str, Any]


class LiveTranslateStartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    start: dict[str, Any]


LiveTranslateStopAction: TypeAlias = "Literal['stop']"


class LiveTranslateSummarizeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    summarize: dict[str, Any]


class NullProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["null"]
    description: str


class NumberProperty(TypedDict, total=False):
    """Base interface for all property types

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["number"]
    enum: list[int | float] | list[SWMLVar]
    default: int | float | SWMLVar


class ObjectProperty(TypedDict, total=False):
    """Base interface for all property types

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["object"]
    default: dict[str, Any]
    properties: dict[str, Any]
    required: list[str]


class OneOfProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    oneOf: list[SchemaType]


class Output(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    response: str
    action: list[Action]


POM: TypeAlias = "PomSectionBodyContent | PomSectionBulletsContent"


class Pay(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    pay: dict[str, Any]


class PayParameters(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    value: str


PayPromptAction: TypeAlias = "PayPromptSayAction | PayPromptPlayAction"


class PayPromptPlayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["Play"]
    phrase: str


class PayPromptSayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["Say"]
    phrase: str


class PayPrompts(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    actions: list[PayPromptAction]
    # non-identifier field 'for': str
    attempts: str
    card_type: str
    error_type: str


class Play(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    play: PlayWithURL | PlayWithURLS


class PlayWithURL(TypedDict, total=False):
    """Play with a single URL

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    auto_answer: bool | SWMLVar
    volume: float | SWMLVar
    say_voice: str
    say_language: str
    say_gender: str
    status_url: str
    url: play_url | SWMLVar


class PlayWithURLS(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    auto_answer: bool | SWMLVar
    volume: float | SWMLVar
    say_voice: str
    say_language: str
    say_gender: str
    status_url: str
    urls: list[play_url] | list[SWMLVar]


class PlaybackBGAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    playback_bg: dict[str, Any]


class PomSectionBodyContent(TypedDict, total=False):
    """Content model with body text and optional bullets

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    title: str
    subsections: list[POM]
    numbered: bool | SWMLVar
    numberedBullets: bool | SWMLVar
    body: str
    bullets: list[str]


class PomSectionBulletsContent(TypedDict, total=False):
    """Content model with bullets and optional body

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    title: str
    subsections: list[POM]
    numbered: bool | SWMLVar
    numberedBullets: bool | SWMLVar
    body: str
    bullets: list[str]


class Prompt(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    prompt: dict[str, Any]


class Pronounce(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    replace: str
    # non-identifier field 'with': str
    ignore_case: bool | SWMLVar


class ReceiveFax(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    receive_fax: dict[str, Any]


class Record(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    record: dict[str, Any]


class RecordCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    record_call: dict[str, Any]


class Request(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    request: dict[str, Any]


class Return(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'return': dict[str, Any]


class SIPRefer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sip_refer: dict[str, Any]


class SMSWithBody(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    to_number: str
    from_number: str
    region: str
    tags: list[str]
    body: str


class SMSWithMedia(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    to_number: str
    from_number: str
    region: str
    tags: list[str]
    media: list[str]
    body: str


class SWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    defaults: SWAIGDefaults
    native_functions: list[SWAIGNativeFunction]
    includes: list[SWAIGIncludes]
    functions: list[SWAIGFunction]
    internal_fillers: SWAIGInternalFiller


class SWAIGDefaults(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    web_hook_url: str


SWAIGFunction: TypeAlias = "UserSWAIGFunction | StartUpHookSWAIGFunction | HangUpHookSWAIGFunction | SummarizeConversationSWAIGFunction"


class SWAIGIncludes(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    functions: list[str]
    url: str
    meta_data: dict[str, Any]


class SWAIGInternalFiller(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hangup: FunctionFillers
    check_time: FunctionFillers
    wait_for_user: FunctionFillers
    wait_seconds: FunctionFillers
    adjust_response_latency: FunctionFillers
    next_step: FunctionFillers
    change_context: FunctionFillers
    get_visual_input: FunctionFillers
    get_ideal_strategy: FunctionFillers


SWAIGNativeFunction: TypeAlias = (
    "Literal['check_time', 'wait_seconds', 'wait_for_user', 'adjust_response_latency']"
)


class SWMLAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: SWMLObject


SWMLMethod: TypeAlias = "Answer | AI | AmazonBedrock | Cond | Connect | Denoise | EnterQueue | Execute | Goto | Label | LiveTranscribe | LiveTranslate | Hangup | JoinRoom | JoinConference | Play | Prompt | ReceiveFax | Record | RecordCall | Request | Return | SendDigits | SendFax | SendSMS | Set | Sleep | SIPRefer | StopDenoise | StopRecordCall | StopTap | Switch | Tap | Transfer | Unset | Pay | DetectMachine | UserEvent"


class SWMLObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    version: Literal["1.0.0"]
    sections: Section


SWMLVar: TypeAlias = "str"


class SayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    say: str


SchemaType: TypeAlias = "StringProperty | IntegerProperty | NumberProperty | BooleanProperty | ArrayProperty | ObjectProperty | NullProperty | OneOfProperty | AllOfProperty | AnyOfProperty | ConstProperty"


class Section(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    main: list[SWMLMethod]


class SendDigits(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_digits: dict[str, Any]


class SendFax(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_fax: dict[str, Any]


class SendSMS(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_sms: SMSWithBody | SMSWithMedia


class Set(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set: dict[str, Any]


class SetGlobalDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set_global_data: dict[str, Any]


class SetMetaDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set_meta_data: dict[str, Any]


class Sleep(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sleep: dict[str, Any] | int | SWMLVar


SpeechEngine: TypeAlias = "Literal['deepgram', 'google']"


class StartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    start: dict[str, Any]


class StartUpHookSWAIGFunction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    purpose: str
    parameters: FunctionParameters
    fillers: FunctionFillers
    argument: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    skip_fillers: bool | SWMLVar
    web_hook_url: str
    wait_file: str
    wait_file_loops: int | str
    wait_for_fillers: bool | SWMLVar
    function: Literal["startup_hook"]


class StopAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop: bool | SWMLVar


class StopDenoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_denoise: dict[str, Any]


class StopPlaybackBGAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_playback_bg: bool | SWMLVar


class StopRecordCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_record_call: dict[str, Any]


class StopTap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_tap: dict[str, Any]


StringFormat: TypeAlias = "Literal['date_time', 'time', 'date', 'duration', 'email', 'hostname', 'ipv4', 'ipv6', 'uri', 'uuid']"


class StringProperty(TypedDict, total=False):
    """Base interface for all property types

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["string"]
    enum: list[str]
    default: str
    pattern: str
    format: StringFormat


class SummarizeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    summarize: dict[str, Any]


SummarizeActionUnion: TypeAlias = "SummarizeAction | Literal['summarize']"


class SummarizeConversationSWAIGFunction(TypedDict, total=False):
    """An internal reserved function that generates a summary of the conversation and sends any specified properties to the configured webhook after the conversation has ended.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    purpose: str
    parameters: FunctionParameters
    fillers: FunctionFillers
    argument: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    skip_fillers: bool | SWMLVar
    web_hook_url: str
    wait_file: str
    wait_file_loops: int | str
    wait_for_fillers: bool | SWMLVar
    function: Literal["summarize_conversation"]


class Switch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    switch: dict[str, Any]


class Tap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    tap: dict[str, Any]


class ToggleFunctionsAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    toggle_functions: list[dict[str, Any]]


TranscribeAction: TypeAlias = (
    "TranscribeStartAction | Literal['stop'] | TranscribeSummarizeActionUnion"
)

TranscribeDirection: TypeAlias = "Literal['remote-caller', 'local-caller']"


class TranscribeStartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    start: dict[str, Any]


class TranscribeSummarizeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    summarize: dict[str, Any]


TranscribeSummarizeActionUnion: TypeAlias = (
    "TranscribeSummarizeAction | Literal['summarize']"
)


class Transfer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    transfer: dict[str, Any]


TranslateAction: TypeAlias = (
    "StartAction | Literal['stop'] | SummarizeActionUnion | InjectAction"
)

TranslateDirection: TypeAlias = "Literal['remote-caller', 'local-caller']"

TranslationFilterPreset: TypeAlias = (
    "Literal['polite', 'rude', 'professional', 'shakespeare', 'gen-z']"
)


class Types_StatusCodes_RestApiErrorItem(TypedDict, total=False):
    """Details about a specific error.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: str
    code: str
    message: str
    attribute: str | None
    url: str


class Types_StatusCodes_StatusCode400(TypedDict, total=False):
    """The request is invalid.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Bad Request"]


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


class Types_StatusCodes_StatusCode404(TypedDict, total=False):
    """The server cannot find the requested resource.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Not Found"]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


class Unset(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    unset: str | list[str]


class UnsetGlobalDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    unset_global_data: str | dict[str, Any]


class UnsetMetaDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    unset_meta_data: str | dict[str, Any]


class UserEvent(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    user_event: dict[str, Any]


class UserInputAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    user_input: str


class UserSWAIGFunction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    purpose: str
    parameters: FunctionParameters
    fillers: FunctionFillers
    argument: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    skip_fillers: bool | SWMLVar
    web_hook_url: str
    wait_file: str
    wait_file_loops: int | str
    wait_for_fillers: bool | SWMLVar
    function: str


ValidConfirmMethods: TypeAlias = "Cond | Set | Unset | Hangup | Play | Prompt | Record | RecordCall | StopRecordCall | Tap | StopTap | SendDigits | SendSMS | Denoise | StopDenoise"


class Webhook(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    expressions: list[Expression]
    error_keys: str | list[str]
    url: str
    foreach: dict[str, Any]
    headers: dict[str, Any]
    method: Literal["GET", "POST", "PUT", "DELETE"]
    input_args_as_params: bool | SWMLVar
    params: dict[str, Any]
    require_args: str | list[str]
    output: Output


play_url: TypeAlias = "str"

uuid: TypeAlias = "str"

CallCommandsRequest: TypeAlias = "CallRequest"
CallCommandsResponse: TypeAlias = "CallResponse"
