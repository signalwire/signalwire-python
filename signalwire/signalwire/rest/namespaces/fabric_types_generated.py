# AUTO-GENERATED from porting-sdk/rest-apis/fabric/openapi.yaml — DO NOT EDIT.
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
    hints: list[str | Hint]
    languages: list[Languages]
    params: AIParams
    post_prompt: AIPostPrompt
    post_prompt_url: str
    pronounce: list[Pronounce]
    prompt: AIPrompt
    SWAIG: SWAIG
    agent_id: uuid
    name: str


class AIAgentAddressListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddressApp]
    links: AIAddressPaginationResponse


class AIAgentCreateRequest(TypedDict, total=False):
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
    agent_id: uuid
    name: str


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
    hints: list[str | Hint]
    languages: list[Languages]
    params: AIParams
    post_prompt: AIPostPromptUpdate
    post_prompt_url: str
    pronounce: list[Pronounce]
    prompt: AIPromptUpdate
    SWAIG: SWAIGUpdate
    agent_id: uuid
    name: str


class AIAgentUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


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


class AIPostPromptPomUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    pom: list[POM]


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


class AIPostPromptTextUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    text: str


AIPostPromptUpdate: TypeAlias = "AIPostPromptTextUpdate | AIPostPromptPomUpdate"


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


class AIPromptPomUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    pom: list[POM]
    contexts: ContextsUpdate


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


class AIPromptTextUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    text: str
    contexts: ContextsUpdate


AIPromptUpdate: TypeAlias = "AIPromptTextUpdate | AIPromptPomUpdate"


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


class AudioChannel(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    audio: str


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


class CXMLScript(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    contents: str
    request_count: int
    last_accessed_at: str | None
    request_url: str
    script_type: Literal["calling", "messaging"]
    display_name: str
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

    display_name: str
    contents: str
    status_callback_url: str
    status_callback_method: Literal["GET"] | Literal["POST"]


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
    name: str
    type: Literal["cxml_script"]
    created_at: str
    updated_at: str
    cxml_script: CXMLScript


class CXMLScriptUpdateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    display_name: str
    contents: str
    status_callback_url: str
    status_callback_method: Literal["GET"] | Literal["POST"]


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
    used_for: UsedForType
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
    used_for: UsedForType
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
    used_for: UsedForType
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
    flow_data: str
    relayml: str
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


class CallFlowUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class CallFlowVersion(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    version: str
    created_at: str
    updated_at: str
    flow_data: str
    relayml: str


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
    flow_data: str
    relayml: str


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

CallStatus: TypeAlias = "str"


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


Ciphers: TypeAlias = "Literal['AEAD_AES_256_GCM_8', 'AES_256_CM_HMAC_SHA1_80', 'AES_CM_128_HMAC_SHA1_80', 'AES_256_CM_HMAC_SHA1_32', 'AES_CM_128_HMAC_SHA1_32']"

Codecs: TypeAlias = "Literal['PCMU', 'PCMA', 'G722', 'G729', 'OPUS', 'VP8', 'H264']"


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


class ConferenceRoom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    description: str
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


class ConferenceRoomUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class Connect(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    connect: ConnectDeviceSingle


ConnectDeviceParallel: TypeAlias = "dict[str, Any]"

ConnectDeviceSerial: TypeAlias = "dict[str, Any]"

ConnectDeviceSerialParallel: TypeAlias = "dict[str, Any]"

ConnectDeviceSingle: TypeAlias = "dict[str, Any]"


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


Contexts: TypeAlias = "dict[str, Context]"

ContextsObject: TypeAlias = "ContextsPOMObject | ContextsTextObject"

ContextsObjectUpdate: TypeAlias = "ContextsPOMObjectUpdate | ContextsTextObjectUpdate"


class ContextsPOMObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    steps: list[ContextSteps]
    isolated: bool
    enter_fillers: list[FunctionFillers]
    exit_fillers: list[FunctionFillers]
    pom: list[POM]


class ContextsPOMObjectUpdate(TypedDict, total=False):
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


class ContextsTextObjectUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    steps: list[ContextSteps]
    isolated: bool
    enter_fillers: list[FunctionFillers]
    exit_fillers: list[FunctionFillers]
    text: str


class ContextsUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: ContextsObjectUpdate


class ConversationMessage(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    content: str
    lang: str
    role: ConversationRole
    tool_call_id: str
    tool_calls: list[Any]


ConversationRole: TypeAlias = "str"

CustomTranslationFilter: TypeAlias = "str"


class CxmlApplication(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    friendly_name: str
    voice_url: str | None
    voice_method: Literal["GET"] | Literal["POST"]
    voice_fallback_url: str | None
    voice_fallback_method: Literal["GET"] | Literal["POST"]
    status_callback: str | None
    status_callback_method: Literal["GET"] | Literal["POST"]
    sms_url: str | None
    sms_method: Literal["GET"] | Literal["POST"]
    sms_fallback_url: str | None
    sms_fallback_method: Literal["GET"] | Literal["POST"]
    sms_status_callback: str | None
    sms_status_callback_method: Literal["GET"] | Literal["POST"]


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

    display_name: str
    account_sid: uuid
    voice_url: str
    voice_method: Literal["GET"] | Literal["POST"]
    voice_fallback_url: str
    voice_fallback_method: Literal["GET"] | Literal["POST"]
    status_callback: str
    status_callback_method: Literal["GET"] | Literal["POST"]
    sms_url: str
    sms_method: Literal["GET"] | Literal["POST"]
    sms_fallback_url: str
    sms_fallback_method: Literal["GET"] | Literal["POST"]
    sms_status_callback: str
    sms_status_callback_method: Literal["GET"] | Literal["POST"]


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


class Denoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    denoise: dict[str, Any] | list[Any] | float | str


class DetectMachine(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    detect_machine: dict[str, Any] | list[Any] | float | str


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
    say: str
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
    voice: str


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
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str
    locked: bool
    channels: AddressChannel
    created_at: str
    type: Literal["app"]


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


class FabricAddress(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str
    locked: bool
    channels: AddressChannel
    created_at: str
    type: DisplayTypes


class FabricAddressApp(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str
    locked: bool
    channels: AddressChannel
    created_at: str
    type: Literal["app"]


class FabricAddressCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str
    locked: bool
    channels: AddressChannel
    created_at: str
    type: Literal["call"]


class FabricAddressPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

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
    preview_url: str
    locked: bool
    channels: AddressChannel
    created_at: str
    type: Literal["room"]


class FabricAddressSubscriber(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    display_name: str
    cover_url: str
    preview_url: str
    locked: bool
    channels: AddressChannel
    created_at: str
    type: Literal["subscriber"]


class FabricAddressesResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    data: list[FabricAddress]
    links: FabricAddressPaginationResponse


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
    display_name: str
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


FunctionFillersUpdate: TypeAlias = "dict[str, Any]"

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


class GuestTokenCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


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


class InviteTokenCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class JoinConference(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    join_conference: JoinConferenceObject | list[str | SWMLVar] | float | dict[str, Any]


class JoinConferenceObject(TypedDict, total=False):
    """Join an ad-hoc audio conference started on either the SignalWire or Compatibility API.

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


Layout: TypeAlias = "Literal['grid-responsive', 'grid-responsive-mobile', 'highlight-1-responsive', '1x1', '2x1', '2x2', '5up', '3x3', '4x4', '5x5', '6x6', '8x8', '10x10']"


class LiveTranscribe(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_transcribe: dict[str, Any] | list[Any] | float | str


class LiveTranslate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_translate: dict[str, Any] | list[Any] | float | str


class MessagingChannel(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    messaging: str


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
    preview_url: str
    locked: bool
    channels: AddressChannel
    created_at: str
    type: Literal["app"]


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
    display_name: str
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


class Request(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    request: dict[str, Any] | list[Any] | float | str


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
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["ai_agent"]
    ai_agent: AIAgent


class ResourceResponseCXMLApplication(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["cxml_application"]
    cxml_application: CxmlApplication


class ResourceResponseCXMLScript(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["cxml_script"]
    cxml_script: CXMLScript


class ResourceResponseCXMLWebhook(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["cxml_webhook"]
    cxml_webhook: CXMLWebhook


class ResourceResponseCallFlow(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["call_flow"]
    call_flow: CallFlow


class ResourceResponseConferenceRoom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["swml_script"]
    conference_room: ConferenceRoom


class ResourceResponseDialogFlowAgent(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["dialogflow_agent"]
    dialogflow_agent: DialogflowAgent


class ResourceResponseFSConnector(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["freeswitch_connector"]
    freeswitch_connector: FreeswitchConnector


class ResourceResponseRelayApp(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["relay_application"]
    relay_application: RelayApplication


class ResourceResponseSWMLScript(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["swml_script"]
    swml_script: SwmlScript


class ResourceResponseSWMLWebhook(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["swml_webhook"]
    swml_webhook: SWMLWebhook


class ResourceResponseSipEndpoint(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["sip_endpoint"]
    sip_endpoint: SipEndpoint


class ResourceResponseSipGateway(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
    created_at: str
    updated_at: str
    type: Literal["sip_gateway"]
    sip_gateway: SipGateway


class ResourceResponseSubscriber(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    project_id: uuid
    display_name: str
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


class ResourceSipEndpointResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    type: Literal["call"]
    cover_url: str | None
    preview_url: str | None
    channels: AddressChannel


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


class SWAIGInternalFillerUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hangup: FunctionFillersUpdate
    check_time: FunctionFillersUpdate
    wait_for_user: FunctionFillersUpdate
    wait_seconds: FunctionFillersUpdate
    adjust_response_latency: FunctionFillersUpdate
    next_step: FunctionFillersUpdate
    change_context: FunctionFillersUpdate
    get_visual_input: FunctionFillersUpdate
    get_ideal_strategy: FunctionFillersUpdate


SWAIGNativeFunction: TypeAlias = "str"


class SWAIGUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    defaults: SWAIGDefaults
    native_functions: list[SWAIGNativeFunction]
    includes: list[SWAIGIncludes]
    functions: list[SWAIGFunction]
    internal_fillers: SWAIGInternalFillerUpdate


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


SWMLMethod: TypeAlias = "AI | AiSidecar | AmazonBedrock | Answer | BindDigit | ClearDigitBindings | Cond | Connect | Denoise | DetectMachine | Dial | Echo | EnterQueue | Eval | Execute | ExecuteRpc | Goto | Hangup | If | JoinConference | JoinRoom | Label | LiveTranscribe | LiveTranslate | Pay | Play | Prompt | ReceiveFax | Record | RecordCall | Request | Return | Ring | SIPRefer | SendDigits | SendFax | SendSMS | Set | SetCapabilities | SetMeta | Sleep | StopDenoise | StopRecordCall | StopStream | StopTap | Stream | Switch | Tap | Transcribe | TranscribeStop | Transfer | Unset | UserEvent"


class SWMLObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sections: Section
    version: Literal["1.0.0"]


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


SWMLVar: TypeAlias = "str"


class SWMLWebhook(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    name: str
    used_for: Literal["calling"]
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
    used_for: Literal["calling"]
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
    used_for: Literal["calling"]
    primary_request_url: str
    primary_request_method: Literal["GET"] | Literal["POST"]
    fallback_request_url: str
    fallback_request_method: Literal["GET"] | Literal["POST"]
    status_callback_url: str
    status_callback_method: Literal["GET"] | Literal["POST"]


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


class SipEndpoint(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    username: str
    caller_id: str
    send_as: str
    ciphers: list[Ciphers]
    codecs: list[Codecs]
    encryption: Encryption
    call_handler: CallHandlerType
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

    id: uuid
    username: str
    caller_id: str
    send_as: str
    ciphers: list[Ciphers]
    codecs: list[Codecs]
    encryption: Encryption
    call_handler: CallHandlerType
    calling_handler_resource_id: uuid | None


class SipEndpointCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SipEndpointListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

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
    encryption: Encryption


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
    encryption: Encryption
    ciphers: list[Ciphers]
    codecs: list[Codecs]


class SipGatewayRequestUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    uri: str
    encryption: Encryption
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


class Subscriber(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    email: str
    first_name: str
    last_name: str
    display_name: str
    job_title: str
    timezone: str
    country: str
    region: str
    company_name: str


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


class SubscriberGuestTokenCreateResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    token: jwt
    refresh_token: jwt


class SubscriberInviteTokenCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    address_id: uuid
    expires_at: int


class SubscriberInviteTokenCreateResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    token: jwt


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
    timezone: str
    country: str
    region: str
    company_name: str


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
    caller_id: str
    send_as: str
    ciphers: list[Ciphers]
    codecs: list[Codecs]
    encryption: Encryption


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


class SwmlScript(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    id: uuid
    contents: str
    request_url: str
    display_name: str
    status_callback_url: str
    status_callback_method: Literal["POST"]


class SwmlScriptCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    contents: str
    status_callback_url: str


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
    """Open shape: extra server keys permitted; not validated at runtime."""

    display_name: str
    contents: str
    status_callback_url: str


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


UsedForType: TypeAlias = "Literal['calling', 'messaging']"


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

If = TypedDict(
    "If",
    {
        "if": "dict[str, Any] | list[Any] | float | str",
    },
    total=False,
)
If.__doc__ = """Open shape: extra server keys permitted; not validated at runtime."""


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


class Eval(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    eval: dict[str, Any]


class Echo(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    echo: dict[str, Any] | list[int | SWMLVar]


class Dial(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    dial: dict[str, Any]


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


ListFabricAddressesResponse: TypeAlias = "FabricAddressesResponse"
GetFabricAddressResponse: TypeAlias = "FabricAddress"
CreateEmbedsTokenRequest: TypeAlias = "EmbedsTokensRequest"
CreateEmbedsTokenResponse: TypeAlias = "EmbedsTokensResponse"
CreateSubscriberGuestTokenRequest: TypeAlias = "SubscriberGuestTokenCreateRequest"
CreateSubscriberGuestTokenResponse: TypeAlias = "SubscriberGuestTokenCreateResponse"
ListResourcesResponse: TypeAlias = "ResourceListResponse"
ListAiAgentsResponse: TypeAlias = "AIAgentListResponse"
CreateAiAgentRequest: TypeAlias = "AIAgentCreateRequest"
CreateAiAgentResponse: TypeAlias = "AIAgentResponse"
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
ListSipEndpointsResponse: TypeAlias = "list[SipEndpointListResponse]"
CreateSipEndpointRequest: TypeAlias = "SipEndpointCreateRequest"
CreateSipEndpointResponse: TypeAlias = "SipEndpointResponse"
AssignResourceSipEndpointRequest: TypeAlias = "ResourceSipEndpointAssignRequest"
AssignResourceSipEndpointResponse: TypeAlias = "ResourceSipEndpointResponse"
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
UpdateSubscriberRequest: TypeAlias = "SubscriberRequest"
UpdateSubscriberResponse: TypeAlias = "SubscriberResponse"
ListSubscriberAddressesResponse: TypeAlias = "list[SubscriberAddressesResponse]"
ListSwmlScriptsResponse: TypeAlias = "list[SwmlScriptListResponse]"
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
CreateSubscriberInviteTokenRequest: TypeAlias = "SubscriberInviteTokenCreateRequest"
CreateSubscriberInviteTokenResponse: TypeAlias = "SubscriberInviteTokenCreateResponse"
CreateSubscriberTokenRequest: TypeAlias = "SubscriberTokenRequest"
CreateSubscriberTokenResponse: TypeAlias = "SubscriberTokenResponse"
RefreshSubscriberTokenRequest: TypeAlias = "SubscriberRefreshTokenRequest"
RefreshSubscriberTokenResponse: TypeAlias = "SubscriberRefreshTokenResponse"
