# AUTO-GENERATED from porting-sdk/schema.json — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# Typed SWML verb surface: one <Verb>Config TypedDict per verb + a _SwmlVerbs
# Protocol declaring each verb method (config -> Self). SwmlBuilder installs these
# verbs dynamically from schema.json at runtime; this static surface lets the type
# checker SEE them (mirrors the TS SwmlVerbMethods.generated.ts augmentation).
# STATIC-ONLY: configs are plain dicts at runtime, never validated.
from __future__ import annotations
from collections.abc import Mapping
from typing import Any, Literal, TypeAlias, TypedDict
from typing import TypeVar

_Self = TypeVar("_Self", bound="_SwmlVerbs")


class AI(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai: AiConfig | list[str | SWMLVar] | float | str | SWMLVar


class AiSidecar(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai_sidecar: AiSidecarConfig | list[Any] | float | str


class AmazonBedrock(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    amazon_bedrock: AmazonBedrockConfig | list[Any] | float | str


class Answer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    answer: AnswerConfig | list[float | SWMLVar] | float | SWMLVar


class CallDeviceStream(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    authorization_bearer_token: str
    codec: str
    custom_parameters: Any
    name: str
    realtime: bool
    status_url: str
    status_url_method: Literal["GET", "POST"]
    url: str


class CallPayParameters(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    value: str


class CallPayPrompts(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    actions: list[CallPayPromptsActions]
    attempt: str
    card_type: str
    error_type: str
    # non-identifier field 'for': Literal['payment-card-number', 'expiration-date', 'security-code', 'postal-code', 'bank-routing-number', 'bank-account-number', 'payment-processing', 'payment-completed', 'payment-failed', 'payment-canceled']
    play: list[RingbackConfig]
    require_matching_inputs: str


class CallPayPromptsActions(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["Say", "Play"]
    phrase: str


class Cond(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    cond: list[CondItem]


class Connect(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    connect: ConnectConfig


class ConnectDevice(TypedDict, total=False):
    """Body shape enforced by CHECK_swml_connect_device, swml_schema.c.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    authorization_bearer_token: str | SWMLVar
    call_state_events: list[str] | SWMLVar
    call_state_url: str | SWMLVar
    codec: str | SWMLVar
    codecs: str | list[Any]
    confirm: str | list[SWMLMethod] | ConnectDeviceConfirm | SWMLVar
    confirm_timeout: int | SWMLVar
    custom_parameters: dict[str, str] | SWMLVar
    encryption: Literal["mandatory", "optional", "forbidden"] | SWMLVar
    # non-identifier field 'from': str | SWMLVar
    from_name: str | SWMLVar
    fsvars: dict[str, str] | SWMLVar
    headers: list[ConnectSipHeader]
    name: str | SWMLVar
    password: str | SWMLVar
    realtime: bool | SWMLVar
    session_timeout: int | SWMLVar
    status_url: str | SWMLVar
    status_url_method: Literal["GET", "POST"] | SWMLVar
    timeout: int | SWMLVar
    to: str | SWMLVar
    username: str | SWMLVar
    webrtc_media: bool | SWMLVar


ConnectSerialParallel: TypeAlias = "list[ConnectDevice]"


class ConnectSipHeader(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    value: str | SWMLVar


class DataMap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    contexts: Any
    expressions: list[Expression] | Expression
    output: Any
    webhooks: list[Webhook] | Webhook


class Denoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    denoise: dict[str, Any] | list[Any] | float | str


class DetectMachine(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    detect_machine: DetectMachineConfig | list[Any] | float | str


class Echo(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    echo: EchoConfig | list[int | SWMLVar] | int | SWMLVar


class EnterQueue(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    enter_queue: EnterQueueConfig | list[Any] | float | str


class Execute(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    execute: ExecuteConfig | list[str | SWMLVar] | float | str | SWMLVar


class ExecuteRpc(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    execute_rpc: ExecuteRpcConfig | list[Any] | float | str


class Expression(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    pattern: str
    expr: str
    # non-identifier field 'nomatch-output': Any
    output: Any
    string: str


class Foreach(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    append: str
    input_key: str
    max: Any
    output_key: str


class Goto(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    goto: GotoConfig | list[str | SWMLVar] | float | str | SWMLVar


class Hangup(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hangup: (
        HangupConfig
        | list[
            Literal["hangup", "cancel", "busy", "noAnswer", "decline", "error"]
            | SWMLVar
        ]
        | float
        | Literal["hangup", "cancel", "busy", "noAnswer", "decline", "error"]
        | SWMLVar
    )


class JoinConference(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    join_conference: JoinConferenceConfig | list[str | SWMLVar] | float | str | SWMLVar


class JoinRoom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    join_room: JoinRoomConfig | list[str | SWMLVar] | float | str | SWMLVar


class JsonSchema(TypedDict, total=False):
    """A JSON Schema (draft 2020-12). The value is forwarded verbatim to the receiving tool-call API, which owns this contract; the engine does not inspect it.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    title: str
    description: str
    type: (
        Literal["array", "boolean", "integer", "null", "number", "object", "string"]
        | list[
            Literal["array", "boolean", "integer", "null", "number", "object", "string"]
        ]
    )
    const: Any
    enum: list[Any]
    format: str
    pattern: str
    minimum: float
    maximum: float
    exclusiveMinimum: float
    exclusiveMaximum: float
    minLength: int
    maxLength: int
    minItems: int
    maxItems: int
    minProperties: int
    maxProperties: int
    default: Any
    examples: list[Any]
    deprecated: bool
    properties: dict[str, JsonSchema | bool]
    required: list[str]
    prefixItems: list[JsonSchema | bool]
    items: JsonSchema | bool
    propertyNames: JsonSchema | bool
    additionalProperties: JsonSchema | bool
    unevaluatedProperties: JsonSchema | bool
    oneOf: list[JsonSchema | bool]
    anyOf: list[JsonSchema | bool]
    allOf: list[JsonSchema | bool]
    # non-identifier field 'not': JsonSchema | bool
    contains: JsonSchema | bool
    dependentRequired: dict[str, list[str]]
    dependentSchemas: dict[str, JsonSchema | bool]
    # non-identifier field 'else': JsonSchema | bool
    # non-identifier field 'if': JsonSchema | bool
    maxContains: int
    minContains: int
    multipleOf: float
    patternProperties: dict[str, JsonSchema | bool]
    readOnly: bool
    then: JsonSchema | bool
    unevaluatedItems: JsonSchema | bool
    uniqueItems: bool
    writeOnly: bool


class Label(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    label: LabelConfig | list[str] | float | str


class LiveTranscribe(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_transcribe: LiveTranscribeConfig | list[Any] | float | str


class LiveTranslate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_translate: LiveTranslateConfig | list[Any] | float | str


class Pay(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    pay: PayConfig | list[Any | Literal["dtmf", "voice"] | SWMLVar] | float | str


class Play(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    play: PlayConfig | list[str] | float | str


class Prompt(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    prompt: PromptConfig | list[str | int | SWMLVar | float] | float | str


class ReceiveFax(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    receive_fax: ReceiveFaxConfig | list[str | SWMLVar] | float | str | SWMLVar


class Record(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    record: RecordConfig | list[Any] | float | str


class RecordCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    record_call: RecordCallConfig | list[Any] | float | str


class Request(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    request: RequestConfig | list[Any] | float | str


class Return(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'return': dict[str, Any] | list[Any] | bool | None | float | str


class Ring(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ring: dict[str, Any] | list[Any] | float | str


class RingbackConfig(TypedDict, total=False):
    """Declared as a named $defs entry so every generator emits a TYPED shape via $ref rather than collapsing an inline object to an untyped map.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    url: str
    urls: list[str]
    volume: float | SWMLVar


class SIPRefer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sip_refer: SipReferConfig | list[str | SWMLVar] | float | str | SWMLVar


SWMLMethod: TypeAlias = "AI | AiSidecar | AmazonBedrock | Answer | Cond | Connect | Denoise | DetectMachine | Echo | EnterQueue | Execute | ExecuteRpc | Goto | Hangup | JoinConference | JoinRoom | Label | LiveTranscribe | LiveTranslate | Pay | Play | Prompt | ReceiveFax | Record | RecordCall | Request | Return | Ring | SIPRefer | SendDigits | SendFax | SendSMS | Set | SetMeta | Sleep | StopDenoise | StopRecordCall | StopStream | StopTap | Stream | Switch | Tap | Transcribe | TranscribeStop | Transfer | Unset | UserEvent"


SWMLVar: TypeAlias = "str"


class Section(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    main: list[SWMLMethod]


class SendDigits(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_digits: SendDigitsConfig | list[str | SWMLVar] | float | str | SWMLVar


class SendFax(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_fax: SendFaxConfig | list[str | SWMLVar] | float | str | SWMLVar


class SendSMS(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_sms: SendSmsConfig


class Set(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set: dict[str, Any]


class SetMeta(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set_meta: SetMetaConfig | list[Any] | float | str


class Sleep(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sleep: SleepConfig | list[int | SWMLVar] | int | SWMLVar


class StopDenoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_denoise: dict[str, Any] | list[Any] | float | str


class StopRecordCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_record_call: StopRecordCallConfig | list[str | SWMLVar] | float | str | SWMLVar


class StopStream(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_stream: StopStreamConfig | list[Any | SWMLVar] | float | str | SWMLVar


class StopTap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_tap: StopTapConfig | list[Any | SWMLVar] | float | str | SWMLVar


class Stream(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stream: StreamConfig | list[str | SWMLVar] | float | str | SWMLVar


class Switch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    switch: SwitchConfig | list[Any] | float | str


class Tap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    tap: (
        TapConfig
        | list[str | SWMLVar | Literal["listen", "speak", "both"]]
        | float
        | str
        | SWMLVar
    )


class Transcribe(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    transcribe: TranscribeConfig | list[Any] | float | str


class TranscribeStop(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    transcribe_stop: dict[str, Any] | list[Any] | float | str


class Transfer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    transfer: TransferConfig | list[str | SWMLVar] | float | str | SWMLVar


class Unset(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    unset: list[str] | str


class UserEvent(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    user_event: UserEventConfig | list[Any] | float | str


class Webhook(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    error_keys: list[Any]
    expressions: Expression | dict[str, Any]
    foreach: Foreach | dict[str, Any]
    form_param: str
    headers: Any
    input_args_as_params: bool
    method: str
    output: Any
    params: Any
    require_args: Any
    url: str


class AiConfig(TypedDict, total=False):
    """Creates an AI agent that conducts voice conversations using automatic speech recognition (ASR),

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    SWAIG: list[AiSWAIGItem] | AiSWAIG
    agent: str | SWMLVar
    engine: str | SWMLVar
    global_data: dict[str, Any]
    hints: list[AiHintsItem | str]
    languages: list[AiLanguagesItem]
    multilingual: AiMultilingual
    params: AiParams
    post_prompt: AiPostPrompt
    post_prompt_auth_password: str | SWMLVar
    post_prompt_auth_user: str | SWMLVar
    post_prompt_url: str | SWMLVar
    prompt: AiPrompt
    pronounce: list[AiPronounceItem]
    voice: str | SWMLVar


class AiSWAIGItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    active: bool | float | str
    argument: dict[str, Any]
    data_map: DataMap
    fillers: dict[str, Any]
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: dict[str, Any]
    purpose: str
    skip_fillers: bool | str
    wait_file: str
    wait_file_loops: float | str
    wait_for_fillers: bool | str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class AiSWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    defaults: dict[str, Any]
    functions: list[AiSWAIGFunctionsItem]
    hooks: list[AiSWAIGHooksItem]
    includes: list[AiSWAIGIncludesItem]
    internal_fillers: dict[str, Any]
    mcp_servers: list[AiSWAIGMcpServersItem]
    native_functions: list[Any]


class AiSWAIGFunctionsItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    active: bool | float | str
    argument: JsonSchema
    data_map: DataMap
    fillers: dict[str, Any]
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: JsonSchema
    purpose: str
    skip_fillers: bool | str
    wait_file: str
    wait_file_loops: float | str
    wait_for_fillers: bool | str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class AiSWAIGHooksItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    active: bool | float | str
    argument: dict[str, Any]
    data_map: DataMap
    fillers: dict[str, Any]
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: dict[str, Any]
    purpose: str
    skip_fillers: bool | str
    wait_file: str
    wait_file_loops: float | str
    wait_for_fillers: bool | str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class AiSWAIGIncludesItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    auth_password: str
    auth_user: str
    functions: list[Any]
    meta_data: dict[str, Any]
    url: str


class AiSWAIGMcpServersItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    headers: dict[str, Any]
    resource_vars: dict[str, Any]
    resources: bool | str
    url: str


class AiHintsItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    pattern: str
    hint: str
    ignore_case: bool | str
    replace: str


class AiLanguagesItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    auto_emotion: bool | str
    auto_speed: bool | str
    code: list[Any] | str
    double_turn_fillers: list[Any]
    engine: str
    fillers: list[Any] | dict[str, Any]
    function_fillers: list[Any] | dict[str, Any]
    listen_language: list[Any] | str
    model: str
    name: str
    params: AiLanguagesItemParams
    pronounce: list[Any]
    speech_fillers: list[Any] | dict[str, Any]
    turn_fillers: list[Any]
    voice: str


class AiLanguagesItemParams(TypedDict, total=False):
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


class AiMultilingual(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    allowed: list[Any]
    engine: str
    fillers: list[Any] | dict[str, Any]
    function_fillers: list[Any] | dict[str, Any]
    languages: list[Any]
    min_switch_words: float
    model: str
    provider: str
    start_language: str
    turn_fillers: list[Any] | dict[str, Any]


class AiParams(TypedDict, total=False):
    """An object of any necessary parameters for the API call. The key is the parameter name and the value is the parameter value.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    acknowledge_interruptions: (
        int
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
        | bool
    )
    acoustic_eot_gate_prob: float | str
    acoustic_eot_trust_prob: float | str
    ai_model: str
    ai_name: str
    ai_volume: int | str
    app_name: str
    asr_diarize: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    asr_params: dict[str, Any]
    asr_smart_format: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    asr_speaker_affinity: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    attention_escalate_prompt: str
    attention_timeout: int | str
    attention_timeout_prompt: str
    auth_token: str
    auto_correct: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    azure_stream_first: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    azure_tts_key: str
    background_file: str
    background_file_loops: int | str
    background_file_volume: int | str
    barge_functions: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    barge_match_string: str
    barge_min_words: int | str
    bill_all_tts: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    cache: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    call_uuid: str
    cartesia_key: str
    cartesia_model: str
    cartesia_stream_first: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    confidence: float | str
    conscience: Literal["false", "true"]
    conversation_id: str
    conversation_sliding_window: int | str
    convo: list[AiParamsConvoItem]
    debug_webhook_level: int | str
    debug_webhook_url: str
    deepgram_key_override: str
    deepgram_stream_first: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    deepgram_tts_key: str
    deepgram_url_override: str
    developer_prompt: str
    digit_terminators: str
    digit_timeout: int | str
    direction: Literal["inbound", "outbound"]
    double_turn_filler_every_n: float | str
    double_turn_filler_min_ms: float | str
    double_turn_model: str
    double_turn_prompt: str
    double_turn_wait_ms: float | str
    double_turns: (
        bool
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    eleven_labs_key: str
    eleven_labs_model: Literal[
        "eleven_english_v2",
        "eleven_flash_v2_5",
        "eleven_multilingual_v1",
        "eleven_multilingual_v2",
        "eleven_turbo_v2",
        "eleven_turbo_v2_5",
        "eleven_v3",
        "multilingual",
    ]
    eleven_labs_similarity: float | str
    eleven_labs_stability: float | str
    eleven_labs_stream_first: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    enable_barge: (
        Literal[
            "0",
            "1",
            "active",
            "all",
            "allow",
            "enabled",
            "false",
            "on",
            "t",
            "true",
            "yes",
        ]
        | bool
    )
    enable_inner_dialog: (
        bool
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    enable_pause: (
        bool
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    enable_text_normalization: Literal[
        "both", "false", "heard", "none", "off", "on", "spoken", "true"
    ]
    enable_thinking: (
        bool
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    enable_turn_detection: (
        bool
        | Literal[
            "0",
            "1",
            "acoustic_only",
            "both",
            "false",
            "off",
            "punct_only",
            "punctuation_only",
            "true",
        ]
    )
    enable_vision: (
        bool
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
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
    function_wait_for_talking: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    functions_on_no_response: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    grok_key: str
    groq_tts_key: str
    hard_stop_prompt: str
    hard_stop_time: str
    hold_music: str
    hold_on_process: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    inactivity_timeout: int | str
    initial_sleep_ms: int | str
    inner_dialog: AiParamsInnerDialog
    inner_dialog_model: str
    inner_dialog_prompt: str
    inner_dialog_scorecard: bool
    input_poll_freq: int | str
    interrupt_on_noise: (
        int
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
        | bool
    )
    interrupt_prompt: str
    inworld_apikey: str
    inworld_key: str
    inworld_model: str
    language: str
    languages_enabled: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    lipsync_debug: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    llm_diarize_aware: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
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
    openai_azure: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    openai_gcloud_version: str
    openai_stream_first: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    openai_tts_key: str
    openai_tts_url: str
    outbound_attention_timeout: int | str
    pcm_channels: int | str
    pcm_rate: int | str
    persist_global_data: (
        bool
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    pom_format: Literal["markdown", "xml"]
    provider: str
    pvt_params: str
    realtime: dict[str, Any]
    redact_prompt: str
    rime_apikey: str
    rime_key: str
    rime_model: str
    rime_stream_first: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    sample_rate: int | str
    save_conversation: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    send_single_llm_response: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    similarity: float | str
    smallest_key: str
    smallest_model: str
    speak_when_spoken_to: (
        bool
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    speaker: str
    speech_event_timeout: int | str
    speech_gen_quick_stops: int | str
    speech_timeout: int | str
    speechify_key: str
    speechify_loudness_normalization: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    speechify_model: str
    speechify_output_format: str
    speechify_stream_first: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    speechify_text_normalization: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    speed: float | str
    stability: float | str
    start_paused: (
        bool
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    static_greeting: str
    static_greeting_no_barge: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    stream_first: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    streaming: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    strict_mode: str
    summary_mode: Literal["original", "string"]
    swaig_allow_settings: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    swaig_allow_swml: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    swaig_post_conversation: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    swaig_post_swml_vars: (
        list[str]
        | bool
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    swaig_set_global_data: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    target_first_segment_ms: int | str
    text_normalization_far_dir: str
    thinking_model: str
    tool_result_distill: bool | dict[str, Any]
    transfer_summary: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    transparent_barge: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    transparent_barge_max_time: int | str
    tts_number_format: Literal["e.164", "e164", "generic", "international", "national"]
    turn_detection: (
        bool
        | Literal[
            "0",
            "1",
            "acoustic_only",
            "both",
            "false",
            "off",
            "punct_only",
            "punctuation_only",
            "true",
        ]
    )
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
    video_scale: Literal["1080p", "480p", "720p", "native"]
    video_talking_file: str
    vision_model: str
    voice_name: str
    vol: int | str
    wait_for_user: (
        bool
        | float
        | Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
    )
    wake_prefix: str


class AiParamsConvoItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    content: str
    lang: str
    role: str
    tool_call_id: str
    tool_calls: list[Any]


class AiParamsInnerDialog(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWAIG: dict[str, Any]


class AiPostPrompt(TypedDict, total=False):
    """The final set of instructions and configuration settings to send to the agent.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[AiPostPromptPomItem]
    reasoning_effort: str
    temperature: float
    text: str
    top_p: float
    verbosity: str


class AiPostPromptPomItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    title: str
    body: str
    bullets: list[Any]
    numbered: bool
    numberedBullets: bool
    subsections: list[Any]


class AiPrompt(TypedDict, total=False):
    """Defines the AI agent's personality, goals, behaviors, and instructions for handling conversations.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    contexts: dict[str, Any]
    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[AiPromptPomItem]
    reasoning_effort: str
    steps: list[AiPromptStepsItem]
    temperature: float
    text: str
    top_p: float
    verbosity: str


class AiPromptPomItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    title: str
    body: str
    bullets: list[Any]
    numbered: bool
    numberedBullets: bool
    subsections: list[Any]


class AiPromptStepsItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    end: bool | str
    gather_info: dict[str, Any]
    instructions: str
    name: str
    pom: list[Any]
    reset: dict[str, Any]
    skip_to_next_step: bool | str
    skip_user_turn: bool | str
    step_criteria: str
    text: str
    valid_contexts: list[Any]
    valid_steps: list[Any]


class AiPronounceItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ignore_case: bool | float | str
    replace: str
    # non-identifier field 'with': str


class AiSidecarConfig(TypedDict, total=False):
    """Start ai_sidecar mode — live_transcribe with an LLM/SWAIG/MCP loop on top.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    SWAIG: AiSidecarSWAIG | SWMLVar
    action: dict[str, Any] | SWMLVar
    customer_role: Literal["remote-caller", "local-caller"] | SWMLVar
    direction: list[Literal["remote-caller", "local-caller"]] | SWMLVar
    global_data: dict[str, Any] | SWMLVar
    hints: list[str] | SWMLVar
    lang: str | SWMLVar
    model: str | SWMLVar
    params: AiSidecarParams | SWMLVar
    permissions: AiSidecarPermissions | SWMLVar
    prompt: AiSidecarPrompt | str | SWMLVar
    url: str | SWMLVar


class AiSidecarSWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    defaults: dict[str, Any]
    functions: list[AiSidecarSWAIGFunctionsItem]
    mcp_servers: list[Any]


class AiSidecarSWAIGFunctionsItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    function: str
    parameters: JsonSchema
    purpose: str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class AiSidecarParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    act_on_channel: bool
    ai_summary: bool
    ai_summary_prompt: str
    debug: bool
    debug_level: int
    deepgram_key_override: str
    deepgram_url_override: str
    final_summary: bool
    idle_timeout_ms: int
    live_events: bool
    max_history_tokens: int
    max_iters_per_tick: int
    min_interval_ms: int
    speech_engine: Literal["deepgram", "google"]
    speech_timeout: int
    summary_model: str
    transcribe_prompt: str
    vad_silence_ms: int
    vad_thresh: int
    verbose_utterances: bool


class AiSidecarPermissions(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    swaig_allow_settings: bool
    swaig_allow_swml: bool
    swaig_set_global_data: bool


class AiSidecarPrompt(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    file: str


class AmazonBedrockConfig(TypedDict, total=False):
    """Creates a new Bedrock AI Agent

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    SWAIG: AmazonBedrockSWAIG
    app_name: str
    assistant_name: str
    assistant_prompt: str
    conversation_id: str
    global_data: dict[str, Any]
    greeting_prompt: AmazonBedrockGreetingPrompt
    params: AmazonBedrockParams
    post_prompt: AmazonBedrockPostPrompt
    post_prompt_url: str
    prompt: AmazonBedrockPrompt
    transcript_webhook_url: str


class AmazonBedrockSWAIG(TypedDict, total=False):
    """An object holding the user-defined functions/endpoints that can be executed during the dialogue. The engine reads two keys off it: `functions`, the array of function definitions, and `defaults`, an object of settings applied to each of them.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    defaults: dict[str, Any]
    functions: list[AmazonBedrockSWAIGFunctionsItem]


class AmazonBedrockSWAIGFunctionsItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    description: str
    data_map: dict[str, Any]
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: dict[str, Any]
    web_hook_url: str


class AmazonBedrockGreetingPrompt(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    role: str
    text: str


class AmazonBedrockParams(TypedDict, total=False):
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


class AmazonBedrockPostPrompt(TypedDict, total=False):
    """The final set of instructions and configuration settings to send to the agent.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    pom: list[Any]
    text: str


class AmazonBedrockPrompt(TypedDict, total=False):
    """Establishes the initial set of instructions and settings to configure the agent.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    pom: list[Any]
    temperature: float | str
    text: str
    top_p: float | str
    voice_id: str


class AnswerConfig(TypedDict, total=False):
    """Answer incoming call and set an optional maximum duration.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    codecs: (
        str
        | list[Literal["PCMU", "PCMA", "OPUS", "G722", "G729", "AMR-WB", "VP8", "H264"]]
        | SWMLVar
    )
    fsvars: dict[str, str] | SWMLVar
    max_duration: float | SWMLVar
    password: str | SWMLVar
    username: str | SWMLVar


class CondItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'else': list[Any]
    then: list[Any]
    when: str


class ConnectConfig(TypedDict, total=False):
    """Dial a SIP URI or phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    answer_on_bridge: bool | str | SWMLVar
    authorization_bearer_token: str | SWMLVar
    call_state_events: list[str] | SWMLVar
    call_state_url: str | SWMLVar
    codec: str | SWMLVar
    codecs: str | list[Any] | SWMLVar
    confirm: str | list[SWMLMethod] | ConnectConfirm | SWMLVar
    confirm_timeout: int | SWMLVar
    custom_parameters: dict[str, str] | SWMLVar
    encryption: Literal["mandatory", "optional", "forbidden"] | SWMLVar
    execute_after_queue: str | SWMLVar
    # non-identifier field 'from': str | SWMLVar
    from_name: str | SWMLVar
    fsvars: dict[str, str] | SWMLVar
    headers: list[ConnectSipHeader]
    max_duration: float | SWMLVar
    name: str | SWMLVar
    parallel: list[ConnectDevice]
    password: str | SWMLVar
    realtime: bool | SWMLVar
    result: list[Any] | dict[str, Any]
    ringback: bool | str | list[RingbackConfig] | Play
    serial: list[ConnectDevice]
    serial_parallel: list[ConnectSerialParallel]
    session_timeout: int | SWMLVar
    status_url: str | SWMLVar
    status_url_method: Literal["GET", "POST"] | SWMLVar
    stop_all_on_reject: list[Any] | bool | str | SWMLVar
    timeout: int | SWMLVar
    to: str | SWMLVar
    username: str | SWMLVar
    webrtc_media: bool | SWMLVar


class ConnectConfirm(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: Any
    meta: Any


class ConnectDeviceConfirm(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: Any
    meta: Any


class DetectMachineConfig(TypedDict, total=False):
    """A detection method that combines AMD (Answering Machine Detection) and fax detection.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    detect_interruptions: bool | SWMLVar
    detect_message_end: bool | SWMLVar
    detectors: str | SWMLVar
    end_silence_timeout: float | SWMLVar
    initial_timeout: float | SWMLVar
    machine_ready_timeout: float | SWMLVar
    machine_voice_threshold: float | SWMLVar
    machine_words_threshold: int | SWMLVar
    status_url: str | SWMLVar
    timeout: float | SWMLVar
    tone: Literal["CNG", "CED", "cng", "ced"] | SWMLVar
    wait: bool | SWMLVar


class EchoConfig(TypedDict, total=False):
    """Echo audio back to the caller.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    timeout: int | SWMLVar


class EnterQueueConfig(TypedDict, total=False):
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


class ExecuteConfig(TypedDict, total=False):
    """Execute a specified section or URL as a subroutine, and upon completion, return to the current document.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    dest: str | SWMLVar
    meta: dict[str, Any]
    on_return: list[SWMLMethod] | ExecuteOnReturn
    params: dict[str, Any] | SWMLVar
    result: list[Any] | dict[str, Any]


class ExecuteOnReturn(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: Any
    meta: Any


class ExecuteRpcConfig(TypedDict, total=False):
    """Execute a remote procedure call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str | SWMLVar
    method: str | SWMLVar
    node_id: str | SWMLVar
    params: dict[str, Any] | SWMLVar


class GotoConfig(TypedDict, total=False):
    """Jump to a label within the current section, optionally based on a condition.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    label: str | SWMLVar
    max: int | SWMLVar
    when: str | SWMLVar


class HangupConfig(TypedDict, total=False):
    """End the call with an optional reason.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    reason: (
        Literal["hangup", "cancel", "busy", "noAnswer", "decline", "error"] | SWMLVar
    )


class JoinConferenceConfig(TypedDict, total=False):
    """Join an ad-hoc audio conference started on either the SignalWire or Compatibility API.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    beep: Literal["true", "false", "onEnter", "onExit"] | SWMLVar
    coach: str | SWMLVar
    emit_call_quality: bool | SWMLVar
    end_on_exit: bool | SWMLVar
    max_participants: int | SWMLVar
    meta: JoinConferenceMeta | SWMLVar
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


class JoinConferenceMeta(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    private: Any
    public: Any


class JoinRoomConfig(TypedDict, total=False):
    """Join a RELAY room. If the room doesn't exist, it creates a new room.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str | SWMLVar


class LabelConfig(TypedDict, total=False):
    """Mark any point of the SWML section with a label so that goto can jump to it.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    label: str


class LiveTranscribeConfig(TypedDict, total=False):
    """Start live transcription of the call. The transcription will be sent to the specified webhook URL.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    action: Literal["start", "stop", "summarize"] | LiveTranscribeAction | SWMLVar
    hints: list[LiveTranscribeHintsItem | str] | SWMLVar


class LiveTranscribeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    start: LiveTranscribeActionStart
    stop: Any
    summarize: LiveTranscribeActionSummarize


class LiveTranscribeActionStart(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai_summary: bool
    ai_summary_prompt: str
    debug_level: int
    deepgram_key_override: str
    deepgram_url_override: str
    direction: list[str]
    hints: list[str]
    lang: str
    live_events: bool
    speech_engine: Literal["deepgram", "google"]
    speech_timeout: int
    vad_silence_ms: int
    vad_thresh: int
    verbose_utterances: bool
    webhook: str


class LiveTranscribeActionSummarize(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai_model: str
    prompt: str
    summary_prompt: str
    webhook: str


class LiveTranscribeHintsItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    pattern: str
    hint: str
    ignore_case: bool | str
    replace: str


class LiveTranslateConfig(TypedDict, total=False):
    """Start live translation of the call. The translation will be sent to the specified webhook URL.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    action: (
        Literal["inject", "start", "stop", "summarize"] | LiveTranslateAction | SWMLVar
    )


class LiveTranslateAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    inject: LiveTranslateActionInject
    start: LiveTranslateActionStart
    stop: Any
    summarize: LiveTranslateActionSummarize


class LiveTranslateActionInject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    direction: str
    message: str


class LiveTranslateActionStart(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai_summary: bool
    ai_summary_prompt: str
    debug_level: int
    deepgram_key_override: str
    deepgram_url_override: str
    direction: list[str]
    filter_from: str
    filter_to: str
    from_lang: str
    from_voice: str
    from_voice_params: dict[str, Any]
    live_events: bool
    mode: str
    speech_engine: Literal["deepgram", "google"]
    speech_timeout: int
    to_lang: str
    to_voice: str
    to_voice_params: dict[str, Any]
    translation_model: str
    translation_model_params: dict[str, Any]
    vad_silence_ms: int
    vad_thresh: int
    webhook: str


class LiveTranslateActionSummarize(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    prompt: str
    summary_prompt: str
    webhook: str


class PayConfig(TypedDict, total=False):
    """Enables secure payment processing during voice calls. When implemented, it manages the entire payment flow

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str | SWMLVar
    bank_account_type: (
        Literal["consumer-checking", "consumer-savings", "commercial-checking"]
        | SWMLVar
    )
    charge_amount: str | SWMLVar
    currency: str | SWMLVar
    input: Literal["dtmf", "voice"] | SWMLVar
    language: str | SWMLVar
    max_attempts: str | SWMLVar
    min_postal_code_length: str | SWMLVar
    parameters: list[CallPayParameters] | SWMLVar
    payment_connector_url: str | SWMLVar
    payment_method: Literal["credit-card", "ach-debit"] | SWMLVar
    postal_code: (
        Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
        | SWMLVar
    )
    prompts: list[CallPayPrompts] | SWMLVar
    say_voice: str | SWMLVar
    security_code: (
        Literal[
            "0", "1", "active", "allow", "enabled", "false", "on", "t", "true", "yes"
        ]
        | SWMLVar
    )
    status_url: str | SWMLVar
    timeout: str | SWMLVar
    token_type: Literal["one-time", "reusable"] | SWMLVar
    valid_card_types: str | SWMLVar
    voice: str | SWMLVar


class PlayConfig(TypedDict, total=False):
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
    url: str
    urls: list[str]
    volume: float | SWMLVar


class PromptConfig(TypedDict, total=False):
    """Play a prompt and wait for input. The input can be received either as digits from the keypad,

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    digit_timeout: float | SWMLVar
    initial_timeout: float | SWMLVar
    max_digits: int | SWMLVar
    play: Play | list[RingbackConfig] | str
    say_gender: Literal["male", "female"] | SWMLVar
    say_language: str | SWMLVar
    say_voice: str | SWMLVar
    speech_end_timeout: float | SWMLVar
    speech_engine: Literal["Google", "Google.V2", "Deepgram"] | SWMLVar
    speech_hints: list[str]
    speech_language: str | SWMLVar
    speech_timeout: float | SWMLVar
    status_url: str | SWMLVar
    terminators: str | SWMLVar
    url: str
    volume: float | SWMLVar


class ReceiveFaxConfig(TypedDict, total=False):
    """Receive a fax being delivered to this call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    status_url: str | SWMLVar


class RecordConfig(TypedDict, total=False):
    """Record the call audio in the foreground, pausing further SWML execution until recording ends.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    format: Literal["wav", "mp3", "mp4"] | SWMLVar
    beep: bool | SWMLVar
    direction: Literal["listen", "speak", "both"] | SWMLVar
    end_silence_timeout: float | SWMLVar
    initial_timeout: float | SWMLVar
    input_sensitivity: float | SWMLVar
    max_length: int | SWMLVar
    status_url: str | SWMLVar
    stereo: bool | SWMLVar
    terminators: str | SWMLVar


class RecordCallConfig(TypedDict, total=False):
    """Record call in the background.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    format: Literal["wav", "mp3", "mp4"] | SWMLVar
    beep: bool | SWMLVar
    control_id: str | SWMLVar
    direction: Literal["listen", "speak", "both"] | SWMLVar
    end_silence_timeout: float | SWMLVar
    initial_timeout: float | SWMLVar
    input_sensitivity: float | SWMLVar
    max_length: int | SWMLVar
    status_url: str | SWMLVar
    stereo: bool | SWMLVar
    terminators: str | SWMLVar


class RequestConfig(TypedDict, total=False):
    """Send a GET, POST, PUT, or DELETE request to a remote URL.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    body: dict[str, Any] | list[Any] | str | float | bool
    connect_timeout: int | SWMLVar
    headers: dict[str, Any]
    method: (
        Literal["get", "GET", "put", "PUT", "POST", "post", "DELETE", "delete"]
        | SWMLVar
    )
    save_variables: bool | SWMLVar
    timeout: int | SWMLVar
    url: str | SWMLVar


class SipReferConfig(TypedDict, total=False):
    """Send SIP REFER to a SIP call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    password: str | SWMLVar
    status_url: str | SWMLVar
    to: str | SWMLVar
    to_uri: str | SWMLVar
    username: str | SWMLVar


class SendDigitsConfig(TypedDict, total=False):
    """Send digit presses as DTMF tones.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    digits: str | SWMLVar


class SendFaxConfig(TypedDict, total=False):
    """Send a fax.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    document: str | SWMLVar
    header_info: str | SWMLVar
    identity: str | SWMLVar
    status_url: str | SWMLVar


class SendSmsConfig(TypedDict, total=False):
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


class SetMetaConfig(TypedDict, total=False):
    """Add customer metadata to call and conference events

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    private: dict[str, Any]
    public: dict[str, Any]


class SleepConfig(TypedDict, total=False):
    """Pause execution for a specified duration.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    duration: int | SWMLVar


class StopRecordCallConfig(TypedDict, total=False):
    """Stop an active background recording.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    control_id: str | SWMLVar


class StopStreamConfig(TypedDict, total=False):
    """Stop streaming call audio.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    control_id: Any | SWMLVar


class StopTapConfig(TypedDict, total=False):
    """Stop an active tap stream.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    control_id: Any | SWMLVar


class StreamConfig(TypedDict, total=False):
    """Stream call audio to a WebSocket endpoint.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    authorization_bearer_token: str | SWMLVar
    codec: str | SWMLVar
    control_id: Any | SWMLVar
    custom_parameters: dict[str, Any]
    name: str | SWMLVar
    status_url: str | SWMLVar
    status_url_method: Literal["GET", "POST"] | SWMLVar
    track: Literal["inbound_track", "outbound_track", "both_tracks"] | SWMLVar
    url: str | SWMLVar


class SwitchConfig(TypedDict, total=False):
    """Execute different instructions based on a variable's value.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    default: list[SWMLMethod] | SwitchDefault
    case: dict[str, Any]
    variable: str | SWMLVar


class SwitchDefault(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: Any
    meta: Any


class TapConfig(TypedDict, total=False):
    """Start background call tap. Media is streamed over Websocket or RTP to customer controlled URI.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    codec: Literal["PCMA", "PCMU", "pcma", "pcmu"] | SWMLVar
    control_id: Any | SWMLVar
    direction: Literal["listen", "speak", "both"] | SWMLVar
    rtp_ptime: int | SWMLVar
    status_url: str | SWMLVar
    uri: str | SWMLVar


class TranscribeConfig(TypedDict, total=False):
    """Start transcription on the call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    status_url: str | SWMLVar


class TransferConfig(TypedDict, total=False):
    """Transfer the execution of the script to a different SWML section, URL, or Relay application.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    dest: str | SWMLVar
    meta: dict[str, Any]
    params: dict[str, Any] | SWMLVar


class UserEventConfig(TypedDict, total=False):
    """Allows the user to set and send events to the connected client on the call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    event: dict[str, Any] | SWMLVar


class _SwmlVerbs:
    """The SWML verb methods SwmlBuilder installs at runtime (static view)."""

    def ai_sidecar(self: _Self, config: AiSidecarConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def amazon_bedrock(self: _Self, config: AmazonBedrockConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def cond(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by is_valid_cond_method, swml_schema.c:1249."""
        raise NotImplementedError  # installed dynamically at runtime

    def connect(self: _Self, config: ConnectConfig | None = None) -> _Self:
        """Dial a SIP URI or phone number."""
        raise NotImplementedError  # installed dynamically at runtime

    def denoise(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def detect_machine(self: _Self, config: DetectMachineConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def echo(self: _Self, config: EchoConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def enter_queue(self: _Self, config: EnterQueueConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def execute(self: _Self, config: ExecuteConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def execute_rpc(self: _Self, config: ExecuteRpcConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def goto(self: _Self, config: GotoConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def join_conference(
        self: _Self, config: JoinConferenceConfig | None = None
    ) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def join_room(self: _Self, config: JoinRoomConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def label(self: _Self, config: LabelConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def live_transcribe(
        self: _Self, config: LiveTranscribeConfig | None = None
    ) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def live_translate(self: _Self, config: LiveTranslateConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def pay(self: _Self, config: PayConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def prompt(self: _Self, config: PromptConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def receive_fax(self: _Self, config: ReceiveFaxConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def record(self: _Self, config: RecordConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def record_call(self: _Self, config: RecordCallConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def request(self: _Self, config: RequestConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def return_(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by CHECK_swml_method_return, swml_schema.c:1468."""
        raise NotImplementedError  # installed dynamically at runtime

    def ring(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def sip_refer(self: _Self, config: SipReferConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def send_digits(self: _Self, config: SendDigitsConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def send_fax(self: _Self, config: SendFaxConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def send_sms(self: _Self, config: SendSmsConfig | None = None) -> _Self:
        """Send an outbound SMS or MMS message to a PSTN phone number."""
        raise NotImplementedError  # installed dynamically at runtime

    def set(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Set script variables to the specified values."""
        raise NotImplementedError  # installed dynamically at runtime

    def set_meta(self: _Self, config: SetMetaConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def sleep(self: _Self, config: SleepConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_denoise(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_record_call(
        self: _Self, config: StopRecordCallConfig | None = None
    ) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_stream(self: _Self, config: StopStreamConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_tap(self: _Self, config: StopTapConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def stream(self: _Self, config: StreamConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def switch(self: _Self, config: SwitchConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def tap(self: _Self, config: TapConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def transcribe(self: _Self, config: TranscribeConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def transcribe_stop(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def transfer(self: _Self, config: TransferConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime

    def unset(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by CHECK_swml_method_unset, swml_schema.c."""
        raise NotImplementedError  # installed dynamically at runtime

    def user_event(self: _Self, config: UserEventConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:889."""
        raise NotImplementedError  # installed dynamically at runtime
