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
from typing import Protocol, TypeVar

_Self = TypeVar("_Self", bound="_SwmlVerbs")


class Section(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    main: list[SWMLMethod]


SWMLMethod: TypeAlias = "Answer | AI | AmazonBedrock | Cond | Connect | Denoise | EnterQueue | Execute | Goto | Label | LiveTranscribe | LiveTranslate | Hangup | JoinRoom | JoinConference | Play | Prompt | ReceiveFax | Record | RecordCall | Request | Return | SendDigits | SendFax | SendSMS | Set | Sleep | SIPRefer | StopDenoise | StopRecordCall | StopTap | Switch | Tap | Transfer | Unset | Pay | DetectMachine | UserEvent"


class Answer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    answer: dict[str, Any]


class AI(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai: AIObject


class AmazonBedrock(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    amazon_bedrock: AmazonBedrockObject


class Cond(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    cond: list[CondParams]


class Connect(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    connect: (
        ConnectDeviceSingle
        | ConnectDeviceSerial
        | ConnectDeviceParallel
        | ConnectDeviceSerialParallel
    )


class Denoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    denoise: dict[str, Any]


class EnterQueue(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    enter_queue: EnterQueueObject


class Execute(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    execute: dict[str, Any]


class Goto(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    goto: dict[str, Any]


class Label(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    label: str


class LiveTranscribe(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_transcribe: dict[str, Any]


class LiveTranslate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_translate: dict[str, Any]


class Hangup(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hangup: dict[str, Any]


class JoinRoom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    join_room: dict[str, Any]


class JoinConference(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    join_conference: JoinConferenceObject


class Play(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    play: PlayWithURL | PlayWithURLS


class Prompt(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    prompt: dict[str, Any]


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


class Sleep(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sleep: dict[str, Any] | int | SWMLVar


class SIPRefer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sip_refer: dict[str, Any]


class StopDenoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_denoise: dict[str, Any]


class StopRecordCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_record_call: dict[str, Any]


class StopTap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_tap: dict[str, Any]


class Switch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    switch: dict[str, Any]


class Tap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    tap: dict[str, Any]


class Transfer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    transfer: dict[str, Any]


class Unset(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    unset: str | list[str]


class Pay(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    pay: dict[str, Any]


class DetectMachine(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    detect_machine: dict[str, Any]


class UserEvent(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    user_event: dict[str, Any]


SWMLVar: TypeAlias = "str"


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


class AmazonBedrockObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    global_data: dict[str, Any]
    params: BedrockParams
    post_prompt: BedrockPostPrompt
    post_prompt_url: str
    prompt: BedrockPrompt
    SWAIG: BedrockSWAIG


CondParams: TypeAlias = "CondReg | CondElse"


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
    encryption: Literal["mandatory"] | Literal["optional"] | Literal["forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    to: str


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
    encryption: Literal["mandatory"] | Literal["optional"] | Literal["forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    serial: list[ConnectDeviceSingle]


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
    encryption: Literal["mandatory"] | Literal["optional"] | Literal["forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    parallel: list[ConnectDeviceSingle]


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
    encryption: Literal["mandatory"] | Literal["optional"] | Literal["forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    serial_parallel: list[list[ConnectDeviceSingle]]


class EnterQueueObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    queue_name: str
    transfer_after_bridge: str | SWMLVar
    status_url: str
    wait_url: str | SWMLVar
    wait_time: int | SWMLVar


class ExecuteSwitch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    variable: str
    case: dict[str, Any]
    default: list[SWMLMethod]


TranscribeAction: TypeAlias = (
    "TranscribeStartAction | Literal['stop'] | TranscribeSummarizeActionUnion"
)


TranslateAction: TypeAlias = (
    "StartAction | Literal['stop'] | SummarizeActionUnion | InjectAction"
)


class JoinConferenceObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    muted: bool | SWMLVar
    beep: Literal["true"] | Literal["false"] | Literal["onEnter"] | Literal["onExit"]
    start_on_enter: bool | SWMLVar
    end_on_exit: bool | SWMLVar
    wait_url: str | SWMLVar
    max_participants: int | SWMLVar
    record: Literal["do-not-record"] | Literal["record-from-start"]
    region: str
    trim: Literal["trim-silence"] | Literal["do-not-trim"]
    coach: str
    status_callback_event: (
        Literal["start"]
        | Literal["end"]
        | Literal["join"]
        | Literal["leave"]
        | Literal["mute"]
        | Literal["hold"]
        | Literal["modify"]
        | Literal["speaker"]
        | Literal["announcement"]
    )
    status_callback: str
    status_callback_method: Literal["GET"] | Literal["POST"]
    recording_status_callback: str
    recording_status_callback_method: Literal["GET"] | Literal["POST"]
    recording_status_callback_event: (
        Literal["in-progress"] | Literal["completed"] | Literal["absent"]
    )
    result: dict[str, Any] | list[CondParams]


class PlayWithURL(TypedDict, total=False):
    """Play with a single URL

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    auto_answer: bool | SWMLVar
    volume: float | SWMLVar
    say_voice: str
    say_language: str
    say_gender: Literal["male", "female"]
    status_url: str
    url: play_url | SWMLVar


class PlayWithURLS(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    auto_answer: bool | SWMLVar
    volume: float | SWMLVar
    say_voice: str
    say_language: str
    say_gender: Literal["male", "female"]
    status_url: str
    urls: list[play_url] | list[SWMLVar]


play_url: TypeAlias = "str"


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


class PayParameters(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    value: str


class PayPrompts(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    actions: list[PayPromptAction]
    # non-identifier field 'for': str
    attempts: str
    card_type: str
    error_type: str


class Hint(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hint: str
    pattern: str
    replace: str
    ignore_case: bool | SWMLVar


Languages: TypeAlias = "LanguagesWithSoloFillers | LanguagesWithFillers"


class AIParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    acknowledge_interruptions: bool | SWMLVar
    ai_model: (
        Literal["gpt-4o-mini"] | Literal["gpt-4.1-mini"] | Literal["gpt-4.1-nano"] | str
    )
    ai_name: str
    ai_volume: int | SWMLVar
    app_name: str
    asr_smart_format: bool | SWMLVar
    attention_timeout: AttentionTimeout | Literal[0] | SWMLVar
    attention_timeout_prompt: str
    asr_diarize: bool | SWMLVar
    asr_speaker_affinity: bool | SWMLVar
    audible_debug: bool | SWMLVar
    audible_latency: bool | SWMLVar
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
    cache_mode: bool | SWMLVar
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
    enable_accounting: bool | SWMLVar
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
    inner_dialog_model: (
        Literal["gpt-4o-mini"] | Literal["gpt-4.1-mini"] | Literal["gpt-4.1-nano"] | str
    )
    inner_dialog_prompt: str
    inner_dialog_synced: bool | SWMLVar
    initial_sleep_ms: int | SWMLVar
    input_poll_freq: int | SWMLVar
    interrupt_on_noise: bool | SWMLVar
    interrupt_prompt: str
    languages_enabled: bool | SWMLVar
    local_tz: str
    llm_diarize_aware: bool | SWMLVar
    max_emotion: int | SWMLVar
    max_response_tokens: int | SWMLVar
    openai_asr_engine: str
    outbound_attention_timeout: int | SWMLVar
    persist_global_data: bool | SWMLVar
    pom_format: Literal["markdown"] | Literal["xml"]
    save_conversation: bool | SWMLVar
    speech_event_timeout: int | SWMLVar
    speech_gen_quick_stops: int | SWMLVar
    speech_timeout: int | SWMLVar
    speak_when_spoken_to: bool | SWMLVar
    start_paused: bool | SWMLVar
    static_greeting: str
    static_greeting_no_barge: bool | SWMLVar
    summary_mode: Literal["string"] | Literal["original"] | SWMLVar
    swaig_allow_settings: bool | SWMLVar
    swaig_allow_swml: bool | SWMLVar
    swaig_post_conversation: bool | SWMLVar
    swaig_set_global_data: bool | SWMLVar
    swaig_post_swml_vars: bool | list[str] | SWMLVar
    thinking_model: (
        Literal["gpt-4o-mini"] | Literal["gpt-4.1-mini"] | Literal["gpt-4.1-nano"] | str
    )
    transparent_barge: bool | SWMLVar
    transparent_barge_max_time: int | SWMLVar
    transfer_summary: bool | SWMLVar
    turn_detection_timeout: int | SWMLVar
    tts_number_format: Literal["international"] | Literal["national"]
    verbose_logs: bool | SWMLVar
    video_listening_file: str
    video_idle_file: str
    video_talking_file: str
    vision_model: (
        Literal["gpt-4o-mini"] | Literal["gpt-4.1-mini"] | Literal["gpt-4.1-nano"] | str
    )
    vad_config: str
    wait_for_user: bool | SWMLVar
    wake_prefix: str
    eleven_labs_stability: float | SWMLVar
    eleven_labs_similarity: float | SWMLVar


AIPostPrompt: TypeAlias = "AIPostPromptText | AIPostPromptPom"


class Pronounce(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    replace: str
    # non-identifier field 'with': str
    ignore_case: bool | SWMLVar


AIPrompt: TypeAlias = "AIPromptText | AIPromptPom"


class SWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    defaults: SWAIGDefaults
    native_functions: list[SWAIGNativeFunction]
    includes: list[SWAIGIncludes]
    functions: list[SWAIGFunction]
    internal_fillers: SWAIGInternalFiller


class BedrockParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    attention_timeout: AttentionTimeout | Literal[0] | SWMLVar
    hard_stop_time: str | SWMLVar
    inactivity_timeout: int | SWMLVar
    video_listening_file: str
    video_idle_file: str
    video_talking_file: str
    hard_stop_prompt: str


BedrockPostPrompt: TypeAlias = "OmitPropertiesBedrockPostPomptTextOmittedPromptProps | OmitPropertiesBedrockPostPromptPomOmittedPromptProps"


BedrockPrompt: TypeAlias = "OmitPropertiesBedrockPromptTextOmittedPromptProps | OmitPropertiesBedrockPromptPomOmittedPromptProps"


class BedrockSWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    functions: list[BedrockSWAIGFunction]
    defaults: SWAIGDefaults
    native_functions: list[SWAIGNativeFunction]
    includes: list[SWAIGIncludes]


class CondReg(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    when: str
    then: list[SWMLMethod]
    # non-identifier field 'else': list[SWMLMethod]


class CondElse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'else': list[SWMLMethod]


class ConnectHeaders(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    value: str


class ConnectSwitch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    variable: str
    case: dict[str, Any]
    default: list[SWMLMethod]


ValidConfirmMethods: TypeAlias = "Cond | Set | Unset | Hangup | Play | Prompt | Record | RecordCall | StopRecordCall | Tap | StopTap | SendDigits | SendSMS | Denoise | StopDenoise"


CallStatus: TypeAlias = "Literal['created', 'ringing', 'answered', 'ended']"


class TranscribeStartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    start: dict[str, Any]


TranscribeSummarizeActionUnion: TypeAlias = (
    "TranscribeSummarizeAction | Literal['summarize']"
)


class StartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    start: dict[str, Any]


SummarizeActionUnion: TypeAlias = "SummarizeAction | Literal['summarize']"


class InjectAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    inject: dict[str, Any]


PayPromptAction: TypeAlias = "PayPromptSayAction | PayPromptPlayAction"


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


AttentionTimeout: TypeAlias = "int"


class ConversationMessage(TypedDict, total=False):
    """A message object representing a single turn in the conversation history.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    role: ConversationRole
    content: str
    lang: str


Direction: TypeAlias = "Literal['inbound', 'outbound']"


class AIPostPromptText(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    text: str


class AIPostPromptPom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    pom: list[POM]


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


class SWAIGDefaults(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    web_hook_url: str


SWAIGNativeFunction: TypeAlias = (
    "Literal['check_time', 'wait_seconds', 'wait_for_user', 'adjust_response_latency']"
)


class SWAIGIncludes(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    functions: list[str]
    url: str
    meta_data: dict[str, Any]


SWAIGFunction: TypeAlias = "UserSWAIGFunction | StartUpHookSWAIGFunction | HangUpHookSWAIGFunction | SummarizeConversationSWAIGFunction"


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


class OmitPropertiesBedrockPostPomptTextOmittedPromptProps(TypedDict, total=False):
    """The template for omitting properties.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    text: str


class OmitPropertiesBedrockPostPromptPomOmittedPromptProps(TypedDict, total=False):
    """The template for omitting properties.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    pom: list[POM]


class OmitPropertiesBedrockPromptTextOmittedPromptProps(TypedDict, total=False):
    """The template for omitting properties.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    voice_id: (
        Literal["tiffany"]
        | Literal["matthew"]
        | Literal["amy"]
        | Literal["lupe"]
        | Literal["carlos"]
    )
    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    text: str


class OmitPropertiesBedrockPromptPomOmittedPromptProps(TypedDict, total=False):
    """The template for omitting properties.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    voice_id: (
        Literal["tiffany"]
        | Literal["matthew"]
        | Literal["amy"]
        | Literal["lupe"]
        | Literal["carlos"]
    )
    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    pom: list[POM]


BedrockSWAIGFunction: TypeAlias = "PickPropertiesUserSWAIGFunctionPickedSWAIGFunctionProps | PickPropertiesStartUpHookSWAIGFunctionPickedSWAIGFunctionProps | PickPropertiesHangUpHookSWAIGFunctionPickedSWAIGFunctionProps | PickPropertiesSummarizeConversationSWAIGFunctionPickedSWAIGFunctionProps"


TranscribeDirection: TypeAlias = "Literal['remote-caller', 'local-caller']"


SpeechEngine: TypeAlias = "Literal['deepgram', 'google']"


class TranscribeSummarizeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    summarize: dict[str, Any]


TranslationFilterPreset: TypeAlias = (
    "Literal['polite', 'rude', 'professional', 'shakespeare', 'gen-z']"
)


CustomTranslationFilter: TypeAlias = "str"


TranslateDirection: TypeAlias = "Literal['remote-caller', 'local-caller']"


class SummarizeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    summarize: dict[str, Any]


class PayPromptSayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["Say"]
    phrase: str


class PayPromptPlayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["Play"]
    phrase: str


class LanguageParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stability: float | SWMLVar
    similarity: float | SWMLVar


ConversationRole: TypeAlias = "Literal['user', 'assistant', 'system']"


POM: TypeAlias = "PomSectionBodyContent | PomSectionBulletsContent"


class Contexts(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    default: ContextsObject


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


FunctionFillers: TypeAlias = "dict[str, Any]"


class PickPropertiesUserSWAIGFunctionPickedSWAIGFunctionProps(TypedDict, total=False):
    """The template for picking properties.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    parameters: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    web_hook_url: str
    function: str


class PickPropertiesStartUpHookSWAIGFunctionPickedSWAIGFunctionProps(
    TypedDict, total=False
):
    """The template for picking properties.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    parameters: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    web_hook_url: str
    function: Literal["startup_hook"]


class PickPropertiesHangUpHookSWAIGFunctionPickedSWAIGFunctionProps(
    TypedDict, total=False
):
    """The template for picking properties.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    parameters: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    web_hook_url: str
    function: Literal["hangup_hook"]


class PickPropertiesSummarizeConversationSWAIGFunctionPickedSWAIGFunctionProps(
    TypedDict, total=False
):
    """The template for picking properties.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    parameters: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    web_hook_url: str
    function: Literal["summarize_conversation"]


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


ContextsObject: TypeAlias = "ContextsPOMObject | ContextsTextObject"


class FunctionParameters(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["object"]
    properties: dict[str, Any]
    required: list[str]


class DataMap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    output: Output
    expressions: list[Expression]
    webhooks: list[Webhook]


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


SchemaType: TypeAlias = "StringProperty | IntegerProperty | NumberProperty | BooleanProperty | ArrayProperty | ObjectProperty | NullProperty | OneOfProperty | AllOfProperty | AnyOfProperty | ConstProperty"


class Output(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    response: str
    action: list[Action]


class Expression(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    string: str
    pattern: str
    output: Output


class Webhook(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    expressions: list[Expression]
    error_keys: str | list[str]
    url: str
    foreach: dict[str, Any]
    headers: dict[str, Any]
    method: Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"]
    input_args_as_params: bool | SWMLVar
    params: dict[str, Any]
    require_args: str | list[str]
    output: Output


ContextSteps: TypeAlias = "ContextPOMSteps | ContextTextSteps"


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


class BooleanProperty(TypedDict, total=False):
    """Base interface for all property types

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["boolean"]
    default: bool | SWMLVar


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


class NullProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["null"]
    description: str


class OneOfProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    oneOf: list[SchemaType]


class AllOfProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    allOf: list[SchemaType]


class AnyOfProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    anyOf: list[SchemaType]


class ConstProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    const: dict[str, Any]


Action: TypeAlias = "SWMLAction | ChangeContextAction | ChangeStepAction | ContextSwitchAction | HangupAction | HoldAction | PlaybackBGAction | SayAction | SetGlobalDataAction | SetMetaDataAction | StopAction | StopPlaybackBGAction | ToggleFunctionsAction | UnsetGlobalDataAction | UnsetMetaDataAction | UserInputAction"


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


StringFormat: TypeAlias = "Literal['date_time', 'time', 'date', 'duration', 'email', 'hostname', 'ipv4', 'ipv6', 'uri', 'uuid']"


class SWMLAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    SWML: dict[str, Any]


class ChangeContextAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    change_context: str


class ChangeStepAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    change_step: str


class ContextSwitchAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    context_switch: dict[str, Any]


class HangupAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hangup: bool | SWMLVar


class HoldAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hold: int | SWMLVar | dict[str, Any]


class PlaybackBGAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    playback_bg: dict[str, Any]


class SayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    say: str


class SetGlobalDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set_global_data: dict[str, Any]


class SetMetaDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set_meta_data: dict[str, Any]


class StopAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop: bool | SWMLVar


class StopPlaybackBGAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_playback_bg: bool | SWMLVar


class ToggleFunctionsAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    toggle_functions: list[dict[str, Any]]


class UnsetGlobalDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    unset_global_data: str | dict[str, Any]


class UnsetMetaDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    unset_meta_data: str | dict[str, Any]


class UserInputAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    user_input: str


class ConnectConfig(TypedDict, total=False):
    """Dial a SIP URI or phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

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
    encryption: Literal["mandatory"] | Literal["optional"] | Literal["forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    to: str
    serial: list[ConnectDeviceSingle]
    parallel: list[ConnectDeviceSingle]
    serial_parallel: list[list[ConnectDeviceSingle]]


class ExecuteConfig(TypedDict, total=False):
    """Execute a specified section or URL as a subroutine, and upon completion, return to the current document.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    dest: str
    params: dict[str, Any]
    meta: dict[str, Any]
    on_return: list[SWMLMethod]
    result: ExecuteSwitch | list[CondParams]


class GotoConfig(TypedDict, total=False):
    """Jump to a label within the current section, optionally based on a condition.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    label: str
    when: str
    max: int | SWMLVar


class LiveTranscribeConfig(TypedDict, total=False):
    """Start live transcription of the call. The transcription will be sent to the specified webhook URL.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    action: TranscribeAction


class LiveTranslateConfig(TypedDict, total=False):
    """Start live translation of the call. The translation will be sent to the specified webhook URL.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    action: TranslateAction


class JoinRoomConfig(TypedDict, total=False):
    """Join a RELAY room. If the room doesn't exist, it creates a new room.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str


class PromptConfig(TypedDict, total=False):
    """Play a prompt and wait for input. The input can be received either as digits from the keypad,

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    play: play_url | list[play_url] | SWMLVar | list[SWMLVar]
    volume: float
    say_voice: str
    say_language: str
    say_gender: Literal["male", "female"]
    max_digits: int | SWMLVar
    terminators: str
    digit_timeout: float | SWMLVar
    initial_timeout: float | SWMLVar
    speech_timeout: float | SWMLVar
    speech_end_timeout: float | SWMLVar
    speech_language: str
    speech_hints: list[str] | list[SWMLVar]
    speech_engine: str
    status_url: str


class ReceiveFaxConfig(TypedDict, total=False):
    """Receive a fax being delivered to this call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    status_url: str


class RecordConfig(TypedDict, total=False):
    """Record the call audio in the foreground, pausing further SWML execution until recording ends.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    stereo: bool | SWMLVar
    format: Literal["wav"] | Literal["mp3"] | Literal["mp4"]
    direction: Literal["speak"] | Literal["listen"]
    terminators: str
    beep: bool | SWMLVar
    input_sensitivity: float | SWMLVar
    initial_timeout: float | SWMLVar
    end_silence_timeout: float | SWMLVar
    max_length: float | SWMLVar
    status_url: str


class RecordCallConfig(TypedDict, total=False):
    """Record call in the background.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    control_id: str
    stereo: bool | SWMLVar
    format: Literal["wav"] | Literal["mp3"] | Literal["mp4"]
    direction: Literal["speak"] | Literal["listen"] | Literal["both"]
    terminators: str
    beep: bool | SWMLVar
    input_sensitivity: float | SWMLVar
    initial_timeout: float | SWMLVar
    end_silence_timeout: float | SWMLVar
    max_length: float | SWMLVar
    status_url: str


class RequestConfig(TypedDict, total=False):
    """Send a GET, POST, PUT, or DELETE request to a remote URL.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    url: str
    method: Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"]
    headers: dict[str, Any]
    body: str | dict[str, Any]
    timeout: float | SWMLVar
    connect_timeout: float | SWMLVar
    save_variables: bool | SWMLVar


class SendDigitsConfig(TypedDict, total=False):
    """Send digit presses as DTMF tones.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    digits: str


class SendFaxConfig(TypedDict, total=False):
    """Send a fax.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    document: str
    header_info: str
    identity: str
    status_url: str


class SipReferConfig(TypedDict, total=False):
    """Send SIP REFER to a SIP call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    to_uri: str
    status_url: str
    username: str
    password: str


class StopRecordCallConfig(TypedDict, total=False):
    """Stop an active background recording.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    control_id: str


class StopTapConfig(TypedDict, total=False):
    """Stop an active tap stream.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    control_id: str


class SwitchConfig(TypedDict, total=False):
    """Execute different instructions based on a variable's value.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    variable: str
    case: dict[str, Any]
    default: list[SWMLMethod]


class TapConfig(TypedDict, total=False):
    """Start background call tap. Media is streamed over Websocket or RTP to customer controlled URI.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    control_id: str
    direction: Literal["speak"] | Literal["listen"] | Literal["both"]
    codec: Literal["PCMU"] | Literal["PCMA"]
    rtp_ptime: int | SWMLVar
    status_url: str


class TransferConfig(TypedDict, total=False):
    """Transfer the execution of the script to a different SWML section, URL, or Relay application.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    dest: str
    params: dict[str, Any]
    meta: dict[str, Any]


class PayConfig(TypedDict, total=False):
    """Enables secure payment processing during voice calls. When implemented, it manages the entire payment flow

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    payment_connector_url: str
    charge_amount: str
    currency: str
    description: str
    input: Literal["dtmf"]
    language: str
    max_attempts: int | SWMLVar
    min_postal_code_length: int | SWMLVar
    parameters: list[PayParameters]
    payment_method: Literal["credit-card"]
    postal_code: bool | str
    prompts: list[PayPrompts]
    security_code: bool | SWMLVar
    status_url: str
    timeout: int | SWMLVar
    token_type: Literal["one-time"] | Literal["reusable"]
    valid_card_types: str
    voice: str


class DetectMachineConfig(TypedDict, total=False):
    """A detection method that combines AMD (Answering Machine Detection) and fax detection.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    detect_message_end: bool | SWMLVar
    detectors: str
    end_silence_timeout: float | SWMLVar
    initial_timeout: float | SWMLVar
    machine_ready_timeout: float | SWMLVar
    machine_voice_threshold: float | SWMLVar
    machine_words_threshold: int | SWMLVar
    status_url: str
    timeout: float | SWMLVar
    tone: Literal["CED"] | Literal["CNG"]
    wait: bool | SWMLVar


class UserEventConfig(TypedDict, total=False):
    """Allows the user to set and send events to the connected client on the call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    event: dict[str, Any]


class _SwmlVerbs(Protocol):
    """The SWML verb methods SwmlBuilder installs at runtime (static view)."""

    def amazon_bedrock(self: _Self, config: AmazonBedrockObject | None = None) -> _Self:
        """Creates a new Bedrock AI Agent"""
        ...

    def cond(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Execute a sequence of instructions depending on the value of a JavaScript condition."""
        ...

    def connect(self: _Self, config: ConnectConfig | None = None) -> _Self:
        """Dial a SIP URI or phone number."""
        ...

    def denoise(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Start noise reduction. You can stop it at any time using `stop_denoise`."""
        ...

    def enter_queue(self: _Self, config: EnterQueueObject | None = None) -> _Self:
        """Place the current call in a named queue where it will wait to be connected to an available agent or resource."""
        ...

    def execute(self: _Self, config: ExecuteConfig | None = None) -> _Self:
        """Execute a specified section or URL as a subroutine, and upon completion, return to the current document."""
        ...

    def goto(self: _Self, config: GotoConfig | None = None) -> _Self:
        """Jump to a label within the current section, optionally based on a condition."""
        ...

    def label(self: _Self, value: str) -> _Self:
        """Mark any point of the SWML section with a label so that goto can jump to it."""
        ...

    def live_transcribe(
        self: _Self, config: LiveTranscribeConfig | None = None
    ) -> _Self:
        """Start live transcription of the call. The transcription will be sent to the specified webhook URL."""
        ...

    def live_translate(self: _Self, config: LiveTranslateConfig | None = None) -> _Self:
        """Start live translation of the call. The translation will be sent to the specified webhook URL."""
        ...

    def join_room(self: _Self, config: JoinRoomConfig | None = None) -> _Self:
        """Join a RELAY room. If the room doesn't exist, it creates a new room."""
        ...

    def join_conference(
        self: _Self, config: JoinConferenceObject | None = None
    ) -> _Self:
        """Join an ad-hoc audio conference started on either the SignalWire or Compatibility API."""
        ...

    def prompt(self: _Self, config: PromptConfig | None = None) -> _Self:
        """Play a prompt and wait for input. The input can be received either as digits from the keypad,"""
        ...

    def receive_fax(self: _Self, config: ReceiveFaxConfig | None = None) -> _Self:
        """Receive a fax being delivered to this call."""
        ...

    def record(self: _Self, config: RecordConfig | None = None) -> _Self:
        """Record the call audio in the foreground, pausing further SWML execution until recording ends."""
        ...

    def record_call(self: _Self, config: RecordCallConfig | None = None) -> _Self:
        """Record call in the background."""
        ...

    def request(self: _Self, config: RequestConfig | None = None) -> _Self:
        """Send a GET, POST, PUT, or DELETE request to a remote URL."""
        ...

    def return_(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Return a value from an execute call or exit the script. The value can be any type."""
        ...

    def send_digits(self: _Self, config: SendDigitsConfig | None = None) -> _Self:
        """Send digit presses as DTMF tones."""
        ...

    def send_fax(self: _Self, config: SendFaxConfig | None = None) -> _Self:
        """Send a fax."""
        ...

    def send_sms(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Send an outbound SMS or MMS message to a PSTN phone number."""
        ...

    def set(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Set script variables to the specified values."""
        ...

    def sleep(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Pause execution for a specified duration."""
        ...

    def sip_refer(self: _Self, config: SipReferConfig | None = None) -> _Self:
        """Send SIP REFER to a SIP call."""
        ...

    def stop_denoise(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Stop noise reduction that was started with denoise."""
        ...

    def stop_record_call(
        self: _Self, config: StopRecordCallConfig | None = None
    ) -> _Self:
        """Stop an active background recording."""
        ...

    def stop_tap(self: _Self, config: StopTapConfig | None = None) -> _Self:
        """Stop an active tap stream."""
        ...

    def switch(self: _Self, config: SwitchConfig | None = None) -> _Self:
        """Execute different instructions based on a variable's value."""
        ...

    def tap(self: _Self, config: TapConfig | None = None) -> _Self:
        """Start background call tap. Media is streamed over Websocket or RTP to customer controlled URI."""
        ...

    def transfer(self: _Self, config: TransferConfig | None = None) -> _Self:
        """Transfer the execution of the script to a different SWML section, URL, or Relay application."""
        ...

    def unset(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Unset specified variables. The variables may have been set using the set method"""
        ...

    def pay(self: _Self, config: PayConfig | None = None) -> _Self:
        """Enables secure payment processing during voice calls. When implemented, it manages the entire payment flow"""
        ...

    def detect_machine(self: _Self, config: DetectMachineConfig | None = None) -> _Self:
        """A detection method that combines AMD (Answering Machine Detection) and fax detection."""
        ...

    def user_event(self: _Self, config: UserEventConfig | None = None) -> _Self:
        """Allows the user to set and send events to the connected client on the call."""
        ...
