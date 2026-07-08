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

    ai: AIObject


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
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    text: str


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
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    text: str
    contexts: Contexts


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

Action: TypeAlias = "SWMLAction | ChangeContextAction | ChangeStepAction | ContextSwitchAction | HangupAction | HoldAction | PlaybackBGAction | SayAction | SetGlobalDataAction | SetMetaDataAction | StopAction | StopPlaybackBGAction | ToggleFunctionsAction | UnsetGlobalDataAction | UnsetMetaDataAction | UserInputAction"

AddressChannel: TypeAlias = "AudioChannel | MessagingChannel | VideoChannel"


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


class AudioChannel(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    audio: str


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

CallStatus: TypeAlias = "Literal['created', 'ringing', 'answered', 'ended']"


class ChangeContextAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    change_context: str


class ChangeStepAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    change_step: str


Ciphers: TypeAlias = "Literal['AEAD_AES_256_GCM_8', 'AES_256_CM_HMAC_SHA1_80', 'AES_CM_128_HMAC_SHA1_80', 'AES_256_CM_HMAC_SHA1_32', 'AES_CM_128_HMAC_SHA1_32']"

Codecs: TypeAlias = "Literal['PCMU', 'PCMA', 'G722', 'G729', 'OPUS', 'VP8', 'H264']"


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
    """A message object representing a single turn in the conversation history.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    role: ConversationRole
    content: str
    lang: str


ConversationRole: TypeAlias = "Literal['user', 'assistant', 'system']"

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

    output: Output
    expressions: list[Expression]
    webhooks: list[Webhook]


class Denoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    denoise: dict[str, Any]


class DetectMachine(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    detect_machine: dict[str, Any]


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


Direction: TypeAlias = "Literal['inbound', 'outbound']"

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


FunctionFillers: TypeAlias = "dict[str, Any]"

FunctionFillersUpdate: TypeAlias = "dict[str, Any]"


class FunctionParameters(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["object"]
    properties: dict[str, Any]
    required: list[str]


class Goto(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    goto: dict[str, Any]


class GuestTokenCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


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


class InviteTokenCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


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


Layout: TypeAlias = "Literal['grid-responsive', 'grid-responsive-mobile', 'highlight-1-responsive', '1x1', '2x1', '2x2', '5up', '3x3', '4x4', '5x5', '6x6', '8x8', '10x10']"


class LiveTranscribe(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_transcribe: dict[str, Any]


class LiveTranslate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_translate: dict[str, Any]


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

    request: dict[str, Any]


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


SWAIGNativeFunction: TypeAlias = (
    "Literal['check_time', 'wait_seconds', 'wait_for_user', 'adjust_response_latency']"
)


class SWAIGUpdate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    defaults: SWAIGDefaults
    native_functions: list[SWAIGNativeFunction]
    includes: list[SWAIGIncludes]
    functions: list[SWAIGFunction]
    internal_fillers: SWAIGInternalFillerUpdate


class SWMLAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: SWMLObject


SWMLMethod: TypeAlias = "Answer | AI | AmazonBedrock | Cond | Connect | Denoise | EnterQueue | Execute | Goto | Label | LiveTranscribe | LiveTranslate | Hangup | JoinRoom | JoinConference | Play | Prompt | ReceiveFax | Record | RecordCall | Request | Return | SendDigits | SendFax | SendSMS | Set | Sleep | SIPRefer | StopDenoise | StopRecordCall | StopTap | Switch | Tap | Transfer | Unset | Pay | DetectMachine | UserEvent"


class SWMLObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    version: Literal["1.0.0"]
    sections: Section


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

    unset: str | list[str]


class UnsetGlobalDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    unset_global_data: str | dict[str, Any]


class UnsetMetaDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    unset_meta_data: str | dict[str, Any]


UsedForType: TypeAlias = "Literal['calling', 'messaging']"


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


class VideoChannel(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    video: str


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


jwt: TypeAlias = "str"

play_url: TypeAlias = "str"

uuid: TypeAlias = "str"

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
