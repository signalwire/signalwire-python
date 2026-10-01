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

    ai: AIObject | list[str | SWMLVar] | float | dict[str, Any]


class AIObject(TypedDict, total=False):
    """Creates an AI agent that conducts voice conversations using automatic speech recognition (ASR),

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    SWAIG: list[dict[str, Any]] | SWAIG
    agent: str | SWMLVar
    engine: str | SWMLVar
    global_data: dict[str, Any]
    hints: list[Hint | str]
    languages: list[Languages]
    multilingual: dict[str, Any]
    params: AIParams
    post_prompt: AIPostPrompt
    post_prompt_auth_password: str | SWMLVar
    post_prompt_auth_user: str | SWMLVar
    post_prompt_url: str | SWMLVar
    prompt: AIPrompt
    pronounce: list[Pronounce]
    voice: str | SWMLVar


class AIParams(TypedDict, total=False):
    """An object of any necessary parameters for the API call. The key is the parameter name and the value is the parameter value.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    acknowledge_interruptions: int | str | bool
    acoustic_eot_gate_prob: float | str
    acoustic_eot_trust_prob: float | str
    ai_model: str
    ai_name: str
    ai_volume: int | str
    app_name: str
    asr_diarize: bool | float | str
    asr_params: dict[str, Any]
    asr_smart_format: bool | float | str
    asr_speaker_affinity: bool | float | str
    attention_escalate_prompt: str
    attention_timeout: AttentionTimeout | str
    attention_timeout_prompt: str
    auth_token: str
    auto_correct: bool | float | str
    azure_stream_first: bool | float | str
    azure_tts_key: str
    background_file: str
    background_file_loops: int | str
    background_file_volume: int | str
    barge_functions: bool | float | str
    barge_match_string: str
    barge_min_words: int | str
    bill_all_tts: bool | float | str
    cache: bool | float | str
    call_uuid: str
    cartesia_key: str
    cartesia_model: str
    cartesia_stream_first: bool | float | str
    confidence: float | str
    conscience: str
    conversation_id: str
    conversation_sliding_window: int | str
    convo: list[ConversationMessage]
    debug_webhook_level: int | str
    debug_webhook_url: str
    deepgram_key_override: str
    deepgram_stream_first: bool | float | str
    deepgram_tts_key: str
    deepgram_url_override: str
    developer_prompt: str
    digit_terminators: str
    digit_timeout: int | str
    direction: Direction
    double_turn_filler_every_n: float | str
    double_turn_filler_min_ms: float | str
    double_turn_model: str
    double_turn_prompt: str
    double_turn_wait_ms: float | str
    double_turns: bool | str
    eleven_labs_key: str
    eleven_labs_model: str
    eleven_labs_similarity: float | str
    eleven_labs_stability: float | str
    eleven_labs_stream_first: bool | float | str
    enable_barge: str | bool
    enable_inner_dialog: bool | str
    enable_pause: bool | str
    enable_text_normalization: str
    enable_thinking: bool | str
    enable_turn_detection: bool | str
    enable_vision: bool | str
    end_of_speech_timeout: int | str
    energy_level: float | str
    escalate_after_ms: int | str
    escalate_after_turns: int | str
    event_webhook_url: str
    ext: str
    first_word_timeout: int | str
    fish_key: str
    fish_model: str
    function_filler_sequence_gap_ms: float | str
    function_wait_for_talking: bool | float | str
    functions_on_no_response: bool | float | str
    grok_key: str
    groq_tts_key: str
    hard_stop_prompt: str
    hard_stop_time: str
    hold_music: str
    hold_on_process: bool | float | str
    inactivity_timeout: int | str
    initial_sleep_ms: int | str
    inner_dialog: dict[str, Any]
    inner_dialog_model: str
    inner_dialog_prompt: str
    inner_dialog_scorecard: bool | dict[str, Any]
    input_poll_freq: int | str
    interrupt_on_noise: int | str | bool
    interrupt_prompt: str
    inworld_apikey: str
    inworld_key: str
    inworld_model: str
    language: str
    # deprecated: languages_enabled
    languages_enabled: bool | float | str
    lipsync_debug: bool | float | str
    llm_diarize_aware: bool | float | str
    local_tz: str
    max_emotion: int | str
    max_response_tokens: float | str
    min_utterance_ms: int | str
    minimax_key: str
    minimax_model: str
    mistral_key: str
    mistral_model: str
    model: str
    openai_asr_engine: str
    openai_azure: bool | float | str
    openai_gcloud_version: str
    openai_stream_first: bool | float | str
    openai_tts_key: str
    openai_tts_url: str
    outbound_attention_timeout: int | str
    pcm_channels: int | str
    pcm_rate: int | str
    persist_global_data: bool | str
    pom_format: str
    provider: str
    pvt_params: str
    realtime: dict[str, Any]
    redact_prompt: str
    rime_apikey: str
    rime_key: str
    rime_model: str
    rime_stream_first: bool | float | str
    sample_rate: int | str
    save_conversation: bool | float | str
    send_single_llm_response: bool | float | str
    similarity: float | str
    smallest_key: str
    smallest_model: str
    speak_when_spoken_to: bool | str
    speaker: str
    speech_event_timeout: int | str
    speech_gen_quick_stops: int | str
    speech_timeout: int | str
    speechify_key: str
    speechify_loudness_normalization: bool | float | str
    speechify_model: str
    speechify_output_format: str
    speechify_stream_first: bool | float | str
    speechify_text_normalization: bool | float | str
    speed: float | str
    stability: float | str
    start_paused: bool | str
    static_greeting: str
    static_greeting_no_barge: bool | float | str
    stream_first: bool | float | str
    streaming: bool | float | str
    strict_mode: str
    summary_mode: str
    swaig_allow_settings: bool | float | str
    swaig_allow_swml: bool | float | str
    swaig_post_conversation: bool | float | str
    swaig_post_swml_vars: list[str] | bool | str
    swaig_set_global_data: bool | float | str
    target_first_segment_ms: int | str
    text_normalization_far_dir: str
    thinking_model: str
    tool_result_distill: bool | dict[str, Any]
    transfer_summary: bool | float | str
    transparent_barge: bool | float | str
    transparent_barge_max_time: int | str
    tts_number_format: str
    turn_detection: bool | str
    turn_detection_min_length: int | str
    turn_detection_timeout: int | str
    turn_filler_every_n: float | str
    turn_filler_min_ms: float | str
    turn_filler_sources: str
    url: str
    utility_model: str
    vad_config: str
    video_fps: int | str
    video_idle_file: str
    video_listening_file: str
    video_scale: str
    video_talking_file: str
    vision_model: str
    voice_name: str
    vol: int | str
    wait_for_user: bool | float | str
    wake_prefix: str


class AIPostPrompt(TypedDict, total=False):
    """The final set of instructions and configuration settings to send to the agent.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    frequency_penalty: Any
    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[POM]
    presence_penalty: Any
    reasoning_effort: str
    temperature: float
    text: str
    top_p: float
    verbosity: str


class AIPostPromptPom(TypedDict, total=False):
    """The final set of instructions and configuration settings to send to the agent.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    frequency_penalty: Any
    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[POM]
    presence_penalty: Any
    reasoning_effort: str
    temperature: float
    text: str
    top_p: float
    verbosity: str


class AIPostPromptText(TypedDict, total=False):
    """The final set of instructions and configuration settings to send to the agent.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    frequency_penalty: Any
    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[POM]
    presence_penalty: Any
    reasoning_effort: str
    temperature: float
    text: str
    top_p: float
    verbosity: str


class AIPrompt(TypedDict, total=False):
    """Defines the AI agent's personality, goals, behaviors, and instructions for handling conversations.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    contexts: Contexts
    frequency_penalty: Any
    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[dict[str, Any]]
    presence_penalty: Any
    reasoning_effort: str
    steps: list[Step]
    temperature: float
    text: str
    top_p: float
    verbosity: str


class AIPromptPom(TypedDict, total=False):
    """Defines the AI agent's personality, goals, behaviors, and instructions for handling conversations.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    contexts: Contexts
    frequency_penalty: Any
    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[dict[str, Any]]
    presence_penalty: Any
    reasoning_effort: str
    steps: list[Step]
    temperature: float
    text: str
    top_p: float
    verbosity: str


class AIPromptText(TypedDict, total=False):
    """Defines the AI agent's personality, goals, behaviors, and instructions for handling conversations.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    contexts: Contexts
    frequency_penalty: Any
    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[dict[str, Any]]
    presence_penalty: Any
    reasoning_effort: str
    steps: list[Step]
    temperature: float
    text: str
    top_p: float
    verbosity: str


class Action(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class AllOfProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    allOf: list[SchemaType]


class AmazonBedrock(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    amazon_bedrock: AmazonBedrockObject | list[Any] | float | str


class AmazonBedrockObject(TypedDict, total=False):
    """Creates a new Bedrock AI Agent

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    SWAIG: BedrockSWAIG
    app_name: str
    assistant_name: str
    assistant_prompt: str
    conversation_id: str
    global_data: dict[str, Any]
    greeting_prompt: dict[str, Any]
    params: BedrockParams
    post_prompt: BedrockPostPrompt
    post_prompt_url: str
    prompt: BedrockPrompt
    transcript_webhook_url: str


class Answer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    answer: dict[str, Any] | list[float | SWMLVar]


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
    """A JSON object containing parameters as key-value pairs.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    attention_timeout: float | str
    compact_conversation_time: str
    compact_strategy: str
    hard_stop_prompt: str
    hard_stop_time: str
    inactivity_timeout: float | str
    video_idle_file: str
    video_listening_file: str
    video_talking_file: str


class BedrockPostPrompt(TypedDict, total=False):
    """The final set of instructions and configuration settings to send to the agent.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    pom: list[dict[str, Any]]
    text: str


class BedrockPrompt(TypedDict, total=False):
    """Establishes the initial set of instructions and settings to configure the agent.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    pom: list[dict[str, Any]]
    temperature: float | str
    text: str
    top_p: float | str
    voice_id: str


class BedrockSWAIG(TypedDict, total=False):
    """An object holding the user-defined functions/endpoints that can be executed during the dialogue. The engine reads two keys off it: `functions`, the array of function definitions, and `defaults`, an object of settings applied to each of them.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    defaults: dict[str, Any]
    functions: list[BedrockSWAIGFunction]


class BedrockSWAIGFunction(TypedDict, total=False):
    """Without `description` and `function`, `SWAIG` (checked only where amazon_bedrock discards the result) has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    data_map: DataMap
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: JsonSchema
    web_hook_url: str


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


CallCreateParamsSWML = TypedDict(
    "CallCreateParamsSWML",
    {
        "from": "str",
        "to": "str",
        "caller_id": "str",
        "fallback_url": "str",
        "status_url": "str",
        "status_events": "list[Literal['answered', 'queued', 'initiated', 'ringing', 'ending', 'ended']]",
        "url_method": "str",
        "codecs": "list[str] | str",
        "to_script": "str | dict[str, Any]",
        "timeout": "int",
        "max_price_per_minute": "float",
        "send_digits": "str",
        "region": "str | list[str]",
        "username": "str",
        "password": "str",
        "headers": "list[dict[str, Any]]",
        "custom_variables": "dict[str, str]",
        "swml": "str | dict[str, Any]",
    },
    total=False,
)
CallCreateParamsSWML.__doc__ = (
    """Open shape: extra server keys permitted; not validated at runtime."""
)

CallCreateParamsURL = TypedDict(
    "CallCreateParamsURL",
    {
        "from": "str",
        "to": "str",
        "caller_id": "str",
        "fallback_url": "str",
        "status_url": "str",
        "status_events": "list[Literal['answered', 'queued', 'initiated', 'ringing', 'ending', 'ended']]",
        "url_method": "str",
        "codecs": "list[str] | str",
        "to_script": "str | dict[str, Any]",
        "timeout": "int",
        "max_price_per_minute": "float",
        "send_digits": "str",
        "region": "str | list[str]",
        "username": "str",
        "password": "str",
        "headers": "list[dict[str, Any]]",
        "custom_variables": "dict[str, str]",
        "url": "str",
    },
    total=False,
)
CallCreateParamsURL.__doc__ = (
    """Open shape: extra server keys permitted; not validated at runtime."""
)


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


CallLeg = TypedDict(
    "CallLeg",
    {
        "id": "uuid",
        "from": "str",
        "to": "str",
        "direction": "CallDirection",
        "source": "Literal['realtime_api']",
        "url": "str | None",
        "charge": "float",
        "created_at": "str",
        "charge_details": "list[ChargeDetails]",
        "status": "CallResponseStatus | None",
        "duration": "int | None",
        "duration_ms": "int | None",
        "billing_ms": "int | None",
        "type": "Literal['relay_pstn_call'] | Literal['relay_sip_call'] | Literal['relay_webrtc_call']",
        "qos_metrics": "dict[str, Any] | None",
        "parent_id": "uuid | None",
    },
    total=False,
)
CallLeg.__doc__ = """A Call leg (PSTN, SIP, or WebRTC).

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""


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


CallRequest: TypeAlias = "CallCreateRequest | CallUpdateCurrentCallRequest | CallHangupRequest | CallHoldRequest | CallUnholdRequest | CallAIMessageRequest | CallLiveTranscribeRequest | CallLiveTranslateRequest | CallTransferRequest | CallUserEventRequest | CallDisconnectRequest | CallPlayRequest | CallPlayPauseRequest | CallPlayResumeRequest | CallPlayStopRequest | CallPlayVolumeRequest | CallRecordRequest | CallRecordPauseRequest | CallRecordResumeRequest | CallRecordStopRequest | CallCollectRequest | CallCollectStopRequest | CallCollectStartInputTimersRequest | CallDetectRequest | CallDetectStopRequest | CallTapRequest | CallTapStopRequest | CallStreamRequest | CallStreamStopRequest | CallDenoiseRequest | CallDenoiseStopRequest | CallTranscribeRequest | CallTranscribeStopRequest | CallAIStopRequest | CallAISidecarRequest | CallAISidecarAskRequest | CallAISidecarPokeRequest | CallAISidecarStopRequest | CallAISidecarStatusRequest | CallSendFaxStopRequest | CallReceiveFaxStopRequest | CallReferRequest"


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


class CallAISidecarRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.ai_sidecar"]
    params: dict[str, Any]


class CallAISidecarAskRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.ai_sidecar.ask"]
    params: dict[str, Any]


class CallAISidecarPokeRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.ai_sidecar.poke"]
    params: dict[str, Any]


class CallAISidecarStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.ai_sidecar.stop"]
    params: dict[str, Any]


class CallAISidecarStatusRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    command: Literal["calling.ai_sidecar.status"]
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


CallResponse: TypeAlias = (
    "CallLeg | FabricDeviceLeg | VideoRoomCallLeg | DialogflowCallLeg"
)

VideoRoomCallLeg = TypedDict(
    "VideoRoomCallLeg",
    {
        "id": "uuid",
        "from": "str | None",
        "to": "str | None",
        "direction": "str | None",
        "source": "Literal['realtime_api']",
        "url": "None",
        "charge": "float",
        "created_at": "str",
        "charge_details": "list[ChargeDetails]",
        "status": "str | None",
        "duration": "int | None",
        "duration_ms": "int | None",
        "type": "Literal['video_room_pstn_leg', 'video_room_sip_leg']",
    },
    total=False,
)
VideoRoomCallLeg.__doc__ = """A PSTN or SIP leg joined to a video room.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""

DialogflowCallLeg = TypedDict(
    "DialogflowCallLeg",
    {
        "id": "uuid",
        "from": "str | None",
        "to": "str | None",
        "source": "Literal['dialogflow']",
        "url": "None",
        "charge": "float",
        "created_at": "str",
        "charge_details": "list[ChargeDetails]",
        "status": "str | None",
        "duration": "float | None",
        "type": "Literal['dialogflow_call']",
    },
    total=False,
)
DialogflowCallLeg.__doc__ = """A Dialogflow call.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""

CallResponseStatus: TypeAlias = "Literal['queued', 'initiated', 'created', 'ringing', 'answered', 'ending', 'ended', 'failed', 'canceled', 'completed']"

CallStatus: TypeAlias = "str"


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
    swml: str | dict[str, Any]


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

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class ChangeStepAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class ChargeDetails(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    charge: float


class Cond(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    cond: list[CondParams]


CondElse = TypedDict(
    "CondElse",
    {
        "else": "list[SWMLMethod]",
        "then": "list[SWMLMethod]",
        "when": "str",
    },
    total=False,
)
CondElse.__doc__ = (
    """Open shape: extra server keys permitted; not validated at runtime."""
)

CondParams = TypedDict(
    "CondParams",
    {
        "else": "list[SWMLMethod]",
        "then": "list[SWMLMethod]",
        "when": "str",
    },
    total=False,
)
CondParams.__doc__ = (
    """Open shape: extra server keys permitted; not validated at runtime."""
)

CondReg = TypedDict(
    "CondReg",
    {
        "else": "list[SWMLMethod]",
        "then": "list[SWMLMethod]",
        "when": "str",
    },
    total=False,
)
CondReg.__doc__ = (
    """Open shape: extra server keys permitted; not validated at runtime."""
)


class Connect(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    connect: ConnectDeviceSingle


class ConnectHeaders(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    value: str | SWMLVar


class ConnectSwitch(TypedDict, total=False):
    """Execute different instructions based on a variable's value.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    default: list[SWMLMethod] | dict[str, Any]
    case: dict[str, list[SWMLMethod] | dict[str, Any]]
    variable: str | SWMLVar


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

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


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
    """Open shape: extra server keys permitted; not validated at runtime."""

    content: str
    lang: str
    role: ConversationRole
    tool_call_id: str
    tool_calls: list[Any]


ConversationRole: TypeAlias = "str"

CustomTranslationFilter: TypeAlias = "str"


class DataMap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    contexts: list[Any] | bool | None | float | dict[str, Any] | str
    expressions: list[Expression] | Expression
    output: Output
    webhooks: list[Webhook] | Webhook


class Denoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    denoise: dict[str, Any] | list[Any] | float | str


class DetectMachine(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    detect_machine: dict[str, Any] | list[Any] | float | str


Direction: TypeAlias = "str"


class EnterQueue(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    enter_queue: EnterQueueObject | list[Any] | float | str


class EnterQueueObject(TypedDict, total=False):
    """Place the current call in a named queue where it will wait to be connected to an available agent or resource.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    execute_after_queue: str | SWMLVar
    queue_name: str | SWMLVar
    status_url: str | SWMLVar
    wait_time: int | SWMLVar
    wait_url: str | SWMLVar
    whisper_url: str | SWMLVar


class Execute(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    execute: dict[str, Any] | list[str | SWMLVar] | float


class ExecuteSwitch(TypedDict, total=False):
    """Execute different instructions based on a variable's value.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    default: list[SWMLMethod] | dict[str, Any]
    case: dict[str, list[SWMLMethod] | dict[str, Any]]
    variable: str | SWMLVar


Expression = TypedDict(
    "Expression",
    {
        "pattern": "str",
        "expr": "str",
        "nomatch-output": "Output",
        "output": "Output",
        "string": "str",
    },
    total=False,
)
Expression.__doc__ = """Without one of `expr` / `string` and `output`, a Expression has no effect: it is accepted and ignored, not rejected.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""

FabricDeviceLeg = TypedDict(
    "FabricDeviceLeg",
    {
        "id": "uuid",
        "from": "str",
        "to": "str",
        "direction": "CallDirection",
        "source": "Literal['realtime_api']",
        "url": "str | None",
        "charge": "float",
        "created_at": "str",
        "charge_details": "list[ChargeDetails]",
        "status": "None",
        "type": "Literal['fabric_subscriber_device_leg']",
    },
    total=False,
)
FabricDeviceLeg.__doc__ = """A Fabric subscriber device leg.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""


class FunctionFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


FunctionParameters = TypedDict(
    "FunctionParameters",
    {
        "title": "str",
        "description": "str",
        "type": "Literal['array', 'boolean', 'integer', 'null', 'number', 'object', 'string'] | list[Literal['array', 'boolean', 'integer', 'null', 'number', 'object', 'string']]",
        "const": "Any",
        "enum": "list[Any]",
        "format": "str",
        "pattern": "str",
        "minimum": "float",
        "maximum": "float",
        "exclusiveMinimum": "float",
        "exclusiveMaximum": "float",
        "minLength": "int",
        "maxLength": "int",
        "minItems": "int",
        "maxItems": "int",
        "minProperties": "int",
        "maxProperties": "int",
        "default": "Any",
        "examples": "list[Any]",
        "deprecated": "bool",
        "nullable": "bool",
        "properties": "dict[str, FunctionParameters | bool]",
        "required": "list[str]",
        "prefixItems": "list[FunctionParameters | bool]",
        "items": "FunctionParameters | bool",
        "propertyNames": "FunctionParameters | bool",
        "additionalProperties": "FunctionParameters | bool",
        "unevaluatedProperties": "FunctionParameters | bool",
        "oneOf": "list[FunctionParameters | bool]",
        "anyOf": "list[FunctionParameters | bool]",
        "allOf": "list[FunctionParameters | bool]",
        "not": "FunctionParameters | bool",
        "contains": "FunctionParameters | bool",
        "dependentRequired": "dict[str, list[str]]",
        "dependentSchemas": "dict[str, FunctionParameters | bool]",
        "else": "FunctionParameters | bool",
        "example": "Any",
        "if": "FunctionParameters | bool",
        "maxContains": "int",
        "minContains": "int",
        "multipleOf": "float",
        "patternProperties": "dict[str, FunctionParameters | bool]",
        "propertyOrdering": "list[str]",
        "readOnly": "bool",
        "then": "FunctionParameters | bool",
        "unevaluatedItems": "FunctionParameters | bool",
        "uniqueItems": "bool",
        "writeOnly": "bool",
    },
    total=False,
)
FunctionParameters.__doc__ = """A JSON Schema (draft 2020-12) that may also carry `example`, `nullable`, `propertyOrdering`: the value is forwarded verbatim to whichever model API the session resolves to, and those receivers do not accept one vocabulary, so a schema here must be able to express their UNION (vocabulary_union). The engine does not inspect it.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""


class Goto(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    goto: dict[str, Any] | list[str | SWMLVar] | float


class HangUpHookSWAIGFunction(TypedDict, total=False):
    """Without one of `data_map` / `web_hook_url`, one of `description` / `purpose` and `function`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    active: bool | float | str
    argument: FunctionParameters
    data_map: DataMap
    fillers: FunctionFillers
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: FunctionParameters
    purpose: str
    skip_fillers: bool | str
    wait_file: str
    wait_file_loops: float | str
    wait_for_fillers: bool | str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class Hangup(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hangup: (
        dict[str, Any]
        | list[
            Literal["hangup", "cancel", "busy", "noAnswer", "decline", "error"]
            | SWMLVar
        ]
        | float
    )


class HangupAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


HangupReason: TypeAlias = (
    "Literal['hangup', 'cancel', 'busy', 'noAnswer', 'decline', 'error']"
)


class Hint(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    pattern: str
    hint: str
    ignore_case: bool | str
    replace: str


class HoldAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


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

    join_conference: JoinConferenceObject | list[str | SWMLVar] | float | dict[str, Any]


class JoinConferenceObject(TypedDict, total=False):
    """Join an ad-hoc audio conference.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    beep: Literal["true", "false", "onEnter", "onExit"] | SWMLVar
    coach: str | SWMLVar
    emit_call_quality: bool | SWMLVar
    end_on_exit: bool | SWMLVar
    max_participants: int | SWMLVar
    meta: dict[str, Any] | SWMLVar
    min_participants: int | SWMLVar
    muted: bool | SWMLVar
    name: str | SWMLVar
    record: Literal["do-not-record", "record-from-start"] | SWMLVar
    recording_status_callback: str | SWMLVar
    recording_status_callback_event: str | SWMLVar
    recording_status_callback_event_type: Literal["cxml", "laml", "relay"] | SWMLVar
    recording_status_callback_method: Literal["GET", "POST"] | SWMLVar
    region: Literal["global", "us", "eu", "ch"] | SWMLVar
    start_on_enter: bool | SWMLVar
    status_callback: str | SWMLVar
    status_callback_event: str | SWMLVar
    status_callback_event_type: Literal["cxml", "laml", "relay"] | SWMLVar
    status_callback_method: Literal["GET", "POST"] | SWMLVar
    stream: CallDeviceStream | SWMLVar
    trim: Literal["trim-silence", "do-not-trim"] | SWMLVar
    video: bool | SWMLVar
    video_layout: str | SWMLVar
    video_preview: bool | SWMLVar
    video_quality: Literal["720p", "1080p"] | SWMLVar
    wait_url: str | SWMLVar


class JoinRoom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    join_room: dict[str, Any] | list[str | SWMLVar] | float


class Label(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    label: dict[str, Any] | list[str] | float


class LanguageParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    emotion: str
    pitch: float | str
    similarity: float | str
    speakingRate: float | str
    speed: float | str
    stability: float | str
    streaming: bool | str
    temperature: float | str
    vol: float | str


class Languages(TypedDict, total=False):
    """Without one of `code` / `listen_language`, `name` and `voice`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    auto_emotion: bool | str
    auto_speed: bool | str
    code: list[Any] | str
    double_turn_fillers: list[Any]
    engine: str
    fillers: list[Any]
    function_fillers: list[Any]
    listen_language: list[Any] | str
    model: str
    name: str
    params: LanguageParams
    pronounce: list[Any]
    speech_fillers: list[Any]
    turn_fillers: list[Any]
    voice: str


class LanguagesWithFillers(TypedDict, total=False):
    """Without one of `code` / `listen_language`, `name` and `voice`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    auto_emotion: bool | str
    auto_speed: bool | str
    code: list[Any] | str
    double_turn_fillers: list[Any]
    engine: str
    fillers: list[Any]
    function_fillers: list[Any]
    listen_language: list[Any] | str
    model: str
    name: str
    params: LanguageParams
    pronounce: list[Any]
    speech_fillers: list[Any]
    turn_fillers: list[Any]
    voice: str


class LanguagesWithSoloFillers(TypedDict, total=False):
    """Without one of `code` / `listen_language`, `name` and `voice`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    auto_emotion: bool | str
    auto_speed: bool | str
    code: list[Any] | str
    double_turn_fillers: list[Any]
    engine: str
    fillers: list[Any]
    function_fillers: list[Any]
    listen_language: list[Any] | str
    model: str
    name: str
    params: LanguageParams
    pronounce: list[Any]
    speech_fillers: list[Any]
    turn_fillers: list[Any]
    voice: str


class LiveTranscribe(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_transcribe: dict[str, Any] | list[Any] | float | str


class LiveTranscribeStartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    start: dict[str, Any]


LiveTranscribeStopAction: TypeAlias = "Literal['stop']"


class LiveTranscribeSummarizeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    summarize: dict[str, Any]


class LiveTranslate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_translate: dict[str, Any] | list[Any] | float | str


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

    action: Action | list[Action]
    post_process: bool
    response: str | dict[str, Any]


class POM(TypedDict, total=False):
    """Without one of `body` / `bullets` / `subsections`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    title: str
    body: str
    bullets: list[Any]
    numbered: bool
    numberedBullets: bool
    subsections: list[Any]


class Pay(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    pay: dict[str, Any] | list[Any | Literal["dtmf", "voice"] | SWMLVar] | float | str


class PayParameters(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str | SWMLVar
    value: str | SWMLVar


class PayPromptAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["Say", "Play"] | SWMLVar
    phrase: str | SWMLVar


class PayPromptPlayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["Say", "Play"] | SWMLVar
    phrase: str | SWMLVar


class PayPromptSayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["Say", "Play"] | SWMLVar
    phrase: str | SWMLVar


PayPrompts = TypedDict(
    "PayPrompts",
    {
        "actions": "list[PayPromptAction | SWMLVar] | SWMLVar",
        "attempt": "str | SWMLVar",
        "card_type": "str | SWMLVar",
        "error_type": "str | SWMLVar",
        "for": "Literal['payment-card-number', 'expiration-date', 'security-code', 'postal-code', 'bank-routing-number', 'bank-account-number', 'payment-processing', 'payment-completed', 'payment-failed', 'payment-canceled'] | SWMLVar",
        "play": "list[RingbackConfig | SWMLVar] | SWMLVar",
        "require_matching_inputs": "str | SWMLVar",
    },
    total=False,
)
PayPrompts.__doc__ = (
    """Open shape: extra server keys permitted; not validated at runtime."""
)


class Play(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    play: PlayWithURL | list[str] | float | dict[str, Any]


class PlayWithURL(TypedDict, total=False):
    """Play file(s), ringtones, speech or silence.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    auto_answer: bool | str | SWMLVar
    loop: int | SWMLVar
    say_gender: Literal["male", "female"] | SWMLVar
    say_language: str | SWMLVar
    say_voice: str | SWMLVar
    status_url: str | SWMLVar
    url: play_url
    urls: list[str]
    volume: float | SWMLVar


class PlayWithURLS(TypedDict, total=False):
    """Play file(s), ringtones, speech or silence.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    auto_answer: bool | str | SWMLVar
    loop: int | SWMLVar
    say_gender: Literal["male", "female"] | SWMLVar
    say_language: str | SWMLVar
    say_voice: str | SWMLVar
    status_url: str | SWMLVar
    url: play_url
    urls: list[str]
    volume: float | SWMLVar


class PlaybackBGAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class PomSectionBodyContent(TypedDict, total=False):
    """Without one of `body` / `bullets` / `subsections`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    title: str
    body: str
    bullets: list[Any]
    numbered: bool
    numberedBullets: bool
    subsections: list[Any]


class PomSectionBulletsContent(TypedDict, total=False):
    """Without one of `body` / `bullets` / `subsections`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    title: str
    body: str
    bullets: list[Any]
    numbered: bool
    numberedBullets: bool
    subsections: list[Any]


class Prompt(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    prompt: dict[str, Any] | list[str | int | SWMLVar | float] | float


Pronounce = TypedDict(
    "Pronounce",
    {
        "ignore_case": "bool | float | str",
        "replace": "str",
        "with": "str",
    },
    total=False,
)
Pronounce.__doc__ = """Without `replace` and `with`, the element has no effect: it is accepted and ignored, not rejected.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""


class ReceiveFax(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    receive_fax: dict[str, Any] | list[str | SWMLVar] | float


class Record(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    record: dict[str, Any] | list[Any] | float | str


class RecordCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    record_call: dict[str, Any] | list[Any] | float | str


class Request(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    request: dict[str, Any] | list[Any] | float | str


Return = TypedDict(
    "Return",
    {
        "return": "dict[str, Any] | list[Any] | bool | None | float | str",
    },
    total=False,
)
Return.__doc__ = (
    """Open shape: extra server keys permitted; not validated at runtime."""
)


class SIPRefer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sip_refer: dict[str, Any] | list[str | SWMLVar] | float


class SMSWithBody(TypedDict, total=False):
    """Send an outbound SMS or MMS message to a PSTN phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    body: str | SWMLVar
    from_number: str | SWMLVar
    media: list[str]
    region: str | SWMLVar
    status_callback: str | SWMLVar
    tags: list[str]
    to_number: str | SWMLVar


class SMSWithMedia(TypedDict, total=False):
    """Send an outbound SMS or MMS message to a PSTN phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    body: str | SWMLVar
    from_number: str | SWMLVar
    media: list[str]
    region: str | SWMLVar
    status_callback: str | SWMLVar
    tags: list[str]
    to_number: str | SWMLVar


class SWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    defaults: SWAIGDefaults
    functions: list[SWAIGFunction]
    hooks: list[dict[str, Any]]
    includes: list[SWAIGIncludes]
    internal_fillers: SWAIGInternalFiller
    mcp_servers: list[dict[str, Any]]
    native_functions: list[SWAIGNativeFunction]


class SWAIGDefaults(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    meta_data: Any
    meta_data_token: str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class SWAIGFunction(TypedDict, total=False):
    """Without one of `data_map` / `web_hook_url`, one of `description` / `purpose` and `function`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    active: bool | float | str
    argument: FunctionParameters
    data_map: DataMap
    fillers: FunctionFillers
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: FunctionParameters
    purpose: str
    skip_fillers: bool | str
    wait_file: str
    wait_file_loops: float | str
    wait_for_fillers: bool | str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class SWAIGIncludes(TypedDict, total=False):
    """Without `functions` and `url`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    auth_password: str
    auth_user: str
    functions: list[Any]
    meta_data: dict[str, Any]
    url: str


class SWAIGInternalFiller(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    adjust_response_latency: dict[str, Any]
    change_context: dict[str, Any]
    check_time: dict[str, Any]
    get_ideal_strategy: dict[str, Any]
    get_visual_input: dict[str, Any]
    next_step: dict[str, Any]
    pause_conversation: dict[str, Any]
    wait_for_user: dict[str, Any]
    wait_seconds: dict[str, Any]


SWAIGNativeFunction: TypeAlias = "str"


class SWMLAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


SWMLMethod: TypeAlias = "AI | AiSidecar | AmazonBedrock | Answer | BindDigit | ClearDigitBindings | Cond | Connect | Denoise | DetectMachine | Echo | EnterQueue | Execute | ExecuteRpc | Goto | Hangup | JoinConference | JoinRoom | Label | LiveTranscribe | LiveTranslate | Pay | Play | Prompt | ReceiveFax | Record | RecordCall | Request | Return | Ring | SIPRefer | SendDigits | SendFax | SendSMS | Set | SetCapabilities | SetMeta | Sleep | StopDenoise | StopRecordCall | StopStream | StopTap | Stream | Switch | Tap | Transcribe | TranscribeStop | Transfer | Unset | UserEvent"


class SWMLObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sections: Section
    version: Literal["1.0.0"]


SWMLVar: TypeAlias = "str"


class SayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


SchemaType: TypeAlias = "StringProperty | IntegerProperty | NumberProperty | BooleanProperty | ArrayProperty | ObjectProperty | NullProperty | OneOfProperty | AllOfProperty | AnyOfProperty | ConstProperty"


class Section(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    main: list[SWMLMethod]


class SendDigits(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_digits: dict[str, Any] | list[str | SWMLVar] | float


class SendFax(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_fax: dict[str, Any] | list[str | SWMLVar] | float


class SendSMS(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_sms: SMSWithBody


class Set(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set: dict[str, Any]


class SetGlobalDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class SetMetaDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class Sleep(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sleep: dict[str, Any] | list[int | SWMLVar]


SpeechEngine: TypeAlias = "Literal['deepgram', 'google']"


class StartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    start: dict[str, Any]


class StartUpHookSWAIGFunction(TypedDict, total=False):
    """Without one of `data_map` / `web_hook_url`, one of `description` / `purpose` and `function`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    active: bool | float | str
    argument: FunctionParameters
    data_map: DataMap
    fillers: FunctionFillers
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: FunctionParameters
    purpose: str
    skip_fillers: bool | str
    wait_file: str
    wait_file_loops: float | str
    wait_for_fillers: bool | str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class StopAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class StopDenoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_denoise: dict[str, Any] | list[Any] | float | str


class StopPlaybackBGAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class StopRecordCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_record_call: dict[str, Any] | list[str | SWMLVar] | float


class StopTap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_tap: dict[str, Any] | list[Any | SWMLVar] | float


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
    """Without one of `data_map` / `web_hook_url`, one of `description` / `purpose` and `function`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    active: bool | float | str
    argument: FunctionParameters
    data_map: DataMap
    fillers: FunctionFillers
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: FunctionParameters
    purpose: str
    skip_fillers: bool | str
    wait_file: str
    wait_file_loops: float | str
    wait_for_fillers: bool | str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class Switch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    switch: dict[str, Any] | list[Any] | float | str


class Tap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    tap: (
        dict[str, Any]
        | list[str | SWMLVar | Literal["listen", "speak", "both"]]
        | float
    )


class ToggleFunctionsAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


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

    transfer: dict[str, Any] | list[str | SWMLVar] | float


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

    unset: list[str] | str


class UnsetGlobalDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class UnsetMetaDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class UserEvent(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    user_event: dict[str, Any] | list[Any] | float | str


class UserInputAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | dict[str, Any]
    clear_dynamic_hints: bool | str
    context_switch: str | dict[str, Any]
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | dict[str, Any]
    playback_bg: str | dict[str, Any]
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | dict[str, Any]
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class UserSWAIGFunction(TypedDict, total=False):
    """Without one of `data_map` / `web_hook_url`, one of `description` / `purpose` and `function`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    active: bool | float | str
    argument: FunctionParameters
    data_map: DataMap
    fillers: FunctionFillers
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: FunctionParameters
    purpose: str
    skip_fillers: bool | str
    wait_file: str
    wait_file_loops: float | str
    wait_for_fillers: bool | str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


ValidConfirmMethods: TypeAlias = "Cond | Set | Unset | Hangup | Play | Prompt | Record | RecordCall | StopRecordCall | Tap | StopTap | SendDigits | SendSMS | Denoise | StopDenoise"


class Webhook(TypedDict, total=False):
    """Without one of `expressions` / `output` and `url`, a Webhook has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error_keys: list[Any] | str
    expressions: list[Expression] | Expression
    foreach: Foreach
    form_param: str
    headers: dict[str, Any]
    input_args_as_params: bool
    method: str
    output: Output
    params: list[Any] | bool | None | float | dict[str, Any] | str
    require_args: list[Any] | str
    url: str


play_url: TypeAlias = "str"

uuid: TypeAlias = "str"


class TranscribeStop(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    transcribe_stop: dict[str, Any] | list[Any] | float | str


class Transcribe(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    transcribe: dict[str, Any] | list[Any] | float | str


class Stream(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stream: dict[str, Any] | list[str | SWMLVar] | float


class StopStream(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_stream: dict[str, Any] | list[Any | SWMLVar] | float


class Step(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    end: bool | str
    functions: list[Any]
    gather_info: dict[str, Any]
    history: str
    name: str
    pom: list[PromptPomSection]
    reset: dict[str, Any]
    skip_to_next_step: bool | str
    skip_user_turn: bool | str
    step_criteria: str
    text: str
    valid_contexts: list[str]
    valid_steps: list[str]


class SetMeta(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set_meta: dict[str, Any] | list[Any] | float | str


class SetCapabilities(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set_capabilities: dict[str, Any] | list[Any] | float | str


class RingbackConfig(TypedDict, total=False):
    """Declared as a named $defs entry so every generator emits a TYPED shape via $ref rather than collapsing an inline object to an untyped map.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    url: str
    urls: list[str]
    volume: float | SWMLVar


class Ring(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ring: dict[str, Any] | list[Any] | float | str


class PromptPomSection(TypedDict, total=False):
    """Without one of `body` / `bullets` / `subsections`, the object has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    title: str
    body: str
    bullets: list[str]
    numbered: bool
    numberedBullets: bool
    subsections: list[PromptPomSection]


JsonSchema = TypedDict(
    "JsonSchema",
    {
        "title": "str",
        "description": "str",
        "type": "Literal['array', 'boolean', 'integer', 'null', 'number', 'object', 'string'] | list[Literal['array', 'boolean', 'integer', 'null', 'number', 'object', 'string']]",
        "const": "Any",
        "enum": "list[Any]",
        "format": "str",
        "pattern": "str",
        "minimum": "float",
        "maximum": "float",
        "exclusiveMinimum": "float",
        "exclusiveMaximum": "float",
        "minLength": "int",
        "maxLength": "int",
        "minItems": "int",
        "maxItems": "int",
        "minProperties": "int",
        "maxProperties": "int",
        "default": "Any",
        "examples": "list[Any]",
        "deprecated": "bool",
        "properties": "dict[str, JsonSchema | bool]",
        "required": "list[str]",
        "prefixItems": "list[JsonSchema | bool]",
        "items": "JsonSchema | bool",
        "propertyNames": "JsonSchema | bool",
        "additionalProperties": "JsonSchema | bool",
        "unevaluatedProperties": "JsonSchema | bool",
        "oneOf": "list[JsonSchema | bool]",
        "anyOf": "list[JsonSchema | bool]",
        "allOf": "list[JsonSchema | bool]",
        "not": "JsonSchema | bool",
        "contains": "JsonSchema | bool",
        "dependentRequired": "dict[str, list[str]]",
        "dependentSchemas": "dict[str, JsonSchema | bool]",
        "else": "JsonSchema | bool",
        "if": "JsonSchema | bool",
        "maxContains": "int",
        "minContains": "int",
        "multipleOf": "float",
        "patternProperties": "dict[str, JsonSchema | bool]",
        "readOnly": "bool",
        "then": "JsonSchema | bool",
        "unevaluatedItems": "JsonSchema | bool",
        "uniqueItems": "bool",
        "writeOnly": "bool",
    },
    total=False,
)
JsonSchema.__doc__ = """A JSON Schema (draft 2020-12). The value is forwarded verbatim to the receiving model API, which owns this contract; the engine does not inspect it.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""


class Foreach(TypedDict, total=False):
    """Without `append`, `input_key` and `output_key`, a Foreach has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    append: str
    input_key: str
    max: float | str
    output_key: str


class ExecuteRpc(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    execute_rpc: dict[str, Any] | list[Any] | float | str


class Echo(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    echo: dict[str, Any] | list[int | SWMLVar]


class Context(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    consolidate: bool | str
    enter_fillers: dict[str, Any]
    exit_fillers: dict[str, Any]
    full_reset: bool | str
    history: str
    initial_step: str
    isolated: bool | str
    pom: list[PromptPomSection]
    post_prompt: dict[str, Any]
    prompt: str
    reset: list[Any] | bool | None | float | dict[str, Any] | str
    steps: list[Step]
    system_prompt: str
    user_prompt: str
    valid_contexts: list[Any]
    valid_steps: list[Any]


ConnectSerialParallel: TypeAlias = "list[ConnectDevice]"

ConnectDevice = TypedDict(
    "ConnectDevice",
    {
        "authorization_bearer_token": "str | SWMLVar",
        "call_state_events": "list[str] | SWMLVar",
        "call_state_url": "str | SWMLVar",
        "codec": "str | SWMLVar",
        "codecs": "str | list[Any]",
        "confirm": "str | list[SWMLMethod] | dict[str, Any] | SWMLVar",
        "confirm_timeout": "int | SWMLVar",
        "custom_parameters": "dict[str, str] | SWMLVar",
        "encryption": "Literal['mandatory', 'optional', 'forbidden'] | SWMLVar",
        "from": "str | SWMLVar",
        "from_name": "str | SWMLVar",
        "headers": "list[ConnectHeaders]",
        "name": "str | SWMLVar",
        "password": "str | SWMLVar",
        "realtime": "bool | SWMLVar",
        "session_timeout": "int | SWMLVar",
        "status_url": "str | SWMLVar",
        "status_url_method": "Literal['GET', 'POST'] | SWMLVar",
        "timeout": "int | SWMLVar",
        "to": "str | SWMLVar",
        "username": "str | SWMLVar",
        "webrtc_media": "bool | SWMLVar",
    },
    total=False,
)
ConnectDevice.__doc__ = """Body shape enforced by CHECK_swml_connect_device, swml_schema.c.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""


class ClearDigitBindings(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    clear_digit_bindings: dict[str, Any]


class CallDeviceStream(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    authorization_bearer_token: str | SWMLVar
    codec: str | SWMLVar
    custom_parameters: Any
    name: str | SWMLVar
    realtime: bool | SWMLVar
    status_url: str | SWMLVar
    status_url_method: Literal["GET", "POST"] | SWMLVar
    url: str | SWMLVar


class BindDigit(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    bind_digit: dict[str, Any]


class AiSidecar(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai_sidecar: dict[str, Any] | list[Any] | float | str


class RelayIsReset(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    full_reset: Any
    system_prompt: Any
    user_prompt: Any


class RelayCallPlayAudio(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    url: str


class RelayCallPlayTts(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    gender: Literal["male", "female"]
    language: str
    text: str
    voice: str


class RelayCallPlaySilence(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    duration: float


class RelayCallPlayRingtone(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    duration: float
    name: Literal[
        "au",
        "be",
        "ca",
        "cn",
        "cy",
        "cz",
        "de",
        "dk",
        "dz",
        "eg",
        "es",
        "fi",
        "fr",
        "hu",
        "il",
        "in",
        "jp",
        "ko",
        "pk",
        "pl",
        "ro",
        "rs",
        "ru",
        "sa",
        "tr",
        "uk",
        "us",
        "at",
        "bg",
        "br",
        "ch",
        "cl",
        "ee",
        "gr",
        "it",
        "lt",
        "mx",
        "my",
        "nl",
        "no",
        "nz",
        "ph",
        "pt",
        "se",
        "sg",
        "th",
        "za",
        "tw",
        "ve",
        "bong",
    ]


class RelayCallRecordInner(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    audio: RelayCallRecordAudio


class RelayCallRecordAudio(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    beep: bool
    direction: Literal["listen", "speak", "both"]
    end_silence_timeout: float
    format: Literal["mp3", "wav", "mp4"]
    initial_timeout: float
    input_sensitivity: float
    max_length: int
    stereo: bool
    terminators: str


class RelayCallCollectDigitsInner(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    digit_timeout: float
    max: int
    terminators: str


class RelayCallCollectSpeechInner(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    end_silence_timeout: float
    engine: Literal["Google", "Google.V2", "Deepgram"]
    hints: list[str]
    language: str
    model: str
    speech_timeout: float


class RelayCallDetectFax(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    tone: Literal["CNG", "CED", "cng", "ced"]


class RelayCallDetectMachine(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    detect_interruptions: bool
    detect_message_end: bool
    end_silence_timeout: float
    initial_timeout: float
    machine_ready_timeout: float
    machine_voice_threshold: float
    machine_words_threshold: int


class RelayCallDetectDigit(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    digits: str


class RelayCallTapDeviceRtp(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    addr: str
    codec: Literal["PCMA", "PCMU", "pcma", "pcmu", "OPUS", "opus"]
    port: int
    ptime: int


class RelayCallTapDeviceWs(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    codec: Literal["PCMA", "PCMU", "pcma", "pcmu", "OPUS", "opus"]
    uri: str


class RelayTap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    params: RelayAudioTapParams
    type: Literal["audio"]


class RelayAudioTapParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    direction: Literal["listen", "speak", "both"]


class RelayCallReferDevice(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    params: RelayCallReferDeviceSip
    type: Literal["sip"]


RelayCallReferDeviceSip = TypedDict(
    "RelayCallReferDeviceSip",
    {
        "from": "str",
        "password": "str",
        "to": "str",
        "username": "str",
    },
    total=False,
)
RelayCallReferDeviceSip.__doc__ = (
    """Open shape: extra server keys permitted; not validated at runtime."""
)

CallCommandsRequest: TypeAlias = "CallRequest"
CallCommandsResponse: TypeAlias = "CallResponse"


# Aliases of one concrete ``dict`` type, emitted unquoted and last so the name stays
# callable at runtime (``ConnectDeviceSingle(to=...)`` builds a dict, as it did when the
# name was a TypedDict).
ConnectDeviceParallel: TypeAlias = dict[str, Any]
ConnectDeviceSerial: TypeAlias = dict[str, Any]
ConnectDeviceSerialParallel: TypeAlias = dict[str, Any]
ConnectDeviceSingle: TypeAlias = dict[str, Any]
Contexts: TypeAlias = dict[str, Context]
RelayCallPlayInner: TypeAlias = dict[str, Any]
RelayCallDetectInner: TypeAlias = dict[str, Any]
RelayCallTapDevice: TypeAlias = dict[str, Any]
