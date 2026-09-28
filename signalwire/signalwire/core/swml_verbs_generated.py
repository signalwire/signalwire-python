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
from signalwire.core.swaig_actions_generated import SwaigResponse
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


class BindDigit(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    bind_digit: BindDigitConfig


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


class CallPayParameters(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str | SWMLVar
    value: str | SWMLVar


class CallPayPrompts(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    actions: list[CallPayPromptsActions | SWMLVar] | SWMLVar
    attempt: str | SWMLVar
    card_type: str | SWMLVar
    error_type: str | SWMLVar
    # non-identifier field 'for': Literal['payment-card-number', 'expiration-date', 'security-code', 'postal-code', 'bank-routing-number', 'bank-account-number', 'payment-processing', 'payment-completed', 'payment-failed', 'payment-canceled'] | SWMLVar
    play: list[RingbackConfig | SWMLVar] | SWMLVar
    require_matching_inputs: str | SWMLVar


class CallPayPromptsActions(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["Say", "Play"] | SWMLVar
    phrase: str | SWMLVar


class ClearDigitBindings(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    clear_digit_bindings: ClearDigitBindingsConfig


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


class DataMap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    contexts: list[Any] | bool | None | float | dict[str, Any] | str
    expressions: list[Expression] | Expression
    output: SwaigResponse
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
    """Without one of `expr` / `string` and `output`, a Expression has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    pattern: str
    expr: str
    # non-identifier field 'nomatch-output': SwaigResponse
    output: SwaigResponse
    string: str


class Foreach(TypedDict, total=False):
    """Without `append`, `input_key` and `output_key`, a Foreach has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    append: str
    input_key: str
    max: float | str
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
    """A JSON Schema (draft 2020-12). The value is forwarded verbatim to the receiving model API, which owns this contract; the engine does not inspect it.

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


class JsonSchemaUnion(TypedDict, total=False):
    """A JSON Schema (draft 2020-12) that may also carry `example`, `nullable`, `propertyOrdering`: the value is forwarded verbatim to whichever model API the session resolves to, and those receivers do not accept one vocabulary, so a schema here must be able to express their UNION (vocabulary_union). The engine does not inspect it.

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
    nullable: bool
    properties: dict[str, JsonSchemaUnion | bool]
    required: list[str]
    prefixItems: list[JsonSchemaUnion | bool]
    items: JsonSchemaUnion | bool
    propertyNames: JsonSchemaUnion | bool
    additionalProperties: JsonSchemaUnion | bool
    unevaluatedProperties: JsonSchemaUnion | bool
    oneOf: list[JsonSchemaUnion | bool]
    anyOf: list[JsonSchemaUnion | bool]
    allOf: list[JsonSchemaUnion | bool]
    # non-identifier field 'not': JsonSchemaUnion | bool
    contains: JsonSchemaUnion | bool
    dependentRequired: dict[str, list[str]]
    dependentSchemas: dict[str, JsonSchemaUnion | bool]
    # non-identifier field 'else': JsonSchemaUnion | bool
    example: Any
    # non-identifier field 'if': JsonSchemaUnion | bool
    maxContains: int
    minContains: int
    multipleOf: float
    patternProperties: dict[str, JsonSchemaUnion | bool]
    propertyOrdering: list[str]
    readOnly: bool
    then: JsonSchemaUnion | bool
    unevaluatedItems: JsonSchemaUnion | bool
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


SWMLMethod: TypeAlias = "AI | AiSidecar | AmazonBedrock | Answer | BindDigit | ClearDigitBindings | Cond | Connect | Denoise | DetectMachine | Echo | EnterQueue | Execute | ExecuteRpc | Goto | Hangup | JoinConference | JoinRoom | Label | LiveTranscribe | LiveTranslate | Pay | Play | Prompt | ReceiveFax | Record | RecordCall | Request | Return | Ring | SIPRefer | SendDigits | SendFax | SendSMS | Set | SetCapabilities | SetMeta | Sleep | StopDenoise | StopRecordCall | StopStream | StopTap | Stream | Switch | Tap | Transcribe | TranscribeStop | Transfer | Unset | UserEvent"


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


class SetCapabilities(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set_capabilities: SetCapabilitiesConfig | list[Any] | float | str


class SetMeta(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set_meta: SetMetaConfig | list[Any] | float | str


class Sleep(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sleep: SleepConfig | list[int | SWMLVar] | int | SWMLVar


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
    output: SwaigResponse
    params: list[Any] | bool | None | float | dict[str, Any] | str
    require_args: list[Any] | str
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
    """Without one of `data_map` / `web_hook_url`, one of `description` / `purpose` and `function`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    active: bool | float | str
    argument: JsonSchemaUnion
    data_map: DataMap
    fillers: AiSWAIGItemFillers
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: JsonSchemaUnion
    purpose: str
    skip_fillers: bool | str
    wait_file: str
    wait_file_loops: float | str
    wait_for_fillers: bool | str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class AiSWAIGItemFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiSWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    defaults: AiSWAIGDefaults
    functions: list[AiSWAIGFunctionsItem]
    hooks: list[AiSWAIGHooksItem]
    includes: list[AiSWAIGIncludesItem]
    internal_fillers: AiSWAIGInternalFillers
    mcp_servers: list[AiSWAIGMcpServersItem]
    native_functions: list[str]


class AiSWAIGDefaults(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    meta_data: Any
    meta_data_token: str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class AiSWAIGFunctionsItem(TypedDict, total=False):
    """Without one of `data_map` / `web_hook_url`, one of `description` / `purpose` and `function`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    active: bool | float | str
    argument: JsonSchemaUnion
    data_map: DataMap
    fillers: AiSWAIGFunctionsItemFillers
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: JsonSchemaUnion
    purpose: str
    skip_fillers: bool | str
    wait_file: str
    wait_file_loops: float | str
    wait_for_fillers: bool | str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class AiSWAIGFunctionsItemFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiSWAIGHooksItem(TypedDict, total=False):
    """Without one of `data_map` / `web_hook_url`, one of `description` / `purpose` and `function`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    active: bool | float | str
    argument: JsonSchemaUnion
    data_map: DataMap
    fillers: AiSWAIGHooksItemFillers
    function: str
    meta_data: dict[str, Any]
    meta_data_token: str
    parameters: JsonSchemaUnion
    purpose: str
    skip_fillers: bool | str
    wait_file: str
    wait_file_loops: float | str
    wait_for_fillers: bool | str
    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class AiSWAIGHooksItemFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiSWAIGIncludesItem(TypedDict, total=False):
    """Without `functions` and `url`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    auth_password: str
    auth_user: str
    functions: list[Any]
    meta_data: dict[str, Any]
    url: str


class AiSWAIGInternalFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    adjust_response_latency: AiSWAIGInternalFillersAdjustResponseLatency
    change_context: AiSWAIGInternalFillersChangeContext
    check_time: AiSWAIGInternalFillersCheckTime
    get_ideal_strategy: AiSWAIGInternalFillersGetIdealStrategy
    get_visual_input: AiSWAIGInternalFillersGetVisualInput
    next_step: AiSWAIGInternalFillersNextStep
    pause_conversation: AiSWAIGInternalFillersPauseConversation
    wait_for_user: AiSWAIGInternalFillersWaitForUser
    wait_seconds: AiSWAIGInternalFillersWaitSeconds


class AiSWAIGInternalFillersAdjustResponseLatency(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiSWAIGInternalFillersChangeContext(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiSWAIGInternalFillersCheckTime(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiSWAIGInternalFillersGetIdealStrategy(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiSWAIGInternalFillersGetVisualInput(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiSWAIGInternalFillersNextStep(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiSWAIGInternalFillersPauseConversation(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiSWAIGInternalFillersWaitForUser(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiSWAIGInternalFillersWaitSeconds(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


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
    params: AiLanguagesItemParams
    pronounce: list[Any]
    speech_fillers: list[Any]
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
    fillers: list[Any] | AiMultilingualFillers
    function_fillers: list[Any] | AiMultilingualFunctionFillers
    languages: list[Any]
    min_switch_words: float
    model: str
    provider: str
    start_language: str
    turn_fillers: list[Any] | AiMultilingualTurnFillers


class AiMultilingualFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiMultilingualFunctionFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any
    auto: Any


class AiMultilingualTurnFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: Any


class AiParams(TypedDict, total=False):
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
    attention_timeout: int | str
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
    convo: list[AiParamsConvoItem]
    debug_webhook_level: int | str
    debug_webhook_url: str
    deepgram_key_override: str
    deepgram_stream_first: bool | float | str
    deepgram_tts_key: str
    deepgram_url_override: str
    developer_prompt: str
    digit_terminators: str
    digit_timeout: int | str
    direction: str
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
    inner_dialog: AiParamsInnerDialog
    inner_dialog_model: str
    inner_dialog_prompt: str
    inner_dialog_scorecard: bool | AiParamsInnerDialogScorecard
    input_poll_freq: int | str
    interrupt_on_noise: int | str | bool
    interrupt_prompt: str
    inworld_apikey: str
    inworld_key: str
    inworld_model: str
    language: str
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
    realtime: AiParamsRealtime
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
    tool_result_distill: bool | AiParamsToolResultDistill
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


class AiParamsConvoItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    content: str
    lang: str
    role: str
    tool_call_id: str
    tool_calls: list[Any]


class AiParamsInnerDialog(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWAIG: AiParamsInnerDialogSWAIG


class AiParamsInnerDialogSWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    defaults: AiParamsInnerDialogSWAIGDefaults
    functions: list[Any]


class AiParamsInnerDialogSWAIGDefaults(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    web_hook_auth_pass: str
    web_hook_auth_password: str
    web_hook_auth_user: str
    web_hook_url: str


class AiParamsInnerDialogScorecard(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    dials: list[Any]
    replace: bool | str


class AiParamsRealtime(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    input_transcription: str
    local_vad: bool | str
    local_vad_frame_ms: float | str
    local_vad_threshold: float | str
    noise_reduction: str
    packets_per_send: float | str
    reasoning_effort: str
    speed: float | str
    temperature: float | str
    tool_model: str
    vad_eagerness: str
    vad_prefix_padding_ms: float | str
    vad_silence_duration_ms: float | str
    vad_threshold: float | str
    vad_type: str
    voice: str


class AiParamsToolResultDistill(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    enabled: bool | str
    min_chars: float
    model: str
    prompt: str


class AiPostPrompt(TypedDict, total=False):
    """The final set of instructions and configuration settings to send to the agent.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    frequency_penalty: Any
    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[AiPostPromptPomItem]
    presence_penalty: Any
    reasoning_effort: str
    temperature: float
    text: str
    top_p: float
    verbosity: str


class AiPostPromptPomItem(TypedDict, total=False):
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


class AiPrompt(TypedDict, total=False):
    """Defines the AI agent's personality, goals, behaviors, and instructions for handling conversations.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    contexts: dict[str, Context]
    frequency_penalty: Any
    max_completion_tokens: float
    max_tokens: float
    model: str
    pom: list[AiPromptPomItem]
    presence_penalty: Any
    reasoning_effort: str
    steps: list[Step]
    temperature: float
    text: str
    top_p: float
    verbosity: str


class AiPromptPomItem(TypedDict, total=False):
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


class AiPronounceItem(TypedDict, total=False):
    """Without `replace` and `with`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

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
    customer_role: str | SWMLVar
    direction: list[str | SWMLVar] | SWMLVar
    global_data: dict[str, Any] | SWMLVar
    hints: list[str | SWMLVar] | SWMLVar
    lang: str | SWMLVar
    model: str | SWMLVar
    params: AiSidecarParams | SWMLVar
    permissions: AiSidecarPermissions | SWMLVar
    prompt: AiSidecarPrompt | str | SWMLVar
    url: str | SWMLVar


class AiSidecarSWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    defaults: AiSidecarSWAIGDefaults | SWMLVar
    functions: list[AiSidecarSWAIGFunctionsItem | SWMLVar] | SWMLVar
    mcp_servers: list[Any] | SWMLVar


class AiSidecarSWAIGDefaults(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    web_hook_auth_pass: str | SWMLVar
    web_hook_auth_password: str | SWMLVar
    web_hook_auth_user: str | SWMLVar
    web_hook_url: str | SWMLVar


class AiSidecarSWAIGFunctionsItem(TypedDict, total=False):
    """Without `function`, the element has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str | SWMLVar
    function: str | SWMLVar
    parameters: JsonSchemaUnion | SWMLVar
    purpose: str | SWMLVar
    web_hook_auth_pass: str | SWMLVar
    web_hook_auth_password: str | SWMLVar
    web_hook_auth_user: str | SWMLVar
    web_hook_url: str | SWMLVar


class AiSidecarParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    act_on_channel: bool | SWMLVar
    ai_summary: bool | SWMLVar
    ai_summary_prompt: str | SWMLVar
    debug: bool | SWMLVar
    debug_level: int | SWMLVar
    deepgram_key_override: str | SWMLVar
    deepgram_url_override: str | SWMLVar
    final_summary: bool | SWMLVar
    idle_timeout_ms: int | SWMLVar
    live_events: bool | SWMLVar
    max_history_tokens: int | SWMLVar
    max_iters_per_tick: int | SWMLVar
    min_interval_ms: int | SWMLVar
    speech_engine: str | SWMLVar
    speech_timeout: int | SWMLVar
    summary_model: str | SWMLVar
    transcribe_prompt: str | SWMLVar
    vad_silence_ms: int | SWMLVar
    vad_thresh: int | SWMLVar
    verbose_utterances: bool | SWMLVar


class AiSidecarPermissions(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    swaig_allow_settings: bool | SWMLVar
    swaig_allow_swml: bool | SWMLVar
    swaig_set_global_data: bool | SWMLVar


class AiSidecarPrompt(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    file: str | SWMLVar


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

    defaults: AmazonBedrockSWAIGDefaults
    functions: list[AmazonBedrockSWAIGFunctionsItem]


class AmazonBedrockSWAIGDefaults(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    web_hook_url: str


class AmazonBedrockSWAIGFunctionsItem(TypedDict, total=False):
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

    pom: list[AmazonBedrockPostPromptPomItem]
    text: str


class AmazonBedrockPostPromptPomItem(TypedDict, total=False):
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


class AmazonBedrockPrompt(TypedDict, total=False):
    """Establishes the initial set of instructions and settings to configure the agent.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    pom: list[AmazonBedrockPromptPomItem]
    temperature: float | str
    text: str
    top_p: float | str
    voice_id: str


class AmazonBedrockPromptPomItem(TypedDict, total=False):
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


class BindDigitConfig(TypedDict, total=False):
    """Bind DTMF digit actions.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    digits: str
    max_triggers: int | SWMLVar
    method: str
    params: dict[str, Any]
    realm: str


class ClearDigitBindingsConfig(TypedDict, total=False):
    """Clear all digit bindings.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    realm: str


class CondItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'else': list[SWMLMethod]
    then: list[SWMLMethod]
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
    result: list[ConnectResultItem] | ConnectResult
    ringback: bool | str | list[str] | RingbackConfig
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

    code: dict[str, Any]
    meta: Any


class ConnectResultItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'else': list[SWMLMethod]
    then: list[SWMLMethod]
    when: str


class ConnectResult(TypedDict, total=False):
    """Execute different instructions based on a variable's value.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    default: list[SWMLMethod] | ConnectResultDefault
    case: dict[str, list[SWMLMethod] | ConnectResultCaseValue]
    variable: str | SWMLVar


class ConnectResultDefault(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: dict[str, Any]
    meta: Any


class ConnectResultCaseValue(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: dict[str, Any]
    meta: Any


class ConnectDeviceConfirm(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: dict[str, Any]
    meta: Any


class DetectMachineConfig(TypedDict, total=False):
    """A detection method that combines AMD (Answering Machine Detection) and fax detection.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

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
    result: list[ExecuteResultItem] | ExecuteResult


class ExecuteOnReturn(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: dict[str, Any]
    meta: Any


class ExecuteResultItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'else': list[SWMLMethod]
    then: list[SWMLMethod]
    when: str


class ExecuteResult(TypedDict, total=False):
    """Execute different instructions based on a variable's value.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    default: list[SWMLMethod] | ExecuteResultDefault
    case: dict[str, list[SWMLMethod] | ExecuteResultCaseValue]
    variable: str | SWMLVar


class ExecuteResultDefault(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: dict[str, Any]
    meta: Any


class ExecuteResultCaseValue(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: dict[str, Any]
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

    action: str | LiveTranscribeAction | SWMLVar
    hints: list[LiveTranscribeHintsItem | str | SWMLVar] | SWMLVar


class LiveTranscribeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    start: LiveTranscribeActionStart | SWMLVar
    stop: Any
    summarize: LiveTranscribeActionSummarize | SWMLVar


class LiveTranscribeActionStart(TypedDict, total=False):
    """Without `direction` and `lang`, `action` (checked only where live_transcribe discards the result) has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    ai_summary: bool | SWMLVar
    ai_summary_prompt: str | SWMLVar
    debug_level: int | SWMLVar
    deepgram_key_override: str | SWMLVar
    deepgram_url_override: str | SWMLVar
    direction: list[str | SWMLVar] | SWMLVar
    hints: list[str | SWMLVar] | SWMLVar
    lang: str | SWMLVar
    live_events: bool | SWMLVar
    speech_engine: str | SWMLVar
    speech_timeout: int | SWMLVar
    vad_silence_ms: int | SWMLVar
    vad_thresh: int | SWMLVar
    verbose_utterances: bool | SWMLVar
    webhook: str | SWMLVar


class LiveTranscribeActionSummarize(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai_model: str | SWMLVar
    prompt: str | SWMLVar
    summary_prompt: str | SWMLVar
    webhook: str | SWMLVar


class LiveTranscribeHintsItem(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    pattern: str | SWMLVar
    hint: str | SWMLVar
    ignore_case: bool | str | SWMLVar
    replace: str | SWMLVar


class LiveTranslateConfig(TypedDict, total=False):
    """Start live translation of the call. The translation will be sent to the specified webhook URL.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    action: str | LiveTranslateAction | SWMLVar


class LiveTranslateAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    inject: LiveTranslateActionInject | SWMLVar
    start: LiveTranslateActionStart | SWMLVar
    stop: Any
    summarize: LiveTranslateActionSummarize | SWMLVar


class LiveTranslateActionInject(TypedDict, total=False):
    """Without `direction` and `message`, `action` (checked only where live_translate discards the result) has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    direction: str | SWMLVar
    message: str | SWMLVar


class LiveTranslateActionStart(TypedDict, total=False):
    """Without `direction`, `from_lang` and `to_lang`, `action` (checked only where live_translate discards the result) has no effect: it is accepted and ignored, not rejected.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    ai_summary: bool | SWMLVar
    ai_summary_prompt: str | SWMLVar
    debug_level: int | SWMLVar
    deepgram_key_override: str | SWMLVar
    deepgram_url_override: str | SWMLVar
    direction: list[str | SWMLVar] | SWMLVar
    filter_from: str | SWMLVar
    filter_to: str | SWMLVar
    from_lang: str | SWMLVar
    from_voice: str | SWMLVar
    from_voice_params: dict[str, Any] | SWMLVar
    live_events: bool | SWMLVar
    mode: str | SWMLVar
    speech_engine: str | SWMLVar
    speech_timeout: int | SWMLVar
    to_lang: str | SWMLVar
    to_voice: str | SWMLVar
    to_voice_params: dict[str, Any] | SWMLVar
    translation_model: str | SWMLVar
    translation_model_params: dict[str, Any] | SWMLVar
    vad_silence_ms: int | SWMLVar
    vad_thresh: int | SWMLVar
    webhook: str | SWMLVar


class LiveTranslateActionSummarize(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    prompt: str | SWMLVar
    summary_prompt: str | SWMLVar
    webhook: str | SWMLVar


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
    parameters: list[CallPayParameters | SWMLVar] | SWMLVar
    payment_connector_url: str | SWMLVar
    payment_method: Literal["credit-card", "ach-debit"] | SWMLVar
    postal_code: str | SWMLVar
    prompts: list[CallPayPrompts | SWMLVar] | SWMLVar
    say_voice: str | SWMLVar
    security_code: str | SWMLVar
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
    play: RingbackConfig | list[str] | str
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


class SetCapabilitiesConfig(TypedDict, total=False):
    """Override subscriber capabilities

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    capabilities: list[str | SWMLVar] | SWMLVar


class SetMetaConfig(TypedDict, total=False):
    """Add customer metadata to call and conference events

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    private: dict[str, Any] | SWMLVar
    public: dict[str, Any] | SWMLVar


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
    case: dict[str, list[SWMLMethod] | SwitchCaseValue]
    variable: str | SWMLVar


class SwitchDefault(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: dict[str, Any]
    meta: Any


class SwitchCaseValue(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    code: dict[str, Any]
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
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def amazon_bedrock(self: _Self, config: AmazonBedrockConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def bind_digit(self: _Self, config: BindDigitConfig | None = None) -> _Self:
        """Bind DTMF digit actions. (api_state: experimental)"""
        raise NotImplementedError  # installed dynamically at runtime

    def clear_digit_bindings(
        self: _Self, config: ClearDigitBindingsConfig | None = None
    ) -> _Self:
        """Clear all digit bindings. (api_state: experimental)"""
        raise NotImplementedError  # installed dynamically at runtime

    def cond(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by is_valid_cond_method, swml_schema.c:1271."""
        raise NotImplementedError  # installed dynamically at runtime

    def connect(self: _Self, config: ConnectConfig | None = None) -> _Self:
        """Dial a SIP URI or phone number."""
        raise NotImplementedError  # installed dynamically at runtime

    def denoise(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911. (api_state: experimental)"""
        raise NotImplementedError  # installed dynamically at runtime

    def detect_machine(self: _Self, config: DetectMachineConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def echo(self: _Self, config: EchoConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def enter_queue(self: _Self, config: EnterQueueConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def execute(self: _Self, config: ExecuteConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def execute_rpc(self: _Self, config: ExecuteRpcConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911. (api_state: experimental)"""
        raise NotImplementedError  # installed dynamically at runtime

    def goto(self: _Self, config: GotoConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def join_conference(
        self: _Self, config: JoinConferenceConfig | None = None
    ) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def join_room(self: _Self, config: JoinRoomConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def label(self: _Self, config: LabelConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def live_transcribe(
        self: _Self, config: LiveTranscribeConfig | None = None
    ) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def live_translate(self: _Self, config: LiveTranslateConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def pay(self: _Self, config: PayConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def prompt(self: _Self, config: PromptConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def receive_fax(self: _Self, config: ReceiveFaxConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def record(self: _Self, config: RecordConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def record_call(self: _Self, config: RecordCallConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def request(self: _Self, config: RequestConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def return_(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by CHECK_swml_method_return, swml_schema.c:1495."""
        raise NotImplementedError  # installed dynamically at runtime

    def ring(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def sip_refer(self: _Self, config: SipReferConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def send_digits(self: _Self, config: SendDigitsConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def send_fax(self: _Self, config: SendFaxConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def send_sms(self: _Self, config: SendSmsConfig | None = None) -> _Self:
        """Send an outbound SMS or MMS message to a PSTN phone number."""
        raise NotImplementedError  # installed dynamically at runtime

    def set(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Set script variables to the specified values."""
        raise NotImplementedError  # installed dynamically at runtime

    def set_capabilities(
        self: _Self, config: SetCapabilitiesConfig | None = None
    ) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911. (api_state: experimental)"""
        raise NotImplementedError  # installed dynamically at runtime

    def set_meta(self: _Self, config: SetMetaConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911. (api_state: experimental)"""
        raise NotImplementedError  # installed dynamically at runtime

    def sleep(self: _Self, config: SleepConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_denoise(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911. (api_state: experimental)"""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_record_call(
        self: _Self, config: StopRecordCallConfig | None = None
    ) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_stream(self: _Self, config: StopStreamConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_tap(self: _Self, config: StopTapConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def stream(self: _Self, config: StreamConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def switch(self: _Self, config: SwitchConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def tap(self: _Self, config: TapConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def transcribe(self: _Self, config: TranscribeConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def transcribe_stop(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def transfer(self: _Self, config: TransferConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911."""
        raise NotImplementedError  # installed dynamically at runtime

    def unset(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by CHECK_swml_method_unset, swml_schema.c."""
        raise NotImplementedError  # installed dynamically at runtime

    def user_event(self: _Self, config: UserEventConfig | None = None) -> _Self:
        """Body shape enforced by check_method_type_and_unknown_params, swml_schema.c:911. (api_state: experimental)"""
        raise NotImplementedError  # installed dynamically at runtime
