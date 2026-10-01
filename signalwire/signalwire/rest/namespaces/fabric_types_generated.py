# AUTO-GENERATED from porting-sdk/rest-apis/fabric/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


class AIAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class AIAgent(TypedDict, total=False):
    """An AI Agent configuration that extends the SWML AI object with additional API-specific properties.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    global_data: dict[str, Any]
    hints: list[str]
    languages: list[AIAgentLanguage]
    params: AIParams
    post_prompt: AIAgentPostPrompt
    post_prompt_url: str
    pronounce: list[AIAgentPronounce]
    prompt: AIAgentPrompt
    SWAIG: AIAgentSWAIG
    agent_id: uuid
    name: str
    multilingual: dict[str, Any]


class AIAgentLanguage(TypedDict, total=False):
    """Without one of `code` / `listen_language`, `name` and `voice`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    auto_emotion: bool | str
    auto_speed: bool | str
    code: list[Any] | str
    double_turn_fillers: list[Any]
    engine: str
    fillers: list[str] | str
    function_fillers: list[Any]
    listen_language: list[Any] | str
    model: str
    name: str
    params: LanguageParams
    pronounce: list[Any]
    speech_fillers: list[Any]
    turn_fillers: list[Any]
    voice: str
    id: str
    provider: str


class AIAgentSWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    defaults: SWAIGDefaults
    functions: list[AIAgentSWAIGFunction]
    hooks: list[dict[str, Any]]
    includes: list[AIAgentSWAIGInclude]
    internal_fillers: SWAIGInternalFiller
    mcp_servers: list[dict[str, Any]]
    native_functions: list[SWAIGNativeFunction]


class AIAgentSWAIGInclude(TypedDict, total=False):
    """Without `functions` and `url`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    functions: list[str]
    url: str


class AIAgentAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressApp]
    links: AIAddressPaginationResponse


class AIAgentVoice(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: str
    provider: str
    language: str
    language_code: str
    voice: str
    premium: int


class AIAgentConversationLogListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    links: AIAddressPaginationResponse
    data: list[AIAgentConversationLog]


class AIAgentConversationLog(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: str
    caller_id_number: str | None
    duration_in_seconds: int
    messages: list[dict[str, Any]] | None
    redacted_at: str | None


class AIAgentCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    global_data: dict[str, Any]
    hints: list[str]
    languages: list[AIAgentLanguage]
    params: AIParams
    post_prompt: AIAgentPostPrompt
    post_prompt_url: str
    pronounce: list[AIAgentPronounce]
    prompt: AIAgentPrompt
    SWAIG: AIAgentSWAIG
    name: str
    post_prompt_auth_user: str
    post_prompt_auth_password: str
    multilingual: dict[str, Any]


class AIAgentCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class AIAgentListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[AIAgentResponse]
    links: AIAgentPaginationResponse


class AIAgentPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class AIAgentResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    type: Literal["ai_agent"]
    created_at: str
    updated_at: str
    ai_agent: AIAgent


class AIAgentUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    global_data: dict[str, Any]
    hints: list[str]
    languages: list[AIAgentLanguage]
    params: AIParams
    post_prompt: AIAgentPostPrompt
    post_prompt_url: str
    pronounce: list[AIAgentPronounce]
    prompt: AIAgentPrompt
    SWAIG: AIAgentSWAIG
    name: str
    post_prompt_auth_user: str
    post_prompt_auth_password: str
    multilingual: dict[str, Any]


class AIAgentUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


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


AddressChannel: TypeAlias = "AudioChannel | MessagingChannel | VideoChannel"

AttentionTimeout: TypeAlias = "int"


class AudioChannel(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    audio: str


class CXMLScript(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    contents: str
    request_count: int
    last_accessed_at: str | None
    request_url: str
    script_type: Literal["calling", "faxing", "messaging"]
    name: str
    status_callback_url: str | None
    status_callback_method: Literal["GET"] | Literal["POST"]


class CXMLScriptAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressApp]
    links: CXMLScriptAddressPaginationResponse


class CXMLScriptAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class CXMLScriptCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    contents: str
    status_callback_url: str
    status_callback_method: Literal["GET"] | Literal["POST"]
    name: str
    script_type: Literal["calling", "faxing", "messaging"]


class CXMLScriptCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class CXMLScriptListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[CXMLScriptResponse]
    links: CXMLScriptAddressPaginationResponse


class CXMLScriptResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    type: Literal["cxml_script"]
    created_at: str
    updated_at: str
    cxml_script: CXMLScript


class CXMLScriptUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    contents: str
    status_callback_url: str
    status_callback_method: Literal["GET"] | Literal["POST"]
    name: str
    script_type: Literal["calling", "faxing", "messaging"]


class CXMLScriptUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class CXMLWebhook(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    used_for: CxmlWebhookUsedForType
    primary_request_url: str
    primary_request_method: Literal["GET"] | Literal["POST"]
    fallback_request_url: str | None
    fallback_request_method: Literal["GET"] | Literal["POST"]
    status_callback_url: str | None
    status_callback_method: Literal["GET"] | Literal["POST"]


class CXMLWebhookAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressApp]
    links: CXMLWebhookAddressPaginationResponse


class CXMLWebhookAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class CXMLWebhookCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    used_for: CxmlWebhookUsedForType
    primary_request_url: str
    primary_request_method: Literal["GET"] | Literal["POST"]
    fallback_request_url: str
    fallback_request_method: Literal["GET"] | Literal["POST"]
    status_callback_url: str
    status_callback_method: Literal["GET"] | Literal["POST"]


class CXMLWebhookCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class CXMLWebhookListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[CXMLWebhookResponse]
    links: CXMLWebhookPaginationResponse


class CXMLWebhookPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class CXMLWebhookResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    type: Literal["cxml_webhook"]
    created_at: str
    updated_at: str
    cxml_webhook: CXMLWebhook


class CXMLWebhookUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    used_for: CxmlWebhookUsedForType
    primary_request_url: str
    primary_request_method: Literal["GET"] | Literal["POST"]
    fallback_request_url: str
    fallback_request_method: Literal["GET"] | Literal["POST"]
    status_callback_url: str
    status_callback_method: Literal["GET"] | Literal["POST"]


class CXMLWebhookUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class CallFlow(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    title: str
    flow_data: dict[str, Any]
    relayml: dict[str, Any]
    document_version: int


class CallFlowAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressApp]
    links: CallFlowAddressPaginationResponse


class CallFlowAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class CallFlowCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    title: str
    flow_data: dict[str, Any] | str
    relayml: dict[str, Any] | str


class CallFlowCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class CallFlowListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    links: CallFlowAddressPaginationResponse
    data: list[CallFlowResponse]


class CallFlowResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    type: Literal["call_flow"]
    created_at: str
    updated_at: str
    call_flow: CallFlow


class CallFlowUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    title: str
    document_version: int
    flow_data: dict[str, Any] | str
    relayml: dict[str, Any] | str


class CallFlowUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class CallFlowVersion(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    document_version: int
    created_at: str
    updated_at: str
    flow_data: dict[str, Any]
    relayml: dict[str, Any]


class CallFlowVersionDeployByDocumentVersion(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    document_version: int


class CallFlowVersionDeployByVersionId(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    call_flow_version_id: uuid


CallFlowVersionDeployRequest: TypeAlias = (
    "CallFlowVersionDeployByDocumentVersion | CallFlowVersionDeployByVersionId"
)


class CallFlowVersionDeployResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    created_at: str
    updated_at: str
    document_version: int
    flow_data: dict[str, Any]
    relayml: dict[str, Any]


class CallFlowVersionListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[CallFlowVersion]
    links: CallFlowVersionsPaginationResponse


class CallFlowVersionsPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


CallHandlerType: TypeAlias = (
    "Literal['default', 'passthrough', 'block-pstn', 'resource']"
)

Ciphers: TypeAlias = "Literal['AEAD_AES_256_GCM_8', 'AES_256_CM_HMAC_SHA1_80', 'AES_CM_128_HMAC_SHA1_80', 'AES_256_CM_HMAC_SHA1_32', 'AES_CM_128_HMAC_SHA1_32']"

Codecs: TypeAlias = "Literal['PCMU', 'PCMA', 'G722', 'G729', 'OPUS', 'VP8', 'H264']"


class ConferenceRoom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    description: str | None
    display_name: str
    max_members: int
    quality: Literal["1080p", "720p"]
    fps: Literal[30, 20]
    join_from: str | None
    join_until: str | None
    remove_at: str | None
    remove_after_seconds_elapsed: int | None
    layout: Layout
    record_on_start: bool
    tone_on_entry_and_exit: bool
    room_join_video_off: bool
    user_join_video_off: bool
    enable_room_previews: bool
    sync_audio_video: bool | None
    meta: dict[str, Any]
    prioritize_handraise: bool


class ConferenceRoomAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressRoom]
    links: ConferenceRoomAddressPaginationResponse


class ConferenceRoomAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class ConferenceRoomCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    display_name: str
    description: str
    join_from: str
    join_until: str
    max_members: int
    quality: Literal["1080p", "720p"]
    remove_at: str
    remove_after_seconds_elapsed: int
    layout: Layout
    record_on_start: bool
    enable_room_previews: bool
    meta: dict[str, Any]
    sync_audio_video: bool
    tone_on_entry_and_exit: bool
    room_join_video_off: bool
    user_join_video_off: bool


class ConferenceRoomCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class ConferenceRoomListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    links: ConferenceRoomAddressPaginationResponse
    data: list[ConferenceRoomResponse]


class ConferenceRoomResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    type: Literal["video_room"]
    created_at: str
    updated_at: str
    conference_room: ConferenceRoom


class ConferenceRoomUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    display_name: str
    join_from: str
    join_until: str
    max_members: int
    quality: Literal["1080p", "720p"]
    remove_at: str
    remove_after_seconds_elapsed: int
    layout: Layout
    record_on_start: bool
    enable_room_previews: bool
    meta: dict[str, Any]
    sync_audio_video: bool


class ConferenceRoomUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class ConversationMessage(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    content: str
    lang: str
    role: ConversationRole
    tool_call_id: str
    tool_calls: list[Any]


ConversationRole: TypeAlias = "str"


class CxmlApplication(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    friendly_name: str
    voice_url: str | None
    voice_method: Literal["GET"] | Literal["POST"] | None
    voice_fallback_url: str | None
    voice_fallback_method: Literal["GET"] | Literal["POST"] | None
    status_callback: str | None
    status_callback_method: Literal["GET"] | Literal["POST"] | None
    sms_url: str | None
    sms_method: Literal["GET"] | Literal["POST"] | None
    sms_fallback_url: str | None
    sms_fallback_method: Literal["GET"] | Literal["POST"] | None
    sms_status_callback: str | None
    sms_status_callback_method: Literal["GET"] | Literal["POST"] | None
    message_status_callback: str | None
    api_version: str
    uri: str


class CxmlApplicationAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddress]
    links: CxmlApplicationAddressPaginationResponse


class CxmlApplicationAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class CxmlApplicationListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[CxmlApplicationResponse]
    links: CxmlApplicationPaginationResponse


class CxmlApplicationPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class CxmlApplicationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    type: Literal["cxml_application"]
    created_at: str
    updated_at: str
    cxml_application: CxmlApplication


class CxmlApplicationUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    call_request_url: str
    call_request_method: Literal["GET", "POST"]
    call_fallback_url: str
    call_fallback_method: Literal["GET", "POST"]
    call_status_url: str
    call_status_method: Literal["GET", "POST"]
    message_request_url: str
    message_request_method: Literal["GET", "POST"]
    message_fallback_url: str
    message_fallback_method: Literal["GET", "POST"]
    message_status_url: str
    message_status_method: Literal["GET", "POST"]


class CxmlApplicationUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class DataMap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    contexts: list[Any] | bool | None | float | dict[str, Any] | str
    expressions: list[Expression] | Expression
    output: Output
    webhooks: list[Webhook] | Webhook


class DialogFlowPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class DialogflowAgent(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    say_enabled: bool
    say: str | None
    voice: str
    display_name: str
    dialogflow_reference_id: uuid
    dialogflow_reference_name: str


class DialogflowAgentAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressApp]
    links: DialogflowAgentAddressPaginationResponse


class DialogflowAgentAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class DialogflowAgentListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[DialogflowAgentResponse]
    links: DialogFlowPaginationResponse


class DialogflowAgentResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    type: Literal["dialogflow_agent"]
    created_at: str
    updated_at: str
    dialogflow_agent: DialogflowAgent


class DialogflowAgentUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    say_enabled: bool
    say: str
    voice: Literal[
        "ar-XA-Standard-A",
        "ar-XA-Standard-B",
        "ar-XA-Standard-C",
        "ar-XA-Wavenet-A",
        "ar-XA-Wavenet-B",
        "ar-XA-Wavenet-C",
        "cs-CZ-Standard-A",
        "cs-CZ-Wavenet-A",
        "da-DK-Standard-A",
        "da-DK-Wavenet-A",
        "nl-NL-Standard-A",
        "nl-NL-Standard-B",
        "nl-NL-Standard-C",
        "nl-NL-Standard-D",
        "nl-NL-Standard-E",
        "nl-NL-Wavenet-A",
        "nl-NL-Wavenet-B",
        "nl-NL-Wavenet-C",
        "nl-NL-Wavenet-D",
        "nl-NL-Wavenet-E",
        "en-AU-Standard-A",
        "en-AU-Standard-B",
        "en-AU-Standard-C",
        "en-AU-Standard-D",
        "en-AU-Wavenet-A",
        "en-AU-Wavenet-B",
        "en-AU-Wavenet-C",
        "en-AU-Wavenet-D",
        "en-IN-Standard-A",
        "en-IN-Standard-B",
        "en-IN-Standard-C",
        "en-IN-Wavenet-A",
        "en-IN-Wavenet-B",
        "en-IN-Wavenet-C",
        "en-GB-Standard-A",
        "en-GB-Standard-B",
        "en-GB-Standard-C",
        "en-GB-Standard-D",
        "en-GB-Wavenet-A",
        "en-GB-Wavenet-B",
        "en-GB-Wavenet-C",
        "en-GB-Wavenet-D",
        "en-US-Standard-B",
        "en-US-Standard-C",
        "en-US-Standard-D",
        "en-US-Standard-E",
        "en-US-Standard-F",
        "en-US-Standard-G",
        "en-US-Standard-H",
        "en-US-Standard-I",
        "en-US-Standard-J",
        "en-US-Wavenet-A",
        "en-US-Wavenet-B",
        "en-US-Wavenet-C",
        "en-US-Wavenet-D",
        "en-US-Wavenet-E",
        "en-US-Wavenet-F",
        "fil-PH-Standard-A",
        "fil-PH-Wavenet-A",
        "fi-FI-Standard-A",
        "fi-FI-Wavenet-A",
        "fr-CA-Standard-A",
        "fr-CA-Standard-B",
        "fr-CA-Standard-C",
        "fr-CA-Standard-D",
        "fr-CA-Wavenet-A",
        "fr-CA-Wavenet-B",
        "fr-CA-Wavenet-C",
        "fr-CA-Wavenet-D",
        "fr-FR-Standard-A",
        "fr-FR-Standard-B",
        "fr-FR-Standard-C",
        "fr-FR-Standard-D",
        "fr-FR-Wavenet-A",
        "fr-FR-Wavenet-B",
        "fr-FR-Wavenet-C",
        "fr-FR-Wavenet-D",
        "de-DE-Standard-A",
        "de-DE-Standard-B",
        "de-DE-Wavenet-A",
        "de-DE-Wavenet-B",
        "de-DE-Wavenet-C",
        "de-DE-Wavenet-D",
        "el-GR-Standard-A",
        "el-GR-Wavenet-A",
        "hi-IN-Standard-A",
        "hi-IN-Standard-B",
        "hi-IN-Standard-C",
        "hi-IN-Wavenet-A",
        "hi-IN-Wavenet-B",
        "hi-IN-Wavenet-C",
        "hu-HU-Standard-A",
        "hu-HU-Wavenet-A",
        "id-ID-Standard-A",
        "id-ID-Standard-B",
        "id-ID-Standard-C",
        "id-ID-Wavenet-A",
        "id-ID-Wavenet-B",
        "id-ID-Wavenet-C",
        "it-IT-Standard-A",
        "it-IT-Standard-B",
        "it-IT-Standard-C",
        "it-IT-Standard-D",
        "it-IT-Wavenet-A",
        "it-IT-Wavenet-B",
        "it-IT-Wavenet-C",
        "it-IT-Wavenet-D",
        "ja-JP-Standard-A",
        "ja-JP-Standard-B",
        "ja-JP-Standard-C",
        "ja-JP-Standard-D",
        "ja-JP-Wavenet-A",
        "ja-JP-Wavenet-B",
        "ja-JP-Wavenet-C",
        "ja-JP-Wavenet-D",
        "ko-KR-Standard-A",
        "ko-KR-Standard-B",
        "ko-KR-Standard-C",
        "ko-KR-Standard-D",
        "ko-KR-Wavenet-A",
        "ko-KR-Wavenet-B",
        "ko-KR-Wavenet-C",
        "ko-KR-Wavenet-D",
        "cmn-CN-Standard-A",
        "cmn-CN-Standard-B",
        "cmn-CN-Standard-C",
        "cmn-CN-Wavenet-A",
        "cmn-CN-Wavenet-B",
        "cmn-CN-Wavenet-C",
        "nb-NO-Standard-A",
        "nb-NO-Standard-B",
        "nb-NO-Standard-C",
        "nb-NO-Standard-D",
        "nb-NO-Wavenet-A",
        "nb-NO-Wavenet-B",
        "nb-NO-Wavenet-C",
        "nb-NO-Wavenet-D",
        "nb-no-Standard-E",
        "nb-no-Wavenet-E",
        "pl-PL-Standard-A",
        "pl-PL-Standard-B",
        "pl-PL-Standard-C",
        "pl-PL-Standard-D",
        "pl-PL-Standard-E",
        "pl-PL-Wavenet-A",
        "pl-PL-Wavenet-B",
        "pl-PL-Wavenet-C",
        "pl-PL-Wavenet-D",
        "pl-PL-Wavenet-E",
        "pt-BR-Standard-A",
        "pt-BR-Wavenet-A",
        "pt-PT-Standard-A",
        "pt-PT-Standard-B",
        "pt-PT-Standard-C",
        "pt-PT-Standard-D",
        "pt-PT-Wavenet-A",
        "pt-PT-Wavenet-B",
        "pt-PT-Wavenet-C",
        "pt-PT-Wavenet-D",
        "ru-RU-Standard-A",
        "ru-RU-Standard-B",
        "ru-RU-Standard-C",
        "ru-RU-Standard-D",
        "ru-RU-Wavenet-A",
        "ru-RU-Wavenet-B",
        "ru-RU-Wavenet-C",
        "ru-RU-Wavenet-D",
        "sk-SK-Standard-A",
        "sk-SK-Wavenet-A",
        "es-ES-Standard-A",
        "sv-SE-Standard-A",
        "sv-SE-Wavenet-A",
        "tr-TR-Standard-A",
        "tr-TR-Standard-B",
        "tr-TR-Standard-C",
        "tr-TR-Standard-D",
        "tr-TR-Standard-E",
        "tr-TR-Wavenet-A",
        "tr-TR-Wavenet-B",
        "tr-TR-Wavenet-C",
        "tr-TR-Wavenet-D",
        "tr-TR-Wavenet-E",
        "uk-UA-Standard-A",
        "uk-UA-Wavenet-A",
        "vi-VN-Standard-A",
        "vi-VN-Standard-B",
        "vi-VN-Standard-C",
        "vi-VN-Standard-D",
        "vi-VN-Wavenet-A",
        "vi-VN-Wavenet-B",
        "vi-VN-Wavenet-C",
        "vi-VN-Wavenet-D",
    ]


class DialogflowAgentUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


Direction: TypeAlias = "str"

DisplayTypes: TypeAlias = "Literal['app', 'room', 'call', 'subscriber']"


class DomainApplicationAssignRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    domain_application_id: uuid


class DomainApplicationCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class DomainApplicationResponse(TypedDict, total=False):
    """Response containing a single domain application.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str | None
    locked: bool
    channels: AudioChannel
    type: Literal["app", "call", "room"]
    resource_id: str


class EmbedTokenCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class EmbedsTokensRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    token: str


class EmbedsTokensResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    token: str


Encryption: TypeAlias = "Literal['required', 'optional', 'default']"

SipGatewayEncryption: TypeAlias = "Literal['required', 'optional', 'forbidden']"

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


class FabricAddress(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str | None
    locked: bool
    channels: AddressChannel
    type: DisplayTypes
    resource_id: str


class FabricAddressApp(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str | None
    locked: bool
    channels: AddressChannel
    type: DisplayTypes
    resource_id: str


class FabricAddressCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str | None
    locked: bool
    channels: AddressChannel
    type: DisplayTypes
    resource_id: str


class FabricAddressPaginationResponse(TypedDict, total=False):
    """Pagination links for the response.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    self: str
    first: str
    next: str
    prev: str


class FabricAddressRoom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str | None
    locked: bool
    channels: AddressChannel
    type: DisplayTypes
    resource_id: str


class FabricAddressSubscriber(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str | None
    locked: bool
    channels: AddressChannel
    type: DisplayTypes
    resource_id: str


FabricAddressItem: TypeAlias = "AliasAddress | SipAddress | PhoneNumberAddress"


class FabricAddressListResponse(TypedDict, total=False):
    """A page of Fabric Addresses.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    data: list[FabricAddressItem]
    links: FabricAddressPaginationResponse
    items_count: int


class FreeswitchConectorPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class FreeswitchConnector(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    caller_id: str | None
    send_as: str | None


class FreeswitchConnectorAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressCall]
    links: FreeswitchConnectorAddressPaginationResponse


class FreeswitchConnectorAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class FreeswitchConnectorCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    token: uuid


class FreeswitchConnectorCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class FreeswitchConnectorListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    links: FreeswitchConectorPaginationResponse
    data: list[FreeswitchConnectorResponse]


class FreeswitchConnectorResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    type: Literal["freeswitch_connector"]
    created_at: str
    updated_at: str
    freeswitch_connector: FreeswitchConnector


class FreeswitchConnectorUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    caller_id: str
    send_as: str


class FreeswitchConnectorUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


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


class GuestTokenCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


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


Layout: TypeAlias = "Literal['grid-responsive', 'grid-responsive-mobile', 'highlight-1-responsive', '1x1', '2x1', '2x2', '5up', '3x3', '4x4', '5x5', '6x6', '8x8', '10x10']"


class MessagingChannel(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    messaging: str


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


class PhoneRouteAssignRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    phone_route_id: uuid
    handler: UsedForType


class PhoneRouteCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class PhoneRouteResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str | None
    locked: bool
    channels: dict[str, Any]
    type: Literal["app", "call", "room"]
    resource_id: str


class RefreshTokenStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class RelayApplication(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    topic: str
    call_status_callback_url: str | None


class RelayApplicationAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressApp]
    links: RelayApplicationAddressPaginationResponse


class RelayApplicationAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class RelayApplicationCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    topic: str
    call_status_callback_url: str


class RelayApplicationCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class RelayApplicationListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[RelayApplicationResponse]
    links: RelayApplicationAddressPaginationResponse


class RelayApplicationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    type: Literal["relay_application"]
    created_at: str
    updated_at: str
    relay_application: RelayApplication


class RelayApplicationUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    topic: str
    call_status_callback_url: str


class RelayApplicationUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class ResourceAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddress]
    links: ResourceAddressPaginationResponse


class ResourceAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class ResourceListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[ResourceResponse]
    links: ResourcePaginationResponse


class ResourcePaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


ResourceResponse: TypeAlias = "ResourceResponseAI | ResourceResponseCallFlow | ResourceResponseCXMLWebhook | ResourceResponseCXMLScript | ResourceResponseCXMLApplication | ResourceResponseDialogFlowAgent | ResourceResponseFSConnector | ResourceResponseRelayApp | ResourceResponseSipEndpoint | ResourceResponseSipGateway | ResourceResponseSubscriber | ResourceResponseSWMLWebhook | ResourceResponseSWMLScript | ResourceResponseConferenceRoom"


class ResourceResponseAI(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["ai_agent"]
    ai_agent: AIAgent


class ResourceResponseCXMLApplication(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["cxml_application"]
    cxml_application: CxmlApplication


class ResourceResponseCXMLScript(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["cxml_script"]
    cxml_script: CXMLScript


class ResourceResponseCXMLWebhook(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["cxml_webhook"]
    cxml_webhook: CXMLWebhook


class ResourceResponseCallFlow(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["call_flow"]
    call_flow: CallFlow


class ResourceResponseConferenceRoom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["video_room"]
    conference_room: ConferenceRoom


class ResourceResponseDialogFlowAgent(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["dialogflow_agent"]
    dialogflow_agent: DialogflowAgent


class ResourceResponseFSConnector(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["freeswitch_connector"]
    freeswitch_connector: FreeswitchConnector


class ResourceResponseRelayApp(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["relay_application"]
    relay_application: RelayApplication


class ResourceResponseSWMLScript(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["swml_script"]
    swml_script: SwmlScript


class ResourceResponseSWMLWebhook(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["swml_webhook"]
    swml_webhook: SWMLWebhook


class ResourceResponseSipEndpoint(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["sip_endpoint"]
    sip_endpoint: SipEndpoint


class ResourceResponseSipGateway(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["sip_gateway"]
    sip_gateway: SipGateway


class ResourceResponseSubscriber(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str | None
    created_at: str
    updated_at: str
    type: Literal["subscriber"]
    subscriber: Subscriber


class ResourceSipEndpointAssignRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sip_endpoint_id: uuid


class ResourceSipEndpointCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class ResourceSipEndpointUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class ResourceSubSipEndpointCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SWAIGDefaults(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    meta_data: Any
    meta_data_token: str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


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


class SWMLScriptAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressApp]
    links: SWMLScriptAddressPaginationResponse


class SWMLScriptAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SWMLWebhook(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    used_for: Literal["calling", "messaging"]
    primary_request_url: str
    primary_request_method: Literal["GET"] | Literal["POST"]
    fallback_request_url: str | None
    fallback_request_method: Literal["GET"] | Literal["POST"]
    status_callback_url: str | None
    status_callback_method: Literal["GET"] | Literal["POST"]


class SWMLWebhookAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressApp]
    links: SWMLWebhookAddressPaginationResponse


class SWMLWebhookAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SWMLWebhookCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    used_for: Literal["calling", "messaging"]
    primary_request_url: str
    primary_request_method: Literal["GET"] | Literal["POST"]
    fallback_request_url: str
    fallback_request_method: Literal["GET"] | Literal["POST"]
    status_callback_url: str
    status_callback_method: Literal["GET"] | Literal["POST"]


class SWMLWebhookListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[SWMLWebhookResponse]
    links: SWMLWebhookPaginationResponse


class SWMLWebhookPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SWMLWebhookResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    type: Literal["swml_webhook"]
    created_at: str
    updated_at: str
    swml_webhook: SWMLWebhook


class SWMLWebhookUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    used_for: Literal["calling", "messaging"]
    primary_request_url: str
    primary_request_method: Literal["GET"] | Literal["POST"]
    fallback_request_url: str
    fallback_request_method: Literal["GET"] | Literal["POST"]
    status_callback_url: str
    status_callback_method: Literal["GET"] | Literal["POST"]


class SipEndpoint(TypedDict, total=False):
    """SIP endpoint model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    username: str
    caller_id: str | None
    send_as: str
    ciphers: list[Ciphers]
    codecs: list[Codecs]
    encryption: Literal["required", "optional"]
    call_handler: Literal[
        "default",
        "passthrough",
        "block-pstn",
        "laml_webhook",
        "laml_application",
        "dialogflow",
        "relay_context",
        "relay_application",
        "relay_connector",
        "video_room",
        "ai_agent",
        "relay_script",
        "call_flow",
        None,
    ]
    calling_handler_resource_id: uuid | None


class SipEndpointAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressCall]
    links: SipEndpointAddressPaginationResponse


class SipEndpointAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SipEndpointCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    username: str
    caller_id: str
    send_as: str
    ciphers: list[Ciphers]
    codecs: list[Codecs]
    encryption: Encryption
    call_handler: CallHandlerType
    calling_handler_resource_id: uuid | None
    password: str


class SipEndpointCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SipEndpointListResponse(TypedDict, total=False):
    """Response containing a list of SIP endpoints.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    data: list[SipEndpointResponse]
    links: SipEndpointPaginationResponse


class SipEndpointPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SipEndpointResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    type: Literal["sip_endpoint"]
    created_at: str
    updated_at: str
    sip_endpoint: SipEndpoint


class SipEndpointUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    username: str
    caller_id: str
    send_as: str
    ciphers: list[Ciphers]
    codecs: list[Codecs]
    encryption: Encryption
    call_handler: CallHandlerType
    calling_handler_resource_id: uuid | None
    password: str


class SipEndpointUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SipGateway(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: str
    uri: str
    name: str
    ciphers: list[Ciphers]
    codecs: list[Codecs]
    encryption: SipGatewayEncryption


class SipGatewayAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressCall]
    links: SipGatewayAddressPaginationResponse


class SipGatewayAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SipGatewayCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SipGatewayListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[SipGatewayResponse]
    links: SipGatewayPaginationResponse


class SipGatewayPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SipGatewayRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    uri: str
    encryption: SipGatewayEncryption
    ciphers: list[Ciphers]
    codecs: list[Codecs]


class SipGatewayRequestUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    uri: str
    encryption: SipGatewayEncryption
    ciphers: list[Ciphers]
    codecs: list[Codecs]


class SipGatewayResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: str
    project_id: str
    display_name: str
    type: Literal["sip_gateway"]
    created_at: str
    updated_at: str
    sip_gateway: SipGateway


class Subscriber(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    email: str
    first_name: str
    last_name: str
    display_name: str
    job_title: str
    country: str
    company_name: str
    time_zone: str


class SubscriberAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SubscriberAddressesResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressSubscriber]
    links: SubscriberAddressPaginationResponse


class SubscriberCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SubscriberGuestTokenCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    allowed_addresses: list[uuid]
    expire_at: int
    ch: str
    region: str
    email: str
    first_name: str
    last_name: str
    display_name: str
    job_title: str
    time_zone: str
    country: str
    company_name: str


class SubscriberGuestTokenCreateResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    token: jwt
    refresh_token: jwt
    address_uri: str
    expires_at: str
    expires_in: int
    issued_at: str


class SubscriberListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[SubscriberResponse]
    links: SubscriberPaginationResponse


class SubscriberPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SubscriberRefreshTokenRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    refresh_token: jwt


class SubscriberRefreshTokenResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    token: jwt
    refresh_token: jwt


class SubscriberRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    password: str
    email: str
    first_name: str
    last_name: str
    display_name: str
    job_title: str
    country: str
    company_name: str
    time_zone: str


class SubscriberUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    password: str
    email: str
    first_name: str
    last_name: str
    display_name: str
    job_title: str
    country: str
    company_name: str
    time_zone: str


class SubscriberResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: str
    project_id: str
    display_name: str
    type: Literal["subscriber"]
    created_at: str
    updated_at: str
    subscriber: Subscriber


class SubscriberSIPEndpoint(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    username: str
    caller_id: str | None
    send_as: str
    ciphers: list[Ciphers]
    codecs: list[Codecs]
    encryption: Literal["required", "optional", None]


class SubscriberSipEndpointListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[SubscriberSIPEndpoint]
    links: SubscriberSipEndpointPaginationResponse


class SubscriberSipEndpointPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SubscriberSipEndpointRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    username: str
    password: str
    caller_id: str
    send_as: str
    ciphers: list[Ciphers]
    codecs: list[Codecs]
    encryption: Encryption


class SubscriberSipEndpointRequestUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    username: str
    password: str
    caller_id: str
    send_as: str
    ciphers: list[Ciphers]
    codecs: list[Codecs]
    encryption: Encryption


class SubscriberTokenRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ch: str
    reference: str
    expire_at: int
    application_id: uuid
    password: str
    first_name: str
    last_name: str
    display_name: str
    job_title: str
    time_zone: str
    country: str
    region: str
    company_name: str
    scope: Literal["sat:refresh"]
    fingerprint: str


class SubscriberTokenResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    subscriber_id: uuid
    token: jwt
    refresh_token: jwt


class SubscriberTokenStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SubscriberUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SwmlScript(TypedDict, total=False):
    """A SWML Script — either a [Calling Script](#schema/CallingSwmlScript) for inbound or

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    contents: dict[str, Any]
    request_url: str
    display_name: str
    status_callback_url: str | None
    status_callback_method: Literal["POST"]
    script_type: Literal["calling", "messaging"]


class SwmlScriptCreateRequest(TypedDict, total=False):
    """Body shape for creating a SWML Script. Choose a [Calling Script](#schema/CallingSwmlScriptCreateRequest) for inbound or outbound calls or a [Messaging Script](#schema/MessagingSwmlScriptCreateRequest) for inbound SMS or MMS messages. `script_type` is optional and defaults to `"calling"` when omitted — set it explicitly to `"messaging"` to create a Messaging Script. The script kind determines whether the script can be assigned as a call handler or a message handler on a phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    contents: str | dict[str, Any]
    status_callback_url: str
    script_type: Literal["calling", "messaging"]


class SwmlScriptCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SwmlScriptListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[SwmlScriptResponse]
    links: SwmlScriptPaginationresponse


class SwmlScriptPaginationresponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


class SwmlScriptResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    type: Literal["swml_script"]
    created_at: str
    updated_at: str
    swml_script: SwmlScript


class SwmlScriptUpdateRequest(TypedDict, total=False):
    """Body shape for updating an existing SWML Script. All fields are optional — include only what you want to change. Choose a [Calling Script](#schema/CallingSwmlScriptUpdateRequest) for inbound or outbound calls or a [Messaging Script](#schema/MessagingSwmlScriptUpdateRequest) for inbound SMS or MMS messages.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    contents: str | dict[str, Any]
    status_callback_url: str
    name: str
    script_type: Literal["calling", "messaging"]


class SwmlScriptUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SwmlWebhookCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SwmlWebhookUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


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


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


class Types_StatusCodes_StatusCode403(TypedDict, total=False):
    """Access is forbidden.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Forbidden"]


class Types_StatusCodes_StatusCode404(TypedDict, total=False):
    """The server cannot find the requested resource.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Not Found"]


class Types_StatusCodes_StatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


CxmlWebhookUsedForType: TypeAlias = "Literal['calling', 'messaging', 'faxing']"

UsedForType: TypeAlias = "Literal['calling', 'messaging']"


class VideoChannel(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    video: str


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


jwt: TypeAlias = "str"

uuid: TypeAlias = "str"


class AliasAddress(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    type: Literal["alias"]
    resource_id: uuid | None
    name: str
    display_name: str
    display_type: str | None
    channels: list[Literal["audio", "messaging", "video"]]
    codecs: (
        list[
            Literal[
                "OPUS",
                "OPUS@48000H@20I",
                "OPUS@24000H@20I",
                "OPUS@16000H@20I",
                "OPUS@8000H@20I",
                "G722",
                "PCMU",
                "PCMA",
                "G729",
                "VP8",
                "H264",
            ]
        ]
        | None
    )
    context: str
    uri: str
    created_at: str
    updated_at: str


class AliasAddressCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    display_name: str
    resource_id: uuid
    channels: list[Literal["audio", "messaging", "video"]]
    codecs: list[
        Literal[
            "OPUS",
            "OPUS@48000H@20I",
            "OPUS@24000H@20I",
            "OPUS@16000H@20I",
            "OPUS@8000H@20I",
            "G722",
            "PCMU",
            "PCMA",
            "G729",
            "VP8",
            "H264",
        ]
    ]
    context: Literal["private", "public"]


class AliasAddressUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    display_name: str
    channels: list[Literal["audio", "messaging", "video"]]
    codecs: list[
        Literal[
            "OPUS",
            "OPUS@48000H@20I",
            "OPUS@24000H@20I",
            "OPUS@16000H@20I",
            "OPUS@8000H@20I",
            "G722",
            "PCMU",
            "PCMA",
            "G729",
            "VP8",
            "H264",
        ]
    ]
    context: Literal["private", "public"]


class SipAddress(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    type: Literal["sip"]
    resource_id: uuid | None
    name: str
    display_name: str
    context: str
    uri: str
    user: str | None
    encryption: Literal["required", "optional", "forbidden"]
    codecs: list[
        Literal[
            "OPUS",
            "OPUS@48000H@20I",
            "OPUS@24000H@20I",
            "OPUS@16000H@20I",
            "OPUS@8000H@20I",
            "G722",
            "PCMU",
            "PCMA",
            "G729",
            "VP8",
            "H264",
        ]
    ]
    ciphers: list[
        Literal[
            "AEAD_AES_256_GCM_8",
            "AES_256_CM_HMAC_SHA1_80",
            "AES_CM_128_HMAC_SHA1_80",
            "AES_256_CM_HMAC_SHA1_32",
            "AES_CM_128_HMAC_SHA1_32",
        ]
    ]
    ip_auth_enabled: bool | None
    ip_auth: list[str] | None
    calling_handler_resource_id: uuid | None
    created_at: str
    updated_at: str


class SipAddressCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    user: str
    context_id: uuid
    calling_handler_resource_id: uuid
    ip_auth_enabled: bool
    ip_auth: list[str]
    codecs: list[
        Literal[
            "OPUS",
            "OPUS@48000H@20I",
            "OPUS@24000H@20I",
            "OPUS@16000H@20I",
            "OPUS@8000H@20I",
            "G722",
            "PCMU",
            "PCMA",
            "G729",
            "VP8",
            "H264",
        ]
    ]
    ciphers: list[
        Literal[
            "AEAD_AES_256_GCM_8",
            "AES_256_CM_HMAC_SHA1_80",
            "AES_CM_128_HMAC_SHA1_80",
            "AES_256_CM_HMAC_SHA1_32",
            "AES_CM_128_HMAC_SHA1_32",
        ]
    ]
    encryption: Literal["required", "optional", "forbidden"]
    password: str


class SipAddressUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    user: str
    context_id: uuid
    ip_auth_enabled: bool
    ip_auth: list[str]
    codecs: list[
        Literal[
            "OPUS",
            "OPUS@48000H@20I",
            "OPUS@24000H@20I",
            "OPUS@16000H@20I",
            "OPUS@8000H@20I",
            "G722",
            "PCMU",
            "PCMA",
            "G729",
            "VP8",
            "H264",
        ]
    ]
    ciphers: list[
        Literal[
            "AEAD_AES_256_GCM_8",
            "AES_256_CM_HMAC_SHA1_80",
            "AES_CM_128_HMAC_SHA1_80",
            "AES_256_CM_HMAC_SHA1_32",
            "AES_CM_128_HMAC_SHA1_32",
        ]
    ]
    encryption: Literal["required", "optional", "forbidden"]
    password: str


class PhoneNumberAddress(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    type: Literal["phone"]
    handler_type: Literal["calling", "messaging"]
    resource_id: uuid | None
    name: str
    phone_number: str | None
    phone_number_id: uuid
    created_at: str
    updated_at: str


class PhoneNumberAddressCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    phone_number_id: uuid
    number: str
    resource_id: uuid
    handler_type: Literal["calling", "messaging"]


class PhoneNumberAddressUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    resource_id: uuid


class AliasAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    links: FabricAddressPaginationResponse
    items_count: int
    data: list[AliasAddress]


class SipAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    links: FabricAddressPaginationResponse
    items_count: int
    data: list[SipAddress]


class PhoneNumberAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    links: FabricAddressPaginationResponse
    items_count: int
    data: list[PhoneNumberAddress]


class WhatsappNumberAssignRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    whatsapp_number_id: uuid
    handler: UsedForType


class WhatsappNumberAddressResponse(TypedDict, total=False):
    """The Address created for the WhatsApp number on the Resource. Its `type` is `app` for most handlers, `room` for a Video Room, and `call` for a Resource that connects the call to a SIP endpoint or connector.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    resource_id: uuid | None
    name: str
    display_name: str
    type: Literal["app", "call", "room"]
    cover_url: str | None
    preview_url: str | None
    locked: bool
    channels: dict[str, Any]


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


class Foreach(TypedDict, total=False):
    """Without `append`, `input_key` and `output_key`, a Foreach has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    append: str
    input_key: str
    max: float | str
    output_key: str


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


class AIAgentPrompt(TypedDict, total=False):
    """Defines the AI agent's personality, goals, behaviors, and instructions for handling conversations.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    contexts: Contexts
    frequency_penalty: float | str
    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[dict[str, Any]]
    presence_penalty: float | str
    reasoning_effort: str
    steps: list[Step]
    temperature: float | str
    text: str
    top_p: float | str
    verbosity: str


class AIAgentPostPrompt(TypedDict, total=False):
    """The final set of instructions and configuration settings to send to the agent.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    frequency_penalty: float | str
    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[POM]
    presence_penalty: float | str
    reasoning_effort: str
    temperature: float | str
    text: str
    top_p: float | str
    verbosity: str


class AIAgentSWAIGFunction(TypedDict, total=False):
    """Without one of `data_map` / `web_hook_url`, one of `description` / `purpose` and `function`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    active: bool | float | str
    argument: dict[str, Any]
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
    id: str
    arguments: list[dict[str, Any]]


AIAgentPronounce = TypedDict(
    "AIAgentPronounce",
    {
        "id": "str",
        "replace": "str",
        "with": "str",
        "replace_with": "str",
        "ignore_case": "bool | float | str",
    },
    total=False,
)
AIAgentPronounce.__doc__ = """Without `replace` and `with`, the element has no effect: it is accepted and ignored, not rejected.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""

ListAliasAddressesResponse: TypeAlias = "AliasAddressListResponse"
CreateAliasAddressRequest: TypeAlias = "AliasAddressCreateRequest"
CreateAliasAddressResponse: TypeAlias = "AliasAddress"
GetAliasAddressResponse: TypeAlias = "AliasAddress"
UpdateAliasAddressRequest: TypeAlias = "AliasAddressUpdateRequest"
UpdateAliasAddressResponse: TypeAlias = "AliasAddress"
ListSipAddressesResponse: TypeAlias = "SipAddressListResponse"
CreateSipAddressRequest: TypeAlias = "SipAddressCreateRequest"
CreateSipAddressResponse: TypeAlias = "SipAddress"
GetSipAddressResponse: TypeAlias = "SipAddress"
UpdateSipAddressRequest: TypeAlias = "SipAddressUpdateRequest"
UpdateSipAddressResponse: TypeAlias = "SipAddress"
ListPhoneNumberAddressesResponse: TypeAlias = "PhoneNumberAddressListResponse"
CreatePhoneNumberAddressRequest: TypeAlias = "PhoneNumberAddressCreateRequest"
CreatePhoneNumberAddressResponse: TypeAlias = "PhoneNumberAddress"
GetPhoneNumberAddressResponse: TypeAlias = "PhoneNumberAddress"
UpdatePhoneNumberAddressRequest: TypeAlias = "PhoneNumberAddressUpdateRequest"
UpdatePhoneNumberAddressResponse: TypeAlias = "PhoneNumberAddress"
ListFabricAddressesResponse: TypeAlias = "FabricAddressListResponse"
GetFabricAddressResponse: TypeAlias = "FabricAddressItem"
CreateEmbedsTokenRequest: TypeAlias = "EmbedsTokensRequest"
CreateEmbedsTokenResponse: TypeAlias = "EmbedsTokensResponse"
CreateSubscriberGuestTokenRequest: TypeAlias = "SubscriberGuestTokenCreateRequest"
CreateSubscriberGuestTokenResponse: TypeAlias = "SubscriberGuestTokenCreateResponse"
ListResourcesResponse: TypeAlias = "ResourceListResponse"
ListAiAgentsResponse: TypeAlias = "AIAgentListResponse"
CreateAiAgentRequest: TypeAlias = "AIAgentCreateRequest"
CreateAiAgentResponse: TypeAlias = "AIAgentResponse"
ListAiAgentVoicesResponse: TypeAlias = "list[AIAgentVoice]"
ListAiAgentConversationLogsResponse: TypeAlias = "AIAgentConversationLogListResponse"
ListAiAgentAddressesResponse: TypeAlias = "AIAgentAddressListResponse"
GetAiAgentResponse: TypeAlias = "AIAgentResponse"
UpdateAiAgentRequest: TypeAlias = "AIAgentUpdateRequest"
UpdateAiAgentResponse: TypeAlias = "AIAgentResponse"
ListCallFlowAddressesResponse: TypeAlias = "CallFlowAddressListResponse"
ListCallFlowVersionsResponse: TypeAlias = "CallFlowVersionListResponse"
DeployCallFlowVersionRequest: TypeAlias = "CallFlowVersionDeployRequest"
DeployCallFlowVersionResponse: TypeAlias = "CallFlowVersionDeployResponse"
ListCallFlowsResponse: TypeAlias = "CallFlowListResponse"
CreateCallFlowRequest: TypeAlias = "CallFlowCreateRequest"
CreateCallFlowResponse: TypeAlias = "CallFlowResponse"
GetCallFlowResponse: TypeAlias = "CallFlowResponse"
UpdateCallFlowRequest: TypeAlias = "CallFlowUpdateRequest"
UpdateCallFlowResponse: TypeAlias = "CallFlowResponse"
ListConferenceRoomAddressesResponse: TypeAlias = "ConferenceRoomAddressListResponse"
ListConferenceRoomsResponse: TypeAlias = "ConferenceRoomListResponse"
CreateConferenceRoomRequest: TypeAlias = "ConferenceRoomCreateRequest"
CreateConferenceRoomResponse: TypeAlias = "ConferenceRoomResponse"
GetConferenceRoomResponse: TypeAlias = "ConferenceRoomResponse"
UpdateConferenceRoomRequest: TypeAlias = "ConferenceRoomUpdateRequest"
UpdateConferenceRoomResponse: TypeAlias = "ConferenceRoomResponse"
ListCxmlApplicationsResponse: TypeAlias = "CxmlApplicationListResponse"
GetCxmlApplicationResponse: TypeAlias = "CxmlApplicationResponse"
UpdateCxmlApplicationRequest: TypeAlias = "CxmlApplicationUpdateRequest"
UpdateCxmlApplicationResponse: TypeAlias = "CxmlApplicationResponse"
ListCxmlApplicationAddressesResponse: TypeAlias = "CxmlApplicationAddressListResponse"
ListCxmlScriptsResponse: TypeAlias = "CXMLScriptListResponse"
CreateCxmlScriptRequest: TypeAlias = "CXMLScriptCreateRequest"
CreateCxmlScriptResponse: TypeAlias = "CXMLScriptResponse"
GetCxmlScriptResponse: TypeAlias = "CXMLScriptResponse"
UpdateCxmlScriptRequest: TypeAlias = "CXMLScriptUpdateRequest"
UpdateCxmlScriptResponse: TypeAlias = "CXMLScriptResponse"
ListCxmlScriptAddressesResponse: TypeAlias = "CXMLScriptAddressListResponse"
ListCxmlWebhooksResponse: TypeAlias = "CXMLWebhookListResponse"
CreateCxmlWebhookRequest: TypeAlias = "CXMLWebhookCreateRequest"
CreateCxmlWebhookResponse: TypeAlias = "CXMLWebhookResponse"
ListCxmlWebhookAddressesResponse: TypeAlias = "CXMLWebhookAddressListResponse"
GetCxmlWebhookResponse: TypeAlias = "CXMLWebhookResponse"
UpdateCxmlWebhookRequest: TypeAlias = "CXMLWebhookUpdateRequest"
UpdateCxmlWebhookResponse: TypeAlias = "CXMLWebhookResponse"
ListDialogflowAgentsResponse: TypeAlias = "DialogflowAgentListResponse"
GetDialogflowAgentResponse: TypeAlias = "DialogflowAgentResponse"
UpdateDialogflowAgentRequest: TypeAlias = "DialogflowAgentUpdateRequest"
UpdateDialogflowAgentResponse: TypeAlias = "DialogflowAgentResponse"
ListDialogflowAgentAddressesResponse: TypeAlias = "DialogflowAgentAddressListResponse"
ListFreeswitchConnectorsResponse: TypeAlias = "FreeswitchConnectorListResponse"
CreateFreeswitchConnectorRequest: TypeAlias = "FreeswitchConnectorCreateRequest"
CreateFreeswitchConnectorResponse: TypeAlias = "FreeswitchConnectorResponse"
GetFreeswitchConnectorResponse: TypeAlias = "FreeswitchConnectorResponse"
UpdateFreeswitchConnectorRequest: TypeAlias = "FreeswitchConnectorUpdateRequest"
UpdateFreeswitchConnectorResponse: TypeAlias = "FreeswitchConnectorResponse"
ListFreeswitchConnectorAddressesResponse: TypeAlias = (
    "FreeswitchConnectorAddressListResponse"
)
ListRelayApplicationsResponse: TypeAlias = "RelayApplicationListResponse"
CreateRelayApplicationRequest: TypeAlias = "RelayApplicationCreateRequest"
CreateRelayApplicationResponse: TypeAlias = "RelayApplicationResponse"
GetRelayApplicationResponse: TypeAlias = "RelayApplicationResponse"
UpdateRelayApplicationRequest: TypeAlias = "RelayApplicationUpdateRequest"
UpdateRelayApplicationResponse: TypeAlias = "RelayApplicationResponse"
ListRelayApplicationAddressesResponse: TypeAlias = "RelayApplicationAddressListResponse"
ListSipEndpointsResponse: TypeAlias = "SipEndpointListResponse"
CreateSipEndpointRequest: TypeAlias = "SipEndpointCreateRequest"
CreateSipEndpointResponse: TypeAlias = "SipEndpointResponse"
AssignResourceSipEndpointRequest: TypeAlias = "ResourceSipEndpointAssignRequest"
AssignResourceSipEndpointResponse: TypeAlias = "ResourceResponseSipEndpoint"
GetSipEndpointResponse: TypeAlias = "SipEndpointResponse"
UpdateSipEndpointRequest: TypeAlias = "SipEndpointUpdateRequest"
UpdateSipEndpointResponse: TypeAlias = "SipEndpointResponse"
ListSipEndpointAddressesResponse: TypeAlias = "SipEndpointAddressListResponse"
ListSipGatewaysResponse: TypeAlias = "SipGatewayListResponse"
CreateSipGatewayRequest: TypeAlias = "SipGatewayRequest"
CreateSipGatewayResponse: TypeAlias = "SipGatewayResponse"
ListSipGatewayAddressesResponse: TypeAlias = "SipGatewayAddressListResponse"
GetSipGatewayResponse: TypeAlias = "SipGatewayResponse"
UpdateSipGatewayRequest: TypeAlias = "SipGatewayRequestUpdate"
UpdateSipGatewayResponse: TypeAlias = "SipGatewayResponse"
ListSubscribersResponse: TypeAlias = "SubscriberListResponse"
CreateSubscriberRequest: TypeAlias = "SubscriberRequest"
CreateSubscriberResponse: TypeAlias = "SubscriberResponse"
ListSubscriberSipEndpointsResponse: TypeAlias = "SubscriberSipEndpointListResponse"
CreateSubscriberSipEndpointRequest: TypeAlias = "SubscriberSipEndpointRequest"
CreateSubscriberSipEndpointResponse: TypeAlias = "SubscriberSIPEndpoint"
GetSubscriberSipEndpointResponse: TypeAlias = "SubscriberSIPEndpoint"
UpdateSubscriberSipEndpointRequest: TypeAlias = "SubscriberSipEndpointRequestUpdate"
UpdateSubscriberSipEndpointResponse: TypeAlias = "SubscriberSIPEndpoint"
GetSubscriberResponse: TypeAlias = "SubscriberResponse"
UpdateSubscriberRequest: TypeAlias = "SubscriberUpdateRequest"
UpdateSubscriberResponse: TypeAlias = "SubscriberResponse"
ListSubscriberAddressesResponse: TypeAlias = "SubscriberAddressesResponse"
ListSwmlScriptsResponse: TypeAlias = "SwmlScriptListResponse"
CreateSwmlScriptRequest: TypeAlias = "SwmlScriptCreateRequest"
CreateSwmlScriptResponse: TypeAlias = "SwmlScriptResponse"
GetSwmlScriptResponse: TypeAlias = "SwmlScriptResponse"
UpdateSwmlScriptRequest: TypeAlias = "SwmlScriptUpdateRequest"
UpdateSwmlScriptResponse: TypeAlias = "SwmlScriptResponse"
ListSwmlScriptAddressesResponse: TypeAlias = "SWMLScriptAddressListResponse"
ListSwmlWebhooksResponse: TypeAlias = "SWMLWebhookListResponse"
CreateSwmlWebhookRequest: TypeAlias = "SWMLWebhookCreateRequest"
CreateSwmlWebhookResponse: TypeAlias = "SWMLWebhookResponse"
GetSwmlWebhookResponse: TypeAlias = "SWMLWebhookResponse"
UpdateSwmlWebhookRequest: TypeAlias = "SWMLWebhookUpdateRequest"
UpdateSwmlWebhookResponse: TypeAlias = "SWMLWebhookResponse"
ListSwmlWebhookAddressesResponse: TypeAlias = "SWMLWebhookAddressListResponse"
GetResourceResponse: TypeAlias = "ResourceResponse"
ListResourceAddressesResponse: TypeAlias = "ResourceAddressListResponse"
AssignResourceDomainApplicationRequest: TypeAlias = "DomainApplicationAssignRequest"
AssignResourceDomainApplicationResponse: TypeAlias = "DomainApplicationResponse"
AssignResourcePhoneRouteRequest: TypeAlias = "PhoneRouteAssignRequest"
AssignResourcePhoneRouteResponse: TypeAlias = "PhoneRouteResponse"
AssignResourceWhatsappNumberRequest: TypeAlias = "WhatsappNumberAssignRequest"
AssignResourceWhatsappNumberResponse: TypeAlias = "WhatsappNumberAddressResponse"
CreateSubscriberTokenRequest: TypeAlias = "SubscriberTokenRequest"
CreateSubscriberTokenResponse: TypeAlias = "SubscriberTokenResponse"
RefreshSubscriberTokenRequest: TypeAlias = "SubscriberRefreshTokenRequest"
RefreshSubscriberTokenResponse: TypeAlias = "SubscriberRefreshTokenResponse"


# Aliases of one concrete ``dict`` type, emitted unquoted and last so the name stays
# callable at runtime (``ConnectDeviceSingle(to=...)`` builds a dict, as it did when the
# name was a TypedDict).
Contexts: TypeAlias = dict[str, Context]


# Deprecated aliases: names this module exported before its types were re-derived
# (signalwire-python 3.x at f870cc15). Kept so existing imports keep working; use the
# new name. Names with no single replacement are listed in CHANGELOG.md instead.
import signalwire.rest.namespaces.calling_types_generated as _dep_m0  # noqa: E402

# deprecated: use signalwire.rest.namespaces.calling_types_generated.AI
AI = _dep_m0.AI
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AIObject
AIObject = _dep_m0.AIObject
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AIPostPrompt
AIPostPrompt = _dep_m0.AIPostPrompt
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AIPostPromptPom
AIPostPromptPom = _dep_m0.AIPostPromptPom
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AIPostPromptPom
AIPostPromptPomUpdate = _dep_m0.AIPostPromptPom
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AIPostPromptText
AIPostPromptText = _dep_m0.AIPostPromptText
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AIPostPromptText
AIPostPromptTextUpdate = _dep_m0.AIPostPromptText
# deprecated: use AIAgentPostPrompt
AIPostPromptUpdate = AIAgentPostPrompt
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AIPrompt
AIPrompt = _dep_m0.AIPrompt
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AIPromptPom
AIPromptPom = _dep_m0.AIPromptPom
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AIPromptPom
AIPromptPomUpdate = _dep_m0.AIPromptPom
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AIPromptText
AIPromptText = _dep_m0.AIPromptText
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AIPromptText
AIPromptTextUpdate = _dep_m0.AIPromptText
# deprecated: use AIAgentPrompt
AIPromptUpdate = AIAgentPrompt
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AllOfProperty
AllOfProperty = _dep_m0.AllOfProperty
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AmazonBedrock
AmazonBedrock = _dep_m0.AmazonBedrock
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AmazonBedrockObject
AmazonBedrockObject = _dep_m0.AmazonBedrockObject
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Answer
Answer = _dep_m0.Answer
# deprecated: use signalwire.rest.namespaces.calling_types_generated.AnyOfProperty
AnyOfProperty = _dep_m0.AnyOfProperty
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ArrayProperty
ArrayProperty = _dep_m0.ArrayProperty
# deprecated: use signalwire.rest.namespaces.calling_types_generated.BedrockParams
BedrockParams = _dep_m0.BedrockParams
# deprecated: use signalwire.rest.namespaces.calling_types_generated.BedrockPostPrompt
BedrockPostPrompt = _dep_m0.BedrockPostPrompt
# deprecated: use signalwire.rest.namespaces.calling_types_generated.BedrockPrompt
BedrockPrompt = _dep_m0.BedrockPrompt
# deprecated: use signalwire.rest.namespaces.calling_types_generated.BedrockSWAIG
BedrockSWAIG = _dep_m0.BedrockSWAIG
# deprecated: use signalwire.rest.namespaces.calling_types_generated.BedrockSWAIGFunction
BedrockSWAIGFunction = _dep_m0.BedrockSWAIGFunction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.BooleanProperty
BooleanProperty = _dep_m0.BooleanProperty
# deprecated: use signalwire.rest.namespaces.calling_types_generated.CallStatus
CallStatus = _dep_m0.CallStatus
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ChangeContextAction
ChangeContextAction = _dep_m0.ChangeContextAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ChangeStepAction
ChangeStepAction = _dep_m0.ChangeStepAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Cond
Cond = _dep_m0.Cond
# deprecated: use signalwire.rest.namespaces.calling_types_generated.CondElse
CondElse = _dep_m0.CondElse
# deprecated: use signalwire.rest.namespaces.calling_types_generated.CondParams
CondParams = _dep_m0.CondParams
# deprecated: use signalwire.rest.namespaces.calling_types_generated.CondReg
CondReg = _dep_m0.CondReg
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Connect
Connect = _dep_m0.Connect
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ConnectDeviceParallel
ConnectDeviceParallel = _dep_m0.ConnectDeviceParallel
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ConnectDeviceSerial
ConnectDeviceSerial = _dep_m0.ConnectDeviceSerial
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ConnectDeviceSerialParallel
ConnectDeviceSerialParallel = _dep_m0.ConnectDeviceSerialParallel
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ConnectDeviceSingle
ConnectDeviceSingle = _dep_m0.ConnectDeviceSingle
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ConnectHeaders
ConnectHeaders = _dep_m0.ConnectHeaders
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ConnectSwitch
ConnectSwitch = _dep_m0.ConnectSwitch
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ConstProperty
ConstProperty = _dep_m0.ConstProperty
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ContextPOMSteps
ContextPOMSteps = _dep_m0.ContextPOMSteps
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ContextSteps
ContextSteps = _dep_m0.ContextSteps
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ContextSwitchAction
ContextSwitchAction = _dep_m0.ContextSwitchAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ContextTextSteps
ContextTextSteps = _dep_m0.ContextTextSteps
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ContextsObject
ContextsObject = _dep_m0.ContextsObject
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ContextsObject
ContextsObjectUpdate = _dep_m0.ContextsObject
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ContextsPOMObject
ContextsPOMObject = _dep_m0.ContextsPOMObject
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ContextsPOMObject
ContextsPOMObjectUpdate = _dep_m0.ContextsPOMObject
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ContextsTextObject
ContextsTextObject = _dep_m0.ContextsTextObject
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ContextsTextObject
ContextsTextObjectUpdate = _dep_m0.ContextsTextObject
# deprecated: use Contexts
ContextsUpdate = Contexts
# deprecated: use signalwire.rest.namespaces.calling_types_generated.CustomTranslationFilter
CustomTranslationFilter = _dep_m0.CustomTranslationFilter
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Denoise
Denoise = _dep_m0.Denoise
# deprecated: use signalwire.rest.namespaces.calling_types_generated.DetectMachine
DetectMachine = _dep_m0.DetectMachine
# deprecated: use signalwire.rest.namespaces.calling_types_generated.EnterQueue
EnterQueue = _dep_m0.EnterQueue
# deprecated: use signalwire.rest.namespaces.calling_types_generated.EnterQueueObject
EnterQueueObject = _dep_m0.EnterQueueObject
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Execute
Execute = _dep_m0.Execute
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ExecuteSwitch
ExecuteSwitch = _dep_m0.ExecuteSwitch
# deprecated: use FunctionFillers
FunctionFillersUpdate = FunctionFillers
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Goto
Goto = _dep_m0.Goto
# deprecated: use signalwire.rest.namespaces.calling_types_generated.HangUpHookSWAIGFunction
HangUpHookSWAIGFunction = _dep_m0.HangUpHookSWAIGFunction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Hangup
Hangup = _dep_m0.Hangup
# deprecated: use signalwire.rest.namespaces.calling_types_generated.HangupAction
HangupAction = _dep_m0.HangupAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Hint
Hint = _dep_m0.Hint
# deprecated: use signalwire.rest.namespaces.calling_types_generated.HoldAction
HoldAction = _dep_m0.HoldAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.InjectAction
InjectAction = _dep_m0.InjectAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.IntegerProperty
IntegerProperty = _dep_m0.IntegerProperty
# deprecated: use signalwire.rest.namespaces.calling_types_generated.JoinConference
JoinConference = _dep_m0.JoinConference
# deprecated: use signalwire.rest.namespaces.calling_types_generated.JoinConferenceObject
JoinConferenceObject = _dep_m0.JoinConferenceObject
# deprecated: use signalwire.rest.namespaces.calling_types_generated.JoinRoom
JoinRoom = _dep_m0.JoinRoom
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Label
Label = _dep_m0.Label
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Languages
Languages = _dep_m0.Languages
# deprecated: use signalwire.rest.namespaces.calling_types_generated.LanguagesWithFillers
LanguagesWithFillers = _dep_m0.LanguagesWithFillers
# deprecated: use signalwire.rest.namespaces.calling_types_generated.LanguagesWithSoloFillers
LanguagesWithSoloFillers = _dep_m0.LanguagesWithSoloFillers
# deprecated: use signalwire.rest.namespaces.calling_types_generated.LiveTranscribe
LiveTranscribe = _dep_m0.LiveTranscribe
# deprecated: use signalwire.rest.namespaces.calling_types_generated.LiveTranslate
LiveTranslate = _dep_m0.LiveTranslate
# deprecated: use signalwire.rest.namespaces.calling_types_generated.NullProperty
NullProperty = _dep_m0.NullProperty
# deprecated: use signalwire.rest.namespaces.calling_types_generated.NumberProperty
NumberProperty = _dep_m0.NumberProperty
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ObjectProperty
ObjectProperty = _dep_m0.ObjectProperty
# deprecated: use signalwire.rest.namespaces.calling_types_generated.OneOfProperty
OneOfProperty = _dep_m0.OneOfProperty
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Pay
Pay = _dep_m0.Pay
# deprecated: use signalwire.rest.namespaces.calling_types_generated.PayParameters
PayParameters = _dep_m0.PayParameters
# deprecated: use signalwire.rest.namespaces.calling_types_generated.PayPromptAction
PayPromptAction = _dep_m0.PayPromptAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.PayPromptPlayAction
PayPromptPlayAction = _dep_m0.PayPromptPlayAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.PayPromptSayAction
PayPromptSayAction = _dep_m0.PayPromptSayAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.PayPrompts
PayPrompts = _dep_m0.PayPrompts
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Play
Play = _dep_m0.Play
# deprecated: use signalwire.rest.namespaces.calling_types_generated.PlayWithURL
PlayWithURL = _dep_m0.PlayWithURL
# deprecated: use signalwire.rest.namespaces.calling_types_generated.PlayWithURLS
PlayWithURLS = _dep_m0.PlayWithURLS
# deprecated: use signalwire.rest.namespaces.calling_types_generated.PlaybackBGAction
PlaybackBGAction = _dep_m0.PlaybackBGAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.PomSectionBodyContent
PomSectionBodyContent = _dep_m0.PomSectionBodyContent
# deprecated: use signalwire.rest.namespaces.calling_types_generated.PomSectionBulletsContent
PomSectionBulletsContent = _dep_m0.PomSectionBulletsContent
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Prompt
Prompt = _dep_m0.Prompt
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Pronounce
Pronounce = _dep_m0.Pronounce
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ReceiveFax
ReceiveFax = _dep_m0.ReceiveFax
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Record
Record = _dep_m0.Record
# deprecated: use signalwire.rest.namespaces.calling_types_generated.RecordCall
RecordCall = _dep_m0.RecordCall
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Request
Request = _dep_m0.Request
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Return
Return = _dep_m0.Return
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SIPRefer
SIPRefer = _dep_m0.SIPRefer
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SMSWithBody
SMSWithBody = _dep_m0.SMSWithBody
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SMSWithMedia
SMSWithMedia = _dep_m0.SMSWithMedia
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SWAIG
SWAIG = _dep_m0.SWAIG
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SWAIGFunction
SWAIGFunction = _dep_m0.SWAIGFunction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SWAIGIncludes
SWAIGIncludes = _dep_m0.SWAIGIncludes
# deprecated: use SWAIGInternalFiller
SWAIGInternalFillerUpdate = SWAIGInternalFiller
# deprecated: use AIAgentSWAIG
SWAIGUpdate = AIAgentSWAIG
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SWMLAction
SWMLAction = _dep_m0.SWMLAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SWMLMethod
SWMLMethod = _dep_m0.SWMLMethod
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SWMLObject
SWMLObject = _dep_m0.SWMLObject
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SWMLVar
SWMLVar = _dep_m0.SWMLVar
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SayAction
SayAction = _dep_m0.SayAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SchemaType
SchemaType = _dep_m0.SchemaType
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Section
Section = _dep_m0.Section
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SendDigits
SendDigits = _dep_m0.SendDigits
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SendFax
SendFax = _dep_m0.SendFax
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SendSMS
SendSMS = _dep_m0.SendSMS
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Set
Set = _dep_m0.Set
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SetGlobalDataAction
SetGlobalDataAction = _dep_m0.SetGlobalDataAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SetMetaDataAction
SetMetaDataAction = _dep_m0.SetMetaDataAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Sleep
Sleep = _dep_m0.Sleep
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SpeechEngine
SpeechEngine = _dep_m0.SpeechEngine
# deprecated: use signalwire.rest.namespaces.calling_types_generated.StartAction
StartAction = _dep_m0.StartAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.StartUpHookSWAIGFunction
StartUpHookSWAIGFunction = _dep_m0.StartUpHookSWAIGFunction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.StopAction
StopAction = _dep_m0.StopAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.StopDenoise
StopDenoise = _dep_m0.StopDenoise
# deprecated: use signalwire.rest.namespaces.calling_types_generated.StopPlaybackBGAction
StopPlaybackBGAction = _dep_m0.StopPlaybackBGAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.StopRecordCall
StopRecordCall = _dep_m0.StopRecordCall
# deprecated: use signalwire.rest.namespaces.calling_types_generated.StopTap
StopTap = _dep_m0.StopTap
# deprecated: use signalwire.rest.namespaces.calling_types_generated.StringFormat
StringFormat = _dep_m0.StringFormat
# deprecated: use signalwire.rest.namespaces.calling_types_generated.StringProperty
StringProperty = _dep_m0.StringProperty
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SummarizeAction
SummarizeAction = _dep_m0.SummarizeAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SummarizeActionUnion
SummarizeActionUnion = _dep_m0.SummarizeActionUnion
# deprecated: use signalwire.rest.namespaces.calling_types_generated.SummarizeConversationSWAIGFunction
SummarizeConversationSWAIGFunction = _dep_m0.SummarizeConversationSWAIGFunction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Switch
Switch = _dep_m0.Switch
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Tap
Tap = _dep_m0.Tap
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ToggleFunctionsAction
ToggleFunctionsAction = _dep_m0.ToggleFunctionsAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.TranscribeAction
TranscribeAction = _dep_m0.TranscribeAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.TranscribeDirection
TranscribeDirection = _dep_m0.TranscribeDirection
# deprecated: use signalwire.rest.namespaces.calling_types_generated.TranscribeStartAction
TranscribeStartAction = _dep_m0.TranscribeStartAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.TranscribeSummarizeAction
TranscribeSummarizeAction = _dep_m0.TranscribeSummarizeAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.TranscribeSummarizeActionUnion
TranscribeSummarizeActionUnion = _dep_m0.TranscribeSummarizeActionUnion
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Transfer
Transfer = _dep_m0.Transfer
# deprecated: use signalwire.rest.namespaces.calling_types_generated.TranslateAction
TranslateAction = _dep_m0.TranslateAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.TranslateDirection
TranslateDirection = _dep_m0.TranslateDirection
# deprecated: use signalwire.rest.namespaces.calling_types_generated.TranslationFilterPreset
TranslationFilterPreset = _dep_m0.TranslationFilterPreset
# deprecated: use signalwire.rest.namespaces.calling_types_generated.Unset
Unset = _dep_m0.Unset
# deprecated: use signalwire.rest.namespaces.calling_types_generated.UnsetGlobalDataAction
UnsetGlobalDataAction = _dep_m0.UnsetGlobalDataAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.UnsetMetaDataAction
UnsetMetaDataAction = _dep_m0.UnsetMetaDataAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.UserEvent
UserEvent = _dep_m0.UserEvent
# deprecated: use signalwire.rest.namespaces.calling_types_generated.UserInputAction
UserInputAction = _dep_m0.UserInputAction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.UserSWAIGFunction
UserSWAIGFunction = _dep_m0.UserSWAIGFunction
# deprecated: use signalwire.rest.namespaces.calling_types_generated.ValidConfirmMethods
ValidConfirmMethods = _dep_m0.ValidConfirmMethods
# deprecated: use signalwire.rest.namespaces.calling_types_generated.play_url
play_url = _dep_m0.play_url
